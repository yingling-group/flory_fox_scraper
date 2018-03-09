#!/usr/bin/env python

'''
Fit Flory Fox Equation - fit_flory_fox.py

Author: James S. Peerless
        Yingling Group
        NC State University

For internal evaluation by Citrine Informatics only.
'''

###############################################################################
#        Initialization                                                       #
###############################################################################

import time
import os
import pandas as pd
import numpy as np
from scipy import stats
from numpy.linalg import inv
from math import sqrt
import matplotlib.pyplot as plt

# Start the clock
t_start = time.time()
total_points = 0

# Input filename:
#i_fname = raw_input('Enter input filename: ')
i_fname = 'flory_fox.csv'
raw_dat = pd.read_csv(i_fname, skiprows = 1, index_col = 0, \
                      names=['p_class','class_abbr','Mn','name','pid','sid',\
                             'Tg'])

# Output prefix:
#o_prefix = raw_input('Enter output prefix: ')
o_prefix = 'test'
if not os.path.isdir(o_prefix + '_plots'):
    os.mkdir(o_prefix + '_plots')

plt.style.use('ggplot')

###############################################################################
#        Get Unique Polymer Dataframe                                         #
###############################################################################

n_polys = raw_dat.pid.nunique()
poly_info = pd.DataFrame({'name' : raw_dat.name.unique(),
                          'pid' : raw_dat.pid.unique(),
                          'p_class' : raw_dat.p_class.unique(),
                          'class_abbr' : raw_dat.class_abbr.unique(),
                          'n_pts' : np.zeros(n_polys),
                          'Tg_inf' : np.zeros(n_polys),
                          'K' : np.zeros(n_polys) })

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
    X = np.column_stack((np.ones(n), np.array(dat_i.rMn)))
    q = inv(X.T.dot(X)).dot(X.T).dot(np.array(dat_i.Tg))
    R = dat_i.Tg - X.dot(q)
    sigma = sqrt((1./(n - p))*R.T.dot(R))
    V = sigma*sigma*inv(X.T.dot(X))
    poly_info.n_pts.iat[i] = n
    poly_info.Tg_inf.iat[i] = q[0]
    poly_info.K.iat[i] = q[1]
    Mn_fit = np.linspace(min(dat_i.Mn), max(dat_i.Mn), num=10000)
    Tg_fit = q[0] + q[1]/Mn_fit
    q_conf_up = q + stats.t.ppf(1-0.025, (n-p))*np.sqrt(np.diag(V))
    q_conf_lo = q - stats.t.ppf(1-0.025, (n-p))*np.sqrt(np.diag(V))
    Tg_conf_up = q_conf_up[0] + q_conf_up[1]/Mn_fit
    Tg_conf_lo = q_conf_lo[0] + q_conf_lo[1]/Mn_fit
    
    # Plot
    plt.figure(1,figsize=(6,10))
    plt.subplot(211)
    plt.plot(dat_i.Mn, dat_i.Tg, '.', \
             Mn_fit, Tg_fit, '--', \
             Mn_fit, Tg_conf_up, 'k--', \
             Mn_fit, Tg_conf_lo, 'k--',)
    plt.xscale('log')
    plt.xlabel('$M_n$ (g/mol)')
    plt.ylabel('$T_g$ (K)')
    plt.subplot(212)
    plt.plot(dat_i.Mn, R, '.', Mn_fit, np.zeros(10000), '--')
    plt.xlabel('$M_n$ (g/mol)')
    plt.ylabel('Residuals (K)')
    plt.xscale('log')
    plt.savefig(o_prefix + '_plots/' + str(poly_info.name[i]) + '.png')
    plt.clf()

###############################################################################
#        Denoument                                                            #
###############################################################################

print poly_info
total_time = time.time() - t_start
print 'Success!'
print 'Excecution time: %.2f min for %i data points' % \
        (total_time/60, total_points)