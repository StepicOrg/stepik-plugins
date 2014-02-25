Naming Conventions
******************

Files for quiz "foo bar"::

    quizzes/
        foo_bar/
            __init__.py
            test.py
            edit.js
            edit.hbs
            show.js
            show.hbs

in ``quizzes/foo_bar/__init__.py``::

    from stepic_plugins.base import BaseQuiz

    class FooBarQuiz(BaseQuiz):
        name = 'foo-bar'
        ...

in ``quizzes/foo_bar/edit.js``::

    function editFooBarQuiz(...) {

        ...
    }

in ``quizzes/foo_bar/show.js``::

    function showFooBarQuiz(...) {
        ...
    }
