"""Main runner for interviews."""

import logging

import flask

from app.resources import server


LOG = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

app = flask.Flask(__name__)  # pylint: disable=invalid-name

api = server.InterviewsServer(app=app)  # pylint: disable=invalid-name


if __name__ == "__main__":
    api.run()
