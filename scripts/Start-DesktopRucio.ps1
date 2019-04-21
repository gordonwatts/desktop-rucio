# Script to start this container running on Windows.
# It is here because there are a bunch of directories that need to have certificates, etc.,
# in them in order to work.
#
# Here, we make the assumption that everything has a particular directory structure.
#
# Yes: This is a pain. But without making all these certs public, I'm not sure what the "right"
# way to do this is.
#
# TODO: CertPath needs to be non-empty
Param(
    # The certifcate folder path
    [Parameter(Mandatory=$true)]
    [ValidateScript({Test-Path $_ -PathType 'Container'})]
    [string]
    $CertPath,

    [Parameter(Mandatory=$true)]
    [string]
    $GRIDPassword,

    [string]
    $containerVersion = "alpha-0.1.0",

    [string]
    $RUCIOAccount = "gwatts",

    [int]
    $WebPort = 8000,

    [string]
    $VOMS = "atlas",

    [switch]
    $StartBash
)
Process {
    $start_command = ""
    if ($StartBash) {
        $start_command = "/bin/bash"
    }
    docker run `
        -v $CertPath/rucio.cfg:/opt/rucio/etc/rucio.cfg `
        -v $CertPath/usercert:/root/rawcert `
        -v $CertPath/vomses:/etc/vomses `
        -v $CertPath/grid-certs:/etc/grid-security/certificates `
        -v $CertPath/vomsdir:/etc/grid-security/vomsdir `
        -v $CertPath/ca.crt:/etc/ca.crt `
        --name=desktop-rucio `
        -e RUCIO_ACCOUNT=${RUCIOAccount} `
        -e GRID_PASSWORD=${GRIDPassword} `
        -e GRID_VOMS=${VOMS} `
        --rm -d -p ${WebPort}:8000 -it `
        desktop-rucio:$containerVersion `
        $start_command
}
