import random

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import PluginError, FormatError
from stepic_plugins.quizzes.executable_base import JailedCodeFailed, run, settings


class DatasetQuiz(BaseQuiz):
    name = 'dataset'

    class Schemas:
        source = {
            'code': str
        }
        reply = {
            'text': str
        }
        dataset = {
            'file': str
        }

    def __init__(self, source):
        super().__init__(source)
        self.code = source.code

    def async_init(self):
        def check_sample():
            try:
                self.run_edyrun('test')
            except JailedCodeFailed as e:
                raise FormatError(str(e))

        def check_random():
            try:
                dataset, clue = self.generate()
                reply = self.run_edyrun('solve', data=dataset,
                                        output_limit=settings.DATASET_QUIZ_SIZE_LIMIT)
                score, hint = self.check(reply, clue, throw=True)
            except JailedCodeFailed as e:
                raise FormatError(str(e))
            if score != 1:
                hint = '\nHint: {}'.format(hint) if hint else ''
                raise FormatError('score of answer is {score} instead of 1.{hint}'.format(
                    score=score,
                    hint=hint))

        check_random()
        check_sample()

        try:
            sample_dataset, sample_output = self.run_edyrun('sample')
        except JailedCodeFailed as e:
            raise FormatError(str(e))

        return {
            'static_content': {
                'time_limit': 5 * 60,
                'sample_dataset': sample_dataset,
                'sample_output': sample_output
            }
        }

    def clean_reply(self, reply, dataset):
        return reply.text.strip()

    def check(self, reply, clue, throw=False):
        try:
            score, hint = self.run_edyrun('score', data=(reply, clue))
            return score, hint
        except (JailedCodeFailed, ValueError, TypeError) as e:
            if throw:
                raise JailedCodeFailed(str(e))
            return False

    def generate(self):
        seed = random.randrange(10 ** 9)
        try:
            dataset, clue = self.run_edyrun('generate', seed=seed,
                                            output_limit=settings.DATASET_QUIZ_SIZE_LIMIT)

            if (isinstance(dataset, dict) and 'file' in dataset and
                    not isinstance(dataset['file'], (str, bytes))):
                raise TypeError("dataset has 'file' but it is not one of (str, bytes)")
            return dataset, clue
        except (JailedCodeFailed, ValueError, TypeError) as e:
            raise PluginError(e)

    def run_edyrun(self, command, data=None, **kwargs):
        files = []
        return run(command, self.code, data, files, **kwargs)
