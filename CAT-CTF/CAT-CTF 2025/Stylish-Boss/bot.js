const puppeteer = require('puppeteer');
const jwt = require('jsonwebtoken');
const { db } = require('./database');
const { JWT_SECRET } = require('./middleware/auth');

let bossUser = null;

db.get("SELECT * FROM users WHERE username = 'Boss'", (err, user) => {
    if (user) {
        bossUser = user;
    } else {
        console.error("Could not find Boss user in database for bot.");
    }
});

const visit = async (url) => {
    if (!bossUser) {
        console.error("Bot cannot operate without Boss user.");
        return;
    }

    const browser = await puppeteer.launch({
        headless: true,
        args: ["--no-sandbox", "--disable-setuid-sandbox"],
    });
    const page = await browser.newPage();

    const token = jwt.sign({ id: bossUser.id, username: bossUser.username, role: bossUser.role }, JWT_SECRET, { expiresIn: '1h' });

    await page.setCookie({
        name: 'token',
        value: token,
        domain: 'localhost',
        httpOnly: true,
        sameSite: 'Strict',
    });

    console.log(`Bot visiting: ${url}`);
    try {
        await page.goto(url, { waitUntil: 'networkidle2' });
        console.log(`Successfully loaded page: ${url}`);
    } catch (error) {
        console.error(`Error loading page: ${url}`, error);
    }

    await new Promise(resolve => setTimeout(resolve, 2000));

    await browser.close();
};

module.exports = { visit };
