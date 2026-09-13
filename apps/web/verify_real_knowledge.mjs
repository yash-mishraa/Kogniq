import { chromium, request } from 'playwright';

async function runTest() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  page.on('console', msg => console.log('BROWSER CONSOLE:', msg.text()));
  page.on('request', req => console.log('REQUEST:', req.method(), req.url()));
  page.on('response', async res => {
      console.log('RESPONSE:', res.status(), res.url());
      if (res.url().includes('/api/v1/knowledge/') && res.status() === 200) {
          console.log('BODY:', await res.text());
      }
  });

  try {
    console.log("0. REGISTER TEST USER ON REAL BACKEND");
    const apiContext = await request.newContext({ baseURL: 'http://localhost:8000' });
    const registerResponse = await apiContext.post('/api/v1/auth/register', {
      data: { email: "test@example.com", password: "password", display_name: "Playwright E2E" }
    });
    console.log("Register response:", registerResponse.status(), await registerResponse.text());
    
    // MOCK DOCUMENTS ENDPOINT
    await page.route('**/api/v1/documents', route => {
      console.log('INTERCEPTED /api/v1/documents');
      route.fulfill({
        status: 200,
        json: [{ id: "79175d83-077e-43b0-81a4-b1ceea1f02f8", title: "Test Document", source: "mock", status: "Ready", importDate: new Date().toISOString() }]
      });
    });

    console.log("1. START THE REAL APPLICATION");
    await page.goto('http://localhost:3000');
    
    console.log("2. COMPLETE AUTHENTICATION");
    await page.waitForSelector('.kogniq-word');
    await page.click('.kogniq-word');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    
    console.log("3. SELECT DOCUMENTS ENVIRONMENT AND A REAL DOCUMENT");
    await page.waitForSelector('button[aria-label="Choose another environment"]', { timeout: 10000 }).catch(async () => {
        // We arrive at Intention screen
        await page.waitForSelector('div[role="listbox"]');
        await page.waitForTimeout(500);
        
        await page.evaluate(() => {
            const docBtn = Array.from(document.querySelectorAll('button[role="option"]')).find(b => b.textContent === 'Documents');
            if (docBtn) docBtn.click();
        });
        await page.waitForTimeout(500);
        await page.evaluate(() => {
            const docBtn = Array.from(document.querySelectorAll('button[role="option"]')).find(b => b.textContent === 'Documents');
            if (docBtn) docBtn.click();
        });
        
        await page.waitForSelector('button[aria-label="Choose another environment"]', { timeout: 10000 });
    });
    
    // Wait for documents to load
    await page.waitForTimeout(2000);

    await page.waitForSelector('text=Test Document', { timeout: 5000 });
    await page.click('text=Test Document');
    await page.waitForTimeout(1000); 

    console.log("4. OPEN KNOWLEDGE GRAPH WORKSPACE");
    await page.click('button[aria-label="Choose another environment"]');
    await page.waitForSelector('div[role="listbox"]');
    await page.waitForTimeout(500);
    
    await page.evaluate(() => {
        const kgBtn = Array.from(document.querySelectorAll('button[role="option"]')).find(b => b.textContent === 'Knowledge');
        if (kgBtn) kgBtn.click();
    });
    await page.waitForTimeout(500);
    await page.evaluate(() => {
        const kgBtn = Array.from(document.querySelectorAll('button[role="option"]')).find(b => b.textContent === 'Knowledge');
        if (kgBtn) kgBtn.click();
    });

    console.log("5. CONFIRM KNOWLEDGE GRAPH RENDERS");
    // Check if the concept text rendered
    await page.waitForSelector('text=Transformer', { timeout: 10000 });
    const transformerNode = await page.$('text=Transformer');
    if (transformerNode) {
        console.log("Found Transformer node in the graph.");
        await transformerNode.click();
    }
    
    console.log("All flows complete! SUCCESS");
  } catch (error) {
    console.error("Test failed:", error);
    process.exit(1);
  } finally {
    await browser.close();
  }
}
runTest();
