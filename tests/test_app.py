import pytest
from app.main import app, orders


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        orders.clear()
        yield test_client
        orders.clear()


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"FoodieHub" in response.data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_get_menu(client):
    response = client.get("/api/menu")
    assert response.status_code == 200
    assert len(response.json) > 0


def test_filter_menu(client):
    response = client.get("/api/menu?category=Pizza")
    assert response.status_code == 200
    assert all(item["category"] == "Pizza" for item in response.json)


def test_create_order(client):
    response = client.post(
        "/api/orders",
        json={"items": [1]}
    )
    assert response.status_code == 201
    assert response.json["items"] == [1]
    assert response.json["status"] == "pending"


def test_create_order_without_items(client):
    response = client.post("/api/orders", json={})
    assert response.status_code == 400


def test_get_orders(client):
    client.post("/api/orders", json={"items": [1]})
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert len(response.json) == 1


def test_get_nonexistent_order(client):
    response = client.get("/api/orders/9999")
    assert response.status_code == 404


def test_update_order_status(client):
    created = client.post("/api/orders", json={"items": [1]})
    order_id = created.json["id"]

    response = client.patch(
        f"/api/orders/{order_id}/status",
        json={"status": "confirmed"}
    )

    assert response.status_code == 200
    assert response.json["status"] == "confirmed"


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"food_ordering_orders_total" in response.data
