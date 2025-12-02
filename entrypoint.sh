#!/bin/sh

# 1. Create the logs directory if it doesn't exist
mkdir -p /app/logs

# 2. Fix permissions (Crucial Step)
# Since this script runs as root, we can give ownership to appuser
chown -R appuser:appuser /app/logs

# 3. Step down from root and run the command (uvicorn) as appuser
# We use 'exec' so uvicorn becomes the main process (PID 1)
exec gosu appuser "$@"