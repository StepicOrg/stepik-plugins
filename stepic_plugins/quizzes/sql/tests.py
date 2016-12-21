import os
import textwrap
import unittest

import docker
import MySQLdb

from unittest import mock

from docker.errors import NotFound

from stepic_plugins import settings
from stepic_plugins.exceptions import FormatError
from stepic_plugins.tests.utils import override_settings
from . import SqlQuiz, InitSqlError, QueryStatus, get_db_root_cursor


class SqlQuizBaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docker = docker.Client(base_url=settings.SQL_DOCKER_HOST)

    def setUp(self):
        self.source = {
            'init_sql': """
                SELECT 42;
                CREATE TABLE users (id INT PRIMARY KEY AUTO_INCREMENT,
                                    name VARCHAR(20),
                                    age INT);
                INSERT INTO users (name, age) VALUES ('Stepic Stepicov', 3);
                INSERT INTO users (name, age) VALUES ('Coursera Courserova', 42);
            """,
            'solve_sql': "INSERT INTO users (name, age) VALUES ('Student Studentov', 1)",
            'check_code': textwrap.dedent("""
                def check(query, result):
                    count = cursor.execute("select * from users where id=3")
                    if cursor.fetchone() == (3, "Student Studentov", 1):
                        return True
                    if count == 0:
                        return False, "Cannot find a record with id=3"
                    return False, "Inserted record is incorrect"
                """),
        }

    @property
    def quiz(self):
        return SqlQuiz(SqlQuiz.Source(self.source))


class SqlQuizTest(SqlQuizBaseTest):
    def test_valid_source(self):
        SqlQuiz(SqlQuiz.Source(self.source))

    def test_clean_reply_empty_query(self):
        reply = SqlQuiz.Reply({'solve_sql': "  "})

        with self.assertRaises(FormatError):
            self.quiz.clean_reply(reply, None)

    def test_clean_reply_only_one_query(self):
        reply = SqlQuiz.Reply({'solve_sql': "SELECT 42; SELECT 42"})

        with self.assertRaises(FormatError):
            self.quiz.clean_reply(reply, None)

    def test_clean_reply_only_one_query_new_line(self):
        reply = SqlQuiz.Reply({'solve_sql': "SELECT 42;\n\n"})

        clean_reply = self.quiz.clean_reply(reply, None)

        self.assertEqual(clean_reply, "SELECT 42;")


@unittest.skipUnless(os.environ.get('RUN_LONG_TESTS'), "Long tests skipped")
class SqlQuizStartDbContainerTest(SqlQuizBaseTest):
    def tearDown(cls):
        try:
            cls.docker.remove_container(settings.SQL_CONTAINER_NAME, v=True, force=True)
        except NotFound:
            pass

    def test_start_db_container(self):
        with self.assertRaises(NotFound):
            self.docker.inspect_container(settings.SQL_CONTAINER_NAME)

        ctr = self.quiz._start_db_container()

        running_ctr = self.docker.inspect_container(settings.SQL_CONTAINER_NAME)
        self.assertEqual(ctr['Id'], running_ctr['Id'])
        self.assertEqual(running_ctr['Name'], '/' + settings.SQL_CONTAINER_NAME)
        self.assertTrue(running_ctr['State']['Running'])

        new_ctr = self.quiz._start_db_container()

        self.assertEqual(new_ctr, running_ctr)

    def test_generate_starts_db_container(self):
        with self.assertRaises(NotFound):
            self.docker.inspect_container(settings.SQL_CONTAINER_NAME)

        try:
            self.quiz.generate()
        except Exception:
            pass

        self.assertTrue(self.docker.inspect_container(settings.SQL_CONTAINER_NAME))

    def test_check_starts_db_container(self):
        with self.assertRaises(NotFound):
            self.docker.inspect_container(settings.SQL_CONTAINER_NAME)

        try:
            self.quiz.check(None, None)
        except Exception:
            pass

        self.assertTrue(self.docker.inspect_container(settings.SQL_CONTAINER_NAME))

    def test_cleanup_starts_db_container(self):
        with self.assertRaises(NotFound):
            self.docker.inspect_container(settings.SQL_CONTAINER_NAME)

        try:
            self.quiz.cleanup(None)
        except Exception:
            pass

        self.assertTrue(self.docker.inspect_container(settings.SQL_CONTAINER_NAME))


class SqlQuizDBContainerTest(SqlQuizBaseTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        quiz = SqlQuiz(SqlQuiz.Source({'init_sql': "", 'solve_sql': "", 'check_code': ""}))
        cls.db_container = quiz._start_db_container()

    @classmethod
    def tearDownClass(cls):
        cls.docker.remove_container(cls.db_container, v=True, force=True)

    def setUp(self):
        super().setUp()
        self.db = get_db_root_cursor()

    def assertDatabaseExists(self, db_name):
        self.assertEqual(self.db.execute("SHOW DATABASES LIKE %s", (db_name, )), 1)

    def assertDatabaseNotExists(self, db_name):
        self.assertEqual(self.db.execute("SHOW DATABASES LIKE %s", (db_name, )), 0)

    def assertUserExists(self, db_user):
        res = self.db.execute("SELECT user FROM mysql.user WHERE user=%s", (db_user, ))
        self.assertEqual(res, 1)

    def assertUserNotExists(self, db_user):
        res = self.db.execute("SELECT user FROM mysql.user WHERE user=%s", (db_user, ))
        self.assertEqual(res, 0)

    def test_async_init(self):
        self.quiz.async_init()

    def test_async_init_error_in_init_sql(self):
        self.source['init_sql'] = "SELECT 1; SELECT 42; SELECT * FROM unknown_table"

        with self.assertRaises(FormatError) as cm:
            self.quiz.async_init()

        self.assertIn("Init SQL script failed", cm.exception.args[0])

    def test_async_init_error_in_solve_sql(self):
        self.source['solve_sql'] = "SELECT * FROM unknown_table"

        with self.assertRaises(FormatError) as cm:
            self.quiz.async_init()

        self.assertIn("The challenge is broken", cm.exception.args[0])
        self.assertIn("ERROR 1146", cm.exception.args[0])

    def test_async_init_wrong_solve_sql(self):
        self.source['solve_sql'] = "SELECT 42"

        with self.assertRaises(FormatError) as cm:
            self.quiz.async_init()

        self.assertIn("The challenge is broken", cm.exception.args[0])
        self.assertIn("Cannot find a record with id=3", cm.exception.args[0])

    def test_async_init_error_in_check_code(self):
        self.source['check_code'] = "def check(query, result): assert False"

        with self.assertRaises(FormatError) as cm:
            self.quiz.async_init()

        self.assertIn("score failed:", cm.exception.args[0])
        self.assertIn("AssertionError", cm.exception.args[0])

    def test_generate_create_db_and_user_and_init_db(self):
        dataset, clue = self.quiz.generate()

        self.assertEquals(dataset, {})
        self.assertSetEqual(set(clue.keys()), {'db_name', 'db_user', 'db_pass'})
        self.assertDatabaseExists(clue['db_name'])
        self.assertUserExists(clue['db_user'])
        res = self.db.execute("SHOW GRANTS for %s@'%%'", (clue['db_user'], ))
        self.assertEqual(res, 2)
        grants = self.db.fetchall()
        self.assertEquals(grants[1], ("GRANT ALL PRIVILEGES ON `{0}`.* TO '{1}'@'%'"
                                      .format(clue['db_name'], clue['db_user']), ))
        attempt_db_conn = MySQLdb.connect(host=settings.SQL_DB_HOST,
                                          port=settings.SQL_BIND_PORT,
                                          user=clue['db_user'],
                                          passwd=clue['db_pass'],
                                          db=clue['db_name'])
        attempt_db = attempt_db_conn.cursor()
        self.assertEqual(attempt_db.execute("SHOW TABLES LIKE 'users'"), 1)

    def test_generate_error_in_init_sql(self):
        self.source['init_sql'] = "SELECT 1; SELECT 42; SELECT * FROM unknown_table"
        db_count = self.db.execute("SHOW DATABASES")

        with self.assertRaises(InitSqlError) as cm:
            self.quiz.generate()

        self.assertEquals(cm.exception.args[0], 1146)
        self.assertIn('unknown_table', cm.exception.args[1])
        # created uninitialized database should be cleaned up
        self.assertEquals(self.db.execute("SHOW DATABASES"), db_count)

    def test_safe_execute(self):
        result = self.quiz._safe_execute(self.db, "SELECT 42; SELECT 100500")

        expected_result = {
            'status': QueryStatus.SUCCEEDED,
            'affected_rows': 1,
            'columns': ('42', ),
            'rows': ((42, ), ),
        }
        self.assertEqual(result, expected_result)

    def test_safe_execute_timeout(self):
        max_execution_time = settings.SQL_MAX_EXECUTION_TIME
        settings.SQL_MAX_EXECUTION_TIME = 1

        result = self.quiz._safe_execute(self.db, "SELECT 42; SELECT sleep(5)")

        settings.SQL_MAX_EXECUTION_TIME = max_execution_time
        expected_result = {
            'status': QueryStatus.FAILED,
            'error_code': 2013,
            'error_msg': mock.ANY,
            'is_killed': True,
        }
        self.assertEqual(result, expected_result)
        self.assertIn("ran too long", result['error_msg'])

    def test_execute_learner_empty_query(self):
        _, clue = self.quiz.generate()

        result = self.quiz._execute_learner_query("", clue)

        expected_result = {
            'status': 'failed',
            'error_code': 1065,
            'error_msg': "Query was empty",
            'is_killed': False,
        }
        self.assertEqual(result, expected_result)

    def test_execute_learner_select_query(self):
        _, clue = self.quiz.generate()

        result = self.quiz._execute_learner_query("SELECT * FROM users", clue)

        expected_result = {
            'status': 'succeeded',
            'affected_rows': 2,
            'columns': ('id', 'name', 'age'),
            'rows': ((1, "Stepic Stepicov", 3), (2, "Coursera Courserova", 42)),
        }
        self.assertEqual(result, expected_result)

    def test_execute_learner_only_one_query(self):
        _, clue = self.quiz.generate()

        result = self.quiz._execute_learner_query("SELECT 42; DROP TABLE users", clue)

        expected_result = {
            'status': 'succeeded',
            'affected_rows': 1,
            'columns': ('42', ),
            'rows': ((42, ), ),
        }
        self.assertEqual(result, expected_result)
        db = get_db_root_cursor(db_name=clue['db_name'])
        self.assertEqual(db.execute("SHOW TABLES LIKE 'users'"), 1)

    @override_settings(SQL_MAX_EXECUTION_TIME=1)
    def test_execute_learner_timeout_query(self):
        _, clue = self.quiz.generate()

        result = self.quiz._execute_learner_query("SELECT sleep(5)", clue)

        expected_result = {
            'status': 'failed',
            'error_code': 2013,
            'error_msg': "Lost connection to MySQL server during query\n"
                         "This may happen because the query ran too long.",
            'is_killed': True,
        }
        self.assertEqual(result, expected_result)

    def test_check_select(self):
        self.source['check_code'] = textwrap.dedent("""
            def check(query, result):
                return True
            """)
        _, clue = self.quiz.generate()

        score, hint = self.quiz.check("SELECT * FROM users", clue)

        self.assertTrue(score)
        self.assertEqual(hint, "Query result:\n"
                               "+----+---------------------+-----+\n"
                               "| id | name                | age |\n"
                               "+----+---------------------+-----+\n"
                               "| 1  | Stepic Stepicov     | 3   |\n"
                               "| 2  | Coursera Courserova | 42  |\n"
                               "+----+---------------------+-----+\n"
                               "Affected rows: 2")

    @override_settings(SQL_QUERY_RESULT_MAX_SIZE=1)
    def test_check_select_truncated_rows(self):
        self.source['check_code'] = textwrap.dedent("""
            def check(query, result):
                return True
            """)
        _, clue = self.quiz.generate()

        score, hint = self.quiz.check("SELECT * FROM users", clue)

        self.assertTrue(score)
        self.assertEqual(hint, "Query result:\n"
                               "+----+-----------------+-----+\n"
                               "| id | name            | age |\n"
                               "+----+-----------------+-----+\n"
                               "| 1  | Stepic Stepicov | 3   |\n"
                               "+----+-----------------+-----+\n"
                               "Affected rows: 2. Showed first 1 rows")

    def test_check_sql_error(self):
        _, clue = self.quiz.generate()

        score, hint = self.quiz.check("SELECT * FROM unknown_table", clue)

        self.assertFalse(score)
        self.assertEqual(hint, "ERROR 1146: Table '{0}.unknown_table' doesn't exist"
                               .format(clue['db_name']))

    def test_check_insert_correct(self):
        _, clue = self.quiz.generate()
        query = "INSERT INTO users (name, age) VALUES ('Student Studentov', 1)"

        score, hint = self.quiz.check(query, clue)

        self.assertTrue(score)
        self.assertEqual(hint, "Affected rows: 1")

    def test_check_not_inserted(self):
        _, clue = self.quiz.generate()

        score, hint = self.quiz.check("SELECT 42", clue)

        self.assertFalse(score)
        self.assertIn("Cannot find a record with id=3", hint)
        self.assertIn("| 42 |", hint)

    def test_cleanup(self):
        _, clue = self.quiz.generate()
        self.assertDatabaseExists(clue['db_name'])
        self.assertUserExists(clue['db_user'])

        self.quiz.cleanup(clue)

        self.assertDatabaseNotExists(clue['db_name'])
        self.assertUserNotExists(clue['db_user'])

    def test_cleanup_no_database_and_user(self):
        clue = dict(db_name='unknown', db_user='unknown', db_pass='pass')
        self.assertDatabaseNotExists(clue['db_name'])
        self.assertUserNotExists(clue['db_user'])

        self.quiz.cleanup(clue)
