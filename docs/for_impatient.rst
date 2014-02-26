For Impatient
*************

* install **Python 3** and **git**
* ``git clone https://github.com/StepicOrg/stepic-plugins``
* ``cd stepic-plugins``
* ``pip install -r requirements.txt``
* ``cd stepic_plugins``
* open `this JS Bin <http://jsbin.com/hikik/latest/edit>`_
* add templates from ``quizzes/simple_choice/{edit, show}.hbs`` to JS Bin html panel
* add functions from ``quizzes/simple_choice/{edit, show}.js`` to JS Bin javascript panel
* run development server ``python3 server.py simple-choice``
* now you can play with Simple Choice Quiz from JS Bin interface
  which will talk with your server on localhost (127.0.0.1:5000).
* experiment with frontend in JS Bin and with backend in ``quizzes/simple_choice/__init__.py``
* start creating your own quiz, just copy files from ``quizzes/template`` to ``quizzes/your_quiz``
