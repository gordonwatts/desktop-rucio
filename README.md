# desktop-rucio

A docker container that will automate downloading GRID files via rucio to your local machines.

## Usage

Working with the GRID means dealing with security. This has a few side effects that one needs to be
aware of before using this package:

- The certificates that rucio needs to communicate with the GRID can't be distributed in docker.
- The certificates are different for different experiments - what you use for ATLAS and CMS will be very different.
- The certificates change over time, especially the certificate revocation lists - and must be updated about once a day.
- The docker container needs access to your personal certificates in order to access the web (as you would expect). This container
  only supports X509 at the moment (it wouldn't be hard to add others if one wanted - see the Development section below).
- Out of the box a script is provided to fetch the certificates from ATLAS only. I'm happy to take PR for other experiments.

### Before Running

Make sure you have a clean directory set aside on your host machine to hold the files and some meta-data from `desktop-rucio`.
Do the same with a directory where the system can keep a set of certificates. Make sure `docker` is allowed to share these
mount points with containers (e.g. on Windows, you must explicitly grant `docker` permission to access each disk).

### Starting the container

Scripts have been written to make this simpler to start as some significant mapping must be done between the container and the
host system.

### Using `desktop-rucio`

The interface is all based on the web API access point. The following are accessible:

- status: The status of the server.
- logs: Log files on the server
- dsfiles: file lists of `rucio` datasets.
- ds: Downloading and inspecting datasets on the server.

#### status

Example:

    $ curl http://localhost:8000/status
    {"grid_cert": {"is_good": true}, "rucio_download": {"downloading": ["mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795"]}}

Returns the status. For example `grid_cert` lets you know the status of the most recent `voms_proxy_init` command.

#### logs

Examples:

    $ curl http://localhost:8000/logs
    ["web_server", "rucio_downloader", "grid_cert"]

Returns the known logs in the system.

    $ curl http://localhost:8000/logs?name=grid_cert
    ["Enter GRID pass phrase for this identity:Contacting voms2.cern.ch:15001 [/DC=ch/DC=cern/OU=computers/CN=voms2.cern.ch] \"atlas\"...\n",
     "Remote VOMS server contacted succesfully.\n",
     "\n",
     "\n",
     "Created proxy in /usr/usercertfile.\n",
     "\n",
     "Your proxy is valid until Mon Apr 29 21:50:37 UTC 2019\n"]

Returns the contents of a log file.

#### dsfiles

## Design Goals

- Designed to run on a laptop or a small Tier 3 cluster that doesn't have a GRID endpoint
- Robust against temporarly loss of an internet connection
- Web API is the user interface, fully accessible with curl or a web browser. JSON is the communication format.
- Files are stored on users disk (not in container)
- The container can be killed at any time and restarted without getting into a bad state
- No authentication to access the web API or the disk files
- Low battery usage if the container is idle.
- General approach to command failures is to retry. There are a few 5 minute timers in the code to keep
  it from re-trying too frequently.

I'm positive there are bugs in the code, so these goals may currently be aspirational.

## Development

