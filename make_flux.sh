#!/bin/bash

COMMAND="python3 -u /home/adiaz/IC-MEOWS-th34/make_flux_fastmc/Fluxes.py "

#echo "mkdir -pv $OUTDIR"
#mkdir -pv $OUTDIR

export HDF5_USE_FILE_LOCKING='FALSE'

echo 'Sourcing environment'
#export NUSQUIDS_DATA_PATH=/cvmfs/icecube.opensciencegrid.org/users/BeyondStandardModel/bsm-py3-v4.1.1/share/nuSQuIDS/
source /cvmfs/icecube.opensciencegrid.org/users/carguelles/sterilize/sterilize_py3-v4.1.1/setup.sh

echo "$COMMAND $@"
eval "$COMMAND $@"
