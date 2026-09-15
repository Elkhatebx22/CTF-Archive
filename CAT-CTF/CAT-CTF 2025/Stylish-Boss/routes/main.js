const express = require('express');
const { db } = require('../database');
const { protect, bossOnly, addUserToRequest } = require('../middleware/auth');
const { visit } = require('../bot');
const router = express.Router();

router.get('/', addUserToRequest, (req, res) => {
    if (req.user) {
        db.get("SELECT fontPreference FROM settings WHERE userId = ?", [req.user.id], (err, row) => {
            if (err) {
                return res.status(500).send("Error fetching user settings.");
            }
            res.render('index', {
                user: req.user,
                currentFont: row ? row.fontPreference : 'sans-serif'
            });
        });
    } else {
        res.render('index', { user: null });
    }
});

router.post('/set-font', protect, (req, res) => {
    let fontName = req.body.fontName || 'sans-serif';

    fontName = fontName.replace(/[<>]/g, '');

    db.run(`UPDATE settings SET fontPreference = ? WHERE userId = ?`, [fontName, req.user.id], function(err) {
        if (err) {
            return res.status(500).send("Error updating font.");
        }
        console.log(`User ${req.user.username} set font to: "${fontName}"`);
        res.redirect('/profile');
    });
});

router.post('/report', protect, (req, res) => {
    const { username } = req.body;
    if (!username) {
        return res.status(400).send("Username is required.");
    }

    const url = `http://localhost:3000/boss/view-theme?username=${encodeURIComponent(username)}`;

    visit(url);

    res.json({
        message: 'Report sent. The Boss will review it shortly.',
    })
});

router.get('/profile', protect, (req, res) => {
    db.get("SELECT fontPreference FROM settings WHERE userId = ?", [req.user.id], (err, settingRow) => {
        if (err) {
            return res.status(500).send("Error fetching settings.");
        }
        db.get("SELECT api_key FROM users WHERE id = ?", [req.user.id], (err, userRow) => {
            if (err) {
                return res.status(500).send("Error fetching API key.");
            }
            res.render('profile', {
                user: req.user,
                userFont: settingRow ? settingRow.fontPreference : 'sans-serif',
                apiKey: userRow.api_key,
                message: req.query.message
            });
        });
    });
});

router.get('/boss/view-theme', protect, bossOnly, (req, res) => {
    const { username } = req.query;
    if (!username) {
        return res.status(400).send("Please provide a 'username' query parameter.");
    }

    console.log(`The Boss is viewing theme for user: ${username}`);
    
    db.get("SELECT * FROM users WHERE username = ?", [username], (err, userToView) => {
        if (err || !userToView) {
            return res.status(404).send("User not found.");
        }
        db.get("SELECT fontPreference FROM settings WHERE userId = ?", [userToView.id], (err, settingRow) => {
            if (err) {
                return res.status(500).send("Error fetching settings.");
            }
            db.get("SELECT api_key FROM users WHERE id = ?", [req.user.id], (err, bossUserRow) => {
                res.render('profile', {
                    user: userToView,
                    userFont: settingRow ? settingRow.fontPreference : 'sans-serif',
                    apiKey: bossUserRow.api_key
                });
            });
        });
    });
});

router.post('/logout', (req, res) => {
    res.clearCookie('token');
    res.redirect('/login');
});

module.exports = router;
