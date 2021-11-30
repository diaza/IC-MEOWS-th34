import math 
import numpy as np
import os
import sys

NOTE=''
tau_neutrinos =''
fastmc_dir = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/FastMC/' + NOTE
osg = "False"

# realization_file = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/FastMC/Platinum_Split_HE_Alex_2.00_7.6_Alex_AIRS_sib_HG_th24_th34_dm2/Asimov_0_1.000000_0.000000_0.409453_0.448906_0.000000_0.000000.npz'
# realization_file = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/FastMC/notaus/Platinum_Split_HE_Alex_2.00_7.6_Alex_AIRS_sib_HG_th24_th34_dm2/Asimov_0_1.000000_0.000000_0.409453_0.448906_0.000000_0.000000.npz'
# OUTDIRNOTE = '0_1.000000_0.000000_0.409453_0.448906_0.000000_0.000000_with_taus/' + NOTE 
# OUTDIRNOTE = '0_1.000000_0.000000_0.409453_0.448906_0.000000_0.000000_without_taus/' + NOTE 

# realization_file = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/FastMC/Platinum_Split_HE_Alex_2.00_7.6_Alex_AIRS_sib_HG_th24_th34_dm2/Asimov.npz'

realization_file = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/FastMC/Platinum_Split_HE_Alex_2.00_7.6_Alex_AIRS_sib_HG_th24_th34_dm2/Asimov_0_1.000000_0.000000_0.159160_0.257232_0.000000_0.000000.npz'
OUTDIRNOTE = '0_1.000000_0.000000_0.159160_0.257232_0.000000_0.000000_with_taus/' + NOTE 

# realization_file = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/FastMC/notaus/Platinum_Split_HE_Alex_2.00_7.6_Alex_AIRS_sib_HG_th24_th34_dm2/Asimov_0_1.000000_0.000000_0.159160_0.257232_0.000000_0.000000.npz'
# OUTDIRNOTE = '0_1.000000_0.000000_0.159160_0.257232_0.000000_0.000000_without_taus/' + NOTE 


def print_vars(f, jobname, var_name, val):
    f.write('VARS\t' + jobname.strip() + '\t' + var_name+'=\"' + val+ "\"\n")


# logdm2_list = np.asarray(np.ndarray.tolist(np.arange(-2.15, 2.10, 0.05))+ [2.15])
logdm2_list = np.asarray(np.ndarray.tolist(np.arange(-2.10, 2.10, 0.1))+ [2.15])
dm2_list = np.power(10, logdm2_list)

dm2_list = dm2_list[np.logical_and(dm2_list>.1, dm2_list<50)]

log_Um4sq_list = np.asarray(np.ndarray.tolist(np.arange(-3., 0., 0.1)))
Um4sq_list = np.power(10, log_Um4sq_list)

log_Ut4sq_list = np.asarray(np.ndarray.tolist(np.arange(-3., 0., 0.2)))
Ut4sq_list = np.power(10, log_Ut4sq_list)
Ut4sq_list = np.insert(Ut4sq_list, 0, 0.)

print(dm2_list)
print(len(dm2_list), len(Um4sq_list), len(Ut4sq_list))
th14 = 0.
del14 = 0.
del24 = 0.
flux_dict = {
    'th14' :  str(format(float(th14), '.6f')),
    'indir' : "/data/user/adiaz/GolemFit/resources/FluxOscCalculator/",
    'index' : "0",
    'del14' : str(format(float(del14), '.6f')),
    'del24' : str(format(float(del24), '.6f')),
    'user' : 'adiaz', 
    'osg' : osg,
    'flux' : "AIRS_flux_sib_HG.dat"
}

fastmc_dict = {
    'gen_fastMC' : 'True',
    'Emax' : '9976',
    'sim' : 'Platinum_Split_HE_Alex',
    'max_sim' : '-1',
    'fast_scaling' : '2.00',
    'tau_neutrinos' : tau_neutrinos,
    'fastmc_dir' : fastmc_dir
}

fit_dict = {
    'use_fastMC' : 'True',
    'Emax' : '9976',
    'sim' : 'Platinum_Split_HE_Alex',
    'max_sim' : '-1', 
    'fast_scaling' : '2.00',
    'tau_neutrinos' : tau_neutrinos,
    'fastmc_dir' : fastmc_dict['fastmc_dir'],
    'realization_file' : realization_file,
    'n_seeds' : '5'
}

def make_flux(filename, jobname, fluxdir, dm2, th24, th34, Ut4sq, osg = "False"):
    if osg == "True":
        filename.write('JOB\t' + jobname + '\t/home/adiaz/Cascades/th34/make_flux_OSG.submit\n')
    else:
        filename.write('JOB\t' + jobname + '\t/home/adiaz/Cascades/th34/make_flux.submit\n')
    print_vars(filename, jobname, 'th24',  str(format(float(th24), '.6f')))
    print_vars(filename, jobname, 'th34',  str(format(float(th34), '.6f')))
    print_vars(filename, jobname, 'dmsq41',  str(format(float(dm2), '.6f')))
    print_vars(filename, jobname, 'outdir',  fluxdir)
    for key, value in flux_dict.items():
        print_vars(filename, jobname, key, value)
    filename.write('Retry ' + jobname + " 2\n")

def make_fastmc(filename, jobname, fluxdir, point, Ut4sq):
    filename.write('JOB\t' + jobname + '\t/home/adiaz/Cascades/th34/make_fastmc.submit\n')
    print_vars(filename, jobname, 'point', point)
    print_vars(filename, jobname, 'fluxdir', fluxdir)
    for key, value in fastmc_dict.items():
        print_vars(filename, jobname, key, value)
    filename.write('Retry ' + jobname + " 2\n")

def make_fit(filename, jobname, fluxdir, point, outdir, Ut4sq):
    filename.write('JOB\t' + jobname + '\t/home/adiaz/Cascades/th34/do_fit.submit\n')
    print_vars(filename, jobname, 'point', point)
    print_vars(filename, jobname, 'fluxdir', fluxdir)
    print_vars(filename, jobname, 'outdir', outdir)
    for key, value in fit_dict.items():
        print_vars(filename, jobname, key, value)
    # filename.write('Retry ' + jobname + " 2\n")

i = -1
for Ut4sq in Ut4sq_list:
    if Ut4sq == 0.:
        j = 1
        points = [(0.,0.,0.)]*(len(dm2_list)*len(Um4sq_list) + 1)
    else:
        j = 0
        points = [(0.,0.,0.)]*(len(dm2_list)*len(Um4sq_list))

    for Um4sq in Um4sq_list:
        for dm2 in dm2_list:
            points[j] = (dm2, Um4sq, Ut4sq)
            j+=1

    years = str(7.6)
    F = os.getcwd() + '/Ut4sq_' + str(format(float(Ut4sq), '.6f')) + '.dag'
    with open(F, 'w') as f:

        for (dm2, Um4sq, Ut4sq) in  points:
            i += 1

            fluxdir = "/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/Fluxes/AIRS_sib_HG_th24_th34_dm2/Ut4sq_" + str(format(float(Ut4sq), '.6f')) + '/'
            # os.makedirs(fluxdir, exist_ok=True)
            outdir = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/Asimov/'+OUTDIRNOTE+'Ut4sq_' + str(format(float(Ut4sq), '.6f')) + '/'
            if Um4sq + Ut4sq > 1.:
                continue
            th24 = np.arcsin(np.sqrt(Um4sq))

            th34 = np.arcsin(np.sqrt( Ut4sq / (1.-Um4sq) ) )

            jobname_A = str(i) + "A"
            make_flux(f, jobname_A, fluxdir, dm2, th24, th34, Ut4sq, osg)

            if not math.isclose(Ut4sq,  np.sin(th34)**2 * np.cos(th24)**2):
                print("ohno", Ut4sq, np.sin(th34)**2 * np.cos(th24)**2)

            # jobname_B = str(i) + "B"
            # point = flux_dict['index'] + "_" + str(format(float(dm2), '.6f')) + "_" + flux_dict['th14'] + "_" + str(format(float(th24), '.6f')) + "_" +str(format(float(th34), '.6f')) + "_" + flux_dict['del14'] + "_" + flux_dict['del24']
            # description = fastmc_dict['sim']+'_'+fastmc_dict['fast_scaling']+'_'+years+'_'+fluxdir.split('/')[-3]+'/'+fluxdir.split('/')[-2]+'/'+ point+'/'

            # if not os.path.exists(fastmc_dict['fastmc_dir'] + description +'/STERILE.meows'):
                # make_fastmc(f, jobname_B, fluxdir, point, Ut4sq)
                # jobname_C = str(i) + "C"
                # make_fit(f, jobname_C, fluxdir, point, outdir, Ut4sq)
                # f.write("PARENT " + jobname_B + " CHILD " + jobname_C + "\n")
                # continue

            # if not os.path.exists(outdir+ point+'_'+ fit_dict['realization_file'].split('/' )[-1].split('.npz')[0]+'.json'):
                # jobname_C = str(i) + "C"
                # make_fit(f, jobname_C, fluxdir, point, outdir, Ut4sq)
                # continue

            # f.write("PARENT " + jobname_A + " CHILD " + jobname_B + "\n")


