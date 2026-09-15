const express = require('express');
const router = express.Router();
const uuid = require('uuid');

module.exports = function(users, notes, sendEmail) {

  router.get('/register', (req, res) => {
    res.render('register', { error: null });
  });

  router.post('/register', (req, res) => {
    const { username, password, email, type } = req.body;
    if (type !== 'user') return res.status(403).send('Admin registration not allowed.');
    if (!email.endsWith('@catf.cat')) return res.render('register', { error: 'Email must end with @catf.cat' });
    if (users[username]) return res.render('register', { error: 'Username exists' });

    users[username] = { password, email, token: null, type };
    notes[username] = [];
    res.redirect('/login');
  });

  router.get('/login', (req, res) => {
    res.render('login', { error: null });
  });

  router.post('/login', (req, res) => {
    const { username, password } = req.body;
    const user = users[username];
    if (!user || user.password !== password)
      return res.render('login', { error: 'Invalid credentials' });

    const token = uuid.v4();
    user.token = token;

    res.render('dashboard', {
      token: user.token,
      username,
      notes: notes[username] || [],
      reset_error: null,
      reset_success: null
    });
  });

  router.get('/reset', (req, res) => {
    res.render('reset', { error: null, success: null });
  });

  router.post('/reset', (req, res) => {
    const { username_or_email } = req.body;
    let user = null, uname = null;
    for (const key in users) {
      if (key === username_or_email || users[key].email === username_or_email) {
        user = users[key];
        uname = key;
      }
    }
    if (!user) return res.render('reset', { error: 'User not found', success: null });

    const token = uuid.v1();
    user.token = token;
    

    if (user.type === 'user') {
      sendEmail(user.email, 'Password Reset Token', `Hello ${uname}, your reset token is: ${token}`);
      return res.render('reset', { error: null, success: 'Token sent to your email' });
    }
    res.render('reset', { error: null, success: 'Token sent to your email' });
  });

  router.get('/change_password', (req, res) => {
    res.render('change_password', { error: null, success: null });
  });

  router.post('/change_password', (req, res) => {
    const { username, token, new_password } = req.body;
    const user = users[username];
    if (!user || user.token !== token) return res.render('change_password', { error: 'Invalid token or user', success: null });

    user.password = new_password;
    user.token = null;

    res.render('change_password', { error: null, success: 'Password changed successfully' });
  });

  return router;
};
