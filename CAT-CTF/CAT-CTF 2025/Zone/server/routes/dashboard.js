const express = require('express');
const router = express.Router();

module.exports = function(users, notes) {

  router.post('/add_note', (req, res) => {
    const { username, token, note } = req.body;
    const user = users[username];
    
    
    if (!user || user.token !== token) {
        
        return res.render('login', { error: 'Session invalid. Please log in again.' });
    }
    
    if (!notes[username]) {
        notes[username] = [];
    }
    notes[username].push(note);
    
    res.render('dashboard', {
      username,
      token: user.token, 
      notes: notes[username],
      reset_error: null,
      reset_success: null
    });
  });

  return router;
};