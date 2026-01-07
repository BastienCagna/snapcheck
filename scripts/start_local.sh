#!/bin/bash

# Generate a secret key
SECRET=$(python scripts/secret.py)

# Start the FastAPI server in the background, without output
SNAP_SECRET="$SECRET" uvicorn python.snapserve.main:app --reload > /dev/null 2>&1 &
SERVER_PID=$!

JWT=$(python scripts/generate_token.py "$SECRET")

# Start the Qt client in the foreground, without output
python python/snapclient/main.py --jwt "$JWT" > /dev/null 2>&1

# When the Qt client exits, stop the FastAPI server
kill $SERVER_PID