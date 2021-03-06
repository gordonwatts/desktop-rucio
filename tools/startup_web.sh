#!/bin/bash
#
# Start everything running as a web server. To function we expect a few arguments:
#
#  ./startup_web.sh <rucio_account> <grid_password> <grid_voms>
#
if [ $# -ne 4 ]; then
    echo "Usage: $0 <rucio-account> <grid-password> <grid-voms> <cache-prefix>"
    echo "  -> $@"
    exit
fi

# Define a few env variables we are doing to need while running
export RUCIO_ACCOUNT=$1
export GRID_PASSWORD=$2
export GRID_VOMS=$3
export CACHE_PREFIX=$4

# Get all the credentials setup with correct permissions,
# make sure the proxy stuff is going to be where it should be.
source /root/web/setup.sh

# Certification manager - will keep the grid certificate vald.
python3 /root/web/cert_manager.py &

# The web server. Note that we don't run it in the background.
mkdir -p /tmp/desktop-rucio-logs
stdbuf -o0 hug -f /root/web/src/api.py &> /tmp/desktop-rucio-logs/web_server.log
