#!/usr/bin/env bash

# install makeapp from sources for local development
# venv python is in ~/.local/share/uv/tools/makeapp/bin/python
cd ../
uv tool install -e .
