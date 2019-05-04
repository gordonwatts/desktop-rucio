# !/bin/env bash
#
# Script to start this container running on linux with sinularity or docker.
# It is here because there are a bunch of directories that need to have certificates, etc.,
# in order for everything to work. This makes life a bit easier by doing a bunch of work for you.
#
# Yes: This is a pain. But without making all these certs public, I'm not sure what the "right"
# way to do this is.
#

# Process options
containerVersion="latest"
webPort=8000
voms="atlas"
startBash=0
certUpdate=0
args=()
while [ -n "$1" ]; do
    case "$1" in
	-v)
	    containerVersion="$2"
	    shift
	    ;;
	-p)
	    webPort="$2"
	    shift
	    ;;
	-g)
	    voms="$2"
	    shift
	    ;;
	-b) startBash=1 ;;
	-u) certUpdate=1 ;;
	*) args+=( $1 ) ;;
    esac
    shift
done
	    
if [ ${#args[@]} -ne 4 ]; then
    echo ${args[@]}
    echo "Usage: startDesktopRucio.sh -ubgpv <cert-path> <data-path> <grid-passwd> <rucio-account-name>"
    exit
fi
cert_path=${args[0]}
data_path=${args[1]}
grid_password=${args[2]}
rucio_account=${args[3]}

# If the directories do not exist, then create them. There are a lot.
if [ ! -d $cert_path ]; then
    mkdir -p $cert_path
    certUpdate=1
fi
if [ ! -d $cert_path/usercert ]; then
    mkdir $cert_path/usercert
    echo "You must copy your user certificate into $cert_path/usercert"
    certUpdate=1
fi
if [ ! -d $cert_path/vomses ]; then
    mkdir $cert_path/vomses
    certUpdate=1
fi
if [ ! -d $cert_path/grid-certs ]; then
    mkdir $cert_path/grid-certs
    certUpdate=1
fi
if [ ! -d $cert_path/vomsdir ]; then
    mkdir $cert_path/vomsdir
    certUpdate=1
fi
if [ ! -d $cert_path/vomses ]; then
    mkdir $cert_path/vomses
    certUpdate=1
fi
if [ ! -d $cert_path/vomses ]; then
    mkdir $cert_path/vomses
    certUpdate=1
fi
if [ ! -f $cert_path/rucio.cfg ]; then
    touch $cert_path/rucio.cfg
    certUpdate=1
fi
if [ ! -f $cert_path/ca.crt ]; then
    touch $cert_path/ca.crt
    certUpdate=1
fi
if [ ! -f $data_path ]; then
    mkdir -p $data_path
fi

# Helper function to run singularity
function start_image {
    cmd=$1
    detach=$2

    singularity exec \
	--contain \
        --bind $cert_path/rucio.cfg:/opt/rucio/etc/rucio.cfg \
        --bind $cert_path/usercert:/root/rawcert \
        --bind $cert_path/vomses:/etc/vomses \
        --bind $cert_path/grid-certs:/etc/grid-security/certificates \
        --bind $cert_path/vomsdir:/etc/grid-security/vomsdir \
        --bind $cert_path/ca.crt:/etc/ca.crt \
        --bind ${data_path}:/data \
        docker://gordonwatts/desktop-rucio:$containerVersion \
        $cmd

#            -e RUCIO_ACCOUNT=${RUCIOAccount} \
#            -e GRID_PASSWORD=${GRIDPassword} \
#            -e GRID_VOMS=${VOMS} \
#            -p ${WebPort}:8000 -it \
}

# Do we need to trigger an update of the certificates we've copied down?
if [ $certUpdate -eq 1 ]; then
    echo "Going to run an image to copy down certificates for rucio from lxplus. SSH is going to ask for your lxplus account password."
    echo start_image "/bin/bash /root/web/sync_cert_with_ATLAS.sh ${rucio_account} ${grid_password} ${rucio_account}" 0
fi

# Container is setup. We should just start it.
if [ $startBash -eq 1 ]; then
    echo "Sorry - starting a bash shell not yet implemented"
    echo start_image "/bin/bash" 1
else
    echo start_image "" 1
fi

exit
    function start_docker($cmd, [switch] $detach) {
        $dopt = ""
        if ($detach) {
            $dopt = "-d"
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
            -e RUCIO_ACCOUNT=${RUCIOAccount} `
            -e GRID_PASSWORD=${GRIDPassword} `
            -e GRID_VOMS=${VOMS} `
            --rm $dopt -p ${WebPort}:8000 -it `
            desktop-rucio:$containerVersion `
            $cmd"
        $str = $str -replace "`n","" -replace "`r",""
        Invoke-Expression "docker $str"
    }
    # Check that all directories properly exist.
    $needs_cert_update = $false

    # Figure out how we will start things
    $start_command = ""
    if ($StartBash) {
        $start_command = "/bin/bash"
    }

}
