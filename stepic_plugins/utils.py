import decimal
import logging
import os
import pwd
import shutil

import bleach
from codejail import jail_code

from stepic_plugins.exceptions import FormatError


logger = logging.getLogger(__name__)


def configure_by_language(config_dict, prefix, limits, user=None, env=None):
    for lang, options in config_dict.items():
        binary = options['bin']
        if not shutil.which(binary):
            msg = "can't find {} binary for {}!"
            logger.warning(msg.format(binary, lang))
        else:
            if 'limits' in options:
                limits.update(options['limits'])
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


def get_limits_for_java(limits):
    java_limits = dict(limits)
    # for gc
    java_limits["CAN_FORK"] = True
    # setrlimit does not work because of MAP_NORESERVE, use -Xmx instead
    java_limits["MEMORY"] = None
    xmxk = limits["MEMORY"] // 1024
    return java_limits, ["-Xmx{}k".format(xmxk), "-Xss8m"]


ALLOWED_TAGS = [
    'a',
    'abbr',
    'acronym',
    'b',
    'blockquote',
    'br',
    'code',
    'div',
    'em',
    'h1',
    'h2',
    'h3',
    'i',
    'img',
    'li',
    'ol',
    'p',
    'pre',
    'span',
    'strong',
    'ul',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel', 'target'],
    'abbr': ['title'],
    'acronym': ['title'],
    'div': ['class'],
    'img': ['src', 'alt', 'class', 'title', 'width', 'height'],
    'span': ['class'],
    'p': ['class'],
    'code': ['class']
}

ALLOWED_STYLES = []


def clean_html(text, strip=True):
    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES,
                        styles=ALLOWED_STYLES, strip=strip)


NUMBER_REPLACEMENTS = (
    (' ', ''),
    (',', '.'),
    ('\N{HYPHEN}', '-'),
    ('\N{NON-BREAKING HYPHEN}', '-'),
    ('\N{FIGURE DASH}', '-'),
    ('\N{EN DASH}', '-'),
    ('\N{EM DASH}', '-'),
    ('\N{HORIZONTAL BAR}', '-'),
    ('\N{MINUS SIGN}', '-'),
)


def parse_decimal(s, filed_name):
    for old, new in NUMBER_REPLACEMENTS:
        s = s.replace(old, new)
    try:
        return decimal.Decimal(s)
    except decimal.DecimalException:
        raise FormatError("Field `{}` should be a number".format(filed_name))
