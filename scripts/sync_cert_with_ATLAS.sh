#!/bin/bash
#
# Copy down certificates from ATLAS so that rucio will work correctly.
#
# Usage: <lxplus-user-name>
#
if [ $# -ne 1 ]
  then
    echo "Usage: sync_cert_with_ATLAS.sh <lxplus-username>"
    exit
fi

# We will write everything out into a "certs" directory
if [ ! -d certs ];
  then
  mkdir certs
fi

# Get lxplus username
user=$1

echo "To copy certificate files from lxplus.cern.ch, I need your lxplus password"
echo -n "lxplus Password: "
read -s password
echo

rshInfo="sshpass -p $password ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -l $user"

# Now start doing the rsync
mkdir -p ./certs/etc/vomses
rsync -zhl --copy-links --rsh="$rshInfo" $user@lxplus.cern.ch:/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/emi/4.0.3-1v3/etc/vomses/* ./certs/etc/vomses
mkdir -p ./certs/etc/grid-security/vomsdir/atlas
rsync -zhl --copy-links --rsh="$rshInfo" $user@lxplus.cern.ch:/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/emi/4.0.3-1v3/etc/grid-security/vomsdir/atlas/* ./certs/etc/grid-security/vomsdir/atlas
mkdir -p ./certs/etc/grid-security/certificates
rsync -zhl --copy-links --rsh="$rshInfo" $user@lxplus.cern.ch:/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/emi/4.0.3-1v3/etc/grid-security/certificates/* ./certs/etc/grid-security/certificates
mkdir -p ./certs/etc/grid-security/certificates
rsync -zhl --copy-links --rsh="$rshInfo" $user@lxplus.cern.ch:/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/etc/grid-security-emi/certificates/* ./certs/etc/grid-security/certificates
rsync -zhl --copy-links --rsh="$rshInfo" $user@lxplus.cern.ch:/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/rucio-clients/1.19.5/etc/ca.crt ./certs/etc/ca.crt.1
cp ./certs/etc/ca.crt.1 ./certs/etc/ca.crt
mkdir -p ./certs/opt/rucio/etc
rsync -zhl --copy-links --rsh="$rshInfo" $user@lxplus.cern.ch:/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/rucio-clients/1.18.5/etc/rucio.cfg ./certs/opt/rucio/etc/rucio.cfg.1
cp ./certs/opt/rucio/etc/rucio.cfg.1 ./certs/opt/rucio/etc/rucio.cfg
echo "auth_type = x509_proxy" >> ./certs/opt/rucio/etc/rucio.cfg

# Next, remove all the revokation certificate files.
find ./certs -name \*.r0 -exec rm {} \;
