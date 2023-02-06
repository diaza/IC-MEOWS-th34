import numpy as np
import json 
from os.path import exists
import matplotlib.pyplot as plt


def get_llh(filename):
    
    f = open(filename, 'r')
    
    try:
        data = json.loads(f.read())
        llh =  data["LLH"]
    except json.decoder.JSONDecodeError:
        print("DecodeError, filename is {}".format(filename))
        llh = np.inf

    
    f.close()
    
    return llh

def get_point_string(index = 0, dm2 = 0., th14 = 0., th24 = 0., th34 = 0., d14 = 0., d24 = 0.):
    
    point = str(index) + '_'\
    + str(format(float(dm2), '.6f')) + '_'\
    + str(format(float(th14), '.6f')) + '_'\
    + str(format(float(th24), '.6f')) + '_'\
    + str(format(float(th34), '.6f')) + '_'\
    + str(format(float(d14), '.6f')) + '_'\
    + str(format(float(d24), '.6f'))
    
    return point

def read_point_string(p):
        
    index, dm2, th14, th24, th34, d14, d24 = p.split('_')
    
    return index, dm2, th14, th24, th34, d14, d24 
    

def Usq_to_thetas(Ue4sq = 0., Um4sq = 0., Ut4sq = 0.):
    
    th14 = np.arcsin(np.sqrt( Ue4sq ))
    th24 = np.arcsin(np.sqrt( Um4sq / (1. - Ue4sq) ))
    th34 = np.arcsin(np.sqrt( Ut4sq / (1. - Ue4sq - Um4sq) ))
    
    return th14, th24, th34

def thetas_to_Usq(th14 = 0., th24 = 0., th34 = 0.):
    
    Ue4sq = np.sin(th14)**2
    Um4sq = np.sin(th24)**2 * np.cos(th14)**2
    Ut4sq = np.sin(th34)**2 * np.cos(th24)**2 * np.cos(th14)**2
    
    return Ue4sq, Um4sq, Ut4sq
    
def get_points(u_dir, dm2_list, Um4sq_list, Ut4sq_list, d24_list, suffix=''):
    points = np.array(len(Ut4sq_list)*[[[0,0,0,np.inf]]*len(dm2_list)*len(Um4sq_list)*len(d24_list)])
    for k, Ut4sq in enumerate(Ut4sq_list):
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
                    point = get_point_string(dm2 = dm2, th24 = th24, th34 = th34, d24 = d24)
#                     print(point)
                    if exists(Ut4sq_dir + point+suffix):             
                        llh = get_llh(Ut4sq_dir + point+suffix)
                        points[k][i] = [dm2, Um4sq, Ut4sq, llh]
                    else: 
                        # print(Ut4sq_dir + point+suffix)
                        points[k][i] = [dm2, Um4sq, Ut4sq, np.inf]

                    i+=1
                    

    return points
    #     points_dict[Ut4sq] = points
    
def make_hist(p1, p2, title):


    
    dllh1 = p1 - p1.min()
    dllh2 = p2 - p2.min()
#     print(p1.min(), p2.min())
    p = 2*(dllh1 - dllh2)
    
    if np.all(~np.isfinite(p)):
        return
    p = p[np.isfinite(p)]
    
    fig, ax = plt.subplots()
    
    ax.set_title(title, size = 20)
    ax.set_xlabel(r'$\Delta (\Delta LLH) $', size = 20)
    ax.set_ylabel('percentage', size = 20)
    ax.tick_params(axis='both', labelsize= 15)
    
    bins = np.linspace(p.min(), p.max(), 100)
#     bins = np.linspace(p.min() ,1,100)
#     ax.set_ylim(.1,1)
    print(len(p))
    h = ax.hist(p, bins = bins, weights = [1./len(p)]*len(p), log=True)
#     h = ax.hist(p, bins = bins, log=True)
    print(h[0].sum())
    
def Um4sqtosin22th(um4sq):
    th24 = np.arcsin(np.sqrt(um4sq))
    sin22th = np.sin(2*th24)**2
    return sin22th


def make_scatter_plots(points_list1, points_list2, critical, title, dm2_list, Um4sq_list, Ut4sq_list, d24_list):
    
    dcp_0_min_llh = points_list1[:,:,3].min()
    dcp_pi_min_llh = points_list2[:,:,3].min()
    # dcp_pi_min_llh = points_list[:,:,2].min()
    print(dcp_0_min_llh, dcp_pi_min_llh, title)
    for j, Ut4sq in enumerate(Ut4sq_list):
        fig, axes = plt.subplots(1,2,figsize=(2*6,6), constrained_layout=True)
        fig.suptitle(title+"%", fontsize =30)
        axes[0].set_xlim(.001, 1)
        axes[1].set_xlim(Um4sqtosin22th(.001), 1)
        for i in range(len(axes)):
            axes[i].set_ylim(dm2_list[0], dm2_list[-1])
            axes[i].set_title(r"$|U_{{\tau 4}}|^2$ = {:.3f}".format(Ut4sq), size = 20)
            axes[i].set_ylabel(r"$\Delta m^2_{41}$",size=20)
            axes[i].set_xscale('log')
            axes[i].set_yscale('log')
            axes[i].tick_params(axis='both', labelsize= 15)
    #         axes[i].set_aspect('equal')

        axes[0].set_xlabel(r"$|U_{{\mu 4}}|^2$",size=20)
        axes[1].set_xlabel(r"$\sin^{2}2\theta_{24}$",size=20)
        
        dllh1 = points_list1[j,:,3] - dcp_pi_min_llh
        dllh2 = points_list2[j,:,3] - dcp_0_min_llh
#         print(dllh1, dllh2)
        llh_diff = 2*(dllh1 - dllh2)
        
#         mask = np.logical_and(np.abs(llh_diff) != np.inf, llh_diff > 0.1)
        
        finite_mask = np.logical_and(points_list1[j,:,3] != np.inf, points_list2[j,:,3] != np.inf)
#         finite_mask = True
        dcp_0_mask = np.logical_and(2*dllh1 < critical, finite_mask)
        dcp_pi_mask = np.logical_and(2*dllh2 < critical, finite_mask)
                
        axes[0].scatter((points_list1[j,:,1])[dcp_0_mask], (points_list1[j,:,0])[dcp_0_mask], s=100, label = r"$\delta_{cp} = 0$")
        axes[0].scatter((points_list2[j,:,1][dcp_pi_mask]), (points_list2[j,:,0])[dcp_pi_mask], label = r"$\delta_{cp} = \pi$")
#         axes[0].scatter((points_list2[j,:,0][mask]), (points_list2[j,:,1])[mask], s=10,  label = r"$\delta_{cp} = \pi$")
        

        axes[1].scatter((Um4sqtosin22th(points_list1[j,:,1])[dcp_0_mask]), (points_list1[j,:,0])[dcp_0_mask], s=100, label = r"$\delta_{cp} = 0$")
        axes[1].scatter((Um4sqtosin22th(points_list2[j,:,1])[dcp_pi_mask]), (points_list2[j,:,0])[dcp_pi_mask], label = r"$\delta_{cp} = \pi$")
#         axes[1].scatter((Um4sqtosin22th(points_list2[j,:,0])[mask]), (points_list2[j,:,1])[mask], s=10, label = r"$\delta_{cp} = \pi$")        
#         axes[0].legend(fontsize=20)
#         axes[1].legend(fontsize=20)
#         plt.savefig("./pics/"+title+"percent/"+str(format(float(Ut4sq), '.6f'))+".png")

def make_exclusion(dm2_list, um4_list, dllh, critical, label= "", ax = None, **plt_kwargs):
    
    if ax is None:
        ax = plt.gca()
    dm2_grid, um4_grid = np.meshgrid(dm2_list, um4_list)
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    # ax.set_xlim(um4_list.min(), um4_list.max())
    # ax.set_ylim(dm2_list.min(), dm2_list.max())
    
#     ax.set_xlabel(x_label)
#     ax.set_ylabel(y_label)
    dllh[~np.isfinite(dllh)]=np.nan
#     print(dllh)
    p=ax.contour(np.log10(um4_list), np.log10(dm2_list), dllh.reshape(len(dm2_list), len(um4_list)), levels = [critical], alpha = 0.)
#     p=plt.contourf(um4_list, dm2_list, dllh.reshape(len(dm2_list), len(um4_list)), alpha = 0.)
#     print(dllh.reshape(len(dm2_list), len(um4_list)))
#     print(p.allsegs)
    
    dat0= p.allsegs[0]
#     print(len(dat0[0]))
    for i in range(len(dat0)):
        if i == 0 :
            c = ax.plot(10**dat0[i][:,0],10**dat0[i][:,1], label = label, **plt_kwargs)
        else:
            if 'color' in plt_kwargs.keys():
                c = ax.plot(10**dat0[i][:,0],10**dat0[i][:,1], **plt_kwargs)
            else:
                c = ax.plot(10**dat0[i][:,0],10**dat0[i][:,1], color = c[0].get_color(), **plt_kwargs)

    return c
            
     
#     print(p)
#     cbar = plt.colorbar()
def make_exclusion_colorful(dm2_list, um4_list, dllh, ax = None, x_label = "", y_label = "", **plt_kwargs):
    
    if ax is None:
        ax = plt.gca()
    dm2_grid, um4_grid = np.meshgrid(dm2_list, um4_list)
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    dllh[~np.isfinite(dllh)]=np.nan
#     print(dllh)
    p=ax.contourf(um4_list, dm2_list, dllh.reshape(len(dm2_list), len(um4_list)), **plt_kwargs)
           
    return p
#     fig.colorbar(p, ax = ax, ticks = np.linspace(0,30,7))

ConvNormCenter          = 1.
ConvNormWidth           = 0.4
AstroNormCenter         = 4.72/6.00
AstroNormWidth          = 0.36
sys_dict = {
'DOMeff'  : (1.27, 0.123, 1.234, 1.346),
'HoleIce'          : (-1, 10, -5.35, 1.85),
        # inject_dict['pkr']              = 1.
        # inject_dict['nnbr']             = 1.
'Normalization'    : (ConvNormCenter, ConvNormWidth, 1e-5, 10.),
'CR'               : (0.,0.03, -0.8, 0.8),
'ZenithCorrection' : (0, 1., -10, 10),
        # inject_dict['HQE']              = 1.35
        # inject_dict['barrHM']           = 0.
        # inject_dict['barrHP']           = 0.
'barrWM'           : (0, 0.4, -0.475, 0.475),
'barrWP'           : (0, 0.4, -0.475, 0.475),
'barrYM'           : (0, 0.3, -0.475, 0.475),
'barrYP'           : (0, 0.3, -0.475, 0.475),
'barrZM'           : (0, 0.12, -0.2375, 0.475),
'barrZP'           : (0, 0.12, -0.19, 0.475),
'icegrad0'         : (0.,1.,-4.,4.),
'icegrad1'         : (0.,1.,-4.,4.),
        # inject_dict['promptNorm']       = PromptNormCenter
'astroNorm'        : (AstroNormCenter, AstroNormWidth, 0, np.inf),
'astroDeltaGamma'  : (0.,0.36, -5, 5),
'nuxs'             : (1., 0.03, 0.582562, 1.4159),
'nubarxs'          : (1., 0.075, 0.582562, 1.4159),
'kaonLosses'       : (0., 1.0, -1., 1.)
}

prop_translator = {}
prop_translator['DOMeff'] = 'DOM Efficiency'
prop_translator['HoleIce'] = 'HoleIce'
prop_translator['icegrad1'] = 'IceGradient 1'
prop_translator['icegrad0'] = 'IceGradient 0'
prop_translator['barrWM'] = 'Barr WM'
prop_translator['barrWP'] = 'Barr WP'
prop_translator['barrZM'] = 'Barr ZM'
prop_translator['barrZP'] = 'Barr ZP'
prop_translator['barrYM'] = 'Barr YM'
prop_translator['barrYP'] = 'Barr YP'
prop_translator['CR'] = r'Cosmic Ray $\Delta\gamma$'
prop_translator['ZenithCorrection'] = 'Atm. Density'
prop_translator['Normalization'] = 'Normalization'
prop_translator['promptNorm'] = 'Prompt Norm'
prop_translator['astroNorm'] = 'Astro. Norm'
prop_translator['astroDeltaGamma'] = 'Astro. $\Delta \gamma$'
prop_translator['nuxs'] = 'Neutrino XS'
prop_translator['nubarxs'] = 'Anti-Neutrino XS'
prop_translator['kaonLosses'] = 'Kaon Energy Loss'
