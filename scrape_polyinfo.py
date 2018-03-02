#!/usr/bin/env python

'''
PolyInfo Database Scraper - scrape_polyinfo.py

Author: James S. Peerless
        Yingling Group
        NC State University

For internal evaluation by Citrine Informatics only.
'''

##############################################################################
#        Initialization                                                      #
##############################################################################

import numpy as np
import time

# Start the clock
t_start = time.time()
update = 1
total_points = 0

##############################################################################
#        Denoument                                                           #
##############################################################################

total_time = time.time() - t_start
print 'Success!'
print 'Excecution time: %.2f min for %i data points' % \
		(total_time/60, total_points)
