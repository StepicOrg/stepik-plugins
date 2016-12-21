This repository contains the code of quizzes at [Stepik](https://stepik.org).

Requirements
===

Python >=3.4 required.

### Run tests

Make sure you've initialized the development environment:
```
$ make init
```
Run both RPC functional and unit tests for all quizzes:
```
$ py.test
```
#### Unit tests
```
$ py.test stepic_plugins/quizzes              # test all quizzes
$ py.test stepic_plugins/quizzes/<quiz_name>  # test only <quiz_name> quiz 
```
#### RPC functional tests
Run RPC functional tests using a fake server (doesn't require any external services and broker communication):
```
$ py.test tests
```
Run RPC functional tests against a running stepic-plugins instance using a real RabbitMQ broker:
```
$ py.test --rpc-url=rabbit://guest:guest@localhost:5672// tests
```

Documentation
===

http://stepic-plugins.readthedocs.org

or

```
pip install -r requirements.txt
cd doc
make html
your-browser _build/html/index.html
```

Let's Start
===

[Quick Start](http://stepic-plugins.readthedocs.org/en/latest/for_impatient.html)

[[Hack StepicOrg/stepic-plugins on Nitrous.IO]](https://www.nitrous.io/hack_button?source=embed&runtime=django&repo=StepicOrg%2Fstepic-plugins&file_to_open=stepic_plugins%2Fquizzes%2Fsimple_choice%2F__init__.py)
