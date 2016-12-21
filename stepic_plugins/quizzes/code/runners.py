import epicbox
import structlog

from stepic_plugins import settings


logger = structlog.get_logger()

custom_runners_registry = {}


class BaseProfiles(object):
    BASE = 'base'
    BASE_ROOT = 'base_root'


class BaseCodeRunner(object):
    """Base code runner for any language.

    A CodeRunner instance must be used as a context manager.

    """
    is_compiled_language = False
    #: file name to save source code to
    filename = 'epiccode'
    #: epicbox profile used to run untrusted code
    profile = BaseProfiles.BASE
    #: a command used to start a sandbox
    command = './main'

    def __init__(self, config, source, limits=None):
        self.source = source
        self.limits = limits
        self.filename = config.get('filename', self.filename)
        self.profile = config.get('profile', self.profile)
        self.command = config.get('command', self.command)
        self.workdir = None
        self._workdir_context_manager = epicbox.working_directory()
        self._is_source_saved = False

    def __enter__(self):
        self.workdir = self._workdir_context_manager.__enter__()
        return self

    def __exit__(self, *exc):
        self._workdir_context_manager.__exit__(*exc)

    def _save_source(self):
        if not self.workdir:
            raise RuntimeError(
                "A CodeRunner instance must be used as a context manager")
        source_bytes = self.source.encode()
        files = [{'name': self.filename, 'content': source_bytes}]
        epicbox.run(BaseProfiles.BASE,
                    command='true',
                    files=files,
                    workdir=self.workdir)
        self._is_source_saved = True
        logger.info("Source code was saved to the sandbox working directory",
                    workdir=self.workdir, files=[f['name'] for f in files])

    def _run_dataset(self, dataset):
        return epicbox.run(self.profile,
                           command=self.command,
                           stdin=dataset,
                           limits=self.limits,
                           workdir=self.workdir)

    def run(self, dataset):
        """Save source code to the working directory, run the command
        in a sandbox, and wait for command to complete.

        :param dataset: any string that is fed as a standard input
        :return: epicbox result dict

        """
        if not self._is_source_saved:
            self._save_source()
        return self._run_dataset(dataset)


class CompiledCodeRunner(BaseCodeRunner):
    """Base code runner for a compiled language."""

    is_compiled_language = True
    #: epicbox profile used to compile source code
    compile_profile = BaseProfiles.BASE_ROOT
    #: a command used to start a compilation sandbox
    compile_command = None

    def __init__(self, config, source, **kwargs):
        super().__init__(config, source, **kwargs)
        self.compile_profile = config.get('compile_profile',
                                          self.compile_profile)
        self.compile_command = config.get('compile_command',
                                          self.compile_command)
        self.is_source_compiled = False

    def _compile_source(self):
        return epicbox.run(self.compile_profile,
                           command=self.compile_command,
                           limits=settings.EPICBOX_COMPILE_LIMITS,
                           workdir=self.workdir)

    def compile(self):
        """Save source code to the working directory and compile it.

        :return: epicbox result dict

        """
        if not self._is_source_saved:
            self._save_source()
        result = self._compile_source()
        self.is_source_compiled = result['exit_code'] == 0
        # TODO: delete source code file
        return result

    def run(self, dataset):
        """Run the compiled code in a sandbox and wait for command to complete.

        :param dataset: any string that is fed as a standard input
        :return: epicbox result dict

        """
        if self.is_compiled_language and not self.is_source_compiled:
            raise RuntimeError(
                "Failed to run the code, you have to compile it first")
        return super().run(dataset)


class JavaCodeRunner(CompiledCodeRunner):
    def _run_dataset(self, dataset):
        command = 'java -Xmx{}k Main'
        limits = dict(self.limits)
        return epicbox.run(self.profile,
                           command=command,
                           stdin=dataset,
                           limits=limits,
                           workdir=self.workdir)


def get_code_runner(language, config, source, limits):
    """A factory function to create a code runner instance
    for the given language."""
    code_runner_class_name = config.get('runner')
    if code_runner_class_name:
        code_runner_class = globals().get(code_runner_class_name)
        if not code_runner_class:
            raise ValueError("Runner '{}' is not found for the language: {}"
                             .format(code_runner_class_name, language))
    else:
        if config.get('compiled', False):
            code_runner_class = CompiledCodeRunner
        else:
            code_runner_class = BaseCodeRunner
    return code_runner_class(config, source, limits=limits)
