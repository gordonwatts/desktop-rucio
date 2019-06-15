#!/bin/bash
#
# Start everything running as a rabbit server. To function we expect a few arguments:
#
#  ./startup_rabbit.sh <rucio_account> <grid_password> <grid_voms> <rabbit_server>
#
if [ $# -ne 5 ]; then
    echo "Usage: $0 <rucio-account> <grid-password> <grid-voms> <cache-prefix> <rabbit-server>"
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

# Run and listen to the rabbit mq server for things to do.
python3 download_did_rabbit.py $5
