# Gunicorn configuration file
# Production settings for the Library Management System

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Maximum number of requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Restart workers after this many seconds
max_worker_time = 1800

# Logging
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "library-management-system"

# Server mechanics
daemon = False
pidfile = "/app/gunicorn.pid"
tmp_upload_dir = None

# SSL (if needed)
keyfile = os.environ.get('SSL_KEYFILE')
certfile = os.environ.get('SSL_CERTFILE')

# Application
wsgi_module = "app:app"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
preload_app = True
sendfile = True
