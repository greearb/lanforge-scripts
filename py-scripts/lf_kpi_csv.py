#!/usr/bin/env python3
'''
NAME: lf_kpi_csv.py

PURPOSE:
Common Library for generating kpi csv for LANforge output
KPI - Key Performance Indicators

SETUP:
/lanforge/html-reports directory needs to be present or output generated in local file

EXAMPLE:
see: run any chamberview test to see what a generated kpi.csv

COPYWRITE
    Copyright 2021 Candela Technologies Inc
    License: Free to distribute and modify. LANforge systems must be licensed.

INCLUDE_IN_README
'''

import pandas as pd


# this layout may need to change
'''
kpi.csv : specific file that is used for the database, dashboard and blog post
A blank entry is a valid entry in some cases. 

    Date: date of run 
    test-rig : testbed that the tests are run on for example ct_us_001
    test-tag : test specific information to differenciate the test,  LANforge radios used, security modes (wpa2 , open)
    dut-hw-version : hardware version of the device under test
    dut-sw-version : software version of the device under test
    dut-model-num : model number / name of the device under test
    test-priority : test-priority is arbitrary number, choosing under 95 means it goes down at bottom of blog report, and higher priority goes at top.
    test-id : script or test name ,  AP Auto, wifi capacity, data plane, dfs
    short-description : short description of the test
    pass/fail : set blank for performance tests
    numeric-score : this is the value for the y-axis (x-axis is a timestamp),  numeric value of what was measured
    test-details : what was measured in the numeric-score,  e.g. bits per second, bytes per second, upload speed, minimum cx time (ms)
    Units : units used for the numeric-scort
    Graph-Group - For the lf_qa.py dashboard

'''
class lf_kpi_csv:
    def __init__(self,
                _kpi_headers = ['Date','test-rig','test-tag','dut-hw-version','dut-sw-version','dut-model-num',
                                'test-priority','test-id','short-description','pass/fail','numberic-score'
                                'test details','Units','Graph-Group','Subtest-Pass','Subtest-Fail'],
                _kpi_file='kpi.csv' #Currently this is the only file name accepted
                ):
        self.kpi_headers = _kpi_headers
        self.kpi_rows = ""
        self.kpi_filename = _kpi_file

    def generate_kpi_csv(self):
        pass

def main():
    test = lf_kpi_csv()
    test.generate_kpi_csv()

if __name__ == "__main__":
    main()    
