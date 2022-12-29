#!/bin/bash

COMMAND="python3 -u /home/adiaz/Cascades/th34/Brazil.py "

export HDF5_USE_FILE_LOCKING='FALSE'

echo 'Sourcing environment'
#export NUSQUIDS_DATA_PATH=/cvmfs/icecube.opensciencegrid.org/users/BeyondStandardModel/bsm-py3-v4.1.1/share/nuSQuIDS/
source /cvmfs/icecube.opensciencegrid.org/users/carguelles/sterilize/sterilize_py3-v4.1.1/setup.sh

mkdir -p ./$FLUXDIR
find $FLUXDIR/*$POINT* -exec cp {} ./$FLUXDIR \;

echo "$COMMAND $@ --fluxdir ./$FLUXDIR"
eval "$COMMAND $@ --fluxdir ./$FLUXDIR"
