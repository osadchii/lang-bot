# CI/CD Setup Guide

Complete guide for setting up automated deployment for the Greek Language Learning Bot.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [SOPS + age Encryption Setup](#sops--age-encryption-setup)
4. [GitHub Secrets Configuration](#github-secrets-configuration)
5. [Production Server Setup](#production-server-setup)
6. [First Deployment](#first-deployment)
7. [Automated Deployment](#automated-deployment)
8. [Troubleshooting](#troubleshooting)
9. [Rollback Procedure](#rollback-procedure)

## Overview

The CI/CD infrastructure consists of:

- **Docker**: Multi-stage containerization for PostgreSQL + Bot
- **SOPS + age**: Encrypted secrets management (safe to commit)
- **GitHub Actions**: Automated testing and deployment
- **SSH**: Secure deployment to production server
- **Automatic migrations**: Database migrations run on container startup

**Deployment Flow:**
```
Push to main → GitHub Actions → Decrypt secrets → SSH to server →
Build Docker image → Run migrations → Deploy containers → Health checks
```

## Prerequisites

### Local Development Machine

- Docker Desktop 24.0+
- SOPS 3.8.1+
- age 1.1.1+
- Git
- SSH client

### Production Server

- Ubuntu 22.04 LTS or newer
- Docker 24.0+ with Docker Compose V2
- 2+ CPU cores, 2GB+ RAM, 20GB+ disk
- SSH access configured
- Port 22 (SSH) open

## SOPS + age Encryption Setup

### 1. Install SOPS and age

#### macOS
```bash
brew install sops age
```

#### Linux
```bash
# Install SOPS
wget https://github.com/getsops/sops/releases/download/v3.8.1/sops-v3.8.1.linux.amd64
chmod +x sops-v3.8.1.linux.amd64
sudo mv sops-v3.8.1.linux.amd64 /usr/local/bin/sops

# Install age
wget https://github.com/FiloSottile/age/releases/download/v1.1.1/age-v1.1.1-linux-amd64.tar.gz
tar xzf age-v1.1.1-linux-amd64.tar.gz
sudo mv age/age /usr/local/bin/
sudo mv age/age-keygen /usr/local/bin/

# Verify installation
sops --version
age --version
```

### 2. Generate age Keys

```bash
# Create directory for age keys
mkdir -p ~/.config/sops/age

# Generate key pair
age-keygen -o ~/.config/sops/age/keys.txt

# Set correct permissions
chmod 600 ~/.config/sops/age/keys.txt

# View your keys
cat ~/.config/sops/age/keys.txt
```

**Output will look like:**
```
# created: 2026-01-20T10:30:00Z
# public key: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AGE-SECRET-KEY-1YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
```

**IMPORTANT:**
- The line starting with `age1` is your **public key** (for .sops.yaml)
- The line starting with `AGE-SECRET-KEY-1` is your **private key** (for GitHub Secrets)
- **NEVER commit the private key to version control**
- Back up `~/.config/sops/age/keys.txt` securely

### 3. Configure .sops.yaml

Edit `.sops.yaml` and replace the placeholder with your public key:

```yaml
creation_rules:
  - path_regex: secrets\.env$
    age: 'age1YOUR_ACTUAL_PUBLIC_KEY_FROM_STEP_2'
    encrypted_regex: '^(.*TOKEN.*|.*KEY.*|.*PASSWORD.*)$'
```

### 4. Create and Encrypt secrets.env

```bash
# Fill in real values in secrets.env
nano secrets.env

# Add your actual credentials:
# TELEGRAM_BOT_TOKEN=123456789:ABCdefGhI...
# OPENAI_API_KEY=sk-proj-abc123...
# POSTGRES_PASSWORD=strong_random_password

# Encrypt the file in-place
sops -e -i secrets.env

# Verify encryption (should see ENC[AES256_GCM,...])
cat secrets.env

# Test decryption
sops -d secrets.env
```

### 5. Allow Encrypted secrets.env in Git

```bash
# Uncomment the line in .gitignore
nano .gitignore

# Change:
# # !secrets.env
# To:
# !secrets.env

# Now you can safely commit the encrypted file
git add secrets.env .sops.yaml
git commit -m "Add encrypted secrets configuration"
```

## GitHub Secrets Configuration

Navigate to: **Repository → Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

#### 1. SOPS_AGE_KEY

The **private key** from `~/.config/sops/age/keys.txt`

```bash
# Copy your private key
cat ~/.config/sops/age/keys.txt | grep "AGE-SECRET-KEY"
```

**Value format:**
```
AGE-SECRET-KEY-1YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
```

#### 2. SSH_PRIVATE_KEY

Generate a dedicated SSH key for GitHub Actions:

```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/deploy_key -N ""

# Copy public key to server
ssh-copy-id -i ~/.ssh/deploy_key.pub user@your-server-ip

# Test connection
ssh -i ~/.ssh/deploy_key user@your-server-ip "echo 'Connection successful'"

# Copy private key for GitHub Secret
cat ~/.ssh/deploy_key
```

**Value:** Entire content of `~/.ssh/deploy_key` including header/footer

#### 3. SSH_HOST

Your production server IP or domain name.

**Examples:**
- `192.168.1.100`
- `bot.example.com`
- `ec2-xx-xx-xx-xx.compute.amazonaws.com`

#### 4. SSH_USER

SSH username on the production server.

**Examples:**
- `ubuntu` (AWS EC2)
- `root` (VPS)
- `deploy` (dedicated user)

### Verify GitHub Secrets

After adding all secrets, verify in GitHub UI:
- Go to **Settings → Secrets and variables → Actions**
- Should see 4 secrets: `SOPS_AGE_KEY`, `SSH_PRIVATE_KEY`, `SSH_HOST`, `SSH_USER`

## Production Server Setup

### 1. Connect to Server

```bash
ssh user@your-server-ip
```

### 2. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Install Docker

```bash
# Install Docker using official script
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group membership
newgrp docker

# Verify Docker installation
docker --version
```

### 4. Install Docker Compose V2

```bash
# Install Docker Compose plugin
sudo apt install docker-compose-plugin -y

# Verify installation
docker compose version
```

### 5. Create Deployment Directory

```bash
# Create directory for the bot
sudo mkdir -p /opt/langbot

# Change ownership to current user
sudo chown $USER:$USER /opt/langbot

# Verify
ls -la /opt/langbot
```

### 6. Configure Firewall (Optional)

```bash
# Install UFW if not present
sudo apt install ufw

# Allow SSH
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### 7. Test Docker

```bash
# Run hello-world container
docker run hello-world

# Should see "Hello from Docker!"
```

## First Deployment

### Option A: Automated via GitHub Actions

**Recommended for production**

```bash
# 1. Commit all changes
git add .
git commit -m "Setup CI/CD infrastructure"

# 2. Push to main branch (triggers deployment)
git push origin main

# 3. Monitor deployment
# Go to: GitHub → Actions → Watch workflow progress

# 4. Verify on server
ssh user@server
cd /opt/langbot
docker compose ps
docker compose logs -f bot
```

### Option B: Manual Deployment

**For testing or emergency deployments**

```bash
# 1. Clone repository on server
ssh user@server
cd /opt/langbot
git clone https://github.com/yourusername/lang-bot.git .

# 2. Create .env file (decrypt secrets locally)
# On local machine:
sops -d secrets.env > .env
scp .env user@server:/opt/langbot/.env

# 3. Build and start containers
ssh user@server
cd /opt/langbot
docker compose build
docker compose up -d

# 4. Check logs
docker compose logs -f bot
```

## Automated Deployment

### Deployment Triggers

Automatic deployment runs on:
- **Push to main branch**
- **Manual trigger** (workflow_dispatch)

### Deployment Process

1. **Test Stage** (continues on error)
   - Run Ruff linting
   - Check Black formatting
   - Run pytest with coverage

2. **Deploy Stage**
   - Install SOPS
   - Decrypt secrets.env → .env
   - Verify critical environment variables
   - Setup SSH connection
   - Sync code to server (rsync)
   - Copy .env to server
   - Build Docker image
   - Stop existing containers (30s timeout)
   - Start new containers
   - Wait for startup (10s)

3. **Health Checks**
   - Container status check
   - Database connectivity test
   - Log error scanning

4. **Cleanup**
   - Remove SSH keys
   - Remove decrypted .env

### Monitor Deployment

```bash
# Watch GitHub Actions workflow
# Repository → Actions → Latest workflow run

# SSH to server and check status
ssh user@server
cd /opt/langbot
docker compose ps
docker compose logs --tail=100 bot

# Check container health
docker inspect langbot-app | grep -A 5 Health
```

## Troubleshooting

### SOPS Decryption Failed

**Error:** `Failed to decrypt secrets`

**Solution:**
```bash
# 1. Verify SOPS_AGE_KEY secret is set correctly
# GitHub → Settings → Secrets → Check SOPS_AGE_KEY

# 2. Test decryption locally
sops -d secrets.env

# 3. Verify .sops.yaml has correct public key
cat .sops.yaml

# 4. Re-encrypt if needed
sops -e -i secrets.env
```

### SSH Connection Failed

**Error:** `Permission denied (publickey)`

**Solution:**
```bash
# 1. Verify SSH_PRIVATE_KEY secret
# Should include BEGIN/END lines

# 2. Test SSH connection locally
ssh -i ~/.ssh/deploy_key user@server

# 3. Verify public key on server
ssh user@server "cat ~/.ssh/authorized_keys"

# 4. Check server SSH config
ssh user@server "sudo cat /etc/ssh/sshd_config | grep PubkeyAuthentication"
```

### Docker Build Failed

**Error:** `Error building Docker image`

**Solution:**
```bash
# 1. Check Dockerfile syntax
docker build -t test -f Dockerfile .

# 2. Check dependencies
cat requirements.txt

# 3. Clear Docker cache
docker builder prune -a

# 4. Check disk space on server
ssh user@server "df -h"
```

### Database Migration Failed

**Error:** `alembic upgrade head failed`

**Solution:**
```bash
# 1. Check migration files
ls -la migrations/versions/

# 2. Check database connectivity
docker compose exec db pg_isready -U postgres

# 3. Check migration logs
docker compose logs bot | grep alembic

# 4. Manual migration (if needed)
docker compose exec bot alembic upgrade head

# 5. Rollback migration
docker compose exec bot alembic downgrade -1
```

### Bot Startup Failed

**Error:** `Container exits immediately`

**Solution:**
```bash
# 1. Check logs
docker compose logs bot

# 2. Check environment variables
docker compose exec bot env | grep -E "TOKEN|KEY|DATABASE"

# 3. Test bot locally
docker compose run --rm bot python -m bot

# 4. Check database connection
docker compose exec bot psql -h db -U postgres -d langbot -c "SELECT 1"
```

### Container Not Healthy

**Error:** `Health check failing`

**Solution:**
```bash
# 1. Check process
docker compose exec bot ps aux | grep python

# 2. Check health check command
docker inspect langbot-app | grep -A 10 Healthcheck

# 3. Manually run health check
docker compose exec bot pgrep -f "python -m bot"

# 4. Check container logs
docker compose logs --tail=200 bot
```

## Rollback Procedure

### Automatic Rollback (Recommended)

```bash
# 1. Identify last working commit
git log --oneline -10

# 2. Revert to previous commit
git revert HEAD
git push origin main

# 3. GitHub Actions will automatically deploy the reverted version
```

### Manual Rollback

```bash
# 1. SSH to server
ssh user@server
cd /opt/langbot

# 2. Stop containers
docker compose down

# 3. Checkout previous commit
git log --oneline -10
git checkout <previous-commit-hash>

# 4. Rollback migration (if needed)
docker compose run --rm bot alembic downgrade -1

# 5. Rebuild and restart
docker compose build --no-cache bot
docker compose up -d

# 6. Verify
docker compose logs -f bot
```

### Emergency Rollback (Complete)

```bash
# 1. Stop all containers
ssh user@server
cd /opt/langbot
docker compose down -v  # WARNING: Removes volumes

# 2. Restore database backup (if available)
# psql -U postgres -d langbot < backup.sql

# 3. Clone fresh copy
cd /opt
rm -rf langbot
git clone https://github.com/yourusername/lang-bot.git langbot
cd langbot
git checkout <working-commit-hash>

# 4. Restore .env
scp .env user@server:/opt/langbot/.env

# 5. Deploy
docker compose up -d

# 6. Verify
docker compose logs -f bot
```

## Best Practices

### Security

1. **Never commit unencrypted secrets**
2. **Rotate SSH keys regularly** (every 90 days)
3. **Use strong PostgreSQL passwords** (32+ characters)
4. **Back up age private key** securely
5. **Enable 2FA on GitHub**
6. **Review GitHub Actions logs** for sensitive data leaks

### Monitoring

1. **Check logs daily**: `docker compose logs --tail=100 bot`
2. **Monitor disk space**: `df -h`
3. **Monitor container status**: `docker compose ps`
4. **Set up alerts** for failed deployments
5. **Monitor bot uptime** in Telegram

### Maintenance

1. **Update dependencies** monthly
2. **Review database size** weekly
3. **Clean old Docker images**: `docker system prune -a`
4. **Back up database** before major changes
5. **Test rollback procedure** quarterly

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [SOPS Documentation](https://github.com/getsops/sops)
- [age Documentation](https://github.com/FiloSottile/age)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review GitHub Actions workflow logs
3. Check project issues: https://github.com/yourusername/lang-bot/issues
4. Contact development team

---

**Last Updated:** 2026-01-21
**Version:** 1.0
