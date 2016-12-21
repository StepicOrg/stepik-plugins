import epicbox
import pytest

from unittest.mock import patch

from ..runners import (BaseCodeRunner, CompiledCodeRunner, JavaCodeRunner,
                       BaseProfiles, get_code_runner)


class TestBaseCodeRunner(object):
    def test_save_source(self):
        source = "epic source code here"

        with BaseCodeRunner({}, source) as runner:
            runner._save_source()

            assert runner._is_source_saved
            result = epicbox.run(BaseProfiles.BASE, 'cat epiccode',
                                 workdir=runner.workdir)
        assert result['exit_code'] == 0
        assert result['stdout'].decode() == source + '\n'

    def test_run_interpreted_code(self):
        source = ('import sys; sys.stderr.write("standard error\\n");'
                  'print(raw_input())')
        config = {
            'filename': 'main.py',
            'profile': 'python3',
            'command': 'python main.py',
        }

        with BaseCodeRunner(config, source) as runner:
            result = runner.run("standard input")

        assert result['exit_code'] == 0
        assert result['stdout'] == b'standard input\n'
        assert result['stderr'] == b'standard error\n'

    def test_run_with_limits(self):
        source = 'l = [1] * 10 ** 7'
        limits = {'cputime': 10, 'memory': 8}
        config = {
            'filename': 'main.py',
            'profile': 'python3',
            'command': 'python main.py',
        }

        with BaseCodeRunner(config, source, limits=limits) as runner:
            result = runner.run('')

        assert result['exit_code'] != 0
        assert result['oom_killed'] is True
        assert result['timeout'] is False

    def test_run_write_denied(self):
        config = {
            'filename': 'main.sh',
            'profile': BaseProfiles.BASE,
            'command': '/bin/sh main.sh',
        }

        with BaseCodeRunner(config, 'touch file') as runner:
            result = runner.run('')

        assert result['exit_code'] != 0
        assert b'Permission denied' in result['stderr']

        with BaseCodeRunner(config, 'touch /tmp/file') as runner:
            result = runner.run('')

        assert result['exit_code'] != 0
        assert b'Read-only file system' in result['stderr']


class TestCompiledCodeRunner(object):
    def test_compile_failed(self):
        config = {
            'compile_profile': BaseProfiles.BASE,
            'compile_command': '>&2 echo "Compilation failed" && false',
        }
        with CompiledCodeRunner(config, 'source') as runner:
            assert not runner.is_source_compiled

            result = runner.compile()

            assert not runner.is_source_compiled
        assert result['exit_code'] == 1
        assert result['stderr'] == b'Compilation failed\n'

    @patch.dict('stepic_plugins.quizzes.code.settings.'
                'EPICBOX_COMPILE_LIMITS', memory=8)
    def test_compile_with_default_limits(self):
        source = 'l = [1] * 10 ** 7'
        config = {
            'compiled': True,
            'filename': 'main.py',
            'compile_profile': 'python3',
            'compile_command': 'python main.py',
        }

        with CompiledCodeRunner(config, source) as runner:
            result = runner.compile()

            assert not runner.is_source_compiled
        assert result['exit_code'] != 0
        assert result['oom_killed'] is True
        assert result['timeout'] is False

    def test_run_before_compile(self):
        config = {'compiled': True}

        with CompiledCodeRunner(config, 'source') as runner:
            with pytest.raises(RuntimeError) as excinfo:
                runner.run("dataset")

        assert "compile it first" in str(excinfo.value)

    def test_run_compiled_code(self):
        source = '#!/bin/sh\ncat && >&2 echo "standard error"'
        config = {
            'compiled': True,
            'filename': 'main.cpp',
            'compile_profile': BaseProfiles.BASE_ROOT,
            'compile_command': 'cp main.cpp main && chmod +x main',
        }
        with CompiledCodeRunner(config, source) as runner:
            assert not runner.is_source_compiled

            compile_result = runner.compile()

            assert runner.is_source_compiled
            assert compile_result['exit_code'] == 0

            result = runner.run("standard input")

        assert result['exit_code'] == 0
        assert result['stdout'] == b'standard input\n'
        assert result['stderr'] == b'standard error\n'


class TestCodeRunnerWrapper(object):
    def test_get_base_runner(self):
        runner = get_code_runner('language', {}, None, None)

        assert runner.__class__ is BaseCodeRunner

    def test_get_compiled_runner(self):
        runner = get_code_runner('language', {'compiled': True}, None, None)

        assert runner.__class__ is CompiledCodeRunner

    def test_get_java_runner(self):
        config = {'runner': 'JavaCodeRunner'}

        runner = get_code_runner('java', config, None, None)

        assert isinstance(runner, JavaCodeRunner)

    def test_get_unknown_runner(self):
        config = {'runner': 'UnknownCodeRunner'}

        with pytest.raises(ValueError) as excinfo:
            get_code_runner('language', config, None, None)

        assert "not found" in str(excinfo.value)
