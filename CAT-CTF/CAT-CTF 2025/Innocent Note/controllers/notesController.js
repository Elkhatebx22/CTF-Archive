const crypto = require('crypto');
const { notes } = require('../models/store');
const sanitize = require('../services/sanitizer');

exports.getNotes = (req, res) => {
    const userNotes = notes[req.user.username] || [];
    const processedNotes = userNotes.map(note => ({
        id: note.id,
        content: sanitize(note.content)
    }));

    res.render('pages/notes', {
        title: 'My Notes',
        notes: processedNotes,
    });
};

exports.postNote = (req, res) => {
    if (req.body.content) {
        const newNote = {
            id: crypto.randomUUID(),
            content: req.body.content 
        };
        if (!notes[req.user.username]) {
            notes[req.user.username] = [];
        }
        notes[req.user.username].push(newNote);
    }
    res.redirect('/notes');
};

exports.getNoteById = (req, res) => {
    const { note_id } = req.query;
    const userNotes = notes[req.user.username] || [];
    
    const note = userNotes.find(n => n.id === note_id);

    if (note) {
        res.render('pages/note-detail', {
            title: 'Note View',
            note: {
                id: note.id,
                content: sanitize(note.content) 
            },
            owner: null 
        });
    } else {
        res.status(404).render('pages/error', {
            title: 'Not Found',
            message: 'The requested note was not found in your account.'
        });
    }
};
