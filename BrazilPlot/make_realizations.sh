#!/bin/bash

realization_loc=/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/Fits/BrazilPlot/AIRS_mceq121_2011_sib_HG_E3/

point=0_0.000000_0.000000_0.000000_0.000000_0.000000_0.000000
Ut4sq=0.000000
fluxdir=/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/Fluxes/AIRS_mceq121_2011_sib_HG_E3/Ut4sq_${Ut4sq}/

outdirname=${realization_loc}//Platinum_Split_Plus_Tau_7.634_AIRS_mceq121_2011_sib_HG_E3/Ut4sq_${Ut4sq}/${point}
mkdir -p ${outdirname}
python3 ./gen_realizations.py --point ${point} --fluxdir ${fluxdir} --fast_scaling 0.50 --realization_loc ${realization_loc}

mkdir -p ${realization_loc}/${point}/realizations
mv ${outdirname}/*  ${realization_loc}/${point}/realizations