#!/bin/bash

#create virtual env for python 3
virtualenv stepic-server -p python3.3
# activate created virtual env 
source stepic-server/bin/activate
# installing dependecies for stepic quiz server
cd workspace/stepic-plugins/
pip install -r requirements.txt
# start server side for "simple-choice" quiz
cd stepic_plugins/
python server.py simple-choice