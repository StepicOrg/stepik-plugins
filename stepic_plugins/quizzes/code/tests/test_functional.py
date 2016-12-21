import textwrap

from stepic_plugins.quizzes.code import CodeQuiz, Languages

from .base import BaseTestQuiz


class TestSubmissions(BaseTestQuiz):
    def test_compilation_error(self):
        quiz = self.prepare_quiz(self.default_source)
        code = "int 42;  // invalid c++ code"

        score, feedback = self.submit(quiz, code, Languages.CPP)

        assert score is False
        assert CodeQuiz.CE_MESSAGE in feedback
        assert "error: expected unqualified-id" in feedback

    def test_time_limit(self):
        quiz = self.prepare_quiz(self.default_source)
        code = textwrap.dedent("""
            int main() {
                int i = 0;
                while (true) {
                    i++;
                }
            }
            """)

        score, feedback = self.submit(quiz, code, Languages.CPP)

        assert score is False
        assert feedback == "Failed. Time limit exceeded"

    def test_memory_limit(self):
        quiz = self.prepare_quiz(self.default_source)
        code = textwrap.dedent("""
            #include <iostream>

            int main() {
                const int SIZE = 100000000;
                int *p = new int[SIZE];
                std::fill(p, p + SIZE, 0);
                std::cout << p[0];
            }
            """)

        score, feedback = self.submit(quiz, code, Languages.CPP)

        assert score is False
        assert feedback == "Failed. Memory limit exceeded"

    def test_runtime_error(self):
        quiz = self.prepare_quiz(self.default_source)
        code = textwrap.dedent("""
            #include <iostream>

            int main() {
                std::cout << "Output to stdin";
                std::cerr << "Output to stderr";
                return 1;
            }
            """)

        score, feedback = self.submit(quiz, code, Languages.CPP)

        assert score is False
        assert feedback == ("Failed. Run time error:\n"
                            "Output to stderr\n")

    def test_wrong_answer_on_sample_test(self):
        quiz = self.prepare_quiz(self.default_source)
        code = textwrap.dedent("""
            #include <iostream>

            int main() {
                std::cout << 43 << std::endl;
            }
            """)

        score, feedback = self.submit(quiz, code, Languages.CPP)

        assert score is False
        assert feedback == ("Failed. Wrong answer\n"
                            "Input:\n"
                            "42\n"
                            "Your output:\n43\n"
                            "Correct output:\n42")

    def test_wrong_answer(self):
        source = dict(self.default_source, **{
            'code': textwrap.dedent("""
                def generate():
                    return ['1', '2']

                def solve(dataset):
                    return '42'

                def check(reply, clue):
                    return int(reply) == 42
                """),
        })
        quiz = self.prepare_quiz(source)
        code = textwrap.dedent("""
            #include <iostream>

            int main() {
                int n;
                std::cin >> n;
                std::cout << (n == 1 ? 42 : 43) << std::endl;
            }
            """)

        score, feedback = self.submit(quiz, code, Languages.CPP)

        assert score is False
        assert feedback == "Failed test #2. Wrong answer"

    def test_wrong_answer_after_passed_tests_with_feedback(self):
        source = dict(self.default_source, **{
            'code': textwrap.dedent("""
                def generate():
                    return ['1', '2']

                def solve(dataset):
                    return '42'

                def check(reply, clue):
                    score = int(reply) == 42
                    return score, "feedback" if score else ""
                """),
        })
        quiz = self.prepare_quiz(source)
        code = textwrap.dedent("""
            #include <iostream>

            int main() {
                int n;
                std::cin >> n;
                std::cout << (n == 1 ? 42 : 43) << std::endl;
            }
            """)

        score, feedback = self.submit(quiz, code, Languages.CPP)

        assert score is False
        assert feedback == "Failed test #2. Wrong answer"

    def test_wrong_answer_custom_feedback(self):
        source = dict(self.default_source, **{
            'code': textwrap.dedent("""
                def generate():
                    return ['']

                def solve(dataset):
                    return '42'

                def check(reply, clue):
                    return int(reply) == 42, "feedback"
                """),
            'samples_count': 0,
        })
        quiz = self.prepare_quiz(source)
        code = textwrap.dedent("""
            #include <iostream>

            int main() {
                int n;
                std::cin >> n;
                std::cout << (n == 1 ? 42 : 43) << std::endl;
            }
            """)

        score, feedback = self.submit(quiz, code, Languages.CPP)

        assert score is False
        assert feedback == "Failed. feedback"

    def test_passed(self):
        quiz = self.prepare_quiz(self.default_source)

        score, feedback = self.submit(quiz, self.default_code, Languages.CPP)

        assert score is True
        assert feedback == ""

    def test_passed_single_test_feedback(self):
        source = dict(self.default_source, **{
            'code': textwrap.dedent("""
                def generate():
                    return ['42']

                def solve(dataset):
                    return '42'

                def check(reply, clue):
                    return int(reply) == 42, "feedback"
                """),
        })
        quiz = self.prepare_quiz(source)

        score, feedback = self.submit(quiz, self.default_code, Languages.CPP)

        assert score is True
        assert feedback == "Passed. feedback"

    def test_passed_multi_test_feedback(self):
        source = dict(self.default_source, **{
            'code': textwrap.dedent("""
                def generate():
                    return [('', 'feedback 1'), ('', 'feedback 2')]

                def solve(dataset):
                    return '42'

                def check(reply, clue):
                    return int(reply) == 42, clue
                """),
        })
        quiz = self.prepare_quiz(source)

        score, feedback = self.submit(quiz, self.default_code, Languages.CPP)

        assert score is True
        assert feedback == ("Passed test #1. feedback 1\n"
                            "Passed test #2. feedback 2")
