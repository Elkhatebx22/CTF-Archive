FROM debian:bookworm-slim@sha256:88200866dfff7ea7f5cbcb6ec7c8a701889efe6fe859fe64d6990e4b07ea4171 AS readflag-builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY operations/readflag.c /src/readflag.c
RUN mkdir -p /out \
    && gcc -static -Os -Wall -Wextra -Werror -o /out/readflag /src/readflag.c \
    && strip /out/readflag

FROM nocobase/nocobase:2.2.7@sha256:dc05cef2902bcaaa96172b8f0d697fae119b2d0c70ec43705c168c35329b0cf1

USER root

ENV PUPPETEER_CACHE_DIR=/opt/puppeteer \
    PUPPETEER_SKIP_CHROME_HEADLESS_SHELL_DOWNLOAD=true

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libcups2 \
        libdbus-1-3 \
        libdrm2 \
        libgbm1 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxkbcommon0 \
        libxrandr2 \
        libxshmfence1 \
        nginx \
        python3 \
        unzip \
        util-linux \
        xdg-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/board
COPY board/package.json board/package-lock.json ./
RUN npm ci --omit=dev
COPY board/app.js ./
COPY board/views ./views
COPY board/public ./public

WORKDIR /srv/reviewer
COPY bot/package.json bot/package-lock.json ./
RUN npm ci --omit=dev
COPY bot/bot.js bot/request_policy.js bot/review_pool.js ./
COPY bot/editorial-companion.zip /tmp/editorial-companion.zip
RUN mkdir -p /app/extension \
    && unzip -q /tmp/editorial-companion.zip -d /app/extension \
    && rm -f /tmp/editorial-companion.zip

WORKDIR /opt/sqlite-driver
RUN npm install --omit=dev --no-package-lock sqlite3@5.1.7

WORKDIR /app/nocobase
COPY operations/plugin /app/nocobase/node_modules/@commonplace/plugin-proof-ingest
COPY --from=readflag-builder --chown=0:0 --chmod=4755 /out/readflag /readflag

ENV HOME=/home/node \
    APPEND_PRESET_BUILT_IN_PLUGINS=@commonplace/plugin-proof-ingest \
    PLUGIN_PACKAGE_PREFIX=@nocobase/plugin-,@nocobase/preset-,@commonplace/plugin- \
    NODE_MODULES_PATH=/app/nocobase/node_modules \
    NODE_PATH=/opt/sqlite-driver/node_modules:/app/nocobase/node_modules \
    APP_PACKAGE_ROOT=/app/nocobase/node_modules/@nocobase/app \
    STORAGE_PATH=/app/nocobase/storage \
    LOCAL_STORAGE_DEST=/app/nocobase/storage/uploads \
    PLUGIN_STORAGE_PATH=/app/nocobase/storage/plugins \
    API_BASE_PATH=/api/ \
    APP_PUBLIC_PATH=/ \
    PLUGIN_STATICS_PATH=/static/plugins/ \
    WS_PATH=/ws

RUN yarn nocobase postinstall \
    && test "$(stat -c '%a %u %g' /readflag)" = "4755 0 0" \
    && groupadd --gid 10004 editorial \
    && usermod --append --groups editorial node \
    && useradd --no-create-home --uid 10001 --user-group reviewer \
    && useradd --no-create-home --uid 10002 --user-group --groups editorial desk \
    && useradd --no-create-home --uid 10003 --user-group board \
    && mkdir -p \
        /app/nocobase/storage/apps/main \
        /app/nocobase/storage/database \
        /app/nocobase/storage/proof-cache \
        /app/nocobase/storage/logs \
        /app/nocobase/storage/plugins \
        /app/nocobase/storage/uploads \
        /home/node/.nocobase \
        /home/node/.pm2 \
    && chown -R node:node /app/nocobase/storage /home/node

COPY desk-api/app.py /srv/desk/app.py
COPY gateway/operations.html /usr/share/nginx/html/operations.html
COPY gateway/operations.js /usr/share/nginx/html/operations.js
COPY runtime/nginx.conf /etc/nginx/nginx.conf
COPY runtime/start.sh /usr/local/bin/commonplace-start
COPY runtime/healthcheck.sh /usr/local/bin/commonplace-healthcheck
RUN chmod 0755 /usr/local/bin/commonplace-start /usr/local/bin/commonplace-healthcheck

WORKDIR /
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/commonplace-start"]
