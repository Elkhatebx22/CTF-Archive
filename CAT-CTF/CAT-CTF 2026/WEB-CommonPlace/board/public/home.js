"use strict";

const form = document.querySelector("#publisher");
const status = document.querySelector("#status");

form.addEventListener("submit", async event => {
  event.preventDefault();
  status.textContent = "Publishing…";

  try {
    const response = await fetch("/api/posts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: document.querySelector("#title").value,
        body: document.querySelector("#body").value,
      }),
    });
    const result = await response.json();
    if (!response.ok) {
      status.textContent = result.error || "Could not publish";
      return;
    }

    location.assign(result.url);
  } catch {
    status.textContent = "Could not publish";
  }
});
