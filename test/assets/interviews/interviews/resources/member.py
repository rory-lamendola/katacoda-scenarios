"""Password policy validation endpoints."""

import abc
import enum
import http
import json
import logging
import random
import re
import uuid
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Pattern
from typing import Union

import flask
import flask_restful

from interviews import models

LOG = logging.getLogger(__name__)


class MemberResource(flask_restful.Resource):
    """Top-level password policy endpoint."""

    def get(self) -> flask.Response:  # pylint: disable=no-self-use
        """Get a dict of password policy checks that will be performed
        Return data structure:
        ```json
        {
          "policies": {
            "policy_name": "policy_description"
            ...
          }
        }
        ```
        Example:
        ```bash
        % curl http://localhost:8080/api/password-policy
        ```
        """

        parser = flask_restful.reqparse.RequestParser()
        parser.add_argument("member_uuid", required=True)
        args = parser.parse_args()

        member = models.Member.get_member(member_uuid=args["member_uuid"])

        return member

    def post(self) -> flask.Response:  # pylint: disable=no-self-use
        """Authenticate with an access token to validate a password.
        The `POST` data must include a single field, `password`, that
        contains the new password to set.  An optional `quick` field [
        Options: 0, 1] may also be included, which allows only
        fast password checks to be run when set to 1.
        Return data structure:
        ```json
        {
          "checks": {
            check_name: {
                'passed': bool,
                'feedback': str
            },
            ...
          },
          "passed": bool
          "tier": str
        }
        ```

        Where tier is one of the ScoreTier types: `weak`, `moderate`,
        `strong`, `very_strong`.

        Example:
        ```bash
        % TOKEN=eyJhbG...ennw4
        % curl -X POST -H Content-Type:application/json \\
               -H "Authorization: Bearer $TOKEN" \\
               -d '{"password":"hunter2"}'
               http://localhost:8080/api/password-policy
        ```
        """
    
        parser = flask_restful.reqparse.RequestParser()
        parser.add_argument("first_name", required=True)
        parser.add_argument("last_name", required=True)
        parser.add_argument("address", required=False)
        args = parser.parse_args()

        models.Member.put_member(models.Member(member_uuid=uuid.uuid4(), first_name=args["first_name"], last_name=args["last_name"], address=args["address"]))

        return {}
