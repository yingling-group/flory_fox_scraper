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
import sys
import pandas as pd
import numpy as np
from numpy.linalg import inv

# Start the clock
t_start = time.time()
update = 1
total_points = 0

# Input filename:
#i_fname = raw_input('Enter input filename: ')
i_fname = 'flory_fox_pmma.csv'
raw_dat = pd.read_csv(i_fname, skiprows = 1, index_col = 0, \
                      names=['p_class','class_abbr','Mn','name','pid','sid',\
                             'Tg'])

# Output prefix:
#o_prefix = raw_input('Enter output prefix: ')
o_prefix = 'test'

###############################################################################
#        Get Unique Polymer Dataframe                                         #
###############################################################################

poly_info = pd.DataFrame({'name' : raw_dat.name.unique(),
                          'pid' : raw_dat.pid.unique(),
                          'p_class' : raw_dat.p_class.unique(),
                          'class_abbr' : raw_dat.class_abbr.unique()})

for i in poly_info.index:
    # Subset Data
    dat_i = raw_dat[raw_dat.pid == poly_info.pid[i]][['Mn','Tg']]
    Mn_lims = [min(dat_i.Mn), max(dat_i.Mn)]
    Tg_lims = [min(dat_i.Tg), max(dat_i.Tg)]
    dat_i['rMn'] = 1./dat_i.Mn
    
    # Perform linear OLS fit
    n = len(dat_i)
    p = 2
    X = np.column_stack((np.ones(n), np.array(dat_i.rMn)))
    q = inv(X.T.dot(X)).dot(X.T).dot(np.array(dat_i.Tg))
    R = dat_i.Tg - X.dot(q)
    sig_sqd = (1./(n - p))*R.T.dot(R)
    V = sig_sqd*inv(X.T.dot(X))

###############################################################################
#        Denoument                                                            #
###############################################################################

total_time = time.time() - t_start
print 'Success!'
print 'Excecution time: %.2f min for %i data points' % \
        (total_time/60, total_points)