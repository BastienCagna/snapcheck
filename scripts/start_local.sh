#!/bin/bash

# Lancer le serveur FastAPI en arrière-plan, sans affichage
uvicorn python.snapserve.main:app --reload > /dev/null 2>&1 &
SERVER_PID=$!

# Lancer le client Qt au premier plan, sans affichage
python python/snapclient/main.py > /dev/null 2>&1

# Quand le client Qt se termine, arrêter le serveur FastAPI
echo "Arrêt du serveur FastAPI (PID $SERVER_PID)..."
kill $SERVER_PID