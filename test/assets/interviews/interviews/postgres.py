"""Postgres connection utilities."""

import copy
import logging
import os
from typing import Any
from typing import Dict
from typing import Tuple
from typing import Type
from typing import TypeVar

import pals
import dictalchemy
import healthcheck
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.ext import declarative
from sqlalchemy.sql import func

from interviews import models

LOG = logging.getLogger(__name__)


class DatabaseConnection:
    """Make a SQLAlchemy connection from `petal.config`.

    Most usage will be fairly simple:

    ```python
    conn = connection.DatabaseConnection(settings.config.get_child('postgres'))
    ```

    This class automatically injects itself into the base models as the
    `query` property. You can also access the `session` and `engine`
    properties directly, if necessary.

    When making a connection, this class attempts to initialize the
    database. This involves attempting to connect with the master
    username and password; if that succeeds, then it will create the
    user named in `username`, grant access to all tables in the public
    schema, and either enable AWS IAM auth for it or set the
    password. Then as a final step the master password will be reset and
    the new master password discarded; if you need master access in the
    future, then you will have to reset the master password (e.g.,
    through the AWS console.)

    The `DatabaseConnection` class does *not* support dynamically
    re-configuring the connection; it makes one connection at startup
    and caches the connection details permanently.

    The constructor understands the following arguments:

    * `config`: The `petal.config.ConfigInterface` instance from which
      connection configuration is drawn.
    * `use_master_creds`: Instead of using `username` and `password`
      (or IAM auth) to authenticate to the database, use the
      credentials in `master_username` and
      `initial_master_password`. This is only intended to be used
      during a migration to IAM auth; it lets you use the master
      credentials while configurating IAM auth.
    * `delay_connect`: If True, do not immediately connect to the
      database; wait for a connection to be required. This delays
      potential connection errors until later in startup, but may be
      useful in certain edge cases like database initialization, where
      the database isn't ready for connection immediately.
    * `engine_args`: Arbitrary keyword arguments passed to
      [`sqlalchemy.create_engine`](https://docs.sqlalchemy.org/en/14/core/engines.html#sqlalchemy.create_engine). By
      default, this sets `max_overflow=-1`.
    """

    def __init__(
        self,
        delay_connect: bool = False,
        engine_args: Dict[str, Any] = None,
    ) -> None:
        # config: schema: The schema to use to connect to the PostgreSQL
        # database.
        self.schema = "postgresql+psycopg2"
        # config: host: The Postgres hostname.
        self.hostname = os.environ["POSTGRES_HOST"]
        # config: port: The port Postgres listens on.
        self.port = os.environ["POSTGRES_PORT"]
        # config: username: The username to use to connect to
        # Postgres.
        self.username = os.environ["POSTGRES_USER"]
        # config: db_name: The PostgreSQL database name.
        self.db_name = os.environ["POSTGRES_DB"]
   
        LOG.debug(f"Using database password from config")
        # config: password: The password to use to connect to
        # Postgres. Only used if `use_iam_auth` is False (the default), in
        # which case it is required.
        self.password = os.environ["POSTGRES_PASSWORD"]

        # config: sslmode: The SSL mode to use. Default is `prefer` if
        # `use_iam_auth` is False (the default), `require` otherwise.
        self.connect_args: Dict[str, str] = {
            "sslmode": "prefer"
        }
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

    ```python
    from petal.service import server
    from petal.utils.postgres import flask as pg_flask

    from myapp import settings

    class MyAppServer(server.PetalService, pg_flask.PostgresMixin):
        def __init__(self, app: flask.Flask,
                     *args: Any, **kwargs: Any) -> None:
            ...
            self.db_connect(
                settings.config.get_child('postgres'), health=server.health)
    ```

    This will initialize the database (if necessary), connect to it, set
    up Datadog APM for SQLAlchemy, health checking, and more.
    """

    def db_connect(
        self,
        health: healthcheck.HealthCheck = None,
    ) -> None:
        """Initialize a database connection."""
        self.conn = DatabaseConnection()  # type: ignore
        self.app.teardown_appcontext(  # type: ignore
            lambda _: self.conn.shutdown()
        )

        if health:

            def postgres() -> Tuple[bool, Dict[str, Any]]:
                """Postgres health check."""
                data = {
                    "uri": self.conn.safe_uri,
                }

                try:
                    self.conn.session.execute(
                        "SET SESSION STATEMENT_TIMEOUT TO 1; SELECT 1"
                    ).first()
                except Exception as err:  # pylint: disable=broad-except
                    data["ok"] = False
                    data["error"] = f"{type(err)}: {err}"
                else:
                    data["ok"] = True
                return data["ok"], data

            health.add_check(postgres)