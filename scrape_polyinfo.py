#!/usr/bin/env python

'''
PoLyInfo Database Scraper - scrape_polyinfo.py

Author: James S. Peerless
        Yingling Group
        NC State University

For internal evaluation by Citrine Informatics only.
'''

###############################################################################
#        Initialization                                                       #
###############################################################################

import time
import requests
from bs4 import BeautifulSoup
import urllib2

# Start the clock
t_start = time.time()
update = 1
total_points = 0

###############################################################################
#        PoLyInfo Login                                                       #
###############################################################################

# My PoLyInfo Login Info
login_info = {
	"IDToken1" : "jspeerle@ncsu.edu",
	"IDToken2" : "0rr!S1*SAs1b",
	"IDToken0" : "",
}

# Login to PoLyInfo search page
login_url = "https://login-matnavi.nims.go.jp/sso/UI/Login?goto="\
            + "http%3A%2F%2Fpolymer.nims.go.jp%3A80%2FPoLyInfo%2Fcgi-bin%2Fp"\
            +"-search.cgi"
login_result = requests.post(
	login_url,
	data = login_info,
)
if 'Authentication failed.' in login_result.content:
	print "ERROR: PoLyInfo login unsuccessful. Check username and/or password!"

###############################################################################
#        Data Import                                                          #
###############################################################################

# Get polymer classes
ez_browse_url = "http://polymer.nims.go.jp/PoLyInfo/cgi-bin/p-easy-ptable.cgi"
ez_browse_html = urllib2.urlopen(ez_browse_url)
ez_browse = BeautifulSoup(ez_browse_html,"lxml")


###############################################################################
#        Denoument                                                            #
###############################################################################

total_time = time.time() - t_start
print 'Success!'
print 'Excecution time: %.2f min for %i data points' % \
		(total_time/60, total_points)