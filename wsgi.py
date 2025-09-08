#!/usr/bin/env python3
"""
WSGI entry point for Reliance Foundation AI Analytics Platform
Production deployment configuration
"""

import os
from simple_app import create_app

# Create application instance
app = create_app(os.getenv('FLASK_CONFIG') or 'production')

if __name__ == "__main__":
    app.run()