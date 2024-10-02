#!/bin/bash

if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

cd anna/extensions

if [ ! -d "takina" ]; then
    git clone https://github.com/orxngc/takina
fi

cd ../..
python3 anna
