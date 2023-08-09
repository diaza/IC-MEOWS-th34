import numpy as np
import matplotlib.pyplot as plt
import utils
import sys

low = int(sys.argv[1])
high = int(sys.argv[2])

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

for i in range(low, high):
    print(i)
    dirbase = "/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/Fits/BrazilPlot/AIRS_mceq121_2011_sib_HG_E3/0_0.000000_0.000000_0.000000_0.000000_0.000000_0.000000/fits/Realization_{}/".format(i)

    points = utils.get_points(dirbase,
                              dm2_list, Um4sq_list, Ut4sq_list, d24_list, "_Realization_{}.json".format(i))
    np.save(dirbase + "/Realization_{}".format(i), points)

    null_file = dirbase + "Ut4sq_0.000000/0_0.000000_0.000000_0.000000_0.000000_0.000000_0.000000_Realization_{}.json".format(i)
    null_llh = utils.get_llh(null_file)
    np.save(dirbase + "/null_llh", null_llh)
