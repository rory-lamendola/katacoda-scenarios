"""Global fixtures and other test config."""

import logging

import flask
import pytest
from petal.utils import faker
import sqlalchemy
from petal.utils.postgres import connection
from petal.utils.postgres import models


from app.resources import server
from app import settings

# pylint: disable=redefined-outer-name


@pytest.fixture
def debug(caplog):
    """Set log capture level to DEBUG."""
    caplog.set_level(logging.DEBUG)
    caplog.set_level(logging.WARNING, logger="faker")
    caplog.set_level(logging.CRITICAL, logger="ddtrace")
    caplog.set_level(logging.CRITICAL, logger="datadog")
    caplog.set_level(logging.INFO, logger="petal.config")
    caplog.set_level(logging.INFO, logger="petal.svc_authnz")
    caplog.set_level(logging.WARNING, logger="botocore")
    yield caplog


@pytest.fixture
def fake():
    """Get a Faker object."""
    yield faker.Faker()


@pytest.fixture
def database(postgresql_proc):
    """Create a fake database connection."""
    force_config = {
        "postgres/schema": "postgresql+psycopg2",
        "postgres/username": postgresql_proc.user,
        "postgres/password": "Interviews",
        "postgres/host": postgresql_proc.host,
        "postgres/port": postgresql_proc.port,
        "postgres/db_name": postgresql_proc.user,
    }

    with settings.config.patch(**force_config):
        conn = connection.DatabaseConnection(
            settings.config.get_child("postgres")
        )
        models.Base.metadata.create_all(bind=conn.engine)

        yield

        conn.shutdown()
        sqlalchemy.orm.close_all_sessions()
        models.Base.metadata.drop_all(bind=conn.engine)
        conn.engine.dispose()


@pytest.fixture
def client(database, fake):  # pylint: disable=unused-argument
    """Get a fake Flask client."""
    force_config = {"flask/debug": True, "flask/secret_key": fake.word()}
    with settings.config.patch(**force_config):
        app = flask.Flask(__name__)
        logging.getLogger().handlers = []

        api = server.InterviewsServer(app=app, TESTING=True)

        yield api.app.test_client()
