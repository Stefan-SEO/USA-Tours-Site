#!/bin/bash

# Kill any existing processes using port 8083
lsof -ti:8083 | xargs kill -9 2>/dev/null

# Run the server with Gunicorn
gunicorn --bind 0.0.0.0:8083 --workers 3 --timeout 120 app:app 