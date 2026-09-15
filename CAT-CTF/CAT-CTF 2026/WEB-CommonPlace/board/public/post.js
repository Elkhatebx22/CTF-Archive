"use strict";

const postId = document.querySelector("main[data-post-id]").dataset.postId;
const reportButton = document.querySelector("#report");
const reviewStatus = document.querySelector("#review-status");
const commentForm = document.querySelector("#comment-form");
const commentStatus = document.querySelector("#comment-status");

reportButton.addEventListener("click", async () => {
  reportButton.disabled = true;
  reviewStatus.textContent = "Reviewing…";

  try {
    const response = await fetch(`/api/posts/${postId}/report`, { method: "POST" });
    const result = await response.json();
    reviewStatus.textContent = response.ok
      ? "Reviewed"
      : (result.error || "Review unavailable");
  } catch {
    reviewStatus.textContent = "Review unavailable";
  } finally {
    reportButton.disabled = false;
  }
});

commentForm.addEventListener("submit", async event => {
  event.preventDefault();
  const input = document.querySelector("#comment");
  commentStatus.textContent = "Posting…";

  try {
    const response = await fetch(`/api/posts/${postId}/comments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input.value }),
    });
    const result = await response.json();
    if (!response.ok) {
      commentStatus.textContent = result.error || "Could not comment";
      return;
    }

    location.reload();
  } catch {
    commentStatus.textContent = "Could not comment";
  }
});
