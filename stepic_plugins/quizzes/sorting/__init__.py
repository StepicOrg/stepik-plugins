import random

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError


class SortingQuiz(BaseQuiz):
    name = 'sorting'

    class Schemas:
        source = {'options': [str]}
        reply = {'ordering': [int]}
        dataset = {'options': [str]}

    def __init__(self, source):
        super().__init__(source)
        self.options = source.options

    def clean_reply(self, reply, dataset):
        if sorted(reply.ordering) != list(range(len(dataset.options))):
            raise FormatError('Reply should be a permutation of numbers 0..(len(dataset.options) - 1)')
        return reply.ordering

    def check(self, reply, clue):
        return reply == clue

    def generate(self):
        options = list(enumerate(self.options))
        random.shuffle(options)
        permutation, dataset = zip(*options)
        inverse_permutation, _ = zip(*sorted(enumerate(permutation), key=lambda x: x[1]))
        return {'options': list(dataset)}, list(inverse_permutation)

