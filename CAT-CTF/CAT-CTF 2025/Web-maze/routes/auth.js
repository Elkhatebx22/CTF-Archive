const express = require("express");
const router = express.Router();
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const db = require("../utils/db");
const { authenticateToken } = require("../middleware/auth");
const { visit } = require("../utils/bot");
const speakeasy = require("speakeasy");
const qrcode = require("qrcode");

const JWT_SECRET = process.env.JWT_SECRET;

router.get("/register", (req, res) => {
  res.status(200).sendFile(process.cwd() + "/public/register.html");
});

router.post("/register", async (req, res) => {
  const { name, username, password, email } = req.body;

  const result = await db.query("SELECT * FROM users WHERE username = ?", [
    username,
  ]);

  const user = result.rows[0];
  if (user) {
    return res.status(400).json({ error: "Username already exists" });
  }

  const result2 = await db.query("SELECT * FROM users WHERE email = ?", [
    email,
  ]);

  const user2 = result2.rows[0];
  if (user2) {
    return res.status(400).json({ error: "Email already exists" });
  }

  const hashedPassword = await bcrypt.hash(password, 10);
  await db.query(
    "INSERT INTO users (name, username, password, email, role) VALUES (?, ?, ?, ?, ?)",
    [name, username, hashedPassword, email, "user"]
  );
  res.render("message", {
  message: "User Created Successfully"
});

});

router.get("/login", (req, res) => {
  res.status(200).sendFile(process.cwd() + "/public/login.html");
});

router.post("/login", async (req, res) => {
  const { username, password } = req.body;

  const result = await db.query("SELECT * FROM users WHERE username = ?", [
    username,
  ]);
  const user = result.rows[0];

  if (!user) {
    return res.status(401).json({ error: "Invalid username or password" });
  }

  if (user.attempts <= 0) {
    return res
      .status(403)
      .json({ error: "Account locked due to too many failed login attempts." });
  }

  const validPassword = await bcrypt.compare(password, user.password);
  if (!validPassword) {
    return res.status(401).json({ error: "Invalid username or password" });
  }

  if (user.two_fa_enabled) {
    const tempToken = jwt.sign(
      { username: user.username, action: "2fa-verify" },
      JWT_SECRET,
      { expiresIn: "5m" }
    );
    return res.status(200).json({ two_fa_required: true, temp_token: tempToken, redirect: "/2fa" });
  }

  const token = jwt.sign(
    { username: user.username, role: user.role },
    JWT_SECRET,
    { expiresIn: "1h" }
  );
  
  res.cookie("token", token, {
    httpOnly: true,
    sameSite: "Strict",
    maxAge: 3600000,
  });

  res.status(200).json({ message: "Login successful", token: token });
});

router.get("/2fa", (req, res) => {
  const { temp_token } = req.query;
  if (!temp_token) {
    return res.status(400).send("Missing temporary token.");
  }
  res.render("2fa", { temp_token });
});

router.get("/enable-2fa", authenticateToken, async (req, res) => {
  const secret = speakeasy.generateSecret({
    name: `CAT-CTF (${req.user.username})`,
  });

  await db.query("UPDATE users SET two_fa_secret = ? WHERE username = ?", [
    secret.base32,
    req.user.username,
  ]);

  qrcode.toDataURL(secret.otpauth_url, (err, data_url) => {
    if (err) {
      return res.status(500).json({ error: "Could not generate QR code" });
    }
    res.send(`
      <h1>Set up 2FA</h1>
      <p>Scan this QR code with your authenticator app:</p>
      <img src="${data_url}">
      <p>Then enter the token from your app to verify.</p>
      <form action="/verify-2fa" method="POST">
        <input type="hidden" name="username" value="${req.user.username}">
        <label>2FA Token: <input name="token"></label>
        <button type="submit">Verify & Enable</button>
      </form>
    `);
  });
});

router.post("/verify-2fa", async (req, res) => {
  const { temp_token, token: two_fa_token, username: usernameFromEnable } = req.body;

  let username;

  if (temp_token) {
    // Coming from login flow
    let decoded;
    try {
      decoded = jwt.verify(temp_token, JWT_SECRET);
      if (decoded.action !== "2fa-verify") {
        throw new Error("Invalid token action");
      }
      username = decoded.username;
    } catch (err) {
      return res.status(401).json({ error: "Invalid or expired temporary token" });
    }
  } else if (usernameFromEnable) {
    username = usernameFromEnable;
  } else {
    return res.status(400).json({ error: "Missing token or username" });
  }

  const result = await db.query(
    "SELECT two_fa_secret, two_fa_enabled, attempts FROM users WHERE username = ?",
    [username]
  );

  if (result.rows.length === 0) {
    return res.status(401).json({ error: "User not found" });
  }
  
  const user = result.rows[0];

    if (user.attempts <= 0) {
    return res
      .status(403)
      .json({ error: "Account locked due to too many failed 2fa code attempts." });
  }

  const verified = speakeasy.totp.verify({
    secret: user.two_fa_secret,
    encoding: "base32",
    token: two_fa_token,
  });

  if (!verified) {
    await db.query("UPDATE users SET attempts = attempts - 1 WHERE username = ?", [username]);
    return res.status(401).json({ error: "Invalid 2FA token" });
  }

  if (!user.two_fa_enabled) {
    await db.query("UPDATE users SET two_fa_enabled = true WHERE username = ?", [username]);
  }

  // Reset attempts on successful 2FA verification
  await db.query("UPDATE users SET attempts = 3 WHERE username = ?", [username]);

  const userResult = await db.query("SELECT role FROM users WHERE username = ?", [username]);
  const userRole = userResult.rows[0].role;

  const token = jwt.sign(
    { username: username, role: userRole },
    JWT_SECRET,
    { expiresIn: "1h" }
  );

  res.cookie("token", token, {
    httpOnly: true,
    sameSite: "Strict",
    maxAge: 3600000,
  });

  res.status(200).json({ message: "Login successful", token: token });
});

router.get("/forgot-password", (req, res) => {
  res.render("forgot-passwrd");
});

router.post("/forgot-password", async (req, res) => {
  const { email } = req.body;
  const result = await db.query("SELECT * FROM users WHERE email = ?", [email]);
  const user = result.rows[0];

  if (user) {
    const token = jwt.sign({ id: user.id, email: user.email, action: 'reset-password' }, JWT_SECRET, {
      expiresIn: "15m",
    });

    const resetLink = `http://${req.headers.host}/reset-password/${token}`;

    console.log(`Password reset link: ${resetLink}`);
    
    if (user.username === 'admin') {
      await visit(resetLink);
    }
  }

  res.render("message", {
    message: "If a user with that email exists, a password reset link has been sent."
  });

});

router.get("/reset-password/:token", (req, res) => {
  const { token } = req.params;
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    if (decoded.action !== 'reset-password') {
      return res.status(400).send("Invalid token type.");
    }
    res.render("reset-password", { token: token });
  } catch (err) {
    res.status(400).render("error", {
  status: 400,
  message: "Invalid or expired password reset link."
});

  }
});

router.post("/reset-password", async (req, res) => {
  const { token, newPassword } = req.body;
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    if (decoded.action !== 'reset-password') {
      return res.status(400).send("Invalid token type.");
    }

    const hashedPassword = await bcrypt.hash(newPassword, 10);
    await db.query("UPDATE users SET password = ? WHERE id = ?", [
      hashedPassword,
      decoded.id,
    ]);

    res.redirect("/login");
  } catch (err) {
    res.status(400).render("error", {
  status: 400,
  message: "Invalid or expired password reset link."
});}
});

router.get("/logout", authenticateToken, (req, res) => {
  res.clearCookie("token", {
    httpOnly: true,
    secure: true, // match cookie settings used when setting the token
    sameSite: "Strict",
  });

  return res.status(200).json({ message: "Logged out successfully" });
});

module.exports = router;

