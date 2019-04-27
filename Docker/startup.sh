#!/bin/bash
#
# Start everything running

# Get all the credentials setup with correct permissions,
# make sure the proxy stuff is going to be where it should be.
source ./setup.sh

# Certification manager - will keep the grid certificate vald.
python3 cert_manager.py &

# The web server. Note that we don't run it in the background.
mkdir -p /tmp/desktop-rucio-logs
stdbuf -o0 hug -f src/api.py &> /tmp/desktop-rucio-logs/web_server.log
