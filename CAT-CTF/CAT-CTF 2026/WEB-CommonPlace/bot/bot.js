"use strict";

const express = require("express");
const rateLimit = require("express-rate-limit");
const puppeteer = require("puppeteer");
const { allowedRequest, configuredOrigin } = require("./request_policy.js");
const { createReviewPool } = require("./review_pool.js");

const PORT = Number.parseInt(process.env.PORT || "8080", 10);
const OPEN_DELAY_MS = Number.parseInt(process.env.OPEN_DELAY_MS || "2000", 10);
const CLOSE_DELAY_MS = Number.parseInt(process.env.CLOSE_DELAY_MS || "2400", 10);
const REVIEW_VIEWPORT = Object.freeze({ width: 1280, height: 720 });
const DISMISS_OFFSET = Object.freeze({ right: 106, bottom: 57 });
const PUBLICATION_ORIGIN = configuredOrigin(
  process.env.PUBLICATION_ORIGIN || "http://board:4000"
);
const reviewPool = createReviewPool();

function delay(milliseconds) {
  return new Promise(resolve => setTimeout(resolve, milliseconds));
}

function validPostId(value) {
  return typeof value === "string" && /^[0-9a-f]{32}$/.test(value);
}

async function runReview(postId) {
  const expectedUrl = new URL(`/posts/${postId}`, PUBLICATION_ORIGIN);
  const browser = await puppeteer.launch({
    enableExtensions: ["/app/extension"],
    headless: true,
    pipe: true,
    env: {
      HOME: "/tmp/browser-home",
      LANG: process.env.LANG || "C.UTF-8",
      PATH: process.env.PATH || "/usr/local/bin:/usr/bin:/bin",
      TZ: process.env.TZ || "UTC",
    },
    args: [
      "--disable-dev-shm-usage",
      "--disable-gpu",
      "--disable-background-networking",
      "--disable-breakpad",
      "--disable-component-update",
      "--no-proxy-server",
      `--window-size=${REVIEW_VIEWPORT.width},${REVIEW_VIEWPORT.height}`,
    ],
  });

  try {
    const page = await browser.newPage();
    await page.setViewport(REVIEW_VIEWPORT);
    page.setDefaultTimeout(10_000);
    page.setDefaultNavigationTimeout(20_000);
    page.on("dialog", dialog => dialog.dismiss().catch(() => undefined));
    page.on("popup", popup => popup.close().catch(() => undefined));
    await page.setRequestInterception(true);
    page.on("request", request => {
      let permitted = false;
      try {
        permitted = allowedRequest(
          new URL(request.url()),
          PUBLICATION_ORIGIN,
          request.isNavigationRequest(),
          request.method()
        );
      } catch {}
      const action = permitted ? request.continue() : request.abort("blockedbyclient");
      action.catch(() => undefined);
    });

    await page.goto(expectedUrl.href, { waitUntil: "domcontentloaded" });
    await delay(OPEN_DELAY_MS);
    if (page.url() !== expectedUrl.href) throw new Error("post left the review page");
    await page.mouse.click(
      REVIEW_VIEWPORT.width - DISMISS_OFFSET.right,
      REVIEW_VIEWPORT.height - DISMISS_OFFSET.bottom
    );
    await delay(CLOSE_DELAY_MS);
  } finally {
    await browser.close();
  }
}

let queue = Promise.resolve();

function serialize(task) {
  const result = queue.then(task, task);
  queue = result.catch(() => undefined);
  return result;
}

const app = express();
app.disable("x-powered-by");
app.use(express.json({ limit: "2kb", strict: true }));
app.use(
  "/jobs",
  rateLimit({
    windowMs: 60_000,
    max: 30,
    standardHeaders: true,
    legacyHeaders: false,
  })
);

app.get("/health", (_request, response) => {
  response.json({ status: "ready" });
});

app.post("/jobs", async (request, response) => {
  const postId = request.body?.postId;
  if (!validPostId(postId)) return response.status(400).json({ error: "invalid post" });

  try {
    await serialize(() => reviewPool.run(() => runReview(postId)));
    return response.json({ status: "complete" });
  } catch (error) {
    console.error("[reviewer]", error.message);
    return response.status(500).json({ error: "review failed" });
  }
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`content reviewer listening on :${PORT}`);
});
