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
    [ValidateScript({Test-Path $_ -PathType 'Container'})]
    [string]
    $DataDirectory,

    [Parameter(Mandatory=$true)]
    [string]
    $GRIDPassword,

    [Parameter(Mandatory=$true)]
    [string]
    $RUCIOAccount,

    [string]
    $containerVersion = "latest",

    [int]
    $WebPort = 8000,

    [string]
    $VOMS = "atlas",

    [switch]
    $StartBash,

    [switch]
    $CertificateUpdate
)
Process {
    function start_docker($entry="", $cmd="", [switch] $detach) {
        $dopt = ""
        if ($detach) {
            $dopt = "-d"
        }
        $entry_opt = ""
        if ($entry -ne "") {
            $entry_opt = "--entrypoint $entry"
        }
        $str = "run `
            -v $CertPath/rucio.cfg:/opt/rucio/etc/rucio.cfg `
            -v $CertPath/usercert:/root/rawcert `
            -v $CertPath/vomses:/etc/vomses `
            -v $CertPath/grid-certs:/etc/grid-security/certificates `
            -v $CertPath/vomsdir:/etc/grid-security/vomsdir `
            -v $CertPath/ca.crt:/etc/ca.crt `
            -v ${DataDirectory}:/data `
            --name=desktop-rucio `
            --rm $dopt -p ${WebPort}:8000 -it `
            $entry_opt `
            gordonwatts/desktop-rucio:$containerVersion `
            $cmd"
        $str = $str -replace "`n","" -replace "`r",""
        Invoke-Expression "docker $str"
    }
    # Check that all directories properly exist.
    $needs_cert_update = $false
    if (!(Test-Path -Path $CertPath)) {
        $junk = New-Item -ItemType Directory $CertPath
        $needs_cert_update = $true
    }
    if (!(Test-Path -Path $CertPath/usercert)) {
        $junk = New-Item -ItemType Directory $CertPath/usercert
        $needs_cert_update = $true
    }
    if (!(Test-Path -Path $CertPath/vomses)) {
        $junk = New-Item -ItemType Directory $CertPath/vomses
        $needs_cert_update = $true
    }
    if (!(Test-Path -Path $CertPath/grid-certs)) {
        $junk = New-Item -ItemType Directory $CertPath/grid-certs
        $needs_cert_update = $true
    }
    if (!(Test-Path -Path $CertPath/vomsdir)) {
        $junk = New-Item -ItemType Directory $CertPath/vomsdir
        $needs_cert_update = $true
    }
    if (!(Test-Path -Path $CertPath/rucio.cfg)) {
        $junk = New-Item -ItemType File $CertPath/rucio.cfg
        $needs_cert_update = $true
    }
    if (!(Test-Path -Path $CertPath/ca.crt)) {
        $junk = New-Item -ItemType File $CertPath/ca.crt
        $needs_cert_update = $true
    }
    if (!(Test-Path -Path $DataDirectory)) {
        $junk = New-Item -ItemType Directory $DataDirectory
        $needs_cert_update = $true
    }

    # If this is the first time, then we should invoke the script that will copy everything over.
    if ($needs_cert_update -or $CertificateUpdate) {
        Write-Host "Not all certificates are downloaded. Will run script in container to copy everything from lxplus."
        start_docker -entry "/bin/bash" -cmd "/root/web/sync_cert_with_ATLAS.sh ${RUCIOAccount} ${GRIDPassword} ${RUCIOAccount}"
    }

    # Start as approprite
    if ($StartBash) {
        start_docker -entry "/bin/bash"
    } else {
        start_docker -cmd "$RUCIOAccount $GRIDPassword $VOMS" -detach
    }
}
