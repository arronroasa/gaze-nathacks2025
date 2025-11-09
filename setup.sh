#!/usr/bin/env bash

if [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "cygwin"* ]] || [[ "$OSTYPE" == "win32"* ]]; then
    python -m venv ./venv
else
    python3 -m venv ./venv
fi

source ./venv/Scripts/activate
pip install -r requirements.txt