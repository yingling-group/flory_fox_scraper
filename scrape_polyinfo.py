#!/usr/bin/env python

'''
PolyInfo Database Scraper - scrape_polyinfo.py

Author: James S. Peerless
        Yingling Group
        NC State University

For internal evaluation by Citrine Informatics only.
'''

###############################################################################
#        Initialization                                                       #
###############################################################################

import numpy as np
import time
import requests

# Start the clock
t_start = time.time()
update = 1
total_points = 0

###############################################################################
#        PolyInfo Login                                                       #
###############################################################################

# My PolyInfo Login Info
payload = {
	"IDToken1" : "jspeerle@ncsu.edu",
	"IDToken2" : "0rr!S1*SAs1b",
	"IDToken0" : "",
}

session_requests = requests.session()
login_url = "https://login-matnavi.nims.go.jp/sso/UI/Login?goto="\
            + "http%3A%2F%2Fpolymer.nims.go.jp%3A80%2FPoLyInfo%2Fcgi-bin%2Fp-search.cgi"

result = requests.post(
	login_url,
	data = payload,
)

if 'Authentication failed.' in result.content:
	print "ERROR: PoLyInfo login unsuccessful. Check username and/or password!"

###############################################################################
#        Denoument                                                            #
###############################################################################

total_time = time.time() - t_start
print 'Success!'
print 'Excecution time: %.2f min for %i data points' % \
		(total_time/60, total_points)