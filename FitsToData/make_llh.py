import numpy as np

import utils

# flux_name = "AIRS_sib_HG_th24_th34_dm2"
# flux_name = "AIRS_mceq121_2011_sib_HG_E3"
# dir_base = "/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/Fits/FitToData/" + flux_name + "/FS_0.50/"
# suffix = '_Data_IC86.All_cut_everything_platinum_LT_240747841.json'

# dir_base = "/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/Fits/Asimov/AIRS_mceq121_2011_sib_HG_E3/CRgamma_0.06/FS_0.50/"
# suffix = "_0_0.000000_0.000000_0.000000_0.000000_0.000000_0.000000_Asimov.json"

# dir_base = "/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/Fits/Asimov/AIRS_mceq121_2011_sib_HG_E3/CRgamma_0.03/FS_0.50/"
# suffix = "_0_0.000000_0.000000_0.000000_0.000000_0.000000_0.000000_Asimov.json"

dir_base = "/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/Fits/Asimov/AIRS_mceq121_2011_sib_HG_E3/CRgamma_0.25/FS_0.50/"
suffix = "_0_0.000000_0.000000_0.000000_0.000000_0.000000_0.000000_Asimov.json"


logdm2_list = np.asarray(np.ndarray.tolist(np.arange(-2.10, 2.10, 0.1))+ [2.15])
dm2_list = np.power(10, logdm2_list)  
dm2_list = dm2_list[np.logical_and(dm2_list>.1, dm2_list<50)]
dm2_list = np.append(dm2_list, 50.0)

log_Um4sq_list = np.asarray(np.ndarray.tolist(np.arange(-3., 0., 0.1)))  
Um4sq_list = np.power(10, log_Um4sq_list)
Um4sq_list = Um4sq_list[Um4sq_list<0.50]
Um4sq_list = np.append(Um4sq_list, 0.50)

log_Ut4sq_list = np.asarray(np.ndarray.tolist(np.arange(-3., 0., 0.2)))   
Ut4sq_list = np.power(10, log_Ut4sq_list)  
Ut4sq_list = np.insert(Ut4sq_list, 0, 0.)
Ut4sq_list = Ut4sq_list[Ut4sq_list<0.50]
Ut4sq_list = np.append(Ut4sq_list, 0.50)

d24_list = [np.pi]

dir_nseed_CV = dir_base + "/n_seeds_-1/"
dir_nseed_4 = dir_base + "/n_seeds_4/"
print(dir_nseed_CV)

null_file_CV = dir_nseed_CV + "Ut4sq_0.000000/0_0.000000_0.000000_0.000000_0.000000_0.000000_0.000000" + suffix
null_file_4 = dir_nseed_4 + "Ut4sq_0.000000/0_0.000000_0.000000_0.000000_0.000000_0.000000_0.000000" + suffix

null_llh_CV = utils.get_llh(null_file_CV)
null_llh_4 = utils.get_llh(null_file_4)

if null_llh_CV < null_llh_4:
    np.save(dir_base + "null_llh", null_llh_CV)
else:
    np.save(dir_base + "null_llh", null_llh_4)

n_seed_CV = utils.get_points(dir_nseed_CV, dm2_list, Um4sq_list, Ut4sq_list, [np.pi], suffix)
n_seeds_4 = utils.get_points(dir_nseed_4, dm2_list, Um4sq_list, Ut4sq_list, [np.pi], suffix)

n_seed_CV_min = n_seed_CV[:,:,3] < n_seeds_4[:,:,3]
minimum_llhs = np.zeros(n_seed_CV.shape)
minimum_llhs[n_seed_CV_min] = n_seed_CV[n_seed_CV_min]
minimum_llhs[~n_seed_CV_min] = n_seeds_4[~n_seed_CV_min]

np.save(dir_base + "/llhs", minimum_llhs)

