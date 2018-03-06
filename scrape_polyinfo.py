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

# Create session object
session_requests = requests.Session()

# Login to PoLyInfo search page
login_url = "https://login-matnavi.nims.go.jp/sso/UI/Login?goto="\
            + "http%3A%2F%2Fpolymer.nims.go.jp%3A80%2FPoLyInfo%2Fcgi-bin%2Fp"\
            +"-search.cgi"
login_result = session_requests.post(
	login_url,
	data = login_info,
)
if 'Authentication failed.' in login_result.content:
	print "ERROR: PoLyInfo login unsuccessful. Check username and/or password!"

###############################################################################
#        Data Import                                                          #
###############################################################################

# Get polymer classes and abbreviations from Easy-browse property table
poly_classes = []
class_abbr = {}
eb_url = "http://polymer.nims.go.jp/PoLyInfo/cgi-bin/p-easy-ptable.cgi"
eb = session_requests.get(eb_url)
eb_soup = BeautifulSoup(eb.content,'lxml')
eb_table = eb_soup.find('table',bgcolor='#808080')
for row in eb_table.find_all('tr'):
	first_cell = row.find('td',class_='small_border')
	if first_cell:
		poly_classes.append(first_cell.find('a').contents[0])
		class_abbr[poly_classes[-1]] = first_cell.find('a')['href'][-9:-5]

###############################################################################
#        Denoument                                                            #
###############################################################################

total_time = time.time() - t_start
print 'Success!'
print 'Excecution time: %.2f min for %i data points' % \
		(total_time/60, total_points)