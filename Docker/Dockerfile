# Build the desktop rucio container
#
# Invoking this container is non-trival becuase the GRID requires an insane number of certificates
# to work properly, and it is probalby not right to be distributing certificates on docker hub.
#
# Following is the command I've used to start this. This works for access ATLAS data, though
# I imagine anyone using rucio would be able to do something similar with a CMS set of
# certs. I would also imagine that is true for anyone else. Sorry!
#
# docker run -v h:/OneDrive/.ssh/rucio-config/rucio.cfg:/opt/rucio/etc/rucio.cfg -it -d --name=rucio-client -eRUCIO_ACCOUNT=gwatts -v h:/OneDrive/.ssh/rucio-config/usercert:/root/rawcert -v h:/OneDrive/.ssh/rucio-config/vomses:/etc/vomses -v h:/OneDrive/.ssh/rucio-config/grid-certs:/etc/grid-security/certificates -v h:/OneDrive/.ssh/rucio-config/vomsdir:/etc/grid-security/vomsdir -v h:/OneDrive/.ssh/rucio-config/ca.crt:/etc/ca.crt --rm  desktop-rucio:alpha-0.1.0
#
# For more info see the documentation.
FROM rucio/rucio-clients:release-1.19.6

COPY setup.sh /root/setup.sh
RUN echo "source /root/setup.sh" >> /root/.bashrc

CMD ["/bin/bash"]