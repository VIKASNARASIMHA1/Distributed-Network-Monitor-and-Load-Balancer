#!/usr/bin/env python3
"""
Web Server Node - Instance 3
"""
import os
# Just import from node1 with different environment
os.environ['SERVER_ID'] = '3'
os.environ['SERVER_NAME'] = 'web-server-3'
os.environ['PORT'] = '5003'

# Import and run the shared code
from node1.app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)