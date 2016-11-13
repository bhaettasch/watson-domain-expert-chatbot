import json
import random
import traceback

from watson_developer_cloud import WatsonException

from bwb import watson
from bwb.models import Message, WatsonMessage, KBEntity, WatsonProcessingLogEntry
from bwb.watson.alchemy_analzyed_message import AlchemyAnalyzedMessage
from bwb.watson.command_processor import CommandProcessor
from bwb.watson.funfact_generator import FunFactGenerator
from bwb.watson.private_instance_request import PrivateInstanceRequest


def process_answer(pk=0):
    answer_generator = AnswerGenerator(Message.objects.get(pk=pk))
    answer_generator.process()


class AnswerGenerator:
    """
    Handles all kind of generating watsons answers to messages in the chat
    """

    def __init__(self, message):
        """
        Constructor

        :param message: message for which the answer is created
        """
        self.message = message
        self.answer_text = ''
        self.additional_answer_text = ''
        self.system_text_pre = ''
        self.system_text_post = ''
        self.confidence = 0.0
        self.action_performed = ''
        self.additional_data = []
        self.answerable = False
        self.api_answer = ''
        self.fallback_tried = False
        self.direct_without_prefix = False
        self.fallback_answer = ''
        self.fallback_confidence = 0

    def process(self, direct_without_prefix=False):
        """
        Process the message
        """
        try:
            self.action_performed += 'process.'
            text = self.message.text.lower()
            self.direct_without_prefix = direct_without_prefix

            self.process_inner(text)

            if self.answer_text != '' or self.system_text_pre != '':
                answer = self._create_answer()
                self._create_log_entry(answer=answer)
                return answer
            else:
                self._create_log_entry()
        except:
            self._create_log_entry(stacktrace=traceback.format_exc())
        return None

    def process_inner(self, text):
        # Message addressed to watson?
        if self.direct_without_prefix or self.check_directly_to_watson(text):
            if self.check_directly_to_watson(text):
                text = self.generate_request_without_prefix(text)
            text = text.strip()

            if text == '':
                self.system_text_pre, self.answer_text, self.system_text_post = CommandProcessor.command_help(text, self)
            else:
                command = CommandProcessor.identify_command(text)
                if command != '':
                    self.system_text_pre, self.answer_text, self.system_text_post = CommandProcessor.get(text, command, self)
                elif text == "who is groot?":
                    self.system_text_pre, self.answer_text, self.system_text_post = '', 'I am Groot!', '<iframe width="340" height="200" src="https://www.youtube.com/embed/ph_l7Pp_1mk?rel=0" frameborder="0" allowfullscreen></iframe>'
                elif self.check_question(text):
                    self.process_question(self.generate_question_from_input(text))
                else:
                    self.process_text(text=text)
        # Normal conversation going on (try to help without content send to watson explicitly)
        else:
            self.process_context()

    def process_question(self, text):
        """
        Process a real question (by sending it to private instance)
        :param text: question text
        """
        r = PrivateInstanceRequest(text)
        self.action_performed += 'process_question:request_status_{}.'.format(r.status())
        if r.status() == 200:
            answer = r.answer_object()
            if answer is not None:
                if answer['confidence'] >= watson.PHRASE_QUALITY_THRESHOLD:
                    self.answer_text = answer['text']
                else:
                    if not self.fallback_tried:
                        self.action_performed += "Fallback."
                        self.fallback_tried = True
                        self.fallback_answer = answer['text']
                        self.fallback_confidence = answer['confidence']
                        self.system_text_pre += watson.NO_DIRECT_ANSWER + ' '
                        self.process_indirect(text)
                    else:
                        self.system_text_pre = random.choice(watson.SUFFICIENT)
                        if answer['confidence'] > self.fallback_confidence:
                            self.answer_text = answer['text']
                            self.confidence = answer['confidence']
                        else:
                            self.answer_text = self.fallback_answer
                            self.confidence = self.fallback_confidence
                self.api_answer = r.raw_answer()
                self.confidence = answer['confidence']
            else:
                self.system_text_pre = watson.NO_ANSWER
        elif r.status() == 400:
            self.system_text_pre = watson.NOT_UNDERSTOOD
        else:
            self.system_text_pre = watson.NO_CONNECTION

    def process_text(self, text):
        """
        Process a block of text
        :param text: text to process
        """
        self.action_performed += 'process_text.'

        # Determine whether this is an answer to a previously asked answerable of watson
        last_answer_for_user = self.generate_last_answer_for_user()

        if self.check_last_answer_exists_and_answerable(last_answer_for_user):
            self.process_direct(text=text, answerable_answer=last_answer_for_user)
        else:
            self.process_indirect(text=text)

    def process_direct(self, text, answerable_answer):
        """
        Process a request without real question that is 1a reaction on a answerable of watson
        :param answerable_answer: answerable this answer might be an answer to
        :param text: text to process
        """
        if text.isdecimal():
            self.action_performed += 'process_question:numeric.'
            option_number = int(text) - 1
            keywords = json.loads(answerable_answer.additional_data)
            if 0 <= option_number < len(keywords):
                selected_keyword = keywords[option_number][0]
                self.additional_answer_text = watson.OK.format(selected_keyword)
                self.process_phrase(selected_keyword, watson.ACTION_SOURCE_DIRECT)
            else:
                self.system_text_pre += watson.NUMBER_PROMPT + self.generate_keyword_string(keywords)
                self.additional_data = keywords
                self.answerable = True

        # No way found to process this directly? Try indirect
        else:
            self.action_performed += 'process_question:not_sufficient.'
            self.process_indirect(text=text)

    def process_indirect(self, text):
        """
        Process a request without real question that is not a reaction on a answerable of watson
        :param text: text to process
        """
        self.action_performed += 'process_indirect.'

        if self.check_is_phrase(text):
            self.process_phrase(text, watson.ACTION_SOURCE_DIRECT)
        else:
            self.process_long_text(text)

    def process_phrase(self, phrase, action_source):
        """
        Process a phrase
        :param phrase: given phrase
        :param action_source: kind of action (specified through its source)
        """
        if self.check_in_fact_db(phrase):
            self.action_performed += 'process_phrase:in_local_db.'
            self.process_local_fact(phrase, action_source)
        elif action_source == watson.ACTION_SOURCE_DIRECT:
            self.action_performed += 'process_phrase:not_local,direct.'
            question = self.generate_question_from_keyword(phrase)
            self.process_question(question)
        else:
            # No answer generation for context keywords without local fact database entries
            self.action_performed += 'process_phrase:failed,not_local,indirect.'

    def process_local_fact(self, phrase, action_source):
        """
        Process a phrase that is part of the local fact database
        :param phrase: phrase to process
        :param action_source: kind of action (specified through its source)
        """
        results = self.generate_kb_entries(phrase)
        if action_source == watson.ACTION_SOURCE_DIRECT:
            self.action_performed += 'process_local_fact:definition.'
            self.system_text_pre, self.answer_text, self.system_text_post = self.generate_local_answer_definition(results, phrase)
        else:
            self.action_performed += 'process_local_fact:funfact.'
            self.system_text_pre, self.answer_text, self.system_text_post = self.generate_local_answer_funfact(results, phrase)

    def process_long_text(self, text):
        """
        Process a longer text (not just one or a few words)
        :param text: text to process
        """
        try:
            alchemy_analyzed_text = self.generate_analyzed_answer(text)

            keywords = alchemy_analyzed_text.keywords(watson.KEYWORD_THRESHOLD)

            if self.check_keywords_found(keywords):
                if len(keywords) == 1:
                    self.process_phrase(keywords[0][0], watson.ACTION_SOURCE_DIRECT)
                else:
                    self.action_performed += 'process_long_text:keywords_found.'
                    self.process_keywords_found(keywords, alchemy_analyzed_text)
            else:
                self.action_performed += 'process_long_text:no_keywords.'
                self.process_no_keywords_found(alchemy_analyzed_text)
        except WatsonException:
            self.action_performed += 'process_long_text:alchemy_analyze_failed'
            self.system_text_pre = watson.NOT_UNDERSTOOD

    def process_keywords_found(self, keywords, alchemy_analyzed_text):
        """
        Do something with the keywords found
        :param keywords: keywords found
        :param alchemy_analyzed_text: analyzed text object
        """
        self.action_performed += 'process_keywords_found.'

        self.system_text_pre += watson.CHOICE
        self.answer_text = self.generate_keyword_string(keywords)
        self.api_answer = alchemy_analyzed_text.raw,
        self.answerable = True
        self.additional_data = keywords

    def process_no_keywords_found(self, alchemy_analyzed_text):
        """
        Do something if no keywords were found
        :param alchemy_analyzed_text: analyzed text object
        """
        self.action_performed += 'process_no_keywords_found.'

        self.answer_text = watson.UNSURE
        self.api_answer = alchemy_analyzed_text.raw

    def process_context(self):
        """
        Process this message in the context of the last ones since they are not specifically directed to watson
        """
        self.action_performed += 'process_context.'

        context_messages = self.generate_context_messages()
        if self.check_context_size(context_messages):
            text = self.generate_context_message_string(context_messages)
            try:
                alchemy_analyzed_text = self.generate_analyzed_answer(text)
                keywords = alchemy_analyzed_text.keywords(watson.KEYWORD_THRESHOLD_INTERJECTION)
                # TODO Improve context processing
                if self.check_keywords_found(keywords):
                    self.action_performed += 'process_context:sufficient_size,keywords_found.'
                    self.process_phrase(keywords[0][0], watson.ACTION_SOURCE_CONTEXT)
                else:
                    self.action_performed += 'process_context:sufficient_size,no_keywords.'
            except WatsonException:
                self.action_performed += 'process_context:alchemy_analyze_failed'
        else:
            self.action_performed += 'process_context:insufficient_size.'

    @staticmethod
    def generate_request_without_prefix(text):
        """
        Removes the prefix from the given text

        :param text: given text
        :return: text without prefix
        """
        return text[len(watson.BOT_ADDRESS_PREFIX):].strip()  # Remove '@watson' prefix

    @staticmethod
    def generate_question_from_input(text):
        """
        Format a given input as question (maybe add a question mark at the end)
        :param text: text to format
        :return: text with question mark in the end
        """
        if text.endswith("?"):
            return text
        if text.endswith(".") or text.endswith("!"):
            text = text[:-1]
        return text + "?"

    @staticmethod
    def generate_analyzed_answer(text):
        """
        Analyze the text and return the answer
        :param text: text to analyze
        :return: object representing the analyzed text
        """
        return AlchemyAnalyzedMessage(text=text)

    @staticmethod
    def generate_question_from_keyword(selected_keyword):
        """
        Generate a question from the keyword that can be send to the watson private instance
        :param selected_keyword: keyword to generate the question from
        :return: question
        """
        # TODO Improve question generation
        return "What is {}?".format(selected_keyword)

    @staticmethod
    def generate_keyword_string(keywords):
        """
        Get a string of keywords with a number assigned

        :param keywords: keywords to represent
        :return: string consisting of number-word-pairs with colons in between separated by spaces
        """
        return ", ".join("{}: {} ({:1.2f})".format(i + 1, word, rel) for (i, (word, rel)) in enumerate(keywords))

    @staticmethod
    def generate_tokenized_text(text):
        """
        Tokenize the given text
        :param text: given text
        :return: tokenzized text (array of strings)
        """
        return text.split()

    def generate_last_answer_for_user(self):
        """
        Found the last answer sent to this user
        :return: last answer sent to this user (may be none)
        """
        return WatsonMessage.objects.filter(requesting_message__author=self.message.author).last()

    def generate_context_messages(self):
        """
        Get text from the last messages. The count depends on the CONTEXT_SIZE param
        :return: list containing the last messages
        """
        filtered_messages = Message.objects.filter(chat=self.message.chat).order_by('-creation_timestamp').all()
        selected_messages = []
        for message in filtered_messages:
            # Only use messages not directed to watson
            if not self.check_directly_to_watson(message.text):
                # But stop as soon as the first one already answered is found
                if message.watsonmessage_set.count() > 0:
                    break
                selected_messages.append(message)

            # Also stop if enough messages were found
            if len(selected_messages) == watson.CONTEXT_SIZE:
                break

        return selected_messages

    @staticmethod
    def generate_context_message_string(context_messages):
        """
        Generate a single string out of context messages
        :param context_messages: a list of context messages
        :return: a string with the concatenated texts of the messages
        """
        return "; ".join(message.text for message in context_messages)

    @staticmethod
    def generate_kb_entries(text):
        """
        Find KB entries for given text

        :param text: text to find kb entries for
        :return: queryset of matching entries
        """
        entities = KBEntity.objects.filter(name__iexact=text)
        if entities.count() > 0:
            return entities
        return KBEntity.objects.filter(name__icontains=text)

    @staticmethod
    def check_question(text):
        """
        Check whether the given text is a question
        :param text: text to check
        :return: true if question, false if not
        """
        return text.endswith("?") or any(text.startswith(w) for w in watson.QUESTION_WORDS)

    @staticmethod
    def check_directly_to_watson(text):
        """
        Check if this message is directed to watson
        :return: true if message is directed to watson (starts with name of agent)
        """
        return text.startswith(watson.BOT_ADDRESS_PREFIX)

    @staticmethod
    def check_in_fact_db(phrase):
        """
        Check whether the given phrase is in our structured fact database

        :param phrase: phrase to find
        :return: true if phrase is in fact database, false if not
        """
        return AnswerGenerator.generate_kb_entries(phrase).count() > 0

    @staticmethod
    def check_keywords_found(keywords):
        """
        Check if keywords were found in the text
        :param keywords: list of keywords (may be empty)
        :return: true if at least one keyword was found
        """
        return len(keywords) > 0

    def check_is_phrase(self, text):
        """
        Check if the text is a phrase (count of words lower than a given threshold)
        :param text: text to check
        :return: true if text is a phrase
        """
        tokenized_text = self.generate_tokenized_text(text)
        return len(tokenized_text) <= watson.MAXIMUM_PHRASE_LENGTH

    @staticmethod
    def check_last_answer_exists_and_answerable(last_answer_for_user):
        """
        Check whether there is a last answer for this user and this one is answerable
        :param last_answer_for_user: answer or None
        :return: true if answer is given and answer is answerable
        """
        return last_answer_for_user is not None and last_answer_for_user.answerable

    @staticmethod
    def check_context_size(context_messages):
        """
        Make sure the size of the context is big enough
        :param context_messages: list of context messages
        :return: true if context size is met, false if not
        """
        return len(context_messages) == watson.CONTEXT_SIZE

    @staticmethod
    def generate_local_answer_definition(found_entities, phrase):
        """
        Create an answer using the local resources containing the definition or definitions
        This may also return an image if available

        :param found_entities: a list of matching local KB Fact Entities
        :param phrase: Phrase that should be defined
        :return: Formatted string to display
        """
        if len(found_entities) == 1:
            entity = found_entities[0]
            if entity.fact.image != '':
                image_representation = AnswerGenerator.generate_img_representation(entity.fact.image)
            else:
                image_representation = ''
            return '', entity.fact.definition, image_representation

        # TODO Make choices
        if len(found_entities) > 5:
            found_entities = found_entities[:5]
        return "Found {} results for <b>{}</b>:".format(len(found_entities),phrase),\
                "<br>".join(str(i + 1) + ": " + result.fact.definition + " (" + result.fact.type.name + ")" for i, result in enumerate(found_entities)),\
                ''

    @staticmethod
    def generate_img_representation(url):
        """
        Generate image representation

        :param url: image url
        :return: image as html representation
        """
        return '<img src="' + url + '" class="img-thumbnail" style="height:150px;width:auto;" />'

    def generate_local_answer_funfact(self, found_entities, phrase, no_recent_facts=True):
        """
        Create a funfact as answer using the local resources

        :param found_entities: a list of matching local KB Fact Entities
        :param phrase: Phrase that the funfact should be about
        :return: Formatted string to display
        """
        if len(found_entities) == 1:
            entity = found_entities[0]
        else:
            entity = random.choice(found_entities)

        ffg = FunFactGenerator(phrase, self.message.chat, entity)
        return 'Did you know:', ffg.next(no_recent_facts), ''

    def _create_answer(self):
        """
        Create an answer object in db and return a reference

        :return: reference to the created answer
        """
        return WatsonMessage.objects.create(
            text=self.answer_text,
            api_answer=self.api_answer,
            chat=self.message.chat,
            requesting_message=self.message,
            answerable=self.answerable,
            additional_data=json.dumps(self.additional_data),
            system_text_pre=self.system_text_pre,
            system_text_post=self.system_text_post,
            confidence=self.confidence,
            action_performed=self.action_performed
        )

    def _create_log_entry(self, answer=None, stacktrace=None):
        """
        Create a log entry object in db

        :param answer: reference to the answer created
        :param stacktrace: stacktrace of any errors occurred
        """
        WatsonProcessingLogEntry.objects.create(
            chat=self.message.chat,
            requesting_message=self.message,
            action_performed=self.action_performed,
            stacktrace=stacktrace,
            answer=answer
        )

