"""An importable server for interviews."""

import logging
from typing import Any

import flask
import flask_restful
import healthcheck

from interviews import postgres
from interviews.resources import member

LOG = logging.getLogger(__name__)


class InterviewsServer(postgres.PostgresMixin):
    """Instantiates Flask application which when run acts as a server."""

    def __init__(self, app: flask.Flask) -> None:
        # pylint: disable=unused-argument
        """Flask server."""
        self.app = app

        self._api = flask_restful.Api(app=self.app)

        self.db_connect(health=healthcheck.HealthCheck(success_ttl=None, failure_ttl=None))

    def add_resources(self, *args: Any, **kwargs: Any) -> None:
        """Mount resources to the server."""
        self.api.add_resource(member.MemberResource, "/api/member")

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

