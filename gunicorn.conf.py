import multiprocessing

# Worker Settings
worker_class = 'gevent'
workers = multiprocessing.cpu_count() * 2 + 1
worker_connections = 1000

# Server Socket Settings
bind = '0.0.0.0:5000'
backlog = 2048

# Logging Settings
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process Naming
proc_name = 'mindscape'

# Timeout Settings
timeout = 30
keepalive = 2

# SSL Settings (if needed, uncomment and set proper paths)
# keyfile = 'path/to/keyfile'
# certfile = 'path/to/certfile'

# Server Mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None

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