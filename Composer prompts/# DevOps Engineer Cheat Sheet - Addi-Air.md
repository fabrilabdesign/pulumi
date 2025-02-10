# DevOps Engineer Cheat Sheet - Addi-Aire Infrastructure

## Infrastructure Overview
- Primary App Server: 192.168.3.26 (Docker + Jenkins + Nginx)
- Development Server: 192.168.3.147
- ESXi Host: 192.168.2.236
- Environment: Multi-server, Virtualized, Containerized

## CI/CD Pipeline
```yaml
stages:
  1. Checkout (GitHub)
  2. Build & Lint
  3. Test
  4. Create Docker Image
  5. Deploy to Staging
  6. Production Deploy
  7. Health Check
```

## Jenkins Configuration
- Master: port 8080
- Agent Ports: 50000-51000
- Required Plugins:
  - Docker Pipeline
  - GitHub Integration
  - Nginx
  - Credentials Binding

## Docker Commands
```bash
# Image Management
docker build -t addi-aire/app:latest .
docker push addi-aire/app:latest
docker pull addi-aire/app:latest

# Container Operations
docker-compose up -d
docker-compose down
docker logs -f container_name
docker exec -it container_name bash

# Health Checks
docker stats
docker ps -a
docker system df
docker system prune -a
```

## Deployment Commands
```bash
# Nginx
nginx -t                          # Validate config
systemctl reload nginx            # Reload config
certbot renew                     # Renew SSL

# Jenkins
jenkins-cli safe-restart         # Restart Jenkins
jenkins-cli list-jobs            # List all jobs
jenkins-cli build job-name       # Trigger build

# Container Deployment
docker stack deploy -c docker-compose.yml addi-aire
docker service ls
docker service logs service_name
docker service scale service_name=3
```

## GitHub Required Secrets
```yaml
PULUMI_ACCESS_TOKEN: Infrastructure as Code
DOCKER_USERNAME: Container Registry
DOCKER_PASSWORD: Container Registry
GRAFANA_ADMIN_PASSWORD: Monitoring
SLACK_WEBHOOK_URL: Notifications
GITHUB_TOKEN: Auto-provided
```

## Monitoring Stack
- Prometheus: Metrics Collection
- Grafana: Visualization
- ELK Stack: Log Aggregation
- Node Exporter: Host Metrics

## Quick Troubleshooting
```bash
# Application Logs
journalctl -u docker            # Docker logs
journalctl -u jenkins          # Jenkins logs
tail -f /var/log/nginx/error.log  # Nginx errors

# Container Debug
docker logs container_name
docker inspect container_name
docker stats container_name
docker events --filter type=container

# System Resources
df -h                          # Disk usage
free -m                        # Memory usage
top                           # Process usage
netstat -tupln                # Port usage
```

## Deployment Checklist
1. Pre-Deployment
   - Git tag version
   - Run full test suite
   - Update changelog
   - Backup current state

2. Deployment
   - Scale down service
   - Deploy new version
   - Run health checks
   - Scale up service

3. Post-Deployment
   - Monitor error rates
   - Check application logs
   - Verify metrics
   - Update documentation

## Recovery Procedures
1. Failed Deployment
```bash
# Roll back to previous version
docker service update --rollback service_name
# Or using specific version
docker service update --image addi-aire/app:previous service_name
```

2. Jenkins Issues
```bash
# Backup Jenkins
jenkins-cli safe-restart
# Check plugin conflicts
jenkins-cli list-plugins
```

3. Container Issues
```bash
# Reset container state
docker-compose down
docker system prune
docker-compose up -d
```

## Automation Scripts Location
- Infrastructure: /opt/addi-aire/infra/
- Deployment: /opt/addi-aire/deploy/
- Monitoring: /opt/addi-aire/monitoring/
- Backup: /opt/addi-aire/backup/

## Regular Maintenance
1. Weekly Tasks
   - Update Docker images
   - Rotate logs
   - Backup Jenkins config
   - Check resource usage

2. Monthly Tasks
   - SSL certificate check
   - Security updates
   - Performance review
   - Capacity planning

3. Quarterly Tasks
   - Full DR test
   - Infrastructure audit
   - Documentation review
   - Security assessment