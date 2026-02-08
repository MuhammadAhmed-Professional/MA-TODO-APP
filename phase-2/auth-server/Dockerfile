# Phase 2 Auth Server - Node.js Dockerfile
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install ALL dependencies (including devDependencies for build)
RUN npm install

# Copy application code
COPY . .

# Build TypeScript code
RUN npm run build

# Note: Skip npm prune --production to avoid breaking better-sqlite3 native bindings

# Expose port
EXPOSE 3001

# Start server
CMD ["npm", "start"]
