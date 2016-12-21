import os
import textwrap
import unittest

from unittest import TestCase
from codejail import jail_code

from stepic_plugins.executable_base import Arena
from stepic_plugins.quizzes.code import CodeQuiz, CodeRunner, Languages


class SandboxTest(TestCase):
    language = ''
    extension = ''
    code_dir = None
    limits = {
        "TIME": 3,
        "MEMORY": 256 * 1024 * 1024
    }

    def setUp(self):
        self.arena = Arena().__enter__()
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.code_path = os.path.join(self.base_path, 'code', self.code_dir or self.language)
        self.secret = os.path.join(self.base_path, 'secret.txt')

        self.source = {
            'code': textwrap.dedent("""
                def generate():
                    return ['2 2\\n', '5 -7\\n']

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
        self.supplementary = {'tests': [['2 2\n', '4'], ['5 -7\n', '-2']]}

    def tearDown(self):
        self.arena.__exit__(None, None, None)

    def get_runner(self, name, limits=None):
        assert self.language
        assert self.extension

        name = "{}.{}".format(name, self.extension)
        name = os.path.join(self.code_dir or self.language, name)
        code = self.get_code(name)
        runner = CodeRunner(self.arena, code, self.language, limits or self.limits)
        assert runner.compilation_success, "{name}: failed to compile\n{ce}".format(
            name=name,
            ce=runner.compilation_result.stderr.decode()
        )
        return runner

    def get_code(self, name):
        path = os.path.join(self.base_path, 'code', name)
        with open(path) as f:
            code = f.read()
        code = code.replace('{{ SECRET_FILE }}', self.secret)
        return code

    def check_output(self, name, expected_output, dataset=''):
        runner = self.get_runner(name)
        result = runner.run(dataset)
        self.assertEqual(result.status, 0,
                         "run time error: {} {}".format(result.stdout, result.stderr))
        self.assertEqual(result.stdout.decode().strip(), str(expected_output).strip())

    def check_forbidden(self, name, dataset=''):
        runner = self.get_runner(name)
        result = runner.run(dataset)
        self.assertNotEqual(result.status, 0)
        return result

    def submit(self, code):
        reply = {
            'language': self.language,
            'code': code,
        }
        quiz = CodeQuiz(CodeQuiz.Source(self.source), supplementary=self.supplementary)
        clean_reply = quiz.clean_reply(CodeQuiz.Reply(reply), None)._original
        return quiz.check(clean_reply, None)

    def test_basic(self):
        if self.language:
            self.check_output('basic', 42)

    def test_cant_read_secret(self):
        if self.language:
            self.check_forbidden('read_secret')

    def test_a_plus_b(self):
        a_plus_b_dir = os.path.join(self.code_path, 'a_plus_b')
        if not os.path.isdir(a_plus_b_dir):
            self.skipTest("There is no 'a_plus_b' directory for {}".format(self.language))
        for sol_name in os.listdir(a_plus_b_dir):
            sol_path = os.path.join(a_plus_b_dir, sol_name)
            with open(sol_path) as fd:
                code = fd.read()

            score, feedback = self.submit(code)

            self.assertTrue(score)
            self.assertFalse(feedback, feedback)


class TestConfiguration(SandboxTest):
    def test_configuration(self):
        def assert_configured(cmd):
            self.assertTrue(jail_code.is_configured(cmd), cmd + " is not configured")

        assert_configured('python')
        assert_configured('user_code')

        for compiler in Languages.compiled:
            assert_configured('compile_' + compiler)
        assert_configured('compile_' + Languages.JAVA)

        for interpreter in Languages.interpreted:
            assert_configured('run_' + interpreter)
        assert_configured('run_' + Languages.JAVA)


class TestPython(SandboxTest):
    language = Languages.PYTHON
    extension = 'py'

    def cant_read(self, name):
        result = self.check_forbidden(name)
        timed_out = 'Connection timed out' in result.stderr.decode() or result.time_limit_exceeded
        self.assertTrue(timed_out)

    def test_cant_read_google(self):
        self.cant_read('read_google')

    def test_cant_read_localhost(self):
        self.cant_read('read_localhost')

    def test_can_read_stepic(self):
        self.check_output('read_stepic', 200)


class TestC(SandboxTest):
    language = Languages.C
    extension = 'c'


class TestCPP(SandboxTest):
    language = Languages.CPP
    extension = 'cpp'


class TestCPP11(SandboxTest):
    language = Languages.CPP11
    extension = 'cpp'


class TestAsm32(SandboxTest):
    language = Languages.ASM32
    extension = 'S'

    @unittest.skip("not implemented")
    def test_cant_read_secret(self):
        pass


class TestAsm64(SandboxTest):
    language = Languages.ASM64
    extension = 'S'

    @unittest.skip("not implemented")
    def test_cant_read_secret(self):
        pass


class TestHaskell(SandboxTest):
    language = Languages.HASKELL
    extension = 'hs'


class TestHaskell710(SandboxTest):
    language = Languages.HASKELL_7_10
    extension = 'hs'
    code_dir = 'haskell'


class TestJava(SandboxTest):
    language = Languages.JAVA
    extension = 'java'


class TestJava8(SandboxTest):
    language = Languages.JAVA8
    extension = 'java'
    code_dir = 'java'


class TestOctave(SandboxTest):
    language = Languages.OCTAVE
    extension = 'm'

    def test_symbolic_package(self):
        runner = self.get_runner('symbolic')
        result = runner.run('')
        self.assertEqual(result.status, 0,
                         "run time error: {} {}".format(result.stdout, result.stderr))
        self.assertIn("OctSymPy: Communication established", result.stdout.decode(),
                      "Octave failed to communicate with Python SymPy")


class TestR(SandboxTest):
    language = Languages.R
    extension = 'R'


class TestClojure(SandboxTest):
    language = Languages.CLOJURE
    extension = 'clj'


class TestMonoCS(SandboxTest):
    language = Languages.MONO_CS
    extension = 'cs'


class TestJavaScript(SandboxTest):
    language = Languages.JAVA_SCRIPT
    extension = 'js'


class TestRust(SandboxTest):
    language = Languages.RUST
    extension = 'rs'


class TestRuby(SandboxTest):
    language = Languages.RUBY
    extension = 'rb'


class TestScala(SandboxTest):
    language = Languages.SCALA
    extension = 'scala'
