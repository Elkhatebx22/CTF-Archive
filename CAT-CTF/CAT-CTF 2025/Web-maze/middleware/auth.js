const jwt = require("jsonwebtoken");
const dotenv = require("dotenv");

dotenv.config();
const JWT_SECRET = process.env.JWT_SECRET;

console.log("JWT_SECRET:", JWT_SECRET);
function authenticateToken(req, res, next) {
  const authHeader = req.headers["authorization"];
  let token = authHeader && authHeader.split(" ")[1]; // Bearer <token>

  if (!token) {
    token = req.cookies.token;
  }

  if (!token)
    return res.status(401).render("error", {
      status: 401,
      message: "Token required",
    });

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err)
      return res.status(403).render("error", {
        status: 403,
        message: "Invalid token",
      });
    req.user = user; 
    next();
  });
}

function is_admin(req, res, next) {
  if (req.user && req.user.username === "admin") {
    next();
  } else {
    return res.status(403).render("error", {
      status: 403,
      message: "Unauthorized: Admin access required",
    });
  }
}

module.exports = { authenticateToken, is_admin };
