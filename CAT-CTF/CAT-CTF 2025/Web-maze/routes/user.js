const express = require("express");
const router = express.Router();
const db = require('../utils/db');
const { authenticateToken } = require("../middleware/auth");

router.get("/user", authenticateToken, (req, res) => {
  console.log(req.user);
  res.status(200).sendFile(process.cwd() + "/user.html");
});

router.get("/profile", authenticateToken, async (req, res) => {
  try {
    const result = await db.query(
      "SELECT name, username, email, role FROM users WHERE username = ?",
      [req.user.username]
    );
    const user = result.rows[0];
    if (!user) return res.status(404).send("User not found");

    res.render("profile", { user });
  } catch (err) {
    console.error("Error loading profile:", err);
    res.status(500).send("Internal Server Error");
  }
});

router.get("/profile/:username", authenticateToken, async (req, res) => {
  const { username } = req.params;
  try {
    const result = await db.query(
      "SELECT name, username, email, role FROM users WHERE username = ?",
      [username]
    );
    const user = result.rows[0];
    if (!user) return res.status(404).send("User not found");

    const posts = await db.query(
      "SELECT content FROM posts WHERE post_owner = ? ORDER BY id DESC",
      [username]
    );

    res.render("profile_other", { user, posts: posts.rows });
  } catch (err) {
    console.error("Error loading profile:", err);
    res.status(500).send("Internal Server Error");
  }
});

module.exports = router;
