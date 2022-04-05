#!/bin/bash
#
# Standalone GUI.py 3 app starter
#
which flask
[ $? != 0 ] &&\
  . venv/bin/activate
export FLASK_APP=wtime_srv.py
export FLASK_DEBUG=1
flask run --host=0.0.0.0 --port=8889
