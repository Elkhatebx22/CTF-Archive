const jwt = require('jsonwebtoken');
const { db } = require('../database');

const JWT_SECRET = process.env.JWT_SECRET || 'your-default-jwt-secret';

const protect = (req, res, next) => {
    const token = req.cookies.token;
    if (!token) {
        return res.status(401).redirect('/login');
    }

    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        db.get('SELECT id, username, role FROM users WHERE id = ?', [decoded.id], (err, user) => {
            if (err || !user) {
                return res.status(401).redirect('/login');
            }
            req.user = user;
            next();
        });
    } catch (error) {
        res.clearCookie('token');
        return res.status(401).redirect('/login');
    }
};

const bossOnly = (req, res, next) => {
    if (req.user && req.user.role === 'Boss') {
        next();
    } else {
        res.status(403).send('Forbidden: Bosses only');
    }
};

const addUserToRequest = (req, res, next) => {
    const token = req.cookies.token;
    if (!token) {
        return next();
    }
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        db.get('SELECT id, username, role FROM users WHERE id = ?', [decoded.id], (err, user) => {
            if (user) {
                req.user = user;
            }
            next();
        });
    } catch (error) {
        next();
    }
};

const apiKeyAuth = (req, res, next) => {
    const apiKey = req.headers['x-api-key'];
    if (!apiKey) {
        return res.status(401).send('Unauthorized: Missing X-API-Key header.');
    }

    db.get("SELECT role FROM users WHERE api_key = ?", [apiKey], (err, user) => {
        if (err) {
            return res.status(500).send('Server error during authentication.');
        }
        if (!user || user.role !== 'Boss') {
            return res.status(403).send('Forbidden: Invalid API key or insufficient privileges.');
        }
        next();
    });
};

module.exports = { protect, bossOnly, addUserToRequest, JWT_SECRET, apiKeyAuth };
