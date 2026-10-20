#!/bin/bash
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then python3 setup_and_run.py
else echo "Python 3 is not installed (sudo apt install python3 python3-venv)"; fi
