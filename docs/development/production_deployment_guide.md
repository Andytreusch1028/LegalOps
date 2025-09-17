# LegalOps Platform - Production Deployment Guide

## Overview
This guide provides comprehensive instructions for deploying the LegalOps platform to production environments, specifically optimized for the Florida launch strategy.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Security Configuration](#security-configuration)
5. [Performance Optimization](#performance-optimization)
6. [Deployment Process](#deployment-process)
7. [Post-Deployment Verification](#post-deployment-verification)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04 LTS or CentOS 8+
- **CPU**: 4+ cores, 2.4GHz+
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 100GB SSD minimum, 500GB recommended
- **Network**: 1Gbps connection minimum

### Software Dependencies
- **Node.js**: v18.17.0 or higher
- **PostgreSQL**: v14.0 or higher
- **Redis**: v6.2 or higher
- **Nginx**: v1.18 or higher
- **Docker**: v20.10 or higher (optional)
- **PM2**: v5.3 or higher (process management)

### Required Services
- **Database**: PostgreSQL with optimized configuration
- **Cache**: Redis for session management and caching
- **Web Server**: Nginx for reverse proxy and static file serving
- **SSL Certificate**: Valid SSL certificate for HTTPS
- **Domain**: Configured domain name with DNS

## Environment Setup

### 1. Server Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget git build-essential software-properties-common

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Redis
sudo apt install -y redis-server

# Install Nginx
sudo apt install -y nginx

# Install PM2 globally
sudo npm install -g pm2
```

### 2. User and Directory Setup
```bash
# Create application user
sudo useradd -m -s /bin/bash legalops
sudo usermod -aG sudo legalops

# Create application directories
sudo mkdir -p /opt/legalops
sudo mkdir -p /var/log/legalops
sudo mkdir -p /etc/legalops
sudo mkdir -p /opt/legalops/backups

# Set permissions
sudo chown -R legalops:legalops /opt/legalops
sudo chown -R legalops:legalops /var/log/legalops
sudo chown -R legalops:legalops /etc/legalops
```

## Database Configuration

### 1. PostgreSQL Setup
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE legalops_production;
CREATE USER legalops_prod WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE legalops_production TO legalops_prod;
\q
```

### 2. Database Optimization
```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/14/main/postgresql.conf

# Add these optimizations:
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 64MB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 3. Database Migration
```bash
# Navigate to application directory
cd /opt/legalops

# Run database migrations
npm run migrate:production

# Verify database setup
npm run db:verify
```

## Security Configuration

### 1. Environment Variables
```bash
# Create production environment file
sudo nano /etc/legalops/.env.production

# Add these variables:
NODE_ENV=production
PORT=3000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=legalops_production
DB_USER=legalops_prod
DB_PASSWORD=your_secure_password
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
JWT_SECRET=your_jwt_secret_key
JWT_REFRESH_SECRET=your_jwt_refresh_secret
ENCRYPTION_KEY=your_encryption_key
BACKUP_ENCRYPTION_KEY=your_backup_encryption_key
UPLOAD_DIR=/opt/legalops/uploads
MAX_FILE_SIZE=10485760
BACKUP_DIRECTORY=/opt/legalops/backups
LOG_LEVEL=info
SECURITY_HEADERS=true
RATE_LIMITING=true
CORS_ORIGIN=https://yourdomain.com
```

### 2. Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3000/tcp
sudo ufw status
```

### 3. SSL Certificate Setup
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test certificate renewal
sudo certbot renew --dry-run
```

## Performance Optimization

### 1. Redis Configuration
```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Add these optimizations:
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
tcp-keepalive 300
timeout 300

# Restart Redis
sudo systemctl restart redis-server
```

### 2. Nginx Configuration
```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/legalops

# Add this configuration:
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none';";

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    # API routes
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Login routes with stricter rate limiting
    location /api/auth/login {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /opt/legalops/frontend/dist/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health {
        proxy_pass http://localhost:3000;
        access_log off;
    }
}

# Enable the site
sudo ln -s /etc/nginx/sites-available/legalops /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Deployment Process

### 1. Application Deployment
```bash
# Clone repository
cd /opt/legalops
sudo -u legalops git clone https://github.com/yourusername/legalops-platform.git .

# Install dependencies
sudo -u legalops npm ci --production

# Build application
sudo -u legalops npm run build

# Set up PM2 configuration
sudo -u legalops pm2 init

# Create PM2 ecosystem file
sudo -u legalops nano ecosystem.config.js
```

### 2. PM2 Configuration
```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'legalops-backend',
    script: './dist/index.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    env_production: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    log_file: '/var/log/legalops/combined.log',
    out_file: '/var/log/legalops/out.log',
    error_file: '/var/log/legalops/error.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    max_memory_restart: '1G',
    node_args: '--max-old-space-size=1024',
    watch: false,
    ignore_watch: ['node_modules', 'logs'],
    max_restarts: 10,
    min_uptime: '10s'
  }]
};
```

### 3. Start Application
```bash
# Start with PM2
sudo -u legalops pm2 start ecosystem.config.js --env production

# Save PM2 configuration
sudo -u legalops pm2 save

# Set up PM2 startup script
sudo -u legalops pm2 startup
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u legalops --hp /home/legalops
```

## Post-Deployment Verification

### 1. Health Checks
```bash
# Check application health
curl -f http://localhost:3000/health || exit 1

# Check database connection
curl -f http://localhost:3000/api/health/database || exit 1

# Check Redis connection
curl -f http://localhost:3000/api/health/redis || exit 1

# Check external health endpoint
curl -f https://yourdomain.com/health || exit 1
```

### 2. Performance Tests
```bash
# Run load tests
npm run test:load

# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://yourdomain.com/api/health

# Monitor system resources
htop
iostat -x 1
```

### 3. Security Verification
```bash
# Check SSL configuration
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Test security headers
curl -I https://yourdomain.com

# Verify firewall
sudo ufw status verbose
```

## Monitoring & Maintenance

### 1. Log Monitoring
```bash
# View application logs
sudo -u legalops pm2 logs

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View system logs
sudo journalctl -u nginx -f
sudo journalctl -u postgresql -f
```

### 2. Backup Procedures
```bash
# Automated backup script
sudo crontab -e

# Add this line for daily backups at 2 AM:
0 2 * * * /opt/legalops/scripts/backup-to-github.sh

# Manual backup
sudo -u legalops npm run backup:full
```

### 3. Update Procedures
```bash
# Update application
cd /opt/legalops
sudo -u legalops git pull origin main
sudo -u legalops npm ci --production
sudo -u legalops npm run build
sudo -u legalops pm2 reload all

# Update system packages
sudo apt update && sudo apt upgrade -y
```

## Troubleshooting

### Common Issues

#### 1. Application Won't Start
```bash
# Check PM2 status
sudo -u legalops pm2 status

# Check logs
sudo -u legalops pm2 logs

# Restart application
sudo -u legalops pm2 restart all
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
sudo -u postgres psql -c "SELECT 1;"

# Check application database config
sudo -u legalops cat /etc/legalops/.env.production | grep DB_
```

#### 3. High Memory Usage
```bash
# Check memory usage
free -h
sudo -u legalops pm2 monit

# Restart if needed
sudo -u legalops pm2 restart all
```

#### 4. SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

### Emergency Procedures

#### 1. Rollback Process
```bash
# Stop application
sudo -u legalops pm2 stop all

# Rollback to previous version
cd /opt/legalops
sudo -u legalops git checkout previous-commit-hash
sudo -u legalops npm ci --production
sudo -u legalops npm run build
sudo -u legalops pm2 start all
```

#### 2. Database Recovery
```bash
# Restore from backup
sudo -u legalops npm run restore:backup -- --backup-id backup-id

# Verify database integrity
sudo -u postgres psql legalops_production -c "SELECT COUNT(*) FROM users;"
```

## Support Contacts

- **Technical Support**: support@legalops.com
- **Emergency Contact**: +1-XXX-XXX-XXXX
- **Documentation**: https://docs.legalops.com
- **Status Page**: https://status.legalops.com

---

**Last Updated**: $(date)
**Version**: 1.0.0
**Environment**: Production

