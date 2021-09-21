#!/bin/sh
#
# run the application in docker

set -eux

. venv/bin/activate
export PYTHONPATH=.

(
    cd "interviews"
    
    alembic upgrade head
)

exec python interviews/main.py
