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
update = 1
total_points = 0

# Output File name:
fname = 'flory_fox'

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
print 'Logging in to PoLyInfo...'
login_url = "https://login-matnavi.nims.go.jp/sso/UI/Login?goto="\
            + "http%3A%2F%2Fpolymer.nims.go.jp%3A80%2FPoLyInfo%2Fcgi-bin%2Fp"\
            +"-search.cgi"
login_result = session_requests.post(
        login_url,
        data = login_info,
)
if 'Authentication failed.' in login_result.content:
    sys.exit("ERROR: PoLyInfo login unsuccessful."\
             + " Check username and/or password!")
print 'Login succcessful!\n'

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
    val_str = page_s.split(split_s,1)[1][0:6]
    val = get_nums(val_str)[0]
    return val

###############################################################################
#        Polymer Classes                                                      #
###############################################################################

print 'Collecting polymer class list...'
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

###############################################################################
#        Polymer Class Loop                                                   #
###############################################################################

# Initialize master lists
poly_class = []
poly_class_abbr = []
poly_name = []
pid = []
sid = []
Tg = []
Mn = []

# Loop through each polymer class
for class_i in all_classes:
    print 'Identifying candidate for %s class...' % (class_i)
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
    pid_i = c_count_pid[Tg_datapoints.index(most_Tg_dps)]
    poly_name_i = str(c_count_names[Tg_datapoints.index(most_Tg_dps)])
    tgt_Tg_url = Tg_urls[Tg_datapoints.index(most_Tg_dps)]
    if pid_i in pid:
        print 'Polymer %s (PID=%s) already compiled.' % (poly_name_i, pid_i)
        break
    print( 'Candidate identified.\n' 
          '\tName: %s\n'
          '\tPID: %s\n'
          '\t%i Tg Measurements \n' 
           % (poly_name_i, pid_i, most_Tg_dps))
    
    # Compile list of Sample ID's of neat resin from Tg datatable
    print '\tCompiling neat resin sample IDs...'
    n_pages = int(ceil(most_Tg_dps/20.))
    sid_list = ['37436-1-1-1', '33530-2-1-1', '11076-1-1-1', '10997-2-1-1', '14014-3-1-1', '24883-1-1-1', '74574-6-1-1', '22144-2-1-2', '24883-1-2-1', '75097-1-1-1', '37911-5-1-1', '70722-5-1-1', '37911-5-1-2', '13619-22-1-1', '70722-4-1-1', '70599-1-1-1', '74574-6-2-1', '33891-3-1-1', '37280-2-1-1', '12993-4-1-1', '21411-3-1-1', '31062-2-1-1', '29374-3-1-1', '70012-1-16-1', '70596-2-6-1', '70596-2-1-1', '22085-1-1-1', '37490-3-1-1', '10728-1-1-1', '23403-11-1-1', '23112-1-1-1', '36910-2-1-1', '22144-3-1-2', '10728-1-2-1', '70724-1-1-1', '70594-5-1-1', '21416-1-1-1', '22144-2-1-1', '12413-1-1-1', '31259-1-1-1', '22973-3-1-1', '70008-4-1-1', '30749-3-1-1', '10728-1-5-1', '75080-11-1-1', '22973-2-1-1', '70584-1-1-1', '21278-2-1-1', '13731-1-1-1', '25930-12-1-1', '20613-1-1-1', '41449-1-1-1', '22787-2-1-1', '11076-2-1-1', '70596-2-5-1', '14217-5-1-1', '37844-2-1-1', '70012-1-19-1', '70594-3-1-1', '40998-2-1-1', '70599-6-1-1', '13284-1-1-1', '71341-1-1-1', '34710-3-1-1', '33891-2-1-1', '10997-1-1-1', '26589-2-1-1', '10038-2-1-2', '75039-1-2-1', '31257-1-1-3', '34190-3-1-1', '70599-5-1-1', '21758-1-1-1', '21758-1-1-2', '70599-4-1-1', '29507-6-1-1', '73610-2-1-1', '37824-2-1-1', '22848-1-1-1', '21411-4-1-1', '79174-1-1-1', '21340-8-1-1', '14199-16-1-1', '40509-1-1-1', '70010-3-1-1', '10728-1-4-1', '26373-2-1-1', '70596-3-1-1', '33891-4-1-1', '34780-1-1-1', '27791-1-1-1', '10384-2-1-1', '30170-1-3-1', '74574-6-4-1', '75039-1-1-1', '34229-2-1-1', '20791-2-1-1', '26205-2-1-1', '70596-2-2-1', '70012-1-14-1', '70596-3-3-1', '70012-1-12-1', '21689-2-1-1', '14316-1-1-1', '70596-1-6-1', '23400-21-1-1', '30603-6-1-1', '70012-1-11-1', '27383-5-1-1', '10728-1-3-1', '20087-2-1-1', '11429-1-1-1', '10394-1-1-1', '14199-11-1-1', '27370-1-1-1', '27370-1-1-3', '27370-1-1-2', '27370-1-1-4', '36570-1-1-1', '37437-2-1-2', '37437-2-1-1', '11473-2-1-1', '70596-1-5-1', '70596-1-2-1', '70560-1-1-1', '70560-1-1-2', '30831-8-1-1', '74302-3-1-1', '70012-1-18-1', '30222-2-1-1', '70596-1-1-1', '70596-2-7-1', '27237-3-1-1', '70778-4-1-1', '10952-1-1-1', '22978-1-1-1', '11293-2-1-1', '70012-1-15-1', '34297-2-1-1', '13986-1-1-1', '70012-1-17-1', '41233-12-1-1', '75399-21-1-1', '34442-3-1-1', '13225-3-1-1', '70570-1-1-1', '11809-2-1-1', '11809-2-1-2', '75237-1-1-1', '70007-5-1-1', '70598-1-1-1', '30357-1-1-1', '30357-1-1-2', '10351-1-1-1', '21510-7-1-1', '14609-3-1-1', '70544-1-1-1', '12899-5-1-1', '20375-7-1-1', '27383-6-1-1', '12088-2-1-1', '14440-1-1-1', '22324-1-3-1', '29384-2-1-1', '29384-2-1-2', '33891-1-1-1', '12544-2-1-1', '70598-2-1-1', '22342-1-1-1', '29808-1-1-1', '75367-2-1-1', '22324-1-4-1', '75039-1-3-1', '11244-1-5-1', '70012-1-13-1', '12370-5-1-1', '33396-1-1-1', '70596-1-7-1', '30170-2-2-1', '22003-1-1-1', '23843-2-1-1', '70596-1-4-1', '31541-1-1-1', '11244-1-6-1', '70544-3-1-1', '22324-1-7-1', '13225-1-1-1', '11293-1-1-1', '36879-2-1-1', '11990-6-1-1', '30231-3-1-1', '38396-1-1-3', '20375-1-1-1', '29219-4-1-2', '23700-1-2-2', '70596-2-8-1', '70592-1-1-1', '23527-1-1-1', '26070-7-1-1', '75159-2-1-1', '70520-6-1-1', '31541-3-1-1', '38102-1-1-1', '34190-1-1-1', '12128-1-1-1', '30170-2-6-1', '30170-2-1-1', '22176-1-1-1', '70596-2-3-1', '70012-1-4-1', '11244-1-2-1', '11293-3-1-1', '38982-1-1-1', '33664-2-2-1', '34190-4-1-1', '13873-4-1-1', '75019-1-1-1', '70007-8-1-1', '41557-1-4-1', '33563-1-1-1', '79169-2-1-1', '70012-1-8-1', '01285-5-1-1', '70778-3-1-1', '13274-1-1-1', '74278-14-1-1', '74210-5-1-1', '25815-1-1-1', '11763-3-1-1', '70594-1-1-1', '41557-1-3-1', '14217-8-1-1', '75080-8-1-1', '12851-5-1-1', '30453-1-1-1', '70012-1-3-1', '70722-2-1-1', '75054-8-1-1', '31382-1-1-1', '40296-1-1-1', '33664-2-1-1', '25565-2-1-1', '13621-1-1-2', '70569-1-1-1', '33664-2-3-1', '11244-1-4-1', '34190-1-2-1', '11572-1-1-1', '23875-1-1-1', '70778-2-1-1', '11244-1-7-1', '36465-10-1-1', '30720-1-1-7', '70592-2-1-1', '22312-4-1-1', '22312-4-6-1', '30720-1-1-8', '41557-2-4-1', '74302-5-1-1', '30170-2-4-1', '34038-1-1-2', '74302-1-1-1', '23100-2-1-1', '30170-2-7-1', '22324-1-1-1', '20049-1-1-1', '36598-5-1-2', '36598-5-1-1', '13619-25-1-1', '28938-1-1-1', '20110-1-1-3', '11617-2-1-1', '22312-4-5-1', '75080-5-1-1', '21672-1-1-1', '23055-1-1-1', '10652-5-1-1', '70012-1-6-1', '12993-3-1-1', '21644-1-1-1', '20643-5-1-1', '70012-1-5-1', '11244-1-3-1', '70594-6-1-1', '14267-1-1-1', '21427-8-1-1', '22312-4-2-1', '30170-2-3-1', '22170-1-1-1', '41486-1-1-1', '23700-1-1-1', '70515-2-1-1', '23700-1-1-3', '23700-1-1-4', '23700-1-1-5', '23700-1-1-6', '23700-1-1-7', '40147-2-1-1', '23017-2-1-2', '75400-1-1-1', '75054-5-1-1', '31004-2-1-1', '70599-2-1-1', '38109-2-1-1', '41205-1-1-1', '30170-2-8-1', '23700-1-1-2', '41557-1-2-1', '00402-7-1-1', '41557-1-1-1', '20735-1-1-1', '22775-2-1-1', '13258-5-1-1', '22163-1-1-1', '13258-5-1-2', '70018-2-1-1', '26918-1-4-1', '33891-5-1-1', '29970-2-1-1', '30707-1-1-1', '22855-5-1-1', '70012-1-2-1', '70778-1-1-1', '37338-1-1-1', '70012-1-1-1', '14775-7-1-1', '74452-8-1-1', '70594-4-1-1', '34610-2-1-1', '26918-1-3-1', '23112-1-2-1', '30336-5-1-1', '70012-1-9-1', '70209-3-1-1', '75141-6-1-1', '14217-12-1-1', '72419-1-1-1', '00370-6-1-1', '24773-3-1-1', '22312-4-7-1', '21811-3-1-1', '75365-5-1-1', '26008-1-1-1', '12833-2-1-1', '75060-3-1-1', '75159-5-1-1', '26918-1-7-1', '70029-15-1-1', '33411-1-1-1', '10384-4-1-1', '12899-1-1-1', '26376-1-1-1', '30697-2-1-2', '30697-2-1-1', '70579-2-4-1', '22312-4-4-1', '70592-6-1-1', '75037-7-1-1', '90244-10-1-1', '40616-1-2-1', '24940-1-1-1', '29384-1-1-2', '29384-1-1-1', '12993-9-1-1', '33774-1-1-1', '26918-1-8-1', '25491-3-1-1', '40616-1-1-1', '01285-2-1-1', '22312-4-3-1', '78022-1-1-1', '14987-1-1-2', '10312-2-1-1', '23700-1-2-3', '70237-16-1-1', '23700-1-2-1', '23700-1-2-4', '31259-2-1-3', '31259-2-1-2', '31259-2-1-1', '20547-1-1-1', '70596-2-4-1', '41557-2-1-1', '22978-2-2-1', '29530-1-1-1', '41557-2-2-1', '26998-1-1-1', '25216-10-1-1', '10806-1-1-1', '22973-1-1-1', '11273-2-1-1', '22324-1-10-1', '23165-4-1-1', '39152-3-1-1', '14199-13-1-1', '12833-3-1-1', '70012-1-21-1', '11540-2-1-1', '70568-1-1-1', '12899-7-1-1', '11998-1-1-1', '29384-3-1-2', '22978-2-1-1', '30364-1-1-1', '31382-5-1-1', '20213-1-1-1', '26918-1-1-1', '75377-3-1-1', '22978-3-1-1', '28873-1-1-1', '25913-2-1-1', '27081-8-1-1', '39833-1-1-1', '26918-1-6-1', '12505-1-1-4', '21075-1-1-1', '12128-2-1-1', '26376-2-1-1', '79169-1-1-1', '70724-3-1-1', '33858-1-1-1', '75010-2-1-1', '31259-1-1-3', '34743-3-1-1', '70012-1-20-1', '21903-2-1-1', '26918-1-5-1', '30453-2-1-1', '70237-15-1-1', '12005-1-1-1', '13487-26-1-1', '26918-1-9-1', '13208-2-1-1', '20375-4-1-1', '10360-3-1-1', '73033-1-1-1', '70579-2-3-1', '75145-2-1-1', '31526-4-1-1', '38681-2-1-1', '12899-4-1-1', '70724-2-1-1', '11824-3-1-1', '70012-1-10-1', '70594-2-1-1', '13819-1-1-1', '15256-1-1-1', '79169-3-1-1', '30170-1-5-1', '30170-1-2-1', '21979-3-1-1', '13621-1-1-1', '11414-1-1-2', '01445-1-1-1', '12213-1-1-1', '70592-5-1-1', '11429-4-1-1', '41391-1-1-9', '75060-2-1-1', '21411-1-1-1', '70579-2-5-1', '79172-1-1-1', '70596-4-8-1', '30170-1-1-1', '70596-4-7-1', '11824-1-1-1', '39498-1-1-1', '75080-2-1-1', '41217-4-1-1', '70012-1-7-1', '37957-1-1-1', '12553-5-1-2', '30170-1-6-1', '36563-1-1-1', '10007-4-1-1', '70596-4-4-1', '29384-3-1-1', '70596-4-3-1', '70596-5-1-1', '13487-17-1-1', '70596-5-6-1', '11262-6-1-1', '30043-1-1-1', '36365-2-1-1', '11244-1-1-1', '22342-3-1-1', '70579-2-1-1', '70579-2-2-1', '70596-5-5-1', '20276-1-1-1', '36535-2-1-1', '25913-1-1-1', '70596-3-2-1', '74302-2-1-1', '22182-1-1-1', '30170-1-8-1', '38935-10-1-1', '21411-2-1-1', '70596-5-2-1', '30170-2-5-1', '37436-2-1-1', '30788-1-1-1', '75354-7-1-1', '74303-1-1-1', '29813-3-1-1', '73611-1-1-1', '22913-1-1-1', '27081-1-1-1', '40913-1-1-1', '22913-1-2-1', '13487-8-1-1', '74311-2-1-1', '70721-11-1-1', '13544-2-1-1', '70722-3-1-1', '26918-1-2-1', '26040-1-1-1', '33530-3-1-1', '30598-1-1-1', '75327-2-1-1', '25231-1-1-1', '30764-1-1-1', '70596-4-6-1', '20761-6-1-1', '74302-4-1-1', '70596-4-5-1', '12846-1-1-1', '29219-4-1-1', '30603-4-1-1', '11429-3-1-1', '29704-1-1-1', '70544-2-1-1', '13551-2-1-1', '30170-1-7-1', '13619-1-1-1', '22144-3-1-1', '37436-2-2-1', '30170-1-4-1', '79172-2-1-1', '36535-1-1-1', '30695-1-1-1', '22113-2-1-1', '78566-2-1-1', '36752-1-1-1', '00402-31-1-1', '70596-4-2-1', '14591-3-1-1', '70587-1-1-1', '22085-2-1-1', '70596-5-7-1', '70596-4-1-1', '41557-2-3-1', '70722-1-1-1', '37117-1-1-1', '37882-1-1-1', '38586-2-1-1', '70516-7-1-1', '70596-4-9-1', '70596-1-3-1', '40969-2-1-1', '75264-1-1-1', '23372-1-1-1', '70596-5-4-1', '11429-2-1-1', '36598-1-1-2', '36598-1-1-1', '70590-1-1-1', '21758-2-1-2', '21758-2-1-1', '70828-1-1-1', '00128-1-1-1', '10728-1-6-1', '25602-4-1-1', '70599-3-1-1', '70596-5-3-1', '70026-1-1-1', '78022-4-1-1', '01216-1-1-1', '11938-6-1-1', '70721-12-1-1', '11066-2-1-1', '33705-2-1-1', '22144-1-1-1', '22144-1-1-2', '37436-3-1-1', '30493-1-1-1', '10384-3-1-1', '21047-3-1-1', '14825-1-1-1', '37509-1-1-1', '26900-1-1-1']
    '''sid_list = []
    for c_page in range(n_pages):
        print '\t...Page %i of %i...' % (c_page + 1, n_pages)
        Tg_table = get_Tg_table(tgt_Tg_url,c_page)
        for row in Tg_table.find_all('tr'):
            if row.find('td',class_='small_border'):
                cells = row.find_all('td')
                row_sid = str(cells[1].find('a').contents[0])
                if cells[2].text == "Neat resin" and "ca" not in cells[4].text:
                    sid_list.append(row_sid)
    sid_list = list(set(sid_list))'''
    print '\t%i unique neat resin samples identified.\n' % (len(sid_list))
    
    # Extract Tg and Mn from sample pages
    print '\tScanning samples...'
    n_poly_points = 0
    for sid_i in sid_list:
        url = 'http://polymer.nims.go.jp/PoLyInfo/cgi-bin/ho-id-search.cgi?'\
            + 'PID=' + pid_i + '&SID=' + sid_i + '&layout=info'
        page = session_requests.get(url)
        soup = BeautifulSoup(page.content,'lxml')
        # Extract Tg
        for prop in soup.find_all('li'):
            if str(prop.contents[0]) == " Glass transition temp.\n      ":
                for detail in prop.find_all('ul'):
                    Tg_str = detail.find_all('li')[0].contents[0]
                    Tg_K = get_nums(Tg_str)[-1]
                    if Tg_K and '[C]' in Tg_str:
                        Tg_K = Tg_K + 273.15
        # Find Mn
        if 'Mn=' in page.content:
            # Calculate from Molecular Weight and Mw/Mn if necessary
            if 'Mw/Mn=' in page.content and 'Mw=' in page.content:
                Mw = val_after_str('Mw=', page.content)
                Mw_ovr_Mn = val_after_str('Mw/Mn=', page.content)
                Mn_i = Mw/Mw_ovr_Mn
            # Use Mn if given, but make sure it's Mn and not Mw/Mn
            else:
                Mn_tmp = val_after_str('Mn=', page.content)
                if Mn_tmp > 10.:
                    Mn_i = Mn_tmp
        # Append to lists if values found
        if Mn_i and Tg_K:
            poly_class.append(class_i)
            poly_class_abbr.append(abbr_i)
            poly_name.append(poly_name_i)
            pid.append(pid_i)
            sid.append(sid_i)
            Tg.append(Tg_K)
            Mn.append(Mn_i)
            Mn_i = False
            Tg_K = False
            n_poly_points = n_poly_points + 1
    print '\tSample scan complete. %i datapoints added for %s.\n' % \
            (n_poly_points,poly_name_i)
    break 

###############################################################################
#        Denoument                                                            #
###############################################################################

# Create and print dataframe to CSV
polyinfo_dat = {'Class': poly_class, \
                'Class Abbr.': poly_class_abbr, \
                'Name': poly_name, \
                'PID': pid, \
                'SID': sid, \
                'Tg (K)': Tg, \
                'Mn (g/mol)': Mn }
polyinfo_df = pd.DataFrame(data=polyinfo_dat)
polyinfo_df.to_csv(fname + '.csv')

total_points = len(Mn)
total_time = time.time() - t_start
print 'Success!'
print 'Excecution time: %.2f min for %i data points' % \
		(total_time/60, total_points)