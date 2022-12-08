import pytest

from auth.app import create_app
from auth.common.app_common import db
from fixtures_collection.user import create_user, login_user
from fixtures_collection.headers import(
    headers_with_admin_access, headers_with_user_access
)
from . import config

pytest_plugins = [
    "fixtures_collection.user",
    "fixtures_collection.headers",
]

@pytest.fixture
def app():
    return create_app(config=config)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def session():
    yield db.session
    db.session.remove()
    db.drop_all()
