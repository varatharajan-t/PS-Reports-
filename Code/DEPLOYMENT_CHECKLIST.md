# Production Deployment Checklist

## Pre-Deployment (Development Environment)

- [ ] All 139 tests passing (`python manage.py test`)
- [ ] Code coverage reviewed (`coverage run && coverage html`)
- [ ] No security vulnerabilities (`safety check`)
- [ ] All migrations created and tested
- [ ] Static files collected locally
- [ ] Documentation updated
- [ ] Git repository clean and committed

## Server Setup

- [ ] Server provisioned (Ubuntu 20.04+ recommended)
- [ ] Python 3.10+ installed
- [ ] PostgreSQL 13+ installed
- [ ] Nginx installed
- [ ] SSL certificate obtained (Let's Encrypt or purchased)
- [ ] Firewall configured (UFW with SSH, HTTP, HTTPS)
- [ ] Application user created (`psreports`)

## Database Configuration

- [ ] PostgreSQL database created (`psreports_prod`)
- [ ] Database user created with secure password
- [ ] Database privileges granted
- [ ] Database connection tested
- [ ] Remote access configured (if needed)

## Application Setup

- [ ] Application code deployed to `/opt/psreports`
- [ ] Virtual environment created
- [ ] All dependencies installed (including production extras)
- [ ] `.env` file created with production settings
- [ ] `SECRET_KEY` generated and configured
- [ ] `DEBUG=False` set in environment
- [ ] `ALLOWED_HOSTS` configured with domain names
- [ ] Database migrations run
- [ ] Static files collected
- [ ] Superuser account created
- [ ] Directory structure verified:
  - [ ] `media/` directory exists
  - [ ] `staticfiles/` directory exists
  - [ ] `backups/database/` directory exists
  - [ ] `logs/` directory exists
  - [ ] `reports/static/` directory exists

## Web Server Configuration

- [ ] Gunicorn configuration file created
- [ ] Systemd service file created (`/etc/systemd/system/psreports.service`)
- [ ] Service enabled and started
- [ ] Service status verified (running)
- [ ] Nginx configuration created
- [ ] Nginx configuration tested (`nginx -t`)
- [ ] Nginx site enabled
- [ ] Nginx restarted successfully

## SSL/HTTPS Setup

- [ ] SSL certificate installed
- [ ] HTTPS configured in Nginx
- [ ] HTTP to HTTPS redirect enabled
- [ ] SSL/TLS settings optimized
- [ ] Certificate auto-renewal configured (if Let's Encrypt)
- [ ] SSL test passed (https://www.ssllabs.com/ssltest/)

## Security Configuration

- [ ] Security headers configured in Nginx
- [ ] Django security settings enabled:
  - [ ] `SECURE_SSL_REDIRECT=True`
  - [ ] `SESSION_COOKIE_SECURE=True`
  - [ ] `CSRF_COOKIE_SECURE=True`
  - [ ] `SECURE_BROWSER_XSS_FILTER=True`
  - [ ] `SECURE_CONTENT_TYPE_NOSNIFF=True`
  - [ ] `X_FRAME_OPTIONS=DENY`
- [ ] File permissions set correctly (755 for dirs, 644 for files)
- [ ] `.env` file permissions set to 600 (read/write owner only)
- [ ] Database password is strong and unique
- [ ] Application runs as non-root user

## Backup Configuration

- [ ] Backup script created (`/opt/psreports/scripts/backup.sh`)
- [ ] Backup script executable
- [ ] Cron job configured for automated backups
- [ ] Backup tested manually
- [ ] Backup log file exists and is writable
- [ ] Backup retention period configured (default: 30 days)
- [ ] Offsite backup strategy planned (optional but recommended)

## Testing & Verification

- [ ] Application accessible via domain name
- [ ] HTTPS working correctly (no mixed content warnings)
- [ ] Admin interface accessible (`/admin/`)
- [ ] Login functionality working
- [ ] User registration working
- [ ] All 7 report types tested:
  - [ ] Budget Report
  - [ ] Budget Updates
  - [ ] Budget Variance
  - [ ] Project Type-wise Report
  - [ ] Cost Center-wise Report
  - [ ] Project Analysis Report
  - [ ] Glimps of Projects
- [ ] File upload working correctly
- [ ] Static files loading (CSS, JavaScript, images)
- [ ] Database queries performing adequately
- [ ] Fullscreen functionality tested for reports
- [ ] Charts rendering correctly
- [ ] Report history tracking working
- [ ] WBS data validation working

## Monitoring Setup

- [ ] Application logs accessible and rotating
- [ ] Nginx access logs configured
- [ ] Nginx error logs configured
- [ ] PostgreSQL logs configured
- [ ] Backup logs configured
- [ ] Log rotation configured (`/etc/logrotate.d/psreports`)
- [ ] Monitoring tools installed (optional: htop, New Relic, DataDog)
- [ ] Alert system configured (optional)

## Maintenance Schedule

- [ ] Daily backup cron job active (recommended: 2 AM)
- [ ] Weekly database maintenance scheduled (recommended: Sunday 4 AM)
- [ ] Monthly security updates planned
- [ ] Quarterly full system review planned

## Documentation

- [ ] Production deployment guide reviewed (`PRODUCTION_DEPLOYMENT_GUIDE.md`)
- [ ] Completion summary reviewed (`COMPLETION_SUMMARY.md`)
- [ ] Troubleshooting procedures documented
- [ ] Emergency rollback procedure documented
- [ ] Server access credentials documented securely
- [ ] Database credentials documented securely
- [ ] Admin account credentials documented securely

## Post-Deployment

- [ ] Stakeholders notified of deployment
- [ ] Training provided to end users (if needed)
- [ ] User documentation distributed
- [ ] Support contact information shared
- [ ] Feedback mechanism established

## Ongoing Maintenance Tasks

### Daily
- [ ] Monitor application logs for errors
- [ ] Check backup success in logs
- [ ] Verify site accessibility

### Weekly
- [ ] Review backup logs
- [ ] Check disk space usage
- [ ] Review database performance

### Monthly
- [ ] Apply security updates (`apt update && apt upgrade`)
- [ ] Review and analyze application logs
- [ ] Test backup restore procedure
- [ ] Review user feedback and issues
- [ ] Update dependencies if needed

### Quarterly
- [ ] Full security audit
- [ ] Performance review and optimization
- [ ] Documentation review and updates
- [ ] Disaster recovery drill

## Emergency Contacts

| Role | Name | Contact |
|------|------|---------|
| System Administrator | | |
| Database Administrator | | |
| Application Developer | | |
| Security Team | | |
| On-Call Support | | |

## Rollback Plan

In case of critical issues:

1. **Immediate Response:**
   ```bash
   sudo systemctl stop psreports
   ```

2. **Restore Database:**
   ```bash
   cd /opt/psreports
   source venv/bin/activate
   python manage.py restore_database backups/database/backup_YYYYMMDD_HHMMSS.sqlite3.gz --force
   ```

3. **Restart Services:**
   ```bash
   sudo systemctl start psreports
   sudo systemctl restart nginx
   ```

4. **Verify:**
   - Check application logs
   - Test critical functionality
   - Notify stakeholders

## Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Developer | | | |
| System Administrator | | | |
| Database Administrator | | | |
| Project Manager | | | |
| Security Officer | | | |

---

**Deployment Date:** _______________

**Production URL:** _______________

**Notes:**
_______________________________________________________
_______________________________________________________
_______________________________________________________
