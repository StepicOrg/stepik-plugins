import inspect

from codejail import jail_code
from stepic_utils import utils, stepicrun

from stepic_plugins import settings


class JailedCodeFailed(Exception):
    pass


def run(command, code, data=None, files=None, output_limit=None, **kwargs):
    assert jail_code.is_configured('python')
    files = files or []
    files.append((code, 'quiz.py'))
    if data is not None:
        data = utils.encode(data)
    runcode = inspect.getsource(stepicrun)
    argv = ['--command={0}'.format(command),
            '--code-path=quiz.py']
    for k, v in kwargs.items():
        argv.append('--{0}={1}'.format(k, v))

    result = jail_code_wrapper("python", code=runcode, argv=argv, files=files,
                               stdin=data)
    if result.status != 0:
        try:
            stderr = result.stderr.decode()
        except ValueError:
            stderr = "undecodable stderr"
        if result.time_limit_exceeded:
            stderr = "Time limit exceeded\n" + stderr
        msg = "{} failed:\n{}".format(command, stderr)
        raise JailedCodeFailed(msg)
    if output_limit and result.stdout and len(result.stdout) > output_limit:
        raise JailedCodeFailed("output is too large")
    try:
        decoded = utils.decode(result.stdout) if result.stdout else None
    except ValueError:
        raise JailedCodeFailed("prints are not allowed, failed to decode stdout:\n{}".format(result.stdout))

    return decoded


def jail_code_wrapper(command, code, argv, files, stdin):
    with Arena() as a:
        return a.run_code(command, code=code, argv=argv, files=files, stdin=stdin)


class Arena(jail_code.Jail):
    def __init__(self):
        super().__init__(tmp_root=settings.ARENA_DIR)
