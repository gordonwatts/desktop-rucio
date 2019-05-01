#!/bin/env bash
#
# Copy down certificates from ATLAS so that rucio will work correctly.
#
# Usage: <lxplus-user-name>
#
if [ $# -ne 2 ]
  then
    echo "Usage: sync_cert_with_ATLAS.sh <rucio-username> <cert-password>"
    exit
fi

# Get username and password
user=$1
certpassword=$2

echo "To copy certificate files from lxplus.cern.ch, I need your lxplus password"
echo -n "lxplus Password: "
read -s password
echo

rshInfo="sshpass -p $password ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -l $user"

# Now start doing the rsync
rsync -zhl --rsh="$rshInfo" $user@lxplus.cern.ch:/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/emi/4.0.3-1v3/etc/vomses/* /etc/vomses
rsync -zhl --rsh="$rshInfo" $user@lxplus.cern.ch:/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/emi/4.0.3-1v3/etc/grid-security/vomsdir/atlas/* /etc/grid-security/vomsdir/atlas
rsync -zhl --rsh="$rshInfo" $user@lxplus.cern.ch:/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/emi/4.0.3-1v3/etc/grid-security/certificates/* /etc/grid-security/certificates
rsync -zhl --rsh="$rshInfo" $user@lxplus.cern.ch:/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/etc/grid-security-emi/certificates/* /etc/grid-security/certificates
rsync -zhl --rsh="$rshInfo" $user@lxplus.cern.ch:/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/rucio-clients/1.19.5/etc/ca.crt /etc/ca.crt.1
cp /etc/ca.crt.1 /etc/ca.crt
rsync -zhl --rsh="$rshInfo" $user@lxplus.cern.ch:/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase/x86_64/rucio-clients/1.18.5/etc/rucio.cfg /opt/rucio/etc/rucio.cfg.1
cp /opt/rucio/etc/rucio.cfg.1 /opt/rucio/etc/rucio.cfg
echo "auth_type = x509_proxy" >> /opt/rucio/etc/rucio.cfg

# Great, lets get the cert setup.
source /root/web/setup.sh
echo $certpassword | voms-proxy-init -voms atlas
echo
echo
echo "Running rucio ping to make sure all is ok. Should repond with a version number"
rucio ping
