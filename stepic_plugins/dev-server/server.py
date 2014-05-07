#!/usr/bin/env python3
import functools
import sys
import os
import traceback
import argparse
import inspect

from flask import Flask, request, jsonify, make_response, render_template, abort, Response
from flask.ext.cors import cross_origin

# modified version of http://stackoverflow.com/a/6655098
if __name__ == "__main__" and __package__ is None:
    # The following assumes the script is in the top level of the package
    # directory.  We use dirname() to help get the parent directory to add to
    # sys.path, so that we can import the current package.  This is necessary
    # since when invoked directly, the 'current' package is not automatically
    # imported.
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    sys.path.insert(1, parent_dir)
    # noinspection PyUnresolvedReferences
    import stepic_plugins

    __package__ = str("stepic_plugins")

from stepic_plugins.base import load_by_name
from stepic_plugins.exceptions import FormatError

app = Flask(__name__)


class Storage(object):
    def __init__(self):
        self.quiz_name = None
        self.quiz_class = None
        self.quiz = None
        self.dataset = None
        self.clue = None

STORE = Storage()


class InconsistentStateError(Exception):
    pass


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
        except InconsistentStateError as e:
            return make_response("InconsistentStateError: " + str(e), 400)
        except Exception as e:
            traceback.print_exc()
            return make_response("Exception! Check console output", 500)

    return wrapper


@app.route("/")
def index():
    name = STORE.quiz_name
    quiz_name_camelized = ''.join(x.capitalize() for x in name.split('-'))
    return render_template(
        'index.html', quiz_name=name, quiz_name_camelized=quiz_name_camelized)

@app.route("/quiz/static/<file>")
def quiz_static(file):
    base_dir = os.path.dirname(inspect.getabsfile(STORE.quiz_class.wrapped_class))
    mimetype = None
    if file in ['show.js', 'edit.js']:
        mimetype = 'application/javascript'
    elif file in ['show.hbs', 'edit.hbs']:
        mimetype = 'text/x-handlebars-template'
    else:
        abort(404)

    path = os.path.join(base_dir, file)
    if not os.path.isfile(path):
        return Response("Can't find {} file!".format(file), status=404, mimetype='text/plain')
    body = open(path).read()

    return Response(body, mimetype=mimetype)


@app.route("/quiz/", methods=['POST', 'OPTIONS'])
@jsbin_view
def create_quiz():
    global STORE
    if request.method == 'POST':
        quiz = STORE.quiz_class(request.json)
        supplementary = quiz.async_init()
        if supplementary:
            STORE.quiz = STORE.quiz_class(request.json, supplementary)
        else:
            STORE.quiz = STORE.quiz_class(request.json)
    return 'OK'


@app.route("/quiz/attempt/", methods=['POST', 'OPTIONS'])
@jsbin_view
def attempt():
    global STORE
    if not STORE.quiz:
        raise InconsistentStateError("Quiz should be created first\n"
                                     "Have you pressed `Update Quiz` button?")

    STORE.dataset, STORE.clue = STORE.quiz.generate()
    return jsonify(
        **STORE.dataset
    )


@app.route("/quiz/submission/", methods=['POST', 'OPTIONS'])
@jsbin_view
def submit():
    global STORE
    if not STORE.dataset:
        raise InconsistentStateError("Dataset should be created first\n"
                                     "Have you pressed `Get Dataset` button?")

    reply = request.json
    reply = STORE.quiz.clean_reply(reply, STORE.dataset)
    (score, hint) = STORE.quiz.check(reply, STORE.clue)
    return jsonify(
        score=score,
        hint=hint
    )


def start_server(quiz_name):
    STORE.quiz_name = quiz_name
    STORE.quiz_class = load_by_name(quiz_name)
    app.run(host='0.0.0.0', debug=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("quiz_name")
    args = parser.parse_args()
    start_server(args.quiz_name)
