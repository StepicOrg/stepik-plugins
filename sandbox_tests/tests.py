import os

from unittest import TestCase
from codejail import jail_code

from stepic_plugins.executable_base import Arena
from stepic_plugins.quizzes.code import CodeRunner, Languages


class SandboxTest(TestCase):
    language = ''
    extension = ''
    limits = {
        "TIME": 3,
        "MEMORY": 128 * 1024 * 1024
    }

    def setUp(self):
        self.arena = Arena().__enter__()
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.secret = os.path.join(self.base_path, 'secret.txt')

    def tearDown(self):
        self.arena.__exit__(None, None, None)

    def get_runner(self, name, limits=None):
        assert self.language
        assert self.extension

        name = "{}.{}".format(name, self.extension)
        name = os.path.join(self.language, name)
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
        self.assertEqual(result.status, 0, "{}: run time error")
        self.assertEqual(result.stdout.decode().strip(), str(expected_output).strip())

    def check_forbidden(self, name, dataset=''):
        runner = self.get_runner(name)
        result = runner.run(dataset)
        self.assertNotEqual(result.status, 0)
        return result

    def test_basic(self):
        if self.language:
            self.check_output('basic', 42)

    def test_cant_read_secret(self):
        if self.language:
            self.check_forbidden('read_secret')


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


class TestCPP(SandboxTest):
    language = Languages.CPP
    extension = 'cpp'


class TestHaskell(SandboxTest):
    language = Languages.HASKELL
    extension = 'hs'


class TestJava(SandboxTest):
    language = Languages.JAVA
    extension = 'java'


class TestOctave(SandboxTest):
    language = Languages.OCTAVE
    extension = 'm'
