import random

from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from bwb import watson
from bwb.models import WatsonMessage


class CommandProcessor:
    @staticmethod
    def get(text, command, answer_generator):
        command_method = CommandProcessor.COMMAND_FUNCTIONS[command][0]
        # Use all tokens that are not commands
        text = " ".join(t for t in text.split() if t not in CommandProcessor.COMMAND_FUNCTIONS.keys())
        return command_method.__func__(text, answer_generator)

    @staticmethod
    def identify_command(text):
        """
        Check which command the given text contains
        :param text: text to check
        :return: first matched command
        """
        tokenized_text = text.split()
        for key, (function, exact_match) in CommandProcessor.COMMAND_FUNCTIONS.items():
            if (exact_match and text == key) or (not exact_match and key in tokenized_text):
                return key
        return ''

    @staticmethod
    def command_help(text, answer_generator):
        """
        React to help command

        :param text: message that triggered the command
        :param answer_generator: reference to answer generator (to access contextual properties)
        """
        return '', watson.HELP_TEXT, ''

    @staticmethod
    def command_video(text, answer_generator):
        """
        React to video command

        :param answer_text: message that triggered the comand (command is removed)
        :param answer_generator: reference to answer generator (to access contextual properties)
        """
        pre = answer_text = post = ''
        try:
            youtube = build(settings.YOUTUBE_API_SERVICE_NAME,
                            settings.YOUTUBE_API_VERSION,
                            developerKey=settings.API_KEY_YOUTUBE)

            search_response = youtube.search().list(
                q=text,
                part="id,snippet",
                maxResults=10,
                type='video',
            ).execute()

            video_id = ''
            results = list(search_response.get("items", []))
            random.shuffle(results)
            for search_result in results:
                video_id = search_result["id"]["videoId"]
                break
            if video_id:
                pre = '<iframe width="340" height="200" src="https://www.youtube.com/embed/' + video_id + '?rel=0" frameborder="0" allowfullscreen></iframe>'
            else:
                pre = watson.NO_RESULT

        except HttpError:
            answer_text = watson.NO_YOUTUBE

        return pre, answer_text, post

    @staticmethod
    def command_funfact(text, answer_generator):
        """
        React to funfact command

        :param text: message that triggered the command
        :param answer_generator: reference to answer generator (to access contextual properties)
        """
        results = answer_generator.generate_kb_entries(text)
        if results.count() > 0:
            return answer_generator.generate_local_answer_funfact(results, text, False)
        return watson.NO_FUNFACT+text, '', ''

    @staticmethod
    def command_more(text, answer_generator):
        """
        React to more command

        :param text: message that triggered the command
        :param answer_generator: reference to answer generator (to access contextual properties)
        """
        last_answers = WatsonMessage.objects.filter(requesting_message__author=answer_generator.message.author).order_by('-creation_timestamp')
        if last_answers.count() > 0:
            for last_answer in last_answers:
                last_text = last_answer.requesting_message.text.lower()
                if last_text != 'more' and last_text != '@watson more' and last_text != '':
                    answer_generator.process_inner(last_text)
                    if answer_generator.system_text_pre != '' or answer_generator.answer_text != '':
                        return answer_generator.system_text_pre, answer_generator.answer_text, answer_generator.system_text_post
        return watson.NO_REPEAT, '', ''

    @staticmethod
    def command_image(text, answer_generator):
        """
        React to funfact command

        :param text: message that triggered the command
        :param answer_generator: reference to answer generator (to access contextual properties)
        """
        results = answer_generator.generate_kb_entries(text).filter(fact__image__isnull=False)
        if results.count() > 0:
            kb_entry = random.choice(results)
            return answer_generator.generate_img_representation(kb_entry.fact.image), '', ''
        return watson.NO_IMAGE+text, '', ''

    COMMAND_FUNCTIONS = {
        'help': (command_help, True),
        'video': (command_video, False),
        'funfact': (command_funfact, False),
        'fact': (command_funfact, False),
        'random': (command_funfact, False),
        'more': (command_more, True),
        'image': (command_image, False),
        'picture': (command_image, False),
    }
