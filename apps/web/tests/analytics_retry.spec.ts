import { test, expect } from '@playwright/test';

test.describe('Analytics Retry and Progress Pipeline', () => {
  test.setTimeout(180000); // Wait for document processing
  test('recovers from transient network failure to deliver progress', async ({ page }) => {
    let batchRequestCount = 0;
    
    // Intercept analytics batch requests
    await page.route('**/api/v1/analytics/events/batch', async route => {
      batchRequestCount++;
      
      // Simulate transient failure on the very first batch
      if (batchRequestCount === 1) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Internal Server Error' })
        });
        return;
      }
      
      // Allow subsequent retries to succeed
      await route.continue();
    });

    // Login
    await page.goto('/');
    await page.getByRole('button', { name: 'Enter Kogniq' }).click();
    await page.getByPlaceholder('email').fill('admin@kogniq.ai');
    await page.getByPlaceholder('password').fill('password');
    await page.getByRole('button', { name: 'Continue.' }).click();
    await expect(page.getByText('Documents', { exact: true }).first()).toBeVisible({ timeout: 10000 });
    await page.getByText('Documents', { exact: true }).first().click();
    
    // Upload a document so we have a resource
    await page.setInputFiles('input[type="file"]', {
      name: 'analytics_test.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('This is a test document to verify the analytics retry mechanism.')
    });

    await expect(page.getByText('Ready').first()).toBeVisible({ timeout: 90000 });

    // Click the Workspace Header to go back to the Intention wheel
    await page.getByRole('button', { name: 'Choose another environment' }).click();

    // Select Learning Hub in the Intention wheel
    const learningHubOption = page.getByRole('option', { name: 'Learning Hub' });
    await learningHubOption.click(); // Focuses it
    await learningHubOption.click(); // Selects it

    // Click the uploaded resource to view its chunks (any resource in the list)
    const resourceBtn = page.locator('ul > li > button').first();
    
    // Wait for it to be visible before clicking
    await expect(resourceBtn).toBeVisible({ timeout: 60000 });
    await resourceBtn.click();

    // Wait for the chunk to be visible
    const chunk = page.getByText('This is a test document to verify the analytics retry mechanism.').first();
    await expect(chunk).toBeVisible({ timeout: 15000 });

    // Scroll the chunk into view to trigger the IntersectionObserver (TrackedChunk)
    await chunk.scrollIntoViewIfNeeded();

    await expect(async () => {
      expect(batchRequestCount).toBeGreaterThanOrEqual(2);
    }).toPass({ timeout: 30000 });
  });
});
