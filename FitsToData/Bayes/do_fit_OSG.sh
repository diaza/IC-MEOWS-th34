#!/bin/bash

COMMAND="python3 -u Brazil.py "

export HDF5_USE_FILE_LOCKING='FALSE'

echo 'Sourcing environment'
#export NUSQUIDS_DATA_PATH=/cvmfs/icecube.opensciencegrid.org/users/BeyondStandardModel/bsm-py3-v4.1.1/share/nuSQuIDS/
source /cvmfs/icecube.opensciencegrid.org/users/carguelles/sterilize/sterilize_py3-v4.1.1/setup.sh

ls -lht
echo "Copying possible recap files"
echo "globus-url-copy -nodcau -rst -v gsiftp://gridftp.icecube.wisc.edu/$OUTDIR/$POINT_PREFIX* file:$PWD/"
eval "globus-url-copy -nodcau -rst -v gsiftp://gridftp.icecube.wisc.edu/$OUTDIR/$POINT_PREFIX* file:$PWD/"
ls -lht

#mkdir -p ./$FLUXDIR
#find $FLUXDIR/*$POINT* -exec cp {} ./$FLUXDIR \;

echo "$COMMAND $@ "
eval "$COMMAND $@ &"

sleep 3600
while [ -e /proc/$! ]; do
        ls -lht
        echo "globus-url-copy -nodcau -rst -v file:$PWD/$POINT_PREFIX* gsiftp://gridftp.icecube.wisc.edu/$OUTDIR"
        eval "globus-url-copy -nodcau -rst -v file:$PWD/$POINT_PREFIX* gsiftp://gridftp.icecube.wisc.edu/$OUTDIR"
        sleep 3600
done
