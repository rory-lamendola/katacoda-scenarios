"""Database models."""

import sqlalchemy
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func

import logging
from typing import Any
from typing import Type
from typing import TypeVar

import dictalchemy
import sqlalchemy
from sqlalchemy.ext import declarative
from sqlalchemy.sql import func

LOG = logging.getLogger(__name__)


# pylint: disable=invalid-name
ModelType = TypeVar("ModelType", bound="Base")
DeclarativeBase = declarative.declarative_base(cls=dictalchemy.DictableModel)

# pylint: enable=invalid-name


class Base(DeclarativeBase):  # type:ignore
    """Base model others should inherit from."""

    __abstract__ = True

    # Annotates query property
    query: sqlalchemy.orm.query.Query = None

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime, server_default=func.now(), nullable=True
    )

    @classmethod
    def get_by(cls: Type[ModelType], **kwargs: Any) -> ModelType:
        """Convenience method to get a single non-deleted object."""
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def put(cls: Type[ModelType], row: Type[ModelType]) -> Type[ModelType]:
        """Convenience method to put an object in the database."""
        cls.query.session.add(row)
        cls.query.session.commit()
        return row

    @classmethod
    def as_dict(self) -> dict:
        return {
            c.name: str(getattr(self, c.name)) for c in self.__table__.columns
        }


class Member(Base):
    """Member table."""

    __tablename__ = "member"

    member_uuid = sqlalchemy.Column(
        postgresql.UUID, nullable=False, unique=True
    )
    first_name = sqlalchemy.Column(sqlalchemy.String(64), nullable=True)
    last_name = sqlalchemy.Column(sqlalchemy.String(64), nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String(64), nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String(64), nullable=True)

    @classmethod
    def get_member(
        cls: Type[ModelType],
        member_uuid: str,
    ) -> ModelType:
        """Convenience method to get one member record."""
        LOG.info(f"Getting member: {member_uuid}")
        return cls.query.filter(cls.member_uuid == member_uuid)


class Card(Base):
    """Card table."""

    __tablename__ = "card"

    member_uuid = sqlalchemy.Column(
        postgresql.UUID,
        sqlalchemy.ForeignKey("member.member_uuid"),
        nullable=False,
    )

    date_activated = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    is_current = sqlalchemy.Column(
        sqlalchemy.Boolean(), default=True, nullable=False
    )

    @classmethod
    def get_card_by_member(
        cls: Type[ModelType],
        member_uuid: str,
    ) -> ModelType:
        """Convenience method to get one alias record."""
        LOG.info(f"Getting member: {member_uuid}")
        return cls.query.filter(cls.member_uuid == member_uuid).filter(
            cls.is_current == True
        )


class Transactions(Base):
    """Transactions table."""

    __tablename__ = "transactions"

    card_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("card.id"), nullable=False
    )

    amount = sqlalchemy.Column(
        sqlalchemy.Numeric(precision=14, scale=2), nullable=False
    )
    merchant = sqlalchemy.Column(sqlalchemy.String(255), nullable=True)
    category = sqlalchemy.Column(sqlalchemy.String(255), nullable=True)
    transaction_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    @classmethod
    def get_transactions_by_card(
        cls: Type[ModelType],
        card_id: str,
    ) -> ModelType:
        """Convenience method to get the transasctions for a particular card."""
        return cls.query.filter(cls.card_id == card_id)
