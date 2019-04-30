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

#### Windows



#### Linux

### Using `desktop-rucio`

The interface is all based on the web API access point. The following are accessible:

- status: The status of the server.
- logs: Log files on the server
- defiles: file lists of `rucio` datasets.
- ds: Downloading and inspecting datasets on the server.

#### status

The server gives you access to small bits of server status here.

Example:

    $ curl http://localhost:8000/status
    {"grid_cert": {"is_good": true}, "rucio_download": {"downloading": ["mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795"]}}

Returns the status. For example `grid_cert` lets you know the status of the most recent `voms_proxy_init` command.

#### logs

Fetch logs from the server.

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

The server mirrors dataset catalogs from the GRID here. The catalog is downloaded on a request-by-request basis. It is assumed that once a catalog if fetched, it will
remain the same on the GRID.

Examples:

    $ curl http://localhost:8000/dsfiles?ds_name=mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795
    {"status": "query queued"}

When you first query a dataset contents, it will return the `query queued` status. Until the server manages to successfully query rucio, this will be the return.

    $ curl http://localhost:8000/dsfiles?ds_name=mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795
    {"status": "OK", "files": [
        ["mc16_13TeV:DAOD_EXOT15.17545497._000001.pool.root.1", 2159294808, 10000],
        ["mc16_13TeV:DAOD_EXOT15.17545497._000002.pool.root.1", 2158221066, 10000],
        ["mc16_13TeV:DAOD_EXOT15.17545497._000003.pool.root.1", 2167884742, 10000],
        ["mc16_13TeV:DAOD_EXOT15.17545497._000004.pool.root.1", 2160368549, 10000],
        ["mc16_13TeV:DAOD_EXOT15.17545497._000005.pool.root.1", 2166811000, 10000]
        ]
    }

Once the query has been successfully completed, the `desktop-rucio` responds with a triplet list for each file. The triplet is composed of the `rucio` filename,
its size in bytes, and the number of events the file contains.

#### ds

This end point can be used to query, and also query files already on the server as well as trigger a download.
This is the only URL here where it matters if you are doing a GET or a POST.

Examples:

    $ curl http://localhost:8000/ds?ds_name=mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795
    {"status": "not_on_server", "filelist": []}

When a GET is done on a dataset that has not been downloaded to `desktop-rucio` it will respond with `not_on_server`. Note that this will be the response you get even if the
dataset doesn't exist (unless the server knows for a fact it doesn't exist due to a previous `dsfiles` or POST `ds` request). In short, this GET request will not initiate an access
to `rucio` or the cloud.

    $ curl -X POST http://localhost:8000/ds?ds_name=mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795
    {"status": "downloading", "filelist": []}

A POST done on an unknown dataset will trigger a download. At this point `desktop-rucio` will attempt to download the dataset. As long as it exists, the download will continue even
across restarts of the container, dropped internet connections, etc.

    $ curl http://localhost:8000/ds?ds_name=mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795
    {"status": "local", "filelist": [
        "mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795/DAOD_EXOT15.17545497._000001.pool.root.1", "mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795/DAOD_EXOT15.17545497._000002.pool.root.1", "mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795/DAOD_EXOT15.17545497._000003.pool.root.1", "mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795/DAOD_EXOT15.17545497._000004.pool.root.1", "mc16_13TeV.311309.MadGraphPythia8EvtGen_A14NNPDF31LO_HSS_LLP_mH125_mS5_ltlow.deriv.DAOD_EXOT15.e7270_e5984_s3234_r10201_r10210_p3795/DAOD_EXOT15.17545497._000005.pool.root.1"
        ]
    }

This is a GET done on a data-set that has already been pinned to the `desktop-rucio` server. Note the fully qualified name.
The names are relative to the data directory you provided when the container was started.

### Other Usage Comments

The container is designed to be stopped and restarted at anytime (e.g. `docker stop desktop-rucio`). If you are in a coffee shop and do not want to
saturate the internet, for example, feel free to just kill it, and then restart it when you later have a good connection. If you move to an area that
has no internet for your laptop, the container shouldn't be bothered - and should use very small amounts of CPU. Given a large file to download,
and a good internet connection, it will use a significant amount of resources, however!

It is possible to access the environment and run any `rucio` command you like. For example, to list datasets. Use the command `docker exec -it desktop-rucio /bin/bash`, and
as soon as you have a prompt issue `source ./setup.sh` to configure your environment.

## Design Goals

- Designed to run on a laptop or a small Tier 3 cluster that doesn't have a GRID endpoint
- Robust against temporary loss of an internet connection
- Web API is the user interface, fully accessible with curl or a web browser. JSON is the communication format.
  Designed to be used by other python libraries as opposed to humans (though possible with a web browser!)
- Files are stored on users disk (not in container)
- The container can be killed at any time and restarted without getting into a bad state
- No authentication to access the web API or the disk files
- Low battery usage if the container is idle.
- General approach to command failures is to retry. There are a few 5 minute timers in the code to keep
  it from re-trying too frequently.

I'm positive there are bugs in the code, so these goals may currently be aspirational.

## Development

A few quick items:

- PR are gratefully accepted on [github](https://github.com/gordonwatts/desktop-rucio).
- To run unit tests use `pytest` from the base directory of the package. If you fix bugs or add new features,
  please do your best to follow the convention and add tests.
- To build the `docker` container use `docker build -t desktop-rucio:alpha-1.0.0 Docker/Dockerfile .` from the package root directory
