#!/bin/bash
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then python3 setup_and_run.py
else echo "Python 3 is not installed. Install it from https://www.python.org/downloads/"; open https://www.python.org/downloads/; fi
read -p "Press Enter to close..."
