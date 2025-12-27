# Quick Start - Deploy to DigitalOcean

## Step 1: Push Code to GitHub

```bash
# On your local machine
cd /Users/stephenpaulsamynathan/Code/web/group-project

git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ai-comedy-lab.git
git push -u origin main
```

## Step 2: Run These Commands on Your Droplet

```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Download and run setup script
wget https://raw.githubusercontent.com/YOUR_USERNAME/ai-comedy-lab/main/deploy/setup-server.sh
chmod +x setup-server.sh
sudo bash setup-server.sh
```

**When prompted:**
1. Enter your repository URL: `https://github.com/YOUR_USERNAME/ai-comedy-lab.git`
2. Edit `.env` file with your actual values
3. Press Enter to continue

## Step 3: Populate Database

```bash
cd /var/www/ai-comedy-lab
sudo -u www-data venv/bin/python scripts/populate_data.py
sudo -u www-data venv/bin/python scripts/generate_embeddings.py
```

## Step 4: Verify

```bash
# Check if running
sudo systemctl status ai-comedy-lab

# View in browser
# http://your-droplet-ip
```

## Future Updates

```bash
# On local machine
git add .
git commit -m "Your changes"
git push origin main

# On droplet
cd /var/www/ai-comedy-lab
sudo -u www-data git pull origin main
sudo systemctl restart ai-comedy-lab
```

---

## Manual Installation (if script fails)

Run these commands one by one:

```bash
# 1. Update system
apt update && apt upgrade -y

# 2. Install prerequisites
apt install -y software-properties-common wget curl gnupg2 lsb-release

# 3. Add Python 3.11 repository
add-apt-repository -y ppa:deadsnakes/ppa
apt update

# 4. Add PostgreSQL repository
sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
apt update

# 5. Install packages
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip \
  postgresql-15 postgresql-contrib-15 nginx git certbot \
  python3-certbot-nginx ufw build-essential postgresql-server-dev-15

# 6. Build pgvector
cd /tmp
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install
cd ~

# 7. Configure firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# 8. Setup PostgreSQL
sudo -u postgres psql <<EOF
CREATE DATABASE ai_comedy_lab;
CREATE USER ai_comedy_user WITH PASSWORD 'YourStrongPassword123!';
ALTER ROLE ai_comedy_user SET client_encoding TO 'utf8';
ALTER ROLE ai_comedy_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ai_comedy_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ai_comedy_lab TO ai_comedy_user;
\c ai_comedy_lab
CREATE EXTENSION vector;
GRANT ALL ON SCHEMA public TO ai_comedy_user;
EOF

# 9. Clone application
cd /var/www
git clone https://github.com/YOUR_USERNAME/ai-comedy-lab.git
chown -R www-data:www-data /var/www/ai-comedy-lab

# 10. Setup Python environment
cd /var/www/ai-comedy-lab
sudo -u www-data python3.11 -m venv venv
sudo -u www-data venv/bin/pip install --upgrade pip
sudo -u www-data venv/bin/pip install -r requirements.txt

# 11. Create .env file
nano /var/www/ai-comedy-lab/.env
```

Add this to `.env`:

```env
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32

DATABASE_URL=postgresql://ai_comedy_user:YourStrongPassword123!@localhost:5432/ai_comedy_lab

OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_SITE_URL=http://your-ip-or-domain
OPENROUTER_APP_NAME=AI Comedy Lab

EMBEDDING_MODEL=openai/text-embedding-ada-002
RAG_MODEL=openai/gpt-3.5-turbo
AGENT_MODEL=openai/gpt-4-turbo-preview

SIMILARITY_TOP_K=5
SIMILARITY_THRESHOLD=0.7
```

Continue:

```bash
# 12. Set permissions
chown www-data:www-data /var/www/ai-comedy-lab/.env
chmod 600 /var/www/ai-comedy-lab/.env

# 13. Run migrations
cd /var/www/ai-comedy-lab
sudo -u www-data venv/bin/flask db upgrade

# 14. Populate data
sudo -u www-data venv/bin/python scripts/populate_data.py
sudo -u www-data venv/bin/python scripts/generate_embeddings.py

# 15. Setup systemd service
cp /var/www/ai-comedy-lab/deploy/ai-comedy-lab.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ai-comedy-lab
systemctl start ai-comedy-lab

# 16. Setup Nginx
cp /var/www/ai-comedy-lab/deploy/nginx-ai-comedy-lab /etc/nginx/sites-available/ai-comedy-lab

# Edit with your IP/domain
nano /etc/nginx/sites-available/ai-comedy-lab
# Change: server_name your-droplet-ip;

# Enable site
ln -s /etc/nginx/sites-available/ai-comedy-lab /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# 17. Check status
systemctl status ai-comedy-lab
systemctl status nginx
```

Your app should now be live at `http://your-droplet-ip`!

## Troubleshooting

**Check logs:**
```bash
sudo journalctl -u ai-comedy-lab -f
tail -f /var/log/nginx/error.log
```

**Restart services:**
```bash
sudo systemctl restart ai-comedy-lab
sudo systemctl restart nginx
```

**Test database:**
```bash
sudo -u postgres psql -d ai_comedy_lab -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

**Test Python:**
```bash
cd /var/www/ai-comedy-lab
sudo -u www-data venv/bin/python -c "import flask; print(flask.__version__)"
```
