const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { db, generateRandomString } = require('../database');
const { JWT_SECRET } = require('../middleware/auth');
const router = express.Router();

const saltRounds = 10;

router.get('/register', (req, res) => {
    res.render('register');
});

router.post('/register', async (req, res) => {
    const { username, password } = req.body;
    if (!username || !password) {
        return res.status(400).send('Username and password are required.');
    }

    try {
        const hashedPassword = await bcrypt.hash(password, saltRounds);
        const role = 'user';
        const apiKey = `sk_${generateRandomString(10)}`;

        db.run('INSERT INTO users (username, password, role, api_key) VALUES (?, ?, ?, ?)',
            [username.toLowerCase(), hashedPassword, role, apiKey],
            function (err) {
                if (err) {
                    return res.status(500).send('Could not register user. Username might be taken.');
                }
                db.run(`INSERT INTO settings (userId, fontPreference) VALUES (?, ?)`, [this.lastID, 'sans-serif']);
                console.log(`User ${username} registered successfully.`);
                res.redirect('/login');
            }
        );
    } catch (error) {
        res.status(500).send('Server error during registration.');
    }
});

router.get('/login', (req, res) => {
    res.render('login');
});

router.post('/login', (req, res) => {
    const { username, password } = req.body;
    db.get('SELECT * FROM users WHERE username = ?', [username], async (err, user) => {
        if (err || !user) {
            return res.status(401).send('Invalid credentials.');
        }

        const match = await bcrypt.compare(password, user.password);
        if (match) {
            const token = jwt.sign({ id: user.id, username: user.username, role: user.role }, JWT_SECRET, { expiresIn: '1h' });
            res.cookie('token', token, { httpOnly: true, secure: process.env.NODE_ENV === 'production' });
            res.redirect('/profile');
        } else {
            res.status(401).send('Invalid credentials.');
        }
    });
});

module.exports = router;
