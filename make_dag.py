import math
import numpy as np
import os
from os.path import exists
import sys
import argparse
import utils

class DagMaker():

    def __init__(self, fast_scaling, realization_file, 
                 n_seeds = '-1', fastmc_dir = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/FastMC/', years = '7.634', 
                 osg = "False", make_flux = False, make_fastmc = False, do_fit = False, inject_fit = "False", inject_fit_file = "None",
                systematics = '11001110', barr= '00111111', multisim = '11', astro = '011', xs='111', bayes = 'False'):
        tau_neutrinos = ''
        self.flux_dict = {
            'indir' : "/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/code/GolemFit/resources/FluxOscCalculator/",
            'index' : "0",
            'user' : 'adiaz', 
            'osg' : osg,
            'conv_flux' : "AIRS_mceq121_conv_flux_2011_sib_HG_E3.dat",
            'prompt_flux' : "AIRS_mceq121_pr_flux_2011_sib_HG_E3.dat",
        }

        self.fastmc_dict = {
            'gen_fastMC' : 'True',
            'Emax' : '9976',
            # 'sim' : 'Platinum_Split_HE_Alex',
            'sim' : 'Platinum_Split_Plus_Tau',
            'max_sim' : '-1',
            'fast_scaling' : fast_scaling,
            'tau_neutrinos' : tau_neutrinos,
            'fastmc_dir' : fastmc_dir,
            'years' : years,
            'osg' : osg
        }

        self.fit_dict = {
            'use_fastMC' : 'True',
            'Emax' : '9976',
            'sim' : self.fastmc_dict['sim'],
            'max_sim' : '-1', 
            'fast_scaling' : self.fastmc_dict['fast_scaling'],
            'tau_neutrinos' : tau_neutrinos,
            'fastmc_dir' : self.fastmc_dict['fastmc_dir'],
            'realization_file' : realization_file,
            'n_seeds' : n_seeds,
            'years' : years,
            'inject_fit' : inject_fit,
            'inject_fit_file' : inject_fit_file,
            'systematics': systematics,
            'barr': barr,
            'multisim': multisim,
            'astro': astro,
            'xs': xs,
            'osg' : osg,
            'change_tol' : '1e-20',
            'grad_tol' : '1e-20',
            'bayes' : bayes
        }

        self.make_flux = make_flux
        self.make_fastmc = make_fastmc
        self.do_fit = do_fit

        self.years = years
    def print_vars(self, f, jobname, var_name, val):
        f.write('VARS\t' + jobname.strip() + '\t' + var_name+'=\"' + val+ "\"\n")

    def do_fluxes_exist(self, fluxdir, point):
        flux_prefixes = ['astro', 'atmospheric', 'barr_grad_WM', 'barr_grad_WP', 'barr_grad_YM', 'barr_grad_YP', 'barr_grad_ZM', 'barr_grad_ZP', 'prompt_atmospheric']
        for prefix in flux_prefixes:
            if not exists(fluxdir + prefix + "_" + point + ".hdf5"):
                return False
        return True

    def make_flux_dag(self, filename, jobname, fluxdir, dm2, th14, th24, th34, Ut4sq, del14, del24, osg = "False"):
        if osg == "True":
            filename.write('JOB\t' + jobname + '\t/home/adiaz/Cascades/th34/make_flux_OSG.submit\n')
        else:
            filename.write('JOB\t' + jobname + '\t/home/adiaz/Cascades/th34/make_flux.submit\n')
        self.print_vars(filename, jobname, 'th14',  str(format(float(th14), '.6f')))
        self.print_vars(filename, jobname, 'th24',  str(format(float(th24), '.6f')))
        self.print_vars(filename, jobname, 'th34',  str(format(float(th34), '.6f')))
        self.print_vars(filename, jobname, 'dmsq41',  str(format(float(dm2), '.6f')))
        self.print_vars(filename, jobname, 'del14',  str(format(float(del14), '.6f')))
        self.print_vars(filename, jobname, 'del24',  str(format(float(del24), '.6f')))
        self.print_vars(filename, jobname, 'outdir',  fluxdir)
        for key, value in self.flux_dict.items():
            self.print_vars(filename, jobname, key, value)
        filename.write('Retry ' + jobname + " 2\n")

    def make_fastmc_dag(self, filename, jobname, fluxdir, point, Ut4sq, osg = "False"):
        if osg == "True":
            filename.write('JOB\t' + jobname + '\t/home/adiaz/Cascades/th34/make_fastmc_OSG.submit\n')
        else:
            filename.write('JOB\t' + jobname + '\t/home/adiaz/Cascades/th34/make_fastmc.submit\n')
        self.print_vars(filename, jobname, 'point', point)
        self.print_vars(filename, jobname, 'fluxdir', fluxdir)
        for key, value in self.fastmc_dict.items():
            self.print_vars(filename, jobname, key, value)
        filename.write('Retry ' + jobname + " 2\n")

    def make_fit_dag(self, filename, jobname, fluxdir, point, outdir, Ut4sq, osg = "False"):
        if osg == "True":
            filename.write('JOB\t' + jobname + '\t/home/adiaz/Cascades/th34/do_fit_OSG.submit\n')
        else:
            filename.write('JOB\t' + jobname + '\t/home/adiaz/Cascades/th34/do_fit.submit\n')
        self.print_vars(filename, jobname, 'point', point)
        self.print_vars(filename, jobname, 'fluxdir', fluxdir)
        self.print_vars(filename, jobname, 'outdir', outdir)
        for key, value in self.fit_dict.items():
            self.print_vars(filename, jobname, key, value)
        # filename.write('Retry ' + jobname + " 3\n")


    def addtodag(self, dm2, Ue4sq, Um4sq, Ut4sq, del14, del24, f, job_index, outdir, index = 0):
        i = job_index
        fluxdir = "/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/Fluxes/AIRS_mceq121_2011_sib_HG_E3/Ut4sq_" + str(format(float(Ut4sq), '.6f')) + '/'


        if Um4sq + Ut4sq > 1.:
            return
        th24 = np.arcsin(np.sqrt(Um4sq))

        th34 = np.arcsin(np.sqrt( Ut4sq / (1.-Um4sq) ) )

        th14, th24, th34 = utils.Usq_to_thetas(Ue4sq, Um4sq, Ut4sq)

        point = utils.get_point_string(index = index, dm2 = dm2, th14 = th14, th24 = th24, th34 = th34, d14 = del14, d24 = del24)

        jobname_A = str(i) + "A"
        jobname_B = str(i) + "B"
        jobname_C = str(i) + "C"

        if not math.isclose(Ut4sq,  np.sin(th34)**2 * np.cos(th24)**2):
            print("ohno", Ut4sq, np.sin(th34)**2 * np.cos(th24)**2)

        description = self.fastmc_dict['sim']+'_'+self.fastmc_dict['fast_scaling']+'_'+self.years+'_'+fluxdir.split('/')[-3]+'/'+fluxdir.split('/')[-2]+'/'+ point+'/'

        if self.make_flux and not self.do_fluxes_exist(fluxdir, point):
            os.makedirs(fluxdir, exist_ok=True)
            self.make_flux_dag(f, jobname_A, fluxdir, dm2, th14, th24, th34, Ut4sq, del14, del24, self.flux_dict['osg'])

            if self.make_fastmc:
                f.write("PARENT " + jobname_A + " CHILD " + jobname_B + "\n")
                os.makedirs(self.fastmc_dict['fastmc_dir'] + description, exist_ok=True)
                self.make_fastmc_dag(f, jobname_B, fluxdir, point, Ut4sq, self.fastmc_dict['osg'])
                return


        if self.make_fastmc and not os.path.exists(self.fastmc_dict['fastmc_dir'] + description +'/STERILE.meows'):
            if not self.do_fluxes_exist(fluxdir, point):
                return
            os.makedirs(self.fastmc_dict['fastmc_dir'] + description, exist_ok=True)
            self.make_fastmc_dag(f, jobname_B, fluxdir, point, Ut4sq, self.fastmc_dict['osg'])
            # continue

        if self.do_fit:
            if not os.path.exists(outdir+ point+'_'+ self.fit_dict['realization_file'].split('/' )[-1].split('.npz')[0]+'.json'):
                os.makedirs(outdir, exist_ok=True)
                self.make_fit_dag(f, jobname_C, fluxdir, point, outdir, Ut4sq, self.fit_dict['osg'])
            # continue

def main(m, dm2_list, Um4sq_list, Ut4sq_list, del24_list, outdirbase, outdir_dag):

    # outdirname = '/Asimov_at_'+fast_scaling+'_tolerance_1e-20/0_0.000000_0.000000_0.000000_0.000000_0.000000_0.000000'
    # outdirbase = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/Fits/'+outdirname +'/'

    # logdm2_list = np.asarray(np.ndarray.tolist(np.arange(-2.15, 2.10, 0.05))+ [2.15])
    print(del24_list)

    print(len(dm2_list), len(Um4sq_list), len(Ut4sq_list), len(del24_list))

    i = -1


    for Ut4sq in Ut4sq_list:
        print(Ut4sq)
        if Ut4sq == 0.:
            j = 1
            points = [(0.,0.,0.,0.)]*(len(dm2_list)*len(Um4sq_list)*len(del24_list) + 1)
        else:
            j = 0
            points = [(0.,0.,0.,0.)]*(len(dm2_list)*len(Um4sq_list)*len(del24_list))

        for Um4sq in Um4sq_list:
            for dm2 in dm2_list:
                for del24 in del24_list:
                    points[j] = (dm2, Um4sq, Ut4sq, del24)
                    j+=1

        F = outdir_dag + '/Ut4sq_' + str(format(float(Ut4sq), '.6f')) + '.dag'
        os.makedirs(outdir_dag, exist_ok=True)
        outdir = outdirbase + '/Ut4sq_' + str(format(float(Ut4sq), '.6f')) + '/'

        Ue4sq = 0.
        del14 = 0.
        with open(F, 'w') as f:

            for (dm2, Um4sq, Ut4sq, del24) in  points:

                i += 1

                m.addtodag(dm2=dm2, Ue4sq=Ue4sq, Um4sq=Um4sq, Ut4sq=Ut4sq, del14=del14, del24=del24, f=f, outdir = outdir, job_index = i) 


if __name__ == "__main__":
    parser = argparse.ArgumentParser() 
    parser.add_argument('--fast_scaling', type=str, required=True)
    parser.add_argument('--fastmc_dir', type=str, default = '/data/ana/SterileNeutrino/IC86/HighEnergy/Analysis/th34/FastMC/')
    parser.add_argument('--realization_file', type=str)
    parser.add_argument('--outdirbase', type=str, default = "")

    parser.add_argument('--make_flux', action="store_true")
    parser.add_argument('--make_fastmc', action="store_true")
    parser.add_argument('--do_fit', action="store_true")

    parser.add_argument('--n_seeds', default='-1')
    parser.add_argument('--osg', type=str, default="False")

    parser.add_argument('--outdir_dag', type=str, default = os.getcwd())

    args = parser.parse_args()

    osg = args.osg
    fast_scaling = args.fast_scaling
    fastmc_dir = args.fastmc_dir
    realization_file = args.realization_file

    make_flux = args.make_flux
    make_fastmc = args.make_fastmc
    do_fit = args.do_fit

    n_seeds = args.n_seeds

    outdir_dag = args.outdir_dag
    logdm2_list = np.asarray(np.ndarray.tolist(np.arange(-2.10, 2.10, 0.1))+ [2.15])
    dm2_list = np.power(10, logdm2_list)

    dm2_list = dm2_list[np.logical_and(dm2_list>.1, dm2_list<50)]
    dm2_list = np.append(dm2_list, 50.)

    log_Um4sq_list = np.asarray(np.ndarray.tolist(np.arange(-3., 0., 0.1)))
    Um4sq_list = np.power(10, log_Um4sq_list)
    Um4sq_list = np.append(Um4sq_list, 0.50)

    log_Ut4sq_list = np.asarray(np.ndarray.tolist(np.arange(-3., 0., 0.2)))
    Ut4sq_list = np.power(10, log_Ut4sq_list)
    Ut4sq_list = np.insert(Ut4sq_list, 0, 0.)
    Ut4sq_list = np.append(Ut4sq_list, 0.50)

    outdirbase = args.outdirbase
    del24_list = [np.pi]

    years = '7.634'
    m = DagMaker(fast_scaling = fast_scaling, fastmc_dir = fastmc_dir, years = years, realization_file = realization_file, osg = osg, make_flux = make_flux, make_fastmc = make_fastmc, do_fit = do_fit, n_seeds = n_seeds)
    main(m, dm2_list, Um4sq_list, Ut4sq_list, del24_list, outdirbase, outdir_dag)
