FROM node:20-alpine AS builder

ARG VITE_API_BASE_URL=/api/v1
ARG VITE_APP_NAME=IntelliWealth

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_APP_NAME=$VITE_APP_NAME

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS runtime

LABEL maintainer="IntelliWealth Engineering <engineering@intelliwealth.io>"
LABEL service="frontend"

RUN apk add --no-cache curl && \
    mkdir -p /var/cache/nginx /var/log/nginx /var/run/nginx && \
    chown -R nginx:nginx /var/cache/nginx /var/log/nginx /var/run/nginx

COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html
COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

ENTRYPOINT []
CMD ["nginx", "-g", "daemon off;"]
