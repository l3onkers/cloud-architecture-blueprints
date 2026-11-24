import { test, expect } from '@playwright/test';

const CURATED_CATALOG = [
  {
    id: '1YMWWN1N4O',
    name: 'Watch',
    description: 'Minimalist brushed stainless steel chronograph watch with sapphire crystal glass.',
    priceUsd: { currencyCode: 'USD', units: 109, nanos: 990000000 },
    categories: ['accessories', 'watches'],
  },
  {
    id: 'OLJCESPC7Z',
    name: 'Sunglasses',
    description: 'A modern take on classic aviator sunglasses with UV400 polarized lenses.',
    priceUsd: { currencyCode: 'USD', units: 19, nanos: 990000000 },
    categories: ['accessories', 'eyewear'],
  },
  {
    id: '6E92ZMYYFZ',
    name: 'Vintage Camera & Leather Bag Bundle',
    description: 'Restored 35mm rangefinder vintage camera paired with a full-grain leather messenger bag.',
    priceUsd: { currencyCode: 'USD', units: 164, nanos: 500000000 },
    categories: ['photography', 'vintage', 'leather'],
  },
];

test.describe('Online Boutique React Storefront E2E Suite', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/products*', async (route) => {
      const url = new URL(route.request().url());
      const category = url.searchParams.get('category');
      if (category) {
        const filtered = CURATED_CATALOG.filter((p) =>
          p.categories.some((c) => c.toLowerCase() === category.toLowerCase())
        );
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          headers: { traceparent: '00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01' },
          body: JSON.stringify(filtered),
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        headers: { traceparent: '00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01' },
        body: JSON.stringify(CURATED_CATALOG),
      });
    });

    await page.route('**/api/cart/*/items', async (route) => {
      const payload = route.request().postDataJSON();
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          userId: 'boutique-session-user',
          items: [{ productId: payload.productId, quantity: payload.quantity }],
        }),
      });
    });

    await page.route('**/api/checkout', async (route) => {
      const payload = route.request().postDataJSON();
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          orderId: 'ORD-E2E-904210',
          shippingTrackingId: 'TRK-E2E-77412',
          userId: payload.userId,
          userCurrency: payload.userCurrency || 'USD',
          itemsCount: 2,
          subtotalConverted: 129.98,
          shippingCostConverted: 8.49,
          totalPaidConverted: 138.47,
          transactionId: 'TXN-E2E-8839201',
          timestampUtc: new Date().toISOString(),
        }),
      });
    });
  });

  test('renders curated products and category badges in the storefront', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'Online Boutique' })).toBeVisible();
    await expect(
      page.getByText('AWS EKS Cloud-Native Microservices Storefront (OTLP Distributed Tracing Enabled)')
    ).toBeVisible();

    await expect(page.getByRole('heading', { name: 'Watch' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Sunglasses' })).toBeVisible();
    await expect(
      page.getByRole('heading', { name: 'Vintage Camera & Leather Bag Bundle' })
    ).toBeVisible();

    await expect(page.getByText('accessories • watches')).toBeVisible();
    await expect(page.getByText('photography • vintage • leather')).toBeVisible();
  });

  test('filters catalog products by category via API contract and updates currency view', async ({
    page,
    request,
  }) => {
    await page.goto('/');

    const currencySelect = page.getByLabel('Currency selector');
    await expect(currencySelect).toHaveValue('USD');
    await expect(page.getByText('USD 109.99')).toBeVisible();

    await currencySelect.selectOption('EUR');
    await expect(page.getByText('EUR 109.99')).toBeVisible();

    const filteredResponse = await page.evaluate(async () => {
      const res = await fetch('/api/products?category=watches');
      return res.json();
    });
    expect(filteredResponse).toHaveLength(1);
    expect(filteredResponse[0].id).toBe('1YMWWN1N4O');
    expect(filteredResponse[0].categories).toContain('watches');
  });

  test('adds items to cart and completes checkout with order confirmation ID', async ({ page }) => {
    await page.goto('/');

    const checkoutButton = page.getByRole('button', { name: /Checkout \(\d+\)/ });
    await expect(checkoutButton).toBeDisabled();
    await expect(checkoutButton).toHaveText('Checkout (0)');

    const addButtons = page.getByRole('button', { name: 'Add to Cart' });
    await addButtons.nth(0).click();
    await expect(checkoutButton).toBeEnabled();
    await expect(checkoutButton).toHaveText('Checkout (1)');

    await addButtons.nth(1).click();
    await expect(checkoutButton).toHaveText('Checkout (2)');

    await checkoutButton.click();

    await expect(page.getByText('Order Confirmed:')).toBeVisible();
    await expect(page.getByText('ORD-E2E-904210')).toBeVisible();
    await expect(page.getByText('TRK-E2E-77412')).toBeVisible();
    await expect(checkoutButton).toHaveText('Checkout (0)');
    await expect(checkoutButton).toBeDisabled();
  });
});
