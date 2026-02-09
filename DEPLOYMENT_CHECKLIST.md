# Deployment Checklist

Use this checklist to ensure successful deployment of the City Governance System.

## Pre-Deployment

### Prerequisites
- [ ] Docker Desktop installed and running
- [ ] Docker version 24.0+ (`docker --version`)
- [ ] Docker Compose version 2.20+ (`docker-compose --version`)
- [ ] Git installed
- [ ] API key obtained (Groq or OpenAI)

### Code Preparation
- [ ] Repository cloned locally
- [ ] Latest code pulled (`git pull origin main`)
- [ ] `.env` file created from `.env.example`
- [ ] API keys added to `.env` file
- [ ] Database password set in `.env`
- [ ] No syntax errors (`docker-compose config`)

## Local Development Deployment

### Build Phase
- [ ] Run `docker-compose build` successfully
- [ ] Backend image created (`docker images | grep backend`)
- [ ] Frontend image created (`docker images | grep frontend`)
- [ ] No build errors in logs

### Database Initialization
- [ ] Start database: `docker-compose up -d postgres`
- [ ] Wait for health check (10 seconds)
- [ ] Database is healthy: `docker-compose ps postgres`
- [ ] Run schema: `docker-compose exec postgres psql -U postgres -d departments -f /docker-entrypoint-initdb.d/complete_schema.sql`
- [ ] Run seed data: `docker-compose exec postgres psql -U postgres -d departments -f /docker-entrypoint-initdb.d/comprehensive_seed_data.sql`
- [ ] Verify tables created: `docker-compose exec postgres psql -U postgres -d departments -c "\dt"`

### Service Startup
- [ ] Start all services: `docker-compose up -d`
- [ ] All containers running: `docker-compose ps`
- [ ] Backend health check passing: `curl http://localhost:8000/health`
- [ ] Frontend health check passing: `curl http://localhost/health`
- [ ] No errors in logs: `docker-compose logs`

### Functional Testing
- [ ] Frontend accessible: http://localhost
- [ ] Backend API accessible: http://localhost:8000
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Can query water agent via API
- [ ] Can query health agent via API
- [ ] Can query fire agent via API
- [ ] Frontend UI responds to clicks
- [ ] Agent constellation video loads
- [ ] No console errors in browser

### Backend Tests
- [ ] Run test suite: `docker-compose exec backend pytest`
- [ ] All tests pass (or acceptable failures documented)
- [ ] Test coverage adequate
- [ ] No import errors

## Production Deployment

### Security
- [ ] Strong PostgreSQL password set
- [ ] API keys never committed to git
- [ ] `.env` file in `.gitignore`
- [ ] Updated all default credentials
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Security headers in Nginx config

### Environment Configuration
- [ ] `ENVIRONMENT=production` in `.env`
- [ ] `LOG_LEVEL=INFO` (not DEBUG)
- [ ] Database backups configured
- [ ] Monitoring enabled
- [ ] Error tracking configured (optional)

### Cloud Deployment (AWS/GCP/Azure)
- [ ] VM/Instance created with sufficient resources (4GB+ RAM)
- [ ] Docker installed on server
- [ ] Git repository cloned
- [ ] `.env` file configured with production credentials
- [ ] Firewall rules configured (ports 80, 443, 8000)
- [ ] SSL certificates obtained (Let's Encrypt)
- [ ] Domain DNS configured
- [ ] Reverse proxy configured (if using)

### Container Registry (Optional)
- [ ] Images tagged for registry
- [ ] Pushed to registry (ECR/GCR/Docker Hub)
- [ ] Registry credentials configured on server
- [ ] Pull images successfully

### Deployment Execution
- [ ] Build production images: `docker-compose build`
- [ ] Start services: `docker-compose up -d`
- [ ] All health checks passing
- [ ] Services accessible from public URL
- [ ] HTTPS working (if configured)
- [ ] API responds correctly
- [ ] Frontend loads correctly

## Post-Deployment

### Verification
- [ ] All services running: `docker-compose ps`
- [ ] Health endpoints responding
- [ ] Database connections working
- [ ] LLM API calls succeeding
- [ ] Logs show no errors
- [ ] Resource usage acceptable: `docker stats`

### Performance
- [ ] Response times acceptable (< 2s for API)
- [ ] Memory usage stable
- [ ] CPU usage reasonable
- [ ] Database queries optimized
- [ ] Frontend loads quickly (< 3s)

### Monitoring Setup
- [ ] Log aggregation configured (optional)
- [ ] Uptime monitoring configured (optional)
- [ ] Error alerting configured (optional)
- [ ] Resource monitoring configured (optional)
- [ ] Database backups automated

### Documentation
- [ ] Deployment notes documented
- [ ] Credentials stored securely (password manager)
- [ ] Runbook created for common tasks
- [ ] Team members have access
- [ ] Support contacts documented

## Backup and Recovery

### Backup Configuration
- [ ] Database backup script tested
- [ ] Backup schedule configured
- [ ] Backup storage location secured
- [ ] Restore procedure tested
- [ ] Backup retention policy set

### Disaster Recovery
- [ ] Recovery procedure documented
- [ ] Tested full restoration from backup
- [ ] Rollback plan documented
- [ ] Alternative access methods documented
- [ ] Contact information current

## Maintenance

### Regular Tasks
- [ ] Weekly health checks scheduled
- [ ] Monthly security updates planned
- [ ] Quarterly dependency updates planned
- [ ] Database maintenance scheduled (VACUUM, ANALYZE)
- [ ] Log rotation configured

### Scaling Preparation
- [ ] Load testing performed (optional)
- [ ] Scaling strategy documented
- [ ] Resource limits configured
- [ ] Auto-scaling configured (if using)

## Troubleshooting Reference

### If Backend Won't Start
1. [ ] Check logs: `docker-compose logs backend`
2. [ ] Verify API keys: `docker-compose exec backend env | grep API_KEY`
3. [ ] Check database connection: `docker-compose exec backend env | grep DATABASE`
4. [ ] Verify imports: `docker-compose exec backend python -c "from agents.coordination_agent.agent import CoordinationAgent"`

### If Frontend Won't Load
1. [ ] Check logs: `docker-compose logs frontend`
2. [ ] Verify build: `docker-compose exec frontend ls /usr/share/nginx/html`
3. [ ] Check Nginx config: `docker-compose exec frontend cat /etc/nginx/conf.d/default.conf`
4. [ ] Test direct access: `curl -I http://localhost`

### If Database Connection Fails
1. [ ] Check database running: `docker-compose ps postgres`
2. [ ] Test connection: `docker-compose exec postgres pg_isready -U postgres`
3. [ ] Check credentials: `docker-compose exec backend env | grep DATABASE`
4. [ ] Verify network: `docker network ls`

## Sign-Off

### Development Deployment
- [ ] Developer: __________________ Date: __________
- [ ] Reviewed by: ________________ Date: __________
- [ ] Status: ☐ Success ☐ Issues (see notes)

### Production Deployment
- [ ] Deployer: ___________________ Date: __________
- [ ] Tested by: __________________ Date: __________
- [ ] Approved by: ________________ Date: __________
- [ ] Status: ☐ Live ☐ Rollback ☐ Issues

## Notes

```
Document any issues, workarounds, or special configurations here:




```

## Rollback Plan

If deployment fails:

1. **Stop new deployment**
   ```bash
   docker-compose down
   ```

2. **Restore previous version**
   ```bash
   git checkout <previous-commit>
   docker-compose build
   docker-compose up -d
   ```

3. **Restore database backup** (if needed)
   ```bash
   docker-compose exec postgres psql -U postgres departments < backup.sql
   ```

4. **Verify rollback**
   - [ ] Services running
   - [ ] Health checks passing
   - [ ] Functionality restored

## Contact Information

- **Primary Contact**: _______________________
- **Email**: _________________________________
- **Phone**: _________________________________
- **Backup Contact**: ________________________
- **Emergency**: _____________________________

---

**Checklist Version**: 1.0  
**Last Updated**: 2024  
**Next Review**: _____________
