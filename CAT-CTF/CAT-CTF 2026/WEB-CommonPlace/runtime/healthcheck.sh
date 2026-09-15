#!/bin/sh
set -eu

curl --fail --silent --output /dev/null http://127.0.0.1:4000/health
curl --fail --silent --output /dev/null http://127.0.0.1:3000/health
curl --fail --silent --output /dev/null http://127.0.0.1:8080/health

status="$(curl --silent --output /dev/null --write-out '%{http_code}' \
  --header 'Content-Type: application/json' \
  --data '{}' \
  http://127.0.0.1:13000/api/proofAssets:ingest)"
test "$status" = 401
