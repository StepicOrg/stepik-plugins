import base64
import decimal
import logging
import os
import pwd
import shutil

import bleach
from codejail import jail_code

from stepic_plugins.exceptions import FormatError
from stepic_plugins.schema import ATTACHMENT_HEADER


logger = logging.getLogger(__name__)


def configure_by_language(config_dict, prefix, limits, user=None, env=None):
    for lang, options in config_dict.items():
        binary = options['bin']
        if not shutil.which(binary):
            msg = "can't find {} binary for {}!"
            logger.warning(msg.format(binary, lang))
        else:
            lang_limits = dict(limits)
            if 'limits' in options:
                lang_limits.update(options['limits'])
            lang_env = env
            if 'env' in options:
                lang_env = env.copy() if env is not None else {}
                lang_env.update(options['env'])
            jail_code.configure(prefix + lang, binary, lang_limits,
                                user=user,
                                extra_args=options['args'],
                                env=lang_env)


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
    if settings.SANDBOX_JAVA8:
        java_limits, args = get_limits_for_java(settings.USER_CODE_LIMITS)
        jail_code.configure('run_java8',
                            settings.SANDBOX_JAVA8,
                            java_limits,
                            extra_args=args,
                            user=settings.SANDBOX_USER,
                            env=settings.SANDBOX_ENV)

    compilers_env = settings.SANDBOX_ENV.copy()
    compilers_env.update({"PATH": os.environ["PATH"], "HOME": home})
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
        if 'java8' in settings.COMPILERS:
            options = settings.COMPILERS['java8']
            jail_code.configure('compile_java8',
                                options['bin'],
                                java_limits,
                                extra_args=options['args'] + args,
                                env=compilers_env)
        if 'scala' in settings.COMPILERS:
            options = settings.COMPILERS['scala']
            jail_code.configure('compile_scala',
                                options['bin'],
                                java_limits,
                                extra_args=options['args'] + args,
                                env=dict(compilers_env,
                                         JAVA_HOME=settings.SANDBOX_JAVA_HOME))
            java_limits, args = get_limits_for_java(settings.USER_CODE_LIMITS)
            jail_code.configure('run_scala',
                                options['bin'][:-1],  # scalac -> scala
                                java_limits,
                                user=settings.SANDBOX_USER,
                                env=dict(settings.SANDBOX_ENV,
                                         JAVA_HOME=settings.SANDBOX_JAVA_HOME))

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
    'audio',
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
    'strike',
    'strong',
    'ul',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel', 'target'],
    'abbr': ['title'],
    'acronym': ['title'],
    'audio': ['src', 'controls'],
    'div': ['class'],
    'img': ['src', 'alt', 'class', 'title', 'width', 'height'],
    'span': ['class'],
    'p': ['class'],
    'code': ['class']
}

ALLOWED_STYLES = []


def clean_html(text, tags=ALLOWED_TAGS, strip=True):
    return bleach.clean(text, tags=tags, attributes=ALLOWED_ATTRIBUTES,
                        styles=ALLOWED_STYLES, strip=strip)


def normalize_text(text):
    return os.linesep.join(text.splitlines()).strip()


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


def attachment_content(attachment):
    content = (getattr(attachment, 'content') if hasattr(attachment, 'content')
               else attachment['content'])
    if not content:
        return None
    return base64.b64decode(content[len(ATTACHMENT_HEADER):])


def create_attachment(filename, content):
    if isinstance(content, str):
        content = content.encode()
    return {
        'name': filename,
        'type': 'application/octet-stream',
        'size': len(content),
        'content': ATTACHMENT_HEADER + base64.b64encode(content).decode(),
        'url': '',
    }
