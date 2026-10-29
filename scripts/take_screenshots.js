const { chromium } = require('../apps/web/node_modules/playwright');
const path = require('path');
const fs = require('fs');

async function main() {
  const artifactDir = '/Users/yashmishra14/.gemini/antigravity/brain/7ea17bc6-aabb-43da-b10a-e0639db6198b/screenshots';
  const docsDir = path.resolve(__dirname, '../docs/screenshots');

  fs.mkdirSync(artifactDir, { recursive: true });
  fs.mkdirSync(docsDir, { recursive: true });

  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2,
  });

  // Set the session cookie for both 127.0.0.1 and localhost
  await context.addCookies([
    {
      name: 'kogniq_session',
      value: 'cdbe62a0-9a1e-4cb5-a909-9e488216f2ff',
      domain: 'localhost',
      path: '/',
      httpOnly: true,
      sameSite: 'Lax',
    },
    {
      name: 'kogniq_session',
      value: 'cdbe62a0-9a1e-4cb5-a909-9e488216f2ff',
      domain: '127.0.0.1',
      path: '/',
      httpOnly: true,
      sameSite: 'Lax',
    },
  ]);

  const page = await context.newPage();

  console.log('Navigating to http://localhost:3000...');
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });

  // If entry experience (login) is shown, fill in credentials
  const emailInput = await page.$('input[type="email"]');
  if (emailInput) {
    console.log('Login form detected, logging in...');
    await page.fill('input[type="email"]', 'demo@kogniq.ai');
    await page.fill('input[type="password"]', 'Password123!');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1500);
  }

  // Helper to save screenshot to both locations
  async function capture(name) {
    const p1 = path.join(artifactDir, `${name}.png`);
    const p2 = path.join(docsDir, `${name}.png`);
    await page.screenshot({ path: p1, fullPage: false });
    fs.copyFileSync(p1, p2);
    console.log(`Saved screenshot: ${name}.png`);
  }

  // 1. Home
  await page.waitForTimeout(1000);
  await capture('home');

  // 2. Documents
  console.log('Navigating to Documents...');
  const docsBtn = page.getByRole('button', { name: 'My Documents' }).first();
  if (await docsBtn.count()) {
    await docsBtn.click();
    await page.waitForTimeout(1200);
    await capture('documents');
  }

  // 3. Ask Questions
  console.log('Navigating to Ask Questions...');
  const askBtn = page.getByRole('button', { name: 'Ask Questions' }).first();
  if (await askBtn.count()) {
    await askBtn.click();
    await page.waitForTimeout(1200);
    await capture('ask');
  }

  // 4. Flashcards
  console.log('Navigating to Flashcards...');
  const flashBtn = page.getByRole('button', { name: 'Flashcards' }).first();
  if (await flashBtn.count()) {
    await flashBtn.click();
    await page.waitForTimeout(1200);
    await capture('flashcards');
  }

  // 5. Quizzes
  console.log('Navigating to Quizzes...');
  const quizBtn = page.getByRole('button', { name: 'Quizzes' }).first();
  if (await quizBtn.count()) {
    await quizBtn.click();
    await page.waitForTimeout(1200);
    await capture('quizzes');
  }

  // 6. Knowledge Graph
  console.log('Navigating to Knowledge Graph...');
  const kgBtn = page.getByRole('button', { name: 'Knowledge Graph' }).first();
  if (await kgBtn.count()) {
    await kgBtn.click();
    await page.waitForTimeout(1500);
    await capture('knowledge_graph');
  }

  // 7. Engineering Console
  console.log('Navigating to Engineering Console...');
  const engBtn = page.getByRole('button', { name: 'Engineering Console' }).first();
  if (await engBtn.count()) {
    await engBtn.click();
    await page.waitForTimeout(1200);
    await capture('engineering_console');
  }

  await browser.close();
  console.log('All screenshots captured successfully!');
}

main().catch(err => {
  console.error('Screenshot error:', err);
  process.exit(1);
});
