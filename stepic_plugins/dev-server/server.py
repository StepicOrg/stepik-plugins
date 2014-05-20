#!/usr/bin/env python3
import functools
import sys
import os
import traceback
import argparse
import inspect

from flask import Flask, request, jsonify, make_response, render_template, abort, Response
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
        self.dataset_created = False
        self.clue = None

STORE = Storage()


class InconsistentStateError(Exception):
    pass


def jsbin_view(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
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
    def read_file(file):
        base_dir = os.path.dirname(inspect.getabsfile(STORE.quiz_class.wrapped_class))
        path = os.path.join(base_dir, file)
        return open(path).read() if os.path.isfile(path) else None

    mime_map = [
        ({'show.js', 'edit.js', 'show.coffee', 'edit.coffee'}, 'application/javascript'),
        ({'show.hbs', 'edit.hbs'}, 'text/x-handlebars-template'),
        ({'style.css'}, 'text/css')
    ]
    for files, mime in mime_map:
        if file in files:
            mimetype = mime
            break
    else:
        mimetype = None

    if not mimetype:
        abort(404)

    body = read_file(file)
    if body is None and file.endswith('.js'):
        coffee_source = read_file(file.replace('.js', '.coffee'))
        if coffee_source is not None:
            if not coffeescript:
                raise Exception("coffeescript module is required to compile coffeescript")
            body = coffeescript.compile(coffee_source)

    if body is None:
        return Response("Can't find {} file!".format(file), status=404, mimetype='text/plain')

    return Response(body, mimetype=mimetype)


@app.route("/quiz/", methods=['POST'])
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


@app.route("/quiz/attempt/", methods=['POST'])
@jsbin_view
def attempt():
    global STORE
    if not STORE.quiz:
        raise InconsistentStateError("Quiz should be created first\n"
                                     "Have you pressed `Update Quiz` button?")

    STORE.dataset, STORE.clue = STORE.quiz.generate() or (None, None)
    STORE.dataset_created = True
    return jsonify(**STORE.dataset) if STORE.dataset else jsonify({'dataset': ''})


@app.route("/quiz/submission/", methods=['POST'])
@jsbin_view
def submit():
    global STORE
    if not STORE.dataset_created:
        raise InconsistentStateError("Dataset should be created first\n"
                                     "Have you pressed `New Attempt` button?")

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
