#!/bin/bash
set -Eeuo pipefail

install -d -o root -g editorial -m 0750 /run/commonplace/access
install -d -o root -g root -m 0700 /run/commonplace-final

case "$(stat -c '%a' /run/secrets/final-flag)" in
  400|600) ;;
  *)
    echo "final value source must be readable only by its owner" >&2
    exit 1
    ;;
esac

umask 0027
od -An -N32 -tx1 /dev/urandom | tr -d ' \n' > /run/commonplace/access/token
chown root:editorial /run/commonplace/access/token
chmod 0440 /run/commonplace/access/token
install -o root -g root -m 0400 /run/secrets/final-flag /run/commonplace-final/flag

setpriv --reuid=1000 --regid=1000 --init-groups mkdir -p \
  /home/node/.nocobase \
  /home/node/.pm2 \
  /app/nocobase/storage/apps/main \
  /app/nocobase/storage/database \
  /app/nocobase/storage/proof-cache \
  /app/nocobase/storage/logs \
  /app/nocobase/storage/plugins \
  /app/nocobase/storage/uploads
setpriv --reuid=1000 --regid=1000 --init-groups chmod 0700 \
  /home/node/.nocobase \
  /home/node/.pm2
setpriv --reuid=1000 --regid=1000 --init-groups chmod 0750 \
  /app/nocobase/storage/apps/main \
  /app/nocobase/storage/database \
  /app/nocobase/storage/proof-cache \
  /app/nocobase/storage/logs \
  /app/nocobase/storage/plugins \
  /app/nocobase/storage/uploads
mkdir -p /tmp/browser-home /tmp/nginx
chown root:root /tmp/browser-home /tmp/nginx
chmod 0700 /tmp/browser-home
chmod 0750 /tmp/nginx
chown reviewer:reviewer /tmp/browser-home
chown www-data:www-data /tmp/nginx

touch /run/commonplace-review-slots/slot-0.lock
touch /run/commonplace-review-slots/slot-1.lock
chmod 0666 /run/commonplace-review-slots/slot-0.lock
chmod 0666 /run/commonplace-review-slots/slot-1.lock

pids=()
stopping=0

start_as() {
  local uid="$1"
  local gid="$2"
  shift 2
  setpriv --reuid="$uid" --regid="$gid" --init-groups "$@" &
  pids+=("$!")
}

stop_all() {
  if (( stopping )); then
    return
  fi
  stopping=1
  trap - TERM INT EXIT
  kill -TERM "${pids[@]}" 2>/dev/null || true
  for pid in "${pids[@]}"; do
    wait "$pid" 2>/dev/null || true
  done
}

trap stop_all TERM INT EXIT

start_as 10003 10003 env \
  PORT=4000 \
  REVIEWER_URL=http://bot:5000/jobs \
  REVIEW_TIMEOUT_MS=900000 \
  node /srv/board/app.js

start_as 10002 10002 env \
  PORT=3000 \
  EDITORIAL_ACCESS_TOKEN_FILE=/run/commonplace/access/token \
  COMPANION_ORIGIN=chrome-extension://dpmmgjgocnenankmgchlmkabpnbgpgmd \
  CONNECTION_TTL_SECONDS=300 \
  python3 /srv/desk/app.py

start_as 10001 10001 env \
  PORT=5000 \
  PUBLICATION_ORIGIN=http://board:4000 \
  REVIEW_SLOT_DIRECTORY=/run/commonplace-review-slots \
  REVIEW_SLOT_COUNT=2 \
  REVIEW_SLOT_WAIT_MS=840000 \
  node /srv/reviewer/bot.js

start_as 1000 1000 env \
  EDITORIAL_ACCESS_TOKEN_FILE=/run/commonplace/access/token \
  /app/nocobase/node_modules/.bin/pm2-runtime \
  start /app/nocobase/node_modules/@nocobase/app/lib/index.js -- start --quickstart

start_as 33 33 nginx -g 'daemon off;'

set +e
wait -n "${pids[@]}"
status="$?"
set -e
stop_all
exit "$status"
