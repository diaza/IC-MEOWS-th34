#!/bin/bash

COMMAND="python3 -u /home/adiaz/IC-MEOWS-th34/Brazil.py "

export HDF5_USE_FILE_LOCKING='FALSE'

echo 'Sourcing environment'
#export NUSQUIDS_DATA_PATH=/cvmfs/icecube.opensciencegrid.org/users/BeyondStandardModel/bsm-py3-v4.1.1/share/nuSQuIDS/
source /cvmfs/icecube.opensciencegrid.org/users/carguelles/sterilize/sterilize_py3-v4.1.1/setup.sh

mkdir -p ./$FLUXDIR
find $FLUXDIR/*$POINT* -exec cp {} ./$FLUXDIR \;

echo ${SEQ[@]}

for i in ${SEQ[@]};
do
    realization_file=${outdirbase}/realizations/Realization_${i}.npz;
    outdir=${outdirbase}/fits/Realization_${i}/Ut4sq_${Ut4sq}/
    echo "$COMMAND $@ --realization_file ${realization_file} --outdir ${outdir} --fluxdir ./$FLUXDIR"
    eval "$COMMAND $@ --realization_file ${realization_file} --outdir ${outdir} --fluxdir ./$FLUXDIR"

done
