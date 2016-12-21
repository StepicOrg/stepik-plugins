import textwrap
import unittest

from unittest.mock import patch

from .. import CodeQuiz
from stepic_plugins import settings
from stepic_plugins.constants import WARNING_NEWLINE
from stepic_plugins.exceptions import FormatError
from stepic_plugins.utils import create_attachment


class CodeQuizTest(unittest.TestCase):
    def setUp(self):
        self.default_source = {
            'code': textwrap.dedent("""
            def generate():
                return ['2 2\\n', '5 7\\n']

            def solve(dataset):
                a, b = dataset.split()
                return str(int(a) + int(b))

            def check(reply, clue):
                return int(reply) == int(clue)
            """),
            'execution_time_limit': 5,
            'execution_memory_limit': 256,
            'samples_count': 1,
            'templates_data': '',
            'is_time_limit_scaled': False,
            'is_memory_limit_scaled': False,
            'manual_time_limits': [],
            'manual_memory_limits': [],
            'test_archive': []
        }
        self.supplementary = None

    @property
    def quiz(self):
        return CodeQuiz(CodeQuiz.Source(self.default_source), supplementary=self.supplementary)

    def clean_reply(self, reply):
        return self.quiz.clean_reply(CodeQuiz.Reply(reply), None)._original

    def test_invalid_source(self):
        dumb_attachment = create_attachment('attach.zip', 'content')
        diff = [
            {'samples_count': -1},
            {'execution_time_limit': 0},
            {'execution_time_limit': 31},
            {'execution_memory_limit': 31},
            {'execution_memory_limit': 513},
            {'manual_time_limits': [{'language': 'python3', 'time': 0}]},
            {'manual_time_limits': [{'language': 'unknown', 'time': 5}]},
            {'manual_memory_limits': [{'language': 'python3', 'memory': 31}]},
            {'manual_memory_limits': [{'language': 'unknown', 'memory': 64}]},
            {'samples_count': -1},
            {'test_archive': [dumb_attachment, dumb_attachment]},
        ]

        for bad_source in [dict(self.default_source, **d) for d in diff]:
            with self.assertRaises(FormatError):
                CodeQuiz(CodeQuiz.Source(bad_source))

    def test_async_init_no_warnings(self):
        quiz = CodeQuiz(CodeQuiz.Source(self.default_source))

        async_result = quiz.async_init()

        self.assertEqual(async_result['warnings'], [])

    def test_async_init_warnings(self):
        self.default_source['code'] = textwrap.dedent("""
        def generate():
            return ['2 2', '5 7']

        def solve(dataset):
            a, b = dataset.split()
            return str(int(a) + int(b))

        def check(reply, clue):
            return int(reply) == int(clue)
        """)
        quiz = CodeQuiz(CodeQuiz.Source(self.default_source))

        async_result = quiz.async_init()

        self.assertIn(WARNING_NEWLINE, async_result['warnings'])

    def test_get_time_limit(self):
        quiz = CodeQuiz(CodeQuiz.Source(self.default_source))

        limits = quiz.language_limits('python3')

        assert limits['TIME'] == 5

    @patch.dict('stepic_plugins.quizzes.code.Languages.default_time_limit_factors',
                c=1.05, python3=2.5)
    def test_get_scaled_time_limit(self):
        self.default_source['is_time_limit_scaled'] = True
        quiz = CodeQuiz(CodeQuiz.Source(self.default_source))

        limits = quiz.language_limits('c')
        assert limits['TIME'] == 5

        limits = quiz.language_limits('python3')
        assert limits['TIME'] == 13

    def test_get_manual_time_limit(self):
        self.default_source['manual_time_limits'] = [{'language': 'python3', 'time': 10}]
        quiz = CodeQuiz(CodeQuiz.Source(self.default_source))

        limits = quiz.language_limits('python3')

        assert limits['TIME'] == 10

    def test_get_memory_limit(self):
        quiz = CodeQuiz(CodeQuiz.Source(self.default_source))

        limits = quiz.language_limits('python3')

        # +1MB hack for sudo
        assert limits['MEMORY'] == 256 * 1024 * 1024

    @patch.dict('stepic_plugins.quizzes.code.Languages.default_memory_limit_factors',
                c=1, python3=1.3)
    def test_get_scaled_memory_limit(self):
        self.default_source['is_memory_limit_scaled'] = True
        quiz = CodeQuiz(CodeQuiz.Source(self.default_source))

        limits = quiz.language_limits('c')
        # +1MB hack for sudo
        assert limits['MEMORY'] == 256 * 1024 * 1024

        limits = quiz.language_limits('python3')
        # +1MB hack for sudo
        assert limits['MEMORY'] == 333 * 1024 * 1024

    def test_get_manual_memory_limit(self):
        self.default_source['manual_memory_limits'] = [{'language': 'python3', 'memory': 128}]
        quiz = CodeQuiz(CodeQuiz.Source(self.default_source))

        limits = quiz.language_limits('python3')

        # +1MB hack for sudo
        assert limits['MEMORY'] == 128 * 1024 * 1024

    def test_generate_empty_tests_list(self):
        quiz = CodeQuiz(CodeQuiz.Source(self.default_source))
        ret = quiz.generate_tests(quiz.zip_archive)
        assert ret == []

    def test_generate_not_zip_archive_test(self):
        self.default_source['test_archive'] = [{'name': 'test', 'type': 'test', 'size': 42,
                                                'url': 'some_url',
                                                'content': 'It\'s not a zip archive}'}]
        quiz = CodeQuiz(CodeQuiz.Source(self.default_source))
        ret = quiz.generate_tests(quiz.zip_archive)
        assert ret == []

    def test_generate_hello_word_test(self):
        self.default_source['test_archive'] = [{'type': 'application/zip',
            'size': 328, 'url': '',
            'content': 'attachment$base64$UEsDBAoAAAAAAIaJSU\
            c26Kp2EAAAABAAAAACABwAMDFVVAkAAzzLF1aHyxdWdXgLAA\
            EE6AMAAAToAwAASGVsbG8gV29ybGQhISEhClBLAwQKAAAAAA\
            CSiUlH+zemvxAAAAAQAAAABwAcADAxLmNsdWVVVAkAA1TLF1\
            aHyxdWdXgLAAEE6AMAAAToAwAASSBsb3ZlIEJlbGFydXMhCl\
            BLAQIeAwoAAAAAAIaJSUc26Kp2EAAAABAAAAACABgAAAAAAA\
            EAAAC0gQAAAAAwMVVUBQADPMsXVnV4CwABBOgDAAAE6AMAAF\
            BLAQIeAwoAAAAAAJKJSUf7N6a/EAAAABAAAAAHABgAAAAAAA\
            EAAAC0gUwAAAAwMS5jbHVlVVQFAANUyxdWdXgLAAEE6AMAAA\
            ToAwAAUEsFBgAAAAACAAIAlQAAAJ0AAAAAAA==', 'name': 'testing.zip'}]

        quiz = CodeQuiz(CodeQuiz.Source(self.default_source))
        ret = quiz.generate_tests(quiz.zip_archive)
        assert ret == [['Hello World!!!!', 'I love Belarus!']]


    def test_generate_mac_tests(self):
        self.default_source['test_archive'] = [{'type': 'application/zip',
            'size': 1898, 'url': '',
            'content': 'attachment$base64$UEsDBBQACAAIAOFucUcA\
            AAAAAAAAAAAAAAABABAAMVVYDAD1C0tWhgdLVvUBFAALz0gsUU\
            gsSlWozC9VSMnPzEtXyEgtSrUHAFBLBwjzbzysGgAAABgAAABQ\
            SwMECgAAAAAA6nFxRwAAAAAAAAAAAAAAAAkAEABfX01BQ09TWC\
            9VWAwARwxLVkcMS1b1ARQAUEsDBBQACAAIAOFucUcAAAAAAAAA\
            AAAAAAAMABAAX19NQUNPU1gvLl8xVVgMAPULS1aGB0tW9QEUAG\
            NgFWNnYGJg8E1MVvAPVohQgAKQGAMnEBsB8QYgBvEfMRAFHENC\
            gqBMkI4ZQOyFpoQRIS6anJ+rl1hQkJOqV1iaWJSYV5KZl8pQqG\
            9gYGBobWpmkmSQmJZk7Z6fn56TGlNhZOCcUZSfmwrSYW3mauJk\
            5upkpGtkbOKia2LsZKprYW5ipGvm5GpkaW5uYmrm4soAAFBLBw\
            hDcWmkkwAAAOIAAABQSwMEFAAIAAgA4W5xRwAAAAAAAAAAAAAA\
            AAYAEAAxLmNsdWVVWAwA9QtLVoYHS1b1ARQAMwQAUEsHCLfv3I\
            MDAAAAAQAAAFBLAwQUAAgACADhbnFHAAAAAAAAAAAAAAAAEQAQ\
            AF9fTUFDT1NYLy5fMS5jbHVlVVgMAPULS1aGB0tW9QEUAGNgFW\
            NnYGJg8E1MVvAPVohQgAKQGAMnEBsB8QYgBvEfMRAFHENCgqBM\
            kI4ZQOyFpoQRIS6anJ+rl1hQkJOqV1iaWJSYV5KZl8pQqG9gYG\
            BobWpmkmSQmJZk7Z6fn56TGlNhZOCcUZSfmwrSYW3mauJk5upk\
            pGtkbOKia2LsZKprYW5ipGvm5GpkaW5uYmrm4soAAFBLBwhDcW\
            mkkwAAAOIAAABQSwMEFAAIAAgA4W5xRwAAAAAAAAAAAAAAAAEA\
            EAAyVVgMAPULS1aGB0tW9QEUAIvML1VILEpVyMsvUagEssszUv\
            PADJBgRmleelElAFBLBwjbKn6XHgAAACMAAABQSwMEFAAIAAgA\
            4W5xRwAAAAAAAAAAAAAAAAwAEABfX01BQ09TWC8uXzJVWAwA9Q\
            tLVoYHS1b1ARQAY2AVY2dgYmDwTUxW8A9WiFCAApAYAycQGwHx\
            BiAG8R8xEAUcQ0KCoEyQjhlA7IWmhBEhLpqcn6uXWFCQk6pXWJ\
            pYlJhXkpmXylCob2BgYGhtamaSZJCYlmTtnp+fnpMaU2Fk4JxR\
            lJ+bCtJhbeZq4mTm6mSka2Rs4qJrYuxkqmthbmKka+bkamRpbm\
            5iaubiygAAUEsHCENxaaSTAAAA4gAAAFBLAwQUAAgACADhbnFH\
            AAAAAAAAAAAAAAAABgAQADIuY2x1ZVVYDAD1C0tWhgdLVvUBFA\
            AzAgBQSwcIDb7VGgMAAAABAAAAUEsDBBQACAAIAOFucUcAAAAA\
            AAAAAAAAAAARABAAX19NQUNPU1gvLl8yLmNsdWVVWAwA9QtLVo\
            YHS1b1ARQAY2AVY2dgYmDwTUxW8A9WiFCAApAYAycQGwHxBiAG\
            8R8xEAUcQ0KCoEyQjhlA7IWmhBEhLpqcn6uXWFCQk6pXWJpYlJ\
            hXkpmXylCob2BgYGhtamaSZJCYlmTtnp+fnpMaU2Fk4JxRlJ+b\
            CtJhbeZq4mTm6mSka2Rs4qJrYuxkqmthbmKka+bkamRpbm5iau\
            biygAAUEsHCENxaaSTAAAA4gAAAFBLAQIVAxQACAAIAOFucUfz\
            bzysGgAAABgAAAABAAwAAAAAAAAAAEC0gQAAAAAxVVgIAPULS1\
            aGB0tWUEsBAhUDCgAAAAAA6nFxRwAAAAAAAAAAAAAAAAkADAAA\
            AAAAAAAAQP1BWQAAAF9fTUFDT1NYL1VYCABHDEtWRwxLVlBLAQ\
            IVAxQACAAIAOFucUdDcWmkkwAAAOIAAAAMAAwAAAAAAAAAAEC0\
            gZAAAABfX01BQ09TWC8uXzFVWAgA9QtLVoYHS1ZQSwECFQMUAA\
            gACADhbnFHt+/cgwMAAAABAAAABgAMAAAAAAAAAABAtIFtAQAA\
            MS5jbHVlVVgIAPULS1aGB0tWUEsBAhUDFAAIAAgA4W5xR0Nxaa\
            STAAAA4gAAABEADAAAAAAAAAAAQLSBtAEAAF9fTUFDT1NYLy5f\
            MS5jbHVlVVgIAPULS1aGB0tWUEsBAhUDFAAIAAgA4W5xR9sqfp\
            ceAAAAIwAAAAEADAAAAAAAAAAAQLSBlgIAADJVWAgA9QtLVoYH\
            S1ZQSwECFQMUAAgACADhbnFHQ3FppJMAAADiAAAADAAMAAAAAA\
            AAAABAtIHzAgAAX19NQUNPU1gvLl8yVVgIAPULS1aGB0tWUEsB\
            AhUDFAAIAAgA4W5xRw2+1RoDAAAAAQAAAAYADAAAAAAAAAAAQL\
            SB0AMAADIuY2x1ZVVYCAD1C0tWhgdLVlBLAQIVAxQACAAIAOFu\
            cUdDcWmkkwAAAOIAAAARAAwAAAAAAAAAAEC0gRcEAABfX01BQ0\
            9TWC8uXzIuY2x1ZVVYCAD1C0tWhgdLVlBLBQYAAAAACQAJAFsC\
            AAD5BAAAAAA=', 'name': 'tests2 (3).zip'}]

        quiz = CodeQuiz(CodeQuiz.Source(self.default_source))
        ret = quiz.generate_tests(quiz.zip_archive)
        assert ret == [["What are you doing here?", "1"],
                       ["You are not you when you are hungry", "2"]]

    def test_generate_shuffle_tests(self):
        self.default_source['test_archive'] = [{'type': 'application/zip',
            'size': 5806, 'url': '',
            'content':'attachment$base64$UEsDBAoAAAAAAAt9eke379\
            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',
            'name': 'many.zip'}]

        quiz = CodeQuiz(CodeQuiz.Source(self.default_source))
        ret = quiz.generate_tests(quiz.zip_archive)
        want = [[str(x), str(x)] for x in range(1, 21 + 1)]
        assert ret == want

    @unittest.skipIf('java' not in settings.COMPILERS, "Java compiler isn't configured")
    def test_java_main_class(self):
        self.supplementary = {'tests': [['2 2\n', '4'], ['5 7\n', '12']]}
        main_reply = {
            'language': 'java',
            'code': textwrap.dedent("""
                import java.util.*;

                class Main {
                    public static void main(String[] args) {
                        Scanner in = new Scanner(System.in);
                        System.out.println(in.nextInt() + in.nextInt());
                    }
                }
                """),
        }
        public_main_code = main_reply['code'].replace("class Main", "public class Main")
        public_main_reply = dict(main_reply, code=public_main_code)

        for reply in [main_reply, public_main_reply]:
            score, feedback = self.quiz.check(self.clean_reply(reply), None)

            self.assertTrue(score)
            self.assertFalse(feedback, feedback)

    @unittest.skipIf('java' not in settings.COMPILERS, "Java compiler isn't configured")
    def test_java_no_public_class(self):
        reply = {
            'language': 'java',
            'code': textwrap.dedent("""
                public class Solution {
                    public static void main(String[] args) {
                    }
                }
                """),
        }

        score, feedback = self.quiz.check(self.clean_reply(reply), None)

        self.assertFalse(score)
        self.assertIn(CodeQuiz.CE_MESSAGE, feedback)
        self.assertIn(CodeQuiz.CE_PUBLIC_CLASS_MESSAGE, feedback)

    @unittest.skipIf('java' not in settings.COMPILERS, "Java compiler isn't configured")
    def test_java_entry_point(self):
        self.supplementary = {'tests': [['2 2\n', '4'], ['5 7\n', '12']]}
        reply = {
            'language': 'java',
            'code': textwrap.dedent("""
                import java.util.*;

                class Solution {
                    static void run() {
                        Scanner in = new Scanner(System.in);
                        System.out.println(in.nextInt() + in.nextInt());
                    }
                }

                class Entry {
                    public static void main(String[] args) {
                        new Solution().run();
                    }
                }
                """),
        }

        score, feedback = self.quiz.check(self.clean_reply(reply), None)

        self.assertTrue(score)
        self.assertFalse(feedback, feedback)
