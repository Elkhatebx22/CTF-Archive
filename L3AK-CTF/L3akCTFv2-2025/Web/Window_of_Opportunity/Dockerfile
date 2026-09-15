FROM node:22-alpine

RUN apk update && apk upgrade && \
    apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    dumb-init

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm i

RUN adduser -D -u 1001 bot && \
    mkdir -p /home/bot && \
    chown -R bot:bot /home/bot /app

COPY . .

USER bot

ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
ENV NODE_ENV=production
ENV FLAG="L3AK{T1gh7_CSRF_y3t_w1nd0w_0p3n3r_w1n5!}"
ENV COOKIE_SECRET="5@Xl7\{[8?2P,hbK1Q~'+K;i`rs£ZQ$@{"

EXPOSE 3000

ENTRYPOINT ["dumb-init", "--"]

CMD ["node", "index.js"]
