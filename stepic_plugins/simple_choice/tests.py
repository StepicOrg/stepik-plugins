from ..base import quiz_wrapper_factory
from ..exceptions import FormatError
from ..tests import InitTest, GenerateTest, CleanReplyTest, CheckTest
from . import SimpleChoice

QuizClass = quiz_wrapper_factory(SimpleChoice)
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
