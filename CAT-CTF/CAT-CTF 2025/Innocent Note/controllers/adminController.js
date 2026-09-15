const jsrender = require('jsrender');
const { users, notes, feedback } = require('../models/store');
const sanitize = require('../services/sanitizer');

exports.getAdminPanel = (req, res) => {
    const userlistHtml = `
        <ul class="user-list">
            ${Object.values(users).map(u => `<li><b>Username:</b> ${sanitize(u.username)} | <b>Role:</b> ${u.role}</li>`).join('')}
        </ul>
    `;

    const renderedFeedback = feedback.map(item => {
        try {
            const feedbackTemplate = jsrender.templates(item.message);
            const renderedMessage = feedbackTemplate.render(); 

            return `
                <div class="feedback-item">
                    <p><strong>For User:</strong> ${sanitize(item.username)}</p>
                    <p><strong>Feedback Result:</strong> ${renderedMessage}</p>
                </div>
            `;
        } catch (e) {
            console.error("Template rendering failed:", e.message);
            return `
                <div class="feedback-item">
                    <p><strong>For User:</strong> ${sanitize(item.username)}</p>
                    <p><strong>Feedback:</strong> (Error rendering template)</p>
                </div>
            `;
        }
    });

    res.render('pages/admin', {
        title: 'Admin Panel',
        userlistHtml: userlistHtml,
        feedback: renderedFeedback
    });
};

exports.postFeedback = (req, res) => {
    const { username, message } = req.body;
    if (username && message) {
        feedback.push({ username, message });
    }
    res.redirect('/admin');
};

exports.viewNoteById = (req, res) => {
    const { note_id } = req.query;
    let foundNote = null;
    let ownerUsername = null;

    for (const username in notes) {
        const userNotes = notes[username];
        const note = userNotes.find(n => n.id === note_id);
        if (note) {
            foundNote = note;
            ownerUsername = username;
            break;
        }
    }

    if (foundNote) {
        res.render('pages/note-detail', {
            title: 'Admin Note View',
            note: {
                id: foundNote.id,
                content: sanitize(foundNote.content)
            },
            owner: ownerUsername
        });
    } else {
        res.status(404).render('pages/error', {
            title: 'Not Found',
            message: `A note with the ID "${note_id}" could not be found.`
        });
    }
};