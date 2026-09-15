'use strict';

const express = require('express');
const puppeteer = require('puppeteer');

const origin = new URL(process.env.APP_ORIGIN).origin;
const username = process.env.ADMIN_USERNAME || 'admin';
const password = process.env.ADMIN_PASSWORD;
const timeout = Number(process.env.NAVIGATION_TIMEOUT_MS || 15000);
const dwell = Number(process.env.BOT_DWELL_MS || 2000);

const app = express();
let busy = false;

app.use(express.json({ limit: '4kb' }));
app.get('/health', (_request, response) => response.json({ status: 'ok' }));

app.post('/visit', async (request, response) => {
  if (busy) return response.status(429).json({ error: 'Bot is busy.' });

  let target;
  try {
    target = new URL(request.body?.url ?? request.body?.uri, origin);
    if (!['http:', 'https:'].includes(target.protocol)) throw new Error();
  } catch {
    return response.status(400).json({ error: 'Invalid URL.' });
  }

  busy = true;
  let browser;

  try {
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-dev-shm-usage', '--ignore-certificate-errors'],
    });

    const login = await browser.newPage();
    await login.goto(`${origin}/login`, { waitUntil: 'domcontentloaded', timeout });
    await login.type('[name="username"]', username);
    await login.type('[name="password"]', password);
    await login.setExtraHTTPHeaders({ 'Sec-Fetch-User': '?1' });
    await Promise.all([
      login.waitForNavigation({ waitUntil: 'domcontentloaded', timeout }),
      login.click('button[type="submit"]'),
    ]);

    if (new URL(login.url()).pathname !== '/dashboard') throw new Error('Login failed.');
    await login.close();

    const page = await browser.newPage();
    await page.goto(target.href, { waitUntil: 'domcontentloaded', timeout });
    await new Promise((resolve) => setTimeout(resolve, dwell));
    response.json({ success: true });
  } catch (error) {
    console.error(error.message);
    response.status(502).json({ error: 'Visit failed.' });
  } finally {
    await browser?.close().catch(() => {});
    busy = false;
  }
});

app.use((_error, _request, response, _next) => {
  response.status(400).json({ error: 'Bad request.' });
});

app.listen(process.env.BOT_PORT || 3000, '0.0.0.0');
