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
import sys
import re
import requests
from bs4 import BeautifulSoup
from math import ceil
import pandas as pd

# Start the clock
t_start = time.time()
total_points = 0

# Output File name:
fname = 'polyinfo'

# PoLyInfo Login Info
email = "jspeerle@ncsu.edu"
password = "0rr!S1*SAs1b"

login_info = {
        "IDToken1" : email,
        "IDToken2" : password,
        "IDToken0" : "",
}

###############################################################################
#        Functions                                                            #
###############################################################################

# Create new session and log into PoLyInfo
def polyinfo_login():
    global t_last_login
    # Create session object
    ses_req = requests.Session()

    # Login to PoLyInfo search page
    print 'Logging in to PoLyInfo...'
    login_url = "https://login-matnavi.nims.go.jp/sso/UI/Login?goto="\
            + "http%3A%2F%2Fpolymer.nims.go.jp%3A80%2FPoLyInfo%2Fcgi-bin%2Fp"\
            +"-search.cgi"
    login_result = ses_req.post(login_url, data = login_info)
    if 'Authentication failed.' in login_result.content:
        sys.exit("ERROR: PoLyInfo login unsuccessful."\
                 + " Check username and/or password!")
    print 'Login succcessful!\n'
    sys.stdout.flush()
    t_last_login = time.time()
    return ses_req

# Get table from a PoLyInfo URL for C-count or multiple polymer pages.
def get_pi_table(url):
    page = session_requests.get(url)
    soup = BeautifulSoup(page.content,'lxml')
    try:
        table = soup.find('table',bgcolor='#808080')
    except IndexError:
        print 'Unexpected format at %s. Skipping...' % (url)
        table = BeautifulSoup('','lxml')
    return table

# Get table from single-polymer Tg pages
def get_Tg_table(url,page_num):
    payload = { "page" : str(page_num+1) }
    page = session_requests.get(url, params = payload)
    soup = BeautifulSoup(page.content,'lxml')
    try:
        table = soup.find_all('table',bgcolor='#808080')[1]
    except IndexError:
        print '\tUnexpected format on page %i. Skipping...' % (page_num+1)
        table = BeautifulSoup('','lxml')
    return table

# Return list of floats contained within a string
def get_nums(s):
    num_str = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?",\
                          s)
    nums = []
    for num in num_str:
        nums.append(float(num))
    if nums == []:
        nums = [False]
    return nums

# Return the number (8 digits or less) immediately after the first instance of 
# some string within a larger string (e.g. an html page)
def val_after_str(split_s,page_s):
    val_str = page_s.split(split_s,1)[1][0:9]
    val = get_nums(val_str)[0]
    return val

###############################################################################
#        Get Polymer Classes                                                  #
###############################################################################

session_requests = polyinfo_login()

print 'Collecting polymer class list...'
sys.stdout.flush()
all_classes = []
class_abbr = {}
eb_url = "http://polymer.nims.go.jp/PoLyInfo/cgi-bin/p-easy-ptable.cgi"
eb_table = get_pi_table(eb_url)
for row in eb_table.find_all('tr'):
    first_cell = row.find('td',class_='small_border')
    if first_cell:
        all_classes.append(str(first_cell.find('a').contents[0]))
        class_abbr[all_classes[-1]] = first_cell.find('a')['href'][-9:-5]
print '%i polymer classes identified.\n' % (len(all_classes))
sys.stdout.flush()

###############################################################################
#        Polymer Class Loop                                                   #
###############################################################################

# Initialize dataframe
polyinfo_df = pd.DataFrame(data = { 'p_class' : [],
                            'class_abbr' : [],
                            'name' : [],
                            'pid' : [],
                            'sid' : [],
                            'Tg' : [],
                            'Mn': [] })

# Loop through each polymer class
for class_i in all_classes:
    print 'Identifying candidate for %s class...' % (class_i)
    abbr_i = class_abbr[class_i]

    # Re-login if necessary
    if (time.time()-t_last_login) > 7200.:
        print 'Session refresh required...'
        session_requests = polyinfo_login()

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
    c_count_names = []
    Tg_datapoints = []
    Tg_urls = []
    for row in c_count_table.find_all('tr'):
        if row.find('td',class_='small_border'):
            cells = row.find_all('td')
            c_count_pid.append(cells[0].find('a')['href'][-7:])
            c_count_names.append(cells[0].find('a').contents[0])
            Tg_dps_i = cells[1].find('a')
            if Tg_dps_i:
                Tg_datapoints.append(int(Tg_dps_i.contents[0]))
                Tg_urls.append( 'http://polymer.nims.go.jp' + Tg_dps_i['href'])
            else:
                Tg_datapoints.append(0)
                Tg_urls.append('')
    most_Tg_dps = max(Tg_datapoints)
    pid_i = str(c_count_pid[Tg_datapoints.index(most_Tg_dps)])
    poly_name_i = str(c_count_names[Tg_datapoints.index(most_Tg_dps)])
    tgt_Tg_url = Tg_urls[Tg_datapoints.index(most_Tg_dps)]
    if pid_i in polyinfo_df.pid.tolist():
        print 'Polymer %s (PID=%s) already compiled.' % (poly_name_i, pid_i)
        continue
    print( 'Candidate identified.\n' 
          '\tName: %s\n'
          '\tPID: %s\n'
          '\t%i Tg Measurements \n' 
           % (poly_name_i, pid_i, most_Tg_dps))
    sys.stdout.flush()

    # Compile list of Sample ID's of neat resin from Tg datatable
    print '\tCompiling neat resin sample IDs...'
    n_pages = int(ceil(most_Tg_dps/20.))
    sid_list = []
    for c_page in range(n_pages):
        print '\t...Page %i of %i...' % (c_page + 1, n_pages)
        sys.stdout.flush()
        Tg_table = get_Tg_table(tgt_Tg_url,c_page)
        for row in Tg_table.find_all('tr'):
            if row.find('td',class_='small_border'):
                cells = row.find_all('td')
                row_sid = str(cells[1].find('a').contents[0])
                if cells[2].text == "Neat resin" and "ca" not in cells[4].text:
                    sid_list.append(row_sid)
    sid_list = list(set(sid_list))
    print '\t%i unique neat resin samples identified.\n' % (len(sid_list))
    
    # Extract Tg and Mn from sample pages
    print '\tScanning samples...'
    sys.stdout.flush()
    n_poly_points = 0
    for sid_i in sid_list:
        samp_url = 'http://polymer.nims.go.jp/PoLyInfo/cgi-bin/ho-id-search.cgi?'\
            + 'PID=' + pid_i + '&SID=' + sid_i + '&layout=info'
        samp_page = session_requests.get(samp_url)
        samp_soup = BeautifulSoup(samp_page.content,'lxml')
        # Extract Tg
        for prop in samp_soup.find_all('li'):
            if str(prop.contents[0]) == " Glass transition temp.\n      ":
                for detail in prop.find_all('ul'):
                    Tg_str = detail.find_all('li')[0].contents[0]
                    Tg_K = get_nums(Tg_str)[-1]
                    if Tg_K and '[C]' in Tg_str:
                        Tg_K = Tg_K + 273.15
        # Extract Mn
        if 'Mn=' in samp_page.content:
            # Calculate from Molecular Weight and Mw/Mn if necessary
            if 'Mw/Mn=' in samp_page.content and 'Mw=' in samp_page.content:
                Mw = val_after_str('Mw=', samp_page.content)
                Mw_ovr_Mn = val_after_str('Mw/Mn=', samp_page.content)
                Mn_i = Mw/Mw_ovr_Mn
            # Use Mn if given, but make sure it's Mn and not Mw/Mn
            else:
                Mn_tmp = val_after_str('Mn=', samp_page.content)
                if Mn_tmp > 10.:
                    Mn_i = Mn_tmp
        # Append to lists if values found and reset
        if Mn_i and Tg_K:
            polyinfo_df = polyinfo_df.append({ 'p_class' : class_i,
                                               'class_abbr' : abbr_i,
                                               'name' : poly_name_i,
                                               'pid' : pid_i,
                                               'sid' : sid_i,
                                               'Tg' : Tg_K,
                                               'Mn': Mn_i },
                                               ignore_index = True )
            Mn_i = False
            Tg_K = False
            n_poly_points = n_poly_points + 1
    print '\tSample scan complete. %i datapoints added for %s.\n' % \
            (n_poly_points,poly_name_i)
    sys.stdout.flush()

###############################################################################
#        Denoument                                                            #
###############################################################################

# Create and print dataframe to CSV
polyinfo_df.to_csv(fname + '.csv')

total_points = len(polyinfo_df)
total_time = time.time() - t_start
print 'Success!'
print 'Excecution time: %.2f min for %i data points' % \
		(total_time/60, total_points)
