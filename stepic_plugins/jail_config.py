import os
import pwd
import shutil
import logging

from codejail import jail_code

from .utils import get_limits_for_java


logger = logging.getLogger(__name__)


def configure_by_language(config_dict, prefix, limits, user=None, env=None):
    for lang, options in config_dict.items():
        binary = options['bin']
        if not shutil.which(binary):
            msg = "can't find {} binary for {}!"
            logger.warning(msg.format(binary, lang))
        else:
            jail_code.configure(prefix + lang, binary, limits,
                                user=user,
                                extra_args=options['args'],
                                env=env)


def configure_jail_code(settings):
    # we need HOME because we don't want jailed code to read /etc/passwd
    if not settings.SANDBOX_USER:
        home = os.path.expanduser('~')
    else:
        home = pwd.getpwnam(settings.SANDBOX_USER).pw_dir
    python_env = settings.SANDBOX_ENV.copy()
    python_env.update({"HOME": home})
    jail_code.configure('python',
                        settings.SANDBOX_PYTHON,
                        settings.SANDBOX_LIMITS,
                        user=settings.SANDBOX_USER,
                        env=python_env)

    jail_code.configure('user_code',
                        './main',
                        settings.USER_CODE_LIMITS,
                        user=settings.SANDBOX_USER,
                        env=settings.SANDBOX_ENV)

    if settings.SANDBOX_JAVA:
        java_limits, args = get_limits_for_java(settings.USER_CODE_LIMITS)
        jail_code.configure('run_java',
                            settings.SANDBOX_JAVA,
                            java_limits,
                            extra_args=args,
                            user=settings.SANDBOX_USER,
                            env=settings.SANDBOX_ENV)

    compilers_env = settings.SANDBOX_ENV.copy()
    compilers_env.update({"PATH": os.environ["PATH"]})
    configure_by_language(settings.COMPILERS, 'compile_', settings.COMPILER_LIMITS,
                          env=compilers_env)
    if 'java' in settings.COMPILERS:
        options = settings.COMPILERS['java']
        java_limits, args = get_limits_for_java(settings.COMPILER_LIMITS)
        args = ['-J' + arg for arg in args]
        jail_code.configure('compile_java',
                            options['bin'],
                            java_limits,
                            extra_args=options['args'] + args,
                            env=compilers_env)

    configure_by_language(settings.INTERPRETERS, 'run_', settings.USER_CODE_LIMITS,
                          user=settings.SANDBOX_USER, env=settings.SANDBOX_ENV)
    run_python3_env = settings.SANDBOX_ENV.copy()
    run_python3_env.update({"HOME": home})
    jail_code.configure('run_python3',
                        settings.SANDBOX_PYTHON,
                        settings.USER_CODE_LIMITS,
                        user=settings.SANDBOX_USER,
                        env=run_python3_env)
