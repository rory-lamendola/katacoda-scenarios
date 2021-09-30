"""Payments endpoints."""

import datetime
import json
import logging

import flask
import flask_restful
from flask_restful import reqparse
from flask_restful import inputs
from sqlalchemy.sql import func

from app import models

LOG = logging.getLogger(__name__)


class PaymentsResource(flask_restful.Resource):
    """Top-level password policy endpoint."""

    def get(self) -> flask.Response:  # pylint: disable=no-self-use
        """Get the payment amount for a customer.
        
        The payment amount will be that month's payment until (and including) 
        the given date.

        Example:
        ```bash
        % curl -d {"member_uuid": "992a54a8-3d3d-43de-a852-4aa41f16cc27", "date": "2021-09-28"} http://localhost:8080/api/payments
        ```
        """

        parser = flask_restful.reqparse.RequestParser()
        parser.add_argument("member_uuid", required=True)
        parser.add_argument(
            "date", required=True, type=flask_restful.inputs.date
        )
        args = parser.parse_args()
        member_uuid = args["member_uuid"]
        date = args["date"]

        month_start = datetime.date(date.year, date.month, 1)
        month_end = date

        card = models.Card.get_card_by_member(member_uuid).first()
        if card:
            total_amount = (
                models.Transactions.get_transactions_by_card(card.id)
                .filter(
                    models.Transactions.transaction_date.between(
                        month_start, month_end
                    )
                )
                .with_entities(
                    func.sum(models.Transactions.amount).label("sum")
                )
                .scalar()
            )
            return json.dumps(float(total_amount))

        return {}
