"""Member endpoints."""

import logging
import uuid

import flask
import flask_restful
from flask_restful import reqparse

from app import models

LOG = logging.getLogger(__name__)


class MemberResource(flask_restful.Resource):
    """Top-level password policy endpoint."""

    def get(self) -> flask.Response:  # pylint: disable=no-self-use
        """Get a dict of the member when given their uuid
        Return data structure:
        ```json
        {
          "id": ...
          "created_at": ...
          "first_name": ...
          "last_name": ...
          "address": ...
          "email": ...
        }
        ```
        Example:
        ```bash
        % curl -X GET -H Content-Type:application/json -d '{"member_uuid":"992a54a8-3d3d-43de-a852-4aa41f16cc27"}' http://localhost:8080/api/member
        ```
        """

        parser = flask_restful.reqparse.RequestParser()
        parser.add_argument("member_uuid", required=True)
        args = parser.parse_args()

        member = models.Member.get_member(
            member_uuid=args["member_uuid"]
        ).first()

        return member

    def post(self) -> flask.Response:  # pylint: disable=no-self-use
        """Create a member in the database.

        Returns the member uuid

        Example:
        ```bash
        % curl -X POST -H Content-Type:application/json \\
               -d '{"first_name":"Rory", "last_name": "LaMendola", "address": "123 Main Street"}' \\
               http://localhost:8080/api/password-policy
        ```
        """

        parser = reqparse.RequestParser()
        parser.add_argument("first_name", required=True)
        parser.add_argument("last_name", required=True)
        parser.add_argument("address", required=False)
        args = parser.parse_args()

        member_uuid = str(uuid.uuid4())
        models.Member.put(
            models.Member(
                member_uuid=member_uuid,
                first_name=args["first_name"],
                last_name=args["last_name"],
                address=args["address"],
            )
        )
        return member_uuid
