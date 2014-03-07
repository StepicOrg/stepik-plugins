#!/usr/bin/env python3
import fnmatch
from inspect import getsourcefile
import os
import sys
import shutil

try:
    import coffeescript
except ImportError:
    coffeescript = None

# modified version of http://stackoverflow.com/a/6655098
if __name__ == "__main__" and __package__ is None:
    # The following assumes the script is in the top level of the package
    # directory.  We use dirname() to help get the parent directory to add to
    # sys.path, so that we can import the current package.  This is necessary
    # since when invoked directly, the 'current' package is not automatically
    # imported.
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(1, parent_dir)
    # noinspection PyUnresolvedReferences
    import stepic_plugins
    __package__ = str("stepic_plugins")

from .server import load_by_name

if __name__ == "__main__":
    name = sys.argv[1]
    quiz = load_by_name(name)
    quiz_directory = os.path.dirname(getsourcefile(quiz.wrapped_class))
    static_directory = os.path.join(os.path.dirname(__file__), 'static', 'stepic_plugins', name)

    if os.path.exists(static_directory):
        shutil.rmtree(static_directory)
    os.mkdir(static_directory)
    coffee = '*.coffee'
    patterns = ['*.js', '*.css', '*.hbs', coffee]
    for file in os.listdir(quiz_directory):
        if any(fnmatch.fnmatch(file, p) for p in patterns):
            source = os.path.join(quiz_directory, file)
            target = os.path.join(static_directory, file)

            if fnmatch.fnmatch(file, coffee):
                if coffeescript is None:
                    print('package `CoffeeScript` required', file=sys.stderr)
                target = os.path.splitext(target)[0] + '.js'
                with open(target, 'w') as f:
                    f.write(coffeescript.compile_file(source))
            else:
                relative_source = os.path.relpath(source, static_directory)
                os.symlink(relative_source, target)
