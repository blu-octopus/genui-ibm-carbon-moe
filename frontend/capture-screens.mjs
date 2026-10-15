import { chromium } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(__dirname, '..', 'data', 'screenshots');

const sources = [
  ['ground_truth', 'prompt_01_ground_truth.png'],
  ['moe_small', 'prompt_01_moe_mistral_small.png'],
  ['baseline_large', 'prompt_01_baseline_mistral_large.png'],
];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

for (const [source, file] of sources) {
  const url = `http://localhost:3000/?source=${source}`;
  console.log('capture', url);
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('[data-testid="carbon-canvas"], [role="alert"]', {
    timeout: 30000,
  });
  await page.waitForTimeout(1500);
  const dest = path.join(out, file);
  await page.screenshot({ path: dest, fullPage: true });
  console.log('wrote', dest);
}

await browser.close();
