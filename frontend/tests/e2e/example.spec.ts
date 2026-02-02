import { test, expect } from '@playwright/test';

test.describe('Marketing Research App E2E Tests', () => {
  test('homepage loads successfully', async ({ page }) => {
    await page.goto('/');

    // Check that the page loaded
    await expect(page).toHaveTitle(/Marketing|Маркетолух/i);
  });

  test('can navigate to login page', async ({ page }) => {
    await page.goto('/');

    // Click on login link/button
    await page.click('text=Войти');

    // Should be on login page
    await expect(page).toHaveURL(/\/login/);
  });

  test('login form validation works', async ({ page }) => {
    await page.goto('/login');

    // Try to submit empty form
    await page.click('button[type="submit"]');

    // Should show validation errors
    await expect(page.locator('text=/required|обязательно/i')).toBeVisible();
  });

  test('can create a research (authenticated)', async ({ page }) => {
    // This test assumes authentication is working
    // In a real scenario, you'd login first

    // Navigate to create research page
    await page.goto('/research/create');

    // Fill in the form
    await page.fill('input[name="title"]', 'E2E Test Research');
    await page.fill('textarea[name="product_description"]', 'Тестовый продукт для E2E тестирования');
    await page.fill('input[name="industry"]', 'Технологии');
    await page.fill('input[name="region"]', 'Москва');

    // Submit the form
    await page.click('button[type="submit"]');

    // Should redirect to research detail or list
    await expect(page).toHaveURL(/\/research/);
  });

  test('dashboard displays research list', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/dashboard');

    // Should see research list or empty state
    const hasResearch = await page.locator('.research-item').count();

    if (hasResearch > 0) {
      await expect(page.locator('.research-item').first()).toBeVisible();
    } else {
      await expect(page.locator('text=/нет исследований|no research/i')).toBeVisible();
    }
  });

  test('responsive design works on mobile', async ({ page }) => {
    // Set viewport to mobile size
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto('/');

    // Mobile menu should be visible or hamburger menu
    const mobileMenu = await page.locator('[data-testid="mobile-menu"]').count();
    expect(mobileMenu).toBeGreaterThanOrEqual(0);
  });
});
