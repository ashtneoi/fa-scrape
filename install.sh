#!/usr/bin/env bash

set -o errexit
shopt -s nullglob

if ! [[ -d .env ]]; then
    virtualenv .env -p $(which python3)
fi

source .env/bin/activate

pip3 install beautifulsoup4==4.6.3
