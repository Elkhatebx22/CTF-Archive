const express = require('express');
const router = express.Router();
const notesController = require('../controllers/notesController');
const { auth } = require('../middleware/auth');

router.get('/', auth, notesController.getNotes);
router.post('/', auth, notesController.postNote);

router.get('/view', auth, notesController.getNoteById);

module.exports = router;