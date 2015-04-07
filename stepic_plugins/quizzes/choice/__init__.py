import random
import collections

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError
from stepic_plugins.utils import clean_html


class ChoiceQuiz(BaseQuiz):
    name = 'choice'

    class Schemas:
        source = {
            'is_multiple_choice': bool,
            'is_always_correct': bool,
            'sample_size': int,
            'preserve_order': bool,
            'options': [{
                'is_correct': bool,
                'text': str
            }]
        }

        reply = {
            'choices': [bool]
        }

        dataset = {
            'is_multiple_choice': bool,
            'options': [str]
        }

    def __init__(self, source):
        super().__init__(source)
        self.is_multiple_choice = source.is_multiple_choice
        self.is_always_correct = source.is_always_correct
        self.sample_size = source.sample_size
        self.preserve_order = source.preserve_order
        self.options = source.options
        for option in self.options:
            option.text = clean_html(option.text)

        if self.is_always_correct:
            if self.sample_size > len(self.options):
                raise FormatError('Sample size is greater then the number of available options')
        else:
            min_correct, max_correct = self.get_min_max_correct()
            if min_correct > max_correct:
                raise FormatError('Not enough answers')

        results = collections.defaultdict(set)
        for option in self.options:
            results[option.text].add(option.is_correct)

        for result in results.values():
            if len(result) > 1:
                raise FormatError('Ambiguous options')

    def clean_reply(self, reply, dataset):
        choices = reply.choices
        if len(choices) != len(dataset.options):
            raise FormatError('Reply has the wrong length')
        if not self.is_multiple_choice and sum(choices) != 1:
            raise FormatError('Only one choice should be `true`')
        return choices

    def check(self, reply, clue):
        if self.is_always_correct:
            score = True
        else:
            wrong = sum(x ^ y for x, y in zip(clue, reply))
            score = (wrong == 0)

        return score

    def generate(self):
        correct = [(i, o) for (i, o) in enumerate(self.options) if o.is_correct]
        wrong = [(i, o) for (i, o) in enumerate(self.options) if not o.is_correct]

        if self.is_always_correct:
            all_options = wrong + correct
            sample = random.sample(all_options, self.sample_size)
        else:
            min_correct, max_correct = self.get_min_max_correct()
            correct_quantity = random.randrange(min_correct, max_correct + 1)
            wrong_quantity = self.sample_size - correct_quantity
            sample = random.sample(correct, correct_quantity) + random.sample(wrong, wrong_quantity)

        if self.preserve_order:
            sample = sorted(sample)
        else:
            random.shuffle(sample)

        sample = [o for (i, o) in sample]
        dataset = {
            'is_multiple_choice': self.is_multiple_choice,
            'options': [option.text for option in sample]
        }
        clue = [option.is_correct for option in sample]
        return dataset, clue

    def partition_options(self):
        correct = [(i, o) for (i, o) in enumerate(self.options) if o.is_correct]
        wrong = [(i, o) for (i, o) in enumerate(self.options) if not o.is_correct]
        return correct, wrong

    def get_min_max_correct(self):
        correct, wrong = self.partition_options()
        if self.is_multiple_choice:
            max_correct = min(len(correct), self.sample_size)
            min_correct = max(1 if len(correct) else 0, self.sample_size - len(wrong))
        else:
            max_correct = min(len(correct), 1)
            min_correct = max(1, self.sample_size - len(wrong))
        return min_correct, max_correct
