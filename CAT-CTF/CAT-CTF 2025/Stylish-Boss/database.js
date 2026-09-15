const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');

function generateRandomString(length) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

const db = new sqlite3.Database('./database.db', (err) => {
    if (err) {
        console.error(err.message);
    }
    console.log('Connected to the SQLite database.');
});

db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS settings (
        userId INTEGER,
        fontPreference TEXT,
        FOREIGN KEY(userId) REFERENCES users(id)
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        api_key TEXT NOT NULL
    )`);

    const bossUsername = 'Boss';
    const bossPassword = generateRandomString(16);
    const bossApiKey = `sk_${generateRandomString(10)}`;
    const saltRounds = 10;

    bcrypt.hash(bossPassword, saltRounds, (err, hashedPassword) => {
        if (err) {
            return console.error('Error hashing Boss password:', err);
        }

        db.run(`INSERT OR IGNORE INTO users (username, password, role, api_key) VALUES (?, ?, ?, ?)`,
            [bossUsername, hashedPassword, 'Boss', bossApiKey],
            function(err) {
                if (err) {
                    return console.error('Error creating Boss user:', err.message);
                }
                if (this.changes > 0) {
                    console.log('--- BOSS CREATED ---');
                    console.log(`Username: ${bossUsername}`);
                    console.log(`Password: ${bossPassword} (save this!)`);
                    console.log(`API Key: ${bossApiKey}`);
                    console.log('--------------------');
                    db.run(`INSERT INTO settings (userId, fontPreference) VALUES (?, ?)`, [this.lastID, 'sans-serif']);
                } else {
                    db.get("SELECT api_key FROM users WHERE username = 'Boss'", [], (err, row) => {
                        if (row) {
                            console.log(`Boss user already exists. Boss API Key for this session: ${row.api_key}`);
                        }
                    });
                }
            }
        );
    });
});

module.exports = { db, generateRandomString };
