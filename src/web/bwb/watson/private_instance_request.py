import json

import requests
from django.conf import settings

from bwb.watson.helper import Helper


class PrivateInstanceRequest:
    """
    Wrapper to request an answer from the private instance
    """

    def __init__(self, text):
        data = {'question': {'questionText': text}}
        self.r = requests.post(settings.PRIVATE_INSTANCE_URL,
                               json=data,
                               auth=(settings.PRIVATE_INSTANCE_USER, settings.PRIVATE_INSTANCE_PW)
                               )
        if self.status() == 200:
            self.answer_json = self.r.json()

    def status(self):
        return self.r.status_code

    def raw_answer(self):
        return json.dumps(self.answer_json)

    def answer_object(self):
        """
        Get an answer object
        :return: the best ranked answer object with text (if applicable) or None
        """

        answer_object = {}
        evidences = self.answer_json['question']['evidencelist']
        for evidence in evidences:
            if len(evidences) > 1 and 'title' in evidence and 'Infobox' in evidence['title']:
                continue
            if 'text' in evidence.keys() and evidence['text'] != '':
                replaced_text = evidence['text'].replace('TALK PAGE.', '')
                text_sentences_split = Helper.split_into_sentences(replaced_text)
                answer_object['text'] = ''
                for sent in text_sentences_split:
                    answer_object['text'] += sent+' '
                    if len(answer_object['text']) >= 140:
                        break

                answer_object['text'] = answer_object['text'].strip().encode('unicode_escape')

                answer_object['confidence'] = float(evidence['value'])
                if answer_object['text'] == '':
                    return None
                else:
                    return answer_object
        return None

    def item_count(self):
        return self.answer_json['question']['items']
