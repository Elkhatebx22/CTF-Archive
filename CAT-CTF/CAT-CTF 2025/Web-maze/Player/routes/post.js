const express = require('express');
const router = express.Router();
const db = require('../utils/db');
const { authenticateToken } = require('../middleware/auth');

router.get('/posts', authenticateToken, async (req, res) => {
  try {
    const result = await db.query(
      'SELECT id, content FROM posts WHERE post_owner = ? ORDER BY id DESC',
      [req.user.username]
    );

    res.json({ posts: result.rows });
  } catch (err) {
    console.error('Error fetching posts:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/posts', authenticateToken, async (req, res) => {
  const { content } = req.body;

  if (!content || content.trim() === '') {
    return res.status(400).json({ error: 'Post content is required' });
  }

  try {
    await db.query(
      'INSERT INTO posts (post_owner, content) VALUES (?, ?)',
      [req.user.username, content]
    );

    res.status(201).json({ message: 'Post created successfully' });
  } catch (err) {
    console.error('Error creating post:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/profile/:username', authenticateToken, async (req, res) => {
  const { username } = req.params;
  try {
    const result = await db.query('SELECT name, username, email, role FROM users WHERE username = ?', [username]);
    const user = result.rows[0];
    if (!user) return res.status(404).send('User not found');

    const posts = await db.query('SELECT content FROM posts WHERE post_owner = ? ORDER BY id DESC', [username]);

    res.render('profile_other', { user, posts: posts.rows });
  } catch (err) {
    console.error('Error loading profile:', err);
    res.status(500).send('Internal Server Error');
  }
});

router.get('/search', authenticateToken, async (req, res) => {
  const query = req.query.q;

  if (!query || query.trim() === '') {
    return res.status(400).json({ error: 'Query required' });
  }

  try {
    const userResults = await db.query(
      'SELECT username, name FROM users WHERE LOWER(username) LIKE LOWER(?) OR LOWER(name) LIKE LOWER(?) LIMIT 10',
      [`%${query}%`, `%${query}%`]
    );

    const postResults = await db.query(
      'SELECT content, post_owner FROM posts WHERE LOWER(content) LIKE LOWER(?) LIMIT 10',
      [`%${query}%`]
    );

    res.json({
      users: userResults.rows,
      posts: postResults.rows
    });
  } catch (err) {
    console.error('Search error:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});
router.get('/feed', authenticateToken, async (req, res) => {
  try {
    const result = await db.query(`
      SELECT post_owner, content
      FROM posts
      ORDER BY id DESC
      LIMIT 50
    `);

    res.render('feed', { posts: result.rows, currentUser: req.user.username });
  } catch (err) {
    console.error('Error loading feed:', err);
    res.status(500).send('Internal Server Error');
  }
});

module.exports = router;