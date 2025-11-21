#!/bin/bash

set -e

echo "🚀 Starting ZaNuri AI Production Deployment..."

# Variables
APP_DIR="/opt/zanuri-ai"
BACKUP_DIR="/opt/backups/zanuri-ai"
DATE=$(date +%Y%m%d_%H%M%S)
MODEL_DIR="$APP_DIR/models"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "1. 📥 Pulling latest changes..."
cd $APP_DIR
git fetch origin
git reset --hard origin/main

echo "2. 💾 Backing up database..."
docker-compose exec -T db pg_dump -U zanuri zanuri_ai > $BACKUP_DIR/backup_$DATE.sql

echo "3. 🐳 Pulling latest images..."
docker-compose pull

echo "4. ⏹️ Stopping existing services..."
docker-compose down

echo "5. 🔄 Checking for model updates..."
# Download new models if specified in model registry
docker-compose run --rm zanuri-ai python scripts/download_models.py --production

echo "6. 🗃️ Migrating database..."
docker-compose run --rm zanuri-ai python manage.py migrate

echo "7. 🧹 Cleaning cache..."
docker-compose run --rm zanuri-ai python manage.py clear_cache

echo "8. 🚀 Starting services..."
docker-compose up -d

echo "9. ✅ Running health checks..."
sleep 30

# Check application health
echo "Checking application health..."
curl -f http://localhost/health || exit 1

# Check model loading status
echo "Checking model status..."
MODEL_STATUS=$(curl -s http://localhost/api/v1/models/status | jq -r '.status')
if [ "$MODEL_STATUS" != "ready" ]; then
    echo "❌ Models not ready. Status: $MODEL_STATUS"
    exit 1
fi

echo "10. 🧹 Cleaning up..."
# Keep last 10 backups
ls -t $BACKUP_DIR/backup_*.sql | tail -n +11 | xargs rm -f

# Clean up docker images and containers
docker system prune -f

echo "🎉 ZaNuri AI Production Deployment Completed Successfully!"
echo "📊 Application is running and models are ready for inference."