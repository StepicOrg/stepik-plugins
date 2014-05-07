Nitrous.IO
************

`Nitrous.IO <https://nitrous.io>`_ is a cloud application platform that helps you create and configure the infrastructure in just seconds.

You can spin up server side for Stepic plugins in Nitrous.IO for free. Just follow this link_. A minute later, when your Nitrous.IO box is ready just run this commands:

    * ``virtualenv hack-stepic -p python3.3``
    * ``source hack-stepic/bin/activate``
    * ``cd workspace/stepic-plugins/``
    * ``pip install -r requirements.txt``
    * ``cd stepic_plugins/``

Now server is ready! You can implement your quiz and start server with ``python dev-server/server.py QUIZ_NAME`` or play around with one of standard quizzes, for example "simple-choice" quiz: ``python dev-server/server.py simple-choice``.

To use this server from front end find out server's public URL from your `dashboard <https://www.nitrous.io/app#/boxes>`_.

.. _link: https://www.nitrous.io/hack_button?source=embed&runtime=django&repo=StepicOrg%2Fstepic-plugins&file_to_open=stepic_plugins%2Fquizzes%2Fsimple_choice%2F__init__.py
