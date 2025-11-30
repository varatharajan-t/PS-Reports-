# Production Deployment Guide

## PS Reports - Enterprise Reporting System
**Version:** 3.0.0
**Last Updated:** 2025-11-30

---

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Application Configuration](#application-configuration)
5. [Web Server Setup](#web-server-setup)
6. [SSL/HTTPS Configuration](#ssl-https-configuration)
7. [Automated Backups](#automated-backups)
8. [Post-Deployment Tasks](#post-deployment-tasks)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

Before deploying to production, ensure:

- [ ] All 139 tests are passing (`python manage.py test`)
- [ ] Code coverage is acceptable (currently 57% overall, 85%+ for core components)
- [ ] Database migrations are up to date
- [ ] Static files are collected
- [ ] Environment variables are documented
- [ ] Backup strategy is in place
- [ ] Server requirements are met (Python 3.10+, PostgreSQL 13+)

---

## Environment Setup

### 1. Server Requirements

**Minimum Specifications:**
- Ubuntu 20.04 LTS or later (or equivalent)
- Python 3.10 or higher
- PostgreSQL 13 or higher
- 2GB RAM minimum (4GB recommended)
- 20GB disk space
- Nginx web server

### 2. Create Production User

```bash
# Create a dedicated user for the application
sudo adduser psreports
sudo usermod -aG sudo psreports
su - psreports
```

### 3. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and PostgreSQL
sudo apt install -y python3.10 python3.10-venv python3-pip postgresql postgresql-contrib nginx

# Install additional dependencies
sudo apt install -y libpq-dev python3-dev build-essential
```

### 4. Setup Application Directory

```bash
# Create application directory
sudo mkdir -p /opt/psreports
sudo chown psreports:psreports /opt/psreports

# Clone or copy application code
cd /opt/psreports
# (Copy your application files here)

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

---

## Database Configuration

### 1. Create PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE psreports_prod;
CREATE USER psreports_user WITH PASSWORD 'your_secure_password_here';

-- Grant privileges
ALTER ROLE psreports_user SET client_encoding TO 'utf8';
ALTER ROLE psreports_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE psreports_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE psreports_prod TO psreports_user;

-- Exit psql
\q
```

### 2. Configure PostgreSQL for Remote Access (if needed)

Edit `/etc/postgresql/13/main/postgresql.conf`:
```conf
listen_addresses = 'localhost'  # or specific IP
```

Edit `/etc/postgresql/13/main/pg_hba.conf`:
```conf
# Add this line for local connections
local   psreports_prod   psreports_user   md5
host    psreports_prod   psreports_user   127.0.0.1/32   md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### 3. Test Database Connection

```bash
psql -U psreports_user -d psreports_prod -h localhost
# Enter password when prompted
# If successful, you'll see the psql prompt
\q
```

---

## Application Configuration

### 1. Generate Production SECRET_KEY

```bash
# Generate a secure random secret key
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output for use in environment variables.

### 2. Create Environment Configuration

Create `/opt/psreports/.env`:

```bash
# Django Settings
SECRET_KEY='your_generated_secret_key_here'
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip

# Database Configuration
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=psreports_prod
DATABASE_USER=psreports_user
DATABASE_PASSWORD=your_secure_password_here
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

# Static and Media Files
STATIC_ROOT=/opt/psreports/staticfiles
MEDIA_ROOT=/opt/psreports/media
```

### 3. Update django_project/settings.py

Add at the beginning of settings.py:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security Settings
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DATABASE_NAME', 'psreports_prod'),
        'USER': os.environ.get('DATABASE_USER', 'psreports_user'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    }
}

# Static files
STATIC_ROOT = os.environ.get('STATIC_ROOT', BASE_DIR / 'staticfiles')
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', BASE_DIR / 'media')

# Security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

Install python-dotenv:
```bash
pip install python-dotenv
```

### 4. Run Migrations and Collect Static Files

```bash
cd /opt/psreports
source venv/bin/activate

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create directories
mkdir -p media reports/static backups/database
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

---

## Web Server Setup

### 1. Create Gunicorn Configuration

Create `/opt/psreports/gunicorn_config.py`:

```python
"""Gunicorn configuration file for PS Reports"""

import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/opt/psreports/logs/gunicorn_access.log"
errorlog = "/opt/psreports/logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "psreports"

# Server mechanics
daemon = False
pidfile = "/opt/psreports/gunicorn.pid"
user = "psreports"
group = "psreports"
```

Create log directory:
```bash
mkdir -p /opt/psreports/logs
```

### 2. Create Systemd Service

Create `/etc/systemd/system/psreports.service`:

```ini
[Unit]
Description=PS Reports Gunicorn Application
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=psreports
Group=psreports
WorkingDirectory=/opt/psreports
Environment="PATH=/opt/psreports/venv/bin"
EnvironmentFile=/opt/psreports/.env
ExecStart=/opt/psreports/venv/bin/gunicorn \
    --config /opt/psreports/gunicorn_config.py \
    django_project.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable psreports
sudo systemctl start psreports
sudo systemctl status psreports
```

### 3. Configure Nginx

Create `/etc/nginx/sites-available/psreports`:

```nginx
upstream psreports_app {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS (will be enabled after SSL setup)
    # return 301 https://$server_name$request_uri;

    client_max_body_size 100M;

    # Access and error logs
    access_log /var/log/nginx/psreports_access.log;
    error_log /var/log/nginx/psreports_error.log;

    # Static files
    location /static/ {
        alias /opt/psreports/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/psreports/media/;
        expires 7d;
    }

    # Proxy to Gunicorn
    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_buffering off;

        proxy_pass http://psreports_app;
    }

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/psreports /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## SSL/HTTPS Configuration

### Using Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

Certbot will automatically update the Nginx configuration to enable HTTPS.

### Manual SSL Configuration

If using a purchased SSL certificate, update `/etc/nginx/sites-available/psreports`:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Rest of configuration...
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Automated Backups

### 1. Create Backup Script

Create `/opt/psreports/scripts/backup.sh`:

```bash
#!/bin/bash

# PS Reports Automated Backup Script
# This script performs database backup with automatic cleanup

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/backup.log"

# Activate virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Change to project directory
cd "$PROJECT_DIR"

# Run backup with compression and 30-day retention
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting database backup..." >> "$LOG_FILE"

python manage.py backup_database \
    --compress \
    --keep-days 30 \
    --output-dir "$PROJECT_DIR/backups/database" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup completed successfully" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup failed!" >> "$LOG_FILE"
    # Optional: Send email notification
fi

# Backup static files and uploaded media (optional)
tar -czf "$PROJECT_DIR/backups/media_$(date +%Y%m%d_%H%M%S).tar.gz" \
    "$PROJECT_DIR/media" >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup process finished" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
```

Make executable:
```bash
chmod +x /opt/psreports/scripts/backup.sh
```

### 2. Configure Cron Job

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/psreports/scripts/backup.sh

# Alternative: Weekly backup on Sundays at 3 AM
# 0 3 * * 0 /opt/psreports/scripts/backup.sh
```

### 3. Test Backup

```bash
/opt/psreports/scripts/backup.sh
cat /opt/psreports/logs/backup.log
ls -lh /opt/psreports/backups/database/
```

---

## Post-Deployment Tasks

### 1. Verify Application is Running

```bash
# Check Gunicorn service
sudo systemctl status psreports

# Check Nginx
sudo systemctl status nginx

# Check logs
tail -f /opt/psreports/logs/gunicorn_error.log
tail -f /var/log/nginx/psreports_error.log
```

### 2. Access Admin Interface

1. Navigate to `https://your-domain.com/admin/`
2. Login with superuser credentials
3. Verify all models are accessible:
   - Company Codes
   - Project Types
   - WBS Elements
   - Report History

### 3. Test Report Generation

1. Navigate to `https://your-domain.com/`
2. Upload test data files
3. Generate each report type:
   - Budget Report
   - Budget Updates
   - Budget Variance
   - Project Type-wise Report
   - Cost Center-wise Report
   - Project Analysis Report
   - Glimps of Projects

### 4. Verify Backup System

```bash
# Run manual backup
cd /opt/psreports
source venv/bin/activate
python manage.py backup_database --compress

# Verify backup file exists
ls -lh backups/database/

# Test restore (on test database!)
python manage.py restore_database backups/database/backup_*.sqlite3.gz --force
```

### 5. Configure Firewall

```bash
# Install UFW if not already installed
sudo apt install -y ufw

# Allow SSH (important!)
sudo ufw allow OpenSSH

# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Enable firewall
sudo ufw enable
sudo ufw status
```

---

## Monitoring & Maintenance

### 1. Application Monitoring

**Check Service Status:**
```bash
sudo systemctl status psreports
sudo systemctl status nginx
sudo systemctl status postgresql
```

**View Logs:**
```bash
# Application logs
tail -f /opt/psreports/logs/gunicorn_error.log
tail -f /opt/psreports/logs/gunicorn_access.log

# Nginx logs
tail -f /var/log/nginx/psreports_error.log
tail -f /var/log/nginx/psreports_access.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log

# Backup logs
tail -f /opt/psreports/logs/backup.log
```

### 2. Database Maintenance

**Weekly Vacuum (optimize database):**
```bash
# Create maintenance script
cat > /opt/psreports/scripts/db_maintenance.sh << 'EOF'
#!/bin/bash
source /opt/psreports/venv/bin/activate
cd /opt/psreports

# Vacuum and analyze database
PGPASSWORD='your_password' psql -U psreports_user -d psreports_prod << SQL
VACUUM ANALYZE;
REINDEX DATABASE psreports_prod;
SQL
EOF

chmod +x /opt/psreports/scripts/db_maintenance.sh

# Add to crontab (weekly on Sundays at 4 AM)
echo "0 4 * * 0 /opt/psreports/scripts/db_maintenance.sh" | crontab -
```

### 3. Log Rotation

Create `/etc/logrotate.d/psreports`:

```conf
/opt/psreports/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 psreports psreports
    sharedscripts
    postrotate
        systemctl reload psreports > /dev/null 2>&1 || true
    endscript
}
```

### 4. Performance Monitoring

**Install and configure monitoring tools (optional):**

```bash
# Install htop for system monitoring
sudo apt install -y htop

# Install monitoring agent (example: New Relic, DataDog, etc.)
# Follow vendor-specific installation instructions
```

**Monitor database performance:**
```sql
-- Active queries
SELECT pid, age(clock_timestamp(), query_start), usename, query
FROM pg_stat_activity
WHERE query != '<IDLE>' AND query NOT ILIKE '%pg_stat_activity%'
ORDER BY query_start DESC;

-- Database size
SELECT pg_size_pretty(pg_database_size('psreports_prod'));

-- Table sizes
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Troubleshooting

### Common Issues

#### 1. 502 Bad Gateway Error

**Cause:** Gunicorn service not running or not accessible

**Solution:**
```bash
# Check Gunicorn status
sudo systemctl status psreports

# Restart Gunicorn
sudo systemctl restart psreports

# Check logs
tail -f /opt/psreports/logs/gunicorn_error.log
```

#### 2. Static Files Not Loading

**Cause:** Static files not collected or Nginx misconfiguration

**Solution:**
```bash
# Collect static files
cd /opt/psreports
source venv/bin/activate
python manage.py collectstatic --noinput

# Check Nginx configuration
sudo nginx -t

# Verify file permissions
ls -la /opt/psreports/staticfiles/
```

#### 3. Database Connection Errors

**Cause:** PostgreSQL not running or incorrect credentials

**Solution:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection manually
psql -U psreports_user -d psreports_prod -h localhost

# Verify .env file has correct credentials
cat /opt/psreports/.env | grep DATABASE
```

#### 4. Permission Errors

**Cause:** Incorrect file ownership or permissions

**Solution:**
```bash
# Fix ownership
sudo chown -R psreports:psreports /opt/psreports

# Fix permissions
chmod -R 755 /opt/psreports
chmod -R 644 /opt/psreports/media
chmod 600 /opt/psreports/.env
```

#### 5. High Memory Usage

**Cause:** Too many Gunicorn workers

**Solution:**
Edit `/opt/psreports/gunicorn_config.py`:
```python
# Reduce workers
workers = 2  # Start with fewer workers
```

Then restart:
```bash
sudo systemctl restart psreports
```

### Emergency Procedures

#### Rollback Deployment

```bash
# Stop services
sudo systemctl stop psreports

# Restore from backup
cd /opt/psreports
source venv/bin/activate
python manage.py restore_database backups/database/backup_YYYYMMDD_HHMMSS.sqlite3.gz --force

# Restart services
sudo systemctl start psreports
```

#### Complete Service Restart

```bash
sudo systemctl restart postgresql
sudo systemctl restart psreports
sudo systemctl restart nginx
```

---

## Security Best Practices

1. **Keep System Updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Regular Security Audits:**
   ```bash
   # Check for security vulnerabilities in Python packages
   pip install safety
   safety check
   ```

3. **Monitor Failed Login Attempts:**
   - Review Django admin login logs
   - Configure fail2ban for additional protection

4. **Database Security:**
   - Use strong passwords
   - Restrict database access to localhost
   - Regular backups with encryption

5. **File Upload Validation:**
   - Already implemented in the application
   - Monitor upload directory size

---

## Support & Documentation

- **Application Documentation:** `/opt/psreports/COMPLETION_SUMMARY.md`
- **Test Coverage:** Run `coverage html` for detailed report
- **Admin Guide:** Django admin at `/admin/`
- **Backup Logs:** `/opt/psreports/logs/backup.log`
- **Application Logs:** `/opt/psreports/logs/gunicorn_*.log`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0.0 | 2025-11-30 | Production-ready release with all 20 features complete |
| 2.0.0 | 2025-11-29 | Added authentication and report history tracking |
| 1.0.0 | 2025-11-28 | Initial production deployment |

---

**End of Production Deployment Guide**
