from unittest import TestCase

from .exceptions import FormatError


class QuizSpecsTest(TestCase):
    def specs(self):
        return []

    def is_format_error(self, obj):
        if isinstance(obj, type) and issubclass(obj, Exception):
            assert issubclass(obj, FormatError), 'init should raise format error'
            return True
        return False

    def flat_specs(self):
        def union(*ditcs):
            ret = {}
            for d in ditcs:
                ret.update(d)
            return ret

        def make_message(s):
            return {'msg': str(s)}

        # support recursion?
        for spec in self.specs():
            if '->' in spec:
                copy = {k: v for k, v in spec.items() if k != '->'}
                for inner in spec['->']:
                    spec = union(copy, inner)
                    yield union(make_message(spec), spec)
            else:
                yield union(make_message(spec), spec)


class InitTest(QuizSpecsTest):
    """ spec format:
    {
        'quiz_class': A class to test,
        'source': argument of __init__,
        'output': Exception or asserting function
    }
    """

    def test_init_specs(self):
        for spec in self.flat_specs():
            output = spec['output']
            msg = spec['msg']
            lazy_ret = lambda: spec['quiz_class'](spec['source'])
            if self.is_format_error(output):
                with self.assertRaises(output, msg=msg):
                    lazy_ret()
            else:
                assert callable(output), 'output should be a callable or an exception'
                ret = lazy_ret()
                output(ret)


class CleanReplyTest(QuizSpecsTest):
    """ spec format:
    {
        'quiz': A quiz object,
        'reply': argument of clean_reply,
        'dataset': argument of clean_reply,
        'output': Exception or expected return value
    }
    """

    def test_clean_reply_specs(self):
        for spec in self.flat_specs():
            output = spec['output']
            msg = spec['msg']
            lazy_ret = lambda: spec['quiz'].clean_reply(spec['reply'], spec['dataset'])
            if self.is_format_error(output):
                with self.assertRaises(output, msg=msg):
                    lazy_ret()
            else:
                ret = lazy_ret()
                self.assertEqual(ret, output, msg)


class CheckTest(QuizSpecsTest):
    """ spec format:
    {
        'quiz': A quiz object,
        'reply': argument of check(should be cleaned),
        'clue': argument of check,
        'output': expected return value
    }
    """

    def test_check_specs(self):
        for spec in self.flat_specs():
            self.assertEqual(spec['quiz'].check(spec['reply'], spec['clue']),
                             spec['output'])


class GenerateTest(QuizSpecsTest):
    """ spec format:
    {
        'quiz': A Quiz object,
        'solve': A function which returns correct reply
    }
    """

    def test_generate_specs(self):
        for spec in self.flat_specs():
            quiz = spec['quiz']
            dataset, clue = quiz.generate()
            raw_reply = spec['solve'](dataset, clue)
            reply = quiz.clean_reply(raw_reply, dataset)
            self.assertTrue(quiz.check(reply, clue)[0])
