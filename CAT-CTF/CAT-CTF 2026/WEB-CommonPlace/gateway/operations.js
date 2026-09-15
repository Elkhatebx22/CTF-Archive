"use strict";

const form = document.querySelector("#asset-form");
const accessCode = document.querySelector("#access-code");
const sourceUrl = document.querySelector("#source-url");
const status = document.querySelector("#operation-status");
const submit = form.querySelector('button[type="submit"]');

form.addEventListener("submit", async event => {
  event.preventDefault();
  submit.disabled = true;
  status.textContent = "Mirroring…";

  try {
    const response = await fetch("/operations/api/proofAssets:ingest", {
      method: "POST",
      credentials: "omit",
      headers: {
        "Authorization": `Bearer ${accessCode.value.trim()}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ sourceUrl: sourceUrl.value }),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.errors?.[0]?.message || "Asset could not be mirrored");
    status.textContent = `${result.data?.bytes ?? 0} bytes mirrored`;
  } catch (error) {
    status.textContent = error.message;
  } finally {
    submit.disabled = false;
  }
});
