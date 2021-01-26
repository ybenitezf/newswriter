import pytest
from photostore import create_app, db

@pytest.fixture
def app():
    app = create_app('config.TestConfig')

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):

    with app.test_client() as client:
        yield client
