FROM node:22-bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends chromium ca-certificates fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /bot

COPY package*.json ./
RUN npm ci --omit=dev

COPY server.js .

EXPOSE 9001
CMD ["npm", "start"]
