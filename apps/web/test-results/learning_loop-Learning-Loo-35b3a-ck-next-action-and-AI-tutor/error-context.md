# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: learning_loop.spec.ts >> Learning Loop >> Upload document, wait for processing, check next action and AI tutor
- Location: tests\learning_loop.spec.ts:5:7

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
  3  | test.describe('Learning Loop', () => {
  4  |   test.setTimeout(180000);
  5  |   test('Upload document, wait for processing, check next action and AI tutor', async ({ page }) => {
  6  |     page.on('console', msg => console.log('BROWSER CONSOLE:', msg.text()));
  7  |     page.on('request', request => console.log('>>', request.method(), request.url()));
  8  |     page.on('response', response => console.log('<<', response.status(), response.url()));
  9  |     await page.goto('http://localhost:3000');
> 10 |     await page.getByRole('button', { name: 'Enter Kogniq' }).click();
     |                                                              ^ TimeoutError: locator.click: Timeout 120000ms exceeded.
  11 |     await page.getByPlaceholder('email').fill('admin@kogniq.ai');
  12 |     await page.getByPlaceholder('password').fill('password');
  13 |     await page.getByRole('button', { name: 'Continue.' }).click();
  14 |     await page.waitForTimeout(3000);
  15 |     await page.getByText('Documents', { exact: true }).first().click();
  16 | 
  17 |     await page.setInputFiles('input[type="file"]', {
  18 |       name: 'test_document.txt',
  19 |       mimeType: 'text/plain',
  20 |       buffer: Buffer.from('# Transformer architecture\n\nThis is a test document explaining the Transformer architecture. The Transformer uses Multi-Head Attention to focus on different parts of the input sequence simultaneously.')
  21 |     });
  22 |     // The document starts as a job with the filename. When processing completes, 
  23 |     // it becomes a document with the extracted title. Wait for this transition.
  24 |     // The lifecycle stages always show "Ready" greyed out, so we can't match on text alone.
  25 |     // Instead, wait for the title to switch from the filename to the extracted title.
  26 |     await expect(page.getByText(/Transformer architecture/i).first()).toBeVisible({ timeout: 90000 });
  27 |     await page.screenshot({ path: 'test-results/debug-after-ready.png' });
  28 |     await page.getByText(/Transformer architecture/i).first().click({ force: true });
  29 |     
  30 |     await expect(page.getByText('Document successfully processed and stored.').first()).toBeVisible({ timeout: 15000 });
  31 |     await expect(page.getByText('Recommended Next Action')).toBeVisible({ timeout: 15000 });
  32 |     await page.screenshot({ path: 'test-results/debug-next-action.png' });
  33 |     await page.getByRole('button', { name: 'Start' }).click();
  34 |     await expect(page.getByText('Learning Material')).toBeVisible({ timeout: 15000 });
  35 |     await page.getByRole('button', { name: /Review Notes/i }).click();
  36 |     await page.getByRole('button', { name: /Start Recall/i }).click();
  37 |     await page.getByRole('button', { name: /Test Understanding/i }).click();
  38 |     await page.getByRole('button', { name: 'Finish Study Session' }).click();
  39 |     await page.getByRole('button', { name: 'Return to Workspace' }).click();
  40 |     
  41 |     // State is reset when DocumentsEnvironment remounts, so we must click the document again
  42 |     await expect(page.getByText(/Transformer architecture/i).first()).toBeVisible({ timeout: 15000 });
  43 |     await page.getByText(/Transformer architecture/i).first().click({ force: true });
  44 |     
  45 |     // We expect the backend to return 'quiz' as the next action, which enables the Start button
  46 |     await page.getByRole('button', { name: 'Start' }).click();
  47 |     
  48 |     // In Phase 2 Quiz UI, answer options are radio buttons
  49 |     await page.getByRole('radio').first().click({ timeout: 30000 });
  50 |     await page.getByRole('button', { name: 'Check answer' }).click();
  51 |     
  52 |     // We expect an explanation to appear
  53 |     await expect(page.locator('[role="status"]')).toBeVisible({ timeout: 5000 });
  54 |   });
  55 | });
  56 | 
```