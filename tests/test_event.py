import pytest
from backend.app import app, db

@pytest.fixture
def client(tmp_path):
    test_db = tmp_path / "test_events2.db"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{test_db}"
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_public_get_events(client):
    rv = client.get("/api/events")
    assert rv.status_code == 200
    assert isinstance(rv.json, list)

def test_create_event_requires_auth(client):
    # create without login -> 401
    rv = client.post("/api/events", json={"title": "x"})
    assert rv.status_code == 401
