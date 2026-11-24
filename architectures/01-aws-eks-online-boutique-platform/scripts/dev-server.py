#!/usr/bin/env python3
"""
Online Boutique Platform — Zero-Dependency Local Dev & Integration Server
Simulates the AWS ALB Gateway API request path locally on http://127.0.0.1:8080:
  - GET    /                        -> Interactive Online Boutique Storefront UI (HTML/JS)
  - GET    /healthz                 -> Gateway & Microservices Health + OTLP (:4317) status
  - GET    /api/products            -> Product Catalog Service (productcatalogservice)
  - GET    /api/products/search?q=  -> Product Search
  - GET    /api/products/<id>       -> Product Detail
  - GET    /api/cart/<user>         -> Cart Service backed by ElastiCache Redis emulator (cartservice)
  - POST   /api/cart/<user>/items   -> Add item to Cart
  - DELETE /api/cart/<user>         -> Empty Cart
  - POST   /api/checkout            -> Checkout Orchestrator Service (checkoutservice)
"""

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

PRODUCTS = [
    {
        "id": "OLJCESPC7Z",
        "name": "Sunglasses",
        "description": "A modern take on classic aviator sunglasses with UV400 polarized lenses.",
        "picture": "🕶️",
        "priceUsd": {"currencyCode": "USD", "units": 19, "nanos": 990000000},
        "categories": ["accessories", "eyewear", "sunglasses"],
    },
    {
        "id": "66VCHSJNUP",
        "name": "Tank Top",
        "description": "Lightweight organic cotton tank top designed for warm coastal days.",
        "picture": "👕",
        "priceUsd": {"currencyCode": "USD", "units": 18, "nanos": 990000000},
        "categories": ["clothing", "tops"],
    },
    {
        "id": "1YMWWN1N4O",
        "name": "Watch",
        "description": "Minimalist brushed stainless steel chronograph watch with sapphire crystal glass.",
        "picture": "⌚",
        "priceUsd": {"currencyCode": "USD", "units": 109, "nanos": 990000000},
        "categories": ["accessories", "watches", "horology"],
    },
    {
        "id": "L9ECAV7KIM",
        "name": "Loafers",
        "description": "Hand-stitched Italian suede loafers with cushioned leather insoles.",
        "picture": "👞",
        "priceUsd": {"currencyCode": "USD", "units": 89, "nanos": 500000000},
        "categories": ["footwear", "leather"],
    },
    {
        "id": "2ZYFJ3GM2N",
        "name": "Hairdryer",
        "description": "Ionic salon-grade compact hairdryer with three thermal settings.",
        "picture": "💨",
        "priceUsd": {"currencyCode": "USD", "units": 24, "nanos": 990000000},
        "categories": ["hair", "beauty", "home"],
    },
    {
        "id": "0PUK6V6EV0",
        "name": "Candle Holder",
        "description": "Artisanal matte brass geometric candle holder for dining tables.",
        "picture": "🕯️",
        "priceUsd": {"currencyCode": "USD", "units": 18, "nanos": 990000000},
        "categories": ["decor", "home"],
    },
    {
        "id": "LS4PSXUNUM",
        "name": "Salt & Pepper Shakers",
        "description": "Walnut and brushed copper precision grinders for sea salt and peppercorns.",
        "picture": "🧂",
        "priceUsd": {"currencyCode": "USD", "units": 18, "nanos": 490000000},
        "categories": ["kitchen", "home"],
    },
    {
        "id": "9SIQT8TOJO",
        "name": "Bamboo Glass Jar",
        "description": "Borosilicate airtight storage jar with sustainable bamboo lid.",
        "picture": "🫙",
        "priceUsd": {"currencyCode": "USD", "units": 5, "nanos": 490000000},
        "categories": ["kitchen", "decor"],
    },
    {
        "id": "6E92ZMYYFZ",
        "name": "Vintage Camera & Leather Bag Bundle",
        "description": "Restored 35mm rangefinder vintage camera paired with a full-grain leather messenger bag.",
        "picture": "📷",
        "priceUsd": {"currencyCode": "USD", "units": 164, "nanos": 500000000},
        "categories": ["photography", "vintage", "accessories"],
    },
]

CURRENCY_RATES = {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "JPY": 154.50, "CAD": 1.38}
REDIS_CART_STORE = {}

STOREFRONT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Online Boutique — AWS EKS 1.34 Gateway API Storefront</title>
  <style>
    :root {
      --bg: #0f172a;
      --surface: #1e293b;
      --border: #334155;
      --primary: #38bdf8;
      --accent: #a855f7;
      --success: #22c55e;
      --text: #f8fafc;
      --muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }
    header {
      background: rgba(15, 23, 42, 0.92);
      border-bottom: 1px solid var(--border);
      padding: 1rem 2rem;
      position: sticky;
      top: 0;
      z-index: 20;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
    }
    .brand { display: flex; align-items: center; gap: 0.75rem; }
    .brand h1 { font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em; }
    .badge {
      font-size: 0.72rem;
      padding: 0.2rem 0.55rem;
      border-radius: 999px;
      background: rgba(56, 189, 248, 0.15);
      color: var(--primary);
      border: 1px solid rgba(56, 189, 248, 0.35);
      font-family: monospace;
    }
    .controls { display: flex; align-items: center; gap: 0.75rem; }
    select, input, button {
      background: var(--surface);
      color: var(--text);
      border: 1px solid var(--border);
      padding: 0.5rem 0.85rem;
      border-radius: 0.5rem;
      font-size: 0.88rem;
    }
    button {
      cursor: pointer;
      background: var(--primary);
      color: #020617;
      font-weight: 600;
      border: none;
      transition: opacity 0.15s;
    }
    button:hover { opacity: 0.9; }
    button.secondary {
      background: var(--surface);
      color: var(--text);
      border: 1px solid var(--border);
    }
    .telemetry-bar {
      background: #020617;
      border-bottom: 1px solid var(--border);
      padding: 0.55rem 2rem;
      font-family: monospace;
      font-size: 0.78rem;
      color: var(--muted);
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 0.5rem;
    }
    .telemetry-bar span.hl { color: var(--success); }
    main {
      max-width: 1320px;
      margin: 1.5rem auto;
      padding: 0 1.5rem;
      display: grid;
      grid-template-columns: 1fr 370px;
      gap: 1.75rem;
    }
    @media (max-width: 960px) { main { grid-template-columns: 1fr; } }
    .toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 0.6rem;
      margin-bottom: 1.25rem;
      align-items: center;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 1.15rem;
    }
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 0.75rem;
      padding: 1.2rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 0.85rem;
    }
    .card-icon {
      font-size: 2.5rem;
      background: rgba(15, 23, 42, 0.6);
      height: 85px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 0.5rem;
    }
    .card h3 { font-size: 1.05rem; }
    .card p { font-size: 0.84rem; color: var(--muted); }
    .tags { display: flex; flex-wrap: wrap; gap: 0.35rem; }
    .tag {
      font-size: 0.7rem;
      background: rgba(148, 163, 184, 0.12);
      color: var(--muted);
      padding: 0.12rem 0.45rem;
      border-radius: 0.3rem;
    }
    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 0.3rem;
    }
    .price { font-size: 1.12rem; font-weight: 700; color: var(--primary); }
    aside {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 0.75rem;
      padding: 1.25rem;
      height: fit-content;
      position: sticky;
      top: 5.5rem;
    }
    aside h2 { font-size: 1.15rem; margin-bottom: 0.75rem; display: flex; justify-content: space-between; }
    .cart-item {
      display: flex;
      justify-content: space-between;
      padding: 0.55rem 0;
      border-bottom: 1px solid var(--border);
      font-size: 0.88rem;
    }
    .order-box {
      margin-top: 1rem;
      padding: 0.9rem;
      border-radius: 0.5rem;
      background: rgba(34, 197, 94, 0.12);
      border: 1px solid rgba(34, 197, 94, 0.4);
      font-size: 0.82rem;
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <h1>🛍️ Online Boutique</h1>
      <span class="badge">app-alb-gateway · HTTPS 443</span>
      <span class="badge">EKS 1.34 · ElastiCache Redis</span>
    </div>
    <div class="controls">
      <input id="searchInput" type="text" placeholder="Search catalog..." oninput="filterProducts()" />
      <select id="categorySelect" onchange="filterProducts()">
        <option value="">All Categories</option>
        <option value="accessories">Accessories</option>
        <option value="clothing">Clothing</option>
        <option value="footwear">Footwear</option>
        <option value="home">Home & Decor</option>
        <option value="kitchen">Kitchen</option>
        <option value="photography">Photography</option>
      </select>
      <select id="currencySelect" onchange="renderCatalog(); renderCart();">
        <option value="USD">USD ($)</option>
        <option value="EUR">EUR (€)</option>
        <option value="GBP">GBP (£)</option>
        <option value="JPY">JPY (¥)</option>
        <option value="CAD">CAD (C$)</option>
      </select>
    </div>
  </header>

  <div class="telemetry-bar">
    <div>Gateway Route: <span class="hl">HTTPRoute -> frontend:80 -> microservices</span></div>
    <div>Last OTLP Traceparent: <span id="traceSpan" class="hl">initializing...</span></div>
    <div>Jaeger Collector: <span class="hl">jaeger-collector.tracing.svc:4317</span></div>
  </div>

  <main>
    <section>
      <div class="grid" id="productGrid"></div>
    </section>

    <aside>
      <h2>
        <span>🛒 Redis Cart</span>
        <span class="badge" id="cartCountBadge">0 items</span>
      </h2>
      <div id="cartList"><p style="color:var(--muted);font-size:0.85rem;">Your cart is empty.</p></div>
      <div style="margin-top:1rem; display:flex; gap:0.5rem;">
        <button style="flex:1;" onclick="checkout()">Checkout Now</button>
        <button class="secondary" onclick="clearCart()">Clear</button>
      </div>
      <div id="orderResult"></div>
    </aside>
  </main>

  <script>
    const RATES = { USD: 1.0, EUR: 0.92, GBP: 0.79, JPY: 154.50, CAD: 1.38 };
    const SYMBOLS = { USD: '$', EUR: '€', GBP: '£', JPY: '¥', CAD: 'C$' };
    const USER_ID = 'user-boutique-live';
    let allProducts = [];
    let currentCart = [];

    function formatPrice(priceUsd) {
      const cur = document.getElementById('currencySelect').value;
      const usd = priceUsd.units + (priceUsd.nanos / 1e9);
      const val = (usd * RATES[cur]).toFixed(cur === 'JPY' ? 0 : 2);
      return SYMBOLS[cur] + val + ' ' + cur;
    }

    async function apiFetch(url, options = {}) {
      const resp = await fetch(url, options);
      const tp = resp.headers.get('traceparent');
      const svc = resp.headers.get('X-OTEL-Service');
      if (tp) {
        document.getElementById('traceSpan').textContent = `${tp} (${svc || 'gateway'})`;
      }
      return resp.json();
    }

    async function loadCatalog() {
      const data = await apiFetch('/api/products');
      allProducts = data.products || [];
      renderCatalog();
    }

    function filterProducts() {
      renderCatalog();
    }

    function renderCatalog() {
      const q = document.getElementById('searchInput').value.toLowerCase().trim();
      const cat = document.getElementById('categorySelect').value.toLowerCase();
      const grid = document.getElementById('productGrid');
      const filtered = allProducts.filter(p => {
        const matchQ = !q || p.name.toLowerCase().includes(q) || p.description.toLowerCase().includes(q);
        const matchC = !cat || p.categories.some(c => c.toLowerCase() === cat);
        return matchQ && matchC;
      });
      grid.innerHTML = filtered.map(p => `
        <div class="card">
          <div>
            <div class="card-icon">${p.picture || '📦'}</div>
            <h3 style="margin-top:0.75rem;">${p.name}</h3>
            <p style="margin:0.4rem 0;">${p.description}</p>
            <div class="tags">${p.categories.map(c => `<span class="tag">${c}</span>`).join('')}</div>
          </div>
          <div class="card-footer">
            <span class="price">${formatPrice(p.priceUsd)}</span>
            <button onclick="addToCart('${p.id}')">+ Add to Cart</button>
          </div>
        </div>
      `).join('');
    }

    async function loadCart() {
      const data = await apiFetch(`/api/cart/${USER_ID}`);
      currentCart = data.items || [];
      document.getElementById('cartCountBadge').textContent = `${data.totalItems || 0} items`;
      renderCart();
    }

    function renderCart() {
      const list = document.getElementById('cartList');
      if (!currentCart.length) {
        list.innerHTML = '<p style="color:var(--muted);font-size:0.85rem;">Your cart is empty.</p>';
        return;
      }
      list.innerHTML = currentCart.map(item => {
        const prod = allProducts.find(p => p.id === item.productId) || { name: item.productId, priceUsd: { units: 20, nanos: 0 } };
        return `<div class="cart-item">
          <span><strong>${prod.name}</strong> × ${item.quantity}</span>
          <span>${formatPrice({ units: prod.priceUsd.units * item.quantity, nanos: prod.priceUsd.nanos * item.quantity })}</span>
        </div>`;
      }).join('');
    }

    async function addToCart(productId) {
      await apiFetch(`/api/cart/${USER_ID}/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productId, quantity: 1 })
      });
      await loadCart();
    }

    async function clearCart() {
      await apiFetch(`/api/cart/${USER_ID}`, { method: 'DELETE' });
      await loadCart();
    }

    async function checkout() {
      if (!currentCart.length) {
        alert('Add at least one item to the cart before checking out.');
        return;
      }
      const userCurrency = document.getElementById('currencySelect').value;
      const res = await apiFetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: USER_ID,
          userCurrency,
          email: 'architect@boutique.example.com',
          address: {
            streetAddress: '100 Cloud Native Way',
            city: 'Madrid',
            state: 'MD',
            country: 'Spain',
            zipCode: '28001'
          },
          items: currentCart
        })
      });
      document.getElementById('orderResult').innerHTML = `
        <div class="order-box">
          <div><strong>✅ Order Confirmed!</strong></div>
          <div>Order ID: <code>${res.orderId}</code></div>
          <div>Tracking: <code>${res.shippingTrackingId}</code></div>
          <div>Total Paid: <strong>${res.totalPaidConverted} ${res.userCurrency}</strong></div>
        </div>
      `;
      await loadCart();
    }

    loadCatalog().then(loadCart);
  </script>
</body>
</html>
"""


class BoutiqueGatewayHandler(BaseHTTPRequestHandler):
    def _traceparent(self):
        incoming = self.headers.get("traceparent")
        if incoming:
            return incoming
        return f"00-{uuid.uuid4().hex}-{uuid.uuid4().hex[:16]}-01"

    def _send_html(self, status_code, html_str, service_name="frontend"):
        body = html_str.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("traceparent", self._traceparent())
        self.send_header("X-OTEL-Service", service_name)
        self.send_header("X-Gateway", "app-alb-gateway")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status_code, payload, service_name):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("traceparent", self._traceparent())
        self.send_header("X-OTEL-Service", service_name)
        self.send_header(
            "X-OTEL-Exporter",
            os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger-collector.tracing.svc.cluster.local:4317"),
        )
        self.send_header("X-Gateway", "app-alb-gateway")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            self._send_html(200, STOREFRONT_HTML, "frontend")
            return

        if path == "/healthz":
            self._send_json(
                200,
                {
                    "status": "ok",
                    "gateway": "app-alb-gateway",
                    "cluster": "terraform-cluster (EKS 1.34)",
                    "otlp_endpoint": "http://jaeger-collector.tracing.svc.cluster.local:4317",
                    "redis_store": "elasticache-redis-cart-store:6379",
                },
                "gateway-health",
            )
            return

        if path in ("/api/products", "/products"):
            category = query.get("category", [None])[0]
            items = PRODUCTS
            if category:
                items = [p for p in PRODUCTS if category.lower() in [c.lower() for c in p["categories"]]]
            self._send_json(200, {"products": items, "total": len(items)}, "productcatalogservice")
            return

        if path in ("/api/products/search", "/products/search"):
            q = (query.get("q", [""])[0]).lower().strip()
            matches = [
                p for p in PRODUCTS if q in p["name"].lower() or q in p["description"].lower()
            ]
            self._send_json(200, {"query": q, "products": matches, "total": len(matches)}, "productcatalogservice")
            return

        if path.startswith("/api/products/") or path.startswith("/products/"):
            prod_id = path.rstrip("/").split("/")[-1]
            for p in PRODUCTS:
                if p["id"] == prod_id:
                    self._send_json(200, p, "productcatalogservice")
                    return
            self._send_json(404, {"detail": f"Product {prod_id} not found"}, "productcatalogservice")
            return

        if path.startswith("/api/cart/") or path.startswith("/cart/"):
            user_id = path.rstrip("/").split("/")[-1]
            items = REDIS_CART_STORE.get(user_id, {})
            item_list = [{"productId": k, "quantity": v} for k, v in items.items()]
            self._send_json(
                200,
                {
                    "userId": user_id,
                    "items": item_list,
                    "totalItems": sum(items.values()),
                    "backingStore": "aws-elasticache-redis-7.1",
                },
                "cartservice",
            )
            return

        self._send_json(404, {"detail": "Route not found"}, "app-alb-gateway")

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/cart/") or path.startswith("/cart/"):
            user_id = path.rstrip("/").split("/")[-1]
            REDIS_CART_STORE.pop(user_id, None)
            self._send_json(
                200,
                {"userId": user_id, "items": [], "totalItems": 0, "backingStore": "aws-elasticache-redis-7.1"},
                "cartservice",
            )
            return
        self._send_json(404, {"detail": "Route not found"}, "app-alb-gateway")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        data = json.loads(raw)

        if (path.startswith("/api/cart/") or path.startswith("/cart/")) and path.endswith("/items"):
            parts = path.strip("/").split("/")
            user_id = parts[-2]
            product_id = data.get("productId", "")
            quantity = int(data.get("quantity", 1))
            if not product_id or quantity <= 0:
                self._send_json(400, {"detail": "Invalid productId or quantity"}, "cartservice")
                return
            user_cart = REDIS_CART_STORE.setdefault(user_id, {})
            user_cart[product_id] = user_cart.get(product_id, 0) + quantity
            item_list = [{"productId": k, "quantity": v} for k, v in user_cart.items()]
            self._send_json(
                200,
                {
                    "userId": user_id,
                    "items": item_list,
                    "totalItems": sum(user_cart.values()),
                    "backingStore": "aws-elasticache-redis-7.1",
                },
                "cartservice",
            )
            return

        if path in ("/api/checkout", "/checkout"):
            items = data.get("items", [])
            currency = data.get("userCurrency", "USD").upper()
            if not items or currency not in CURRENCY_RATES:
                self._send_json(400, {"detail": "Invalid items or currency"}, "checkoutservice")
                return
            rate = CURRENCY_RATES[currency]
            price_lookup = {
                p["id"]: p["priceUsd"]["units"] + p["priceUsd"]["nanos"] / 1e9 for p in PRODUCTS
            }
            subtotal_usd = sum(price_lookup.get(i["productId"], 25.0) * int(i["quantity"]) for i in items)
            total_qty = sum(int(i["quantity"]) for i in items)
            shipping_usd = 0.0 if subtotal_usd >= 100.0 else round(5.99 + 1.25 * total_qty, 2)
            subtotal_conv = round(subtotal_usd * rate, 2)
            shipping_conv = round(shipping_usd * rate, 2)
            total_conv = round(subtotal_conv + shipping_conv, 2)

            user_id = data.get("userId", "guest")
            REDIS_CART_STORE.pop(user_id, None)

            self._send_json(
                200,
                {
                    "orderId": f"ORD-{uuid.uuid4().hex[:10].upper()}",
                    "shippingTrackingId": f"TRK-{uuid.uuid4().hex[:12].upper()}",
                    "userId": user_id,
                    "userCurrency": currency,
                    "itemsCount": total_qty,
                    "subtotalConverted": subtotal_conv,
                    "shippingCostConverted": shipping_conv,
                    "totalPaidConverted": total_conv,
                    "transactionId": f"TXN-{uuid.uuid4().hex[:10].upper()}",
                    "timestampUtc": datetime.now(timezone.utc).isoformat(),
                },
                "checkoutservice",
            )
            return

        self._send_json(404, {"detail": "Route not found"}, "app-alb-gateway")

    def log_message(self, fmt, *args):
        return


def run_server(port=8080):
    server = HTTPServer(("127.0.0.1", port), BoutiqueGatewayHandler)
    print(f"Online Boutique Storefront & Gateway listening on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv[1:]) >= 1 else 8080
    run_server(port)
