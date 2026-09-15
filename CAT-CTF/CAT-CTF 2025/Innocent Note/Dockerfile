# Use an official Node.js runtime as a parent image
FROM node:18-slim

# Install dependencies for puppeteer
RUN apt-get update && apt-get install -y \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
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
    lsb-release \
    wget \
    xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install application dependencies
RUN npm install

# Generate flag
RUN echo "CATF{0n3_bl1nk_4nd_1_w4s_r3nd3r3d}" > /flag.txt

# Copy the main server file
COPY server.js .

# Copy all source code directories into the container
COPY controllers ./controllers
COPY middleware ./middleware
COPY models ./models
COPY utils ./utils
COPY public ./public
COPY routes ./routes
COPY services ./services
COPY views ./views

ENV ADMIN_PASSWORD=sadsa

# Your app binds to port 3000, so expose i`t
EXPOSE 3000

# Define the command to run the app
CMD [ "node", "server.js" ]
