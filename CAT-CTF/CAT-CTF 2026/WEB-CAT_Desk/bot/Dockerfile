FROM node:22-bookworm-slim

ENV NODE_ENV=production \
    PUPPETEER_CACHE_DIR=/home/node/.cache/puppeteer \
    PUPPETEER_CHROME_VERSION=152.0.7977.82

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        dumb-init \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libcairo2 \
        libcups2 \
        libdbus-1-3 \
        libexpat1 \
        libfontconfig1 \
        libgbm1 \
        libglib2.0-0 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libx11-6 \
        libx11-xcb1 \
        libxcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxi6 \
        libxrandr2 \
        libxrender1 \
        libxss1 \
        libxtst6 \
        unzip \
        xdg-utils \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p "$PUPPETEER_CACHE_DIR" \
    && chown -R node:node /home/node

ENV HOME=/home/node \
    XDG_CACHE_HOME=/home/node/.cache \
    XDG_CONFIG_HOME=/home/node/.config

WORKDIR /bot

COPY package.json package-lock.json ./
RUN PUPPETEER_SKIP_DOWNLOAD=true npm ci --omit=dev --no-audit --no-fund \
    && npx puppeteer browsers install chrome@152.0.7977.82 \
    && test -x /home/node/.cache/puppeteer/chrome/linux-152.0.7977.82/chrome-linux64/chrome \
    && npm cache clean --force \
    && chown -R node:node "$PUPPETEER_CACHE_DIR"

COPY bot.js ./

USER node

EXPOSE 3000

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "bot.js"]
