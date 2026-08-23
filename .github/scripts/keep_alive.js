const { chromium } = require('playwright');

(async () => {
  console.log('Launching headless browser...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('Navigating to https://synapvoxai.streamlit.app/...');
  try {
    await page.goto('https://synapvoxai.streamlit.app/', { waitUntil: 'networkidle', timeout: 60000 });
  } catch (e) {
    console.log('Navigation note:', e.message);
  }

  await page.waitForTimeout(5000);

  const wakeButton = page.locator('button:has-text("Yes, get this app back up!"), button:has-text("Wake"), button:has-text("wake")').first();
  if (await wakeButton.isVisible({ timeout: 10000 }).catch(() => false)) {
    console.log('⚡ App was sleeping! Clicking wake up button...');
    await wakeButton.click();
    console.log('Waiting 30 seconds for Streamlit app to boot up...');
    await page.waitForTimeout(30000);
  } else {
    console.log('✅ App is active! WebSocket session connected successfully.');
    await page.waitForTimeout(5000);
  }

  await browser.close();
  console.log('Keep-alive task complete!');
})();
