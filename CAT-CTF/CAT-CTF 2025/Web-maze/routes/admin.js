const express = require("express");
const router = express.Router();
const { authenticateToken, is_admin } = require("../middleware/auth");
const qrcode = require("qrcode");
const db = require("../utils/db");
const path = require("path");

const contentFilePath = path.join(__dirname, "..", "views", "dashboard.ejs");
console.log(`Content file path: ${contentFilePath}`);


const blacklist = [
  'env',
  'ENV',
  'environment',
  'printenv',
  'set',
  'export',
  'cat',
  'fromCharCode',
  'join',
  'substring',
  'getOwnPropertyNames',
  'process\\.env',
  'process\\["env"\\]',
  "process\\['env'\\]",
  'process\\[`env`\\]',
  'echo.*\\$',
  '\\$[A-Z_]',
  'cat.*proc.*environ',
  '/proc/self/environ',
  '/proc/*/environ',
  'global\\.process\\.env',
  'globalThis\\.process\\.env',
  'window\\.process\\.env',
  'cHJvY2Vzcy5lbnY',
  'ZW52',
  '70726f636573732e656e76',
  '656e76',
  'eval',
  'Function\\(',
  '/etc/environment',
  '/etc/profile',
  'Object\\.keys\\(process\\)',
  'constructor.*constructor',
  'console\\.log.*process',
  'console\\.dir.*process'
];
router.get("/admin", authenticateToken, is_admin, async (req, res) => {
  try {
    res.render("admin", { 
      user: req.user.username
    });
  } catch (error) {
    console.error("Error rendering admin:", error);
    res.status(500).send("Error.");
  }
});

router.post("/admin/update", authenticateToken, is_admin, async (req, res) => {
  const { html } = req.body;
  if (!html) {
    return res.status(400).json({ error: "No HTML content provided." });
  }

  try {
    const lowerHtml = html.toLowerCase();
    let blockedPattern = null;
    
    const containsBlacklisted = blacklist.some(pattern => {
      const regex = new RegExp(pattern, 'gi');
      if (regex.test(html) || regex.test(lowerHtml)) {
        blockedPattern = pattern;
        return true;
      }
      return false;
    });
    
    if (containsBlacklisted) {
      return res.status(400).json({ 
        error: "Nice try! But that's blocked. Think more creatively... 🐱",
        blocked_pattern: blockedPattern
      });
    }
        
    const tempTemplate = html;
    
    const ejs = require('ejs');
    
    try {
      const result = ejs.render(tempTemplate, { 
        user: req.user.username,
      });
      
      return res.json({
        success: true,
        result: result.trim(),
        payload: html.substring(0, 100) + (html.length > 100 ? '...' : '')
      });
      
    } catch (renderError) {
      return res.json({
        success: false,
        error: `Template Error: ${renderError.message}`,
        payload: html.substring(0, 100) + (html.length > 100 ? '...' : '')
      });
    }
    
  } catch (error) {
    return res.status(500).json({ error: "Internal server error." });
  }
});

router.get(
  "/admin/2fa-setup",
  authenticateToken,
  is_admin,
  async (req, res) => {
    const result = await db.query(
      "SELECT two_fa_secret FROM users WHERE username = ?",
      [req.user.username]
    );
    const secret = result.rows[0].two_fa_secret;
    const otpauthUrl = `otpauth://totp/CAT-CTF:${req.user.username}?secret=${secret}&issuer=CAT-CTF`;

    qrcode.toDataURL(otpauthUrl, (err, imageUrl) => {
      if (err) {
        console.log("Error with QR code generation");
        return res.status(500).send("Error generating QR code");
      }

      res.render("2fa-setup", {
        qr: imageUrl,
        secret
      });
    });
  }
);


module.exports = router;
