"use strict";

const { spawn } = require("node:child_process");
const { join } = require("node:path");

const READY_MARKER = "review-slot-ready\n";

function delay(milliseconds) {
  return new Promise(resolve => setTimeout(resolve, milliseconds));
}

function positiveInteger(value, fallback, maximum) {
  const parsed = Number.parseInt(value ?? "", 10);
  if (!Number.isSafeInteger(parsed) || parsed < 1 || parsed > maximum) return fallback;
  return parsed;
}

function attemptLease(lockPath) {
  return new Promise((resolve, reject) => {
    const holder = spawn(
      "/usr/bin/flock",
      [
        "--nonblock",
        "--conflict-exit-code",
        "75",
        lockPath,
        "/bin/sh",
        "-c",
        `printf '${READY_MARKER}'; cat >/dev/null`,
      ],
      { stdio: ["pipe", "pipe", "pipe"] }
    );

    let settled = false;
    let output = "";
    let errors = "";

    const settle = value => {
      if (settled) return;
      settled = true;
      resolve(value);
    };

    holder.once("error", error => {
      if (settled) return;
      settled = true;
      reject(error);
    });

    holder.stderr.on("data", chunk => {
      errors += chunk.toString();
    });

    holder.stdout.on("data", chunk => {
      output += chunk.toString();
      if (!output.includes(READY_MARKER)) return;

      settle({
        async release() {
          if (holder.exitCode !== null) return;
          holder.stdin.end();
          await Promise.race([
            new Promise(resolveExit => holder.once("exit", resolveExit)),
            delay(2_000).then(() => holder.kill("SIGKILL")),
          ]);
        },
      });
    });

    holder.once("exit", code => {
      if (settled) return;
      if (code === 75) return settle(null);
      const detail = errors.trim();
      const suffix = detail ? `: ${detail}` : "";
      const error = new Error(`review slot helper exited with status ${code}${suffix}`);
      settled = true;
      reject(error);
    });
  });
}

function createReviewPool(environment = process.env) {
  const directory = environment.REVIEW_SLOT_DIRECTORY;
  if (!directory) {
    return {
      async run(task) {
        return task();
      },
    };
  }

  const slots = positiveInteger(environment.REVIEW_SLOT_COUNT, 2, 32);
  const pollMilliseconds = positiveInteger(environment.REVIEW_SLOT_POLL_MS, 200, 10_000);
  const waitMilliseconds = positiveInteger(environment.REVIEW_SLOT_WAIT_MS, 840_000, 900_000);
  let cursor = Math.floor(Math.random() * slots);

  async function acquire() {
    const deadline = Date.now() + waitMilliseconds;

    while (Date.now() < deadline) {
      for (let offset = 0; offset < slots; offset += 1) {
        const index = (cursor + offset) % slots;
        const lease = await attemptLease(join(directory, `slot-${index}.lock`));
        if (lease) {
          cursor = (index + 1) % slots;
          return lease;
        }
      }

      const jitter = Math.floor(Math.random() * Math.max(1, pollMilliseconds / 2));
      await delay(pollMilliseconds + jitter);
    }

    throw new Error("content review capacity was unavailable");
  }

  return {
    async run(task) {
      const lease = await acquire();
      try {
        return await task();
      } finally {
        await lease.release();
      }
    },
  };
}

module.exports = { createReviewPool };
