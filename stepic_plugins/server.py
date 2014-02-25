#!/usr/bin/env python3
import functools
import sys
import os
import traceback

from flask import Flask, request, jsonify, make_response, abort
from flask.ext.cors import cross_origin



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

from .base import quiz_wrapper_factory, load_by_name
from .exceptions import FormatError

app = Flask(__name__)


class Storage(object):
    def __init__(self):
        self.quiz_class = None
        self.quiz = None
        self.dataset = None
        self.clue = None


STORE = Storage()


def jsbin_view(f):
    @cross_origin(headers=['Content-Type'])
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if request.method == 'OPTIONS':  # browser 'preflight' POST with OPTIONS
            return ""
        try:
            return f(*args, **kwargs)
        except FormatError as e:
            traceback.print_exc()
            return make_response("FormatError: " + str(e), 400)
        except Exception as e:
            traceback.print_exc()
            return make_response("Exception! Check console output", 500)

    return wrapper


@app.route("/", methods=['POST', 'OPTIONS'])
@jsbin_view
def create_quiz():
    global STORE
    if request.method == 'POST':
        STORE.quiz = quiz_wrapper_factory(STORE.quiz_class)(request.json)
        STORE.quiz.set_supplementary(STORE.quiz.get_supplementary())
    return 'OK'


@app.route("/attempt/", methods=['POST', 'OPTIONS'])
@jsbin_view
def attempt():
    global STORE
    if not STORE.quiz:
        abort(404, "Quiz should be crated first")

    STORE.dataset, STORE.clue = STORE.quiz.generate()
    return jsonify(
        **STORE.dataset
    )


@app.route("/submission/", methods=['POST', 'OPTIONS'])
@jsbin_view
def submit():
    global STORE
    if not STORE.dataset:
        abort(404, "Dataset should be crated first")

    reply = request.json
    reply = STORE.quiz.clean_reply(reply, STORE.dataset)
    (score, hint) = STORE.quiz.check(reply, STORE.clue)
    return jsonify(
        score=score,
        hint=hint
    )


def main():
    name = sys.argv[1]
    STORE.quiz_class = load_by_name(name)
    app.run(debug=True)


if __name__ == "__main__":
    main()
