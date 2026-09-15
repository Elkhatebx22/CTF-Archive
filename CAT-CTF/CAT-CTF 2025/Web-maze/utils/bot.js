const puppeteer = require("puppeteer");
const jwt = require("jsonwebtoken");
const { URL } = require("url");
require("dotenv").config();

const visit = async (url, withAdminCookie = false) => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });
  const page = await browser.newPage();

  // Set the admin cookie before visiting the page
  const { hostname, origin } = new URL(url);

  await page.goto(origin, { waitUntil: "networkidle2" });

  if (withAdminCookie) {
    const adminToken = jwt.sign(
      { username: "admin", role: "admin" },
      process.env.JWT_SECRET
    );

    await page.setCookie({
      name: "token",
      value: adminToken,
      domain: hostname,
      httpOnly: true,
      sameSite: "Strict",
    });
  }

  console.log(`Bot visiting: ${url}`);
  try {
    await page.goto(url, { waitUntil: "networkidle2" });
    console.log(`Successfully loaded page: ${url}`);
  } catch (error) {
    console.error(`Error loading page: ${url}`, error);
  }

  await new Promise((resolve) => setTimeout(resolve, 2000));

  await browser.close();
};

module.exports = { visit };
