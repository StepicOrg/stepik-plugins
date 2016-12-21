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
        nonblank_second_parts = [pair.second for pair in self.pairs if pair.second]
        if (len(first_parts) != len(set(first_parts)) or
                len(nonblank_second_parts) != len(set(nonblank_second_parts))):
            raise FormatError("Ambiguous pairs")

    def clean_reply(self, reply, dataset):
        if list(sorted(reply.ordering)) != list(range(len(reply.ordering))):
            raise FormatError("Reply ordering is not a correct permutation")
        return reply.ordering

    def check(self, reply, clue):
        inverse_perm, blanks = clue
        # there is only one correct permutation for non-blank unique elements
        nonblank_perm = [image for i, image in enumerate(inverse_perm) if image not in blanks]
        reply_nonblank_perm = [image for i, image in enumerate(reply) if image not in blanks]
        # any permutation for blank elements is correct
        blank_indexes = [i for i, image in enumerate(inverse_perm) if image in blanks]
        reply_blank_indexes = [i for i, image in enumerate(reply) if image in blanks]
        return nonblank_perm == reply_nonblank_perm and blank_indexes == reply_blank_indexes

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
        blanks = [i for i, pair in enumerate(dataset['pairs']) if not pair['second']]
        return dataset, (inverse_permutation, blanks)
