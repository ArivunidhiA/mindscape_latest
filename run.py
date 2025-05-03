from app import create_app
import os
from config import DevelopmentConfig, ProductionConfig

# Create app with development config by default
app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    # Use localhost and port 5000 by default for local development
    host = os.environ.get('HOST', 'localhost')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port, debug=True) 