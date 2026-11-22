import os

# Test dung SQLite trong bo nho, khong can PostgreSQL
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import app as product_app  # noqa: E402


class FakeResponse:
    status_code = 200

    def json(self):
        return {"id": 1, "name": "Nguyen Van A"}


def test_health():
    client = product_app.app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "UP"


def test_list_products_calls_user_service(monkeypatch):
    monkeypatch.setattr(product_app.requests, "get", lambda *a, **k: FakeResponse())
    client = product_app.app.test_client()
    resp = client.get("/products")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) >= 3
    assert data[0]["owner_name"] == "Nguyen Van A"


def test_user_service_down_returns_none(monkeypatch):
    def boom(*a, **k):
        raise product_app.requests.ConnectionError("down")

    monkeypatch.setattr(product_app.requests, "get", boom)
    client = product_app.app.test_client()
    resp = client.get("/products/1")
    assert resp.status_code == 200
    assert resp.get_json()["owner_name"] is None


def test_product_not_found():
    client = product_app.app.test_client()
    assert client.get("/products/999").status_code == 404


def test_create_product(monkeypatch):
    monkeypatch.setattr(product_app.requests, "get", lambda *a, **k: FakeResponse())
    client = product_app.app.test_client()
    resp = client.post("/products", json={"name": "Man hinh", "price": 150, "owner_id": 1})
    assert resp.status_code == 201
    assert resp.get_json()["name"] == "Man hinh"


def test_create_product_missing_field():
    client = product_app.app.test_client()
    resp = client.post("/products", json={"name": "Thieu gia"})
    assert resp.status_code == 400
