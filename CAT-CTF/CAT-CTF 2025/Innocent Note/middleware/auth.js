const { sessions } = require('../models/store');

const auth = (req, res, next) => {
    const sessionId = req.cookies.sessionId;
    if (sessionId && sessions[sessionId]) {
        req.user = sessions[sessionId];
        res.locals.user = req.user; 
        return next();
    }
    res.redirect('/login');
};

const adminOnly = (req, res, next) => {
    if (req.user && req.user.role === 'admin') {
        return next();
    }
    res.status(403).render('pages/error', {
        title: 'Forbidden',
        message: 'You do not have permission to view this page.',
        user: req.user
    });
};

module.exports = { auth, adminOnly };