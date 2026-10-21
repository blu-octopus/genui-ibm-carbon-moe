import { chromium } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(__dirname, '..', 'data', 'screenshots');

const PROMPTS = [
  'prompt_01_enterprise_table',
  'prompt_02_registration_form',
  'prompt_03_kpi_grid',
  'prompt_04_destructive_modal',
  'prompt_05_global_shell',
];

const SOURCES = ['ground_truth', 'moe', 'baseline', 'design_md'];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

for (const prompt of PROMPTS) {
  for (const source of SOURCES) {
    const url = `http://localhost:3000/?prompt=${prompt}&source=${source}`;
    console.log('capture', url);
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    try {
      await page.waitForSelector('[data-testid="carbon-canvas"], [role="alert"]', {
        timeout: 30000,
      });
    } catch {
      console.warn('timeout waiting for canvas/alert', prompt, source);
    }
    await page.waitForTimeout(800);
    const dest = path.join(out, `${prompt}__${source}.png`);
    await page.screenshot({ path: dest, fullPage: true });
    console.log('wrote', dest);
  }
}

await browser.close();
