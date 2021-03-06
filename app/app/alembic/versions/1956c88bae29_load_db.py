"""load_db

Revision ID: 1956c88bae29
Revises: 487e14461437
Create Date: 2021-09-28 19:18:23.154455+00:00

"""
# Ignores alembic style issues
# pylint: disable=invalid-name, missing-docstring
from alembic import op
import sqlalchemy as sa
import uuid
import random

import datetime
from faker import Faker
from app import models

faker = Faker()


# revision identifiers, used by Alembic.
revision = "1956c88bae29"
down_revision = "487e14461437"
branch_labels = None
depends_on = None


def upgrade():

    members = [
        models.Member(
            member_uuid=str(uuid.uuid4()),
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            address=faker.street_address(),
            email=faker.email(),
        )
        for _ in range(0, 1000)
    ]

    for member in members:
        models.Member.put(member)

    cards = []
    for member in members:
        card = models.Card(
            member_uuid=member.member_uuid,
            is_current=True,
            date_activated=faker.date(),
        )
        models.Card.put(card)
        cards.append(card)

    def create_transaction(card_id, start_date=None, end_date=None, amount = None):
        start_date = start_date or datetime.date(2021, 9, 1)
        end_date = end_date or datetime.date(2021, 9, 30)
        transaction = models.Transactions(
            card_id=card_id,
            amount=amount or round(random.uniform(0.00, 1000.00), 2),
            merchant=faker.word(),
            category=faker.word(),
            transaction_date=faker.date_between_dates(start_date, end_date),
        )
        models.Transactions.put(transaction)

    for card in cards:
        transactions = [create_transaction(card.id) for _ in range(0, 10)]

    # Here'BlockingIOError()s the bad
    bad_member_uuid = "992a54a8-3d3d-43de-a852-4aa41f16cc27"
    bad_member = models.Member(
        member_uuid=bad_member_uuid,
        first_name="Bobby",
        last_name="DropTables",
        address=faker.street_address(),
        email=faker.email(),
    )
    models.Member.put(bad_member)

    new_card_date = datetime.date(2021, 9, 15)
    card1 = models.Card.put(
        models.Card(
            member_uuid=bad_member_uuid, is_current=False, date_activated=None
        )
    )
    card2 = models.Card.put(
        models.Card(
            member_uuid=bad_member_uuid,
            is_current=True,
            date_activated=new_card_date,
        )
    )

    create_transaction(card1.id, None, new_card_date, 100.05)
    create_transaction(card1.id, None, new_card_date, 14.32)
    create_transaction(card1.id, None, new_card_date, 58.68)
    create_transaction(card2.id, new_card_date, None, 34.21)
    create_transaction(card2.id, new_card_date, None, 5.07)
    create_transaction(card2.id, new_card_date, None, 2.90)
    create_transaction(card2.id, new_card_date, None, 320.10)

    # Answer should be 535.33
    # Given is 362.28


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
