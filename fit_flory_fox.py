#!/usr/bin/env python

'''
Fit Flory Fox Equation - fit_flory_fox.py

Author: James S. Peerless
        Yingling Group
        NC State University

'''

###############################################################################
#        Initialization                                                       #
###############################################################################

import time
import os
import pandas as pd
import numpy as np
from numpy.linalg import inv
from math import sqrt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Start the clock
t_start = time.time()
total_points = 0

# Input filename:
i_fname = raw_input('Enter input filename: ')
raw_dat = pd.read_csv(i_fname, index_col = 0)

# Output prefix:
o_prefix = raw_input('Enter output prefix: ')
if not os.path.isdir(o_prefix + '_plots'):
    os.mkdir(o_prefix + '_plots')

plt.style.use('ggplot')

###############################################################################
#        Initialize Polymer Dataframe                                         #
###############################################################################

n_polys = raw_dat.pid.nunique()
empty_list = []
for i in range(n_polys):
    empty_list.append([])
poly_info = pd.DataFrame({'name' : raw_dat.name.unique(),
                          'pid' : raw_dat.pid.unique(),
                          'p_class' : raw_dat.p_class.unique(),
                          'class_abbr' : raw_dat.class_abbr.unique(),
                          'n_pts' : np.zeros(n_polys),
                          'Tg_inf' : np.zeros(n_polys),
                          'K' : np.zeros(n_polys), 
                          'sigma' : np.zeros(n_polys), 
                          'V' : empty_list,
                          'Tg_inf_int' : empty_list,
                          'K_int' : empty_list })

for i in poly_info.index:
    # Subset Data
    dat_i = raw_dat[raw_dat.pid == poly_info.pid[i]][['Mn','Tg']]
    dat_i = dat_i.drop_duplicates()
    dat_i = dat_i[np.abs(dat_i.Tg-dat_i.Tg.mean())<=(2*dat_i.Tg.std())]
    dat_i = dat_i[np.abs(dat_i.Mn-dat_i.Mn.mean())<=(2*dat_i.Mn.std())]
    dat_i['rMn'] = 1./dat_i.Mn
    
    # Perform linear OLS fit
    n = len(dat_i)
    if n < 3:
        print 'Not enough datapoints for %s! Skipping...' % (poly_info.name[i])
        continue
    total_points = total_points + n
    p = 2
    X = np.column_stack((np.ones(n), np.array(dat_i.rMn*-1.)))
    q = inv(X.T.dot(X)).dot(X.T).dot(np.array(dat_i.Tg))
    R = dat_i.Tg - X.dot(q)
    sigma = sqrt((1./(n - p))*R.T.dot(R))
    V = sigma*sigma*inv(X.T.dot(X))
    q_sig = np.sqrt(np.diag(V))
    Tg_inf_int = [q[0]-(2.*q_sig[0]), q[0]+(2.*q_sig[0])]
    K_int = [q[1]+(2.*q_sig[1]), q[1]-(2.*q_sig[1])]
    
    # Construct Fit Data
    Mn_fit = np.linspace(min(dat_i.Mn), max(dat_i.Mn), num=10000)
    Tg_fit = q[0] - q[1]/Mn_fit
    Tg_up = Tg_fit + 2*sigma
    Tg_lo = Tg_fit - 2*sigma
    
    # Store in Dataframe
    poly_info.n_pts.iat[i] = n
    poly_info.Tg_inf.iat[i] = q[0]
    poly_info.K.iat[i] = q[1]
    poly_info.sigma.iat[i] = sigma
    poly_info.V.iat[i] = V
    poly_info.Tg_inf_int.iat[i] = Tg_inf_int
    poly_info.K_int.iat[i] = K_int
    
    # Plot
    plt.figure(1,figsize=(6,10))
    plt.subplot(211)
    plt.plot(dat_i.Mn, dat_i.Tg, '.', \
             Mn_fit, Tg_fit, '--', \
             Mn_fit, Tg_up, 'k--', \
             Mn_fit, Tg_lo, 'k--', )
    plt.xscale('log')
    plt.xlabel('$M_n$ (g/mol)')
    plt.ylabel('$T_g$ (K)')
    plt.legend(['PoLyInfo Data', 'OLS Fit', '$2 \sigma$ Intervals'])
    plt.subplot(212)
    plt.plot(dat_i.Mn, R, '.', \
             Mn_fit, np.zeros(10000), '--', \
             Mn_fit, np.ones(10000)*2*sigma, 'k--', \
             Mn_fit, np.ones(10000)*-2*sigma, 'k--', \
             label=['PoLyInfo Data'])
    plt.xlabel('$M_n$ (g/mol)')
    plt.ylabel('Residuals (K)')
    plt.xscale('log')
    plt.legend(['PoLyInfo Data', 'OLS Fit'])
    plt.savefig(o_prefix + '_plots/' + str(poly_info.name[i]) + '.png')
    plt.clf()

###############################################################################
#        Denoument                                                            #
###############################################################################

# Write fit data to file
pd.set_option("display.max_colwidth", 70)
of = open(o_prefix + '.txt', 'w')
of.write(poly_info.to_string(columns=['p_class', 'name','pid','Tg_inf',\
                                      'Tg_inf_int','K','K_int','n_pts',\
                                      'sigma','V'],
                             header=['Polymer Class', 'Polymer Name', 'PID',\
                                     'Tg Max (K)', 'Tg Max 2 sigma Int.',\
                                     'K (K mol/g)', 'K 2 sigma Int.',\
                                     'n Data Points', 'Variance (sigma)',\
                                     'Covariance Matrix (V)'],
                             float_format = '%.2f' ))
of.close()

total_time = time.time() - t_start
print 'Success!'
print 'Excecution time: %.2f min for %i data points' % \
        (total_time/60, total_points)
