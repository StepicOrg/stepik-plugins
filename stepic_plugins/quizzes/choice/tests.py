import unittest

from . import ChoiceQuiz
from stepic_plugins.exceptions import FormatError


class ChoiceQuizTest(unittest.TestCase):
    def setUp(self):
        self.default_options = [
            {'is_correct': False, 'text': 'wrong1'},
            {'is_correct': False, 'text': 'wrong2'},
            {'is_correct': False, 'text': 'wrong3'},
            {'is_correct': False, 'text': 'wrong4'},
            {'is_correct': True, 'text': 'correct1'},
            {'is_correct': True, 'text': 'correct2'},
            {'is_correct': True, 'text': 'correct3'},
            {'is_correct': True, 'text': 'correct4'},
        ]

        self.default_source = {'is_multiple_choice': False,
                               'is_always_correct': False,
                               'preserve_order': False,
                               'sample_size': 4,
                               'options': self.default_options}

        sources = [
            {'is_multiple_choice': is_multiple_choice,
             'is_always_correct': is_always_correct,
             'preserve_order': preserve_order,
             'sample_size': 4,
             'options': self.default_options}

            for is_multiple_choice in [True, False]
            for is_always_correct in [True, False]
            for preserve_order in [True, False]
        ]
        self.quizzes = [ChoiceQuiz(ChoiceQuiz.Source(source)) for source in sources]


class ChoiceQuizInitTest(ChoiceQuizTest):
    def test_invalid_sources(self):
        diff = [
            {'options': []},
            {'sample_size': 10},
            {'sample_size': 10, 'is_always_correct': True},
            {'options': self.default_options[:4]},  # all wrong
            {'options': self.default_options[4:]},  # all correct
            {'options': self.default_options[:2] + self.default_options[4:6]}  # 2 wrong 2 correct
        ]

        for bad_source in [dict(self.default_source, **d) for d in diff]:
            with self.assertRaises(FormatError):
                quiz = ChoiceQuiz(ChoiceQuiz.Source(bad_source))

    def test_valid_sources(self):
        diff = [
            {'is_multiple_choice': True,
             'options': self.default_options[:4]},
            {'is_multiple_choice': True,
             'options': self.default_options[4:]}
        ]
        for good_source in [dict(self.default_source, **d) for d in diff]:
            ChoiceQuiz(ChoiceQuiz.Source(good_source))

    def test_sanitized_options(self):
        self.default_source['options'] = [
            {'is_correct': False, 'text': '<script>alert("XSS");</script>'},
            {'is_correct': True, 'text': '<p hack_attr="42">correct</p>'},
        ]
        self.default_source['sample_size'] = 2

        quiz = ChoiceQuiz(ChoiceQuiz.Source(self.default_source))

        assert quiz.options[0].text == 'alert("XSS");'
        assert quiz.options[1].text == '<p>correct</p>'


class ChoiceQuizCleanReplyTest(ChoiceQuizTest):
    def setUp(self):
        super().setUp()
        self.quiz = ChoiceQuiz(ChoiceQuiz.Source(self.default_source))
        self.dataset = ChoiceQuiz.Dataset({'is_multiple_choice': self.quiz.is_multiple_choice,
                                           'options': ['Foo', 'bar']})

    def test_invalid_reply(self):
        with self.assertRaises(FormatError):
            self.quiz.clean_reply(
                reply=ChoiceQuiz.Reply({'choices': [True]}), dataset=self.dataset)

        with self.assertRaises(FormatError):
            self.quiz.clean_reply(
                reply=ChoiceQuiz.Reply({'choices': [True, True]}), dataset=self.dataset)

    def test_options_extracted_from_reply(self):
        cleaned_reply = self.quiz.clean_reply(
            reply=ChoiceQuiz.Reply({'choices': [True, False]}), dataset=self.dataset)

        self.assertEqual(cleaned_reply, [True, False])


class ChoiceQuizCheckTest(ChoiceQuizTest):
    def test_single_choice(self):
        quiz = ChoiceQuiz(ChoiceQuiz.Source(self.default_source))
        self.assertIs(quiz.check([True, False, False], [True, False, False]), True)
        self.assertIs(quiz.check([False, True, False], [True, False, False]), False)

    def test_multiple_choice(self):
        quiz = ChoiceQuiz(ChoiceQuiz.Source(dict(self.default_source, is_multiple_choice=True)))
        self.assertIs(quiz.check([True, True, False], [True, True, False]), True)
        self.assertIs(quiz.check([True, False, True], [True, True, False]), False)

    def test_anyone_correct(self):
        quiz = ChoiceQuiz(ChoiceQuiz.Source(dict(self.default_source, is_always_correct=True)))
        self.assertIs(quiz.check([True, False, False], [True, False, False]), True)
        self.assertIs(quiz.check([False, True, False], [True, False, False]), True)


class ChoiceQuizGenerateTest(ChoiceQuizTest):
    def test_generate(self):
        def get_correct_wrong(quiz, dataset):
            def f(correctness):
                return {o.text for o in quiz.options if o.is_correct == correctness}

            return f(True), f(False)

        def should_have_correct_length(quiz, dataset, clue):
            self.assertEqual(len(dataset.options), quiz.sample_size)
            self.assertEqual(len(clue), quiz.sample_size)

        def should_have_correct_clue(quiz, dataset, clue):
            correct, _ = get_correct_wrong(quiz, dataset)
            for text, correctness in zip(dataset.options, clue):
                self.assertEqual(correctness, text in correct)

        def should_have_correct_choice(quiz, dataset, clue):
            correct, wrong = get_correct_wrong(quiz, dataset)
            self.assertTrue(quiz.is_always_correct or quiz.is_multiple_choice or
                            (set(dataset.options) & correct))

        def should_have_wrong_choice(quiz, dataset, clue):
            correct, wrong = get_correct_wrong(quiz, dataset)
            self.assertTrue(quiz.is_always_correct or quiz.is_multiple_choice or
                            (set(dataset.options) & wrong))

        def should_preserve_order(quiz, dataset, clue):
            texts = [o.text for o in quiz.options]
            positions = [texts.index(t) for t in dataset.options]
            self.assertTrue(not quiz.preserve_order or positions == sorted(positions))

        predicates = [should_have_correct_length, should_have_correct_choice,
                      should_have_wrong_choice, should_preserve_order]

        for quiz_instance in self.quizzes:
            dataset_dict, clue_instance = quiz_instance.generate()
            dataset_instance = ChoiceQuiz.Dataset(dataset_dict)
            for pred in predicates:
                pred(quiz_instance, dataset_instance, clue_instance)


class ChoiceQuizSolveTest(ChoiceQuizTest):
    def test_all(self):
        def solve(quiz, dataset):
            if quiz.is_always_correct:
                choices = [True] + [False] * (len(dataset.options) - 1)
            else:
                choices = ['correct' in o for o in dataset.options]
            return {'choices': choices}

        for quiz in self.quizzes:
            dataset, clue = quiz.generate()
            dataset = ChoiceQuiz.Dataset(dataset)
            reply = ChoiceQuiz.Reply(solve(quiz, dataset))
            cleaned_reply = quiz.clean_reply(reply, dataset)
            self.assertIs(quiz.check(cleaned_reply, clue), True)
