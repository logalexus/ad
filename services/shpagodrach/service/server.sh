#!/usr/bin/env bash
echo "[DEBUG] Starting server.sh in: $(pwd)"
cd task
echo "$(ls -lah)"
echo "$(pwd)"
socat tcp-l:1337,fork,reuseaddr exec:"sudo -E -u root ./chall"