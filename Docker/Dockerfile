# Build the desktop rucio container
# See the Start up scripts to see how to run this container.
# For more info see the documentation.
FROM rucio/rucio-clients:release-1.19.6

# Get the webserver installed
RUN yum -y install python36 python36-pip wget
COPY requirements.txt .
RUN pip3 install -r requirements.txt 

# The func_adl
RUN mkdir /root/web
WORKDIR /root/web
RUN wget -q https://github.com/gordonwatts/functional_adl/releases/download/v0.1.0/functional_adl-0.1.0-py3-none-any.whl
RUN pip3 install /root/web/*.whl

# The certificates so rucio can properly access everything
COPY certs/opt/rucio/etc/rucio.cfg /opt/rucio/etc/rucio.cfg
COPY certs/etc/ca.crt /etc/ca.crt

COPY certs/etc/vomses/ /etc/vomses/
COPY certs/etc/grid-security/certificates/ /etc/grid-security/certificates/
COPY certs/etc/grid-security/vomsdir/ /etc/grid-security/vomsdir/

# The local files
COPY ./src/ /root/web/src/
COPY ./tools /root/web

# Turn this on so that stdout isn't buffered - otherwise logs in kubectl don't
# show up until much later!
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
ENTRYPOINT ["/bin/bash", "/root/web/startup_web.sh"]
