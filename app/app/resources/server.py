"""An importable server for interviews."""

import logging
from typing import Any

import flask
import flask_restful
from healthcheck import HealthCheck

from app import postgres
from app.resources import member
from app.resources import payments

LOG = logging.getLogger(__name__)


health = HealthCheck()


class InterviewsServer(postgres.PostgresMixin):
    """Instantiates Flask application which when run acts as a server."""

    def __init__(self, app: flask.Flask) -> None:
        # pylint: disable=unused-argument
        """Flask server."""
        self.app = app

        self._api = flask_restful.Api(app=self.app)

        self.db_connect()
        self.add_resources()

    def add_resources(self, *args: Any, **kwargs: Any) -> None:
        """Mount resources to the server."""
        self.api.add_resource(member.MemberResource, "/api/member")
        self.api.add_resource(payments.PaymentsResource, "/api/payments")

    def run(self) -> None:
        """Run the server with thread support."""
        host = "localhost"
        port = 5000

        LOG.info(f"Running server on: {host}:{port}")
        self.app.run(host=host, port=port, threaded=True)

    @property
    def api(self) -> flask_restful.Api:
        """Property reference to underlying flask_restful.Api."""
        return self._api
