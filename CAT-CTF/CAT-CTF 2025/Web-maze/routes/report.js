const express = require("express");
const router = express.Router();
const { visit } = require("../utils/bot");

const validHttpPrefix = `http://${process.env.URL}/`;
const validPrefix = process.env.URL

router.get('/report', (req, res) => {
    res.sendFile('report.html', { root: 'public' });
});

router.post("/report", async (req, res) => {
    const { url } = req.body;

    if (!url || typeof url !== 'string') {
        return res.status(400).send("URL is required.");
    }

    if (url.startsWith(validHttpPrefix) || url.startsWith(validPrefix)) {
        try {
            // Ensure the bot visits a full URL
            const urlToVisit = url.startsWith('http') ? url : `http://${url}`;
            await visit(urlToVisit, true);
            return res.send("The admin will check your link shortly.");
        } catch (error) {
            console.error("Bot visit failed:", error);
            res.status(500).render("error", {
            status: 500,
            message: "An error occurred while the bot was visiting the URL."
            });
        }
    }
    res.status(400).render("error", {
        status: 400,
        message: `URL must start with ${validHttpPrefix}`
        });
});

module.exports = router;
