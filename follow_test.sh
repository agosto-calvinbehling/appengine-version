#!/bin/bash

set -euo pipefail
set -x

./test.py || true
reflex -r '\.py$' "./test.py" --only-files
