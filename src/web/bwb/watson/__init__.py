from bwb.models import Message

CONTEXT_SIZE = 3
BOT_ADDRESS_PREFIX = "@watson"
KEYWORD_THRESHOLD = 0.4
KEYWORD_THRESHOLD_INTERJECTION = 0.9
QUESTION_WORDS = ['who', 'what', 'which', 'when', 'to whom', 'why', 'where', 'how']
MAXIMUM_PHRASE_LENGTH = 4
ANSWER_SENTENCE_COUNT = 2
PHRASE_QUALITY_THRESHOLD = 0.25

ACTION_SOURCE_DIRECT = 1
ACTION_SOURCE_CONTEXT = 2

RECENT_FACT_HOURS = 10

# messages
HELP_TEXT = '''
To directly talk to me address me with @Watson.<br>
For a definition just pass me a name.<br>
For an answer to a question start your message with a question word or end it with a question mark.<br>
<br>
I appreciate it if you rate my answers.
To have my answer read aloud hit the speaker button.<br>
If I find several things I could talk to you about I will number them. If you then address me with just a number I will tell you something about that option.<br>
You may search for an image using <code>image</code> or a video on youtube using the keyword <code>video</code> and get funfacts with <code>fact</code> or <code>random</code> and a search term. With <code>more</code> the last query is repeated.<br>
<br>
Don't be alarmed if I talk to you, but you didn't ask me anything; I like to contribute to the conversation with little fun facts.<br>
'''

SUFFICIENT = ["<i>Sorry, I was not able to find a sufficient answer. Nevertheless, here is the best guess I could find:</i>", "<i>Um, I'm not quite sure but maybe this is what you want:</i>", "<i>Unfortunately, I'm not a know-it-all, so try my best guess:</i>", "<i>It's on the tip of my tongue but it doesn't cross my mind... Maybe this?</i>"]
NO_ANSWER = "Sorry, I was not able to find an answer."
NO_DIRECT_ANSWER = "I was not able to find a direct answer to your question."
NOT_UNDERSTOOD = "Sorry, I did not understand your question"
NO_CONNECTION = "Sorry, cannot connect to computing instance."
NUMBER_PROMPT = "<i>Sorry. I don't know what word to search for. Please give a valid number:</i><br>"
OK = "OK. Searching for <b>{}</b>"
CHOICE = "<i>Would you like me to search for one of the following words?</i>"
UNSURE = "Sorry, I'm not totally sure how I can help you. Could you rephrase your question, please?"
NO_YOUTUBE = "Could not connect to youtube."
NO_RESULT = "Sorry, I couldn't find anything like that."
NO_FUNFACT = "Sorry, I don't know any funfacts about "
NO_IMAGE = "Sorry, I couldn't find any images about "
NO_REPEAT = "Sorry, there is no recent action to repeat"
