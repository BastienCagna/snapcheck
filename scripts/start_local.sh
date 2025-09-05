#!/bin/bash

# Start the FastAPI server in the background, without output
uvicorn python.snapserve.main:app --reload > /dev/null 2>&1 &
SERVER_PID=$!

# Start the Qt client in the foreground, without output
python python/snapclient/main.py > /dev/null 2>&1

# When the Qt client exits, stop the FastAPI server
kill $SERVER_PID