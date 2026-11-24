#!/usr/bin/env python3
"""
Live End-to-End Integration Test for Online Boutique Platform Architecture
Spawns the local Gateway & Microservice server on an ephemeral port and executes
a complete customer journey simulating the Gateway API request path:
  1. GET  /healthz                       (Gateway + Jaeger OTLP :4317 check)
  2. GET  /api/products                  (productcatalogservice list)
  3. GET  /api/products/search?q=camera  (productcatalogservice search)
  4. POST /api/cart/user-gaia-01/items   (cartservice -> ElastiCache Redis store)
  5. GET  /api/cart/user-gaia-01         (cartservice state verification)
  6. POST /api/checkout                  (checkoutservice currency conversion + order ID)
"""

import json
import socket
import threading
import time
import urllib.request
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../scripts")))
from http.server import HTTPServer
import importlib.util

spec = importlib.util.spec_from_file_location(
    "dev_server",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../scripts/dev-server.py")),
)
dev_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dev_server)


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def request_json(method, url, payload=None, headers=None):
    hdrs = {"Content-Type": "application/json", "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"}
    if headers:
        hdrs.update(headers)
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, dict(resp.headers), json.loads(resp.read().decode("utf-8"))


def main():
    port = get_free_port()
    base = f"http://127.0.0.1:{port}"
    httpd = HTTPServer(("127.0.0.1", port), dev_server.BoutiqueGatewayHandler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(0.1)

    print("==============================================================================")
    print(f" [ARTEMIS LIVE E2E] Testing Gateway API Request Path on {base}")
    print("==============================================================================")

    # Step 1: Healthz & OTLP traceparent propagation
    status, headers, body = request_json("GET", f"{base}/healthz")
    assert status == 200 and body["status"] == "ok"
    assert "traceparent" in headers
    print(f"  [PASS] Step 1 — GET /healthz (200 OK) | OTLP: {body['otlp_endpoint']} | traceparent: {headers['traceparent']}")

    # Step 2: Browse Product Catalog
    status, headers, body = request_json("GET", f"{base}/api/products")
    assert status == 200 and body["total"] == 9
    print(f"  [PASS] Step 2 — GET /api/products (200 OK) | Loaded {body['total']} curated boutique products")

    # Step 3: Search Product Catalog
    status, headers, body = request_json("GET", f"{base}/api/products/search?q=camera")
    assert status == 200 and body["total"] == 1 and body["products"][0]["id"] == "6E92ZMYYFZ"
    print(f"  [PASS] Step 3 — GET /api/products/search?q=camera (200 OK) | Matched: {body['products'][0]['name']}")

    # Step 4: Add items to Redis Cart
    status, headers, body = request_json(
        "POST",
        f"{base}/api/cart/user-gaia-01/items",
        {"productId": "1YMWWN1N4O", "quantity": 1},
    )
    assert status == 200 and body["totalItems"] == 1
    status, headers, body = request_json(
        "POST",
        f"{base}/api/cart/user-gaia-01/items",
        {"productId": "OLJCESPC7Z", "quantity": 2},
    )
    assert status == 200 and body["totalItems"] == 3
    print(f"  [PASS] Step 4 — POST /api/cart/user-gaia-01/items (200 OK) | Cart totalItems: {body['totalItems']} ({body['backingStore']})")

    # Step 5: Retrieve Cart
    status, headers, body = request_json("GET", f"{base}/api/cart/user-gaia-01")
    assert status == 200 and len(body["items"]) == 2
    print(f"  [PASS] Step 5 — GET /api/cart/user-gaia-01 (200 OK) | Distinct SKUs in Redis cart: {len(body['items'])}")

    # Step 6: Execute Multi-Currency Checkout (EUR)
    status, headers, body = request_json(
        "POST",
        f"{base}/api/checkout",
        {
            "userId": "user-gaia-01",
            "userCurrency": "EUR",
            "email": "devops@boutique.example.com",
            "address": {
                "streetAddress": "742 Evergreen Terrace",
                "city": "Madrid",
                "state": "MD",
                "country": "Spain",
                "zipCode": "28001",
            },
            "items": [
                {"productId": "1YMWWN1N4O", "quantity": 1},
                {"productId": "OLJCESPC7Z", "quantity": 2},
            ],
        },
    )
    assert status == 200 and body["orderId"].startswith("ORD-") and body["shippingTrackingId"].startswith("TRK-")
    print(
        f"  [PASS] Step 6 — POST /api/checkout (200 OK) | Order: {body['orderId']} | Tracking: {body['shippingTrackingId']} | Total Paid: {body['totalPaidConverted']} {body['userCurrency']}"
    )

    httpd.shutdown()
    print("==============================================================================")
    print(" [ARTEMIS LIVE E2E] ALL 6 CUSTOMER JOURNEY STEPS PASSED (100% E2E SUCCESS)")
    print("==============================================================================")


if __name__ == "__main__":
    main()
