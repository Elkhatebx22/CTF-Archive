const express = require('express');
const router = express.Router();
const { sessions } = require('../models/store');
const { adminVisit } = require('../utils/bot');


router.get('/', (req, res) => {
    if (req.cookies.sessionId && sessions[req.cookies.sessionId]) {
        res.redirect('/notes');
    } else {
        res.redirect('/login');
    }
});

router.post('/report', (req, res) => {
    const { note_id } = req.body;
    if (note_id) {
        adminVisit(note_id).catch(console.error);
        res.status(200).send('The admin will check your note shortly.');
    } else {
        res.status(400).send('Note ID is required.');
    }
});

router.get('/report', (req, res) => {
    const user = sessions[req.cookies.sessionId];
    res.render('pages/report', {
        title: 'Report Note',
        user: user || null
    });
});

module.exports = router;