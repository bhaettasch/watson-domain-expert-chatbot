import json
import re
import threading

import requests
from django.conf import settings
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.utils import html
from django.views import View
from django.views.generic import TemplateView, DetailView, CreateView
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from bwb.models import Chat, Message, WatsonMessage, KBFact, KBFactType, KBEntity
from bwb.watson.answer_generator import process_answer, AnswerGenerator
from bwb_api.forms import PostMessageForm, PostFactForm, CreateExternalChatForm, AskExpertQuestionForm


class JSONMixin():
    """
    Render content of context['content'] into JSON answer
    """

    def get_context_data(self, **kwargs):
        context = super(JSONMixin, self).get_context_data(**kwargs)
        context['content'] = {}
        return context

    def render_to_response(self, context, **response_kwargs):
        content = json.dumps(context['content'])

        response = HttpResponse("", content_type="text/json; charset=utf-8", **response_kwargs)
        response['Pragma'] = 'no-cache'
        response['Cache-Control'] = 'no-cache must-revalidate proxy-revalidate'
        response['Content-Length'] = len(content)

        response.write(content)
        return response

    def get_template_names(self):
        return []


class JSONView(JSONMixin, TemplateView):
    """
    Use this view if no special view should be used. Otherwise, use JSONMixin
    """
    pass


class APIGetForbiddenMixin():
    """
    Mixin to prevent calling a class based view with GET
    """
    def get(self, request, *args, **kwargs):
        context = {}
        context['content'] = {'status': 405, 'message': 'This method has to be called with POST data.'}
        return self.render_to_response(context, status=405)


class APIPostMixin():
    """
    Mixin to answer POST calls to this class based view
    """
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class NewMessagesView(JSONMixin, DetailView):
    """
    Get messages from a chat
    If the param lastMessageID is given, only messages posted after the one with the given ID are returned
    If this param is omitted, all messages from the chat are returned
    """
    model = Chat
    context_object_name = 'chat'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ID of last received message given? Only return new messages
        if "lastMessageID" in self.kwargs:
            message_set = context['chat'].message_set.filter(pk__gt=self.kwargs['lastMessageID'])
            watson_message_set = context['chat'].watsonmessage_set.filter(pk__gt=self.kwargs['lastWatsonMessageID'])
        # Otherwise, return all messages
        else:
            message_set = context['chat'].message_set.all()
            watson_message_set = context['chat'].watsonmessage_set.all()

        context['content']['messages'] = [message.info_object() for message in message_set]
        context['content']['watsonmessages'] = [message.info_object() for message in watson_message_set]
        context['content']['messagecount'] = len(context['content']['messages'])
        context['content']['watsonmessagecount'] = len(context['content']['watsonmessages'])
        context['content']['status'] = 200
        return context


class NewWatsonMessagesView(JSONMixin, DetailView):
    """
    Get watson messages from a chat
    If the param lastMessageID is given, only watson messages posted after the one with the given ID are returned
    If this param is omitted, all watson messages from the chat are returned
    """
    model = Chat
    context_object_name = 'chat'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ID of last received message given? Only return new messages
        if "lastMessageID" in self.kwargs:
            watson_message_set = context['chat'].watsonmessage_set.filter(pk__gt=self.kwargs['lastMessageID'])
        # Otherwise, return all messages
        else:
            watson_message_set = context['chat'].watsonmessage_set.all()

        context['content']['answers'] = [message.info_object() for message in watson_message_set]
        context['content']['count'] = len(context['content']['answers'])
        context['content']['status'] = 200
        return context


class AddMessageView(JSONMixin, APIGetForbiddenMixin, CreateView):
    """
    Post a new message (using POST)
    """
    success_url = ""
    form_class = PostMessageForm
    model = Message

    def form_valid(self, form):
        if form.instance.chat.is_external:
            form.instance.author = None
        else:
            if self.request.user is None:
                return HttpResponse("Must be logged in to post a message", status=403)
            form.instance.author = self.request.user

        self.object = form.save()

        t = threading.Thread(target=process_answer, kwargs={'pk': self.object.pk})
        t.start()

        return HttpResponse(status=201)

    def form_invalid(self, form):
        return HttpResponse("Invalid message", status=400)


class CreateExternalChatView(JSONMixin, APIGetForbiddenMixin, CreateView):
    """
    Post a new message (using POST)
    """
    success_url = ""
    form_class = CreateExternalChatForm
    model = Chat

    def form_valid(self, form):
        form.instance.is_external = True
        form.instance.name = "External chat: {}".format(form.instance.external_id)
        self.object = form.save()
        answer = json.dumps({'status': 201, 'id': self.object.pk})
        return HttpResponse(answer, status=201)

    def form_invalid(self, form):
        return HttpResponse("Could not create external chat. Invalid request.", status=400)


class VoteView(JSONMixin, APIGetForbiddenMixin, APIPostMixin, DetailView):
    """
    Vote (mark a message as correct/helpful or not)
    """
    model = WatsonMessage
    context_object_name = 'message'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'action' not in self.request.POST:
            context['content']['message'] = 'No field specified'
            context['content']['status'] = 400
        else:
            action = self.request.POST['action']
            changed = False

            if action == 'correct':
                context['message'].vote_correct += 1
                changed = True
            elif action == 'incorrect':
                context['message'].vote_incorrect += 1
                changed = True
            elif action == 'helpful':
                context['message'].vote_helpful += 1
                changed = True
            elif action == 'nothelpful':
                context['message'].vote_not_helpful += 1
                changed = True

            if changed:
                context['message'].save()
                context['content']['message'] = 'Vote saved'
                context['content']['status'] = 200
            else:
                context['content']['message'] = 'Invalid action'
                context['content']['status'] = 400

        return context


class AddFactView(JSONMixin, APIGetForbiddenMixin, CreateView):
    """
    Post a new fact (using POST)
    """
    form_class = PostFactForm
    model = KBFact

    def form_valid(self, form):
        if 'names' not in self.request.POST:
            return HttpResponse('Error: Names missing', status=400)
        if 'type' not in self.request.POST:
            return HttpResponse('Error: Fact type missing', status=400)

        fact_type = KBFactType.objects.filter(name=self.request.POST['type']).first()
        if fact_type is None:
            return HttpResponse('Error: Invalid fact type', status=400)

        form.instance.type = fact_type

        # Update existing fact...
        existing_facts = KBFact.objects.filter(source_id=form.instance.source_id, type=fact_type)
        if existing_facts.count() > 0:
            self.object = existing_facts.first()
            self.object.definition = form.instance.definition
            self.object.facts = form.instance.facts
            self.object.image = form.instance.image
            self.object.save()
            response_message = "Updated fact: {}.".format(self.object.pk)
        # or create a new one
        else:
            self.object = form.save()
            response_message = "Created new fact: {}.".format(self.object.pk)

        created_name_count = 0
        names = set(json.loads(self.request.POST['names']))
        for name in names:
            if KBEntity.objects.filter(name=name, fact_id=self.object.pk).count() == 0:
                KBEntity.objects.create(name=name, fact=self.object)
                created_name_count += 1

        response_message += " Created {} new entities.".format(created_name_count)

        return HttpResponse(response_message, status=201)

    def form_invalid(self, form):
        return HttpResponse("Invalid request", status=400)


class WatsonMessageToSpeechView(DetailView):
    model = WatsonMessage
    context_object_name = "watsonmessage"

    def render_to_response(self, context, **response_kwargs):
        # Remove html tags (otherwise bluemix tries to interpret them as SSML and probably fails
        text = re.sub(r'<[^>]+>', '', context['watsonmessage'].text, count=0)

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        r = requests.get(settings.T2S_URL + "/v1/synthesize",
                            auth=(settings.T2S_USER, settings.T2S_PW),
                            params={'text': text, 'voice': settings.T2S_VOICE},
                            stream=True, verify=False
                            )

        if r.status_code == 200:
            response = StreamingHttpResponse(
                (chunk for chunk in r.iter_content(512 * 1024)),
                content_type='audio/ogg;codecs=opus ')
        else:
            response = HttpResponse(status=r.status_code)

        return response


class ExpertAskView(JSONMixin, APIGetForbiddenMixin, CreateView):
    """
    Ask the expert a question (using POST)
    """
    form_class = AskExpertQuestionForm
    model = Message

    def form_valid(self, form):
        if self.request.user is None:
            return HttpResponse("Please login", status=403)

        # Find or create the private expert chat
        chat_id = 'wme_'+str(self.request.user.pk)
        try:
            chat = Chat.objects.get(external_id=chat_id)
        except Chat.DoesNotExist:
            chat = Chat.objects.create(
                name="Watson Expert Chat for "+str(self.request.user),
                is_external=True,
                external_id=chat_id
            )

        # Set additional fields and save
        form.instance.chat = chat
        form.instance.author = self.request.user
        self.object = form.save()

        # Create answer
        answer_generator = AnswerGenerator(self.object)
        answer = answer_generator.process(direct_without_prefix=True)

        if answer is not None:
            return HttpResponse('{"status":200}', content_type="text/json; charset=utf-8", status=201)
        return HttpResponse('{"status":500}', content_type="text/json; charset=utf-8", status=200)


class ExpertAnswerView(JSONMixin, DetailView):
    """
    Get watson answer for expert chat
    """
    model = WatsonMessage
    context_object_name = 'answer'

    def get_object(self, queryset=None):
        return WatsonMessage.objects.filter(chat__external_id='wme_'+str(self.request.user.pk)).last()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if 'answer' in context and context['answer'] is not None:
            context['content']['answer'] = context['answer'].info_object()
            context['content']['status'] = 200
        else:
            context['content']['status'] = '404'
        return context


class AudioURLToTextView(View):
    def post(self, *args, **kwargs):

        if 'url' not in self.request.POST:
            return HttpResponse('URL missing', status=400)
        url = self.request.POST['url']

        # Load audio file from external service
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        r = requests.get(url, stream=True, verify=False)

        # Process using bluemix
        uplodad_request = requests.post(url=settings.S2T_URL + '/v1/recognize?continuous=true',
                                        auth=(settings.S2T_USER, settings.S2T_PW),
                                        data=r.content,
                                        headers={'Content-Type': 'audio/ogg;codecs=opus'}
                                        )

        if uplodad_request.status_code != 200:
            return HttpResponse(status=400)

        result = uplodad_request.json()
        answer = {
            "text": result['results'][0]['alternatives'][0]['transcript'],
            "confidence": result['results'][0]['alternatives'][0]['confidence']
        }

        return HttpResponse(json.dumps(answer), content_type="text/json; charset=utf-8", status=200)
