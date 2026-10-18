# ==============================================================================
# SecureFlow AI - Admin SOC Console Production Dockerfile
# ==============================================================================
# Multi-stage build: compiles React/Vite assets and serves with Nginx Alpine
# ==============================================================================

# Stage 1: Build React Vite SPA
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . ./
RUN npm run build

# Stage 2: Hardened Nginx Web Server
FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
