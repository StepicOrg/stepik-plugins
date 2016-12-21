import random
import string
import threading
import time

import docker
import MySQLdb
import sqlparse
import structlog
import textwrap

from docker.errors import APIError, DockerException, NotFound
from docker.utils import create_host_config
from terminaltables import AsciiTable

from stepic_plugins import settings
from stepic_plugins.base import BaseQuiz
from stepic_plugins.exceptions import FormatError, PluginError
from stepic_plugins.executable_base import JailedCodeFailed, run


logger = structlog.get_logger(plugin='sql')


MYSQL_ERROR = "ERROR {0}: {1}"
DB_NAME_PREFIX = 'stepic_'
WAIT_DB_CONTAINER_STARTED_TIMEOUT = 120
CHECK_CODE_LIMITS = {
    'TIME': 30,
    'MEMORY':  128 * 1024 * 1024,
}


class QueryStatus(object):
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'


class InitSqlError(MySQLdb.ProgrammingError):
    """Exception raised for errors in init sql script."""


def get_db_cursor(db_user, db_pass, db_name=None):
    db = MySQLdb.connect(host=settings.SQL_DB_HOST,
                         port=settings.SQL_BIND_PORT,
                         user=db_user,
                         passwd=db_pass,
                         db=db_name if db_name else '',
                         autocommit=True)
    return db.cursor()


def get_db_root_cursor(db_name=None):
    return get_db_cursor('root', settings.SQL_DB_ROOT_PASS, db_name=db_name)


def random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


class SqlQuiz(BaseQuiz):
    name = 'sql'

    class Schemas:
        source = {
            'init_sql': str,
            'solve_sql': str,
            'check_code': str,
        }
        dataset = {}
        reply = {
            'solve_sql': str,
        }

    def __init__(self, source):
        super().__init__(source)
        self.docker = docker.Client(base_url=settings.SQL_DOCKER_HOST)

    def async_init(self):
        try:
            _, clue = self.generate()
        except InitSqlError as e:
            raise FormatError("Init SQL script failed:\n" +
                              MYSQL_ERROR.format(e.args[0], e.args[1]))
        score, hint = self.check(self.source.solve_sql, clue)
        if not score:
            raise FormatError("The challenge is broken. Please verify your solution "
                              "query and check code.\n" + hint)

    def generate(self):
        self._start_db_container()
        db_name = db_user = DB_NAME_PREFIX + random_string(8)
        db_pass = random_string(8)
        db = get_db_root_cursor()
        db.execute("CREATE DATABASE " + db_name)
        db.execute("CREATE USER %s@'%%' IDENTIFIED BY %s", (db_user, db_pass))
        db.execute("GRANT ALL PRIVILEGES ON {0}.* TO %s@'%%'".format(db_name), (db_user, ))
        db.close()
        clue = dict(db_name=db_name, db_user=db_user, db_pass=db_pass)
        if self.source.init_sql.strip():
            attempt_db = get_db_cursor(db_user, db_pass, db_name)
            result = self._safe_execute(attempt_db, self.source.init_sql,
                                        fetch_size=1)
            if not result.get('is_killed', False):
                attempt_db.close()
            if result['status'] != QueryStatus.SUCCEEDED:
                self.cleanup(clue)
                raise InitSqlError(result['error_code'], result['error_msg'])
        return {}, clue

    def clean_reply(self, reply, dataset):
        solve_sql = reply.solve_sql.strip()
        if not solve_sql:
            raise FormatError("Empty query")
        if len(sqlparse.split(solve_sql)) > 1:
            raise FormatError("Only one query is allowed")
        return solve_sql

    def check(self, reply, clue):
        self._start_db_container()
        result = self._execute_learner_query(reply, clue)
        if result['status'] == QueryStatus.SUCCEEDED:
            hint = ''
            if result['rows']:
                table = [list(result['columns'])]
                table.extend(list(map(str, row)) for row in result['rows'])
                hint = "Query result:\n" + AsciiTable(table).table + "\n"
            affected_rows_msg = "Affected rows: {}".format(result['affected_rows'])
            if (result['affected_rows'] > settings.SQL_QUERY_RESULT_MAX_SIZE and
                        len(result['rows']) == settings.SQL_QUERY_RESULT_MAX_SIZE):
                affected_rows_msg += ". Showed first {} rows".format(
                    settings.SQL_QUERY_RESULT_MAX_SIZE)
            hint += affected_rows_msg
            check_result = {k: result[k] for k in ['affected_rows', 'columns', 'rows']}
            score, teacher_hint = self._check_learner_query_result(reply, check_result, clue)
            if teacher_hint:
                hint = teacher_hint + '\n\n' + hint
            return score, hint
        elif result['status'] == QueryStatus.FAILED:
            hint = MYSQL_ERROR.format(result['error_code'], result['error_msg'])
            return False, hint
        return False, ""

    def cleanup(self, clue):
        self._start_db_container()
        db = get_db_root_cursor()
        db.execute("DROP DATABASE IF EXISTS " + clue['db_name'])
        try:
            db.execute("DROP USER %s@'%%'", (clue['db_user'], ))
        except db.DatabaseError:
            logger.exception("Failed to drop user: '%s'", clue['db_user'])
        db.close()

    def _start_db_container(self):
        """Start a new db container if it hasn't been started yet."""
        try:
            return self.docker.inspect_container(settings.SQL_CONTAINER_NAME)
        except NotFound:
            pass
        # TODO: start if stopped
        # TODO: handle docker connection error
        logger.info("Starting new db container")
        try:
            self.docker.inspect_image(settings.SQL_CONTAINER_IMAGE)
        except NotFound:
            logger.info("Docker image for db container wasn't found, pulling...")
            self.docker.pull(settings.SQL_CONTAINER_IMAGE)
            logger.info("Docker image for db container has been pulled successfully")
        port_bindings = {settings.SQL_CONTAINER_PORT: (settings.SQL_BIND_HOST,
                                                       settings.SQL_BIND_PORT)}
        environment = {'MYSQL_ROOT_PASSWORD': settings.SQL_DB_ROOT_PASS}
        host_config = create_host_config(binds=['{}:{}'.format(settings.SQL_CONTAINER_NAME,
                                                               settings.SQL_CONTAINER_VOLUME)])
        try:
            ctr = self.docker.create_container(settings.SQL_CONTAINER_IMAGE,
                                               command=settings.SQL_DB_CONF_OPTIONS,
                                               name=settings.SQL_CONTAINER_NAME,
                                               environment=environment,
                                               host_config=host_config)
            self.docker.start(ctr, port_bindings=port_bindings,
                              restart_policy={'Name': 'always'})
        except (APIError, DockerException):
            logger.exception("Failed to start db container '{0}'"
                             .format(settings.SQL_CONTAINER_NAME))
            raise PluginError("Failed to start db container")
        self._wait_db_container_started(ctr)
        return ctr

    def _wait_db_container_started(self, container):
        logger.info("Waiting for db container to be ready")
        try:
            for _ in range(WAIT_DB_CONTAINER_STARTED_TIMEOUT):
                ctr_info = self.docker.inspect_container(container)
                if not ctr_info['State']['Running']:
                    logger.error("Started db container terminated unexpectedly")
                    raise PluginError("Failed to start db container (terminated unexpectedly)")
                logs = self.docker.logs(container)
                if logs.count(b"mysqld: ready for connections") >= 2:
                    logger.info("DB container started and ready for connections")
                    break
                time.sleep(1)
        except (APIError, DockerException):
            logger.exception("Failed to start db container '{0}' (timed out)"
                             .format(settings.SQL_CONTAINER_NAME))
            raise PluginError("Failed to start db container (timed out)")

    def _safe_execute(self, cursor, query, fetch_size=None):
        """Execute a query with time limit.

        Runs a Timer thread that kills the query and connection after
        `SQL_MAX_EXECUTION_TIME` seconds if it is still running.

        """
        self.is_query_killed = False
        proc_id = cursor.connection().thread_id()
        kill_query_timer = threading.Timer(settings.SQL_MAX_EXECUTION_TIME,
                                           self._kill_query, (proc_id, ))
        kill_query_timer.start()
        try:
            affected_rows = cursor.execute(query)
            columns = tuple(c[0] for c in cursor.description) if cursor.description else ()
            rows = cursor.fetchmany(size=fetch_size)
            while cursor.nextset():
                pass
        except cursor.DatabaseError as e:
            result = {
                'status': QueryStatus.FAILED,
                'error_code': e.args[0],
                'error_msg': e.args[1],
                'is_killed': self.is_query_killed,
            }
            if self.is_query_killed:
                result['error_msg'] += "\nThis may happen because the query ran too long."
            return result
        finally:
            kill_query_timer.cancel()
        return {
            'status': QueryStatus.SUCCEEDED,
            'affected_rows': affected_rows,
            'columns': columns,
            'rows': rows,
        }

    def _kill_query(self, proc_id):
        logger.info("Killing query execution with processlist_id: %s", proc_id)
        self.is_query_killed = True
        db = get_db_root_cursor()
        try:
            db.execute("KILL %s", (proc_id, ))
        except db.DatabaseError:
            logger.exception("Failed to kill query execution with processlist_id: %s", proc_id)
        db.close()

    def _execute_learner_query(self, query, clue):
        first_query_end = query.find(';')
        if first_query_end >= 0:
            query = query[:first_query_end]
        with get_db_cursor(clue['db_user'], clue['db_pass'], clue['db_name']) as db:
            return self._safe_execute(db, query, fetch_size=settings.SQL_QUERY_RESULT_MAX_SIZE)

    def _check_learner_query_result(self, query, result, clue):
        check_code = textwrap.dedent("""
            import MySQLdb

            db = MySQLdb.connect(host='{host}',
                                 port={port},
                                 user='{user}',
                                 passwd='{passwd}',
                                 db='{db}')
            cursor = db.cursor()

            def generate():
                pass

            def solve(dataset):
                pass

            {teacher_check}
            """).format(host=settings.SQL_DB_HOST,
                        port=settings.SQL_BIND_PORT,
                        user=clue['db_user'],
                        passwd=clue['db_pass'],
                        db=clue['db_name'],
                        teacher_check=self.source.check_code)
        try:
            return run('score', check_code, data=(query, result))
        except JailedCodeFailed as e:
            raise FormatError(str(e))
