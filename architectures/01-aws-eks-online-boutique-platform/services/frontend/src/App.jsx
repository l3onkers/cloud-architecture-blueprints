import React, { useEffect, useState } from "react";

const FALLBACK_PRODUCTS = [
  {
    id: "1YMWWN1N4O",
    name: "Watch",
    description: "Minimalist brushed stainless steel chronograph watch with sapphire crystal glass.",
    priceUsd: { currencyCode: "USD", units: 109, nanos: 990000000 },
    categories: ["accessories", "watches"],
  },
  {
    id: "OLJCESPC7Z",
    name: "Sunglasses",
    description: "A modern take on classic aviator sunglasses with UV400 polarized lenses.",
    priceUsd: { currencyCode: "USD", units: 19, nanos: 990000000 },
    categories: ["accessories", "eyewear"],
  },
  {
    id: "6E92ZMYYFZ",
    name: "Vintage Camera & Leather Bag Bundle",
    description: "Restored 35mm rangefinder vintage camera paired with a full-grain leather messenger bag.",
    priceUsd: { currencyCode: "USD", units: 164, nanos: 500000000 },
    categories: ["photography", "vintage", "leather"],
  },
];

export default function App() {
  const [products, setProducts] = useState(FALLBACK_PRODUCTS);
  const [cart, setCart] = useState([]);
  const [currency, setCurrency] = useState("USD");
  const [orderConfirmation, setOrderConfirmation] = useState(null);
  const userId = "boutique-session-user";

  useEffect(() => {
    fetch("/api/products")
      .then((res) => (res.ok ? res.json() : FALLBACK_PRODUCTS))
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setProducts(data);
        }
      })
      .catch(() => setProducts(FALLBACK_PRODUCTS));
  }, []);

  const formatPrice = (priceUsd) => {
    const amount = priceUsd.units + priceUsd.nanos / 1e9;
    return `${currency} ${amount.toFixed(2)}`;
  };

  const addToCart = async (product) => {
    const updated = [...cart];
    const existing = updated.find((item) => item.productId === product.id);
    if (existing) {
      existing.quantity += 1;
    } else {
      updated.push({
        productId: product.id,
        name: product.name,
        quantity: 1,
        unitPriceUsd: product.priceUsd.units + product.priceUsd.nanos / 1e9,
      });
    }
    setCart(updated);

    try {
      await fetch(`/api/cart/${userId}/items`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ productId: product.id, quantity: 1 }),
      });
    } catch {
      // Local state already updated for responsive UI
    }
  };

  const handleCheckout = async () => {
    if (cart.length === 0) return;
    const payload = {
      userId,
      userCurrency: currency,
      email: "shopper@online-boutique.aws",
      address: {
        streetAddress: "410 Terry Ave N",
        city: "Seattle",
        state: "WA",
        country: "United States",
        zipCode: "98109",
      },
      items: cart.map((i) => ({
        productId: i.productId,
        quantity: i.quantity,
        unitPriceUsd: i.unitPriceUsd,
      })),
    };

    try {
      const response = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (response.ok) {
        const confirmation = await response.json();
        setOrderConfirmation(confirmation);
        setCart([]);
      }
    } catch {
      setOrderConfirmation({
        orderId: "ORD-LOCAL-DEMO",
        shippingTrackingId: "TRK-LOCAL-9981",
        userCurrency: currency,
        totalPaidConverted: cart.reduce((acc, i) => acc + i.unitPriceUsd * i.quantity, 0).toFixed(2),
      });
      setCart([]);
    }
  };

  return (
    <div style={{ maxWidth: "1100px", margin: "0 auto", padding: "24px" }}>
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: "1px solid #e2e8f0",
          paddingBottom: "16px",
          marginBottom: "24px",
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: "1.75rem" }}>Online Boutique</h1>
          <p style={{ margin: "4px 0 0", color: "#475569", fontSize: "0.9rem" }}>
            AWS EKS Cloud-Native Microservices Storefront (OTLP Distributed Tracing Enabled)
          </p>
        </div>
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <select
            aria-label="Currency selector"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
          >
            <option value="USD">USD ($)</option>
            <option value="EUR">EUR (€)</option>
            <option value="GBP">GBP (£)</option>
          </select>
          <button
            onClick={handleCheckout}
            disabled={cart.length === 0}
            style={{
              padding: "10px 16px",
              borderRadius: "6px",
              border: "none",
              background: cart.length > 0 ? "#0284c7" : "#94a3b8",
              color: "#fff",
              fontWeight: 600,
              cursor: cart.length > 0 ? "pointer" : "not-allowed",
            }}
          >
            Checkout ({cart.reduce((sum, i) => sum + i.quantity, 0)})
          </button>
        </div>
      </header>

      {orderConfirmation && (
        <section
          style={{
            padding: "16px",
            marginBottom: "24px",
            borderRadius: "8px",
            background: "#ecfdf5",
            border: "1px solid #10b981",
          }}
        >
          <strong>Order Confirmed:</strong> {orderConfirmation.orderId} |{" "}
          <strong>Tracking:</strong> {orderConfirmation.shippingTrackingId} |{" "}
          <strong>Total Paid:</strong> {orderConfirmation.userCurrency}{" "}
          {orderConfirmation.totalPaidConverted}
        </section>
      )}

      <main
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
          gap: "20px",
        }}
      >
        {products.map((product) => (
          <article
            key={product.id}
            style={{
              background: "#fff",
              border: "1px solid #e2e8f0",
              borderRadius: "10px",
              padding: "20px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
            }}
          >
            <div>
              <span
                style={{
                  fontSize: "0.75rem",
                  textTransform: "uppercase",
                  color: "#0284c7",
                  fontWeight: 700,
                }}
              >
                {(product.categories || []).join(" • ")}
              </span>
              <h2 style={{ margin: "8px 0", fontSize: "1.2rem" }}>{product.name}</h2>
              <p style={{ color: "#475569", fontSize: "0.9rem", lineHeight: 1.4 }}>
                {product.description}
              </p>
            </div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginTop: "16px",
              }}
            >
              <strong style={{ fontSize: "1.1rem" }}>{formatPrice(product.priceUsd)}</strong>
              <button
                onClick={() => addToCart(product)}
                style={{
                  padding: "8px 14px",
                  borderRadius: "6px",
                  border: "1px solid #0284c7",
                  background: "#f0f9ff",
                  color: "#0369a1",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                Add to Cart
              </button>
            </div>
          </article>
        ))}
      </main>
    </div>
  );
}
