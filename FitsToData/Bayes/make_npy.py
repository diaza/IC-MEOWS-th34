import numpy as np
import json
from os.path import exists

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

def get_ev(filename):

    f = open(filename, 'r')

    try:
        data = json.loads(f.read())
        if "BayesEvidence" in data.keys():
            llh =  data["BayesEvidence"]
        else:
            llh = -np.inf
    except json.decoder.JSONDecodeError:
        print("DecodeError, filename is {}".format(filename))
        llh = -np.inf

    f.close()

    return llh

def get_data(u_dir):

    data = np.array(len(Ut4sq_list)*[[[0,0,0,-np.inf]]*len(dm2_list)*len(Um4sq_list)*len(d24_list)])
    for k, Ut4sq in enumerate(Ut4sq_list):
        print(Ut4sq)
        i=0

        Ut4sq_dir = u_dir + "Ut4sq_" + str(format(float(Ut4sq), '.6f')) +'/'
        for d24 in d24_list:
            for dm2 in dm2_list:
                for Um4sq in Um4sq_list:

                    if Um4sq + Ut4sq > 1.:
                        i+=1
                        continue

                    th24 = np.arcsin( np.sqrt(Um4sq) )
                    th34 = np.arcsin( np.sqrt(Ut4sq/np.cos(th24)**2) )
                    point = "{:.6f}_{:.6f}_{:.6f}".format(dm2, th24, th34)
                    suffix = ".json"
    #                     print(point)
                    if exists(Ut4sq_dir + point+suffix):
                        llh = get_ev(Ut4sq_dir + point+suffix)
                        data[k][i] = [dm2, Um4sq, Ut4sq, llh]
                    else:
                        # print(Ut4sq_dir + point+suffix)
                        data[k][i] = [dm2, Um4sq, Ut4sq, -np.inf]

                    i+=1

    return data


dir_name = "/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/Fits/FitToData/AIRS_sib_HG_th24_th34_dm2/Bayes/evidence_tolerance_0.5_n_live_points_300_sampling_efficiency_0.5_crSlopeWidth_0.25/"
data = get_data(dir_name)
data_null =  np.array([0.,0.,0.,get_ev(dir_name +"Ut4sq_0.000000/0.000000_0.000000_0.000000.json")])
np.save(dir_name + "bayes_evidence_tolerance_0.5_n_live_points_300_sampling_efficiency_0.5_crSlopeWidth_0.25", data)
np.save(dir_name + "bayes_evidence_tolerance_0.5_n_live_points_300_sampling_efficiency_0.5_crSlopeWidth_0.25_null", data_null)
