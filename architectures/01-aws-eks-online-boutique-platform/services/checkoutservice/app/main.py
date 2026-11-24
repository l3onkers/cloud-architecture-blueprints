"""Online Boutique Checkout Orchestrator Service (FastAPI)."""

import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field

app = FastAPI(
    title="Online Boutique — Checkout Service",
    version="1.0.0",
    description="Orchestrates cart validation, currency conversion, shipping quote, and order confirmation.",
)

CURRENCY_RATES_FROM_USD: Dict[str, float] = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 154.50,
    "CAD": 1.38,
}

DEFAULT_PRODUCT_PRICES_USD: Dict[str, float] = {
    "OLJCESPC7Z": 19.99,
    "66VCHSJNUP": 18.99,
    "1YMWWN1N4O": 109.99,
    "L9ECAV7KIM": 89.50,
    "2ZYFJ3GM2N": 24.99,
    "0PUK6V6EV0": 18.99,
    "LS4PSXUNUM": 18.49,
    "9SIQT8TOJO": 5.49,
    "6E92ZMYYFZ": 164.50,
}


class CheckoutItem(BaseModel):
    productId: str
    quantity: int = Field(..., gt=0)
    unitPriceUsd: float = Field(default=0.0, ge=0.0)


class ShippingAddress(BaseModel):
    streetAddress: str
    city: str
    state: str
    country: str
    zipCode: str


class CheckoutRequest(BaseModel):
    userId: str
    userCurrency: str = "USD"
    email: str
    address: ShippingAddress
    items: List[CheckoutItem]


class OrderConfirmation(BaseModel):
    orderId: str
    shippingTrackingId: str
    userId: str
    userCurrency: str
    itemsCount: int
    subtotalConverted: float
    shippingCostConverted: float
    totalPaidConverted: float
    transactionId: str
    timestampUtc: str


@app.middleware("http")
async def attach_otlp_trace_context(request: Request, call_next):
    incoming_traceparent = request.headers.get("traceparent")
    if incoming_traceparent:
        traceparent = incoming_traceparent
    else:
        trace_id = uuid.uuid4().hex
        span_id = uuid.uuid4().hex[:16]
        traceparent = f"00-{trace_id}-{span_id}-01"

    response: Response = await call_next(request)
    response.headers["traceparent"] = traceparent
    response.headers["X-OTEL-Service"] = os.getenv("OTEL_SERVICE_NAME", "checkoutservice")
    response.headers["X-OTEL-Exporter"] = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://jaeger-collector.tracing.svc.cluster.local:4317",
    )
    return response


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "checkoutservice",
        "otlp_endpoint": os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://jaeger-collector.tracing.svc.cluster.local:4317",
        ),
    }


@app.post("/checkout", response_model=OrderConfirmation)
def place_order(payload: CheckoutRequest) -> OrderConfirmation:
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cannot checkout an empty cart.")

    currency = payload.userCurrency.upper()
    if currency not in CURRENCY_RATES_FROM_USD:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported currency '{currency}'. Supported: {list(CURRENCY_RATES_FROM_USD.keys())}",
        )

    rate = CURRENCY_RATES_FROM_USD[currency]
    subtotal_usd = 0.0
    total_units = 0

    for item in payload.items:
        unit_price = (
            item.unitPriceUsd
            if item.unitPriceUsd > 0
            else DEFAULT_PRODUCT_PRICES_USD.get(item.productId, 25.00)
        )
        subtotal_usd += unit_price * item.quantity
        total_units += item.quantity

    shipping_usd = round(4.99 + (1.75 * total_units), 2)
    subtotal_converted = round(subtotal_usd * rate, 2)
    shipping_converted = round(shipping_usd * rate, 2)
    total_converted = round(subtotal_converted + shipping_converted, 2)

    return OrderConfirmation(
        orderId=f"ORD-{uuid.uuid4().hex[:12].upper()}",
        shippingTrackingId=f"TRK-{uuid.uuid4().hex[:10].upper()}",
        userId=payload.userId,
        userCurrency=currency,
        itemsCount=total_units,
        subtotalConverted=subtotal_converted,
        shippingCostConverted=shipping_converted,
        totalPaidConverted=total_converted,
        transactionId=f"TXN-{uuid.uuid4().hex[:14].upper()}",
        timestampUtc=datetime.now(timezone.utc).isoformat(),
    )
