#!/usr/bin/env python

import sys, time, os, glob, json, random, subprocess
import GolemFitPy as gf
import numpy as np
from optparse import OptionParser
from os.path import expandvars
import matplotlib as mpl
mpl.use("agg")
import matplotlib.pyplot as plt
import pylab
from pylab import *
import scipy
from scipy import stats
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
import scipy.stats
from scipy.stats import chisquare
import scipy.ndimage
import warnings

import scipy.interpolate as interpolate

try:
    import psutil
    def getMem():
        return 'Ram: '+str(np.round((psutil.Process(os.getpid()).memory_info().rss)/1.E9,4))+'GB'
except:
    def getMem():
        return 'Ram: psutil not installed'

warnings.filterwarnings("ignore")
if not sys.warnoptions:
    warnings.simplefilter("ignore")

t1 = time.time()
usage = "usage: %prog [options] inputfile"
parser = OptionParser(usage)

parser.add_option("--point",    type="string", default = '0_0.000000_0.000000_0.000000_0.000000_0.000000_0.000000',
                        help = 'The point in the physics parameter space you want to calculate. index dmsq41 [eV 2] th14 th24 th34 del14 del24.')
parser.add_option("--realization_file", type="string",  default = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/scripts/jobs/Data/Data_IC86.Fake_cut_everything_platinum_LT_240747841.npz',
                        help = 'The file that contains an array of events. Put data here.')
parser.add_option("--gen_realizations",     type="string",  default = 'False', 	
                        help ="Do you want to generate realizations at given point?")
parser.add_option("--gen_fastMC", type="string",  default = 'False', 	
                        help ="generate realizations at given point.")
parser.add_option("--use_fastMC", type="string",  default = 'True', 	
                        help ="Use the Fast Mode MC? To use it, you must have already generated it.")
parser.add_option("--sim", 		  type="string",  default = 'Platinum_Split', 	
                        help ="Name of the simulation set you want to use. MEOWS uses Platinum_Split")
parser.add_option("--fast", 	  type="string", 	default = 'False', 					
                        help = 'Use fast mode?')
parser.add_option("--fast_scaling", 	type="string", 	default = '2.00', 					
                        help = 'What scaling factor of the fast mode do you want? MEOWS analysis for data uses 0.50.')
parser.add_option("--plot", 	  type="string", 	default = 'False', 					
                        help = 'Not used right now.')
parser.add_option("--outdir", 	  type="string",  default = '/data/user/saxani/test/',
                        help = 'Where do you want to save the output? You will get a JSON and txt file for each point.')
parser.add_option("--Emax", 	type="string",  default = '9976',
                        help = 'Max energy. You should keep this at 9976 since the MultiSim assumes this in the binning.')
parser.add_option("--Emin", 	type="string",  default = '500',
                        help = 'Min energy. You should keep this at 500 since the MultiSim assumes this in the binning.')
parser.add_option("--Ebin", 	type="string",  default = '0.1',
                        help = 'Log energy bining width. You should keep this at 0.1 since the MultiSim assumes this in the binning.')
parser.add_option("--Zbin", 	type="string",  default = '0.05',
                        help = 'Linear CosZ bining width. You should keep this at 0.05 since the MultiSim assumes this in the binning.')
parser.add_option("--Zmax", 	type="string",  default = '0.0',
                        help = 'Max CosZ value. You should keep this at 0.0 since the MultiSim assumes this in the binning.')
parser.add_option("--systematics", type="string", default = '11001110',
                        help = 'Turn on and off systematics. DOMEff, HoleIce, PionKaonRatio, Nu/nubar, Norm, deltaGamma, Atm. Density, HQE DOMS.')
parser.add_option("--barr",     type="string", default = '00111111',
                        help = 'Turn on and off various barr parameters. HM,HP, WM,WP, YM,YP, ZM,ZP.')
parser.add_option("--multisim",     type="string",  default = '11',
                         help = 'Turn on and off various Multisim parameters. IceGrad0 and IceGrad1.')
parser.add_option("--astro", type="string", 
                        help="prompt and astro", default = '011')
parser.add_option("--xs", type="string", 
                        help="cross section",default = '111')
parser.add_option("--years", 	    type="string",  default = '7.6',
                        help = 'The number of livetime years in the analysis. MEOWS = 7.6.')
parser.add_option("--description", 	type="string",  default = '',
                        help = 'Not used')
parser.add_option("--n_seeds", 	    type="int",     default = 2,
                        help = 'The number of seeds used during the minization (essentially starting points for walkers). The analysis uses 5 seeds.')
parser.add_option("--bayes", 	    type="string",  default = 'False',
                        help = 'Calcualte the Bayesian factor at this point. Takes ~2-4 hours per point.')
parser.add_option("--overwrite", 	type="string",  default = 'True',
                        help = 'Overwrite file? If already generated.')
parser.add_option("--cpu", 	        type="string",  default = '1',
                        help = 'How many cpus do you want to use during the calculation?')
parser.add_option("--osg",		    type="string",  default="False", 
                        help="Is this running on the OSG?")
parser.add_option("--spit_weights",		    type="string",  default="False", 
                        help="Make an h5 file of the weights after minimization? Used for control distributions.")
parser.add_option("--inject_fit_file",		    type="string",  default="/data/user/saxani/Realization_scans/Data_Flux_AIRS_sib_HG_th24_dm2_Platinum_Split_S11001110_B00111111_A011_X111_M11_F0.25/Data/Data_IC86.All_cut_everything_platinum_LT_240747841/0_0.000000_0.000000_0.000000_0.000000_0.000000_0.000000_Data_IC86.All_cut_everything_platinum_LT_240747841.json", 
                        help="The best fit systematic values will be used")
parser.add_option("--inject_fit",		    type="string",  default="False", 
                        help="Do you want to use the fitted values from the fit file as the central values?")
parser.add_option("--fluxdir",      type="string", help="location of flux files",
	default = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/Fluxes/Flux_AIRS_sib_HG_th24_dm2/')

parser.add_option("--realization_loc", type="string",  default='', 
                        help="Set where to find/create realization directory")
parser.add_option("--fastmc_dir", type="string",  default='', 
                        help="Set where to find/create fastmc directory")
parser.add_option("--max_sim", type="int", default = -1)
parser.add_option("--tau_neutrinos", help="Add contribution from tau neutrinos",
                    action="store_true", default=False)
parser.add_option("--make_asimov", help="Create Asimov dataset",
                  action="store_true", default=False)
parser.add_option("--change_tol", type="string",  default='1e-20',
                        help="Set change tolerance of fitter")
parser.add_option("--grad_tol", type="string",  default='1e-20',
                        help="Set gradient tolerance of fitter")
# 0_50.000000_0.000000_0.039758_0.341393_0.000000_0.000000
# 0_4.466836_0.000000_0.160875_0.000000_0.000000_0.000000

(options,args) 		= parser.parse_args()

realization_file    = options.realization_file
gen_realizations    = options.gen_realizations
inject_fit_file     = options.inject_fit_file
inject_fit          = options.inject_fit
n_seeds             = options.n_seeds
bayes               = options.bayes
use_fastMC          = options.use_fastMC
gen_fastMC          = options.gen_fastMC
if gen_fastMC == 'True':
    use_fastMC = 'True'
point 		        = options.point
sim 		        = options.sim
fluxdir  	        = options.fluxdir
if not fluxdir.endswith('/'):
    fluxdir = fluxdir + '/'
fast 		        = options.fast
plot 		        = options.plot
outdir 		        = options.outdir
Emax 		        = options.Emax
Emin 		        = options.Emin
Ebin 		        = options.Ebin
Zbin 	    	    = options.Zbin
Zmax 		        = options.Zmax
systematics         = options.systematics
astro               = options.astro
xs                  = options.xs
multisim            = options.multisim
barr                = options.barr
years 		        = options.years
description         = options.description
fast_scaling        = options.fast_scaling
fast_scaling        = "%.2f" % float(fast_scaling)
cpu                 = options.cpu
overwrite           = options.overwrite
osg                 = options.osg
spit_weights        = options.spit_weights
Ebin_Edge           = 500

if options.realization_loc == '':
    realization_loc = '/data/user/adiaz/Realizations/'+ sim+'_'+years+'_'+fluxdir.split('/')[-2]+'/'+point+'/'
else:
    realization_loc = options.realization_loc +'/' + sim+'_'+years+'_'+fluxdir.split('/')[-3]+'/'+fluxdir.split('/')[-2]+'/'+point+'/'

print('Calculating the LLH at Point: ' + point)
print('Compared to the Realization: ' + realization_file)

#signal_point = realization_file.split('/')[-2]

def mkdir(path):
    folder_list = path.split('/')
    outdir = '/'
    for i in range(len(folder_list)):
        outdir = outdir +'/'+ folder_list[i]
        try:
            if not os.path.exists(outdir):
                os.mkdir(outdir)
        except:
            pass
    outdir = outdir +'/'
    return outdir
    
#realization_loc = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/scripts/jobs/Realizations/'+ sim+'_'+years+'_'+fluxdir.split('/')[-2]+'/'+point+'/'

if options.fastmc_dir == '':
    fastMC_location = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/scripts/jobs/FastMC/'+ sim+'_'+fast_scaling+'_'+years+'_'+fluxdir.split('/')[-2]+'/'+ point+'/'
else:
    fastMC_location = options.fastmc_dir + '/' + sim+'_'+fast_scaling+'_'+years+'_'+fluxdir.split('/')[-3]+'/'+fluxdir.split('/')[-2]+'/'+ point+'/'

datapath    = '/data/user/adiaz/GolemFit/'
# datapath = '/cvmfs/icecube.opensciencegrid.org/users/carguelles/sterilize/sterilize_py3-v4.1.1/shared/'

#prompt      = '/cvmfs/icecube.opensciencegrid.org/users/carguelles/sterile/resources/Fluxes/prompt/prompt_atmospheric.hdf5'
#prompt_file = fluxdir + '/prompt_atmospheric_'+point+'.hdf5'
#prompt_file = '/data/user/saxani/test_fluxes/prompt_atmospheric_0_0.000000_0.000000_0.000000_0.000000_0.000000_0.000000.hdf5'
#astro_file  = fluxdir + '/astro_'+point+'.hdf5'
#conv_file   = fluxdir + '/atmospheric_'+point+'.hdf5'



# If you are doing this calculation on the OSG, you need to send all the necessary files to the working dir that the job on the OSG is running.
if osg == 'True':
    def copy_to_OSG(NPX_file):
        subprocess.check_call(['globus-url-copy','-nodcau','-rst', '-v', '-sync','-sync-level', '0', NPX_file,"file:"+os.getcwd()+'/'+str(NPX_file.split('/')[-1])])
    def copy_to_NPX(NPX_file):
        subprocess.check_call(['globus-url-copy','-nodcau','-rst',"file:"+os.getcwd()+'/'+str(NPX_file.split('/')[-1]), NPX_file])

    #datapath = '/cvmfs/icecube.opensciencegrid.org/users/carguelles/sterile/resources/'
    datapath = '/cvmfs/icecube.opensciencegrid.org/users/carguelles/sterilize/sterilize_py3-v4.1.1/shared/'
    outfile_NPX     = 'gsiftp://gridftp.icecube.wisc.edu'+outdir + point+'_'+realization_file.split('/')[-1].split('.npz')[0]+'.json'
    # outfile_txt_NPX = outfile_NPX.replace('.json','.txt')
    outfile_npz_NPX = outfile_NPX.replace('.json','.npz')
    
    realization_file_NPX = 'gsiftp://gridftp.icecube.wisc.edu'+realization_file
    copy_to_OSG(realization_file_NPX)
    realization_file = str(os.getcwd()+'/'+realization_file_NPX.split('/')[-1])

    if inject_fit == 'True':
        inject_fit_file_NPX = 'gsiftp://gridftp.icecube.wisc.edu'+inject_fit_file
        copy_to_OSG(inject_fit_file_NPX)
        inject_fit_file = str(os.getcwd()+'/'+inject_fit_file_NPX.split('/')[-1])
    
    outdir_NPX = 'gsiftp://gridftp.icecube.wisc.edu'+outdir
    outdir = os.getcwd()+'/'

    #prompt = '/cvmfs/icecube.opensciencegrid.org/users/carguelles/sterile/resources/Fluxes/prompt/prompt_atmospheric.hdf5'

    fastMC_location = os.getcwd()+'/' 
    fastMC_NPX = 'gsiftp://gridftp.icecube.wisc.edu/' + options.fastmc_dir + '/' + sim+'_'+fast_scaling+'_'+years+'_'+fluxdir.split('/')[-3]+'/'+fluxdir.split('/')[-2]+'/'+ point+ '/STERILE.meows'
    copy_to_OSG(fastMC_NPX)
    
    fluxdir_NPX = 'gsiftp://gridftp.icecube.wisc.edu' + fluxdir
    flux_files = [  fluxdir_NPX + '/barr_grad_WM_'+point+'.hdf5',
                    fluxdir_NPX + '/barr_grad_WP_'+point+'.hdf5',
                    fluxdir_NPX + '/barr_grad_YM_'+point+'.hdf5',
                    fluxdir_NPX + '/barr_grad_YP_'+point+'.hdf5',
                    fluxdir_NPX + '/barr_grad_ZM_'+point+'.hdf5',
                    fluxdir_NPX + '/barr_grad_ZP_'+point+'.hdf5',
                    fluxdir_NPX + '/atmospheric_'+point+'.hdf5',
                    fluxdir_NPX + '/astro_'+point+'.hdf5',
                    fluxdir_NPX + '/prompt_atmospheric_'+point+'.hdf5',
                    ]

    for flux_file in flux_files:
        copy_to_OSG(flux_file)
    fluxdir = os.getcwd()+'/'
    
prompt_file = fluxdir + '/prompt_atmospheric_'+point+'.hdf5'
astro_file  = fluxdir + '/astro_'+point+'.hdf5'
conv_file   = fluxdir + '/atmospheric_'+point+'.hdf5'
   
if bayes == 'True':
    point_values = point.split('_')
    dm2 = point_values[1]
    th24 = point_values[3]
    th34 = point_values[4]
    outfile_json= outdir + dm2+'_' +th24+'_'+th34+'.json'
else:
    outfile_json = outdir + point+'_'+realization_file.split('/')[-1].split('.npz')[0]+'.json'

#outfile_txt  = outfile_json.replace('.json','.txt')
getMem()

class converter():
     def __init__(self,golemSpit):
            self.MuExEnergy = np.asarray(golemSpit[:,0])
            self.MuExZenith = np.asarray(golemSpit[:,1])
            self.MuExAzimuth= np.asarray(golemSpit[:,2])
            self.weights    = np.asarray(golemSpit[:,-1])


ConvNormCenter          = 1.
ConvNormWidth           = 0.4
AstroNormCenter         = 4.72/6.00
AstroNormWidth          = 0.36
PromptNormCenter        = 1.

if gen_realizations !='True':
    if gen_fastMC != 'True':
        try:
            check_data = np.load(realization_file)['realization']
        except:
            check_data = np.load(realization_file)['null_dist']
        Data_nevents = np.shape(check_data)[0]
        print(Data_nevents)

# Set the true values for the systeamtisc -- or the central values.
def get_CV():
    CV_dict = {}
    CV_dict['DOMeff']           = 1.27
    CV_dict['HoleIce']          = -1.
    CV_dict['pkr']              = 1.
    CV_dict['nnbr']             = 1.
    CV_dict['Normalization']    = ConvNormCenter
    CV_dict['CR']               = 0.
    CV_dict['ZenithCorrection'] = 0.
    CV_dict['HQE']              = 1.35
    CV_dict['barrHM']           = 0.
    CV_dict['barrHP']           = 0.
    CV_dict['barrWM']           = 0.
    CV_dict['barrWP']           = 0.
    CV_dict['barrYM']           = 0.
    CV_dict['barrYP']           = 0.
    CV_dict['barrZM']           = 0.
    CV_dict['barrZP']           = 0.
    CV_dict['icegrad0']         = 0.
    CV_dict['icegrad1']         = 0.
    CV_dict['promptNorm']       = PromptNormCenter
    CV_dict['astroNorm']        = AstroNormCenter
    CV_dict['astroDeltaGamma']  = 0.
    CV_dict['nuxs']             = 1.
    CV_dict['nubarxs']          = 1.
    CV_dict['kaonLosses']       = 0.

    return CV_dict

inject_dict = get_CV()

if inject_fit == 'True':
    with open(inject_fit_file) as fit_file_json:
        fit_json = json.load(fit_file_json)    
    fit_json = eval(json.dumps(fit_json))

    for sys_i in inject_dict.keys():
        inject_dict[sys_i] = float(fit_json[sys_i])
        print('Modifying the systematic: '+str(sys_i) +' = '+str(float(fit_json[sys_i])))

# Set which barr parameters will be used during the minimization
barr = barr[:8]
use_barrHM = barr[0]=='1'
use_barrHP = barr[1]=='1'
use_barrWM = barr[2]=='1'
use_barrWP = barr[3]=='1'
use_barrYM = barr[4]=='1'
use_barrYP = barr[5]=='1'
use_barrZM = barr[6]=='1'
use_barrZP = barr[7]=='1'

if '1' in barr:
    use_barr = True
else:
    use_barr = False

# Set which systematics will be used during the minimization
systematics = systematics[:8]
use_domeff  = systematics[0] == '1'
use_holeice = systematics[1] == '1'
use_nnbr    = systematics[2] == '1'
use_pkr     = systematics[3] == '1'
use_norm    = systematics[4] == '1'
use_cr      = systematics[5] == '1'
use_atm     = systematics[6] == '1'
use_hqe     = systematics[7] == '1'

if '1' in multisim:
    use_multisim = True
else:
    use_multisim = False

# Set the MultiSim parameters
use_icegrad0 = multisim[0] == '1'
use_icegrad1 = multisim[1] == '1'

# Set the MultiSim parameters
if '1' in astro:
    use_astro = True
else:
    use_astro = False
use_promptNorm      = False#astro[0] == '1'
use_astroNorm       = astro[1] == '1'
use_astroDeltaGamma = astro[2] == '1'

# Set the Cross section parameters
if '1' in xs:
    use_xs = True
else:
    use_xs = False
use_nuxs            = xs[0] == '1'
use_nubarxs         = xs[1] == '1'
use_kaonLosses      = xs[2] == '1'

t_start = time.time()

print('Using XS: '+str(use_xs))
print('           nuXS: '+str(use_nuxs))
print('        nubarXS: '+str(use_nubarxs))
print('     kaonLosses: '+str(use_kaonLosses))

print('Using Astro: '+str(use_astro))
print('           prompt: '+str(use_promptNorm))
print('        astroNorm: '+str(use_astroNorm))
print('  astroDeltaGamma: '+str(use_astroDeltaGamma))

print('Using Barr: '+str(use_barr))
print('  HM: '+str(use_barrHM))
print('  HP: '+str(use_barrHP))
print('  WM: '+str(use_barrWM))
print('  WP: '+str(use_barrWP))
print('  YM: '+str(use_barrYM))
print('  YP: '+str(use_barrYP))
print('  ZM: '+str(use_barrZM))
print('  ZP: '+str(use_barrZP))

print('Using Systematics: ')
print('  DOMEFF: '+str(use_domeff))
print(' HoleIce: '+str(use_holeice))
print('    NNBR: '+str(use_nnbr))
print('     PKR: '+str(use_pkr))
print('    NORM: '+str(use_norm))
print('      CR: '+str(use_cr))
print('     ATM: '+str(use_atm))
print('     HQE: '+str(use_hqe))

print('Using Multisim: ')
print('  IceGrad0: '+str(use_icegrad0))
print('  IceGrad1: '+str(use_icegrad1))

if not fluxdir.endswith('/'):
	fluxdir = fluxdir + '/'

if gen_realizations !='True':
    print('Using realization: '+realization_file)

print('Outfile JSON: '+str(outfile_json))
if os.path.exists(outfile_json) and overwrite != 'True':
    print('Looks like the outfile already exists. Exiting...')
    sys.exit()

# Break the name of the Point into the physics variables
dm2 	= str(np.round(float(point.split('_')[1]),4))
th24 	= float(point.split('_')[3])
s2t 	= str(np.round(np.sin(2*th24)*np.sin(2*th24),4))
th34 	= str(np.round(float(point.split('_')[4]),4))
Uu4sq   = np.sin(th24)**2
Ut4sq   = np.cos(th24)**2*np.sin(float(th34))**2

#if osg == 'True':
#    datapath = '/cvmfs/icecube.opensciencegrid.org/users/carguelles/sterile/'

if not os.path.exists(fluxdir + 'atmospheric_'+point+'.hdf5'):
    print('Cannot find flux: ' + fluxdir + 'atmospheric_' + point + '.hdf5')

# Set all the required paths and links to data and MC to run GolemFit.
datapaths                                   = gf.DataPaths(datapath)
npp                                         = gf.NewPhysicsParams()
# Point to the conventional atmospheric neutrino file
print(fluxdir + 'atmospheric_'+point+'.hdf5')
print('Conv  : '+conv_file)
print('Astro : '+astro_file)
print('Prompt: '+prompt_file )

datapaths.conventional_nusquids_atmospheric_file    = conv_file
datapaths.prompt_nusquids_atmospheric_file 	        = prompt_file
datapaths.astro_nusquids_file 	                    = astro_file
# Point to the location of the Barr parameter files.
datapaths.barr_resources_location 		    = fluxdir

# Set the true values of the systematics. These are the central values. 
fitparams 			                = gf.FitParameters(gf.sampleTag.Sterile)
fitparams.barrHM                    = inject_dict['barrHM']
fitparams.barrHP                    = inject_dict['barrHP']
fitparams.barrWM                    = inject_dict['barrWM']
fitparams.barrWP                    = inject_dict['barrWP']
fitparams.barrYM                    = inject_dict['barrYM']
fitparams.barrYP                    = inject_dict['barrYP']
fitparams.barrZM                    = inject_dict['barrZM']
fitparams.barrZP                    = inject_dict['barrZP']
fitparams.domEfficiency             = inject_dict['DOMeff']
fitparams.holeiceForward            = inject_dict['HoleIce']
fitparams.NeutrinoAntineutrinoRatio = inject_dict['nnbr']
fitparams.piKRatio                  = inject_dict['pkr']
fitparams.convNorm                  = inject_dict['Normalization']
fitparams.CRDeltaGamma              = inject_dict['CR']
fitparams.zenithCorrection          = inject_dict['ZenithCorrection']
fitparams.hqdomEfficiency           = inject_dict['HQE']
fitparams.icegrad0                  = inject_dict['icegrad0']
fitparams.icegrad1                  = inject_dict['icegrad1']
fitparams.promptNorm                = inject_dict['promptNorm']
fitparams.astroNorm                 = inject_dict['astroNorm']
fitparams.astroDeltaGamma           = inject_dict['astroDeltaGamma']
fitparams.nuxs                      = inject_dict['nuxs']
fitparams.nubarxs                   = inject_dict['nubarxs']
fitparams.kaonLosses                = inject_dict['kaonLosses']


#if NormCenter != '':
#    fitparams.convNorm                  = NormCenter
#    fitparams.astroNorm                 = AstroNormCenter
#    fitparams.promptNorm                = PromptNormCenter

# spit_weights is for the control distributions. It just spits out the weights of each MC event after minimization.
if spit_weights == 'True':
    # Here, I want to use the best fit of the analysis. 
    infile = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/Realization_scans/Data_H2_HG_SB23C_th34_0.000_Platinum_Split_S11001110_B00111111_M11_F2.00/All/LLH.json'
    with open(infile) as data_file:    
        data_dict = json.load(data_file)
    data_dict = eval(json.dumps(data_dict))

    Best_fit_file   = data_dict['best_fit_file'][0]
    point           = data_dict['best_fit_point'][0]

    with open(Best_fit_file) as data_file:
        data = json.load(data_file)
    All_dict = eval(json.dumps(data))
    
    fitparams 			                = gf.FitParameters(gf.sampleTag.Sterile)
    print(All_dict['barrWM'],All_dict['barrWP'],All_dict['barrYM'])
    fitparams.barrHM                    = float(0)
    fitparams.barrHP                    = float(0)
    fitparams.barrWM                    = float(All_dict['barrWM'])
    fitparams.barrWP                    = float(All_dict['barrWP'])
    fitparams.barrYM                    = float(All_dict['barrYM'])
    fitparams.barrYP                    = float(All_dict['barrYP'])
    fitparams.barrZM                    = float(All_dict['barrZM'])
    fitparams.barrZP                    = float(All_dict['barrZP'])
    fitparams.domEfficiency             = float(All_dict['DOMeff'])
    fitparams.holeiceForward            = float(All_dict['HoleIce'])
    fitparams.convNorm                  = float(All_dict['Normalization'])
    fitparams.CRDeltaGamma              = float(All_dict['CR'])
    fitparams.zenithCorrection          = float(All_dict['ZenithCorrection'])
    fitparams.icegrad0                  = float(All_dict['icegrad0'])
    fitparams.icegrad1                  = float(All_dict['icegrad1'])
    fitparams.promptNorm                = float(All_dict['promptNorm'])
    fitparams.astroNorm                 = float(All_dict['astroNorm'])
    fitparams.astroDeltaGamma           = float(All_dict['astroDeltaGamma'])
    fitparams.nuxs                      = float(All_dict['nuxs'])

    fitparams.nubarxs                   = float(All_dict['nubarxs'])
    fitparams.kaonLosses                = float(All_dict['kaonLosses'])
    #datapaths.conventional_nusquids_atmospheric_file    = fluxdir + 'atmospheric_'+point+'.hdf5'
    #datapaths.astro_nusquids_file                       = fluxdir + 'astro_'+point+'.hdf5'
    #datapaths.prompt_nusquids_atmospheric_file 	        = prompt_file


# These are the GOLEM fit parameters for the binning and livetime
print(fitparams.domEfficiency,fitparams.holeiceForward,fitparams.convNorm)
steering_params				        = gf.SteeringParams(gf.sampleTag.Sterile)
steering_params.simToLoad 		    = sim # The MC simulation set
steering_params.fullLivetime 		= {0:float(years)*365*24*60*60.} # The livetime of the analysis in years
steering_params.logEbinEdge 		= np.log10(Ebin_Edge) # The bin edge for energy.
steering_params.logEbinWidth 		= float(Ebin) # The bin width in log energy
steering_params.minFitEnergy 		= float(Emin) # The min energy
steering_params.maxFitEnergy 		= float(Emax) # The max energy
#steering_params.maxFitZenith 		= float(Zmax) # The max cosZ

steering_params.maxCosth        = float(Zmax)
print('AAAAAAAAAAAAAAAAAAAAAAa')
print(steering_params.maxCosth)


steering_params.cosThbinEdge 		= 0.0#0.0#-0.10          # The min cosZ
steering_params.cosThbinWidth 		= float(Zbin) # The cosZ bin width
steering_params.sterile_model_label = point       # The point in the parameter space of interest.

steering_params.use_single_conventional_atmospheric_neutrino_file = True    # We describe the neutrino flux in a single file.
steering_params.load_atmospheric_density_spline     = True#use_atm       # Use the spline for the atm. density systematic
steering_params.spline_dom_efficiency   			= True#use_domeff    # Use the splines for the DOM efficiency
steering_params.spline_hqdom_efficiency             = use_hqe       # Use the splines for the HQE DOMs
steering_params.spline_hole_ice   					= True#use_holeice   # Use the splines for the hole ice systematics
steering_params.use_precalculated_nusquids_fluxes 	= True          # Use the flux files
steering_params.load_barr_gradients     		    = True#use_barr      # Use the Barr gradients
steering_params.use_ice_gradients                   = True#use_multisim  # Use the ice multisim gradients
steering_params.evalThreads                         = int(cpu)      # How many cpus are you using
steering_params.quiet                               = False         #
steering_params.fastmode_scaling                    = float(fast_scaling) # The MC can be compressed to improve RAM and minimization time. This is the compression factor.
steering_params.spline_attenuation                  = True#use_xs
steering_params.use_nusquids_height_sampling        = False
steering_params.load_kaon_losses_spline             = True#use_kaonLosses
steering_params.add_contribution_from_tau_neutrinos = options.tau_neutrinos
if options.max_sim != -1:
    steering_params.maximum_number_of_hdf5_files_to_read = options.max_sim
steering_params.change_tol = float(options.change_tol)
steering_params.grad_tol = float(options.grad_tol)

# The following selects what we are doing with the MC. Are we generateing the FastMC, reading the FastMC, or using the MC straight up?
if use_fastMC == 'True':
    print('Using FastMC.')
    datapaths.compact_file_path                 = fastMC_location # The location of the Fast MC.
    if gen_fastMC == 'True':
        # You are generateing the fast MC. Check to see if the Fast MC already exists.
        if os.path.exists(datapaths.compact_file_path+'/STERILE.meows'):
            print('Fast MC already exists.')
            print(datapaths.compact_file_path+'/STERILE.meows')
            sys.exit()
        else:
            print('Generating the FastMC requires fast mode to True.')
            mkdir(fastMC_location)
            steering_params.fastmode        = True  # If you are generating Fast MC you need the fast Mode.
            steering_params.readCompact     = False # ReadCompact is whether you want to use the fast MC. Here, it wasn't generated yet.
            t1_gf = time.time()
            golemfit = gf.GolemFit(datapaths,steering_params,npp) # setup Golem fit.
            t2_gf = time.time()
            print('Setting up GolemFit took' + str(t2_gf-t1_gf) + ' seconds')
            print('Loading MC with Fast Mode: '+getMem())
            print('Writing FastMC to: '+datapaths.compact_file_path)
            golemfit.WriteCompact()                 # WriteCompact writes the generated FastMC to a file in the compact_file_path location
            if osg == 'True':
                NPX_file = fastMC_NPX 
                subprocess.check_call(['globus-url-copy','-nodcau','-rst',"file:"+os.getcwd()+'/'+str(NPX_file.split('/')[-1]), NPX_file])
            sys.exit()  # After finishing generating the FastMC, you can exit.

    if not os.path.isfile(datapaths.compact_file_path+'/STERILE.meows'):
        print('FastMC does not exists: '+datapaths.compact_file_path+'/STERILE.meows')
        sys.exit()
    else:
        steering_params.fastmode    = False # We are going to use the FastMC, have to set FastMode to false
        steering_params.readCompact = True  # Read the fast MC that was generated earlier.
        print('Starting... '+getMem())
        t1 = time.time()
        golemfit = gf.GolemFit(datapaths,steering_params,npp)
        t2 = time.time()
        print('FastMC consumption: '+getMem())

else:
    print('Not using Fast mode.')
    steering_params.fastmode    = False # We are not using the Fastmode, or the FastMC
    steering_params.readCompact = False # We are specifying that we do not want to use the FastMC.
    t1                          = time.time()
    golemfit                    = gf.GolemFit(datapaths,steering_params,npp)
    t2                          = time.time()
    print('Normal MC consumption: '+getMem())
        

#null_dist = golemfit.SpitExpectation(fitparams)
#print('sahpe of null:')
#print(np.shape(null_dist))

# This generates a bunch of realizations used for the Brazil Bands. It spits out fake data toy MC.
if gen_realizations == 'True':
    from random import shuffle
    if inject_fit == 'True':
        realization_loc = realization_loc.replace('Realizations','Realizations_Injected')
        print(realization_loc)
        mkdir(realization_loc)

    else:
        print(realization_loc)
        mkdir(realization_loc)

    realization_seeds = list(range(2000))#2001) # This is the seeds used for the toy mc. The length of this is how many realizations are generated.
    #realization_seeds = [1099]
    shuffle(realization_seeds) # Shuffle them so that you can run multiple instances of this. 
    for seed in realization_seeds:
        print('Setting up Null:'+str(seed))
        real_outfile  = realization_loc+'/Realization_'+str(seed)+'.npz' # The name of the toy MC output
        if not os.path.isfile(real_outfile):
            print('Making realization: '+real_outfile)
            realization = golemfit.SpitRealization(fitparams,seed)
            real_energies = []
            for i in range(len(realization)):
                if realization[i][0]>float(Emin) and realization[i][0]<float(Emax):
                    real_energies.append(1)
            np.savez(real_outfile, realization = realization)
    print('Finished generating the realizations...')
    sys.exit()



print('Using realization: '+realization_file)

# this is the distribution of events for the realization. 
#try:
realization_dist = np.load(realization_file)['realization']

#except:
#    realization_dist = np.load(realization_file)['null_dist']

print('Shape of realization')
print(np.shape(realization_dist))
golemfit.Swallow(realization_dist)  # Swallow the realization (you want to use this in the minimzation)

realization         = golemfit.GetDataDistribution()[0][0][0]   # Get the expected distribution prior to minization.
realization_sum     = np.sum(realization)                                                                                                                                                                    

realization_events = converter(np.asarray(golemfit.SpitData())) 
print('Realization Sum: '+str(sum(realization_sum))) 

energy_bin_edges 	= np.log10(golemfit.GetEnergyBinsMC()[:])
zenith_bin_edges 	= np.asarray(golemfit.GetZenithBinsMC()[:])
energy_bin_centers 	= np.asarray(energy_bin_edges[:-1] + np.diff(energy_bin_edges)/2.)
zenith_bin_centers 	= np.asarray(zenith_bin_edges[:-1] + np.diff(zenith_bin_edges)/2.)

# These turn on and off the systematics that you want to use. False means you want to use it.
fitparams_flag                          = gf.FitParametersFlag(True)
fitparams_flag.domEfficiency    		= not use_domeff
fitparams_flag.holeiceForward    		= not use_holeice
fitparams_flag.convNorm         		= not use_norm
fitparams_flag.CRDeltaGamma     		= not use_cr
fitparams_flag.piKRatio         		= not use_pkr
fitparams_flag.NeutrinoAntineutrinoRatio   	= not use_nnbr
fitparams_flag.zenithCorrection   	 	    = not use_atm
fitparams_flag.hqdomEfficiency              = not use_hqe
fitparams_flag.barrHM                  		= not use_barrHM
fitparams_flag.barrHP                  		= not use_barrHP
fitparams_flag.barrWM                  		= not use_barrWM
fitparams_flag.barrWP                  		= not use_barrWP
fitparams_flag.barrYM                 		= not use_barrYM
fitparams_flag.barrYP                 		= not use_barrYP
fitparams_flag.barrZM                		= not use_barrZM
fitparams_flag.barrZP               		= not use_barrZP
fitparams_flag.icegrad0                     = not use_icegrad0
fitparams_flag.icegrad1                     = not use_icegrad1
fitparams_flag.promptNorm                   = True#not use_promptNorm
fitparams_flag.astroNorm                    = not use_astroNorm
fitparams_flag.astroDeltaGamma              = not use_astroDeltaGamma
fitparams_flag.nuxs                         = not use_nuxs
fitparams_flag.nubarxs                      = not use_nubarxs
fitparams_flag.kaonLosses                   = not use_kaonLosses
golemfit.SetFitParametersFlag(fitparams_flag)

# You can set custom priors here. 
priors 					= gf.Priors(gf.sampleTag.Sterile)
priors.convNormCenter           = ConvNormCenter
priors.convNormWidth            = ConvNormWidth
priors.astro1Comp2DNormCenter   = AstroNormCenter
priors.astro1Comp2DNormWidth    = AstroNormWidth
priors.promptNormCenter         = PromptNormCenter

priors.crSlopeWidth     = 0.03
priors.domEffWidth      = 0.123
#priors.icegrad1Width = 2.0
#priors.convNormWidth  = 0.4
#priors.nubarXSCenter                        = 1.
#priors.nuXSCenter                           = 1.

priors.nubarXSCenter                        = 1
priors.nubarXSWidth                         = 0.075
priors.nuXSCenter                           = 1
priors.nuXSWidth                            = 0.03


if inject_fit == 'True':
    priors.domEffCenter           = inject_dict['DOMeff']
    priors.holeiceForwardCenter   = inject_dict['HoleIce']
    priors.convNormCenter         = inject_dict['Normalization']
    priors.crSlopeCenter          = inject_dict['CR']
    priors.zenithCorrectionCenter = inject_dict['ZenithCorrection']
    priors.barrZMCenter           = inject_dict['barrZM']
    priors.barrZPCenter           = inject_dict['barrZP']
    priors.barrYMCenter           = inject_dict['barrYM']
    priors.barrYPCenter           = inject_dict['barrYP']
    priors.barrWMCenter           = inject_dict['barrWM']
    priors.barrWPCenter           = inject_dict['barrWP']
    priors.icegrad0Center         = inject_dict['icegrad0']
    priors.icegrad1Center         = inject_dict['icegrad1']
    priors.nuXSCenter                   = inject_dict['nuxs']
    priors.nubarXSCenter                = inject_dict['nubarxs']
    priors.kaonLossesCenter             = inject_dict['kaonLosses']
    priors.astro1Comp2DNormCenter       = inject_dict['astroNorm']
    priors.astro1Comp2DDeltaGammaCenter = inject_dict['astroDeltaGamma']


golemfit.SetFitParametersPriors(priors)

expectation         = golemfit.GetExpectation(fitparams)[0][0][0]
expectation_events  = converter(golemfit.SpitExpectation(fitparams))
print('Shape of expecation')
print(np.shape(expectation_events.MuExEnergy))
print('Expectation: '+str(sum(expectation)))
# print(np.array2string(expectation, separator = ', '))
if options.make_asimov:
    print("Saving Asimov dataset Asimov.npz")
    np.savez("Asimov.npz", realization=golemfit.SpitExpectation(fitparams))
    sys.exit()

if spit_weights == 'True':
    golemfit.SpitWeightedMonteCarloToHDF5(fitparams,"/data/user/saxani/test.h5")

def get_seed(center,width,scale,low,high):
    seed_value = np.random.normal(center,width/scale)
    if seed_value < low:
        seed_value = low
    if seed_value > high:
        seed_value = high
    return seed_value

# We can minimize several times to ensure that we find the global minima rather than the local minima.

seed_list       = []

if n_seeds == -1:
    seed_fitparams                              = gf.FitParameters(gf.sampleTag.Sterile)
    CV_dict = get_CV()
    seed_fitparams.convNorm  = CV_dict['Normalization']
    seed_fitparams.CRDeltaGamma = CV_dict['CR']
    seed_fitparams.domEfficiency = CV_dict['DOMeff'] 
    seed_fitparams.holeiceForward = CV_dict['HoleIce'] 
    seed_fitparams.zenithCorrection = CV_dict['ZenithCorrection']
    seed_fitparams.barrWM  = CV_dict['barrWM']
    seed_fitparams.barrWP = CV_dict['barrWP']
    seed_fitparams.barrYM = CV_dict['barrYM']
    seed_fitparams.barrYP = CV_dict['barrYP']
    seed_fitparams.barrZM = CV_dict['barrZM']
    seed_fitparams.barrZP = CV_dict['barrZP']
    seed_fitparams.icegrad0 =CV_dict['icegrad0']
    seed_fitparams.icegrad1 = CV_dict['icegrad1']
    seed_fitparams.astroNorm = CV_dict['astroNorm']
    seed_fitparams.astroDeltaGamma = CV_dict['astroDeltaGamma']
    seed_fitparams.nuxs = CV_dict['nuxs']
    seed_fitparams.nubarxs = CV_dict['nubarxs'] 
    seed_fitparams.kaonLosses = CV_dict['kaonLosses']
    seed_list.append(seed_fitparams) 

else:
    for i in range(n_seeds):
        seed_fitparams                              = gf.FitParameters(gf.sampleTag.Sterile)
        if use_norm:
            seed_fitparams.convNorm                 = get_seed(ConvNormCenter, ConvNormWidth/10., 2.,0.9*ConvNormCenter,1.1*ConvNormCenter)
        else:
            seed_fitparams.convNorm  = inject_dict['Normalization']

        if use_cr:
            seed_fitparams.CRDeltaGamma            	= get_seed(priors.crSlopeCenter, priors.crSlopeWidth, 2,-0.02,0.02)
        else:
            seed_fitparams.CRDeltaGamma = inject_dict['CR']

        if use_domeff:
            seed_fitparams.domEfficiency			= get_seed(1.27, 0.01, 2., 1.255, 1.285)
        else:
            seed_fitparams.domEfficiency = inject_dict['DOMeff']

        if use_holeice:
            seed_fitparams.holeiceForward			= get_seed(-1, 1, 2.,-3.,1.,)
        else:
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa')
            print(inject_dict['HoleIce'])
            seed_fitparams.holeiceForward = inject_dict['HoleIce']

        if use_atm:
            seed_fitparams.zenithCorrection	 		= get_seed(priors.zenithCorrectionCenter,priors.zenithCorrectionWidth, 2., -1.5,1.5)
        else:
            seed_fitparams.zenithCorrection = inject_dict['ZenithCorrection']

        if use_barrHM:
            seed_fitparams.barrHM                   = get_seed(priors.barrHMCenter ,priors.barrHMWidth, 5.,-0.5,0.5)
        else:
            seed_fitparams.barrHM  = inject_dict['barrHM']

        if use_barrHP:
            seed_fitparams.barrHP                   = get_seed(priors.barrHPCenter ,priors.barrHPWidth, 5.,-0.5,0.5)
        else:
            seed_fitparams.barrHP  = inject_dict['barrHP']

        if use_barrWM:
            seed_fitparams.barrWM                   = get_seed(priors.barrWMCenter ,priors.barrWMWidth, 5.,-0.5,0.5)
        else:
            seed_fitparams.barrWM  = inject_dict['barrWM']

        if use_barrWP:
            seed_fitparams.barrWP                   = get_seed(priors.barrWPCenter ,priors.barrWPWidth, 5.,-0.5,0.5)
        else:
            seed_fitparams.barrWP = inject_dict['barrWP']
        if use_barrYM:
            seed_fitparams.barrYM                   = get_seed(priors.barrYMCenter ,priors.barrYMWidth, 5.,-0.5,0.5)
        else:
            seed_fitparams.barrYM = inject_dict['barrYM']

        if use_barrYP:
            seed_fitparams.barrYP                   = get_seed(priors.barrYPCenter ,priors.barrYPWidth, 5.,-0.5,0.5)
        else:
            seed_fitparams.barrYP = inject_dict['barrYP']

        if use_barrZM:      
            seed_fitparams.barrZM                   = get_seed(priors.barrZMCenter ,priors.barrZMWidth, 5.,-0.25,0.5)
        else:
            seed_fitparams.barrZM = inject_dict['barrZM']

        if use_barrZP:
            seed_fitparams.barrZP                   = get_seed(priors.barrZPCenter ,priors.barrZPWidth, 5.,-0.2,0.5)
        else:
            seed_fitparams.barrZP = inject_dict['barrZP']

        if use_icegrad0:
            seed_fitparams.icegrad0                 = 0.01
        else:
            seed_fitparams.icegrad0 =inject_dict['icegrad0']


        if use_icegrad1:
            seed_fitparams.icegrad1                 = 0.01
        else:
            seed_fitparams.icegrad1 = inject_dict['icegrad1']

        if use_promptNorm:
            seed_fitparams.promptNorm               = PromptNormCenter
        else:
            seed_fitparams.promptNorm               = 1.0
        if use_astroNorm:
            seed_fitparams.astroNorm                = 4.72/6
            if AstroNormCenter != '':
                seed_fitparams.astroNorm             = get_seed(AstroNormCenter, AstroNormWidth/10., 2.,0.9*AstroNormCenter,1.1*AstroNormCenter)
        else:
            seed_fitparams.astroNorm = inject_dict['astroNorm']

        if use_astroDeltaGamma:
            seed_fitparams.astroDeltaGamma          = get_seed(0. ,0.36, 2.,-1,1)
        else:
            seed_fitparams.astroDeltaGamma = inject_dict['astroDeltaGamma']
        if use_nuxs:
            seed_fitparams.nuxs                         = get_seed(1. ,0.03, 2.,0.5,1.5)
        else:
            seed_fitparams.nuxs = inject_dict['nuxs']
        if use_nubarxs:
            seed_fitparams.nubarxs                      = get_seed(1. ,0.075, 2.,0.5,1.5)
        else:
            seed_fitparams.nubarxs = inject_dict['nubarxs']
        if use_kaonLosses:
            seed_fitparams.kaonLosses                   = get_seed(0 ,1., 2.,-5,5)
        else:
            seed_fitparams.kaonLosses = inject_dict['kaonLosses']

        seed_list.append(seed_fitparams) 

golemfit.SetFitParametersSeed(seed_list)

# Finally, this minizes with respect to the swallowd data-- either toy MC or data.
print('LLH at fitparams: ' + str(golemfit.EvalLLH(fitparams)))
print('Starting minimization...')
t3 = time.time()
min_llh = golemfit.MinLLH()
t4 = time.time()
print('Minimization complete...')


# You are done. The following are the values after minimization.
llh         = min_llh.likelihood
norm        = min_llh.params.convNorm
gamma       = min_llh.params.CRDeltaGamma
pkr         = min_llh.params.piKRatio
nnbr        = min_llh.params.NeutrinoAntineutrinoRatio
domeff      = min_llh.params.domEfficiency
hi    	    = min_llh.params.holeiceForward
atm 		= min_llh.params.zenithCorrection
hqe         = min_llh.params.hqdomEfficiency
barrHM     	= min_llh.params.barrHM
barrHP     	= min_llh.params.barrHP
barrWM    	= min_llh.params.barrWM
barrWP    	= min_llh.params.barrWP
barrYM    	= min_llh.params.barrYM
barrYP    	= min_llh.params.barrYP
barrZM    	= min_llh.params.barrZM
barrZP    	= min_llh.params.barrZP
icegrad0    = min_llh.params.icegrad0
icegrad1    = min_llh.params.icegrad1
promptNorm          = min_llh.params.promptNorm
astroNorm           = min_llh.params.astroNorm
astroDeltaGamma     = min_llh.params.astroDeltaGamma
nuxs            = min_llh.params.nuxs
nubarxs         = min_llh.params.nubarxs
kaonLosses = min_llh.params.kaonLosses

print('LLH:           '+str(llh))
print('Normalization: '+str(norm))
print('CR Slope:      '+str(gamma))
print('Pi/K:          '+str(pkr))
print('nnbr:          '+str(nnbr))
print('DOMeff:        '+str(domeff))
print('HoleIce:       '+str(hi))
print('ZenithCorrection: '+str(atm))
print('HQE:           '+str(hqe))
print('barrHM:        '+str(barrHM))
print('barrHP:        '+str(barrHP))
print('barrWM:        '+str(barrWM))
print('barrWP:        '+str(barrWP))
print('barrYM:        '+str(barrYM))
print('barrYP:        '+str(barrYP))
print('barrZM:        '+str(barrZM))
print('barrZP:        '+str(barrZP))
print('IceGrad0:      '+str(icegrad0))
print('IceGrad1:      '+str(icegrad1))
print('PromptNorm:    '+str(promptNorm))
print('astroNorm:     '+str(astroNorm))
print('astroDeltaGamma: '+str(astroDeltaGamma))
print('nuxs;          '+str(nuxs))
print('nubarxs;       '+str(nubarxs))
print('kaonLosses:    '+str(kaonLosses))
print('LoadingTime:   '+str(t2-t1))
print('MinTime:       '+str(t4-t3))

fit 	    = golemfit.GetExpectation(min_llh.params)[0][0][0]
fit_sum     = sum(fit)
fit_events  = converter(golemfit.SpitExpectation(min_llh.params))

print('Fit Sum: '+str(fit_sum))
t_end = time.time()

# Let's make some outfiles. Here's the JSON file:
outfile_distributions = {}
outfile_distributions['Expectation']        = np.ndarray.tolist(expectation)
outfile_distributions['Fit']                = np.ndarray.tolist(fit)
outfile_distributions['Realization']        = np.ndarray.tolist(realization)
outfile_distributions['Signal']             = realization_file.split('/')[-1]
outfile_distributions['Realization_file']             = realization_file
outfile_distributions['LLH']         		= llh
outfile_distributions['Point']         		= point
outfile_distributions['Normalization']   	= norm
outfile_distributions['CR']       		    = gamma
outfile_distributions['pkr']         		= pkr
outfile_distributions['nnbr']        		= nnbr
outfile_distributions['DOMeff']      		= domeff
outfile_distributions['HoleIce']         	= hi
outfile_distributions['ZenithCorrection']   = atm
outfile_distributions['HQE']                = hqe
outfile_distributions['dm2']         		= dm2
outfile_distributions['s2t']        		= s2t
outfile_distributions['n_seeds']            = n_seeds
outfile_distributions['barrHM']         = barrHM
outfile_distributions['barrHP']         = barrHP
outfile_distributions['barrWM']         = barrWM
outfile_distributions['barrWP']         = barrWP
outfile_distributions['barrYM']         = barrYM
outfile_distributions['barrYP']         = barrYP
outfile_distributions['barrZM']         = barrZM
outfile_distributions['barrZP']         = barrZP
outfile_distributions['icegrad0']       = icegrad0
outfile_distributions['icegrad1']       = icegrad1
outfile_distributions['promptNorm']     = promptNorm
outfile_distributions['astroNorm']      = astroNorm
outfile_distributions['astroDeltaGamma'] = astroDeltaGamma
outfile_distributions['nuxs']           = nuxs
outfile_distributions['nubarxs']        = nubarxs
outfile_distributions['kaonLosses']        = kaonLosses

outfile_distributions['Emin'] 			= Emin
outfile_distributions['Emax'] 			= Emax
outfile_distributions['Ebin'] 			= Ebin
outfile_distributions['Zmax'] 			= Zmax
outfile_distributions['Zbin'] 			= Zbin
outfile_distributions['Systematics'] 	= systematics
outfile_distributions['Barr'] 	        = barr
outfile_distributions['Simulation']     = sim
outfile_distributions['years'] 			= years
outfile_distributions['flux location'] 	= fluxdir
outfile_distributions['fast mode'] 		= fast
outfile_distributions['E_Edges'] 	    = np.ndarray.tolist(energy_bin_edges)
outfile_distributions['Z_Edges'] 	    = np.ndarray.tolist(zenith_bin_edges)
outfile_distributions['E_centers'] 	    = np.ndarray.tolist(energy_bin_centers)
outfile_distributions['Z_centers'] 	    = np.ndarray.tolist(zenith_bin_centers)
outfile_distributions['LoadingTime']    = t2-t1
outfile_distributions['MinTime']        = t4-t3
outfile_distributions['TotalTime']      = t_end - t_start
outfile_distributions['FastMode']       = fast
outfile_distributions['FastModeScaling'] = fast_scaling
outfile_distributions['th34']           = th34
outfile_distributions['th24']           = th24
outfile_distributions['Uu4sq']          = Uu4sq
outfile_distributions['Ut4sq']          = Ut4sq
'''
outfile_distributions['SeedNorm']       =  seed_fitparams.convNorm
outfile_distributions['SeedPKR']        = seed_fitparams.piKRatio
outfile_distributions['SeedCR']         = seed_fitparams.CRDeltaGamma
outfile_distributions['SeedNNBR'] = seed_fitparams.NeutrinoAntineutrinoRatio
outfile_distributions['SeedDE'] = seed_fitparams.domEfficiency
outfile_distributions['SeedHI'] = seed_fitparams.holeiceForward
outfile_distributions['SeedATM'] = seed_fitparams.zenithCorrection
outfile_distributions['SeedHQE'] = seed_fitparams.hqdomEfficiency
outfile_distributions['SeedHM'] = seed_fitparams.barrHM
outfile_distributions['SeedHP'] = seed_fitparams.barrHP
outfile_distributions['SeedWM'] = seed_fitparams.barrWM
outfile_distributions['SeedWP'] = seed_fitparams.barrWP
outfile_distributions['SeedYM'] = seed_fitparams.barrYM
outfile_distributions['SeedYP'] = seed_fitparams.barrYP
outfile_distributions['SeedZM'] = seed_fitparams.barrZM
outfile_distributions['SeedZP'] = seed_fitparams.barrZP
'''
#outfile_distributions['Signal_point'] = signal_point

outfile_distributions['pullNorm']       = (norm - priors.convNormCenter)/priors.convNormWidth
outfile_distributions['pullPKR']        = (pkr - priors.piKRatioCenter)/priors.piKRatioWidth
outfile_distributions['pullCR']         = (gamma - priors.crSlopeCenter)/priors.crSlopeWidth
outfile_distributions['pullNNBR']       = (nnbr - priors.nuNubarRatioCenter)/priors.nuNubarRatioWidth
outfile_distributions['pullDE']         = (domeff - priors.domEffCenter)/priors.domEffWidth
outfile_distributions['pullHI']         = (hi - priors.holeiceForwardCenter)/priors.holeiceForwardWidth
outfile_distributions['pullATM']        = (atm - priors.zenithCorrectionCenter)/priors.zenithCorrectionWidth
outfile_distributions['pullHQE']        = (hqe - priors.hqdomEffCenter)/priors.hqdomEffWidth
outfile_distributions['pullHM']         = (barrHM - priors.barrHMCenter)/priors.barrHMWidth
outfile_distributions['pullHP']         = (barrHP - priors.barrHPCenter)/priors.barrHPWidth
outfile_distributions['pullWM']         = (barrWM - priors.barrWMCenter)/priors.barrWMWidth
outfile_distributions['pullWP']         = (barrWP - priors.barrWPCenter)/priors.barrWPWidth
outfile_distributions['pullYM']         = (barrYM - priors.barrYMCenter)/priors.barrYMWidth
outfile_distributions['pullYP']         = (barrYP - priors.barrYPCenter)/priors.barrYPWidth
outfile_distributions['pullZM']         = (barrZM - priors.barrZMCenter)/priors.barrZMWidth
outfile_distributions['pullZP']         = (barrZP - priors.barrZPCenter)/priors.barrZPWidth
outfile_distributions['pullI0']         = (icegrad0 - priors.icegrad0Center)/priors.icegrad0Width
outfile_distributions['pullI1']         = (icegrad1 - priors.icegrad1Center)/priors.icegrad1Width
outfile_distributions['pullAstroNorm']  = (astroNorm - priors.astro1Comp2DNormCenter)/priors.astro1Comp2DNormWidth
outfile_distributions['pullAstroDeltaGamma'] = (astroDeltaGamma - priors.astro1Comp2DDeltaGammaCenter)/priors.astro1Comp2DDeltaGammaWidth
outfile_distributions['pullnuxs']       = (nuxs - priors.nuXSCenter)/priors.nuXSWidth
outfile_distributions['pullnubarxs']    = (nubarxs - priors.nubarXSCenter)/priors.nubarXSWidth
outfile_distributions['pullkaonLosses'] = (kaonLosses - priors.kaonLossesCenter)/priors.kaonLossesWidth



with open(outfile_json, 'w') as f:
        json.dump(outfile_distributions, f, indent=10,sort_keys=True)

# Let's save a condensed .txt file as well.
txt_outfile = []
txt_label = []
txt_outfile.append(point)
txt_label.append('Point')
txt_outfile.append(realization_file.split('/')[-1])
txt_label.append('Signal')
txt_outfile.append(llh)
txt_label.append('LLH')
txt_outfile.append(domeff)
txt_label.append('DE')
txt_outfile.append(hi)
txt_label.append('HI')
txt_outfile.append(pkr)
txt_label.append('PKR')
txt_outfile.append(nnbr)
txt_label.append('NNBR')
txt_outfile.append(norm)
txt_label.append('Norm')
txt_outfile.append(gamma)
txt_label.append('Gamma')
txt_outfile.append(atm)
txt_label.append('ATM')
txt_outfile.append(hqe)
txt_label.append('HQE')
txt_outfile.append(barrHM)
txt_label.append('HM')
txt_outfile.append(barrHP)
txt_label.append('HP')
txt_outfile.append(barrWM)
txt_label.append('WM')
txt_outfile.append(barrWP)
txt_label.append('WP')
txt_outfile.append(barrYM)
txt_label.append('YM')
txt_outfile.append(barrYP)
txt_label.append('YP')
txt_outfile.append(barrZM)
txt_label.append('ZM')
txt_outfile.append(barrZP)
txt_label.append('ZP')
txt_outfile.append(icegrad0)
txt_label.append('I0')
txt_outfile.append(icegrad1)
txt_label.append('I1')
txt_outfile.append(promptNorm)
txt_label.append('Prompt')
txt_outfile.append(astroNorm)
txt_label.append('AstroNorm')
txt_outfile.append(astroDeltaGamma)
txt_label.append('AstroDeltaGamma')
txt_outfile.append(nuxs)
txt_label.append('nuxs')
txt_outfile.append(nubarxs)
txt_label.append('nubarxs')
txt_outfile.append(kaonLosses)
txt_label.append('kaonLosses')
txt_outfile.append(t2-t1)
txt_label.append('LTime')
txt_outfile.append(t4-t3)
txt_label.append('MTime')
txt_outfile.append(sim)
txt_label.append('Sim')
txt_outfile.append(systematics)
txt_label.append('Sys')
txt_outfile.append(barr)
txt_label.append('Barr')
txt_outfile.append(multisim)
txt_label.append('MS')
txt_outfile.append(th34)
txt_label.append('th34')

header_string = ''
for i in range(len(txt_label)):
    if i < len(txt_label)-1:
        header_string += txt_label[i] + ' '
    else:
        header_string += txt_label[i]
print(header_string)

'''
f = open(outfile_txt, "w")
f.write(header_string+'\n')
for i in range(len(txt_outfile)):
    f.write(str(txt_outfile[i]))
    if i < len(txt_outfile)-1:
        f.write(' ')
    else:
        f.write('\n')
f.close()
'''

# Copy the file back to NPX if you were running on the OSG.
if osg == 'True' and bayes == 'False':
    #copy_to_NPX(outfile_txt_NPX)
    copy_to_NPX(outfile_NPX)

print('Realization:  '   +realization_file)
print('Outfile JSON: '       +outfile_json)
#print('Outfile txt:  '   +outfile_txt)

t3 = time.time()
print('Processing time [m]: '+str((t3-t1)/60.))

# This calculates the Bayes factor.

if bayes == 'True':
    #import tqdm
    import pymultinest
    from pymultinest.solve import solve
    from pymultinest.watch import ProgressPrinter

    t3 = time.time()
    print('Calculting Bayes...')

    verbose = True

    parameters = [r"Normalization",
                   r"CR",
                   r"zenithCorrection",
                   r"WP",
                   r"WM",
                   r"YP",
                   r"YM",
                   r"ZP",
                   r"ZM",
                   r"DOMefficiency",
                   r"HoleIce",
                   r"IceGrad0",
                   r"IceGrad1",
                   "astroNorm",
                   "astroDeltaGamma",
                   "nuxs",
                   "nubarxs",
                   "kaonLosses"]


    p0_low =  [0.1,-0.25,-3.0,-0.5,-0.5,-0.5,-0.5,-0.1,-0.2,1.23,-5.0,-3.,-3.,0,-1,0.5,0.5,-5]
    p0_high = [2.0, 0.25, 3.0, 0.5, 0.5, 0.5, 0.5, 0.4, 0.4,1.35, 2.0, 3., 3.,2, 1,1.5,1.5,5]

    n_params = len(parameters)
    assert(len(p0_low) == n_params)
    assert(len(p0_high) == n_params)

    parameters_prior_ranges = []
    for i in range(n_params):
        parameters_prior_ranges.append(p0_low[i])
        parameters_prior_ranges.append(p0_high[i])

    theta = np.zeros(n_params)
    prange = np.zeros(n_params)

    def GetLikelihood(convNorm, CRDeltaGamma,
                      zenithCorrection, barrWP, barrWM, barrYP, barrYM, barrZP, barrZM,
                      domEfficiency, holeiceForward, icegrad0, icegrad1,astroNorm,astroDeltaGamma,nuxs,nubarxs,kaonLosses):
        fitparams = gf.FitParameters(gf.sampleTag.Sterile)
        fitparams.convNorm = convNorm
        fitparams.CRDeltaGamma = CRDeltaGamma
        fitparams.domEfficiency = domEfficiency
        fitparams.zenithCorrection = zenithCorrection
        fitparams.barrWP = barrWP
        fitparams.barrWM = barrWM
        fitparams.barrYP = barrYP
        fitparams.barrYM = barrYM
        fitparams.barrZP = barrZP
        fitparams.barrZM = barrZM
        fitparams.holeiceForward = holeiceForward
        fitparams.icegrad0 = icegrad0
        fitparams.icegrad1 = icegrad1
        fitparams.promptNorm = promptNorm
        fitparams.astroNorm = astroNorm
        fitparams.astroDeltaGamma = astroDeltaGamma
        fitparams.nuxs              = nuxs
        fitparams.nubarxs           = nubarxs
        fitparams.kaonLosses           = kaonLosses
        likelihood = golemfit.EvalLLH(fitparams)
        return -likelihood

    def lnProb(cube, ndim, nparams):
        for i in range(ndim):
            #    prange[i] = parameters_prior_ranges[2*i+1] - parameters_prior_ranges[2*i]
            #    theta[i] = prange[i]*cube[i] + parameters_prior_ranges[2*i]
            theta[i] = cube[i]
        #print theta
        return GetLikelihood(*theta)
        #return GetLikelihood(*cube)

    def CubePrior(cube, ndim, nparams):
        for i in range(ndim):
            prange[i] = parameters_prior_ranges[2*i+1] - parameters_prior_ranges[2*i]
            cube[i] = prange[i]*cube[i] + parameters_prior_ranges[2*i]
        # default are uniform priors
        return ;

    ## Multinest business

    #prefix = "./sterile_evidence"
    prefix = outfile_json.replace('json','')
    print("begin running evidence calculation")
    #evidence_tolerance = 0.005
    #evidence_tolerance = 0.1
    evidence_tolerance = 0.5
    #n_live_points = 2000
    n_live_points = 300

    #result = pymultinest.run(LogLikelihood=lnProb, Prior=CubePrior, n_dims=n_params,
    #                           outputfiles_basename=prefix, verbose=verbose, n_live_points = n_live_points,
    #                           evidence_tolerance=evidence_tolerance, sampling_efficiency=0.3)
    result = pymultinest.run(LogLikelihood=lnProb, Prior=CubePrior, n_dims=n_params,
                               outputfiles_basename=prefix, verbose=verbose, n_live_points = n_live_points,
                               evidence_tolerance=evidence_tolerance, sampling_efficiency=0.5)
    print("end running evidence calculation")
    print("begin analysis")
    analyzer = pymultinest.Analyzer(outputfiles_basename=prefix, n_params=n_params)
    a_lnZ = analyzer.get_stats()['global evidence']
    print("end analysis")

    if False:
        output_location = './'
        np.savez('evidence_'+prefix+'.npy',a_lnZ=a_lnZ)

    print("Evidence ", a_lnZ)

    print("End analysis...")
    t4 = time.time()
    outfile_distributions['BayesEvidence'] = a_lnZ
    outfile_distributions['BayesCalcTime'] = str(t4-t3)
    outfile_distributions['evidence_tolerance'] = evidence_tolerance
    outfile_distributions['n_live_points'] = n_live_points

    with open(outfile_json, 'w') as f:
        json.dump(outfile_distributions, f, indent=10,sort_keys=True)

    if osg == 'True':
        import glob
        filenames = glob.glob(prefix+"*")
        print(filenames)
        for f in filenames:
            out = outdir_NPX + f.split('/')[-1]
            print(out)
            copy_to_NPX(out)
