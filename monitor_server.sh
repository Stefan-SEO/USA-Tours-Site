#!/bin/bash

# Monitor and restart the Flask server if it goes down

LOG_FILE="server_monitor.log"
SERVER_LOG="server_log.txt"

echo "$(date): Starting server monitor" >> $LOG_FILE

while true; do
    # Check if the server is running
    if ! pgrep -f "gunicorn --bind 0.0.0.0:8083" > /dev/null; then
        echo "$(date): Server is down, restarting..." >> $LOG_FILE
        
        # Kill any zombie processes that might be using the port
        lsof -ti:8083 | xargs kill -9 2>/dev/null
        
        # Start the server in the background
        gunicorn --bind 0.0.0.0:8083 --workers 3 --timeout 120 app:app > $SERVER_LOG 2>&1 &
        
        echo "$(date): Server restarted with PID $!" >> $LOG_FILE
        
        # Give the server time to start
        sleep 5
    else
        echo "$(date): Server is running" >> $LOG_FILE
    fi
    
    # Check every 30 seconds
    sleep 30
done 