const express = require("express");
const puppeteer = require("puppeteer-core");

const app = express();

const PORT = Number(process.env.BOT_PORT || 9001);
const FLAG = process.env.FLAG || "flag{change_me}";
const CHALLENGE_ORIGIN = process.env.CHALLENGE_ORIGIN || "http://web:5000";
const ALLOWED_PREFIX = process.env.ALLOWED_PREFIX || "http";
const VISIT_MS = Number(process.env.VISIT_MS || 10000);
const NAVIGATION_TIMEOUT_MS = Number(process.env.NAVIGATION_TIMEOUT_MS || 10000);
const CHROME_PATH = process.env.CHROME_PATH || "/usr/bin/chromium-browser";

app.use(express.urlencoded({ extended: false }));

app.post("/visit", async (req, res) => {
  const url = req.body.url || "";

  if (!url.startsWith(ALLOWED_PREFIX)) {
    return res.status(400).send("URL rejected.");
  }

  let browser;
  try {
    browser = await puppeteer.launch({
      executablePath: CHROME_PATH,
      headless: "new",
      args: ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
    });

    const page = await browser.newPage();
    await page.goto(CHALLENGE_ORIGIN, { waitUntil: "domcontentloaded", timeout: NAVIGATION_TIMEOUT_MS });
    await page.setCookie({
      name: "flag",
      value: FLAG,
      url: CHALLENGE_ORIGIN,
      httpOnly: false,
      sameSite: "Lax",
    });
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: NAVIGATION_TIMEOUT_MS });
    await new Promise((resolve) => setTimeout(resolve, VISIT_MS));

    return res.send("Admin bot visited the URL.");
  } catch (error) {
    console.error(error);
    return res.status(500).send("Bot failed.");
  } finally {
    if (browser) {
      await browser.close();
    }
  }
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Bot listening on ${PORT}`);
});
