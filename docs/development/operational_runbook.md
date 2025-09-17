# LegalOps Platform - Operational Runbook

## Overview
This runbook provides operational procedures, troubleshooting guides, and maintenance tasks for the LegalOps platform in production environments.

## Table of Contents
1. [Daily Operations](#daily-operations)
2. [Monitoring & Alerting](#monitoring--alerting)
3. [Backup & Recovery](#backup--recovery)
4. [Security Operations](#security-operations)
5. [Performance Monitoring](#performance-monitoring)
6. [Incident Response](#incident-response)
7. [Maintenance Procedures](#maintenance-procedures)
8. [Emergency Procedures](#emergency-procedures)

## Daily Operations

### Morning Checklist
- [ ] Check system health dashboard
- [ ] Review overnight alerts and logs
- [ ] Verify backup completion
- [ ] Check database performance metrics
- [ ] Review security events
- [ ] Monitor application performance
- [ ] Check SSL certificate status
- [ ] Verify external service connectivity

### Evening Checklist
- [ ] Review daily performance metrics
- [ ] Check error rates and trends
- [ ] Verify scheduled backups
- [ ] Review security logs
- [ ] Check disk space usage
- [ ] Monitor memory usage
- [ ] Review user activity patterns
- [ ] Update operational logs

### Health Check Commands
```bash
# System health overview
curl -f https://api.legalops.com/health

# Detailed health check
curl -f https://api.legalops.com/api/health/detailed \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Database connectivity
sudo -u postgres psql -c "SELECT 1;" legalops_production

# Redis connectivity
redis-cli ping

# Application status
sudo -u legalops pm2 status

# System resources
htop
df -h
free -h
```

## Monitoring & Alerting

### Key Metrics to Monitor

#### Application Metrics
- **Response Time**: < 200ms average
- **Error Rate**: < 1% of requests
- **Throughput**: Requests per second
- **Uptime**: > 99.9%
- **Memory Usage**: < 80% of available
- **CPU Usage**: < 70% average

#### Database Metrics
- **Connection Pool**: < 80% utilization
- **Query Performance**: < 100ms average
- **Lock Wait Time**: < 50ms average
- **Cache Hit Rate**: > 95%
- **Disk Usage**: < 85% of available

#### Infrastructure Metrics
- **Disk Space**: < 85% utilization
- **Network Latency**: < 50ms
- **SSL Certificate**: > 30 days remaining
- **Backup Status**: Daily completion
- **Log Rotation**: Successful

### Alert Thresholds

#### Critical Alerts (Immediate Response)
- Application down (5xx errors > 5%)
- Database connection failure
- Disk space > 90%
- Memory usage > 90%
- SSL certificate expires in < 7 days
- Security breach detected

#### Warning Alerts (Response within 1 hour)
- Response time > 500ms
- Error rate > 2%
- CPU usage > 80%
- Memory usage > 80%
- Database query time > 200ms
- Backup failure

#### Info Alerts (Monitor and log)
- High traffic volume
- Unusual user patterns
- Performance degradation
- Resource usage trends

### Monitoring Commands
```bash
# Check application metrics
curl -s https://api.legalops.com/api/metrics/application \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# Check database metrics
curl -s https://api.legalops.com/api/metrics/database \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# Check system metrics
curl -s https://api.legalops.com/api/metrics/system \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# Check security metrics
curl -s https://api.legalops.com/api/metrics/security \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

## Backup & Recovery

### Backup Schedule
- **Full Database Backup**: Daily at 2:00 AM
- **Incremental Backup**: Every 6 hours
- **Configuration Backup**: Daily at 3:00 AM
- **Application Backup**: Weekly on Sunday at 1:00 AM
- **Log Backup**: Daily at 4:00 AM

### Backup Verification
```bash
# Check backup status
sudo -u legalops npm run backup:status

# Verify latest backup
sudo -u legalops npm run backup:verify -- --backup-id latest

# List available backups
sudo -u legalops npm run backup:list

# Test restore (dry run)
sudo -u legalops npm run backup:test-restore -- --backup-id backup-id
```

### Recovery Procedures

#### Database Recovery
```bash
# Stop application
sudo -u legalops pm2 stop all

# Restore database
sudo -u legalops npm run restore:database -- --backup-id backup-id

# Verify database integrity
sudo -u postgres psql legalops_production -c "SELECT COUNT(*) FROM users;"

# Start application
sudo -u legalops pm2 start all
```

#### Full System Recovery
```bash
# Restore from full backup
sudo -u legalops npm run restore:full -- --backup-id backup-id

# Verify all services
sudo -u legalops pm2 status
sudo systemctl status postgresql
sudo systemctl status redis-server
sudo systemctl status nginx

# Run health checks
curl -f https://api.legalops.com/health
```

## Security Operations

### Security Monitoring
- **Failed Login Attempts**: Monitor for brute force attacks
- **Suspicious IP Addresses**: Track and block malicious IPs
- **Rate Limiting**: Monitor for abuse patterns
- **File Uploads**: Scan for malicious files
- **API Usage**: Monitor for unusual patterns
- **SSL/TLS**: Monitor certificate status and security

### Security Commands
```bash
# Check security events
curl -s https://api.legalops.com/api/security/events \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# Check blocked IPs
curl -s https://api.legalops.com/api/security/blocked-ips \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# Check failed logins
curl -s https://api.legalops.com/api/security/failed-logins \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# Block IP address
curl -X POST https://api.legalops.com/api/security/block-ip \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ipAddress": "192.168.1.100", "reason": "Suspicious activity"}'
```

### Security Incident Response
1. **Identify**: Determine scope and impact
2. **Contain**: Isolate affected systems
3. **Eradicate**: Remove threat
4. **Recover**: Restore normal operations
5. **Document**: Record incident details
6. **Review**: Analyze and improve

## Performance Monitoring

### Performance Metrics
- **Response Time**: Track API response times
- **Throughput**: Monitor requests per second
- **Error Rates**: Track 4xx and 5xx errors
- **Resource Usage**: Monitor CPU, memory, disk
- **Database Performance**: Track query times
- **Cache Performance**: Monitor hit rates

### Performance Optimization
```bash
# Check performance metrics
curl -s https://api.legalops.com/api/performance/metrics \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# Check cache performance
curl -s https://api.legalops.com/api/performance/cache \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# Check database performance
curl -s https://api.legalops.com/api/performance/database \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# Run performance test
npm run test:performance
```

### Performance Tuning
- **Database Indexing**: Monitor and optimize indexes
- **Query Optimization**: Review slow queries
- **Caching Strategy**: Optimize cache usage
- **Connection Pooling**: Tune pool settings
- **Load Balancing**: Distribute traffic efficiently

## Incident Response

### Incident Classification

#### Severity 1 (Critical)
- **Definition**: Complete service outage
- **Response Time**: 15 minutes
- **Escalation**: Immediate
- **Examples**: Application down, database failure

#### Severity 2 (High)
- **Definition**: Significant service degradation
- **Response Time**: 1 hour
- **Escalation**: Within 2 hours
- **Examples**: High error rates, slow response times

#### Severity 3 (Medium)
- **Definition**: Minor service issues
- **Response Time**: 4 hours
- **Escalation**: Within 8 hours
- **Examples**: Feature not working, minor performance issues

#### Severity 4 (Low)
- **Definition**: Cosmetic issues or minor bugs
- **Response Time**: 24 hours
- **Escalation**: Within 48 hours
- **Examples**: UI issues, documentation errors

### Incident Response Process
1. **Detection**: Identify and classify incident
2. **Response**: Acknowledge and begin investigation
3. **Resolution**: Implement fix and verify
4. **Communication**: Update stakeholders
5. **Post-Mortem**: Document and learn

### Emergency Contacts
- **Primary On-Call**: +1-XXX-XXX-XXXX
- **Secondary On-Call**: +1-XXX-XXX-XXXX
- **Engineering Manager**: +1-XXX-XXX-XXXX
- **CTO**: +1-XXX-XXX-XXXX

## Maintenance Procedures

### Weekly Maintenance
- [ ] Review system logs
- [ ] Check disk space usage
- [ ] Update security patches
- [ ] Review performance metrics
- [ ] Test backup procedures
- [ ] Update documentation
- [ ] Review user feedback

### Monthly Maintenance
- [ ] Security audit
- [ ] Performance review
- [ ] Capacity planning
- [ ] Disaster recovery test
- [ ] Update dependencies
- [ ] Review monitoring alerts
- [ ] Plan infrastructure updates

### Quarterly Maintenance
- [ ] Full security assessment
- [ ] Performance optimization
- [ ] Infrastructure review
- [ ] Disaster recovery drill
- [ ] Update operational procedures
- [ ] Review and update runbooks
- [ ] Plan major updates

### Maintenance Commands
```bash
# System updates
sudo apt update && sudo apt upgrade -y

# Application updates
cd /opt/legalops
sudo -u legalops git pull origin main
sudo -u legalops npm ci --production
sudo -u legalops npm run build
sudo -u legalops pm2 reload all

# Database maintenance
sudo -u postgres psql legalops_production -c "VACUUM ANALYZE;"

# Log rotation
sudo logrotate -f /etc/logrotate.d/legalops

# SSL certificate renewal
sudo certbot renew --dry-run
```

## Emergency Procedures

### System Down
1. **Assess**: Determine scope of outage
2. **Communicate**: Notify stakeholders
3. **Investigate**: Check logs and metrics
4. **Restore**: Implement quick fix if possible
5. **Monitor**: Watch for stability
6. **Document**: Record incident details

### Database Corruption
1. **Stop**: Halt application services
2. **Assess**: Determine corruption extent
3. **Restore**: Restore from latest backup
4. **Verify**: Test database integrity
5. **Start**: Restart application services
6. **Monitor**: Watch for issues

### Security Breach
1. **Contain**: Isolate affected systems
2. **Assess**: Determine breach scope
3. **Notify**: Alert security team
4. **Investigate**: Analyze attack vectors
5. **Remediate**: Fix vulnerabilities
6. **Monitor**: Enhanced monitoring
7. **Report**: Document and report

### High Load/DoS
1. **Monitor**: Track traffic patterns
2. **Scale**: Increase resources if needed
3. **Block**: Block malicious IPs
4. **Rate Limit**: Implement stricter limits
5. **Communicate**: Update users if needed
6. **Analyze**: Review attack patterns

### Emergency Commands
```bash
# Emergency stop
sudo -u legalops pm2 stop all
sudo systemctl stop nginx

# Emergency start
sudo systemctl start nginx
sudo -u legalops pm2 start all

# Emergency backup
sudo -u legalops npm run backup:emergency

# Emergency restore
sudo -u legalops npm run restore:emergency -- --backup-id backup-id

# Emergency monitoring
sudo -u legalops pm2 monit
htop
iostat -x 1
```

## Troubleshooting Guide

### Common Issues

#### Application Won't Start
```bash
# Check PM2 status
sudo -u legalops pm2 status

# Check logs
sudo -u legalops pm2 logs

# Check environment
sudo -u legalops cat /etc/legalops/.env.production

# Restart application
sudo -u legalops pm2 restart all
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
sudo -u postgres psql -c "SELECT 1;" legalops_production

# Check connection pool
curl -s https://api.legalops.com/api/health/database

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### High Memory Usage
```bash
# Check memory usage
free -h
sudo -u legalops pm2 monit

# Check for memory leaks
sudo -u legalops pm2 logs --lines 100

# Restart if needed
sudo -u legalops pm2 restart all
```

#### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Test certificate
openssl s_client -connect api.legalops.com:443

# Renew certificate
sudo certbot renew

# Restart Nginx
sudo systemctl restart nginx
```

### Log Analysis
```bash
# Application logs
sudo -u legalops pm2 logs --lines 1000

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u nginx -f
sudo journalctl -u postgresql -f

# Security logs
sudo tail -f /var/log/auth.log
```

## Contact Information

### Internal Contacts
- **Operations Team**: ops@legalops.com
- **Engineering Team**: engineering@legalops.com
- **Security Team**: security@legalops.com
- **On-Call Phone**: +1-XXX-XXX-XXXX

### External Contacts
- **Hosting Provider**: support@hosting-provider.com
- **SSL Provider**: support@ssl-provider.com
- **Monitoring Service**: support@monitoring-service.com
- **Backup Service**: support@backup-service.com

### Documentation
- **API Documentation**: https://docs.legalops.com/api
- **Deployment Guide**: https://docs.legalops.com/deployment
- **Security Guide**: https://docs.legalops.com/security
- **Status Page**: https://status.legalops.com

---

**Last Updated**: $(date)
**Version**: 1.0.0
**Environment**: Production

