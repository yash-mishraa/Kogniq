# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: analytics_retry.spec.ts >> Analytics Retry and Progress Pipeline >> recovers from transient network failure to deliver progress
- Location: tests\analytics_retry.spec.ts:5:7

# Error details

```
TimeoutError: locator.click: Timeout 120000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Enter Kogniq' })

```

# Page snapshot

```yaml
- generic [active] [ref=e1]: Internal Server Error
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Analytics Retry and Progress Pipeline', () => {
  4  |   test.setTimeout(180000); // Wait for document processing
  5  |   test('recovers from transient network failure to deliver progress', async ({ page }) => {
  6  |     let batchRequestCount = 0;
  7  |     
  8  |     // Intercept analytics batch requests
  9  |     await page.route('**/api/v1/analytics/events/batch', async route => {
  10 |       batchRequestCount++;
  11 |       
  12 |       // Simulate transient failure on the very first batch
  13 |       if (batchRequestCount === 1) {
  14 |         await route.fulfill({
  15 |           status: 500,
  16 |           contentType: 'application/json',
  17 |           body: JSON.stringify({ detail: 'Internal Server Error' })
  18 |         });
  19 |         return;
  20 |       }
  21 |       
  22 |       // Allow subsequent retries to succeed
  23 |       await route.continue();
  24 |     });
  25 | 
  26 |     // Login
  27 |     await page.goto('/');
> 28 |     await page.getByRole('button', { name: 'Enter Kogniq' }).click();
     |                                                              ^ TimeoutError: locator.click: Timeout 120000ms exceeded.
  29 |     await page.getByPlaceholder('email').fill('admin@kogniq.ai');
  30 |     await page.getByPlaceholder('password').fill('password');
  31 |     await page.getByRole('button', { name: 'Continue.' }).click();
  32 |     await expect(page.getByText('Documents', { exact: true }).first()).toBeVisible({ timeout: 10000 });
  33 |     await page.getByText('Documents', { exact: true }).first().click();
  34 |     
  35 |     // Upload a document so we have a resource
  36 |     await page.setInputFiles('input[type="file"]', {
  37 |       name: 'analytics_test.txt',
  38 |       mimeType: 'text/plain',
  39 |       buffer: Buffer.from('This is a test document to verify the analytics retry mechanism.')
  40 |     });
  41 | 
  42 |     await expect(page.getByText('Ready').first()).toBeVisible({ timeout: 90000 });
  43 | 
  44 |     // Click the Workspace Header to go back to the Intention wheel
  45 |     await page.getByRole('button', { name: 'Choose another environment' }).click();
  46 | 
  47 |     // Select Learning Hub in the Intention wheel
  48 |     const learningHubOption = page.getByRole('option', { name: 'Learning Hub' });
  49 |     await learningHubOption.click(); // Focuses it
  50 |     await learningHubOption.click(); // Selects it
  51 | 
  52 |     // Click the uploaded resource to view its chunks (any resource in the list)
  53 |     const resourceBtn = page.locator('ul > li > button').first();
  54 |     
  55 |     // Wait for it to be visible before clicking
  56 |     await expect(resourceBtn).toBeVisible({ timeout: 60000 });
  57 |     await resourceBtn.click();
  58 | 
  59 |     // Wait for the chunk to be visible
  60 |     const chunk = page.getByText('This is a test document to verify the analytics retry mechanism.').first();
  61 |     await expect(chunk).toBeVisible({ timeout: 15000 });
  62 | 
  63 |     // Scroll the chunk into view to trigger the IntersectionObserver (TrackedChunk)
  64 |     await chunk.scrollIntoViewIfNeeded();
  65 | 
  66 |     await expect(async () => {
  67 |       expect(batchRequestCount).toBeGreaterThanOrEqual(2);
  68 |     }).toPass({ timeout: 30000 });
  69 |   });
  70 | });
  71 | 
```