import random

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError


class MatchingQuiz(BaseQuiz):
    name = 'matching'

    class Schemas:
        source = {
            'preserve_firsts_order': bool,
            'pairs': [{
                'first': str,
                'second': str
            }]
        }
        reply = {'ordering': [int]}
        dataset = {
            'pairs': [{
                'first': str,
                'second': str
            }]
        }

    def __init__(self, source):
        super().__init__(source)
        self.preserve_firsts_order = source.preserve_firsts_order
        self.pairs = source.pairs
        if not self.pairs:
            raise FormatError("Empty pairs")

        first_parts = [pair.first for pair in self.pairs]
        second_parts = [pair.second for pair in self.pairs]
        if len(first_parts) != len(set(first_parts)) or len(second_parts) != len(set(second_parts)):
            raise FormatError("Ambiguous pairs")

    def clean_reply(self, reply, dataset):
        return reply.ordering

    def check(self, reply, clue):
        return reply == clue

    def generate(self):
        pairs = list(self.pairs)
        if not self.preserve_firsts_order:
            random.shuffle(pairs)
        l = len(pairs)
        permutation = list(range(l))
        random.shuffle(permutation)
        dataset = {'pairs': []}
        for i in range(l):
            dataset['pairs'].append({
                'first': pairs[i].first,
                'second': pairs[permutation[i]].second
            })
        inverse_permutation, _ = zip(*sorted(enumerate(permutation), key=lambda x: x[1]))
        return dataset, inverse_permutation

