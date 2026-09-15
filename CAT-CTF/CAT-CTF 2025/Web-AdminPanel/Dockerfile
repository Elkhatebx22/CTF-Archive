FROM node:20

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ENV FLAG=flag{default_flag}

EXPOSE 3000

CMD ["node", "main.js"]