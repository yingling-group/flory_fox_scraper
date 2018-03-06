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
from math import ceil
import numpy as np
import pandas as pd

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
#        Functions                                                            #
###############################################################################

# Get table from a PoLyInfo URL for C-count or multiple polymer pages.
def get_pi_table(url):
    page = session_requests.get(url)
    soup = BeautifulSoup(page.content,'lxml')
    return soup.find('table',bgcolor='#808080')

# Get table of from single-polymer Tg pages
def get_Tg_table(url,page_num):
    payload = { "page" : str(page_num+1) }
    page = session_requests.get(url, params = payload)
    soup = BeautifulSoup(page.content,'lxml')
    return soup.find_all('table',bgcolor='#808080')[1]

###############################################################################
#        Polymer Classes                                                      #
###############################################################################

all_classes = []
class_abbr = {}
eb_url = "http://polymer.nims.go.jp/PoLyInfo/cgi-bin/p-easy-ptable.cgi"
eb_table = get_pi_table(eb_url)
for row in eb_table.find_all('tr'):
    first_cell = row.find('td',class_='small_border')
    if first_cell:
        all_classes.append(first_cell.find('a').contents[0])
        class_abbr[all_classes[-1]] = first_cell.find('a')['href'][-9:-5]

###############################################################################
#        Polymer Class Loop                                                   #
###############################################################################

# Initialize master lists
poly_class = []
poly_name = []
pid = []
Tg = []
Mn = []

# Loop through each polymer class
for class_i in all_classes:
    abbr_i = class_abbr[class_i]
	
	# Find C Count value with most Tg data points available
    class_url = 'http://polymer.nims.go.jp/PoLyInfo/cgi-bin/p-easy-ptable.cgi?'\
                + 'H=Thermal&vtype=points&V=cn&vpclass=' + abbr_i + '&vcn='
    class_table = get_pi_table(class_url)
    Tg_datapoints = []
    C_counts = []
    for row in class_table.find_all('tr'):
        if row.find('td',class_='small_border'):
            cells = row.find_all('td')
            C_counts.append(cells[0].find('a').contents[0])
            Tg_dps_i = cells[1].contents[0]
            if Tg_dps_i == '-':
                Tg_datapoints.append(0)
            else:
                Tg_datapoints.append(int(Tg_dps_i))
    most_Tg_dps = max(Tg_datapoints)
    tgt_C_count = C_counts[Tg_datapoints.index(most_Tg_dps)]
	
	# Find polymer ID, name, and Tg datatable url with most datapoints available
    c_count_url = 'http://polymer.nims.go.jp/PoLyInfo/cgi-bin/p-easy-ptable.'\
                + 'cgi?H=Thermal&vtype=points&V=pi&vpclass=' + abbr_i \
                + '&vcn=' + abbr_i + '-' + tgt_C_count
    c_count_table = get_pi_table(c_count_url)
    c_count_pid = []
    c_count_name = []
    Tg_datapoints = []
    Tg_urls = []
    for row in c_count_table.find_all('tr'):
        if row.find('td',class_='small_border'):
            cells = row.find_all('td')
            c_count_pid.append(cells[0].find('a')['href'][-7:])
            c_count_name.append(cells[0].find('a').contents[0])
            Tg_dps_i = cells[1].find('a')
            if Tg_dps_i:
                Tg_datapoints.append(int(Tg_dps_i.contents[0]))
                Tg_urls.append( 'http://polymer.nims.go.jp' + Tg_dps_i['href'])
            else:
                Tg_datapoints.append(0)
                Tg_urls.append('')
    most_Tg_dps = max(Tg_datapoints)
    tgt_pid = c_count_pid[Tg_datapoints.index(most_Tg_dps)]
    tgt_name = c_count_name[Tg_datapoints.index(most_Tg_dps)]
    tgt_Tg_url = Tg_urls[Tg_datapoints.index(most_Tg_dps)]
    
    # Compile list of Sample ID's of neat resin from Tg datatable
    n_pages = int(ceil(most_Tg_dps/20.))
    sid = []
    for c_page in range(n_pages):
        Tg_table = get_Tg_table(tgt_Tg_url,c_page)
        for row in Tg_table.find_all('tr'):
            if row.find('td',class_='small_border'):
                cells = row.find_all('td')
                row_sid = str(cells[1].find('a').contents[0])
                if cells[2].text == "Neat resin" and "ca" not in cells[4].text:
                    sid.append(row_sid)
    print sid
    break
	
###############################################################################
#        Denoument                                                            #
###############################################################################

total_time = time.time() - t_start
print 'Success!'
print 'Excecution time: %.2f min for %i data points' % \
		(total_time/60, total_points)