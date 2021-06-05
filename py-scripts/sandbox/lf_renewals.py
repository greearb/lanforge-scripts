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
          self.stdout_log_txt = ""
          self.stdout_log = ""
          self.stderr_log_txt = ""
          self.stderr_log = ""

     def get_data(self):

          # o.k. a little over kill here ,  just save data to file to help debug if something goes wrong
          if self.outfile is not None:
               self.stdout_log_txt = self.outfile
               self.stdout_log_txt = self.stdout_log_txt + "-{}-stdout.txt".format("test")
               self.stdout_log = open(self.stdout_log_txt, 'a')
               self.stderr_log_txt = self.outfile
               self.stderr_log_txt = self.stderr_log_txt + "-{}-stderr.txt".format("test")                    
               #self.logger.info("stderr_log_txt: {}".format(stderr_log_txt))
               self.stderr_log = open(self.stderr_log_txt, 'a')

               print("Names {} {}".format(self.stdout_log.name, self.stderr_log.name))

          command = "pdfgrep -r --include 'ASA*.pdf' 'ASA End Date'"
          print("running {}".format(command))

          process = subprocess.Popen(['pdfgrep','-r','--include','ASA*.pdf','ASA End Date'], shell=False, stdout=self.stdout_log, stderr=self.stderr_log, universal_newlines=True)
          try:
               process.wait(timeout=int(self.timeout))
               self.result = "SUCCESS"
          except subprocess.TimeoutExpired:
               process.terminate()
               self.result = "TIMEOUT"

          self.stdout_log.close()
          self.stderr_log.close()

          return self.stdout_log_txt

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
    output_file = renewals.get_data()

    print("output file: {}".format(str(output_file)))
    print("END lf_renewals.py")


if __name__ == "__main__":
     main()