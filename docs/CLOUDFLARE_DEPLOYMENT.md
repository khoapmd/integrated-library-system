# Cloudflare Tunnel Deployment Guide

This guide covers deploying the Library Management System behind a Cloudflare tunnel.

## 🌐 Cloudflare Tunnel Setup

### Prerequisites
- Cloudflare account with domain
- Docker and Docker Compose installed
- Cloudflare tunnel configured

### 1. Configure Environment

Create a `.env.production` file based on `.env.production.example`:

```bash
cp .env.production.example .env.production
```

Edit `.env.production` and set:
```env
SECRET_KEY=your-super-secret-production-key-here
POSTGRES_PASSWORD=your-secure-database-password-here
PREFERRED_URL_SCHEME=https
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
```

**Important:** Change the default passwords and secret keys!

### 2. Deploy with Docker Compose

The setup includes PostgreSQL database for production reliability:

```bash
# Start the application (PostgreSQL + Library App)
docker-compose up -d

# Check logs
docker-compose logs -f library-app

# Check database logs if needed
docker-compose logs -f db
```

The deployment script handles database initialization automatically.

### 3. Configure Cloudflare Tunnel

In your Cloudflare tunnel configuration, point to your Docker container:

```yaml
tunnel: your-tunnel-id
credentials-file: /path/to/credentials.json

ingress:
  - hostname: library.yourdomain.com
    service: http://localhost:5000
  - service: http_status:404
```

Or using the Cloudflare dashboard:
- Service: HTTP
- URL: `localhost:5000` (or your Docker host IP)

### 4. Security Considerations

✅ **Already Configured:**
- ProxyFix middleware handles X-Forwarded headers from Cloudflare
- Session cookies secured for HTTPS
- CORS properly configured
- Health checks enabled

✅ **Cloudflare Features to Enable:**
- SSL/TLS: Full (strict) mode recommended
- Always Use HTTPS: On
- HSTS: Enable for enhanced security
- Bot Fight Mode: Consider enabling
- Security Level: Medium or High

### 5. Performance Optimization

**Cloudflare Settings:**
- Caching Level: Standard
- Browser Cache TTL: 1 hour for dynamic content
- Edge Cache TTL: 2 hours for static assets
- Minification: Auto Minify HTML, CSS, JS

**Application Settings:**
- Static files are served with 1-year cache headers
- Database queries optimized for production
- Debug mode disabled

### 6. Monitoring

Monitor your deployment:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' library-app

# View application logs
docker-compose logs -f library-app

# Check resource usage
docker stats library-app
```

### 7. SSL Certificate Management

Cloudflare handles SSL termination, so the application runs on HTTP internally. The ProxyFix middleware ensures Flask recognizes the connection as HTTPS for:
- Secure cookie handling
- Proper redirect generation
- CSRF protection

### 8. Troubleshooting

**Common Issues:**

1. **Cookie Issues:** Ensure `SESSION_COOKIE_SECURE=true` is set
2. **Redirect Loops:** Check `PREFERRED_URL_SCHEME=https` setting
3. **CORS Errors:** Verify Cloudflare isn't blocking legitimate requests
4. **Database Permissions:** Ensure volumes have correct permissions

**Debug Mode:**
```bash
# Temporarily enable debug for troubleshooting
docker-compose exec library-app python -c "
import app; 
print('App Config:', {k:v for k,v in app.app.config.items() if 'SECRET' not in k})
"
```

### 9. Updates and Maintenance

```bash
# Update the application
git pull
docker-compose build --no-cache
docker-compose up -d

# Backup PostgreSQL database
docker-compose exec db pg_dump -U libraryuser library > backup-$(date +%Y%m%d).sql

# Restore PostgreSQL database
docker-compose exec -T db psql -U libraryuser library < backup-20250710.sql

# Access PostgreSQL shell
docker-compose exec db psql -U libraryuser library

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### 10. Production Checklist

- [ ] Environment variables configured
- [ ] Secret key changed from default
- [ ] Database backups scheduled
- [ ] Cloudflare security settings enabled
- [ ] Health monitoring set up
- [ ] Log rotation configured
- [ ] Volume permissions verified
- [ ] HTTPS redirects working
- [ ] Scanner functionality tested through tunnel

## 🔧 Advanced Configuration

### Using PostgreSQL

For production databases, consider PostgreSQL:

1. Add PostgreSQL to docker-compose.yml:
```yaml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: library
      POSTGRES_USER: libraryuser
      POSTGRES_PASSWORD: your-secure-password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

2. Update DATABASE_URL:
```env
DATABASE_URL=postgresql://libraryuser:your-secure-password@db:5432/library
```

### Rate Limiting with Redis

Add Redis for advanced rate limiting:

```yaml
services:
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

Set in environment:
```env
REDIS_URL=redis://redis:6379/0
```
