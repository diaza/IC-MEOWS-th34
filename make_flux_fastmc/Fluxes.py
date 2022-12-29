#!/usr/bin/env python 

import numpy as np
import glob
from os.path import expandvars
import subprocess
import os
import sys
from optparse import OptionParser

usage = "usage: %prog [options] inputfile"
parser = OptionParser(usage)

#parser.add_option("--indir",type="string",default = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/scripts/jobs/Resources/Flux_resources/')
parser.add_option("--indir",type="string",default = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/code/GolemFit/resources/FluxOscCalculator/')
parser.add_option("--outdir",type="string",default = '/data/user/adiaz/test_fluxes/')
parser.add_option("--conv_flux",type="string",default = 'AIRS_mceq121_conv_flux_2011_sib_HG_E3.dat')
parser.add_option("--prompt_flux",type="string",default = 'AIRS_mceq121_pr_flux_2011_sib_HG_E3.dat')
parser.add_option("--th24",type="string",default = '0.0')
parser.add_option("--index",type="string",default = '0')
parser.add_option("--dmsq41",type="string",default = '0')
parser.add_option("--th14",type="string",default = '0.0')
parser.add_option("--th34",type="string",default = '0.0')
parser.add_option("--del14",type="string",default = '0.0')
parser.add_option("--del24",type="string",default = '0.0')
parser.add_option("--osg",type="string",default = 'False')

(options,args) = parser.parse_args()

indir   = options.indir
outdir  = options.outdir
index 	= options.index
conv_flux    = options.conv_flux
prompt_flux    = options.prompt_flux
dmsq41  = options.dmsq41
th24    = options.th24
th14 	= options.th14
th34 	= options.th34
del14	= options.del14
del24 	= options.del24
osg     = options.osg

dmsq41_str  = str(format(float(dmsq41), '.6f'))
th14_str    = str(format(float(th14), '.6f'))
th24_str    = str(format(float(th24), '.6f'))
th34_str    = str(format(float(th34), '.6f'))
del14_str   = str(format(float(del14), '.6f'))
del24_str   = str(format(float(del24), '.6f'))

if osg == 'True':
    raise RuntimeError("Haven't made file compatible with OSG.")
    def copy_to_OSG(NPX_file):
        subprocess.check_call(['globus-url-copy','-nodcau','-rst', NPX_file,"file:"+os.getcwd()+'/'+str(NPX_file.split('/')[-1])])
    def copy_to_NPX(NPX_file):
        subprocess.check_call(['globus-url-copy','-nodcau','-rst',"file:"+os.getcwd()+'/'+str(NPX_file.split('/')[-1]), NPX_file])

    NPX_dir = 'gsiftp://gridftp.icecube.wisc.edu'+indir
    infiles = [NPX_dir+'/deriv_WM.dat', 
                NPX_dir+'/deriv_WP.dat', 
                NPX_dir+'/deriv_YM.dat', 
                NPX_dir+'/deriv_YP.dat', 
                NPX_dir+'/deriv_ZM.dat', 
                NPX_dir+'/deriv_ZP.dat', 
                NPX_dir+'/'+flux, 
                NPX_dir+'/EARTH_MODEL_PREM.dat', 
                NPX_dir+'/prompt_atmospheric_flux_calculator_with_interactions_from_nuflux',
                NPX_dir+'/conventional_atmospheric_flux_calculator_with_interactions_from_file',
                NPX_dir+'/astrophysical_neutrino_flux_calculator_with_interactions',
                NPX_dir+'/conventional_atmospheric_flux_calculator_with_interactions_from_file_barr']


    for infile in infiles:
        copy_to_OSG(infile) 
        osg_file = os.getcwd()+'/'+str(infile.split('/')[-1])
        os.chmod(osg_file, 0o777)

    indir = os.getcwd()+'/'
    outdir_NPX = 'gsiftp://gridftp.icecube.wisc.edu'+outdir
    outdir = os.getcwd()+'/'

if not os.path.exists(outdir):
    os.mkdir(outdir)
    #os.chmod(outdir, 0777)

if dmsq41 == '0.000000':
    print('generating null')
    th24 = str(0.0)


print(' --- Calculating prompt atmospheric flux ---')
check_file = outdir + '/prompt_atmospheric_0_'+dmsq41_str+'_'+th14_str+'_'+th24_str+'_'+th34_str+'_'+del14_str+'_'+del24_str+'.hdf5'
if not os.path.isfile(check_file):
    options = ' ' + indir + ' ' + outdir+' '+ prompt_flux +  ' '+str(index)+' ' + str(dmsq41)+' '+str(th14)+' '+str(th24)+' '+str(th34)+' '+str(del14)+' '+str(del24)
    call_function = indir+ "/prompt_atmospheric_flux_calculator_with_interactions_from_file " + options
    print(call_function)
    subprocess.call(call_function, shell=True)
else:
    print('Output prompt atmospheric file exists: '+check_file)
    print('   ... skipping calculation')

if osg == 'True':
        #filepath_NPX = outdir_NPX + '/atmospheric_0_'+str(format(float(dmsq41), '.6f'))+'_'+str(format(float(th14), '.6f'))+'_'+str(format(float(th24), '.6f'))+'_'+str(format(float(th34), '.6f'))+'_'+str(format(float(del14), '.6f'))+'_'+str(format(float(del24), '.6f'))+'.hdf5'
        filepath_NPX = outdir_NPX + '/prompt_atmospheric_0_'+dmsq41_str+'_'+th14_str+'_'+th24_str+'_'+th34_str+'_'+del14_str+'_'+del24_str+'.hdf5'
        if not os.path.isfile(indir+ '/'+filepath_NPX.split('/')[-1]):
            print('Cannot find this file in current dir: '+ filepath_NPX.split('/')[-1])
            print('The following files are visible: ')
            import glob
            files = glob.glob(indir+'*')
            for file in files:
                print(files)
        copy_to_NPX(filepath_NPX)

print(' --- Calculating conventional atmospheric flux ---')
check_file = outdir + '/atmospheric_0_'+dmsq41_str+'_'+th14_str+'_'+th24_str+'_'+th34_str+'_'+del14_str+'_'+del24_str+'.hdf5'
if not os.path.isfile(check_file):
    options = ' ' + indir +' '+outdir+' '+ conv_flux +  ' '+str(index)+' ' + str(dmsq41)+' '+str(th14)+' '+str(th24)+' '+str(th34)+' '+str(del14)+' '+str(del24)
    call_function = indir+ "/conventional_atmospheric_flux_calculator_with_interactions_from_file " + options
    print(call_function)
    subprocess.call(call_function, shell=True)
else:
    print('Output conventional atmospheric file exists: '+check_file)
    print('   ... skipping calculation')

if osg == 'True':
        #filepath_NPX = outdir_NPX + '/atmospheric_0_'+str(format(float(dmsq41), '.6f'))+'_'+str(format(float(th14), '.6f'))+'_'+str(format(float(th24), '.6f'))+'_'+str(format(float(th34), '.6f'))+'_'+str(format(float(del14), '.6f'))+'_'+str(format(float(del24), '.6f'))+'.hdf5'
        filepath_NPX = outdir_NPX + '/atmospheric_0_'+dmsq41_str+'_'+th14_str+'_'+th24_str+'_'+th34_str+'_'+del14_str+'_'+del24_str+'.hdf5'
        if not os.path.isfile(indir+ '/'+filepath_NPX.split('/')[-1]):
            print('Cannot find this file in current dir: '+ filepath_NPX.split('/')[-1])
            print('The following files are visible: ')
            import glob
            files = glob.glob(indir+'*')
            for file in files:
                print(files)
        copy_to_NPX(filepath_NPX)


print(' --- Calculatinga astrophysical flux ---')
check_file = outdir + '/astro_0_'+dmsq41_str+'_'+th14_str+'_'+th24_str+'_'+th34_str+'_'+del14_str+'_'+del24_str+'.hdf5'
if not os.path.isfile(check_file):
    options = ' '+ indir + ' ' + outdir+' '+ str(index)+' ' + str(dmsq41)+' '+str(th14)+' '+str(th24)+' '+str(th34)+' '+str(del14)+' '+str(del24)
    call_function = indir+ "/astrophysical_neutrino_flux_calculator_with_interactions " + options
    print(call_function)
    subprocess.call(call_function, shell=True)
else:
    print('Output conventional atmospheric file exists: '+check_file)
    print('   ... skipping calculation')

if osg == 'True':
        #filepath_NPX = outdir_NPX + '/atmospheric_0_'+str(format(float(dmsq41), '.6f'))+'_'+str(format(float(th14), '.6f'))+'_'+str(format(float(th24), '.6f'))+'_'+str(format(float(th34), '.6f'))+'_'+str(format(float(del14), '.6f'))+'_'+str(format(float(del24), '.6f'))+'.hdf5'
        filepath_NPX = outdir_NPX + '/astro_0_'+dmsq41_str+'_'+th14_str+'_'+th24_str+'_'+th34_str+'_'+del14_str+'_'+del24_str+'.hdf5'
        if not os.path.isfile(indir+ '/'+filepath_NPX.split('/')[-1]):
            print('Cannot find this file in current dir: '+ filepath_NPX.split('/')[-1])
            print('The following files are visible: ')
            import glob
            files = glob.glob(indir+'*')
            for file in files:
                print(files)
        copy_to_NPX(filepath_NPX)




print('\n --- Calculating Barr fluxes ---')
for flux in ['WM','WP','YM','YP','ZM','ZP']:
    print('Calculating Flux: '+str(flux))
    options = ' '+indir+' '+outdir+' '+str(index)+' '+str(dmsq41)+' '+str(th14)+' '+str(th24)+' '+str(th34)+' '+str(del14)+' '+str(del24)+' '+str(flux)
    call_function = indir + "/conventional_atmospheric_flux_calculator_with_interactions_from_file_barr " + options
    print(call_function)
    check_file = outdir + '/barr_grad_'+flux+'_0_'+dmsq41_str+'_'+th14_str+'_'+th24_str+'_'+th34_str+'_'+del14_str+'_'+del24_str+'.hdf5'
    if not os.path.isfile(check_file):
        subprocess.call(call_function, shell=True) 
    else:
        print('File Exists: '+check_file)

    if osg == 'True':
        filepath_NPX = outdir_NPX + '/barr_grad_'+flux+'_0_'+dmsq41_str+'_'+th14_str+'_'+th24_str+'_'+th34_str+'_'+del14_str+'_'+del24_str+'.hdf5'
        if not os.path.isfile(indir+'/'+filepath_NPX.split('/')[-1]):
            print('Cannot find this file in current dir: '+ filepath_NPX.split('/')[-1])
            print('The following files are visible: ')
            import glob
            files = glob.glob(indir+'*')
            for file in files:
                print(files)
        copy_to_NPX(filepath_NPX)
#sys.exit()
#filepath = outdir + '/barr_grad_'+flux+'_0_'+str(format(float(dmsq41), '.6f'))+'_'+str(format(float(th14), '.6f'))+'_'+str(format(float(th24), '.6f'))+'_'+str(format(float(th34), '.6f'))+'_'+str(format(float(del14), '.6f'))+'_'+str(format(float(del24), '.6f'))+'.hdf5'
#filepath_NPX = outdir_NPX + '/barr_grad_'+flux+'_0_'+str(format(float(dmsq41), '.6f'))+'_'+str(format(float(th14), '.6f'))+'_'+str(format(float(th24), '.6f'))+'_'+str(format(float(th34), '.6f'))+'_'+str(format(float(del14), '.6f'))+'_'+str(format(float(del24), '.6f'))+'.hdf5'
