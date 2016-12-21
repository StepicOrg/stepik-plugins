import base64
import collections
import glob
import io
import logging
import os
import random
import re
import subprocess
import textwrap
import zipfile

from decimal import Decimal, ROUND_HALF_UP

from stepic_plugins import settings
from stepic_plugins.base import BaseQuiz
from stepic_plugins.constants import WARNING_NEWLINE, WARNING_SPLIT_LINES
from stepic_plugins.exceptions import FormatError
from stepic_plugins.executable_base import Arena, JailedCodeFailed, run
from stepic_plugins.schema import attachment
from .runners import get_code_runner


logger = logging.getLogger(__name__)


# NOTE: After releasing a new language in Code challenge you should run two
#       migration commands: `update_code_limits` and `update_code_templates`.
#       They will populate `source` and `options` dicts in previously created
#       code steps with limits and a template for a new language.


class Languages(object):
    PYTHON = 'python3'
    C = 'c'
    CPP = 'c++'
    CPP11 = 'c++11'
    HASKELL = 'haskell'
    HASKELL_7_10 = 'haskell 7.10'
    HASKELL_8_0 = 'haskell 8.0'
    JAVA = 'java'
    JAVA8 = 'java8'
    OCTAVE = 'octave'
    ASM32 = 'asm32'
    ASM64 = 'asm64'
    SHELL = 'shell'
    RUST = 'rust'
    R = 'r'
    RUBY = 'ruby'
    CLOJURE = 'clojure'
    MONO_CS = 'mono c#'
    JAVA_SCRIPT = 'javascript'
    SCALA = 'scala'
    all = [PYTHON, C, CPP, CPP11, HASKELL, HASKELL_7_10, HASKELL_8_0, JAVA, JAVA8, OCTAVE,
           ASM32, ASM64, SHELL, RUST, R, RUBY, CLOJURE, MONO_CS, JAVA_SCRIPT, SCALA]
    compiled = [C, CPP, CPP11, HASKELL, HASKELL_7_10, HASKELL_8_0, ASM32, ASM64, RUST]
    interpreted = [PYTHON, OCTAVE, SHELL, R, RUBY, CLOJURE, JAVA_SCRIPT]
    default_templates = {
        PYTHON: "# put your python code here",
        C: "#include <stdio.h>\n\nint main() {\n  // put your code here\n  return 0;\n}",
        CPP: "#include <iostream>\n\nint main() {\n  // put your code here\n  return 0;\n}",
        CPP11: "#include <iostream>\n\nint main() {\n  // put your code here\n  return 0;\n}",
        HASKELL: "main :: IO ()\n-- put your code here",
        HASKELL_7_10: "main :: IO ()\n-- put your code here",
        HASKELL_8_0: "main :: IO ()\n-- put your code here",
        JAVA: "class Main {\n  public static void main(String[] args) {\n    // put your code here\n  }\n}",
        JAVA8: "class Main {\n  public static void main(String[] args) {\n    // put your code here\n  }\n}",
        OCTAVE: "% put your octave code here",
        ASM32: "# put your asm32 code here",
        ASM64: "# put your asm64 code here",
        SHELL: "# put your shell (bash) code here",
        RUST: "fn main() {\n    // put your Rust code here\n}",
        R: "# put your R code here",
        RUBY: "# put your ruby code here",
        CLOJURE: ";; put your clojure code here",
        MONO_CS: "using System;\n\npublic class MainClass\n{\n    public static void Main()\n"
                 "    {\n        // put your c# code here\n    }\n}",
        JAVA_SCRIPT: "// put your javascript (node.js) code here",
        SCALA: "object Main {\n  def main(args: Array[String]) {\n    // put your code here\n  }\n}",
    }

    default_time_limit_factors = {
        PYTHON: 3,
        HASKELL: 2,
        HASKELL_7_10: 2,
        HASKELL_8_0: 2,
        JAVA: 1.5,
        JAVA8: 1.5,
        OCTAVE: 2.5,
        RUST: 2.5,
        R: 1.5,
        RUBY: 3,
        CLOJURE: 2,
        MONO_CS: 1.5,
        JAVA_SCRIPT: 3,
        SCALA: 1.5,
    }
    default_memory_limit_factors = {
        # TODO: set factors
    }


class Directives(object):
    HEADER, FOOTER, CODE = 'header', 'footer', 'code'
    all = [HEADER, FOOTER, CODE]


class CodeQuiz(BaseQuiz):
    name = 'code'

    class Schemas:
        source = {
            'code': str,
            'execution_time_limit': int,
            'execution_memory_limit': int,
            'samples_count': int,
            'templates_data': str,
            'is_time_limit_scaled': bool,
            'is_memory_limit_scaled': bool,
            'manual_time_limits': [{'language': str, 'time': int}],
            'manual_memory_limits': [{'language': str, 'memory': int}],
            'test_archive': [attachment],
        }

        reply = {
            'language': str,
            'code': str
        }

    TL_MIN = 1
    TL_MAX = 30
    ML_MIN = 32
    ML_MAX = 512

    FAILED_SINGLE_TEST_MESSAGE = "Failed. {message}"
    FAILED_TEST_MESSAGE = "Failed test #{test_number}. {message}"
    SAMPLE_TEST_MESSAGE = "\nInput:\n{dataset}\nYour output:\n{reply}\nCorrect output:\n{output}"
    PASSED_SINGLE_TEST_MESSAGE = "Passed. {message}"
    PASSED_TEST_MESSAGE = "Passed test #{test_number}. {message}"

    CE_MESSAGE = "Compilation error"
    TL_MESSAGE = "Time limit exceeded"
    ML_MESSAGE = "Memory limit exceeded"
    RE_MESSAGE = "Run time error:\n{}"
    WA_MESSAGE = "Wrong answer"

    CE_PUBLIC_CLASS_MESSAGE = "Please do not declare public classes."

    def __init__(self, source, supplementary=None):
        super().__init__(source)
        self.code = source.code
        self.execution_time_limit = source.execution_time_limit
        self.execution_memory_limit = source.execution_memory_limit
        self.samples_count = source.samples_count
        self.templates_data = source.templates_data
        self.zip_archive = source.test_archive
        self.tests = supplementary['tests'] if supplementary else None
        self._validate_source()

    def _validate_source(self):
        if self.samples_count < 0:
            raise FormatError("Number of sample tests should be non-negative")
        self._validate_time_limit(self.execution_time_limit)
        for manual_time_limit in self.source.manual_time_limits:
            self._validate_language(manual_time_limit.language)
            self._validate_time_limit(manual_time_limit.time)
        self._validate_memory_limit(self.execution_memory_limit)
        for manual_memory_limit in self.source.manual_memory_limits:
            self._validate_language(manual_memory_limit.language)
            self._validate_memory_limit(manual_memory_limit.memory)
        if len(self.source.test_archive) > 1:
            raise FormatError("Number of test archives should be at most 1")

    def _validate_time_limit(self, value):
        if value < CodeQuiz.TL_MIN:
            raise FormatError("Time Limit should be at least {}".format(CodeQuiz.TL_MIN))
        if value > CodeQuiz.TL_MAX:
            raise FormatError("Time Limit should be at most {}".format(CodeQuiz.TL_MAX))

    def _validate_memory_limit(self, value):
        if value < CodeQuiz.ML_MIN:
            raise FormatError("Memory Limit should be at least {}".format(CodeQuiz.ML_MIN))
        if value > CodeQuiz.ML_MAX:
            raise FormatError("Memory Limit should be at most {}".format(CodeQuiz.ML_MAX))

    def _validate_language(self, value):
        if value not in Languages.all:
            raise FormatError("Unknown language")

    def async_init(self):
        samples = []
        try:
            tests = self.get_tests()
            dataset, output = self.run_edyrun('sample')
            if not dataset:
                # samples from generate function
                for i in range(min(self.samples_count, len(tests))):
                    dataset, clue = tests[i]
                    output = self.run_edyrun('solve', data=dataset)
                    samples.append((dataset, output))
            else:
                # samples from tests list
                samples.append((dataset, output))
        except JailedCodeFailed as e:
            raise FormatError(str(e))
        return {
            'tests': tests,
            'options': {
                'execution_time_limit': self.execution_time_limit,
                'execution_memory_limit': self.execution_memory_limit,
                'limits': self.limits,
                'code_templates': {lang: temp[Directives.CODE] for lang, temp in self.code_templates.items()},
                'samples': samples,
            },
            'warnings': self._generate_warnings(tests),
        }

    def _generate_warnings(self, tests):
        warnings = []
        for dataset, _ in tests:
            if not dataset.endswith('\n'):
                warnings.append(WARNING_NEWLINE)
                break
        for pattern in [r".split('\n')", r'.split("\n")']:
            if pattern in self.code:
                warnings.append(WARNING_SPLIT_LINES)
                break
        return warnings

    def set_supplementary(self, supplementary):
        self.tests = supplementary

    def clean_reply(self, reply, dataset):
        if reply.language not in self.available_languages:
            msg = "Unknown language: {0}. Please reload the page and try again"
            raise FormatError(msg.format(reply.language))
        return reply

    def check(self, reply, clue, throw=False):
        language = reply['language']
        source = self.concat_code(language, reply['code'])
        failed_test_message = (self.FAILED_SINGLE_TEST_MESSAGE if len(self.tests) == 1 else
                               self.FAILED_TEST_MESSAGE)
        passed_test_message = (self.PASSED_SINGLE_TEST_MESSAGE if len(self.tests) == 1 else
                               self.PASSED_TEST_MESSAGE)
        if language in settings.CODE_LANGUAGES:
            # Use epicbox sandboxes for this language
            config = settings.CODE_LANGUAGES[language]
            limits_old_format = self.language_limits(language)
            limits = {
                'cputime': limits_old_format['TIME'],
                'memory': limits_old_format['MEMORY'] // 1024 // 1024,
            }
            with get_code_runner(language, config, source, limits) as runner:
                if runner.is_compiled_language:
                    result = runner.compile()
                    if not runner.is_source_compiled:
                        feedback = "{message}\n{stderr}".format(
                            message=self.CE_MESSAGE,
                            stderr=result['stderr'].decode(errors='replace'))
                        return False, feedback
                tests_feedback = []
                for test_number, (dataset, clue) in enumerate(self.tests, start=1):
                    result = runner.run(dataset)
                    if result['exit_code'] != 0:
                        if result['timeout']:
                            message = self.TL_MESSAGE
                        elif result['oom_killed']:
                            message = self.ML_MESSAGE
                        else:
                            stderr = result['stderr'].decode(errors='replace')
                            message = self.RE_MESSAGE.format(stderr)
                        feedback = failed_test_message.format(
                            test_number=test_number,
                            message=message
                        )
                        return False, feedback
                    reply = result['stdout'].decode(errors='replace').strip()
                    score, one_test_feedback = self.score_one_test(reply, clue)
                    if score != 1:
                        feedback = failed_test_message.format(
                            test_number=test_number,
                            message=one_test_feedback or self.WA_MESSAGE
                        )
                        if test_number <= self.samples_count:
                            output = self.run_edyrun('solve', data=dataset)
                            feedback += self.SAMPLE_TEST_MESSAGE.format(
                                dataset=dataset,
                                reply=reply,
                                output=output
                            )
                        return False, feedback
                    if one_test_feedback:
                        feedback = passed_test_message.format(
                            test_number=test_number,
                            message=one_test_feedback
                        )
                        tests_feedback.append(feedback)
                return True, '\n'.join(tests_feedback)
        # Use apparmor sandboxes for other languages
        with Arena() as arena:
            runner = CodeRunner(arena, source, language, self.language_limits(language))
            if not runner.compilation_success:
                hint = "{message}\n{stderr}".format(
                    message=self.CE_MESSAGE,
                    stderr=runner.compilation_result.stderr.decode(errors='replace')
                )
                return 0, hint

            hints = []

            for i, (dataset, clue) in enumerate(self.tests):
                test_number = i + 1
                result = runner.run(dataset)
                if result.status != 0:
                    if result.time_limit_exceeded:
                        message = self.TL_MESSAGE
                    else:
                        message = self.RE_MESSAGE.format(result.stderr.decode(errors='replace'))
                    hint = failed_test_message.format(
                        test_number=test_number,
                        message=message
                    )
                    return False, hint

                reply = result.stdout.decode(errors='replace').strip()
                result = self.score_one_test(reply, clue)
                if result[0] != 1:
                    hint = failed_test_message.format(
                        test_number=test_number,
                        message=result[1] or self.WA_MESSAGE
                    )
                    if i < self.samples_count:
                        output = self.run_edyrun('solve', data=dataset)
                        hint += self.SAMPLE_TEST_MESSAGE.format(
                            dataset=dataset,
                            reply=reply,
                            output=output
                        )
                    return False, hint

                if result[1]:
                    hint = passed_test_message.format(
                        test_number=test_number,
                        message=result[1]
                    )
                    hints.append(hint)

            return True, '\n'.join(hints)

    def concat_code(self, language, code):
        res = []
        header = self.header(language)
        if header:
            res.append(header)
        res.append(code)
        footer = self.footer(language)
        if footer:
            res.append(footer)
        return '\n'.join(res)

    def footer(self, language):
        return self.code_templates[language][Directives.FOOTER]

    def header(self, language):
        return self.code_templates[language][Directives.HEADER]

    @property
    def code_templates(self):
        """Extracts language templates from text

        ::python3
        print("hello world")

        ::haskell
        main = putStrLn "hello, world"

        If empty template specified, then use default template for this language
        If no templates at all, then returns default templates for all supported languages
        """

        one_of_languages = '|'.join(l if 'c++' not in l else re.escape(l) for l in Languages.all)
        pattern = r'^::[ \t\r\f\v]*(' + one_of_languages + r')[ \t\r\f\v]*$'
        parts = re.split(pattern, self.templates_data, flags=re.MULTILINE)
        parts = parts[1:]
        languages = parts[::2]
        templates = parts[1::2]
        assert (len(languages) == len(templates))
        templates = dict(zip(languages, templates)) or {language: '' for language in Languages.all}
        for language, template in templates.items():
            templates[language] = self.split_template(template or Languages.default_templates[language])
        return templates

    def split_template(self, template):
        pattern = r'^::[ \t\r\f\v]*(' + '|'.join(Directives.all) + r')[ \t\r\f\v]*$'
        parts = re.split(pattern, template, flags=re.MULTILINE)
        if len(parts) == 1:
            return {Directives.HEADER: '',
                    Directives.FOOTER: '',
                    Directives.CODE: textwrap.dedent(template).strip()}

        parts = parts[1:]
        directives = parts[::2]
        parts = [textwrap.dedent(p).strip() for p in parts[1::2]]
        assert len(directives) == len(parts)

        return dict({d: '' for d in Directives.all}, **dict(zip(directives, parts)))

    @property
    def available_languages(self):
        return self.code_templates.keys()

    @property
    def limits(self):
        """Get limits for all available languages.

        Used to set up `limits` value in `options` dictionary.

        """
        limits = {}
        for language in self.available_languages:
            language_limits = self.language_limits(language)
            limits[language] = dict(time=language_limits['TIME'],
                                    memory=language_limits['MEMORY'] // 1024 // 1024)
        return limits

    def language_limits(self, language):
        limits = {
            'TIME': self.source.execution_time_limit,
            'MEMORY': self.source.execution_memory_limit,
        }
        # Customize time limits
        manual_time_limit = [limit.time for limit in self.source.manual_time_limits
                             if limit.language == language]
        if manual_time_limit:
            limits['TIME'] = manual_time_limit[0]
        else:
            if self.source.is_time_limit_scaled:
                scaled_time = (Decimal(limits['TIME']) *
                               Decimal(Languages.default_time_limit_factors.get(language, 1)))
                limits['TIME'] = int(scaled_time.to_integral_value(rounding=ROUND_HALF_UP))
        # Customize memory limits
        manual_memory_limit = [limit.memory for limit in self.source.manual_memory_limits
                               if limit.language == language]
        if manual_memory_limit:
            limits['MEMORY'] = manual_memory_limit[0]
        else:
            if self.source.is_memory_limit_scaled:
                scaled_memory = (Decimal(limits['MEMORY']) *
                                 Decimal(Languages.default_memory_limit_factors.get(language, 1)))
                limits['MEMORY'] = int(scaled_memory.to_integral_value(rounding=ROUND_HALF_UP))
        # Calculate memory limit in bytes
        limits['MEMORY'] *= 1024 * 1024
        return limits

    def score_one_test(self, reply, clue, throw=False):
        try:
            data = (reply, clue)
            score, hint = self.run_edyrun('score', data=data)
            return score, hint
        except (JailedCodeFailed, ValueError, TypeError) as e:
            return False, str(e) if throw else "Cannot check answer. Perhaps output format is wrong."

    def generate_tests(self, archive):
        """
            Pull out tests from attachments
        :param archive: - list of attachments, where containing encoded zip files in "content"
        :return: list of tests, giving in archive
        """

        def is_applicable_name(name):
            if name.endswith(".clue"):
                name = name[:-5]
            return name.isdigit()

        if not archive:
            return []
        # extract encoded sequence
        encoded_sequence = archive[0].content
        PREFIX = "base64$"
        #It is not a correct base64 format
        if encoded_sequence.find(PREFIX) == -1:
            return []
        decode_sequence = encoded_sequence[encoded_sequence.find(PREFIX) + len(PREFIX):]
        decode_sequence = base64.b64decode(decode_sequence)
        bytes_reader = io.BytesIO(decode_sequence)
        zip_file = None
        try:
            zip_file = zipfile.ZipFile(bytes_reader)
        except:
            return []
        test_contain = dict()
        for file_name in zip_file.namelist():
            if is_applicable_name(file_name):
                byte_representation = zip_file.read(file_name)
                test_contain[file_name] = byte_representation.decode("utf-8").strip()
        tests = []
        files = []
        for file_name in zip_file.namelist():
            if file_name and file_name + ".clue" in test_contain:
                files.append((file_name, file_name + ".clue"))
        try:
            files = sorted(files, key=lambda value: int(value[0]))
        except Exception:
            raise FormatError("Input files should be named as integer numbers") from None
        for input_name, output_name in files:
                tests.append([test_contain[input_name], test_contain[output_name]])
        return tests

    def get_tests(self):
        tests = self.run_edyrun("generate", seed=random.randrange(10 ** 6))
        tests.extend(self.generate_tests(self.zip_archive))
        if not isinstance(tests, collections.Sequence):
            raise FormatError("Generate should return a Sequence")
        if len(tests) > 100:
            raise FormatError("Too many tests (should be <= 100 tests)")
        if len(tests) == 0:
            raise FormatError("Empty test sequence (should be > 0 test)")
        for element in tests:
            if not (isinstance(element, collections.Sequence) and len(element) == 2):
                raise FormatError("Test format is wrong")
            dataset, clue = element
            if not (isinstance(dataset, str)):
                raise FormatError("Test format is wrong")

        for dataset, clue in tests:
            msg = "{}\ndataset: {}\nclue: {}\nreply: {}\nresult: {}\nhint: {}"
            reply = self.run_edyrun('solve', data=dataset)
            result = self.score_one_test(reply, clue, throw=True)
            if result[0] != 1:
                raise FormatError(msg.format("Test is broken", dataset, clue, reply, *result))

        return tests

    def run_edyrun(self, command, data=None, **kwargs):
        files = []
        return run(command, self.code, data, files, type='code', **kwargs)


class CodeRunner(object):
    def __init__(self, arena, source, language, limits):
        self.arena = arena
        self.source = source
        self.language = language
        self.limits = limits
        # Dirty way to add extra memory for sudo initialization
        # TODO: delete when moved to epicbox
        self.limits['MEMORY'] += 1 * 1024 * 1024
        self.java_class_name = 'Main'
        self.compilation_success, self.compilation_result = self._compile()

    def run(self, dataset):
        assert self.compilation_success
        if self.language in Languages.compiled:
            #just run `./main`
            return self.arena.run_code('user_code', stdin=dataset, limits=self.limits)
        elif self.language in [Languages.JAVA, Languages.JAVA8]:
            #run `java EntryPointClass`
            java_limits, args = get_limits_for_java(self.limits)
            return self.arena.run_code('run_' + self.language,
                                       command_argv=args + [self.java_class_name],
                                       stdin=dataset, limits=java_limits)
        elif self.language == Languages.CLOJURE:
            #run `java -cp closure.jar closure.main self.source`
            java_limits, args = get_limits_for_java(self.limits)
            return self.arena.run_code('run_clojure',
                                       command_argv=args + ['clojure.main'],
                                       code=self.source,
                                       stdin=dataset,
                                       limits=java_limits)
        elif self.language == Languages.SCALA:
            #run `scala EntryPointClass`
            java_limits, args = get_limits_for_java(self.limits)
            args = ['-J' + arg for arg in args]
            return self.arena.run_code('run_scala',
                                       command_argv=args + [self.java_class_name],
                                       stdin=dataset,
                                       limits=java_limits)
        elif self.language == Languages.MONO_CS:
            #run `mono main.exe`
            return self.arena.run_code('run_mono c#',
                                       command_argv=['main.exe'],
                                       stdin=dataset,
                                       limits=self.limits)
        elif self.language == Languages.JAVA_SCRIPT:
            #run `node --max-old-space-size=ML self.source`
            node_limits = dict(self.limits)
            ml_argv = '--max-old-space-size={0}'.format(node_limits['MEMORY'] // 1024 // 1024)
            node_limits['MEMORY'] = None
            return self.arena.run_code('run_javascript',
                                       command_argv=[ml_argv],
                                       code=self.source,
                                       stdin=dataset,
                                       limits=node_limits)
        elif self.language in Languages.interpreted:
            #run `python self.source`
            limits = dict(self.limits)
            if self.language in settings.INTERPRETERS:
                limits["MEMORY"] += settings.INTERPRETERS[self.language].get('reserved_memory', 0)

            return self.arena.run_code('run_' + self.language, code=self.source, argv=[], files=[],
                                       stdin=dataset, limits=limits)
        assert False, 'unknown language: ' + self.language

    def _compile(self):
        if self.language not in settings.COMPILERS:
            return True, None
        language_settings = settings.COMPILERS[self.language]
        source_file_name = language_settings.get('filename')
        source_file_name = source_file_name or 'main.{}'.format(
            settings.COMPILERS[self.language]['ext'])
        compilation_result = self.arena.run_code('compile_' + self.language,
                                                 command_argv=[source_file_name],
                                                 files=[(self.source, source_file_name)])
        if language_settings.get('check_compiled_file', False):
            compiled_filename = language_settings.get('compiled_filename', 'main')
            if not os.path.isfile(os.path.join(self.arena.tmpdir, compiled_filename)):
                return False, compilation_result
        try:
            os.remove(os.path.join(self.arena.tmpdir, source_file_name))
        except OSError:
            logger.exception("Failed to delete the source code file")
        if self.language in [Languages.JAVA, Languages.JAVA8, Languages.SCALA]:
            if compilation_result.status != 0:
                if b"is public, should be declared" in compilation_result.stderr:
                    compilation_result.stderr += b'\n' + CodeQuiz.CE_PUBLIC_CLASS_MESSAGE.encode()
            else:
                java_compiler = self.language
                if self.language == Languages.SCALA:
                    java_compiler = Languages.JAVA
                javap_bin = os.path.join(os.path.dirname(settings.COMPILERS[java_compiler]['bin']),
                                         'javap')
                # grep *.class files to find one with psvm defined
                for class_path in glob.glob(os.path.join(self.arena.tmpdir, '*.class')):
                    self.java_class_name, _ = os.path.splitext(os.path.basename(class_path))
                    try:
                        code = subprocess.check_output([javap_bin, '-p', class_path],
                                                       timeout=settings.JAVA_DISASSEMBLE_TIMEOUT)
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                        continue
                    if b'public static void main(java.lang.String[])' in code:
                        break
        return compilation_result.status == 0, compilation_result


def get_limits_for_java(limits):
    java_limits = dict(limits)
    #for gc
    java_limits["CAN_FORK"] = True
    #setrlimit does not work because of MAP_NORESERVE, use -Xmx instead
    java_limits["MEMORY"] = None
    xmxk = limits["MEMORY"] // 1024
    return java_limits, ["-Xmx{}k".format(xmxk), "-Xss8m"]
