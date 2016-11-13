import json
from string import Template
import pytz

from django.contrib.auth.models import User
from django.db import models
from django.utils import html


class Chat(models.Model):
    """
    Chat. A chat contains a list of messages. All active chats can be joined by every user. Watson BWB is a member of
    every chat
    """

    zone = pytz.timezone('Europe/Berlin')

    class Meta:
        ordering = ['active', 'name']
        verbose_name_plural = 'Chats'

    name = models.CharField(max_length=100)
    desc = models.TextField(verbose_name='Description', blank=True)
    start_timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    is_external = models.BooleanField(verbose_name="Is external?", default=False)
    external_id = models.CharField(max_length=100, verbose_name="ID of external chat", help_text="ID for cross referencing. May be empty for internal chats", blank=True)

    def __str__(self):
        if self.active:
            return "{} (started at {})".format(self.name, self.start_timestamp.astimezone(self.zone).strftime("%d.%m.%y %H:%M"))
        else:
            return "{} (archived)".format(self.name)


class Message(models.Model):
    """
    A single chat message
    """

    zone = pytz.timezone('Europe/Berlin')

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['creation_timestamp']

    chat = models.ForeignKey(Chat)
    author = models.ForeignKey(User, verbose_name="Author", null=True)
    text = models.TextField()
    creation_timestamp = models.DateTimeField(verbose_name="Sent at", auto_now_add=True)

    def __str__(self):
        return "{} @ {}".format(self.get_author_name(), self.creation_timestamp.astimezone(self.zone).strftime("%d.%m.%y %H:%M"))

    @property
    def text_excerpt(self):
        if len(self.text) < 50:
            return self.text
        return "{}...".format(self.text[:50])

    def info_object(self):
        print(self.creation_timestamp)
        return {
            'id': self.pk,
            'author': self.get_author_name(),
            'text': html.strip_tags(self.text[:1000] + (self.text[1000:] and '...')),
            'timestamp': self.creation_timestamp.astimezone(self.zone).strftime("%d.%m.%y %H:%M")
        }

    def get_author_name(self):
        if self.author is None:
            return "Anonymous"
        return html.strip_tags(self.author.username)


class WatsonMessage(models.Model):
    """
    An answer by watson
    """

    zone = pytz.timezone('Europe/Berlin')

    class Meta:
        verbose_name = "Message by Watson"
        verbose_name_plural = "Messages by Watson"
        ordering = ['creation_timestamp']

    chat = models.ForeignKey(Chat)
    text = models.TextField()
    api_answer = models.TextField(default="", blank=True, verbose_name="Raw bluemix answer", help_text="This is filled with the answer watson/blumix gave")
    additional_data = models.TextField(default="", blank=True, verbose_name="Additional data (JSON dump)", help_text="This field contains data that can be used to fullfill later requests")
    creation_timestamp = models.DateTimeField(verbose_name="Sent at", auto_now_add=True)
    vote_correct = models.IntegerField(default=0, verbose_name="Vote count: correct")
    vote_incorrect = models.IntegerField(default=0, verbose_name="Vote count: incorrect")
    vote_helpful = models.IntegerField(default=0, verbose_name="Vote count: helpful")
    vote_not_helpful = models.IntegerField(default=0, verbose_name="Vote count: not helpful")
    requesting_message = models.ForeignKey("Message", blank=True, null=True)
    answerable = models.BooleanField(default=False, verbose_name="Further reaction possible")
    action_performed = models.TextField(blank=True, verbose_name="Action(s) performed")
    system_text_pre = models.TextField(default="", blank=True, help_text="System text (to display before the actual message, may contain html tags)")
    system_text_post = models.TextField(default="", blank=True, help_text="System text (to display after the actual message, may contain html tags)")
    confidence = models.FloatField(default=0.0, blank=True)

    @property
    def text_excerpt(self):
        if len(self.text) < 50:
            return self.text
        return "{}...".format(self.text[:50])

    def info_object(self):
        if self.requesting_message is None:
            message_id = -1
        else:
            message_id = self.requesting_message.pk

        return {
            'id': self.pk,
            'text': self.text.encode('utf-8').decode('unicode_escape'),
            'timestamp': self.creation_timestamp.astimezone(self.zone).strftime("%d.%m.%y %H:%M"),
            'message': message_id,
            'system_text_pre': self.system_text_pre,
            'system_text_post': self.system_text_post,
            'confidence': self.confidence
        }

    def __str__(self):
        return "Watson @ {}".format(self.creation_timestamp.astimezone(self.zone).strftime("%d.%m.%y %H:%M"))


class WatsonProcessingLogEntry(models.Model):
    """
    Log entries to store also processings where no answer was produced in database
    """

    zone = pytz.timezone('Europe/Berlin')

    class Meta:
        verbose_name = "Watson Processing Log Entry"
        verbose_name_plural = "Watson Processing Log Entries"
        ordering = ['creation_timestamp']

    chat = models.ForeignKey(Chat)
    creation_timestamp = models.DateTimeField(verbose_name="Sent at", auto_now_add=True)
    requesting_message = models.ForeignKey("Message", blank=True, null=True)
    action_performed = models.TextField(blank=True, verbose_name="Action(s) performed")
    answer = models.ForeignKey("WatsonMessage", blank=True, null=True)
    stacktrace = models.TextField(blank=True, default='', null=True)

    def exception_occurred(self):
        return self.stacktrace is not None
    exception_occurred.boolean = True

    def __str__(self):
        return self.creation_timestamp.astimezone(self.zone).strftime("%d.%m.%y %H:%M")


class KBFact(models.Model):
    class Meta:
        verbose_name = "KB Fact"
        verbose_name_plural = "KB Facts"

    type = models.ForeignKey("KBFactType")
    definition = models.TextField()
    facts = models.TextField()
    image = models.URLField(blank=True)
    source_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return "{} ({})".format(self.definition, self.source_id)


class KBEntity(models.Model):
    class Meta:
        verbose_name = "KB Entity"
        verbose_name_plural = "KB Entities"

    name = models.CharField(max_length=250)
    fact = models.ForeignKey("KBFact")

    def __str__(self):
        return self.name+" ("+self.fact.type.name+")"


class KBFactType(models.Model):
    class Meta:
        verbose_name = "KB Fact Type"
        verbose_name_plural = "KB Fact Types"

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class KBFactTypePattern(models.Model):
    class Meta:
        verbose_name = "KB Fact Type Pattern"
        verbose_name_plural = "KB Fact Type Patterns"

    name = models.CharField(max_length=250)
    fact_type = models.ForeignKey("KBFactType")
    template_text = models.TextField()

    def __str__(self):
        return self.name+" for "+self.fact_type.name

    def substitute(self, name, fact_string):
        """
        Get pattern with substituted placeholders
        :param name: name of the current entity
        :param fact_string: facts (as json string)
        :return: pattern with replaced placeholders
        """
        facts = json.loads(fact_string)
        facts['name'] = name
        template = Template(self.template_text)
        try:
            output = template.substitute(facts)
            return output[0].upper() + output[1:]
        except KeyError:
            return None


class ChatRecentFunFact(models.Model):
    """
    Model recent FunFacts for each chat
    (can be used to prevent the same fact from occuring again and again in short amount of time)
    """
    class Meta:
        verbose_name = "Recent FunFact for Chat"
        verbose_name_plural = "Recent FunFact for Chats"
        ordering = ['creation_timestamp']

    chat = models.ForeignKey(Chat)
    fact = models.ForeignKey(KBFact)
    pattern = models.ForeignKey(KBFactTypePattern)
    creation_timestamp = models.DateTimeField(verbose_name="Sent at", auto_now_add=True)
