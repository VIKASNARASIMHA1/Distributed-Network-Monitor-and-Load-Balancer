#!/usr/bin/env python3
"""
Web Server Node - Instance 2
"""
import os
# Just import from node1 with different environment
os.environ['SERVER_ID'] = '2'
os.environ['SERVER_NAME'] = 'web-server-2'
os.environ['PORT'] = '5002'

# Import and run the shared code
from node1.app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)