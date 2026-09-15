const crypto = require('crypto');
const { users, notes, sessions } = require('../models/store');

exports.getRegister = (req, res) => {
    res.render('pages/register', { title: 'Register', user: null });
};

exports.postRegister = (req, res) => {
    const { username, password } = req.body;
    if (!username || !password || users[username]) {
        return res.status(400).render('pages/error', {
            title: 'Error',
            message: 'Username is invalid or already taken.',
            user: null
        });
    }
    users[username] = { username, password, role: 'user' };
    notes[username] = [];
    res.redirect('/login');
};

exports.getLogin = (req, res) => {
    res.render('pages/login', { title: 'Login', user: null });
};

exports.postLogin = (req, res) => {
    const { username, password } = req.body;
    const user = users[username];
    if (user && user.password === password) {
        const sessionId = crypto.randomBytes(16).toString('hex');
        sessions[sessionId] = user;
        res.cookie('sessionId', sessionId, { httpOnly: true, sameSite: 'strict' });
        res.redirect('/notes');
    } else {
        res.status(401).render('pages/error', {
            title: 'Error',
            message: 'Invalid credentials.',
            user: null
        });
    }
};

exports.getLogout = (req, res) => {
    const sessionId = req.cookies.sessionId;
    delete sessions[sessionId];
    res.clearCookie('sessionId');
    res.redirect('/login');
};