#!/bin/bash

# AI Comedy Lab - DigitalOcean Droplet Deployment Script
# Run this script on your fresh Ubuntu 22.04 droplet
# Usage: sudo bash setup-server.sh

set -e  # Exit on any error

echo "=== AI Comedy Lab Server Setup ==="
echo "This script will set up the complete deployment environment"
echo ""

# Update system
echo "[1/10] Updating system packages..."
apt update && apt upgrade -y

# Install required system packages
echo "[2/10] Installing system dependencies..."
apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql-15 \
    postgresql-contrib-15 \
    nginx \
    git \
    certbot \
    python3-certbot-nginx \
    ufw

# Configure firewall
echo "[3/10] Configuring firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Set up PostgreSQL
echo "[4/10] Setting up PostgreSQL database..."
sudo -u postgres psql <<EOF
CREATE DATABASE ai_comedy_lab;
CREATE USER ai_comedy_user WITH PASSWORD 'CHANGE_THIS_PASSWORD';
ALTER ROLE ai_comedy_user SET client_encoding TO 'utf8';
ALTER ROLE ai_comedy_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ai_comedy_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ai_comedy_lab TO ai_comedy_user;
\c ai_comedy_lab
CREATE EXTENSION IF NOT EXISTS vector;
EOF

echo "[5/10] Granting database privileges..."
sudo -u postgres psql -d ai_comedy_lab <<EOF
GRANT ALL ON SCHEMA public TO ai_comedy_user;
EOF

# Clone application from git
echo "[6/10] Cloning application from git repository..."
read -p "Enter your git repository URL (e.g., https://github.com/username/ai-comedy-lab.git): " GIT_REPO

if [ -z "$GIT_REPO" ]; then
    echo "Error: Git repository URL is required"
    exit 1
fi

# Clone into temporary directory first
cd /var/www
git clone "$GIT_REPO" ai-comedy-lab-temp
if [ $? -ne 0 ]; then
    echo "Error: Failed to clone repository. Please check the URL and try again."
    exit 1
fi

# Move to final location
mv ai-comedy-lab-temp ai-comedy-lab
chown -R www-data:www-data /var/www/ai-comedy-lab

echo "[7/10] Application cloned successfully!"

# Set up Python virtual environment
echo "[8/10] Setting up Python virtual environment..."
cd /var/www/ai-comedy-lab
sudo -u www-data python3.11 -m venv venv
sudo -u www-data venv/bin/pip install --upgrade pip
sudo -u www-data venv/bin/pip install -r requirements.txt

# Create environment file
echo "[9/10] Creating environment file..."
cat > /var/www/ai-comedy-lab/.env <<EOF
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)

# Database Configuration
DATABASE_URL=postgresql://ai_comedy_user:CHANGE_THIS_PASSWORD@localhost:5432/ai_comedy_lab

# OpenRouter API
OPENROUTER_API_KEY=your-openrouter-api-key-here
OPENROUTER_SITE_URL=http://your-domain-or-ip
OPENROUTER_APP_NAME=AI Comedy Lab

# Model Configuration
EMBEDDING_MODEL=openai/text-embedding-ada-002
RAG_MODEL=openai/gpt-3.5-turbo
AGENT_MODEL=openai/gpt-4-turbo-preview

# Vector Search
SIMILARITY_TOP_K=5
SIMILARITY_THRESHOLD=0.7

# OpenAI (optional, for fine-tuning)
# OPENAI_API_KEY=your-openai-key-here
EOF

chown www-data:www-data /var/www/ai-comedy-lab/.env
chmod 600 /var/www/ai-comedy-lab/.env

echo ""
echo "IMPORTANT: Edit /var/www/ai-comedy-lab/.env and update:"
echo "  - DATABASE_URL password"
echo "  - OPENROUTER_API_KEY"
echo "  - OPENROUTER_SITE_URL"
echo ""
read -p "Press Enter once you've updated the .env file..."

# Run database migrations
echo "[10/10] Running database migrations..."
cd /var/www/ai-comedy-lab
sudo -u www-data venv/bin/flask db upgrade

# Set up systemd service
echo "Setting up systemd service..."
cp deploy/ai-comedy-lab.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ai-comedy-lab
systemctl start ai-comedy-lab

# Set up Nginx
echo "Setting up Nginx..."
cp deploy/nginx-ai-comedy-lab /etc/nginx/sites-available/ai-comedy-lab
ln -sf /etc/nginx/sites-available/ai-comedy-lab /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Your application should now be running!"
echo "Check status with: sudo systemctl status ai-comedy-lab"
echo ""
echo "Next steps:"
echo "1. Update Nginx config with your domain: sudo nano /etc/nginx/sites-available/ai-comedy-lab"
echo "2. Populate database: cd /var/www/ai-comedy-lab && sudo -u www-data venv/bin/python scripts/populate_data.py"
echo "3. Generate embeddings: cd /var/www/ai-comedy-lab && sudo -u www-data venv/bin/python scripts/generate_embeddings.py"
echo "4. Set up SSL: sudo certbot --nginx -d your-domain.com"
echo ""
echo "View logs: sudo journalctl -u ai-comedy-lab -f"
echo "Restart app: sudo systemctl restart ai-comedy-lab"
