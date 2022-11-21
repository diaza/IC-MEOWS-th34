import nuflux
import nuSQuIDS as nsq
# import nuSQUIDSpy as nsq
#import nuSQUIDSTools

import numpy as np
from scipy import integrate
import time

def get_nusquids_obj(numneu, dm2, th14, th24, th34, cp, flux):

    assert numneu == 3 or numneu == 4, "numneu must be equal to 3 or 4"

    units = nsq.Const()

    interactions = True

    Emin = 1.e1*units.GeV
    Emax = 1.e6*units.GeV
    czmin = -1.
    czmax = 1.

    cz_nodes = nsq.linspace(czmin, czmax, 101)
    energy_nodes = nsq.logspace(Emin, Emax, 301)

    nuSQ = nsq.nuSQUIDSAtm(cz_nodes, energy_nodes, numneu, nsq.NeutrinoType.both, interactions)


    nuSQ.Set_MixingAngle(0,1,0.563942)
    nuSQ.Set_MixingAngle(0,2,0.154085)
    nuSQ.Set_MixingAngle(1,2,0.785398)

    nuSQ.Set_SquareMassDifference(1,7.65e-05)
    nuSQ.Set_SquareMassDifference(2,0.00247)

    nuSQ.Set_CPPhase(0,2,cp)
    if numneu > 3:
        nuSQ.Set_SquareMassDifference(3,dm2)
        nuSQ.Set_MixingAngle(0,3, th14)
        nuSQ.Set_MixingAngle(1,3, th24)
        nuSQ.Set_MixingAngle(2,3, th34)

    nuSQ.Set_rel_error(1.0e-08)
    nuSQ.Set_abs_error(1.0e-08)
    # nuSQ.Set_GSL_step(gsl_odeiv2_step_rk4)

    inistate = np.zeros( (nuSQ.GetNumCos(), nuSQ.GetNumE(), nuSQ.GetNumRho(), nuSQ.GetNumNeu()) )

    e_range = nuSQ.GetERange()
    cz_range = nuSQ.GetCosthRange()

    for ci in range(nuSQ.GetNumCos()):
        for ei in range(nuSQ.GetNumE()):

            inistate[ci][ei][0][0] = flux.getFlux(nuflux.NuE, e_range[ei]/units.GeV, cz_range[ci])
            inistate[ci][ei][0][1] = flux.getFlux(nuflux.NuMu, e_range[ei]/units.GeV, cz_range[ci])
            # inistate[ci][ei][0][2] = flux.getFlux(nuflux.NuTau, e_range[ei]/units.GeV, cz_range[ci])
            inistate[ci][ei][0][2] = 0.

            inistate[ci][ei][1][0] = flux.getFlux(nuflux.NuEBar, e_range[ei]/units.GeV, cz_range[ci])
            inistate[ci][ei][1][1] = flux.getFlux(nuflux.NuMuBar, e_range[ei]/units.GeV, cz_range[ci])
            # inistate[ci][ei][1][2] = flux.getFlux(nuflux.NuTauBar, e_range[ei]/units.GeV, cz_range[ci])
            inistate[ci][ei][1][2] = 0.

            if nuSQ.GetNumNeu() == 4:
                inistate[ci][ei][0][3] = 0.
                inistate[ci][ei][1][3] = 0.

    nuSQ.Set_initial_state(inistate, nsq.Basis.flavor)

    nuSQ.Set_ProgressBar(True)
    nuSQ.Set_IncludeOscillations(True)

    return nuSQ

def get_contour(x, y, f):

    units = nsq.Const()

    cz, en = np.meshgrid(x, y)

    z = np.zeros(cz.shape)

    for i in range(len(z)):
        for j in range(len(z[i])):

            z[i][j] = f(cz[i][j], en[i][j])

    return z

# def get_grid(cz, en, f):

    # units = nsq.Const()

    # z = np.zeros( (len(en) - 1, len(cz) - 1) )

    # for i in range(len(z)):
        # for j in range(len(z[i])):
            # xmin = cz[j]
            # xmax = cz[j+1]
            # ymin = en[i]
            # ymax = en[i+1]

            # integrand = lambda x, y: f(x, y)
            # z[i][j] = 2.*np.pi*integrate.dblquad( integrand, \
                                        # ymin, ymax, lambda x: xmin, lambda x: xmax)[0]
            # # integrand_log = lambda x, y: np.log(10) * 10**y *f(x, (10**y))
            # # z[i][j] = 2. * np.pi * integrate.dblquad( integrand_log, \
                                        # # np.log10(ymin), np.log10(ymax), lambda x: xmin, lambda x: xmax)[0]

    # return z


# def get_grid_preint(cz, en, f):

    # units = nsq.Const()

    # z = np.zeros( (len(en) - 1, len(cz) - 1) )

    # for i in range(len(z)):
        # for j in range(len(z[i])):
            # xmin = cz[j]
            # xmax = cz[j+1]
            # ymin = en[i]
            # ymax = en[i+1]

            # z[i][j] = 2*np.pi*integrate.quad(f, ymin, ymax, args=(xmin, xmax))[0]

    # return z

