# LegalOps Platform - Local Installation Guide

## Overview
This guide provides step-by-step instructions for installing and running the LegalOps platform locally for testing and rollout preparation.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS, or Linux
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **Network**: Internet connection for initial setup

### Required Software
- **Node.js**: v18.17.0 or higher
- **PostgreSQL**: v14.0 or higher
- **Redis**: v6.2 or higher
- **Git**: Latest version
- **Docker** (optional but recommended)

## Installation Methods

### Method 1: Docker Compose (Recommended)

#### Step 1: Install Docker
```bash
# Windows (using Chocolatey)
choco install docker-desktop

# macOS (using Homebrew)
brew install --cask docker

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install docker.io docker-compose
```

#### Step 2: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/legalops-platform.git
cd legalops-platform

# Create environment file
cp .env.example .env.production
```

#### Step 3: Configure Environment
Edit `.env.production`:
```env
NODE_ENV=production
PORT=3000
DB_HOST=postgres
DB_PORT=5432
DB_NAME=legalops_production
DB_USER=legalops_prod
DB_PASSWORD=your_secure_password
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
JWT_SECRET=your_jwt_secret_key
JWT_REFRESH_SECRET=your_jwt_refresh_secret
ENCRYPTION_KEY=your_encryption_key
BACKUP_ENCRYPTION_KEY=your_backup_encryption_key
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=10485760
BACKUP_DIRECTORY=/app/backups
LOG_LEVEL=info
SECURITY_HEADERS=true
RATE_LIMITING=true
CORS_ORIGIN=http://localhost:3000
```

#### Step 4: Start Services
```bash
# Start all services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f legalops-backend
```

#### Step 5: Verify Installation
```bash
# Test health endpoint
curl http://localhost:3000/health

# Test API
curl http://localhost:3000/api/health/detailed
```

### Method 2: Manual Installation

#### Step 1: Install Dependencies
```bash
# Install Node.js dependencies
cd backend
npm install

# Install system dependencies
# Windows
choco install postgresql redis

# macOS
brew install postgresql redis

# Linux
sudo apt install postgresql postgresql-contrib redis-server
```

#### Step 2: Database Setup
```bash
# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Create database and user
sudo -u postgres psql
CREATE DATABASE legalops_production;
CREATE USER legalops_prod WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE legalops_production TO legalops_prod;
\q
```

#### Step 3: Redis Setup
```bash
# Start Redis
sudo systemctl start redis-server  # Linux
brew services start redis          # macOS

# Test Redis connection
redis-cli ping
```

#### Step 4: Application Setup
```bash
# Build application
npm run build

# Run database migrations
npm run migrate:production

# Start application
npm start
```

### Method 3: Development Mode

#### Step 1: Development Setup
```bash
# Install dependencies
npm install

# Create development environment
cp .env.example .env.development
```

#### Step 2: Configure Development Environment
Edit `.env.development`:
```env
NODE_ENV=development
PORT=3000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=legalops_development
DB_USER=postgres
DB_PASSWORD=postgres
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET=dev_jwt_secret
JWT_REFRESH_SECRET=dev_jwt_refresh_secret
ENCRYPTION_KEY=dev_encryption_key
LOG_LEVEL=debug
SECURITY_HEADERS=false
RATE_LIMITING=false
CORS_ORIGIN=http://localhost:3000
```

#### Step 3: Start Development Server
```bash
# Start in development mode
npm run dev

# Run tests
npm test

# Run with hot reload
npm run dev:watch
```

## Testing Your Installation

### Health Checks
```bash
# Basic health check
curl http://localhost:3000/health

# Detailed health check
curl http://localhost:3000/api/health/detailed

# Database health
curl http://localhost:3000/api/health/database

# Redis health
curl http://localhost:3000/api/health/redis
```

### API Testing
```bash
# Test user registration
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testPassword123",
    "firstName": "John",
    "lastName": "Doe"
  }'

# Test user login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testPassword123"
  }'
```

### Business Formation Testing
```bash
# Test Florida LLC formation
curl -X POST http://localhost:3000/api/business-formation/entities \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "My Florida LLC",
    "type": "LLC",
    "state": "FL",
    "registeredAgent": {
      "name": "John Doe",
      "address": "123 Main St, Miami, FL 33101",
      "phone": "+1234567890"
    }
  }'
```

## Configuration Options

### Production Configuration
- **Security**: Full security headers and rate limiting
- **Logging**: Production-level logging
- **Performance**: Optimized for production workloads
- **Monitoring**: Full monitoring and alerting

### Development Configuration
- **Security**: Relaxed for development
- **Logging**: Verbose debugging logs
- **Performance**: Optimized for development speed
- **Hot Reload**: Automatic restart on changes

### Testing Configuration
- **Database**: Separate test database
- **Isolation**: Each test runs in isolation
- **Mocking**: Mock external services
- **Coverage**: Full test coverage reporting

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 3000
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill process
kill -9 PID  # macOS/Linux
taskkill /PID PID /F  # Windows
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS

# Check connection
psql -h localhost -U legalops_prod -d legalops_production
```

#### Redis Connection Issues
```bash
# Check Redis status
sudo systemctl status redis-server  # Linux
brew services list | grep redis  # macOS

# Test connection
redis-cli ping
```

#### Build Issues
```bash
# Clean and rebuild
rm -rf node_modules dist
npm install
npm run build
```

### Logs and Debugging
```bash
# View application logs
docker-compose logs -f legalops-backend

# View database logs
docker-compose logs -f postgres

# View Redis logs
docker-compose logs -f redis

# Debug mode
NODE_ENV=development npm run dev
```

## Performance Optimization

### Local Performance Tuning
```bash
# Increase Node.js memory limit
node --max-old-space-size=4096 dist/index.js

# Optimize PostgreSQL
# Edit postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB

# Optimize Redis
# Edit redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
```

### Monitoring
```bash
# Monitor system resources
htop  # Linux/macOS
Task Manager  # Windows

# Monitor application
curl http://localhost:3000/api/metrics/system
curl http://localhost:3000/api/metrics/performance
```

## Security Considerations

### Local Security
- **Firewall**: Configure local firewall rules
- **Access Control**: Limit access to localhost only
- **SSL**: Use self-signed certificates for HTTPS
- **Secrets**: Keep environment variables secure

### Production Preparation
- **Environment Variables**: Use secure, unique values
- **Database Passwords**: Strong, unique passwords
- **JWT Secrets**: Cryptographically secure secrets
- **Encryption Keys**: Strong encryption keys

## Next Steps

### After Installation
1. **Test All Features**: Verify all functionality works
2. **Load Testing**: Test under realistic loads
3. **Security Testing**: Verify security measures
4. **Backup Testing**: Test backup and recovery
5. **Documentation**: Update any local-specific docs

### Before Production
1. **Performance Tuning**: Optimize for your hardware
2. **Security Hardening**: Apply production security
3. **Monitoring Setup**: Configure monitoring and alerting
4. **Backup Strategy**: Implement backup procedures
5. **Disaster Recovery**: Test recovery procedures

## Support

### Getting Help
- **Documentation**: Check the docs/ directory
- **Logs**: Review application and system logs
- **Health Checks**: Use the health check endpoints
- **Community**: Join the LegalOps community

### Reporting Issues
- **Bug Reports**: Use GitHub issues
- **Feature Requests**: Submit feature requests
- **Security Issues**: Report security issues privately
- **Documentation**: Help improve documentation

---

**Last Updated**: $(date)
**Version**: 1.0.0
**Environment**: Local Development/Testing

