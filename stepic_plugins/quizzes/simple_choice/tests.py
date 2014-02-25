from stepic_plugins.base import quiz_wrapper_factory
from stepic_plugins.exceptions import FormatError
from stepic_plugins.tests import InitTest, GenerateTest, CleanReplyTest, CheckTest
from . import SimpleChoiceQuiz

QuizClass = quiz_wrapper_factory(SimpleChoiceQuiz)
quiz = QuizClass({
    'options': [
        {'is_correct': True, 'text': 'A'},
        {'is_correct': False, 'text': 'B'},
    ]
})


class SimpleChoiceInitTest(InitTest):
    def specs(self):
        return [
            {
                'quiz_class': QuizClass,
                'output': FormatError,
                '->': [
                    {
                        'source': {
                            'options': [
                                {'is_correct': True, 'text': 'A'},
                                {'is_correct': True, 'text': 'B'},
                            ]
                        },
                    },
                    {
                        'source': {
                            'options': [
                                {'is_correct': False, 'text': 'A'},
                                {'is_correct': False, 'text': 'B'},
                            ]
                        },
                    }
                ]
            }
        ]


class SimpleChoiceGenerateTest(GenerateTest):
    def specs(self):
        return [
            {
                'quiz': quiz,
                'solve': lambda dataset, clue: {
                    'choices': [x == 'A' for x in dataset['options']]
                }
            }
        ]


class SimpleChoiceCleanReplyTest(CleanReplyTest):
    def specs(self):
        return [
            {
                'quiz': quiz,
                'dataset': {'options': ['A', 'B']},
                '->': [
                    {
                        'reply': {'choices': [True]},
                        'output': FormatError
                    },
                    {
                        'reply': {'choices': [True, True]},
                        'output': FormatError
                    },
                    {
                        'reply': {'choices': [True, False]},
                        'output': [True, False]
                    },
                ]
            }
        ]


class SimpleChoiceCheckTest(CheckTest):
    def specs(self):
        return [
            {
                'quiz': quiz,
                'clue': [True, False],
                '->': [
                    {
                        'reply': [True, False],
                        'output': (True, '')
                    },
                    {
                        'reply': [False, True],
                        'output': (False, '')
                    }
                ]
            }
        ]
