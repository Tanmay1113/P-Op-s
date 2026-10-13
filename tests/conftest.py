import pytest
from app import create_app
from app.extensions import db
from app.models import User

@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-not-for-production",
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "WTF_CSRF_ENABLED": False,
        "RATELIMIT_ENABLED": False,
        "SESSION_COOKIE_SECURE": False,
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def make_user(app):
    def _make(username, role="Employee", password="a-strong-test-password", active=True):
        with app.app_context():
            user = User(username=username, email=f"{username}@example.test", role=role, is_active_account=active)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user.user_id
    return _make
