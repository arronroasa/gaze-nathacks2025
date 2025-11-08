#!/usr/bin/env bash

if [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "cygwin"* ]] || [[ "$OSTYPE" == "win32"* ]]; then
    python -m venv ./venv
    source ./venv/Scripts/activate
    pip install -r requirements.txt
else
    python3 -m venv ./venv
    source ./venv/bin/activate
    pip install -r requirements.txt
fi

