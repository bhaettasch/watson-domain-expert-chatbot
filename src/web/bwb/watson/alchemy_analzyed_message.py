from django.conf import settings
from watson_developer_cloud import AlchemyLanguageV1


class AlchemyAnalyzedMessage:
    """
    Wrapper to analyze a text using Alchemy API.
    Provides some convenience functions to access the returned data
    """

    def __init__(self, text):
        self.alchemy_language = AlchemyLanguageV1(api_key=settings.API_KEY_ALCHEMY)
        self.raw = self.alchemy_language.combined(text=text)

    def keywords(self, threshold=0.0):
        """
        Get a list of keywords for this message
        Optionally, the list can be limited to keywords of a given relevance or higher

        :param threshold: minimal relevance. Default is 0.0, so all keywords are returned
        :return: a list of (keyword-name, relevance)-pairs
        """
        keywords = []
        for keyword in self.raw['keywords']:
            relevance = float(keyword['relevance'])
            if relevance > threshold:
                keywords.append((keyword['text'], relevance))
        return keywords
