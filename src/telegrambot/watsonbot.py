#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""TelegramBot integration adapter"""


import os
import random
import string
import sys
import re
import signal
import traceback
import configparser
from threading import Event, Thread
import codecs
import urllib.request
import urllib.parse
import mimetypes
import requests
import telepot
#import imghdr
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

config = configparser.ConfigParser()
config.read('config.ini')

BOT_NAME = config['DEFAULT']['BOT_NAME']  # For replacing '@BesserwisserBot ' in requests
API_TOKEN = config['DEFAULT']['API_TOKEN']
BASE_URL = config['DEFAULT']['BASE_URL']

# Persistence file
LAST_CHAT_IDS_FILE = 'chat_ids.txt'


AT_WATSON_PREFIX = '@Watson '
AT_BOT_PREFIX = '@'+BOT_NAME+' '


SHOW_WELCOME_MESSAGE = True

WELCOME_MESSAGE_PRIVATE_CHAT = "Hello, {}. Nice to talk to you! You can ask me nearly everything about the Marvel universe and I'll try to answer.\nYou can type `help` for a short introduction."
WELCOME_MESSAGE_GROUP_CHAT   = "Hello. Nice to join your conversation about {}! I'll listen and toss in some facts if I know something. You can ask me nearly everything directly about the Marvel universe and I'll try to answer. To do so, start your message with '@Watson'.\nYou can type `help` for a short introduction."

HELP_STRING_PRIVATE = "In a private chat with me, you don't have to prepend _"+AT_WATSON_PREFIX+"_.\nFor a definition just pass me a name. For an answer to a question start your message with a question word or end it with a question mark.\nI appreciate it if you rate my answers by giving thanks to me or by typing `/rate` and one of `helpful`, `not helpful`, `correct`, `not correct` or `incorrect`.\nIf I find several things I could talk to you about I will number them. If you then choose a number I will tell you something about that option.\nYou may get funfacts with `fact` or `random` and a search term. With `more` the last query is repeated.\nYou may also send me a voice message and I'll try to understand your question."
HELP_STRING_GROUP = "To directly talk to me, address me with _"+AT_WATSON_PREFIX+"_.\nFor a definition just pass me a name. For an answer to a question start your message with a question word or end it with a question mark.\nI appreciate it if you rate my answers by giving thanks to me or by typing `/rate` and one of `helpful`, `not helpful`, `correct`, `not correct` or `incorrect`.\nIf I find several things I could talk to you about I will number them. If you then choose a number I will tell you something about that option.\nYou may get funfacts with `fact` or `random` and a search term. With `more` the last query is repeated.\n\nDon't be alarmed if I talk to you, but you didn't ask me something; I like to contribute to the conversation with little fun facts.\nYou may also send me a voice message and I'll try to understand your question."

ANSWER_INTERNAL_ERROR = ["Oh, sorry. I'm a bit confused. I need medical help...", "Uups... I have to talk to my admin", "I can't be bothered with it now. I have an internal issue. Don't take it amiss."]
ANSWER_CONTENT_TYPE_NOT_SUPPORTED = ["Um, I'm not able to make use of this...", "What's this?", "Nice, but not interesting... ;-)"]
ANSWER_NOT_ABOUT_ME = ["This chat topic is not about me, it's about the Marvel Universe...", "No comment", "I could tell you but then I'd have to kill you!", "Want your nose back? 'Cause it puts in my affairs...", "That's an interesting question. Do you still have such a question?", "I have to ask my mother, but she has Alzheimer", "I don't know", "I am not at liberty to discuss it."]
ANSWER_DIRECT_VOICE_MESSAGE_RESPONSE = ["Nice voice! Let me try to understand what you've said...", "Oh,hey! A voice message! Let me listen to it...", "One moment please..."]
ANSWER_VOICE_MESSAGE_RESPONSE = ["Okay, I understood: _\"{}\"_. Am I right?", "Did you say _\"{}\"_?", "Is _\"{}\"_ what you've said?"]
ANSWER_MISUNDERSTOOD = ["Sorry, I was wrong. Maybe you'll try it again?", "Please repeat it so I can hear your beautiful voice again... ;-)", "It seems that I was distracted of your beautiful voice...", "So, would you please speak up?", "I'm an english speaker and I don't speak any other foreign language, sorry..."]
ANSWER_FACT_TOPIC_MISSING = ["You have to tell me a topic if you want a fact", "A fact about what?", "A fact about...?!", "Use `/fact <topic>`"]
ANSWER_PLEASE = ["That's what I'm there for", "Sure!", "Please!", "Don't mention it.", "No problem!", "No probs.", "Here you go!", "Watson's your uncle!"]

ANSWER_FEEDBACK_GOOD = ["Thank you for your feedback!", "That's what I'm there for", "Sure!", "Please!", "Don't mention it.", "No problem!"]
ANSWER_FEEDBACK_BAD  = ["Thank you for your feedback! I'm still learning...", "We all make mistakes. Thank you for being honest!", "To err is human... um... wait... Let's drop the idea..", "What a pity! Maybe next time I know best...", "I did my best. Thank you for the feedback!"]

KEYWORDS_WELCOME = ['hi', 'hello', 'hey']
KEYWORDS_HELP = ['help']
KEYWORDS_NOSY_QUESTION = ['you', 'your', 'watson']
KEYWORDS_THANK_YOU = ['thank', "thanks", "thanx", "thx", "thankee", "cheers"]

COMMAND_HELP = 'help'
COMMAND_FACT = 'fact'
COMMAND_RATE = 'rate'

RATE_HELPFUL = 'helpful'
RATE_CORRECT = 'correct'
RATE_INCORRECT = 'incorrect'

WATSON_CHOICE_PRETEXT = "Would you like me to search for one of the following words?"

VOTE_ACTION_CORRECT = 'correct'
VOTE_ACTION_INCORRECT = 'incorrect'
VOTE_ACTION_HELPFUL = 'helpful'
VOTE_ACTION_NOT_HELPFUL = 'nothelpful'

# Some Telegram API constants
CHAT_TYPE_PRIVATE = 'private'
CHAT_TYPE_GROUP = 'group'
CHAT_TYPE_SUPERGROUP = 'supergroup'
CHAT_TYPE_CHANNEL = 'channel'

CONTENT_TYPE_TEXT = 'text'
CONTENT_TYPE_VOICE = 'voice'

PARSE_MODE_MARKDOWN = 'Markdown'
PARSE_MODE_HTML = 'HTML'
TELEGRAM_CHAT_ID_PREFIX = 'tg_'


# Watson chat states
lastWatsonMessageIdsPerChat = {}
messageEditorsPerChat = {}
pendingRequestsPerChat = {}
active_watson_chat_ids = set()

# ID mapping
telegramChatIDsToWatsonChatIDs = {}
watsonChatIDsToTelegramChatIDs = {}


# Some pre-compiled regular expressions
CHOICE_LIST_REGEX     = re.compile(r'\), (\d+):')
HTML_IMG_TAG_REGEX    = re.compile(r'src="(https?://.*?)"')
HTML_A_HREF_TAG_REGEX = re.compile(r'<a .*?href="(https?://.*?)".*?>(.+?)</a>')
HTML_BR_TAG_REGEX     = re.compile(r'<br\s*/?>', re.IGNORECASE)
HTML_B_TAG_REGEX      = re.compile(r'<b>(.*?)</b>', re.IGNORECASE)
HTML_STRONG_TAG_REGEX = re.compile(r'<strong>(.*?)</strong>', re.IGNORECASE)
HTML_I_TAG_REGEX      = re.compile(r'<i>(.*?)</i>', re.IGNORECASE)
HTML_EM_TAG_REGEX     = re.compile(r'<em>(.*?)</em>', re.IGNORECASE)
HTML_PRE_TAG_REGEX    = re.compile(r'<pre>(.*?)</pre>', re.IGNORECASE)
HTML_CODE_TAG_REGEX   = re.compile(r'<code>(.*?)</code>', re.IGNORECASE)

HTTP_OK = 200
HTTP_CREATED = 201

bot = telepot.Bot(API_TOKEN)
answerer = telepot.helper.Answerer(bot)

TELEGRAM_DOWNLOAD_URL = 'https://api.telegram.org/file/bot'+API_TOKEN+'/'
TELEGRAM_SUPPORTED_IMAGE_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.bmp']


def _url(path):
    if path.startswith('/') and BASE_URL.endswith('/'):
        path = path[1:]
    return BASE_URL + path


class ApiError(Exception):
    pass


### Utility methods for chat ID conversion and processing ###

def parseInt(msgId, default=-1):
    try:
        return int(msgId)
    except ValueError:
        return default


def addChatIDMapping(telegram_chat_id, watson_chat_id):
    telegramChatIDsToWatsonChatIDs[telegram_chat_id] = watson_chat_id
    watsonChatIDsToTelegramChatIDs[watson_chat_id] = telegram_chat_id


def getUsernameFromTelegramMessage(msg, default):
    try:
        username = msg['from']['first_name']
    except KeyError:
        try:
            username = msg['from']['username']
        except KeyError:
            return default

    return username


def extractWords(text):
    return [word.strip(string.punctuation) for word in text.split()]


def remove_html_markup(s):
    if s:
        out = ""
        tag = False
        quote = False

        for c in s:
            if c == '<' and not quote:
                tag = True
            elif c == '>' and not quote:
                tag = False
            elif (c == '"' or c == "'") and tag:
                quote = not quote
            elif not tag:
                out += c

        return out
    return s


def convertHtmlLineBreaksToNewlines(text):
    return re.sub(HTML_BR_TAG_REGEX, '\n', text) if text else text


def convertHtmlStylesToMarkdown(text):
    if text:
        text = re.sub(HTML_B_TAG_REGEX, '*\\1*', text)
        text = re.sub(HTML_STRONG_TAG_REGEX, '*\\1*', text)
        text = re.sub(HTML_I_TAG_REGEX, '_\\1_', text)
        text = re.sub(HTML_EM_TAG_REGEX, '_\\1_', text)
        text = re.sub(HTML_CODE_TAG_REGEX, '`\\1`', text)
        text = re.sub(HTML_PRE_TAG_REGEX, '```\\1```', text)
    return text


def convertHtmlALinksToMarkdown(text):
    return re.sub(HTML_A_HREF_TAG_REGEX, '[\\2](\\1)', text) if text else text


def convertHtmlTags(text):
    if text:
        text = convertHtmlStylesToMarkdown(text)
        text = convertHtmlLineBreaksToNewlines(text)
        text = convertHtmlALinksToMarkdown(text)
        text = remove_html_markup(text)  # Remove all other HTML tags
    return text


def extractImageURLs(textWithHtml):
    return HTML_IMG_TAG_REGEX.findall(textWithHtml) if textWithHtml else textWithHtml


def extractLinkURLs(textWithHtml):
    return HTML_A_HREF_TAG_REGEX.findall(textWithHtml) if textWithHtml else textWithHtml


def reformatChoiceList(text):
    return re.sub(CHOICE_LIST_REGEX, ')\n\\1:', text) if text else text


def answer(answers):
    return random.choice(answers)


def checkAndSendWelcomeMessageIfNecessary(chat_id, msg, chat_type=None):
    if SHOW_WELCOME_MESSAGE:
        if chat_type is None:
            chat_type = telepot.glance(msg)[1]

        if chat_type == CHAT_TYPE_PRIVATE:
            username = getUsernameFromTelegramMessage(msg, 'unknown user')
            welcome_message = WELCOME_MESSAGE_PRIVATE_CHAT.format(username)

        elif chat_type == CHAT_TYPE_GROUP:
            topic = msg['chat']['title']
            if not topic:
                topic = 'this topic'
            welcome_message = WELCOME_MESSAGE_GROUP_CHAT.format(topic)
        else:
            return

        bot.sendMessage(chat_id, welcome_message, PARSE_MODE_MARKDOWN)


def internalError(chat_id):
    bot.sendMessage(chat_id, answer(ANSWER_INTERNAL_ERROR), PARSE_MODE_MARKDOWN)


def isKeywordTrigger(keywords, words):
    return any(s in keywords for s in words)


def interceptQuestion(text, watson_chat_id, msg, chat_type, chat_id):
    # Some shortcut answers to simulate a more natural conversation
    words = extractWords(text.lower())

    if isKeywordTrigger(KEYWORDS_HELP, words) and len(words) <= 3:  # Allow 'I need help' or 'Help me!'. Assuming a request with less than 4 words isn't a valid question
        bot.sendMessage(chat_id, HELP_STRING_PRIVATE if chat_type == CHAT_TYPE_PRIVATE else HELP_STRING_GROUP, PARSE_MODE_MARKDOWN)
        return True

    if isKeywordTrigger(KEYWORDS_WELCOME, words) and len(words) < 3:  # Allow 'Hello Watson'. Assuming a request with less than 3 words isn't a valid question
        checkAndSendWelcomeMessageIfNecessary(chat_id, msg, chat_type)
        return True

    if chat_type == CHAT_TYPE_PRIVATE or text.startswith(AT_BOT_PREFIX):
        if isKeywordTrigger(KEYWORDS_THANK_YOU, words):
            bot.sendMessage(chat_id, answer(ANSWER_PLEASE))
            voteLastWatsonMessage(watson_chat_id, VOTE_ACTION_HELPFUL)
            return True

        if isKeywordTrigger(KEYWORDS_NOSY_QUESTION, words):
            bot.sendMessage(chat_id, answer(ANSWER_NOT_ABOUT_ME), PARSE_MODE_MARKDOWN)
            return True

    return False


### Telegram-Chat ###

def on_telegram_default_handler(msg):
    print("on_telegram_default_handler: ", locals())


def processTelegramBotCommand(chat_id, msg, cmd, watson_chat_id, chat_type):
    print("Bot command detected: ", locals())

    cmd = cmd.replace(AT_BOT_PREFIX[:-1], '')  # Remove @<BOT_NAME>. Remember that the AT_BOT_PREFIX constant has a space character at its end!

    cmd_lower = cmd.lower()

    if cmd_lower == COMMAND_HELP:
        bot.sendMessage(chat_id, HELP_STRING_PRIVATE if chat_type == CHAT_TYPE_PRIVATE else HELP_STRING_GROUP, PARSE_MODE_MARKDOWN)
        return

    words = extractWords(cmd_lower)

    if COMMAND_FACT in words:
        if len(words) == 1:
            bot.sendMessage(chat_id, answer(ANSWER_FACT_TOPIC_MISSING), PARSE_MODE_MARKDOWN)
        else:
            postWatsonMessage(watson_chat_id, AT_WATSON_PREFIX + cmd)
        return

    if COMMAND_RATE in words:
        negate = 'not' in words

        good = False
        action = None

        if RATE_HELPFUL in words:
            action = VOTE_ACTION_NOT_HELPFUL if negate else VOTE_ACTION_HELPFUL
            good = not negate

        elif RATE_CORRECT in words:
            action = VOTE_ACTION_INCORRECT if negate else VOTE_ACTION_CORRECT
            good = not negate

        elif RATE_INCORRECT in words:
            action = VOTE_ACTION_CORRECT if negate else VOTE_ACTION_INCORRECT
            good = negate

        if action:
            voteLastWatsonMessage(watson_chat_id, action)
            bot.sendMessage(chat_id, answer(ANSWER_FEEDBACK_GOOD if good else ANSWER_FEEDBACK_BAD))


def stripPrefix(text, prefix, ignoreCase=False):
    return text[len(prefix):].strip() if text and prefix and ((not ignoreCase and text.startswith(prefix)) or (ignoreCase and text.lower().startswith(prefix.lower()))) else text


def on_telegram_message(msg):
    """
    Callback for received Telegram messages
    :param msg: the Telegram Message data structure
    :return: void
    """
    print('on_telegram_message: ', msg)
    content_type, chat_type, chat_id = telepot.glance(msg)

    dismissReplyMarkups(chat_id)

    watson_chat_id = telegramChatIDsToWatsonChatIDs.get(chat_id)

    if watson_chat_id is None:
        on_telegram_new_chat(msg)
        watson_chat_id = telegramChatIDsToWatsonChatIDs.get(chat_id)  # Retry

    if not watson_chat_id:
        print('Could not retrieve Watson-Chat-ID for Telegram-Chat-ID {}'.format(chat_id))
        internalError(chat_id)
        return

    if content_type == CONTENT_TYPE_TEXT:
        text = msg.get('text', '').strip()

        if text.startswith('/'):  # Telegram bot command
            processTelegramBotCommand(chat_id, msg, text[1:], watson_chat_id, chat_type)
            return

        # Replace '@<BOT_NAME> ' with AT_WATSON_PREFIX
        text = re.sub(re.escape(AT_BOT_PREFIX), AT_WATSON_PREFIX, text, flags=re.IGNORECASE)

        textWithoutATPrefix = stripPrefix(text, AT_WATSON_PREFIX, ignoreCase=True)
        hasPrefix = textWithoutATPrefix != text


        if interceptQuestion(textWithoutATPrefix, watson_chat_id, msg, chat_type, chat_id):
            return


        # Prepend AT_WATSON_PREFIX if not present
        if not hasPrefix and chat_type == CHAT_TYPE_PRIVATE:
            text = AT_WATSON_PREFIX + text

        try:
            postWatsonMessage(watson_chat_id, text)

            if hasPrefix or chat_type == CHAT_TYPE_PRIVATE:
                bot.sendChatAction(chat_id, "typing")
        except Exception as e:
            print("Error while posting WatsonMessage: {}".format(e))
            traceback.print_exc()
            internalError(chat_id)

    elif content_type == CONTENT_TYPE_VOICE:
        print('Content type {}. Data: {}'.format(content_type, msg))
        voice = msg['voice']
        file_id = voice.get('file_id')  # something like 'AwADAgADFQADb_3ZBxNtcb2ddYMYAg'
        #duration = voice.get('duration')  # in seconds
        #mime_type = voice.get('mime_type')  # seen: 'audio/ogg'
        #file_size = voice.get('file_size')  # in bytes

        file = bot.getFile(file_id)
        print('File info for ID {}: {}'.format(file_id, file))
        file_path = file.get('file_path')  # something like 'voice/file_7.oga'

        # Build URL
        url = TELEGRAM_DOWNLOAD_URL + file_path
        print('Voice URL: {}'.format(url))

        bot.sendMessage(chat_id, answer(ANSWER_DIRECT_VOICE_MESSAGE_RESPONSE), PARSE_MODE_MARKDOWN)

        bot.sendChatAction(chat_id, "typing")

        try:
            transcription = speechToText(url)
            transcription = transcription.strip()
        except Exception as e:
            print('Error while transcription: {}'.format(e))
            traceback.print_exc()
            internalError(chat_id)
        else:
            if interceptQuestion(transcription, watson_chat_id, msg, chat_type, chat_id):
                return

            btns = [[InlineKeyboardButton(text='Yes', callback_data='yes'),
                     InlineKeyboardButton(text='No', callback_data='no')]]
            kb = InlineKeyboardMarkup(inline_keyboard=btns)

            pendingRequestsPerChat[chat_id] = transcription

            sent = bot.sendMessage(chat_id, answer(ANSWER_VOICE_MESSAGE_RESPONSE).format(transcription), PARSE_MODE_MARKDOWN, reply_markup=kb)

            editor = telepot.helper.Editor(bot, telepot.message_identifier(sent))
            messageEditorsPerChat[chat_id] = editor

    else:
        print('Content type {} not yet supported!', content_type)
        bot.sendMessage(chat_id, answer(ANSWER_CONTENT_TYPE_NOT_SUPPORTED), PARSE_MODE_MARKDOWN)


def on_telegram_new_chat(msg):
    print('on_telegram_new_chat: ', msg)
    content_type, chat_type, chat_id = telepot.glance(msg)

    watson_chat_id = createNewWatsonChat(chat_id)

    if watson_chat_id >= 0:
        addChatIDMapping(chat_id, watson_chat_id)
        active_watson_chat_ids.add(watson_chat_id)

        checkAndSendWelcomeMessageIfNecessary(chat_id, msg, chat_type)


def dismissReplyMarkups(chat_id):
    editor = messageEditorsPerChat.get(chat_id)
    if editor:
        editor.editMessageReplyMarkup(reply_markup=None)
        del messageEditorsPerChat[chat_id]


def on_telegram_callback_query(msg):
    print('on_telegram_callback_query: ', msg)
    query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')

    bot.answerCallbackQuery(query_id, text='Got it. One moment...')

    dismissReplyMarkups(chat_id)

    watson_chat_id = telegramChatIDsToWatsonChatIDs.get(chat_id)

    if watson_chat_id:
        if query_data == 'no':
            bot.sendMessage(chat_id, answer(ANSWER_MISUNDERSTOOD))
            return
        elif query_data == 'yes':
            req = pendingRequestsPerChat.get(chat_id)

            if chat_id in pendingRequestsPerChat:
                del pendingRequestsPerChat[chat_id]

            if req:
                query_data = req
            else:
                bot.sendMessage(chat_id, "Sorry, I forgot your question. Would you please ask again?")
                return

        postWatsonMessage(watson_chat_id, AT_WATSON_PREFIX + query_data)
        bot.sendChatAction(chat_id, "typing")
    else:
        print('Could not retrieve Watson-Chat-ID for Telegram-Chat-ID {}'.format(chat_id))
        internalError(chat_id)



### Watson-Chat-API ###

def sendPhotos(telegram_chat_id, urls):
    if urls:
        for url in urls:
            # FIX: Remove some fancy stuff from the image URLs
            idx = url.find("/revision/")
            if idx >= 0:
                url = url[:idx]

            path = urllib.parse.urlsplit(url).path
            filename = path.split('/')[-1]   # Extract filename from URL
            ext = os.path.splitext(path)[1]  # Extract file extension from URL

            print("Image URL: {}, extracted filename: {}, extension: {}".format(url, filename, ext))

            fh = urllib.request.urlopen(url)

            if ext not in TELEGRAM_SUPPORTED_IMAGE_FILE_EXTENSIONS:
                try:
                    # Try to guess an other file extension
                    mimetype = fh.info().get_content_type()  #gettype()
                    ext = mimetypes.guess_extension(mimetype, strict=False)
                except:
                    traceback.print_exc()
                else:
                    if ext == ".jpe":  # Work around
                        ext = ".jpg"

                    #ext = imghdr.what(fh.read())  # Try to guess file extension
                    if not filename.endswith(ext):
                        filename += ext

                    print("Image URL: {}, MIME-Type: {}, guessed extension: {}, fixed filename: {}".format(url, mimetype, ext, filename))

            if ext in TELEGRAM_SUPPORTED_IMAGE_FILE_EXTENSIONS:
                try:
                    bot.sendChatAction(telegram_chat_id, 'upload_photo')
                    bot.sendPhoto(telegram_chat_id, (filename, fh))
                except Exception as e:
                    print("Error while sending image file {}. Sending as document instead...".format(filename))
                    try:
                        bot.sendChatAction(telegram_chat_id, 'upload_document')
                        fh = urllib.request.urlopen(url)  # re-open file
                        bot.sendDocument(telegram_chat_id, (filename, fh))
                    except Exception as e:
                        print("Exception: {}".format(e))
                        traceback.print_exc()
                        internalError(telegram_chat_id)


def processPreOrPostText(telegram_chat_id, text):
    if text:
        urls = extractImageURLs(text)
        sendPhotos(telegram_chat_id, urls)

        text = convertHtmlTags(text)
        if text:
            bot.sendMessage(telegram_chat_id, text, PARSE_MODE_MARKDOWN)


def on_watson_chat_message(watson_chat_id, data):
    print('on_watson_chat_message: {}'.format(data))

    telegram_chat_id = watsonChatIDsToTelegramChatIDs.get(watson_chat_id)
    if telegram_chat_id is not None:
        system_text_pre = data.get('system_text_pre')

        processPreOrPostText(telegram_chat_id, system_text_pre)

        text = data.get('text')
        if text:
            kb = None

            # Provide a choice keyboard
            if WATSON_CHOICE_PRETEXT.lower() in system_text_pre.lower():
                # Extract number of items
                num = len(re.compile(r'\d+: .+? \(').findall(text))
                if num > 0:
                    dismissReplyMarkups(telegram_chat_id)

                    btns = [[InlineKeyboardButton(text=str(i + 1), callback_data=str(i + 1)) for i in range(num)]]
                    kb = InlineKeyboardMarkup(inline_keyboard=btns)

            text = convertHtmlLineBreaksToNewlines(text)
            text = reformatChoiceList(text)
            sent = bot.sendMessage(telegram_chat_id, text, reply_markup=kb)

            if kb is not None:
                editor = telepot.helper.Editor(bot, telepot.message_identifier(sent))
                messageEditorsPerChat[telegram_chat_id] = editor

        processPreOrPostText(telegram_chat_id, data.get('system_text_post'))


def getAllWatsonMessages(watson_chat_id):
    return getWatsonMessages(watson_chat_id, -1)


def getNewWatsonMessages(watson_chat_id):
    lastWatsonMessageId = lastWatsonMessageIdsPerChat.get(watson_chat_id, -1)
    return getWatsonMessages(watson_chat_id, lastWatsonMessageId)


def getWatsonMessages(watson_chat_id, lastWatsonMessageId=-1):
    path = '/chat/{:d}/answers/'.format(watson_chat_id)
    if lastWatsonMessageId >= 0:
        path += '{:d}/new'.format(lastWatsonMessageId)

    url = _url(path)

    resp = requests.get(url)

    if resp.status_code != HTTP_OK:
        raise ApiError('GET {} {}'.format(url, resp.status_code))

    response = resp.json()

    if response and response['status'] != HTTP_OK:
        print('getWatsonMessages: Invalid response for URL {}. Removing watson_chat_id {} from active_watson_chat_ids...'.format(url, watson_chat_id))
        active_watson_chat_ids.discard(watson_chat_id)

    # Update lastWatsonMessageId:
    if response and response.get('count', 0) > 0:
        active_watson_chat_ids.discard(watson_chat_id)

        for message in response.get('answers'):
            watsonMsgId = message.get('id', -1)
            watsonMsgId = parseInt(watsonMsgId)

            if watsonMsgId > lastWatsonMessageId:
                lastWatsonMessageId = watsonMsgId

    lastWatsonMessageIdsPerChat[watson_chat_id] = lastWatsonMessageId
    return response


def postWatsonMessage(watson_chat_id, msg):
    url = _url('/chat/post/')

    data = {
        'chat': watson_chat_id,
        'text': msg
    }

    print("Sending data to Watson: ", data)

    resp = requests.post(url, data=data)

    if resp.status_code != HTTP_CREATED:
        raise ApiError('POST URL={}, Code={}, Body={}'.format(url, resp.status_code, resp.text))

    active_watson_chat_ids.add(watson_chat_id)


def speechToText(audioFileUrl):
    url = _url('/speech/totext/url/')

    data = {'url': audioFileUrl}

    print("Sending data to STT: ", data)

    resp = requests.post(url, data=data)

    if resp.status_code != HTTP_OK:
        raise ApiError('POST URL={}, Code={}, Body={}'.format(url, resp.status_code, resp.text))

    json = resp.json()
    print("Got response from SpeechToText: ", json)

    return json.get('text', '')


def voteLastWatsonMessage(watson_chat_id, action):
    message_id = lastWatsonMessageIdsPerChat.get(watson_chat_id, -1)
    voteWatsonMessage(message_id, action)


def voteWatsonMessage(message_id, action):
    if message_id < 0: return

    url = _url('/message/{:d}/vote/'.format(message_id))

    data = {'action': action}

    print("Sending vote data to server: ", data, ", URL: ", url)

    resp = requests.post(url, data=data)

    if resp.status_code != HTTP_OK:
        raise ApiError('POST URL={}, Code={}, Body={}'.format(url, resp.status_code, resp.text))


def createNewWatsonChat(external_id=0):
    url = _url('/chat/create/')

    resp = requests.post(url, data={
        'external_id': TELEGRAM_CHAT_ID_PREFIX + str(external_id)
        })

    if resp.status_code != HTTP_CREATED:
        raise ApiError('POST URL={}, Code={}, Body={}'.format(url, resp.status_code, resp.text))

    response = resp.json()

    if response and response.get('status', 0) != HTTP_CREATED:
        print('createNewWatsonChat: Invalid response for URL {}.'.format(url))

    if response and response.get('id', -1) >= 0:
        return int(response.get('id', -1))

    return -1


def pollWatsonChatMessages(watson_chat_id):
    resp = getNewWatsonMessages(watson_chat_id)
    if resp and resp.get('count', 0) > 0:
        newMsgs = resp.get('answers')
        for msg in newMsgs:
            on_watson_chat_message(watson_chat_id, msg)


def pollAllWatsonChatMessages():
    for watson_chat_id in active_watson_chat_ids.copy():  # copy for thread-safety
        try:
            pollWatsonChatMessages(watson_chat_id)
        except Exception as e:
            print("Error while polling for watson message updates: ", e)
            traceback.print_exc()



def call_repeatedly(interval, func, *args):
    stopped = Event()

    def loop():
        while not stopped.wait(interval):  # the first call is in `interval` secs
            func(*args)
    t = Thread(target=loop)
    t.setDaemon(True)
    t.start()
    return stopped.set



# Persistence for chat information:

def saveState():
    print('Saving state...')
    try:
        if len(telegramChatIDsToWatsonChatIDs) > 0:
            fd = codecs.open(LAST_CHAT_IDS_FILE, 'w', 'utf-8')

            fd.write("# --- This file is created automatically! No need to edit. ---\r\n")
            fd.write("# Format: Telegram-Chat-ID <SPACE> Watson-Chat-ID <SPACE> LastWatsonMessageID\r\n")

            for telegram_chat_id, watson_chat_id in sorted(telegramChatIDsToWatsonChatIDs.items()):
                lastWatsonMessageId = lastWatsonMessageIdsPerChat.get(watson_chat_id, -1)
                fd.write("%s %s %s\r\n" % (telegram_chat_id, watson_chat_id, lastWatsonMessageId))
            fd.close()
            print('State saved.')
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
        traceback.print_exc()


def reloadState():
    if os.path.isfile(LAST_CHAT_IDS_FILE):
        print('Restoring state...')
        try:
            fd = codecs.open(LAST_CHAT_IDS_FILE, 'r', 'utf-8')
            for line in fd.readlines():
                line = line.strip()
                line = line.lower()

                if not line:
                    continue

                if "#" in line:
                    if line.startswith("#"):
                        continue
                    line = line[0:line.find("#")]
                    line = line.rstrip()

                line = line.split(" ", 2)
                if not len(line) == 3:
                    print("Invalid line format: " + line)
                    continue

                try:
                    telegram_chat_id = int(line[0].strip())
                    watson_chat_id = int(line[1].strip())
                    lastWatsonMessageId = int(line[2].strip())

                    lastWatsonMessageIdsPerChat[watson_chat_id] = lastWatsonMessageId
                    addChatIDMapping(telegram_chat_id, watson_chat_id)
                except ValueError:
                    print("Invalid line format: " + line)

            fd.close()
            print('Last state restored.')
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            traceback.print_exc()


if __name__ == '__main__':
    reloadState()

    # Catch SIGINT and SIGTERM signals and save current state
    def signal_handler(signal, frame):
        saveState()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    cancel_func = call_repeatedly(2, pollAllWatsonChatMessages)  # poll every 2 seconds

    # The following line will stop the repeated calls:
    #cancel_func()

    # This call blocks forever
    bot.message_loop({
            'chat': on_telegram_message,
            'callback_query': on_telegram_callback_query,
            #'edited_chat': on_telegram_chat_edited,
            #'edited_chat': on_telegram_message,
            #'inline_query': on_telegram_inline_query,
            #'chosen_inline_result': on_chosen_inline_result,
            None: on_telegram_default_handler
        }, relax=0.5, run_forever='Listening ...')
