"""Unit tests for Online Boutique Product Catalog Service."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "productcatalogservice"
    assert "traceparent" in response.headers


def test_list_products():
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert isinstance(products, list)
    assert len(products) >= 5
    names = {item["name"] for item in products}
    assert "Sunglasses" in names
    assert "Watch" in names


def test_get_product_by_id():
    response = client.get("/products/1YMWWN1N4O")
    assert response.status_code == 200
    product = response.json()
    assert product["id"] == "1YMWWN1N4O"
    assert product["name"] == "Watch"
    assert product["priceUsd"]["currencyCode"] == "USD"


def test_search_products():
    response = client.get("/products/search?q=leather")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert any("leather" in item["description"].lower() for item in results)
