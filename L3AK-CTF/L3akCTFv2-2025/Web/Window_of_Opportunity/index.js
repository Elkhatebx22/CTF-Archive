const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const jwt = require('jsonwebtoken');
const puppeteer = require("puppeteer");
const cors = require('cors');
const crypto = require('crypto');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const app = express();
const HOST = "127.0.0.1";
const PORT = 3000;

const REMOTE_IP = "34.134.162.213";
const REMOTE_PORT = 17001

const FLAG = process.env.FLAG || "L3AK{t3mp_flag}";
const COOKIE_SECRET = process.env.COOKIE_SECRET || "1234";

const csrfTokens = new Map();

const limiter = rateLimit.rateLimit({
  windowMs: 5 * 60 * 1000,
  limit: 10,
  legacyHeaders: false
});

app.use(cookieParser());
app.use(cors({
  origin: ["http://127.0.0.1:3000", `http://${REMOTE_IP}:${REMOTE_PORT}`],
  credentials: true,
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-CSRF-Token']
}));
app.use('/visit_url', limiter);

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function generateCSRFToken() {
  const token = crypto.randomBytes(32).toString('hex');
  const timestamp = Date.now();
  csrfTokens.set(token, timestamp);

  const fiveMinutesAgo = timestamp - (5 * 60 * 1000);
  for (const [storedToken, storedTime] of csrfTokens.entries()) {
    if (storedTime < fiveMinutesAgo) {
      csrfTokens.delete(storedToken);
    }
  }

  // So infra doesn't implode hopefully
  const MAX_TOKENS = 2000;
  if (csrfTokens.size > MAX_TOKENS) {
    csrfTokens.clear();
  }

  return token;
}

function validateCSRFToken(token) {
  if (!token || !csrfTokens.has(token)) {
    return false;
  }
  
  const timestamp = csrfTokens.get(token);
  const fiveMinutesAgo = Date.now() - (5 * 60 * 1000);
  
  if (timestamp < fiveMinutesAgo) {
    csrfTokens.delete(token);
    return false;
  }
  
  return true;
}

function csrfProtection(req, res, next) {
  const origin = req.headers.origin;
  const allowedOrigins = [ // Requests from these origins are probably safe
    `http://${HOST}:${PORT}`,
    `http://${REMOTE_IP}:${REMOTE_PORT}`
  ] 

  if (req.path === '/') {
    return next();
  }

  if (req.path === '/get_flag') {
    if(!req.headers.origin) {
      return next();
    }
  }
    
  if (!origin || !allowedOrigins.includes(origin)) {
    return res.status(403).json({ 
      error: 'Cross-origin request blocked',
      message: 'Origin not allowed'
    });
  }

  let csrfToken = null;
  
  csrfToken = req.headers['x-csrf-token'];
  
  if (!csrfToken && req.headers.authorization) {
    const authHeader = req.headers.authorization;
    if (authHeader.startsWith('Bearer ')) {
      csrfToken = authHeader.substring(7);
    }
  }
  
  if (!csrfToken && req.body && req.body.csrf_token) {
    csrfToken = req.body.csrf_token;
  }
  
  if (!csrfToken && req.query.csrf_token) {
    csrfToken = req.query.csrf_token;
  }
  
  if (!validateCSRFToken(csrfToken)) {
    return res.status(403).json({ 
      error: 'CSRF token validation failed',
      message: 'Invalid, missing, or expired CSRF token'
    });
  }
  
  csrfTokens.delete(csrfToken);
  next();
}

app.get('/', (req, res) => {
  const csrfToken = generateCSRFToken();
  
  res.cookie('csrf_token', csrfToken, {
    httpOnly: false,
    sameSite: 'Strict',
    secure: false,
    maxAge: 5 * 60 * 1000,
  });

  res.send(`
    <!DOCTYPE html>
    <!-- Doors...Windows...The flag is waiting --!>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <script src="https://cdn.tailwindcss.com"></script>
      <title>Window of Opportunity</title>
      <meta name="csrf-token" content="${csrfToken}">
    </head>
    <body class="min-h-screen flex items-center justify-center bg-cover bg-center" style="background-image: url('/bg.jpg');">
      <audio autoplay loop hidden>
        <source src="/music.mp3" type="audio/mpeg">
        Your browser does not support the audio element.
      </audio>
      <div class="bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-xl w-full max-w-md text-center">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">Window of Opportunity</h1>
        <p class="text-gray-600 mb-6 text-sm">A curious admin will open your door<br/>what secrets might it contain?</p>
        
        <form id="urlForm" class="space-y-4">
          <input 
            type="url" 
            name="url"
            id="urlInput"
            placeholder="https://l3ak.team" 
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" 
            required
          />
          <input type="hidden" name="csrf_token" id="csrfTokenField" value="${csrfToken}">
          <button 
            type="submit" 
            class="w-full bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-200"
          >
            Submit
          </button>
        </form>
        <div id="response" class="mt-4 text-sm text-gray-700"></div>
      </div>

      <script>
        function getCookie(name) {
          const value = "; " + document.cookie;
          const parts = value.split("; " + name + "=");
          if (parts.length === 2) return parts.pop().split(";").shift();
        }

        function getCSRFToken() {
          const metaToken = document.querySelector('meta[name="csrf-token"]');
          if (metaToken) return metaToken.getAttribute('content');
          
          const cookieToken = getCookie('csrf_token');
          if (cookieToken) return cookieToken;
          
          const hiddenField = document.getElementById('csrfTokenField');
          if (hiddenField) return hiddenField.value;
          
          return null;
        }

        document.getElementById('urlForm').addEventListener('submit', async function(e) {
          e.preventDefault();

          const urlInput = document.getElementById('urlInput').value;
          const responseDiv = document.getElementById('response');
          const csrfToken = getCSRFToken();

          if (!csrfToken) {
            responseDiv.textContent = 'Error: CSRF token not found';
            return;
          }

          responseDiv.textContent = 'Submitting...';

          try {
            const headers = {
              'Content-Type': 'application/x-www-form-urlencoded',
              'X-CSRF-Token': csrfToken,
              'Authorization': 'Bearer ' + csrfToken
            };

            const body = new URLSearchParams({ 
              url: urlInput,
              csrf_token: csrfToken
            });

            const res = await fetch('/visit_url', {
              method: 'POST',
              headers: headers,
              body: body,
              credentials: 'include'
            });

            if (res.ok) {
              window.location.href = window.location.pathname + '?visited=true';
            } else {
              window.location.href = window.location.pathname + '?visited=false';
            }
          } catch (err) {
            responseDiv.textContent = 'Request failed: ' + err.message;
          }
        });
      </script>

      <script>
        const params = new URLSearchParams(window.location.search);
        const visited = params.get('visited');

        if (visited === 'true') {
          document.getElementById('response').textContent = '✅ Admin has visited your link.';
        } else if (visited === 'false') {
          document.getElementById('response').textContent = '❌ Admin could not visit your link.';
        }
    </script>
    </body>
    </html>
  `);
});

app.get('/get_flag', csrfProtection, (req, res) => {
  const token = req.cookies.token;

  if (!token) {
    return res.status(401).json({ error: 'Unauthorized: No token provided.' });
  }

  try {
    const decoded = jwt.verify(token, COOKIE_SECRET);
    if (decoded.admin === true) {
      return res.json({ flag: FLAG, message: 'You opened the right door!' });
    } else {
      return res.status(403).json({ error: 'Forbidden: You are not admin (-_-)' });
    }
  } catch (err) {
    return res.status(401).json({ error: 'Unauthorized: Invalid token.' });
  }
});

app.post('/visit_url', csrfProtection, (req, res) => {
  const { url } = req.body;

  if (!url || typeof url !== 'string') {
    return res.status(400).json({ error: 'Bad Request: URL is required.' });
  }

  try {
    new URL(url);
    visit(url)
      .then(() => {
        return res.json({ message: 'URL visited successfully!', url: url });
      })
      .catch((e) => {
        return res.status(400).json({ error: 'Server Error: Failed to visit URL', details: e.message });
      })
  } catch (e) {
    return res.status(400).json({ error: 'Bad Request: Invalid URL format.' });
  }
});

app.get('/csrf-token', csrfProtection, (req, res) => {
  const token = generateCSRFToken();
  res.cookie('csrf_token', token, {
    httpOnly: false,
    sameSite: 'Strict',
    secure: false,
    maxAge: 5 * 60 * 1000
  });
  res.json({ csrf_token: token });
});

let browser;

(async () => {
  const args = [
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-setuid-sandbox",
    "--no-sandbox",
    "--no-zygote",
    "--disable-webgl",
    "--disable-accelerated-2d-canvas",
    "--disable-software-rasterizer",
    "--disable-features=IsolateOrigins,site-per-process",
    "--disable-web-security",
    "--js-flags=--jitless --no-expose-wasm",
    "--disable-extensions",
    "--disable-popup-blocking",
    "--disable-sync",
    "--disable-translate",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-client-side-phishing-detection",
    "--disable-default-apps",
    "--disable-hang-monitor",
    "--disable-prompt-on-repost",
    "--metrics-recording-only",
    "--mute-audio",
    "--no-first-run",
    "--safebrowsing-disable-auto-update",
    "--disable-site-isolation-trials",
    "--incognito"
  ];

  browser = await puppeteer.launch({ headless: true, args });
})();

async function visit(url) {
  console.log(url)
  const context = await browser.createBrowserContext();
  const page = await context.newPage();

  const token = jwt.sign({ admin: true }, COOKIE_SECRET);

  await page.setRequestInterception(true);
  await page.setCookie({
    name: "token",
    value: token,
    domain: REMOTE_IP,
    httpOnly: true,
    secure: false,
    sameSite: "Lax"
  });

  page.on('request', req => { // Some extra csrf measures yk
    if(req.resourceType() == 'script') {
      req.abort();
    } else {
      req.continue();
    }
  })

  await page.goto(`http://${REMOTE_IP}:${REMOTE_PORT}/`, { waitUntil: "networkidle2" });

  await sleep(1000);

  await page.evaluate((targetUrl) => {
    window.open(targetUrl, "_blank");
  }, url);

  await sleep(1000);

  await context.close();
}

app.listen(PORT, () => {
  console.log(`Server running at http://${HOST}:${PORT}`);
});
