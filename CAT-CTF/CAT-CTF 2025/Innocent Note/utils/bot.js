const puppeteer = require('puppeteer');

const adminVisit = async (noteId) => {
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();

    const URL = process.env.URL || 'http://localhost:3000';

    try {
        // Login as admin
        await page.goto(`${URL}/login`, { waitUntil: 'networkidle0' });
        await page.type('input[name="username"]', 'admin');
        await page.type('input[name="password"]', process.env.ADMIN_PASSWORD);
        await Promise.all([
            page.waitForNavigation({ waitUntil: 'networkidle0' }),
            page.click('button[type="submit"]')
        ]);

        // Visit the note
        await page.goto(`${URL}/admin/view-note?note_id=${noteId}`, {
            waitUntil: 'networkidle0',
            timeout: 5000
        });
    } catch (e) {
        console.error('Error visiting note:', e);
    } finally {
        await page.close();
        await browser.close();
    }
};

module.exports = { adminVisit };
