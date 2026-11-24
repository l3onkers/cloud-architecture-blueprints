"""Online Boutique Product Catalog Service (FastAPI + OTLP trace headers)."""

import os
import uuid
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, Request, Response
from pydantic import BaseModel

app = FastAPI(
    title="Online Boutique — Product Catalog Service",
    version="1.0.0",
    description="Curated Online Boutique product catalog exposing search, details, and OTLP trace headers.",
)


class Money(BaseModel):
    currencyCode: str = "USD"
    units: int
    nanos: int = 0


class Product(BaseModel):
    id: str
    name: str
    description: str
    picture: str
    priceUsd: Money
    categories: List[str]


PRODUCTS_DB: List[Product] = [
    Product(
        id="OLJCESPC7Z",
        name="Sunglasses",
        description="A modern take on classic aviator sunglasses with UV400 polarized lenses.",
        picture="/static/img/products/sunglasses.jpg",
        priceUsd=Money(currencyCode="USD", units=19, nanos=990000000),
        categories=["accessories", "eyewear", "sunglasses"],
    ),
    Product(
        id="66VCHSJNUP",
        name="Tank Top",
        description="Lightweight organic cotton tank top designed for warm coastal days.",
        picture="/static/img/products/tank-top.jpg",
        priceUsd=Money(currencyCode="USD", units=18, nanos=990000000),
        categories=["clothing", "tops"],
    ),
    Product(
        id="1YMWWN1N4O",
        name="Watch",
        description="Minimalist brushed stainless steel chronograph watch with sapphire crystal glass.",
        picture="/static/img/products/watch.jpg",
        priceUsd=Money(currencyCode="USD", units=109, nanos=990000000),
        categories=["accessories", "watches", "horology"],
    ),
    Product(
        id="L9ECAV7KIM",
        name="Loafers",
        description="Hand-stitched Italian suede loafers with cushioned leather insoles.",
        picture="/static/img/products/loafers.jpg",
        priceUsd=Money(currencyCode="USD", units=89, nanos=500000000),
        categories=["footwear", "leather"],
    ),
    Product(
        id="2ZYFJ3GM2N",
        name="Hairdryer",
        description="Ionic salon-grade compact hairdryer with three thermal settings.",
        picture="/static/img/products/hairdryer.jpg",
        priceUsd=Money(currencyCode="USD", units=24, nanos=990000000),
        categories=["hair", "beauty", "home"],
    ),
    Product(
        id="0PUK6V6EV0",
        name="Candle Holder",
        description="Artisanal matte brass geometric candle holder for dining tables.",
        picture="/static/img/products/candle-holder.jpg",
        priceUsd=Money(currencyCode="USD", units=18, nanos=990000000),
        categories=["decor", "home"],
    ),
    Product(
        id="LS4PSXUNUM",
        name="Salt & Pepper Shakers",
        description="Walnut and brushed copper precision grinders for sea salt and peppercorns.",
        picture="/static/img/products/salt-and-pepper-shakers.jpg",
        priceUsd=Money(currencyCode="USD", units=18, nanos=490000000),
        categories=["kitchen", "home"],
    ),
    Product(
        id="9SIQT8TOJO",
        name="Bamboo Glass Jar",
        description="Borosilicate airtight storage jar with sustainable bamboo lid.",
        picture="/static/img/products/bamboo-glass-jar.jpg",
        priceUsd=Money(currencyCode="USD", units=5, nanos=490000000),
        categories=["kitchen", "decor"],
    ),
    Product(
        id="6E92ZMYYFZ",
        name="Vintage Camera & Leather Bag Bundle",
        description="Restored 35mm rangefinder vintage camera paired with a full-grain leather messenger bag.",
        picture="/static/img/products/camera.jpg",
        priceUsd=Money(currencyCode="USD", units=164, nanos=500000000),
        categories=["photography", "vintage", "leather", "bags"],
    ),
]


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
    response.headers["X-OTEL-Service"] = os.getenv("OTEL_SERVICE_NAME", "productcatalogservice")
    response.headers["X-OTEL-Exporter"] = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://jaeger-collector.tracing.svc.cluster.local:4317",
    )
    return response


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "productcatalogservice",
        "otlp_endpoint": os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://jaeger-collector.tracing.svc.cluster.local:4317",
        ),
    }


@app.get("/products", response_model=List[Product])
def list_products(category: Optional[str] = Query(default=None)) -> List[Product]:
    if category:
        lowered = category.lower()
        return [p for p in PRODUCTS_DB if any(c.lower() == lowered for c in p.categories)]
    return PRODUCTS_DB


@app.get("/products/search", response_model=List[Product])
def search_products(q: str = Query(..., min_length=1, description="Search query")) -> List[Product]:
    term = q.strip().lower()
    return [
        p
        for p in PRODUCTS_DB
        if term in p.name.lower()
        or term in p.description.lower()
        or any(term in cat.lower() for cat in p.categories)
    ]


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str) -> Product:
    for product in PRODUCTS_DB:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
