#!/bin/sh
#
# run the application in docker

set -eux

. venv/bin/activate
pip install -e .
export PYTHONPATH=.

(
    cd "app"
    
    alembic upgrade head
)

exec uwsgi --ini uwsgi.ini
