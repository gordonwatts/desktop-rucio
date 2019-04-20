#
# .bashrc file to be used in the rest of the code
#

# Get the user certificates setup
if [ ! -d /root/.globus ]
then
    mkdir  /root/.globus
    cp /root/rawcert/userkey.pem /root/.globus
    cp /root/rawcert/usercert.pem /root/.globus
    chmod 400 /root/.globus/userkey.pem
    chmod 444 /root/.globus/usercert.pem
fi

# Make sure the proxy is defined.
if [ -z ${X509_USER_PROXY+x} ]; then export X509_USER_PROXY=/usr/usercertfile; fi
export RUCIO_HOME=
