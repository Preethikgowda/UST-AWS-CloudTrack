#!/usr/bin/env bash
set -euo pipefail

DOCKERHUB_USERNAME=${DOCKERHUB_USERNAME:?'Set DOCKERHUB_USERNAME env var'}
IMAGE_TAG=${IMAGE_TAG:-latest}

echo "==> Logging in to Docker Hub"
docker login

echo "==> Building frontend"
docker build \
  --target runtime \
  --build-arg VITE_API_BASE_URL=/api/v1 \
  -t ${DOCKERHUB_USERNAME}/intelliwealth-frontend:${IMAGE_TAG} \
  ./frontend

echo "==> Building portfolio-service"
docker build \
  --target runtime \
  -t ${DOCKERHUB_USERNAME}/intelliwealth-portfolio-service:${IMAGE_TAG} \
  ./portfolio-service

echo "==> Building market-service"
docker build \
  --target runtime \
  -t ${DOCKERHUB_USERNAME}/intelliwealth-market-service:${IMAGE_TAG} \
  ./market-service

echo "==> Pushing images to Docker Hub"
docker push ${DOCKERHUB_USERNAME}/intelliwealth-frontend:${IMAGE_TAG}
docker push ${DOCKERHUB_USERNAME}/intelliwealth-portfolio-service:${IMAGE_TAG}
docker push ${DOCKERHUB_USERNAME}/intelliwealth-market-service:${IMAGE_TAG}

echo "==> Done. Images pushed:"
echo "    ${DOCKERHUB_USERNAME}/intelliwealth-frontend:${IMAGE_TAG}"
echo "    ${DOCKERHUB_USERNAME}/intelliwealth-portfolio-service:${IMAGE_TAG}"
echo "    ${DOCKERHUB_USERNAME}/intelliwealth-market-service:${IMAGE_TAG}"
