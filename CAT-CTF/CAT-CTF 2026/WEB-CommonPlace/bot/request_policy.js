"use strict";

function configuredOrigin(rawValue) {
  const url = new URL(rawValue);
  if (!["http:", "https:"].includes(url.protocol)) throw new Error("unsupported origin");
  if (url.username || url.password || url.pathname !== "/" || url.search || url.hash) {
    throw new Error("invalid origin");
  }
  return url.origin;
}

function allowedRequest(url, pageOrigin, navigationRequest, method) {
  if (url.protocol === "data:") return !navigationRequest;
  if (url.protocol === "blob:") return !navigationRequest && url.origin === pageOrigin;
  if (!["http:", "https:"].includes(url.protocol)) return false;
  if (url.username || url.password) return false;
  if (url.origin === pageOrigin) return true;

  return (
    !navigationRequest &&
    url.origin === "http://gateway:8081" &&
    url.pathname === "/desk/memo" &&
    ["GET", "OPTIONS"].includes(method)
  );
}

module.exports = { allowedRequest, configuredOrigin };
