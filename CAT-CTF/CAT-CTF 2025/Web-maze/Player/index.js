const express = require("express");
const app = express();
const dotenv = require("dotenv");
const cookieParser = require("cookie-parser");
const fixUrl = require("./middleware/fix");

// Import routes
const authRoutes = require("./routes/auth");
const userRoutes = require("./routes/user");
const adminRoutes = require("./routes/admin");
const reportRoutes = require("./routes/report");
const postRoutes = require("./routes/post");

app.set("view engine", "ejs");
app.set("views", __dirname + "/views");

dotenv.config();

app.use(cookieParser());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static("./public"));

// Use middleware
app.use(fixUrl);

// Use routes
app.use(authRoutes);
app.use(userRoutes);
app.use(adminRoutes);
app.use(reportRoutes);
app.use(postRoutes);

// 404 Not Found handler
app.use((req, res, next) => {
  res.status(404).render("error", {
    status: 404,
    message: "Page Not Found",
  });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error("Global error:", err.stack);
  res.status(err.status || 500).render("error", {
    status: err.status || 500,
    message: err.message || "Internal Server Error",
  });
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
