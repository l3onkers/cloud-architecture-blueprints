"""Unit tests for Online Boutique Checkout Service."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "checkoutservice"
    assert "traceparent" in response.headers


def test_checkout_order_confirmation():
    payload = {
        "userId": "user-boutique-01",
        "userCurrency": "EUR",
        "email": "customer@example.com",
        "address": {
            "streetAddress": "1600 Amphitheatre Pkwy",
            "city": "Mountain View",
            "state": "CA",
            "country": "United States",
            "zipCode": "94043",
        },
        "items": [
            {"productId": "1YMWWN1N4O", "quantity": 1},
            {"productId": "OLJCESPC7Z", "quantity": 2},
        ],
    }
    response = client.post("/checkout", json=payload)
    assert response.status_code == 200
    order = response.json()
    assert order["orderId"].startswith("ORD-")
    assert order["shippingTrackingId"].startswith("TRK-")
    assert order["userCurrency"] == "EUR"
    assert order["itemsCount"] == 3
    assert order["totalPaidConverted"] > 0


def test_checkout_empty_cart_rejected():
    payload = {
        "userId": "user-boutique-01",
        "userCurrency": "USD",
        "email": "customer@example.com",
        "address": {
            "streetAddress": "1600 Amphitheatre Pkwy",
            "city": "Mountain View",
            "state": "CA",
            "country": "United States",
            "zipCode": "94043",
        },
        "items": [],
    }
    response = client.post("/checkout", json=payload)
    assert response.status_code == 400
