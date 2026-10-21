import pytest
from sqlalchemy.exc import OperationalError
from app.main import app
from app.db import get_db


def test_health_and_root(client):
    assert client.get("/health").json() == {"status": "UP"}
    assert client.get("/").json()["service"] == "TaskBoard API"
    assert client.get("/ready").status_code == 200


def test_crud(client):
    payload = {"title": "Deploy synthetic release", "description": "Demo", "assignee": "Demo Student", "priority": "HIGH"}
    r = client.post("/api/tasks", json=payload)
    assert r.status_code == 201
    task = r.json()
    assert task["created_at"] and task["status"] == "TODO"
    url = f"/api/tasks/{task['id']}"
    assert client.get(url).json()["title"] == payload["title"]
    assert len(client.get("/api/tasks").json()) == 1
    r = client.put(url, json={"title": "Release verified", "status": "DONE", "priority": "LOW"})
    assert r.status_code == 200 and r.json()["status"] == "DONE"
    assert r.json()["assignee"] == "Demo Student"
    assert client.delete(url).status_code == 204
    assert client.get(url).status_code == 404


def test_statistics_route_and_counts(client):
    assert client.get("/api/tasks/stats").json() == {"total": 0, "todo": 0, "inProgress": 0, "done": 0}
    for status in ["TODO", "IN_PROGRESS", "DONE", "DONE"]:
        assert client.post("/api/tasks", json={"title": status, "status": status}).status_code == 201
    assert client.get("/api/tasks/stats").json() == {"total": 4, "todo": 1, "inProgress": 1, "done": 2}


@pytest.mark.parametrize("payload", [{"title": ""}, {"title": "   "}, {"title": "x"*201}, {"title": "x", "priority": "URGENT"}, {"title": "x", "status": "broken"}, {"title": "x", "assignee": "x"*121}, {"title": "x", "unknown": 1}])
def test_create_validation(client, payload):
    assert client.post("/api/tasks", json=payload).status_code == 422
    assert client.get("/api/tasks").json() == []


@pytest.mark.parametrize("payload", [{"title": None}, {"status": None}, {"title": " "}, {"priority": "BAD"}])
def test_update_validation(client, payload):
    task = client.post("/api/tasks", json={"title": "Valid"}).json()
    assert client.put(f"/api/tasks/{task['id']}", json=payload).status_code == 422
    assert client.get(f"/api/tasks/{task['id']}").json()["title"] == "Valid"


@pytest.mark.parametrize("method,payload", [("get", None), ("put", {"title": "Absent"}), ("delete", None)])
def test_not_found(client, method, payload):
    r = client.request(method, "/api/tasks/999999", **({"json": payload} if payload else {}))
    assert r.status_code == 404 and r.json() == {"detail": "Task not found"}


def test_database_failure_is_safe_and_recovers(client):
    previous = app.dependency_overrides[get_db]
    class Broken:
        def execute(self, *args):
            raise OperationalError("secret connection detail", {}, Exception("secret password"))
    app.dependency_overrides[get_db] = lambda: Broken()
    r = client.get("/ready")
    assert r.status_code == 503 and r.json() == {"detail": "Database temporarily unavailable"}
    assert "secret" not in r.text
    assert client.get("/health").status_code == 200
    app.dependency_overrides[get_db] = previous
    assert client.get("/ready").status_code == 200


def test_metrics_and_docs(client):
    client.get("/health")
    r = client.get("/metrics")
    assert r.status_code == 200 and "http_requests_total" in r.text
    assert client.get("/docs").status_code == 200
