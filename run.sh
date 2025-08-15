#!/bin/bash

if [ ! -d "venv" ] 
then
    python -m venv venv
	source venv/bin/activate
    pip install --upgrade pip
    pip install networkx numpy scikit_learn Shapely
else
	source venv/bin/activate
fi

python generate_all.py
