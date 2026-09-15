const express = require('express');
const router = express.Router();
const adminController = require('../controllers/adminController');
const { auth, adminOnly } = require('../middleware/auth');

router.get('/', auth, adminOnly, adminController.getAdminPanel);


router.post('/feedback', auth, adminOnly, adminController.postFeedback);

router.get('/view-note', auth, adminOnly, adminController.viewNoteById);

module.exports = router;
