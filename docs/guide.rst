A Guide To Plugin Creation
**************************

In this guide, a simple choice quiz will be created step by step.

Step 1: Design the quiz
=======================

How will the quiz look like? We should answer this question from two perspectives,
the author's and the student's.

Let's say that the author should specify a list of options, of which one must be marked
as a correct answer. Author should be able to add new options, to edit existing ones and to
change, which option is the correct one.

The student then should be presented with a random permutation of options. He will select
one he thinks is correct. If his choice coincide with the author's, he solves the quiz.

This design can be extended in a numerous ways, for example to allow selecting several
correct answers, but for the sake of simplicity we won't do this. Full featured implementation
of a choice quiz can be found at `plugins/choice`

Step 2: Create plugin scaffold
==============================

Create a directory 'plugins/simple_choice' and a file `__init__.py`
with the following contents:::

    from ..base import BaseQuiz

    class SimpleChoice(BaseQuiz):
        name = 'simple-choice'

Plugin backend is just a class that inherits from ``base.BaseQuiz`` and overrides several members.
At the moment we have overridden just ``name`` -- a unique label under which the quiz will be
registered.

Step 3: Design message format
=============================

The next step is to design a format of the quiz source, dataset and reply.

Formats are expressed with the help of JSON specification mini language.
In this language, JSON objects are specified as python dictionaries,
JSON arrays as lists and primitive types like ``int``, ``str``, etc.

For example, an object with field ``numbers`` which is an array of ints is specified as::

    {
        'numbers': [int]
    }

It's a good idea to start with a quiz source specification. In a case of a choice quiz it's
reasonable to represent a quiz as an object with one field ``options`` which is a list of
options, where ``option`` itself is and object with boolean field ``is_correct`` and
string field ``text``. If we encode it as a schema, we get::

    {
        'options': [{'is_correct': bool, 'text': str}]
    }

The dataset can be similarly encoded as a list of strings(we don't want to pass ``is_correct``
part to the user, don't we?)::

    {
        'options': [str]
    }

And reply is just a list of booleans::

    {
        'choices': [bool]
    }

Note that although JSON specification allows the top level entity to be an array, we must use
objects here.

To plug this schemas into the Quiz, define ``Schemas`` inner class, like this::

    from ..base import Quiz


    class SimpleChoice(Quiz):
        name = 'simple-choice'

        class Schemas:
            source = {
                'options': [{'is_correct': bool, 'text': str}]
            }

            dataset = {
                'options': [str]
            }

            reply = {
                'choices': [bool]
            }

Step 3: Creating quiz instance form source
==========================================

The next step is to create an ``__init__`` method, which should produce a Quiz instance from
source::

    def __init__(self, source):
        super().__init__(source)

In the ``__init__``, data will be a python object conforming to the schema. So, for example,
to iterate options, we could write::

    for options in source.options:
        ...

The data is guaranteed to conform to the schema, however it is still may be invalid.
Thus ``__init__`` method is also responsible for raising a ``FormatError`` in case of invalid
data.

In our case, data is valid if and only if only one of the options is correct.
So the complete ``__init__`` looks like this::

    def __init__(self, source):
        super().__init__(source)
        self.options = data.options
        correct_options = [option for option in self.options if option.is_correct]
        if len(correct_options) != 1:
            raise FormatError("Exactly one option must be correct")

Step 4: Generating a dataset and a clue
=======================================

Let's implement generate function. This function should return
a tuple of ``(dataset, clue)``. Dataset is send to the student. Clue will be used later
in score to evaluate student's submission. Usually the clue is just the correct answer,
however it may be something else, especially when there are multiple possible correct
answers.

For simple choice quiz, an array specifying for each option if it is correct or not is a
good clue. One thing to note is that dataset must be a python dictionary,
conforming to the schema.

So here is how generate may look like::

    def generate(self):
        options = self.options[:]  # copy options for shuffling
        random.shuffle(options)
        dataset = {
            'options': [option.text for option in options]
        }
        clue = [option.is_correct for option in options]
        return dataset, clue


Step 5: Cleaning users reply
============================

So now it's high time to evaluate users reply. But remember that although the reply is
guaranteed to be conforming with schema, it may still be malformed.

Method ``clean_reply`` is responsible for 'cleaning' user reply. That is, it should throw a
``FormatError`` if reply is malformed and return a transformed reply otherwise.
Transformation step is optional but may be convenient.

Note that ``clean_reply`` takes ``reply`` and ``dataset`` as arguments. Dataset is needed
because reply validity is dependent on it. For example in choice quiz reply must be the
same length as a dataset.

So here is the ``clean_reply`` method. We check that ``reply`` is of a correct length and
that it has exactly one ``True`` entry. We also for convenience transform reply from
object to a list of choices::

    def clean_reply(self, reply, dataset):
        choices = reply.choices
        if len(choices) != len(dataset.options):
            raise FormatError("Reply has a wrong length")
        if choices.count(True) != 1:
            raise FormatError("Reply has more than one choice")

        return choices


Step 6: Evaluating users reply
==============================

Method ``check`` evaluates user's reply. It takes a cleaned reply and a clue.
It should return a tuple of (score, hint), where score is a
boolean (True means correct answer) and hint is a string.

The ``check`` method turns out to be the simplest one because all heavy lifting was done
while generating a clue and cleaning the reply::

    def check(self, reply, clue):
        return reply == clue, ''

Step 7: Testing backend
=======================

Let's write some tests! They should go to `tests.py` file. You can write
usual unittest tests there, however there are several convenient base classes
in `plugins/tests.py` for testing plugins in a declarative way.

To write a declarative test for one of a functions(``__init__``, ``generate``,
``clean_reply``, ``check``) you should subclass a proper base class and implement
the ``specs`` method. This method should return `specs`: a list with object describing
pairs of input arguments and expected outputs.

Let's do this first for generate. Looking at `plugins/tests.py`, we find that ``InitTest``
is a proper base class with the following spec format::

    {
        'quiz_class': A class to test,
        'source': argument of __init__,
        'output': Exception or asserting function
    }

So the test that checks that it is impossible to create quiz without correct answer
should look like this::

    from ..exceptions import FormatError
    from ..tests import InitTest
    from . import SimpleChoice

    class SimpleChoiceInitTest(InitTest):
        def specs(self):
            return [
                {
                    'quiz_class': SimpleChoice,
                    'source': {
                        'options': [
                            {'is_correct': True, 'text': 'A'},
                            {'is_correct': True, 'text': 'B'},
                        ]
                    },
                    'output': FormatError
                },

            ]

However if we run this test with ``python -m unittest plugins.simple_choice.tests`` we
see that it is failing with message `AttributeError: 'dict' object
has no attribute 'options'`. Indeed, ``__init__`` method expects an object with ``options``
attribute, and not the dictionary ``{'options': ..}``. To fix this problem, we can
substitute dict for object with attributes, however it is not very convenient.

It would be nice to wrap quiz object into a wrapper, which has the same interface,
except that it accept dictionaries as an arguments, converts them to objects with
the help of schema and delegates to underlying quiz. And there is a easy way to create
such wrapper: function ``base.quiz_wrapper_factory`` does exactly this. So, we can rewrite
the test like this::

    from ..base import quiz_wrapper_factory
    from ..exceptions import FormatError
    from ..tests import InitTest
    from . import SimpleChoice

    Quiz = quiz_wrapper_factory(SimpleChoice)


    class SimpleChoiceInitTest(InitTest):
        def specs(self):
            return [
                {
                    'quiz_class': Quiz,
                    'source': {
                        'options': [
                            {'is_correct': True, 'text': 'A'},
                            {'is_correct': True, 'text': 'B'},
                        ]
                    },
                    'output': FormatError
                },

            ]

Now it passes tests.

Other functions can be tested similarly, refer to `plugins/simple_choice/tests.py` for
implementation details.

One more thing to mention is that you can use ``'->'`` key to propagate values into specs.
That is, instead of writing::

    [
        {
            'quiz_class': Quiz,
            'output': FormatError,
            'source': {
                'options': [
                    {'is_correct': True, 'text': 'A'},
                    {'is_correct': True, 'text': 'B'},
                ]
            }
        },
        {
            'quiz_class': Quiz,
            'output': FormatError,
            'source': {
                'options': [
                    {'is_correct': False, 'text': 'A'},
                    {'is_correct': False, 'text': 'B'},
                ]
            }
        },
    ]

you can write::

    [
        {
            'quiz_class': QuizClass,
            'output': FormatError,
            '->': [
                {
                    'source': {
                        'options': [
                            {'is_correct': True, 'text': 'A'},
                            {'is_correct': True, 'text': 'B'},
                        ]
                    },
                },
                {
                    'source': {
                        'options': [
                            {'is_correct': False, 'text': 'A'},
                            {'is_correct': False, 'text': 'B'},
                        ]
                    },
                }
            ]
        }
    ]

Step 8: Getting started with frontend
=====================================

To create a Quiz frontend you should define two javascript functions, ``editQuiz``
and ``showQuiz``. This functions should create necessary UI and return an object
with ``submit`` method. This method should return an object representing quiz source
for ``editQuiz`` and reply for ``showQuiz``.

Create a new jsbin(http://jsbin.com/) and paste html and js file from `plugins/jsbin`
there. You will see stub ``editQuiz`` and ``showQuiz`` functions at the top of js file.

In the html file there are two stub handlebars templates -- this templates will be used
to render the quiz.


Step 9: Creating edit UI
========================

``editQuiz`` function takes three arguments:
    * ``target`` -- jQuery object representing parent DOM element.
    * ``template`` -- a compiled handlebars template.
    * ``source`` -- an empty object, if it is a new quiz, or existing quiz source.

It should return an object with ``submit`` method, which should return new source.

If you press ``update button`` you will see ``source`` data which will be send to server.

Simple edit template for choice quiz looks like this::

    <script id="edit-template" type="text/x-handlebars-template">
      <div class="options">
        {{#each options}}
        <div class="option">
          <input type="checkbox" class="is_correct"/>
          <input type="text" class="text"/>
        </div>
        {{/each}}
      </div>
      <button class="button tiny">+</button>
    </script>

And simple edit function like this::

    function editQuiz(target, template, source) {
      target.html(template(source));
      target.find('button').click(function () {
        var row = $('<div class="option"><input type="checkbox" class="is_correct"/><input type="text" class="text"/></div>');
        target.find('.options').append(row);
      });

      return {
        'submit': function () {
          var options = target.find('.option').map(function () {
            var t = $(this);
            return {
              'is_correct': t.find('.is_correct').prop('checked'),
              'text': t.find('.text').val()
            };
          }).get();
          return {'options': options };
        }
      };
    }

Step 10: Launching development server
=====================================

To test frontend part in conjunction with backend part, you should launch a
development server. Do it with the command::

    $ python3 plugins/server.py plugins.simple_choice.SimpleChoice

Flask development server will be started. This server will be able co communicate
with jsbin. If you now press `update` button on http://jsbin.com, you will see "OK" in `Update response`
field or error in the console.


Step 11: Creating show UI
=========================

``showQuiz`` function takes five arguments:
    * ``target``
    * ``template``
    * ``dataset``
    * ``reply``
    * ``disabled``

It should return an object with ``submit`` method, which should return new reply.

If you press `Get Dataset` button, a server responds with a new dataset, which is passed to
``showQuiz`` function. If you press `Submit` button, the ``reply`` is send to server and
resulting score and hint are displayed.

For choice quiz, simple template looks like this::

    <script id="show-template" type="text/x-handlebars-template">
    {{#each options}}
      <label>
        <input type="radio" name="options"/>
        <span>{{ this }}</span>
      </label>
      {{/each}}
    </script>

And simple functions looks like this::

    function showQuiz(target, template, dataset, reply, disabled) {
      target.html(template(dataset));
      return {
        'submit': function () {
          var choices = target.find("input").map(function () {
            return $(this).prop("checked");
          }).get();
          return {'choices': choices };
        }
      };
    }

Step 12: Integrating UI with Stepic
===================================

???
