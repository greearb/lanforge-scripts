#!/usr/bin/python3

'''
NAME:
lf_renewals.py

PURPOSE:
lf_renewals.py will run "pdfgrep -r --include 'ASA*.pdf' 'ASA End Date'" to find the renews in the /ct/sales directory 

EXAMPLE:
lf_renewals.py

NOTES:
1. copy lf_renewals.py to the /ct/sales directory to run

TO DO NOTES:
6/4/2021 :  
1. Organize data to be print based on: 
     customer
     vendor
     date
2. add and delete information form the google calender

'''
import datetime
import pprint
import sys
if sys.version_info[0]  != 3:
    print("This script requires Python3")
    exit()


import os
import socket
import logging
import time
from time import sleep
import argparse
import json
import configparser
import subprocess
import csv
import shutil
import os.path
import xlsxwriter


class lf_renewals():
     def __init__(self):

          self.renewal_info = ""
          self.timeout = 10
          self.outfile = "renewal"
          self.result = ""

     def get_data(self):
          command = "pdfgrep -r --include 'ASA*.pdf' 'ASA End Date'"
          #self.renewal_info = subprocess.check_output("pdfgrep -r --include 'ASA*.pdf' 'ASA End Date'", shell=True)
          self.renewal_info = subprocess.Popen("pdfgrep -r --include 'ASA*.pdf' 'ASA End Date'", shell=True)
          print("running {}".format(command))

          # o.k. a little over kill here ,  just save data to file to help debug if something goes wrong
          if self.outfile is not None:
               stdout_log_txt = self.outfile
               stdout_log_txt = stdout_log_txt + "-{}-stdout.txt".format(test)
               stdout_log = open(stdout_log_txt, 'a')
               stderr_log_txt = self.outfile
               stderr_log_txt = stderr_log_txt + "-{}-stderr.txt".format(test)                    
               #self.logger.info("stderr_log_txt: {}".format(stderr_log_txt))
               stderr_log = open(stderr_log_txt, 'a')

          process = subprocess.Popen((command).split(' '), shell=False, stdout=stdout_log, stderr=stderr_log, universal_newlines=True)
          try:
               process.wait(timeout=int(self.timeout))
               self.result = "SUCCESS"
          except subprocess.TimeoutExpired:
               process.terminate()
               self.result = "TIMEOUT"

def main():
    # arguments
    parser = argparse.ArgumentParser(
        prog='renewals.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            renewals.py : for running scripts listed in lf_check_config.ini file
            ''',
        description='''\
renewals.py
-----------

Summary :
---------
show renewas
            ''')

    parser.add_argument('--outfile', help="--outfile <Output Generic Name>  used as base name for all files generated", default="")
    parser.add_argument('--logfile', help="--logfile <logfile Name>  logging for output of renewals script", default="renewals.log")

    args = parser.parse_args()    

    renewals = lf_renewals()
    renewals.get_data()


if __name__ == "__main__":
     main()