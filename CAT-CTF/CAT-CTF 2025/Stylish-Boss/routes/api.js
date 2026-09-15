const express = require('express');
const { MetadataStripper } = require('metadata-stripper');
const { apiKeyAuth } = require('../middleware/auth');
const router = express.Router();

router.post('/strip-metadata', apiKeyAuth, (req, res) => {
    const filename = req.headers['x-file-name'];
    if (!filename) {
        return res.status(400).json({ message: 'X-File-Name header is required.' });
    }

    try {
        const stripper = new MetadataStripper();
        const output = stripper.processFile(filename);

        res.status(200).json({
            message: 'Filename processed successfully.',
            details: output || 'No output from command.'
        });

    } catch (error) {
        console.error('[API] Error during file processing:', error);
        res.status(500).json({ message: 'Failed to process file.' });
    }
});

module.exports = router;
