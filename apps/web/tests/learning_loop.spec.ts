import { test, expect } from '@playwright/test';

test.describe('Learning Loop', () => {
  test.setTimeout(180000);
  test('Upload document, wait for processing, check next action and AI tutor', async ({ page }) => {
    page.on('console', msg => console.log('BROWSER CONSOLE:', msg.text()));
    page.on('request', request => console.log('>>', request.method(), request.url()));
    page.on('response', response => console.log('<<', response.status(), response.url()));
    await page.goto('http://localhost:3000');
    await page.getByRole('button', { name: 'Enter Kogniq' }).click();
    await page.getByPlaceholder('email').fill('admin@kogniq.ai');
    await page.getByPlaceholder('password').fill('password');
    await page.getByRole('button', { name: 'Continue.' }).click();
    await page.waitForTimeout(3000);
    await page.getByText('Documents', { exact: true }).first().click();

    await page.setInputFiles('input[type="file"]', {
      name: 'test_document.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('# Transformer architecture\n\nThis is a test document explaining the Transformer architecture. The Transformer uses Multi-Head Attention to focus on different parts of the input sequence simultaneously.')
    });
    // The document starts as a job with the filename. When processing completes, 
    // it becomes a document with the extracted title. Wait for this transition.
    // The lifecycle stages always show "Ready" greyed out, so we can't match on text alone.
    // Instead, wait for the title to switch from the filename to the extracted title.
    await expect(page.getByText(/Transformer architecture/i).first()).toBeVisible({ timeout: 90000 });
    await page.screenshot({ path: 'test-results/debug-after-ready.png' });
    await page.getByText(/Transformer architecture/i).first().click({ force: true });
    
    await expect(page.getByText('Document successfully processed and stored.').first()).toBeVisible({ timeout: 15000 });
    await expect(page.getByText('Recommended Next Action')).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'test-results/debug-next-action.png' });
    await page.getByRole('button', { name: 'Start' }).click();
    await expect(page.getByText('Learning Material')).toBeVisible({ timeout: 15000 });
    await page.getByRole('button', { name: /Review Notes/i }).click();
    await page.getByRole('button', { name: /Start Recall/i }).click();
    await page.getByRole('button', { name: /Test Understanding/i }).click();
    await page.getByRole('button', { name: 'Finish Study Session' }).click();
    await page.getByRole('button', { name: 'Return to Workspace' }).click();
    
    // State is reset when DocumentsEnvironment remounts, so we must click the document again
    await expect(page.getByText(/Transformer architecture/i).first()).toBeVisible({ timeout: 15000 });
    await page.getByText(/Transformer architecture/i).first().click({ force: true });
    
    // We expect the backend to return 'quiz' as the next action, which enables the Start button
    await page.getByRole('button', { name: 'Start' }).click();
    
    // In Phase 2 Quiz UI, answer options are radio buttons
    await page.getByRole('radio').first().click({ timeout: 30000 });
    await page.getByRole('button', { name: 'Check answer' }).click();
    
    // We expect an explanation to appear
    await expect(page.locator('[role="status"]')).toBeVisible({ timeout: 5000 });
  });
});
