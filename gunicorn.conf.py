import multiprocessing
import os

# Worker Settings
workers = 2  # Number of worker processes
worker_class = 'gthread'  # Use gthread worker class
threads = 2  # Number of threads per worker
worker_connections = 1000  # Maximum number of simultaneous connections
timeout = 120  # Worker timeout in seconds
keepalive = 5  # The number of seconds to wait for requests on a Keep-Alive connection

# Server Mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process Naming
proc_name = None

# Server Socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# SSL
keyfile = None
certfile = None

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Server Hooks
def on_starting(server):
    """
    Called just before the master process is initialized.
    """
    pass

def on_reload(server):
    """
    Called before code is reloaded.
    """
    pass

def when_ready(server):
    """
    Called just after the server is started.
    """
    pass 