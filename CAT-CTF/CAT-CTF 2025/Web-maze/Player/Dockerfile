# Use an official Node.js runtime as a parent image
FROM node:18-slim

# Set the working directory in the container
WORKDIR /usr/src/app

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

# Copy package.json and package-lock.json
COPY package*.json ./

# Install app dependencies
RUN npm install

# Copy app source
COPY . .

# Your app binds to port 3000
EXPOSE 3000

# Define environment variables (empty by default, generated at runtime)
ENV URL="nginx:80" // different in prod
ENV JWT_SECRET=""
ENV ADMIN_PASSWORD=""
ENV ADMIN_2FA_SECRET=""
ENV FLAG="flag{example_flag}"

# Create startup script
RUN echo '#!/bin/bash\n\
if [ -z "$JWT_SECRET" ]; then\n\
  export JWT_SECRET=$(openssl rand -hex 64)\n\
  echo "Generated JWT_SECRET: $JWT_SECRET"\n\
fi\n\
if [ -z "$ADMIN_PASSWORD" ]; then\n\
  export ADMIN_PASSWORD=$(openssl rand -hex 16)\n\
  echo "Generated ADMIN_PASSWORD: $ADMIN_PASSWORD"\n\
fi\n\
if [ -z "$ADMIN_2FA_SECRET" ]; then\n\
  export ADMIN_2FA_SECRET=$(openssl rand -base64 20 | tr -d "=+/" | cut -c1-16)\n\
  echo "Generated ADMIN_2FA_SECRET: $ADMIN_2FA_SECRET"\n\
fi\n\
exec node index.js' > /usr/src/app/start.sh && chmod +x /usr/src/app/start.sh

# Run the startup script
CMD ["./start.sh"]