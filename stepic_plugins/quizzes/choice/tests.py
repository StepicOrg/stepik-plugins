import unittest

from . import ChoiceQuiz
from stepic_plugins.exceptions import FormatError


class ChoiceQuizTest(unittest.TestCase):
    def setUp(self):
        self.default_options = [
            {'is_correct': False, 'text': 'wrong1', 'feedback': 'feedback1'},
            {'is_correct': False, 'text': 'wrong2', 'feedback': '   '},
            {'is_correct': False, 'text': 'wrong3', 'feedback': ''},
            {'is_correct': False, 'text': 'wrong4', 'feedback': ''},
            {'is_correct': True, 'text': 'correct1', 'feedback': ' feedback5 \n '},
            {'is_correct': True, 'text': 'correct2', 'feedback': ''},
            {'is_correct': True, 'text': 'correct3', 'feedback': ''},
            {'is_correct': True, 'text': 'correct4', 'feedback': ''},
        ]

        self.default_source = {'is_multiple_choice': False,
                               'is_always_correct': False,
                               'preserve_order': False,
                               'is_html_enabled': True,
                               'is_options_feedback': False,
                               'sample_size': 4,
                               'options': self.default_options}

        sources = [
            {'is_multiple_choice': is_multiple_choice,
             'is_always_correct': is_always_correct,
             'preserve_order': preserve_order,
             'sample_size': 4,
             'is_html_enabled': True,
             'is_options_feedback': False,
             'options': self.default_options}

            for is_multiple_choice in [True, False]
            for is_always_correct in [True, False]
            for preserve_order in [True, False]
        ]
        self.quizzes = [ChoiceQuiz(ChoiceQuiz.Source(source)) for source in sources]

    @property
    def quiz(self):
        return ChoiceQuiz(ChoiceQuiz.Source(self.default_source))


class ChoiceQuizInitTest(ChoiceQuizTest):
    def test_invalid_sources(self):
        diff = [
            {'options': []},
            {'sample_size': 10},
            {'sample_size': 10, 'is_always_correct': True},
            {'options': self.default_options[:4]},  # all wrong
            {'options': self.default_options[4:]},  # all correct
            {'options': self.default_options[:2] + self.default_options[4:6]},  # 2 wrong 2 correct
            {'sample_size': 2, 'options': [  # equal text but different results
                {'is_correct': False, 'text': 'correct', 'feedback': ''},
                {'is_correct': True, 'text': 'correct', 'feedback': ''},
            ]},
            {'sample_size': 0, 'options': self.default_options},
        ]

        for bad_source in [dict(self.default_source, **d) for d in diff]:
            with self.assertRaises(FormatError):
                quiz = ChoiceQuiz(ChoiceQuiz.Source(bad_source))

    def test_valid_sources(self):
        diff = [
            {'is_multiple_choice': True,
             'options': self.default_options[:4]},
            {'is_multiple_choice': True,
             'options': self.default_options[4:]},
            # Do not check the number of correct options if is_always_correct
            {'options': self.default_options[:4], 'is_always_correct': True},
        ]
        for good_source in [dict(self.default_source, **d) for d in diff]:
            ChoiceQuiz(ChoiceQuiz.Source(good_source))

    def test_sanitized_options(self):
        self.default_source['options'] = [
            {'is_correct': False, 'text': '<script>alert("XSS");</script>', 'feedback': ''},
            {'is_correct': True, 'text': '<p hack_attr="42">correct</p>', 'feedback': ''},
        ]
        self.default_source['sample_size'] = 2

        quiz = ChoiceQuiz(ChoiceQuiz.Source(self.default_source))

        assert quiz.options[0].text == '&lt;script&gt;alert("XSS");&lt;/script&gt;'
        assert quiz.options[1].text == '<p>correct</p>'

    def test_incorrect_html_options(self):
        self.default_source['options'] = [
            {'is_correct': False, 'text': 'a<b', 'feedback': ''},
            {'is_correct': True, 'text': 'b>a', 'feedback': ''},
        ]
        self.default_source['sample_size'] = 2
        with self.assertRaises(FormatError):
            ChoiceQuiz(ChoiceQuiz.Source(self.default_source))

    def test_correct_html_options(self):
        self.default_source['options'] = [
            {'is_correct': False, 'text': 'a < b', 'feedback': ''},
            {'is_correct': True, 'text': 'b > a', 'feedback': ''},
        ]
        self.default_source['sample_size'] = 2
        ChoiceQuiz(ChoiceQuiz.Source(self.default_source))

    def test_escaped_options_html_disabled(self):
        self.default_source['options'] = [
            {'is_correct': False, 'text': '<script>alert("XSS");</script>', 'feedback': ''},
            {'is_correct': True, 'text': 'A<LinkedList<Object>> a;', 'feedback': ''},
        ]
        self.default_source['sample_size'] = 2
        self.default_source['is_html_enabled'] = False

        quiz = ChoiceQuiz(ChoiceQuiz.Source(self.default_source))

        assert quiz.options[0].text == '&lt;script&gt;alert(&quot;XSS&quot;);&lt;/script&gt;'
        assert quiz.options[1].text == 'A&lt;LinkedList&lt;Object&gt;&gt; a;'


class ChoiceQuizCleanReplyTest(ChoiceQuizTest):
    def setUp(self):
        super().setUp()
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
        self.assertIs(quiz.check([False, False, True], [0, 1, 4]), True)
        # Get global feedback for one incorrect option
        score, feedback = quiz.check([True, False, True], [0, 1, 4])
        self.assertIs(score, False)
        self.assertEqual(feedback, "feedback1")
        # Get global feedback for multiple incorrect options
        score, feedback = quiz.check([True, False, False], [0, 1, 4])
        self.assertIs(score, False)
        self.assertEqual(feedback, "feedback1\nfeedback5")
        # Get global feedback for multiple incorrect options and skip empty feedback
        score, feedback = quiz.check([True, True, False], [0, 1, 4])
        self.assertIs(score, False)
        self.assertEqual(feedback, "feedback1\nfeedback5")

    def test_multiple_choice(self):
        quiz = ChoiceQuiz(ChoiceQuiz.Source(dict(self.default_source, is_multiple_choice=True)))
        self.assertIs(quiz.check([False, False, True], [0, 1, 4]), True)
        self.assertEqual(quiz.check([False, False, False], [0, 1, 5]), (False, ""))

    def test_anyone_correct(self):
        quiz = ChoiceQuiz(ChoiceQuiz.Source(dict(self.default_source, is_always_correct=True)))
        self.assertIs(quiz.check([False, False, True], [0, 1, 4]), True)
        self.assertIs(quiz.check([False, True, False], [0, 1, 4]), True)

    def test_backward_compatible_clue(self):
        quiz = ChoiceQuiz(ChoiceQuiz.Source(self.default_source))
        self.assertIs(quiz.check([False, False, True], [False, False, True]), True)
        self.assertIs(quiz.check([False, False, True], [True, False, True]), False)
        self.assertIs(quiz.check([False, False, True], [False, True, False]), False)
        self.assertIs(quiz.check([False, False, True], [True, True, True]), False)
        self.assertIs(quiz.check([False, False, True], [True, True, False]), False)

    def test_options_feedback(self):
        self.default_source['is_options_feedback'] = True

        score, feedback = self.quiz.check([True, False, True], [0, 1, 4])

        self.assertIs(score, False)
        expected_feedback = {'options_feedback': ["feedback1", "", ""]}
        self.assertEqual(feedback, expected_feedback)

        score, feedback = self.quiz.check([True, False, False], [0, 1, 4])

        self.assertIs(score, False)
        expected_feedback = {'options_feedback': ["feedback1", "", "feedback5"]}
        self.assertEqual(feedback, expected_feedback)


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
            for text, index in zip(dataset.options, clue):
                self.assertEqual(quiz.options[index].text, text)

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

        predicates = [should_have_correct_length, should_have_correct_clue,
                      should_have_correct_choice, should_have_wrong_choice,
                      should_preserve_order]

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
