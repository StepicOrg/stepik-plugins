import random

from ..base import BaseQuiz
from ..exceptions import FormatError


class SimpleChoice(BaseQuiz):
    name = 'simple-choice'

    class Schemas:
        source = {
            'options': [{'is_correct': bool, 'text': str}]
        }

        dataset = {
            'options': [str]
        }

        reply = {
            'choices': [bool]
        }

    def __init__(self, source):
        super().__init__(source)
        self.options = source.options
        correct_options = [option for option in self.options if option.is_correct]
        if len(correct_options) != 1:
            raise FormatError("Exactly one option must be correct")

    def generate(self):
        options = self.options[:]  # copy options for shuffling
        random.shuffle(options)
        dataset = {
            'options': [option.text for option in options]
        }
        clue = [option.is_correct for option in options]
        return dataset, clue

    def clean_reply(self, reply, dataset):
        choices = reply.choices
        if len(choices) != len(dataset.options):
            raise FormatError("Reply has a wrong length")
        if choices.count(True) != 1:
            raise FormatError("Reply has more than one choice")

        return choices

    def check(self, reply, clue):
        return reply == clue, ''
