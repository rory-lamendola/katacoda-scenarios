"""Postgres connection utilities."""

import copy
import logging
import os
from typing import Any
from typing import Dict

import pals
import sqlalchemy
from sqlalchemy import orm

from app import models

LOG = logging.getLogger(__name__)


class DatabaseConnection:
    """Make a SQLAlchemy connection."""

    def __init__(
        self,
        delay_connect: bool = False,
        engine_args: Dict[str, Any] = None,
    ) -> None:

        self.schema = "postgresql+psycopg2"
        self.hostname = os.environ["POSTGRES_HOST"]
        self.port = os.environ["POSTGRES_PORT"]
        self.username = os.environ["POSTGRES_USER"]
        self.db_name = os.environ["POSTGRES_DB"]
        self.password = os.environ["POSTGRES_PASSWORD"]

        self.connect_args: Dict[str, str] = {"sslmode": "prefer"}
        self.engine_args: Dict[str, Any] = engine_args or {}
        self.engine_args.setdefault("max_overflow", -1)

        self.engine: sqlalchemy.engine.Engine = None
        self.session: orm.scoping.ScopedSession = None

        self._locker: pals.core.Locker = None

        if not delay_connect:
            self.connect()

    def connect(self, engine_args: Dict[str, Any] = None) -> None:
        """Initialize a database connection."""
        if engine_args:
            final_engine_args = copy.deepcopy(self.engine_args)
            final_engine_args.update(engine_args)
        else:
            final_engine_args = {}

        if self.engine is None or self.session is None:
            LOG.info(f"Connecting to database at {self.safe_uri}")

            self.engine = sqlalchemy.create_engine(
                self.uri,
                connect_args=self.connect_args,
                **final_engine_args,
            )

            LOG.info(f"Successfully connected to database at {self.safe_uri}")
            self.session = orm.scoped_session(
                orm.sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self.engine,
                    expire_on_commit=False,
                )
            )
            models.Base.query = self.session.query_property()

            self._locker = pals.Locker(
                self.db_name, create_engine_callable=lambda: self.engine
            )

    @property
    def uri(self) -> str:
        """Get a fully-formed URI from the details of this connection."""
        return (
            f"{self.schema}://{self.username}:{self.password}@"
            f"{self.hostname}:{self.port}/{self.db_name}"
        )

    @property
    def safe_uri(self) -> str:
        """Get a URI with password scrubbed."""
        return (
            f"{self.schema}://{self.username}:***@"
            f"{self.hostname}:{self.port}/{self.db_name}"
        )

    def shutdown(self) -> None:
        """Cleanly shutdown the database session."""
        self.session.remove()


class PostgresMixin:
    """Postgres utility mixin for `petal.server.PetalService`.

    Call `db_connect()` in your `__init__`:

    This will initialize the database (if necessary), connect to it.
    """

    def db_connect(
        self,
    ) -> None:
        """Initialize a database connection."""
        self.conn = DatabaseConnection()  # type: ignore
        self.app.teardown_appcontext(  # type: ignore
            lambda _: self.conn.shutdown()
        )
