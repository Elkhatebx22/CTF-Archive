const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const path = require('path');

const app = express();
app.use(bodyParser.urlencoded({ extended: true }));

app.use(express.static(path.join(__dirname, 'public')));

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

const users = {
  admin: {
    password: 'adminpass',
    email: 'admin@cattdd.cat',
    type: 'admin',
    token: null
  }
};
const notes = { 
  admin: [
    "Welcome, Admin! This is a pre-defined note.", 
    "Flag : CATF{gr!ll3d_ch33s3_0v3rfl0w@bun}"
  ] 
};

const EMAIL_SERVER_URL = 'http://localhost:5001';

function sendEmail(to, subject, body) {
  axios.post(`${EMAIL_SERVER_URL}/receive`, {
    to,
    subject,
    body
  }).catch(err => console.log('[EMAIL ERROR]', err.message));
}

const indexRouter = require('./routes/index');
const authRouter = require('./routes/auth')(users, notes, sendEmail);
const dashboardRouter = require('./routes/dashboard')(users, notes);

app.use('/', indexRouter);
app.use('/', authRouter);
app.use('/', dashboardRouter);

const PORT = 5000;
app.listen(PORT, () => console.log(`API server running at http://localhost:${PORT}`));