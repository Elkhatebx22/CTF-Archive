'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

const crypto = require('node:crypto');
const filesystem = require('node:fs');
const fs = require('node:fs/promises');
const path = require('node:path');
const contentDisposition = require('content-disposition');
const { Plugin } = require('@nocobase/server');

const SPOOL_DIRECTORY = '/app/nocobase/storage/proof-cache';
const MAX_PROOF_SIZE = 512;
const FETCH_TIMEOUT = 5000;
const ACCESS_TOKEN_FILE = process.env.EDITORIAL_ACCESS_TOKEN_FILE || '/run/commonplace-access/token';
const ACCESS_TOKEN = filesystem.readFileSync(ACCESS_TOKEN_FILE, 'ascii').trim();

if (!/^[A-Za-z0-9_-]{32,128}$/.test(ACCESS_TOKEN)) {
  throw new Error('editorial access token must contain 32..128 safe characters');
}

function authorized(ctx) {
  const expected = Buffer.from(`Bearer ${ACCESS_TOKEN}`);
  const supplied = Buffer.from(ctx.request.headers.authorization || '');
  return supplied.length === expected.length && crypto.timingSafeEqual(supplied, expected);
}

function requireSourceUrl(ctx, value) {
  if (typeof value !== 'string' || value.length === 0 || value.length > 2048) {
    ctx.throw(400, 'sourceUrl must be a non-empty URL');
  }

  let parsed;
  try {
    parsed = new URL(value);
  } catch {
    ctx.throw(400, 'sourceUrl must be a valid URL');
  }
  if (!['http:', 'https:'].includes(parsed.protocol) || parsed.username || parsed.password) {
    ctx.throw(400, 'sourceUrl must use HTTP or HTTPS without credentials');
  }
  return parsed.href;
}

function responseFilename(ctx, response) {
  const value = response.headers.get('content-disposition');
  if (!value) ctx.throw(400, 'proof response is missing Content-Disposition');

  let parsed;
  try {
    parsed = contentDisposition.parse(value);
  } catch {
    ctx.throw(400, 'proof response has invalid Content-Disposition');
  }
  const filename = parsed.parameters.filename;
  if (typeof filename !== 'string' || filename.length === 0 || filename.includes('\0')) {
    ctx.throw(400, 'proof response has no usable filename');
  }
  return filename;
}

function validateMetadata(ctx, response) {
  if (!response.ok) ctx.throw(400, `proof metadata returned HTTP ${response.status}`);
  if (response.headers.get('content-type') !== 'application/octet-stream') {
    ctx.throw(400, 'proof must use application/octet-stream');
  }

  const length = Number(response.headers.get('content-length'));
  if (!Number.isSafeInteger(length) || length < 1 || length > MAX_PROOF_SIZE) {
    ctx.throw(400, 'proof metadata has an invalid size');
  }

  const filename = responseFilename(ctx, response);
  if (
    path.posix.basename(filename) !== filename ||
    path.win32.basename(filename) !== filename ||
    !/^[A-Za-z0-9][A-Za-z0-9._-]{0,80}\.proof$/.test(filename)
  ) {
    ctx.throw(400, 'proof metadata has an invalid filename');
  }
  return { filename, length };
}

async function fetchProof(ctx, sourceUrl, method) {
  let response;
  try {
    response = await fetch(sourceUrl, {
      method,
      redirect: 'follow',
      signal: AbortSignal.timeout(FETCH_TIMEOUT),
    });
  } catch {
    ctx.throw(400, 'proof source could not be reached');
  }
  return response;
}

async function readProof(ctx, response, expectedLength) {
  if (!response.ok) ctx.throw(400, `proof download returned HTTP ${response.status}`);
  if (response.headers.get('content-type') !== 'application/octet-stream') {
    ctx.throw(400, 'proof download changed content type');
  }

  let contents;
  try {
    contents = Buffer.from(await response.arrayBuffer());
  } catch {
    ctx.throw(400, 'proof download failed');
  }
  if (contents.length !== expectedLength || contents.length > MAX_PROOF_SIZE) {
    ctx.throw(400, 'proof download changed size');
  }
  return contents;
}

class PluginProofIngestServer extends Plugin {
  async load() {
    await fs.mkdir(SPOOL_DIRECTORY, { recursive: true });

    this.app.resourceManager.define({
      name: 'proofAssets',
      actions: {
        async ingest(ctx, next) {
          if (!authorized(ctx)) ctx.throw(401, 'editorial desk credential required');

          const values = ctx.action.params.values || {};
          const sourceUrl = requireSourceUrl(ctx, values.sourceUrl);

          const metadataResponse = await fetchProof(ctx, sourceUrl, 'HEAD');
          const metadata = validateMetadata(ctx, metadataResponse);

          const downloadResponse = await fetchProof(ctx, sourceUrl, 'GET');
          const deliveredFilename = responseFilename(ctx, downloadResponse);
          const contents = await readProof(ctx, downloadResponse, metadata.length);

          const jobRoot = path.join(SPOOL_DIRECTORY, crypto.randomUUID());
          const destination = path.join(jobRoot, deliveredFilename);
          await fs.mkdir(path.dirname(destination), { recursive: true });
          await fs.writeFile(destination, contents, { flag: 'w' });

          ctx.body = {
            mirrored: metadata.filename,
            bytes: contents.length,
          };
          await next();
        },
      },
    });

    this.app.acl.allow('proofAssets', ['ingest'], 'public');
  }
}

exports.PluginProofIngestServer = PluginProofIngestServer;
exports.default = PluginProofIngestServer;
