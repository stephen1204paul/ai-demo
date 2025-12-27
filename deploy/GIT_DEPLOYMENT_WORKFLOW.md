# Git-Based Deployment Workflow

This guide covers deploying and updating your AI Comedy Lab application using Git.

## Prerequisites

- GitHub/GitLab/Bitbucket account
- Git installed on your local machine
- DigitalOcean droplet with Ubuntu 22.04

---

## Part 1: Initial Git Setup (Local Machine)

### Step 1: Initialize Git Repository

```bash
# Navigate to your project directory
cd /Users/stephenpaulsamynathan/Code/web/group-project

# Initialize git (if not already done)
git init

# Check what will be committed
git status

# Add all files (sensitive files already excluded by .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: AI Comedy Lab application"
```

### Step 2: Create Remote Repository

**Option A: GitHub (Recommended)**

1. Go to https://github.com/new
2. Repository name: `ai-comedy-lab`
3. Choose **Private** (recommended for production apps)
4. Don't initialize with README (we already have code)
5. Click "Create repository"

**Option B: GitLab**

1. Go to https://gitlab.com/projects/new
2. Project name: `ai-comedy-lab`
3. Visibility: **Private**
4. Click "Create project"

### Step 3: Push to Remote Repository

```bash
# Add remote origin (replace with your actual URL)
# GitHub:
git remote add origin https://github.com/yourusername/ai-comedy-lab.git

# Or GitLab:
git remote add origin https://gitlab.com/yourusername/ai-comedy-lab.git

# Push code to remote
git branch -M main
git push -u origin main
```

### Step 4: Verify Files Were Pushed

Check your repository on GitHub/GitLab. You should see:
- ✅ Application code (`app/`, `migrations/`, etc.)
- ✅ Deployment files (`deploy/`)
- ✅ Requirements (`requirements.txt`)
- ✅ Documentation files
- ❌ `.env` file (should NOT be present - sensitive)
- ❌ `venv/` directory (should NOT be present)

---

## Part 2: Initial Deployment to DigitalOcean

### Step 1: Create SSH Key for Deployment (Optional but Recommended)

For private repositories, set up SSH key authentication:

```bash
# On your droplet
ssh root@your-droplet-ip

# Generate SSH key
ssh-keygen -t ed25519 -C "droplet@ai-comedy-lab"

# Press Enter for all prompts (no passphrase for automation)

# Display public key
cat ~/.ssh/id_ed25519.pub
```

**Add this key to your Git provider:**

- **GitHub**: Settings → SSH and GPG keys → New SSH key
- **GitLab**: Preferences → SSH Keys

### Step 2: Run Automated Deployment Script

```bash
# On your droplet
cd /root

# Download the setup script (first time only)
curl -o setup-server.sh https://raw.githubusercontent.com/yourusername/ai-comedy-lab/main/deploy/setup-server.sh

# Or if you prefer to clone just to get the script
git clone https://github.com/yourusername/ai-comedy-lab.git temp-repo
cp temp-repo/deploy/setup-server.sh .
rm -rf temp-repo

# Make executable and run
chmod +x setup-server.sh
sudo bash setup-server.sh
```

When prompted, enter your repository URL:
- **HTTPS** (public repos or with PAT): `https://github.com/yourusername/ai-comedy-lab.git`
- **SSH** (recommended for private repos): `git@github.com:yourusername/ai-comedy-lab.git`

### Step 3: Configure Environment Variables

```bash
# Edit .env file
nano /var/www/ai-comedy-lab/.env
```

Update these values:
```env
SECRET_KEY=your-generated-secret-key
DATABASE_URL=postgresql://ai_comedy_user:your-password@localhost:5432/ai_comedy_lab
OPENROUTER_API_KEY=your-actual-api-key
OPENROUTER_SITE_URL=http://your-domain.com
```

### Step 4: Complete Setup

```bash
# Populate database
cd /var/www/ai-comedy-lab
sudo -u www-data venv/bin/python scripts/populate_data.py
sudo -u www-data venv/bin/python scripts/generate_embeddings.py

# Restart service
sudo systemctl restart ai-comedy-lab

# Check status
sudo systemctl status ai-comedy-lab
```

---

## Part 3: Making Updates and Deploying Changes

### Workflow for Code Updates

**On Your Local Machine:**

```bash
# 1. Make your code changes
# Edit files as needed...

# 2. Test locally
python run.py

# 3. Stage changes
git add .

# 4. Commit with descriptive message
git commit -m "Add new feature: improved dialogue search"

# 5. Push to remote
git push origin main
```

**On Your Droplet:**

```bash
# 1. SSH into droplet
ssh root@your-droplet-ip

# 2. Navigate to application directory
cd /var/www/ai-comedy-lab

# 3. Pull latest changes
sudo -u www-data git pull origin main

# 4. Install any new dependencies
sudo -u www-data venv/bin/pip install -r requirements.txt

# 5. Run database migrations (if any)
sudo -u www-data venv/bin/flask db upgrade

# 6. Restart application
sudo systemctl restart ai-comedy-lab

# 7. Verify deployment
sudo systemctl status ai-comedy-lab
sudo journalctl -u ai-comedy-lab -n 50
```

### Quick Update Script

Create this script on your droplet for faster updates:

```bash
# Create update script
nano /root/update-app.sh
```

Add this content:

```bash
#!/bin/bash
set -e

echo "Updating AI Comedy Lab..."

cd /var/www/ai-comedy-lab

echo "[1/5] Pulling latest code..."
sudo -u www-data git pull origin main

echo "[2/5] Installing dependencies..."
sudo -u www-data venv/bin/pip install -r requirements.txt

echo "[3/5] Running migrations..."
sudo -u www-data venv/bin/flask db upgrade

echo "[4/5] Restarting application..."
systemctl restart ai-comedy-lab

echo "[5/5] Checking status..."
systemctl status ai-comedy-lab --no-pager

echo ""
echo "Update complete! Application is running."
echo "View logs: journalctl -u ai-comedy-lab -f"
```

Make it executable:

```bash
chmod +x /root/update-app.sh
```

Now you can update with a single command:

```bash
sudo /root/update-app.sh
```

---

## Part 4: Advanced Deployment Patterns

### Using Git Branches for Environments

**Development Branch:**

```bash
# On local machine
git checkout -b development
# Make experimental changes
git push origin development

# On droplet (development server)
cd /var/www/ai-comedy-lab
sudo -u www-data git checkout development
sudo -u www-data git pull origin development
sudo systemctl restart ai-comedy-lab
```

**Production Branch:**

```bash
# On local machine (merge tested changes)
git checkout main
git merge development
git push origin main

# On droplet (production server)
cd /var/www/ai-comedy-lab
sudo -u www-data git checkout main
sudo -u www-data git pull origin main
sudo systemctl restart ai-comedy-lab
```

### Deployment with Tags (Recommended for Production)

Tag releases for better version control:

```bash
# On local machine
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# On droplet (deploy specific version)
cd /var/www/ai-comedy-lab
sudo -u www-data git fetch --tags
sudo -u www-data git checkout v1.0.0
sudo systemctl restart ai-comedy-lab
```

View deployed version:

```bash
cd /var/www/ai-comedy-lab
git describe --tags
```

---

## Part 5: Automated Deployments with Git Webhooks

### Option A: Manual Webhook Script

Create a webhook endpoint on your server:

```bash
# Install webhook utility
apt install webhook

# Create webhook script
nano /root/deploy-webhook.sh
```

Add content:

```bash
#!/bin/bash
cd /var/www/ai-comedy-lab
sudo -u www-data git pull origin main
sudo -u www-data venv/bin/pip install -r requirements.txt
sudo -u www-data venv/bin/flask db upgrade
systemctl restart ai-comedy-lab
```

Make executable:

```bash
chmod +x /root/deploy-webhook.sh
```

Configure webhook to trigger this script on push events.

### Option B: GitHub Actions (Recommended)

Create `.github/workflows/deploy.yml` in your repository:

```yaml
name: Deploy to DigitalOcean

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Deploy to droplet
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.DROPLET_IP }}
        username: root
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          cd /var/www/ai-comedy-lab
          sudo -u www-data git pull origin main
          sudo -u www-data venv/bin/pip install -r requirements.txt
          sudo -u www-data venv/bin/flask db upgrade
          systemctl restart ai-comedy-lab
```

**Setup GitHub Secrets:**

1. Go to your repository → Settings → Secrets → Actions
2. Add secrets:
   - `DROPLET_IP`: Your droplet IP address
   - `SSH_PRIVATE_KEY`: Your SSH private key

Now every push to `main` automatically deploys!

---

## Part 6: Rollback Strategy

### Quick Rollback to Previous Version

```bash
# On droplet
cd /var/www/ai-comedy-lab

# View recent commits
git log --oneline -10

# Rollback to previous commit
sudo -u www-data git reset --hard HEAD~1

# Or rollback to specific commit
sudo -u www-data git reset --hard <commit-hash>

# Restart application
sudo systemctl restart ai-comedy-lab
```

### Rollback to Specific Tag

```bash
cd /var/www/ai-comedy-lab
sudo -u www-data git checkout v1.0.0
sudo systemctl restart ai-comedy-lab
```

---

## Part 7: Best Practices

### Pre-Deployment Checklist

- [ ] Test changes locally
- [ ] Run tests (if you have them)
- [ ] Check migrations work: `flask db upgrade`
- [ ] Update `requirements.txt` if dependencies changed
- [ ] Review changes: `git diff`
- [ ] Write clear commit message
- [ ] Tag version for production releases

### Deployment Checklist

- [ ] Pull latest code
- [ ] Install dependencies
- [ ] Run migrations
- [ ] Restart service
- [ ] Check logs for errors
- [ ] Test application in browser
- [ ] Monitor for 5-10 minutes

### Git Workflow Tips

```bash
# View what changed before pulling
git fetch origin
git diff main origin/main

# Stash local changes before pulling
git stash
git pull
git stash pop

# Check current branch and status
git status
git branch

# View deployment history
git log --oneline --graph --decorate
```

---

## Part 8: Troubleshooting

### "Permission denied" on Git Pull

```bash
# Fix ownership
chown -R www-data:www-data /var/www/ai-comedy-lab

# Or run as www-data
sudo -u www-data git pull origin main
```

### Merge Conflicts During Pull

```bash
# If you have local changes conflicting with remote
cd /var/www/ai-comedy-lab

# Option 1: Discard local changes
sudo -u www-data git reset --hard origin/main

# Option 2: Stash local changes
sudo -u www-data git stash
sudo -u www-data git pull
sudo -u www-data git stash pop
```

### Authentication Failed (Private Repo)

**For HTTPS:**

```bash
# Use Personal Access Token (PAT)
# Generate PAT on GitHub: Settings → Developer settings → Personal access tokens
git remote set-url origin https://YOUR_TOKEN@github.com/username/repo.git
```

**For SSH (Recommended):**

```bash
# Make sure SSH key is added to GitHub/GitLab
cat ~/.ssh/id_ed25519.pub

# Test SSH connection
ssh -T git@github.com

# Change remote to SSH
git remote set-url origin git@github.com:username/ai-comedy-lab.git
```

### Accidentally Committed Secrets

If you accidentally committed `.env` or secrets:

```bash
# Remove from git history (⚠️ rewrites history)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (if already pushed)
git push origin --force --all

# Rotate all exposed secrets immediately!
```

---

## Summary: Daily Workflow

**Development:**

```bash
# Local machine
git pull                          # Get latest
# ... make changes ...
git add .
git commit -m "Descriptive message"
git push origin main
```

**Deployment:**

```bash
# On droplet
/root/update-app.sh               # Automated update
# OR manually:
cd /var/www/ai-comedy-lab
sudo -u www-data git pull origin main
sudo systemctl restart ai-comedy-lab
```

Your git-based deployment workflow is now complete! This approach gives you version control, easy rollbacks, and a clear deployment history.
