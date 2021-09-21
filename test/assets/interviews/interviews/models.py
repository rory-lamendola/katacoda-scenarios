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


class Member(Base):
    """Member table."""

    __tablename__ = "member"

    member_uuid = sqlalchemy.Column(postgresql.UUID, nullable=False)
    first_name = sqlalchemy.Column(sqlalchemy.String(64), nullable=True)
    last_name = sqlalchemy.Column(sqlalchemy.String(64), nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String(64), nullable=True)

    @classmethod
    def get_member(
        cls: Type[ModelType], member_uuid: str,
    ) -> ModelType:
        """Convenience method to get one alias record."""
        return cls.query.filter(cls.member_uuid == member_uuid)

    @classmethod
    def put_member(
        cls: Type[ModelType], row: Type[ModelType]
    ) -> Type[ModelType]:
        """Record an attempt against a policy for a subject."""
        cls.query.session.add(row)
        cls.query.session.commit()
        return row


