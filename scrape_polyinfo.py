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
from lxml import html

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
	"IDToken2" : "0rr!S1*SAa1b",
	"IDToken0" : "",
	"goto" : "aHR0cDovL3BvbHltZXIubmltcy5nby5qcDo4MC9Qb0x5SW5mby8=",
	"SunQueryParamsString" : "",
	"encoded" : "true",
	"gx_charset" : "UTF-8"
}

session_requests = requests.session()
login_url = "https://login-matnavi.nims.go.jp/sso/UI/Login?goto="\
            + "http%3A%2F%2Fpolymer.nims.go.jp%3A80%2FPoLyInfo%2F"
result = session_requests.get(login_url)
tree = html.fromstring(result.text)

result = session_requests.post(
	login_url,
	data = payload,
	headers = dict(referer=login_url)
)

# Test login by accessing search page
url = 'http://polymer.nims.go.jp/PoLyInfo/cgi-bin/p-search.cgi'
result = session_requests.get(
	url,
	headers = dict(referer = url)
)

print result

tree = html.fromstring(result.content)

if result.ok == False:
	print "PoLyInfo Login Error. Check username/password!"

###############################################################################
#        Denoument                                                            #
###############################################################################

total_time = time.time() - t_start
print 'Success!'
print 'Excecution time: %.2f min for %i data points' % \
		(total_time/60, total_points)