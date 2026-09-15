const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const dbPath = path.resolve(__dirname, 'cat-ctf.db');
const bcrypt = require("bcrypt");
require('dotenv').config();

const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error opening database', err.message);
  } else {
    console.log('Connected to the SQLite database.');
    initializeDatabase();
  }
});

function initializeDatabase() {
  db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      two_fa_enabled BOOLEAN DEFAULT false,
      two_fa_secret TEXT,
      name TEXT,
      email TEXT UNIQUE,
      role TEXT,
      attempts INTEGER DEFAULT 3
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS posts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      post_owner TEXT NOT NULL,
      content TEXT NOT NULL,
      FOREIGN KEY (post_owner) REFERENCES users(username)
    )`);

    const adminUsername = 'admin';
    const adminPassword = bcrypt.hashSync(process.env.ADMIN_PASSWORD || 'admin123', 10);
    const admin2faEnabled = true;
    const admin2faSecret = process.env.ADMIN_2FA_SECRET || 'default2faSecret';
    const adminEmail = 'admin@admin.com'
    const adminName = 'Admin';
    
    db.get('SELECT * FROM users WHERE username = ?', [adminUsername], (err, row) => {
      if (err) {
        return console.error('Error checking for admin user:', err.message);
      }
      
      if (!row) {
        db.run('INSERT INTO users (username, password, two_fa_enabled, two_fa_secret, email, name) VALUES (?, ?, ?, ?, ?, ?)', [adminUsername, adminPassword, admin2faEnabled, admin2faSecret, adminEmail, adminName], (err) => {
          if (err) {
            return console.error('Error creating admin user:', err.message);
          }
        });
      }
    });
  });
}

const query = (sql, params = []) => {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) {
        reject(err);
      } else {
        resolve({ rows, rowCount: rows.length });
      }
    });
  });
};

module.exports = { query, db };