""" Base Resource and Authenticated Resource definitions. """

from typing import Any

import flask
import flask_restful


class BasePetalResource(flask_restful.Resource):
    """Petal API Resource base class."""

    def dispatch_request(self, *args: Any, **kwargs: Any) -> Any:
        flask.g.resource = self.__class__.__name__
        return super().dispatch_request(*args, **kwargs)
