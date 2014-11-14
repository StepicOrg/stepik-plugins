import random
import re
import textwrap
import collections

from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError
from stepic_plugins.quizzes.executable_base import JailedCodeFailed, Arena, settings, run


class Languages(object):
    PYTHON = 'python3'
    CPP = 'c++'
    HASKELL = 'haskell'
    JAVA = 'java'
    OCTAVE = 'octave'
    ASM32 = 'asm32'
    ASM64 = 'asm64'
    all = [PYTHON, CPP, HASKELL, JAVA, OCTAVE, ASM32, ASM64]
    compiled = [CPP, HASKELL, ASM32, ASM64]
    interpreted = [PYTHON, OCTAVE]
    default_templates = {
        PYTHON: "# put your python code here",
        CPP: "#include <iostream>\n\nint main() {\n  // put your code here\n  return 0;\n}",
        HASKELL: "main :: IO ()\n-- put your code here",
        JAVA: "class Main {\n  public static void main(String[] args) {\n    // put your code here\n  }\n}",
        OCTAVE: "# put your octave code here",
        ASM32: "# put your asm32 code here",
        ASM64: "# put your asm64 code here"
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
        }

        reply = {
            'language': str,
            'code': str
        }

    FAILED_TEST_MESSAGE = "Failed test #{test_number}. {message}"

    CE_MESSAGE = "Compilation error"
    TL_MESSAGE = "Time limit exceeded"
    RE_MESSAGE = "Run time error:\n{}"
    WA_MESSAGE = "Wrong answer"

    def __init__(self, source, supplementary=None):
        super().__init__(source)
        self.code = source.code
        self.execution_time_limit = source.execution_time_limit
        self.execution_memory_limit = source.execution_memory_limit
        self.samples_count = source.samples_count
        self.templates_data = source.templates_data
        self.tests = supplementary['tests'] if supplementary else None

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
                'code_templates': {lang: temp[Directives.CODE] for lang, temp in self.code_templates.items()},
                'samples': samples,
            }
        }

    def set_supplementary(self, supplementary):
        self.tests = supplementary

    def clean_reply(self, reply, dataset):
        if reply.language not in self.available_languages:
            raise FormatError("Unknown language: " + reply.language)
        return reply

    def check(self, reply, clue, throw=False):
        with Arena() as arena:
            runner = CodeRunner(arena, self.concat_code(reply.language, reply.code), reply.language, self.limits)
            if not runner.compilation_success:
                hint = "{message}\n{stderr}".format(
                    message=self.CE_MESSAGE,
                    stderr=runner.compilation_result.stderr.decode()
                )
                return 0, hint

            for i, (dataset, clue) in enumerate(self.tests):
                test_number = i + 1
                result = runner.run(dataset)
                if result.status != 0:
                    if result.time_limit_exceeded:
                        message = self.TL_MESSAGE
                    else:
                        message = self.RE_MESSAGE.format(result.stderr.decode())
                    hint = self.FAILED_TEST_MESSAGE.format(
                        test_number=test_number,
                        message=message
                    )
                    return False, hint

                reply = result.stdout.decode(errors='replace').strip()
                result = self.score_one_test(reply, clue)
                if result[0] != 1:
                    hint = self.FAILED_TEST_MESSAGE.format(
                        test_number=test_number,
                        message=result[1] or self.WA_MESSAGE
                    )
                    return False, hint

            return True

    def concat_code(self, language, code):
        return '\n'.join([self.header(language), code, self.footer(language)])

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

        one_of_languages = '|'.join(l if l != 'c++' else r'c\+\+' for l in Languages.all)
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
    def limits(self):
        return {"TIME": self.execution_time_limit,
                "MEMORY": self.execution_memory_limit * 1024 * 1024}

    @property
    def available_languages(self):
        return self.code_templates.keys()

    def score_one_test(self, reply, clue):
        try:
            data = (reply, clue)
            score, hint = self.run_edyrun('score', data=data)
            return score, hint
        except (JailedCodeFailed, ValueError, TypeError):
            return False, ''

    def get_tests(self):
        tests = self.run_edyrun("generate", seed=random.randrange(10 ** 6))
        if not isinstance(tests, collections.Sequence):
            raise FormatError("Generate should return a Sequence")
        if len(tests) > 100:
            raise FormatError("Too many tests")
        if len(tests) == 0:
            raise FormatError("Empty test sequence")
        for element in tests:
            if not (isinstance(element, collections.Sequence) and len(element) == 2):
                raise FormatError("Test format is wrong")
            dataset, clue = element
            if not (isinstance(dataset, str)):
                raise FormatError("Test format is wrong")

        for dataset, clue in tests:
            msg = "{{}}\ndataset: {}\nclue: {}".format(dataset, clue)
            reply = self.run_edyrun('solve', data=dataset)
            result = self.score_one_test(reply, clue)
            if result[0] != 1:
                raise FormatError(msg.format("Test is broken"))

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
        self.compilation_success, self.compilation_result = self._compile()

    def run(self, dataset):
        assert self.compilation_success
        if self.language in Languages.compiled:
            #just run `./main`
            return self.arena.run_code('user_code', stdin=dataset, limits=self.limits)
        elif self.language == Languages.JAVA:
            #run `java Main` from compiled Main.class
            java_limits, args = get_limits_for_java(self.limits)
            return self.arena.run_code('run_java', command_argv=args + ['Main'],
                                       stdin=dataset, limits=java_limits)
        elif self.language in Languages.interpreted:
            #run `python self.source`
            limits = dict(self.limits)
            if self.language in settings.INTERPRETERS:
                limits["MEMORY"] += settings.INTERPRETERS[self.language]['reserved_memory']

            return self.arena.run_code('run_' + self.language, code=self.source, argv=[], files=[],
                                       stdin=dataset, limits=limits)
        assert False, 'unknown language: ' + self.language

    def _compile(self):
        if self.language in settings.COMPILERS:
            source_file_name = 'main.{}'.format(settings.COMPILERS[self.language]['ext'])
            compilation_result = self.arena.run_code('compile_' + self.language,
                                                     command_argv=[source_file_name],
                                                     files=[(self.source, source_file_name)])
            return compilation_result.status == 0, compilation_result
        else:
            return True, None


def get_limits_for_java(limits):
    java_limits = dict(limits)
    #for gc
    java_limits["CAN_FORK"] = True
    #setrlimit does not work because of MAP_NORESERVE, use -Xmx instead
    java_limits["MEMORY"] = None
    xmxk = limits["MEMORY"] // 1024
    return java_limits, ["-Xmx{}k".format(xmxk), "-Xss8m"]
