# AI Comedy Lab - DigitalOcean Droplet Deployment Guide

Complete step-by-step guide to deploy your Flask application on a DigitalOcean droplet.

## Prerequisites

- DigitalOcean account
- A fresh Ubuntu 22.04 droplet (minimum 2GB RAM recommended)
- Your OpenRouter API key
- Domain name (optional, but recommended for SSL)

## Quick Deploy (Automated)

If you want to use the automated script:

```bash
# 1. SSH into your droplet
ssh root@your-droplet-ip

# 2. Upload deployment files
# On your local machine:
scp -r deploy root@your-droplet-ip:/root/

# 3. Run the setup script
cd /root/deploy
chmod +x setup-server.sh
sudo bash setup-server.sh
```

The script will guide you through the remaining steps.

---

## Manual Deployment (Step-by-Step)

If you prefer manual deployment or need to troubleshoot:

### Step 1: Initial Server Setup

```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Update system packages
apt update && apt upgrade -y

# Create a non-root user (optional but recommended)
adduser deploy
usermod -aG sudo deploy
```

### Step 2: Install System Dependencies

```bash
# Install Python 3.11
apt install -y python3.11 python3.11-venv python3-pip

# Install PostgreSQL 15
apt install -y postgresql-15 postgresql-contrib-15

# Install Nginx
apt install -y nginx

# Install other utilities
apt install -y git certbot python3-certbot-nginx ufw
```

### Step 3: Configure Firewall

```bash
# Allow SSH and HTTP/HTTPS
ufw allow OpenSSH
ufw allow 'Nginx Full'

# Enable firewall
ufw --force enable

# Check status
ufw status
```

### Step 4: Set Up PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt, run:
CREATE DATABASE ai_comedy_lab;
CREATE USER ai_comedy_user WITH PASSWORD 'your-secure-password-here';
ALTER ROLE ai_comedy_user SET client_encoding TO 'utf8';
ALTER ROLE ai_comedy_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ai_comedy_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ai_comedy_lab TO ai_comedy_user;

# Connect to the database
\c ai_comedy_lab

# Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

# Grant schema privileges
GRANT ALL ON SCHEMA public TO ai_comedy_user;

# Exit PostgreSQL
\q
```

### Step 5: Upload Application Files

On your **local machine**, upload the application:

```bash
# Option 1: Using scp
scp -r /path/to/ai-comedy-lab root@your-droplet-ip:/var/www/

# Option 2: Using git (if repository is set up)
ssh root@your-droplet-ip
cd /var/www
git clone https://github.com/yourusername/ai-comedy-lab.git

# Option 3: Using rsync (recommended for updates)
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '.git' \
  /path/to/ai-comedy-lab/ root@your-droplet-ip:/var/www/ai-comedy-lab/
```

### Step 6: Set Up Application Directory

```bash
# Create directory if it doesn't exist
mkdir -p /var/www/ai-comedy-lab

# Set permissions
chown -R www-data:www-data /var/www/ai-comedy-lab
cd /var/www/ai-comedy-lab
```

### Step 7: Create Python Virtual Environment

```bash
# Create virtual environment
sudo -u www-data python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Deactivate
deactivate
```

### Step 8: Configure Environment Variables

```bash
# Create .env file
nano /var/www/ai-comedy-lab/.env
```

Add the following content (replace placeholders):

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-use-openssl-rand-hex-32

# Database Configuration
DATABASE_URL=postgresql://ai_comedy_user:your-password@localhost:5432/ai_comedy_lab

# OpenRouter API
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
OPENROUTER_SITE_URL=http://your-domain.com
OPENROUTER_APP_NAME=AI Comedy Lab

# Model Configuration
EMBEDDING_MODEL=openai/text-embedding-ada-002
RAG_MODEL=openai/gpt-3.5-turbo
AGENT_MODEL=openai/gpt-4-turbo-preview

# Vector Search
SIMILARITY_TOP_K=5
SIMILARITY_THRESHOLD=0.7
```

Generate a secure SECRET_KEY:
```bash
openssl rand -hex 32
```

Set proper permissions:
```bash
chown www-data:www-data /var/www/ai-comedy-lab/.env
chmod 600 /var/www/ai-comedy-lab/.env
```

### Step 9: Run Database Migrations

```bash
cd /var/www/ai-comedy-lab
sudo -u www-data venv/bin/flask db upgrade
```

### Step 10: Populate Initial Data

```bash
# Populate dialogues database
sudo -u www-data venv/bin/python scripts/populate_data.py

# Generate embeddings (this may take a few minutes)
sudo -u www-data venv/bin/python scripts/generate_embeddings.py
```

### Step 11: Set Up Systemd Service

```bash
# Copy service file
cp /var/www/ai-comedy-lab/deploy/ai-comedy-lab.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable service to start on boot
systemctl enable ai-comedy-lab

# Start the service
systemctl start ai-comedy-lab

# Check status
systemctl status ai-comedy-lab
```

### Step 12: Configure Nginx

```bash
# Copy Nginx configuration
cp /var/www/ai-comedy-lab/deploy/nginx-ai-comedy-lab /etc/nginx/sites-available/ai-comedy-lab

# Update the configuration with your domain/IP
nano /etc/nginx/sites-available/ai-comedy-lab
# Change: server_name your-domain.com;

# Create symbolic link
ln -s /etc/nginx/sites-available/ai-comedy-lab /etc/nginx/sites-enabled/

# Remove default Nginx site
rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx
```

### Step 13: Set Up SSL (Optional but Recommended)

If you have a domain name:

```bash
# Install SSL certificate
certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow the prompts
# Certbot will automatically configure Nginx for HTTPS

# Test auto-renewal
certbot renew --dry-run
```

---

## Post-Deployment

### Verify Deployment

```bash
# Check if the app is running
systemctl status ai-comedy-lab

# Check application logs
journalctl -u ai-comedy-lab -f

# Check Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Test the application
curl http://localhost:5000
curl http://your-droplet-ip
```

### Common Commands

```bash
# Restart application
sudo systemctl restart ai-comedy-lab

# Stop application
sudo systemctl stop ai-comedy-lab

# View live logs
sudo journalctl -u ai-comedy-lab -f

# Update application code
cd /var/www/ai-comedy-lab
git pull  # or upload new files
sudo -u www-data venv/bin/pip install -r requirements.txt
sudo systemctl restart ai-comedy-lab

# Run database migrations after updates
sudo -u www-data venv/bin/flask db upgrade
```

### Update Deployment

When you make changes to your code:

```bash
# On your local machine
rsync -avz --exclude 'venv' --exclude '__pycache__' \
  /path/to/ai-comedy-lab/ root@your-droplet-ip:/var/www/ai-comedy-lab/

# On the droplet
cd /var/www/ai-comedy-lab
sudo -u www-data venv/bin/pip install -r requirements.txt
sudo -u www-data venv/bin/flask db upgrade
sudo systemctl restart ai-comedy-lab
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check service status
systemctl status ai-comedy-lab

# View detailed logs
journalctl -u ai-comedy-lab -n 50

# Check if port 5000 is in use
netstat -tulpn | grep 5000

# Test Gunicorn manually
cd /var/www/ai-comedy-lab
sudo -u www-data venv/bin/gunicorn --bind 127.0.0.1:5000 'app:create_app()'
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
systemctl status postgresql

# Test database connection
sudo -u postgres psql -d ai_comedy_lab -c "SELECT 1;"

# Check pgvector extension
sudo -u postgres psql -d ai_comedy_lab -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

### Nginx 502 Bad Gateway

```bash
# Check if Flask app is running
systemctl status ai-comedy-lab

# Check Nginx error logs
tail -f /var/log/nginx/error.log

# Test upstream connection
curl http://127.0.0.1:5000
```

### Permission Issues

```bash
# Fix file permissions
chown -R www-data:www-data /var/www/ai-comedy-lab
chmod 600 /var/www/ai-comedy-lab/.env
```

---

## Monitoring and Maintenance

### Set Up Log Rotation

Create `/etc/logrotate.d/ai-comedy-lab`:

```
/var/log/ai-comedy-lab/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload ai-comedy-lab
    endscript
}
```

### Monitor Resource Usage

```bash
# Check memory usage
free -h

# Check disk usage
df -h

# Check running processes
htop

# Monitor database size
sudo -u postgres psql -d ai_comedy_lab -c "SELECT pg_size_pretty(pg_database_size('ai_comedy_lab'));"
```

### Backup Database

```bash
# Create backup
sudo -u postgres pg_dump ai_comedy_lab > backup_$(date +%Y%m%d).sql

# Restore from backup
sudo -u postgres psql ai_comedy_lab < backup_20250127.sql
```

---

## Performance Optimization

### Increase Gunicorn Workers

Edit `/etc/systemd/system/ai-comedy-lab.service`:

```ini
# Calculate workers: (2 x CPU cores) + 1
# For 2 CPU cores: 5 workers
ExecStart=/var/www/ai-comedy-lab/venv/bin/gunicorn --workers 5 --bind 127.0.0.1:5000 'app:create_app()'
```

Then:
```bash
systemctl daemon-reload
systemctl restart ai-comedy-lab
```

### Enable PostgreSQL Connection Pooling

Already configured in `app/config.py` ProductionConfig.

### Add Nginx Caching (Optional)

Add to Nginx config:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=app_cache:10m max_size=1g inactive=60m;

location / {
    proxy_cache app_cache;
    proxy_cache_valid 200 10m;
    # ... rest of proxy settings
}
```

---

## Security Checklist

- [ ] Firewall configured (UFW)
- [ ] SSL certificate installed
- [ ] SSH key-based authentication enabled
- [ ] Root login disabled
- [ ] .env file permissions set to 600
- [ ] Database using strong password
- [ ] SECRET_KEY is randomly generated
- [ ] Regular security updates scheduled
- [ ] Fail2ban installed (optional)

---

## Support

If you encounter issues:

1. Check the logs: `journalctl -u ai-comedy-lab -f`
2. Verify environment variables: `cat /var/www/ai-comedy-lab/.env`
3. Test database connection
4. Check Nginx configuration: `nginx -t`

Your application should now be live at: `http://your-droplet-ip` or `https://your-domain.com`
