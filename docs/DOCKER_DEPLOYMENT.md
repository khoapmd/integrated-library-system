# Docker Deployment Guide

This guide covers deploying the Library Management System using Docker.

## 🐳 Quick Start with Docker

### Prerequisites
- Docker installed on your system
- Docker Compose (optional, for easier management)

### Basic Docker Deployment

1. **Build the Docker image:**
   ```bash
   docker build -t library-management .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name library-app \
     -p 5000:5000 \
     -v library_data:/app/instance \
     -v library_uploads:/app/uploads \
     library-management
   ```

3. **Access the application:**
   Open your browser to `http://localhost:5000`

### Docker Compose Deployment (Recommended)

1. **Start the application:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f library-app
   ```

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

## 🔧 Configuration

### Environment Variables

You can configure the application using environment variables:

```bash
docker run -d \
  --name library-app \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e DATABASE_URL=sqlite:///instance/library.db \
  library-management
```

### Persistent Data

The Docker setup uses volumes to persist important data:

- `library_data` - Database files
- `library_uploads` - Uploaded files
- `library_member_cards` - Generated member QR codes
- `library_logs` - Application logs

### SSL/HTTPS

For HTTPS in production:

1. **Mount SSL certificates:**
   ```bash
   docker run -d \
     --name library-app \
     -p 5000:5000 \
     -v /path/to/ssl:/app/ssl:ro \
     library-management \
     python main.py --https --host 0.0.0.0
   ```

## 🚀 Production Deployment

### With Reverse Proxy (Recommended)

Use the included nginx configuration for production:

```bash
# Start with nginx reverse proxy
docker-compose --profile production up -d
```

### Docker Swarm / Kubernetes

For container orchestration, refer to the examples in the `deployment/` directory.

### Health Checks

The Docker image includes health checks:
- Endpoint: `http://localhost:5000/`
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3

## 🔍 Troubleshooting

### View Application Logs
```bash
docker logs library-app
```

### Access Container Shell
```bash
docker exec -it library-app /bin/bash
```

### Rebuild After Changes
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📊 Monitoring

### Resource Usage
```bash
docker stats library-app
```

### Container Health
```bash
docker inspect --format='{{.State.Health.Status}}' library-app
```

## 🔄 Updates

1. **Pull latest code**
2. **Rebuild image:**
   ```bash
   docker-compose build --no-cache
   ```
3. **Restart services:**
   ```bash
   docker-compose up -d
   ```

## 🛡️ Security Considerations

- The container runs as a non-root user
- SSL certificates should be mounted as read-only
- Use Docker secrets for sensitive configuration
- Keep the base image updated

## 📁 File Structure in Container

```
/app/
├── app.py              # Flask application
├── main.py             # Entry point
├── models.py           # Database models
├── config.py           # Configuration
├── utils.py            # Utilities
├── templates/          # HTML templates
├── static/             # Static assets
├── scripts/            # Utility scripts
├── instance/           # Database (volume mounted)
├── uploads/            # File uploads (volume mounted)
├── member_cards/       # QR codes (volume mounted)
└── logs/               # Application logs (volume mounted)
```
