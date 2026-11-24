/**
 * Online Boutique — k6 Load & Performance Validation Suite
 * Governed by: artemis-k6-load-test
 *
 * Validates the AWS EKS Gateway API / ALB request path across three concurrent scenarios:
 *   1. browse_catalog  — GET /api/products & GET /api/products/{id}
 *   2. cart_operations — POST /api/cart/{userId}/items & GET /api/cart/{userId}
 *                        (Exercises ElastiCache Redis throughput & cartservice-hpa triggers)
 *   3. checkout_flow   — POST /api/checkout
 *                        (Exercises multi-currency checkout orchestration & checkoutservice-hpa triggers)
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

const DOMAIN_NAME = __ENV.DOMAIN_NAME || '';
const BASE_URL = __ENV.BASE_URL || (DOMAIN_NAME ? `https://shop.${DOMAIN_NAME}` : 'http://localhost:8080');

const catalogLatency = new Trend('boutique_catalog_duration_ms', true);
const cartLatency = new Trend('boutique_cart_duration_ms', true);
const checkoutLatency = new Trend('boutique_checkout_duration_ms', true);
const ordersConfirmed = new Counter('boutique_orders_confirmed_total');
const errorRate = new Rate('boutique_business_error_rate');

const PRODUCT_IDS = [
  '1YMWWN1N4O',
  'OLJCESPC7Z',
  '6E92ZMYYFZ',
  '66VCHSJNUP',
  'L9ECAV7KIM',
  '2ZYFJ3GM2N',
  '0PUK6V6EV0',
  'LS4PSXUNUM',
  '9SIQT8TOJO',
];

const CURRENCIES = ['USD', 'EUR', 'GBP'];

export const options = {
  scenarios: {
    browse_catalog: {
      executor: 'ramping-vus',
      exec: 'browseCatalogScenario',
      startVUs: 2,
      stages: [
        { duration: '1m', target: 40 }, // Ramp up catalog traffic
        { duration: '3m', target: 40 }, // Hold steady state
        { duration: '1m', target: 0 },  // Ramp down cleanly
      ],
      gracefulRampDown: '15s',
    },
    cart_operations: {
      executor: 'ramping-vus',
      exec: 'cartOperationsScenario',
      startVUs: 1,
      stages: [
        { duration: '1m', target: 25 }, // Ramp up to trigger cartservice-hpa & ElastiCache ops
        { duration: '3m', target: 25 }, // Hold load against Redis cluster
        { duration: '1m', target: 0 },  // Ramp down
      ],
      gracefulRampDown: '15s',
    },
    checkout_flow: {
      executor: 'ramping-vus',
      exec: 'checkoutFlowScenario',
      startVUs: 1,
      stages: [
        { duration: '1m', target: 15 }, // Ramp up checkout transactions (checkoutservice-hpa)
        { duration: '3m', target: 15 }, // Hold sustained order placement
        { duration: '1m', target: 0 },  // Ramp down
      ],
      gracefulRampDown: '15s',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<300', 'p(99)<600'],
    http_req_failed: ['rate<0.01'],
    boutique_catalog_duration_ms: ['p(95)<250'],
    boutique_cart_duration_ms: ['p(95)<300'],
    boutique_checkout_duration_ms: ['p(95)<400'],
    boutique_business_error_rate: ['rate<0.01'],
  },
};

function buildHeaders() {
  const traceId = `${Math.random().toString(16).slice(2, 18)}${Math.random().toString(16).slice(2, 18)}`.padEnd(32, '0').slice(0, 32);
  const spanId = Math.random().toString(16).slice(2, 18).padEnd(16, '0').slice(0, 16);
  return {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'traceparent': `00-${traceId}-${spanId}-01`,
  };
}

export function browseCatalogScenario() {
  const headers = buildHeaders();
  const productId = PRODUCT_IDS[Math.floor(Math.random() * PRODUCT_IDS.length)];

  group('browse_catalog', () => {
    const listRes = http.get(`${BASE_URL}/api/products`, {
      headers,
      tags: { scenario: 'browse_catalog', endpoint: 'list_products' },
    });
    catalogLatency.add(listRes.timings.duration);

    const listOk = check(listRes, {
      'catalog list returns HTTP 200': (r) => r.status === 200,
      'catalog list returns non-empty array': (r) => {
        try {
          const body = r.json();
          return Array.isArray(body) && body.length > 0;
        } catch (_) {
          return false;
        }
      },
      'catalog list propagates OTLP traceparent': (r) => Boolean(r.headers['Traceparent'] || r.headers['traceparent']),
    });
    errorRate.add(!listOk);

    const detailRes = http.get(`${BASE_URL}/api/products/${productId}`, {
      headers,
      tags: { scenario: 'browse_catalog', endpoint: 'get_product' },
    });
    catalogLatency.add(detailRes.timings.duration);

    const detailOk = check(detailRes, {
      'product detail returns HTTP 200': (r) => r.status === 200,
      'product detail matches requested id': (r) => {
        try {
          return r.json('id') === productId;
        } catch (_) {
          return false;
        }
      },
    });
    errorRate.add(!detailOk);
  });

  sleep(0.5);
}

export function cartOperationsScenario() {
  const headers = buildHeaders();
  const userId = `k6-shopper-vu${__VU}-iter${__ITER}`;
  const productId = PRODUCT_IDS[Math.floor(Math.random() * PRODUCT_IDS.length)];

  group('cart_operations', () => {
    const addPayload = JSON.stringify({
      productId,
      quantity: Math.floor(Math.random() * 2) + 1,
    });

    const addRes = http.post(`${BASE_URL}/api/cart/${userId}/items`, addPayload, {
      headers,
      tags: { scenario: 'cart_operations', endpoint: 'add_cart_item' },
    });
    cartLatency.add(addRes.timings.duration);

    const addOk = check(addRes, {
      'add to cart returns HTTP 200': (r) => r.status === 200,
      'cart response contains user items': (r) => {
        try {
          const body = r.json();
          return Array.isArray(body.items) && body.items.length >= 1;
        } catch (_) {
          return false;
        }
      },
    });
    errorRate.add(!addOk);

    const getRes = http.get(`${BASE_URL}/api/cart/${userId}`, {
      headers,
      tags: { scenario: 'cart_operations', endpoint: 'get_cart' },
    });
    cartLatency.add(getRes.timings.duration);

    const getOk = check(getRes, {
      'get cart returns HTTP 200': (r) => r.status === 200,
      'get cart returns matching userId': (r) => {
        try {
          return r.json('userId') === userId;
        } catch (_) {
          return false;
        }
      },
    });
    errorRate.add(!getOk);
  });

  sleep(0.6);
}

export function checkoutFlowScenario() {
  const headers = buildHeaders();
  const userId = `k6-checkout-vu${__VU}-iter${__ITER}`;
  const currency = CURRENCIES[Math.floor(Math.random() * CURRENCIES.length)];
  const primaryProduct = PRODUCT_IDS[Math.floor(Math.random() * PRODUCT_IDS.length)];

  group('checkout_flow', () => {
    const checkoutPayload = JSON.stringify({
      userId,
      userCurrency: currency,
      email: 'loadtest-synthetic@online-boutique.internal',
      address: {
        streetAddress: '410 Terry Ave N',
        city: 'Seattle',
        state: 'WA',
        country: 'United States',
        zipCode: '98109',
      },
      items: [
        { productId: primaryProduct, quantity: 1, unitPriceUsd: 109.99 },
        { productId: 'OLJCESPC7Z', quantity: 2, unitPriceUsd: 19.99 },
      ],
    });

    const checkoutRes = http.post(`${BASE_URL}/api/checkout`, checkoutPayload, {
      headers,
      tags: { scenario: 'checkout_flow', endpoint: 'place_order' },
    });
    checkoutLatency.add(checkoutRes.timings.duration);

    const checkoutOk = check(checkoutRes, {
      'checkout returns HTTP 200': (r) => r.status === 200,
      'checkout generates orderId with ORD- prefix': (r) => {
        try {
          const orderId = r.json('orderId');
          return typeof orderId === 'string' && orderId.startsWith('ORD-');
        } catch (_) {
          return false;
        }
      },
      'checkout generates shippingTrackingId with TRK- prefix': (r) => {
        try {
          const trackingId = r.json('shippingTrackingId');
          return typeof trackingId === 'string' && trackingId.startsWith('TRK-');
        } catch (_) {
          return false;
        }
      },
    });

    if (checkoutOk) {
      ordersConfirmed.add(1);
    }
    errorRate.add(!checkoutOk);
  });

  sleep(0.8);
}

export default function () {
  browseCatalogScenario();
  cartOperationsScenario();
  checkoutFlowScenario();
}
