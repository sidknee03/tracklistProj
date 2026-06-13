#!/usr/bin/env bash
# One-shot deploy script: build image -> push to ECR -> update ECS service
set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
REPO_NAME="music-api"
CLUSTER="music-analytics-cluster"
SERVICE="music-api-service"

# 1. Ensure ECR repo exists
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}"

aws ecr describe-repositories --repository-names "$REPO_NAME" --region "$REGION" 2>/dev/null || \
    aws ecr create-repository --repository-name "$REPO_NAME" --region "$REGION"

# 2. Build & push
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
docker build -t "$REPO_NAME" ./backend
docker tag "${REPO_NAME}:latest" "${ECR_URI}:latest"
docker push "${ECR_URI}:latest"

# 3. Force new ECS deployment
aws ecs update-service --cluster "$CLUSTER" --service "$SERVICE" --force-new-deployment --region "$REGION"

echo "Deployed ${ECR_URI}:latest to ${SERVICE}"
