# Script to start this container running on Windows.
# It is here because there are a bunch of directories that need to have certificates, etc.,
# in them in order to work.
#
# Here, we make the assumption that everything has a particular directory structure.
#
# Yes: This is a pain. But without making all these certs public, I'm not sure what the "right"
# way to do this is.
#
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
            -v ${CertPath}:/root/rawcert `
            -v ${DataDirectory}:/data `
            --name=desktop-rucio `
            --rm $dopt -p ${WebPort}:8000 -it `
            $entry_opt `
            gordonwatts/desktop-rucio:$containerVersion `
            $cmd"
        $str = $str -replace "`n","" -replace "`r",""
        Invoke-Expression "docker $str"
    }

    # Start as approprite
    if ($StartBash) {
        start_docker -entry "/bin/bash"
    } else {
        start_docker -cmd "$RUCIOAccount $GRIDPassword $VOMS file://${DataDirectory}" -detach
    }
}
