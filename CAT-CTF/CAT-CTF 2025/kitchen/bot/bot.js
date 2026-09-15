const express = require('express');
const puppeteer = require('puppeteer');
const bodyParser = require('body-parser');

const app = express();
const PORT = 3000;

app.use(bodyParser.json());

app.post('/visit', async (req, res) => {
  const { note, username, password } = req.body;

  if (!note || !username || !password) {
    return res.status(400).json({ error: 'Missing username, or password' });
  }

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-dev-shm-usage']
  });

  const page = await browser.newPage();

  try {
    await page.goto('http://app:5000/login', { waitUntil: 'networkidle2' });

    await page.type('#user', username);
    await page.type('#password', password);

    await Promise.all([
      page.keyboard.press('Enter'),
      page.waitForNavigation({ waitUntil: 'networkidle2' }),
    ]);
    var url =`http://app:5000/notes?username=${note}`

    await page.goto(url, { waitUntil: 'networkidle2' });

    await new Promise(resolve => setTimeout(resolve, 2000));

    res.json({ success: true, message: 'Visited successfully' });
  } catch (err) {
    console.error('Error:', err);
    res.status(500).json({ error: 'Automation failed', details: err.message });
  } finally {
    await browser.close();
  }
});

app.listen(PORT,"0.0.0.0", () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
