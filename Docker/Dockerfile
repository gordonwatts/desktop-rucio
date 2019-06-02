# Build the desktop rucio container
#
# Invoking this container is non-trival becuase the GRID requires an insane number of certificates
# to work properly, and it is probalby not right to be distributing certificates on docker hub.
#
# Following is the command I've used to start this. This works for access ATLAS data, though
# I imagine anyone using rucio would be able to do something similar with a CMS set of
# certs. I would also imagine that is true for anyone else. Sorry!
#
# docker run -v h:/OneDrive/.ssh/rucio-config/rucio.cfg:/opt/rucio/etc/rucio.cfg -d --name=rucio-client -eRUCIO_ACCOUNT=gwatts -v h:/OneDrive/.ssh/rucio-config/usercert:/root/rawcert -v h:/OneDrive/.ssh/rucio-config/vomses:/etc/vomses -v h:/OneDrive/.ssh/rucio-config/grid-certs:/etc/grid-security/certificates -v h:/OneDrive/.ssh/rucio-config/vomsdir:/etc/grid-security/vomsdir -v h:/OneDrive/.ssh/rucio-config/ca.crt:/etc/ca.crt --rm -d -p 8000:8000 -it  desktop-rucio:alpha-0.1.0
#
# For more info see the documentation.
FROM rucio/rucio-clients:release-1.19.6

# Get the webserver installed
RUN yum -y install rsync
RUN yum -y install openssh-clients
RUN yum -y install sshpass
RUN yum -y install python36
RUN yum -y install python36-pip
RUN pip3 install --upgrade hug 

# The local files
COPY Docker/setup.sh /root/web/setup.sh
COPY Docker/sync_cert_with_ATLAS.sh /root/web/sync_cert_with_ATLAS.sh
COPY Docker/cert_manager.py /root/web/cert_manager.py
COPY Docker/startup.sh /root/web/startup.sh
COPY ./src/ /root/web/src/

EXPOSE 8000
WORKDIR /root/web
ENTRYPOINT ["/bin/bash", "/root/web/startup.sh"]
