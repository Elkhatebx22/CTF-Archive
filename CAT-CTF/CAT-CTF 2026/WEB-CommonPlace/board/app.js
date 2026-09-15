"use strict";

import { randomBytes } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import express from "express";
import { rateLimit } from "express-rate-limit";
import { marked } from "marked";

const APP_DIRECTORY = dirname(fileURLToPath(import.meta.url));
const PORT = Number.parseInt(process.env.PORT || "4000", 10);
const REVIEWER_URL = process.env.REVIEWER_URL || "http://bot:8080/jobs";
const REVIEW_TIMEOUT_MS = Number.parseInt(process.env.REVIEW_TIMEOUT_MS || "60000", 10);
const MAX_POSTS = 256;
const MAX_COMMENTS = 64;

const posts = new Map();
const dateFormatter = new Intl.DateTimeFormat("en", {
  year: "numeric",
  month: "short",
  day: "numeric",
  hour: "numeric",
  minute: "2-digit",
  timeZone: "UTC",
  timeZoneName: "short",
});

marked.use({ gfm: true, breaks: true });

function validId(value) {
  return typeof value === "string" && /^[0-9a-f]{32}$/.test(value);
}

function formatDate(value) {
  return dateFormatter.format(new Date(value));
}

function textField(value, maximum) {
  if (typeof value !== "string") return null;
  const normalized = value.replaceAll("\u0000", "").trim();
  if (normalized.length === 0 || normalized.length > maximum) return null;
  return normalized;
}

function prunePosts() {
  if (posts.size < MAX_POSTS) return;

  for (const [id, post] of posts) {
    if (post.state === "reviewing") continue;
    posts.delete(id);
    if (posts.size < MAX_POSTS) return;
  }
}

function sendJson(response, status, value) {
  response.status(status).json(value);
}

const createLimit = rateLimit({
  windowMs: 60_000,
  max: 30,
  standardHeaders: true,
  legacyHeaders: false,
});

const reportLimit = rateLimit({
  windowMs: 60_000,
  max: 30,
  standardHeaders: true,
  legacyHeaders: false,
});

const app = express();
app.disable("x-powered-by");
app.set("trust proxy", 1);
app.set("views", join(APP_DIRECTORY, "views"));
app.set("view engine", "ejs");

app.use(express.json({ limit: "64kb", strict: true }));
app.use((_request, response, next) => {
  response.set({
    "Cache-Control": "no-store",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
  });
  next();
});
app.use("/assets", express.static(join(APP_DIRECTORY, "public"), {
  dotfiles: "deny",
  fallthrough: true,
  index: false,
}));

app.get("/health", (_request, response) => {
  sendJson(response, 200, { status: "ready" });
});

app.get("/", (_request, response) => {
  response.render("home", { title: "Publish" });
});

app.post("/api/posts", createLimit, (request, response) => {
  const title = textField(request.body?.title, 120);
  const body = textField(request.body?.body, 48_000);
  if (!title || !body) return sendJson(response, 400, { error: "Invalid post" });

  prunePosts();
  if (posts.size >= MAX_POSTS) {
    return sendJson(response, 503, { error: "Publishing is temporarily full" });
  }

  const id = randomBytes(16).toString("hex");
  posts.set(id, {
    id,
    title,
    body,
    comments: [],
    state: "published",
    createdAt: new Date().toISOString(),
  });
  return sendJson(response, 201, { id, url: `/posts/${id}` });
});

app.get("/api/posts/:id", (request, response) => {
  if (!validId(request.params.id)) {
    return sendJson(response, 404, { error: "Not found" });
  }

  const post = posts.get(request.params.id);
  if (!post) return sendJson(response, 404, { error: "Not found" });

  return sendJson(response, 200, {
    id: post.id,
    title: post.title,
    body: post.body,
    comments: post.comments,
    state: post.state,
    createdAt: post.createdAt,
  });
});

app.get("/posts/:id", (request, response) => {
  if (!validId(request.params.id)) {
    return response.status(404).type("text").send("Not found");
  }

  const post = posts.get(request.params.id);
  if (!post) return response.status(404).type("text").send("Not found");

  return response.render("post", {
    title: post.title,
    post,
    bodyHtml: marked.parse(post.body),
    publishedAt: formatDate(post.createdAt),
  });
});

app.post("/api/posts/:id/comments", createLimit, (request, response) => {
  if (!validId(request.params.id)) {
    return sendJson(response, 404, { error: "Not found" });
  }

  const post = posts.get(request.params.id);
  const message = textField(request.body?.message, 4_000);
  if (!post || !message) return sendJson(response, 400, { error: "Invalid comment" });
  if (post.comments.length >= MAX_COMMENTS) {
    return sendJson(response, 409, { error: "Discussion is full" });
  }

  const comment = { message, createdAt: new Date().toISOString() };
  post.comments.push(comment);
  return sendJson(response, 201, comment);
});

app.post("/api/posts/:id/report", reportLimit, async (request, response) => {
  if (!validId(request.params.id)) {
    return sendJson(response, 404, { error: "Not found" });
  }

  const post = posts.get(request.params.id);
  if (!post) return sendJson(response, 404, { error: "Not found" });
  if (post.state === "reviewing") {
    return sendJson(response, 409, { error: "Already under review" });
  }

  post.state = "reviewing";
  try {
    const upstream = await fetch(REVIEWER_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ postId: post.id }),
      signal: AbortSignal.timeout(REVIEW_TIMEOUT_MS),
    });
    if (!upstream.ok) throw new Error(`reviewer returned ${upstream.status}`);

    post.state = "reviewed";
    return sendJson(response, 200, { status: "reviewed" });
  } catch (error) {
    console.error("[board] review unavailable:", error.message);
    post.state = "published";
    return sendJson(response, 502, { error: "Review unavailable" });
  }
});

app.use((error, _request, response, _next) => {
  if (error?.type === "entity.parse.failed" || error?.type === "entity.too.large") {
    return sendJson(response, 400, { error: "Invalid request" });
  }

  console.error("[board]", error?.message || error);
  return sendJson(response, 500, { error: "Unexpected error" });
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`community board listening on :${PORT}`);
});
