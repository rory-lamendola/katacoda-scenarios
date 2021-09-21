"""Main runner for interviews."""

import logging

import flask

from interviews.resources import server


LOG = logging.getLogger(__name__)

app = flask.Flask(__name__)  # pylint: disable=invalid-name

api = server.InterviewsServer(app=app)  # pylint: disable=invalid-name


if __name__ == '__main__':
    api.run()