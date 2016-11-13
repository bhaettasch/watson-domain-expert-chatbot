import random
import re
from datetime import timedelta

from django.utils import timezone

from bwb import watson
from bwb.models import KBFactTypePattern, ChatRecentFunFact


class FunFactGenerator:
    def __init__(self, phrase, chat, entity):
        self.phrase = phrase
        self.chat = chat
        self.entity = entity

    def next(self, no_recent_facts=True):
        fact_type = self.entity.fact.type
        # Find patterns for the right type that have not been seen for this fact in this chat recently
        matching_patterns = KBFactTypePattern.objects.filter(fact_type=fact_type)

        if no_recent_facts:
            matching_patterns = matching_patterns.exclude(
                    chatrecentfunfact__chat=self.chat,
                    chatrecentfunfact__fact=self.entity.fact,
                    chatrecentfunfact__creation_timestamp__gte=timezone.now() - timedelta(hours=watson.RECENT_FACT_HOURS)
                )

        count = matching_patterns.count()
        if count > 0:
            # Randomly try facts until a funfact was correctly created (all necessary facts available)
            pattern_indices = list(range(count))
            random.shuffle(pattern_indices)
            for i in pattern_indices:
                pattern = matching_patterns.all()[i]
                name = text = re.sub(r'<[^>]+>', '', self.entity.name, count=0)
                funfact = pattern.substitute(name, self.entity.fact.facts)
                if funfact is not None:
                    funfact_representation = "{} [{}]".format(funfact, self.entity.fact.type)
                    ChatRecentFunFact.objects.create(
                        chat=self.chat,
                        fact=self.entity.fact,
                        pattern=pattern
                    )
                    return funfact_representation
        return None
