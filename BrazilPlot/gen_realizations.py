import os
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--point', type=str, required=True)
parser.add_argument('--sim', type=str, default='Platinum_Split_Plus_Tau')
parser.add_argument('--fluxdir', type=str, default='/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/Fluxes/AIRS_mceq121_2011_sib_HG_E3/Ut4sq_0.000000/')
parser.add_argument('--fast_scaling', type=str, required=True)
parser.add_argument('--realization_loc', type=str, required=True)


args = parser.parse_args()

os.system("python3 -u ./../Brazil.py  --point {point} --use_fastMC True --Emax 9976 --sim {sim} --max_sim -1 --fast_scaling {fast_scaling} --fastmc_dir /data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/FastMC/ --years 7.634 --fluxdir {fluxdir} --gen_realization True --realization_loc {realization_loc}".format(point=args.point, sim = args.sim, fluxdir = args.fluxdir, fast_scaling = args.fast_scaling, realization_loc = args.realization_loc))
