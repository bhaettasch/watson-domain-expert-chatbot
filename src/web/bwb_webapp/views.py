import json
import math

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseForbidden
from django.views.generic import ListView, DetailView, TemplateView, CreateView

from bwb.models import Chat, WatsonMessage, Message


class ChatListView(LoginRequiredMixin, ListView):
    template_name = 'bwb_webapp/chats.html'
    context_object_name = 'chats'
    model = Chat

    def get_queryset(self):
        return Chat.objects.filter(is_external=False, active=True)


class ChatDetailView(LoginRequiredMixin, DetailView):
    template_name = 'bwb_webapp/chat.html'
    context_object_name = 'chat'
    model = Chat

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_external:
            return HttpResponseForbidden("You may not access expert chat data")
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['api_root'] = self.request.META['SCRIPT_NAME'] + '/api/'
        return context


class ChatCreateView(LoginRequiredMixin, CreateView):
    model = Chat
    fields = ['name']
    template_name = 'bwb_webapp/chat_form.html'
    success_url = reverse_lazy('app:chatOverview')


class QuestionAnswerPairsView(LoginRequiredMixin, ListView):
    model = WatsonMessage
    context_object_name = 'watsonMessages'
    template_name = 'bwb_webapp/question_answer.html'
    ordering = '-creation_timestamp'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().filter(chat__is_external=False)


class WelcomePageView(TemplateView):
    template_name = 'bwb_webapp/welcome_page.html'


class WatsonMarvelExpertView(LoginRequiredMixin, TemplateView):
    template_name = 'bwb_webapp/watson_marvel_expert.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['api_root'] = self.request.META['SCRIPT_NAME'] + '/api/'
        return context


class StatsView(LoginRequiredMixin, TemplateView):
    template_name = 'bwb_webapp/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TODO Prepare more data

        # Scatter plots
        conf_vs_correct = []
        conf_vs_helpful = []

        histogram_bins = [0 for i in range(0, 11)]
        histogram_bins_correct = [['{} - {}'.format(i*10, (i+1)*10-1), 0, 0, 0] for i in range(0, 11)]
        histogram_bins_correct[10][0] = "100"
        histogram_bins_helpful = [['{} - {}'.format(i*10, (i+1)*10-1), 0, 0, 0] for i in range(0, 11)]
        histogram_bins_helpful[10][0] = "100"

        vote_count = 0

        messages = Message.objects.filter(chat__active=True)

        watson_messages = WatsonMessage.objects.filter(chat__active=True)
        for wm in watson_messages:
            if wm.confidence > 0:
                confidence = wm.confidence
                index = math.floor(confidence*10)
                histogram_bins[index] += 1
                c_sum = wm.vote_correct + wm.vote_incorrect
                if c_sum > 0:
                    c = (wm.vote_correct - wm.vote_incorrect) / c_sum
                    histogram_bins_correct[index][1] += 1
                    if c > 0:
                        histogram_bins_correct[index][2] += 1
                    elif c < 0:
                        histogram_bins_correct[index][3] += 1
                    conf_vs_correct.append([wm.confidence, c])
                    vote_count += c_sum
                h_sum = wm.vote_helpful + wm.vote_not_helpful
                if h_sum > 0:
                    h = (wm.vote_helpful - wm.vote_not_helpful) / h_sum
                    histogram_bins_helpful[index][1] += 1
                    if c > 0:
                        histogram_bins_helpful[index][2] += 1
                    elif c < 0:
                        histogram_bins_helpful[index][3] += 1
                    conf_vs_helpful.append([wm.confidence, h])
                    vote_count += h_sum

        context['message_count'] = messages.count()
        context['answer_count'] = watson_messages.count()
        context['vote_count'] = vote_count
        context['conf_vs_correct'] = json.dumps(conf_vs_correct)
        context['conf_vs_helpful'] = json.dumps(conf_vs_helpful)
        confidence_steps = [["{} - {}".format(i*10, (i+1)*10-1), histogram_bins[i]] for i in range(0, 11)]
        confidence_steps[-1][0] = "100"
        context['confidence_steps'] = json.dumps(confidence_steps)

        context['histogram_bins_correct'] = json.dumps(histogram_bins_correct)
        context['histogram_bins_helpful'] = json.dumps(histogram_bins_helpful)
        context['user_count'] = User.objects.count()

        return context


class RegistrationPageView(CreateView):
    template_name='bwb_webapp/registration.html'
    form_class=UserCreationForm
    success_url=reverse_lazy("app:index")

    def form_valid(self, form):
        req = super(RegistrationPageView, self).form_valid(form)
        form.save()
        user = authenticate(username=self.request.POST['username'], password=self.request.POST['password1'])
        login(self.request, user)
        return req
