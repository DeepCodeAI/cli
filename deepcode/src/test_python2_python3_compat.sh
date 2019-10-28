#!/usr/bin/env bash

# deactivate in case we are in a virtualenv
deactivate &> /dev/null
rm -rf tmp_venv

# exit on error
set -e

# run tests with python 2
# virtualenv tmp_venv -p python2
# source tmp_venv/bin/activate
# echo "-----------------------------"
# echo "Running with Python version: "
# python --version 
# echo "-----------------------------"
# pip install -r requirements.txt
# echo "Pip install done, running tests"
# python -m unittest discover tests
# deactivate
# rm -rf tmp_venv

# run tests with python 3
virtualenv tmp_venv -p python3
source tmp_venv/bin/activate
echo "-----------------------------"
echo "Running with Python version: "
python --version
echo "-----------------------------"
pip install -r requirements.txt
echo "Pip install done, running tests"
python -m unittest discover tests
deactivate
rm -rf tmp_venv
