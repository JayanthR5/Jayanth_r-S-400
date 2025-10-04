import pytest
from backend.app import app, db, User

@pytest.fixture
def client(tmp_path, monkeypatch):
    # Use temp DB for tests
    test_db = tmp_path / "test_events.db"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{test_db}"
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register_and_login(client):
    # register
    rv = client.post("/api/register", json={"username": "alice", "password": "pass"})
    assert rv.status_code == 201

    # duplicate register fails
    rv2 = client.post("/api/register", json={"username": "alice", "password": "pass"})
    assert rv2.status_code == 400

    # login
    rv3 = client.post("/api/login", json={"username": "alice", "password": "pass"})
    assert rv3.status_code == 200
    assert rv3.json.get("username") == "alice"

    # wrong password
    rv4 = client.post("/api/login", json={"username": "alice", "password": "wrong"})
    assert rv4.status_code == 401
