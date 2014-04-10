import random

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError


class SimpleChoiceQuiz(BaseQuiz):
    # The name(type) of the quiz. Use dasherized-case.
    name = 'simple-choice'

    # Specification of JSON message format.
    class Schemas:
        """Source is the data needed to create quiz instance.

        Here it is a list of options which are marked as correct
        or incorrect.

        Example source:
        {
            'options': [
                {
                    'text': 'An option',
                    'is_correct': false
                },
                {
                    'text': 'Another option',
                    'is_correct': true
                }
            ]
        }
        """
        source = {
            'options': [{'is_correct': bool, 'text': str}]
        }

        """Dataset is presented to the student for solving.

        Here it is a list of options without correctness marks.

        Example Dataset:
        {
            'options': ['An option', 'Another option']
        }
        """
        dataset = {
            'options': [str]
        }

        """Reply is the student's solution to the dataset.

        Here it is a list of correctness marks, ordered as options in dataset.

        Example reply:
        {
            'choices': [true, false]
        }
        """
        reply = {
            'choices': [bool]
        }

    def __init__(self, source):
        """Initializes quiz instance from parsed source and raises `FormatError` if source is invalid."""

        super().__init__(source)
        # `source` is parsed, that is, it is an object with `options` field, and not a dict.
        self.options = source.options
        correct_options = [option for option in self.options if option.is_correct]
        # Can't check via Schemas.source that there is exactly one correct option,
        # so do it here.
        if len(correct_options) != 1:
            raise FormatError("Exactly one option must be correct")

    def generate(self):
        """Generates one random dataset and a clue for it and returns (dataset, clue) pair."""

        options = self.options[:]  # copy options for shuffling
        random.shuffle(options)

        # Dataset should be a dict conforming to Schemas.dataset.
        dataset = {
            'options': [option.text for option in options]
        }
        # Clue can be any serializable object. It is never send to the frontend.
        clue = [option.is_correct for option in options]
        return dataset, clue

    def clean_reply(self, reply, dataset):
        """Checks that reply is valid and transforms it before `check`."""

        # `choices` and `dataset` are parsed.
        # Make sure that they have the same length and that exactly one choice is correct.
        choices = reply.choices
        if len(choices) != len(dataset.options):
            raise FormatError("Reply has a wrong length")
        if choices.count(True) != 1:
            raise FormatError("Reply has more than one choice")

        return choices

    def check(self, reply, clue):
        """Checks reply and return either (score, hint) pair or just score"""
        # Sore should be True or false. It also may be a number in range [0.0, 1.0].
        # Hint is optional and should be a string.
        return reply == clue
