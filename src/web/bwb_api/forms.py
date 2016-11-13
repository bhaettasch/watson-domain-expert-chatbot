from django.utils import html

from bwb.models import Message, KBFact, Chat
from django.forms import ModelForm


class PostMessageForm(ModelForm):
    """
    Form for message posting
    Author and chat are set while saving and thus hidden fields
    """

    class Meta:
        model = Message
        fields = ['chat', 'text']
        exclude = ['author']

    def clean_text(self):
        return html.strip_tags(self.cleaned_data['text'])


class AskExpertQuestionForm(ModelForm):
    """
    Form for question asking
    Other fields are set during saving
    """

    class Meta:
        model = Message
        fields = ['text']

    def clean_text(self):
        return html.strip_tags(self.cleaned_data['text'])


class CreateExternalChatForm(ModelForm):
    class Meta:
        model = Chat
        fields = ['external_id']
        exclude = ['name', 'is_external']

    def clean_external_id(self):
        return html.strip_tags(self.cleaned_data['external_id'])


class PostFactForm(ModelForm):
    """
    Form for message posting
    Type is set when saving and thus hiddden
    """

    class Meta:
        model = KBFact
        fields = ['definition', 'facts', 'image', 'source_id']
        exclude = ['type']
