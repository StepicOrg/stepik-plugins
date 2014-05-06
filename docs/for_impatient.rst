For Impatient
*************

* click this image |nitrous| to create server in `Nitrous.IO <http://nitrous.io>`_
* start server by running ``workspace/stepic-plugins/stepic_plugins/conf_nitrous.sh``
* open `this JS Bin <http://jsbin.com/hikik/latest/edit>`_
* add templates from ``quizzes/simple_choice/{edit, show}.hbs`` to JS Bin html panel
* add functions from ``quizzes/simple_choice/{edit, show}.js`` to JS Bin javascript panel
* find out server's public URL from your `dashboard <https://www.nitrous.io/app#/boxes>`_.
* assign ``http://XXXXXX.nitrousbox.com:5000`` to ``localhost`` in JS Bin javascript
* now you can play with Simple Choice Quiz from JS Bin interface
* experiment with frontend in JS Bin and with backend in ``quizzes/simple_choice/__init__.py``
* start creating your own quiz, just copy files from ``quizzes/template`` to ``quizzes/your_quiz``


.. |nitrous| image:: https://d3o0mnbgv6k92a.cloudfront.net/assets/hack-s-v1-7475db0cf93fe5d1e29420c928ebc614.png 
  :height: 16
  :alt: create server at Nitrous.IO
  :target: https://www.nitrous.io/hack_button?source=embed&runtime=django&repo=StepicOrg%2Fstepic-plugins&file_to_open=stepic_plugins%2Fquizzes%2Fsimple_choice%2F__init__.py