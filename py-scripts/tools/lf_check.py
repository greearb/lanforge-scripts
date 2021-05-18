#!/usr/bin/python3

'''
NAME:
lf_check.py

PURPOSE:
Configuration for lf_check.py , runs various tests

EXAMPLE:
lf_check.py

NOTES:

'''

import sys
if sys.version_info[0]  != 3:
    print("This script requires Python3")
    exit()


import os
import pexpect
import logging
import time
from time import sleep
import argparse
import json
from json import load
import configparser
from pprint import *
import subprocess
import re
import csv

# lf_report is from the parent of the current file
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path,os.pardir))
sys.path.insert(0, parent_dir_path)

#sys.path.append('../')
from lf_report import lf_report
sys.path.append('/')

CONFIG_FILE = os.getcwd() + '/lf_check_config.ini'    
RUN_CONDITION = 'ENABLE'

# setup logging FORMAT
FORMAT = '%(asctime)s %(name)s %(levelname)s: %(message)s'

class lf_check():
    def __init__(self,
                _csv_results,
                _outfile):
        self.lf_mgr_ip = ""
        self.lf_mgr_port = "" 
        self.radio_dict = {}
        self.test_dict = {}
        path_parent = os.path.dirname(os.getcwd())
        os.chdir(path_parent)
        self.scripts_wd = os.getcwd()
        self.results = ""
        self.outfile = _outfile
        self.test_result = "Failure"
        self.results_col_titles = ["Test","Command","Result","STDOUT","STDERR"]
        self.html_results = ""
        self.background_green = "background-color:green"
        self.background_red = "background-color:red"
        self.background_purple = "background-color:purple"

        self.http_test_ip = ""
        self.ftp_test_ip = ""
        self.test_ip = ""

        self.radio_lf = ""
        self.ssdi = ""
        self.ssid_pw = ""
        self.security = ""
        self.num_sta = ""
        self.col_names = ""
        self.upstream_port = ""

        self.csv_results = _csv_results
        self.csv_results_file = ""
        self.csv_results_writer = ""
        self.csv_results_column_headers = ""
        self.logger = logging.getLogger(__name__)

    def get_csv_results(self):
        return self.csv_file.name

    def start_csv_results(self):
        print("self.csv_results")
        self.csv_results_file = open(self.csv_results, "w")
        self.csv_results_writer = csv.writer(self.csv_results_file, delimiter=",")
        self.csv_results_column_headers = ['Test','Command','Result','STDOUT','STDERR'] 
        self.csv_results_writer.writerow(self.csv_results_column_headers)
        self.csv_results_file.flush()

    def get_html_results(self):
        return self.html_results

    def start_html_results(self):
        self.html_results += """
                <table border="1" class="dataframe">
                    <thead>
                        <tr style="text-align: left;">
                          <th>Test</th>
                          <th>Command</th>
                          <th>Result</th>
                          <th>STDOUT</th>
                          <th>STDERR</th>
                        </tr>
                      </thead>
                      <tbody>
                      """

    def finish_html_results(self):
        self.html_results += """
                    </tbody>
                </table>
                <br>
                <br>
                <br>
                """

    # Functions in this section are/can be overridden by descendants
    def read_config_contents(self):
        self.logger.info("read_config_contents {}".format(CONFIG_FILE))
        config_file = configparser.ConfigParser()
        success = True
        success = config_file.read(CONFIG_FILE)
        self.logger.info("logger worked")

        if 'LF_MGR' in config_file.sections():
            section = config_file['LF_MGR']
            self.lf_mgr_ip = section['LF_MGR_IP']
            self.lf_mgr_port = section['LF_MGR_PORT']
            self.logger.info("lf_mgr_ip {}".format(self.lf_mgr_ip))
            self.logger.info("lf_mgr_port {}".format(self.lf_mgr_port))

        if 'TEST_NETWORK' in config_file.sections():
            section = config_file['TEST_NETWORK']
            self.http_test_ip = section['HTTP_TEST_IP']
            self.logger.info("http_test_ip {}".format(self.http_test_ip))
            self.ftp_test_ip = section['FTP_TEST_IP']
            self.logger.info("ftp_test_ip {}".format(self.ftp_test_ip))
            self.test_ip = section['TEST_IP']
            self.logger.info("test_ip {}".format(self.test_ip))

        if 'TEST_GENERIC' in config_file.sections():
            section = config_file['TEST_GENERIC']
            self.radio_lf = section['RADIO_USED']
            self.logger.info("radio_lf {}".format(self.radio_lf))
            self.ssid = section['SSID_USED']
            self.logger.info("ssid {}".format(self.ssid))
            self.ssid_pw = section['SSID_PW_USED']
            self.logger.info("ssid_pw {}".format(self.ssid_pw))
            self.security = section['SECURITY_USED']
            self.logger.info("secruity {}".format(self.security))
            self.num_sta = section['NUM_STA']
            self.logger.info("num_sta {}".format(self.num_sta))
            self.col_names = section['COL_NAMES']
            self.logger.info("col_names {}".format(self.col_names))
            self.upstream_port = section['UPSTREAM_PORT']
            self.logger.info("upstream_port {}".format(self.upstream_port))


        if 'RADIO_DICTIONARY' in config_file.sections():
            section = config_file['RADIO_DICTIONARY']
            self.radio_dict = json.loads(section.get('RADIO_DICT', self.radio_dict))
            self.logger.info("self.radio_dict {}".format(self.radio_dict))

        if 'TEST_DICTIONARY' in config_file.sections():
            section = config_file['TEST_DICTIONARY']
            # for json replace the \n and \r they are invalid json characters, allows for multiple line args 
            self.test_dict = json.loads(section.get('TEST_DICT', self.test_dict).replace('\n',' ').replace('\r',' '))
            #self.logger.info("test_dict {}".format(self.test_dict))


    def load_factory_default_db(self):
        #self.logger.info("file_wd {}".format(self.scripts_wd))
        try:
            os.chdir(self.scripts_wd)
            #self.logger.info("Current Working Directory {}".format(os.getcwd()))
        except:
            self.logger.info("failed to change to {}".format(self.scripts_wd))

        # no spaces after FACTORY_DFLT
        command = "./{} {}".format("scenario.py", "--load FACTORY_DFLT")
        process = subprocess.Popen((command).split(' '), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        # wait for the process to terminate
        out, err = process.communicate()
        errcode = process.returncode

    # Not currently used
    def load_blank_db(self):
        #self.logger.info("file_wd {}".format(self.scripts_wd))
        try:
            os.chdir(self.scripts_wd)
            #self.logger.info("Current Working Directory {}".format(os.getcwd()))
        except:
            self.logger.info("failed to change to {}".format(self.scripts_wd))

        # no spaces after FACTORY_DFLT
        command = "./{} {}".format("scenario.py", "--load BLANK")
        process = subprocess.Popen((command).split(' '), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)


    def run_script_test(self):
        self.start_html_results() 
        self.start_csv_results()

        for test in self.test_dict:
            if self.test_dict[test]['enabled'] == "FALSE":
                self.logger.info("test: {}  skipped".format(test))
            # load the default database 
            elif self.test_dict[test]['enabled'] == "TRUE":
                # Make the command replace ment a separate method call.
                # loop through radios
                for radio in self.radio_dict:
                    # Replace RADIO, SSID, PASSWD, SECURITY with actual config values (e.g. RADIO_0_CFG to values)
                    # not "KEY" is just a word to refer to the RADIO define (e.g. RADIO_0_CFG) to get the vlaues
                    # --num_stations needs to be int not string (no double quotes)
                    if self.radio_dict[radio]["KEY"] in self.test_dict[test]['args']:
                        self.test_dict[test]['args'] = self.test_dict[test]['args'].replace(self.radio_dict[radio]["KEY"],'--radio "{}" --ssid "{}" --passwd "{}" --security "{}" --num_stations {}'
                        .format(self.radio_dict[radio]['RADIO'],self.radio_dict[radio]['SSID'],self.radio_dict[radio]['PASSWD'],self.radio_dict[radio]['SECURITY'],self.radio_dict[radio]['STATIONS']))

                if 'HTTP_TEST_IP' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('HTTP_TEST_IP',self.http_test_ip)
                if 'FTP_TEST_IP' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('FTP_TEST_IP',self.ftp_test_ip)
                if 'TEST_IP' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('TEST_IP',self.test_ip)

                if 'RADIO_USED' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('RADIO_USED',self.radio_lf)
                if 'SSID_USED' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('SSID_USED',self.ssid)
                if 'SSID_PW_USED' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('SSID_PW_USED',self.ssid_pw)
                if 'SECURITY_USED' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('SECURITY_USED',self.security)
                if 'NUM_STA' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('NUM_STA',self.num_sta)
                if 'COL_NAMES' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('COL_NAMES',self.col_names)
                if 'UPSTREAM_PORT' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('UPSTREAM_PORT',self.col_names)


                self.load_factory_default_db()
                sleep(5) # the sleep is to allow for the database to stablize

                try:
                    os.chdir(self.scripts_wd)
                    #self.logger.info("Current Working Directory {}".format(os.getcwd()))
                except:
                    self.logger.info("failed to change to {}".format(self.scripts_wd))
                cmd_args = "{}".format(self.test_dict[test]['args'])
                command = "./{} {}".format(self.test_dict[test]['command'], cmd_args)
                self.logger.info("command: {}".format(command))
                self.logger.info("cmd_args {}".format(cmd_args))

                if self.outfile is not None:
                    stdout_log_txt = self.outfile
                    stdout_log_txt = stdout_log_txt + "-{}-stdout.txt".format(test)
                    #self.logger.info("stdout_log_txt: {}".format(stdout_log_txt))
                    stdout_log = open(stdout_log_txt, 'a')
                    stderr_log_txt = self.outfile
                    stderr_log_txt = stderr_log_txt + "-{}-stderr.txt".format(test)                    
                    #self.logger.info("stderr_log_txt: {}".format(stderr_log_txt))
                    stderr_log = open(stderr_log_txt, 'a')

                process = subprocess.Popen((command).split(' '), shell=False, stdout=stdout_log, stderr=stderr_log, universal_newlines=True)
                
                try:
                    #out, err = process.communicate()
                    process.wait(timeout=120)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    self.test_result = "TIMEOUT"

                    #if err:
                    #    self.logger.info("command Test timed out: {}".format(command))

                #self.logger.info(stderr_log_txt)
                if(self.test_result != "TIMEOUT"):
                    stderr_log_size = os.path.getsize(stderr_log_txt)
                    if stderr_log_size > 0 :
                        self.logger.info("File: {} is not empty: {}".format(stderr_log_txt,str(stderr_log_size)))

                        self.test_result = "Failure"
                        background = self.background_red
                    else:
                        self.logger.info("File: {} is empty: {}".format(stderr_log_txt,str(stderr_log_size)))
                        self.test_result = "Success"
                        background = self.background_green
                else:
                    self.logger.info("TIMEOUT FAILURE,  Check LANforge Radios")
                    self.test_result = "Time Out"
                    background = self.background_purple

                self.html_results += """
                    <tr><td>""" + str(test) + """</td><td class='scriptdetails'>""" + str(command) + """</td>
                <td style="""+ str(background) + """>""" + str(self.test_result) + """ 
                <td><a href=""" + str(stdout_log_txt) + """ target=\"_blank\">STDOUT</a></td>"""
                if self.test_result == "Failure":
                    self.html_results += """<td><a href=""" + str(stderr_log_txt) + """ target=\"_blank\">STDERR</a></td>"""
                elif self.test_result == "Time Out":
                    self.html_results += """<td><a href=""" + str(stderr_log_txt) + """ target=\"_blank\">STDERR</a></td>"""
                else:
                    self.html_results += """<td></td>"""
                self.html_results += """</tr>""" 

                row = [test,command,self.test_result,stdout_log_txt,stderr_log_txt]
                self.csv_results_writer.writerow(row)
                self.csv_results_file.flush()
                #self.logger.info("row: {}".format(row))
                self.logger.info("test: {} executed".format(test))

            else:
                self.logger.info("enable value {} invalid for test: {}, test skipped".format(self.test_dict[test]['enabled'],test))

        self.finish_html_results()        

def main():
    # arguments
    parser = argparse.ArgumentParser(
        prog='lf_check.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            lf_check.py : for running scripts listed in lf_check_config.ini file
            ''',
        description='''\
lf_check.py
-----------

Summary :
---------
for running scripts listed in lf_check_config.ini
            ''')

    parser.add_argument('--outfile', help="--outfile <Output Generic Name>  used as base name for all files generated", default="")
    parser.add_argument('--logfile', help="--logfile <logfile Name>  logging for output of lf_check.py script", default="lf_check.log")

    args = parser.parse_args()    

    # output report.
    report = lf_report(_results_dir_name = "lf_check",_output_html="lf_check.html",_output_pdf="lf-check.pdf")

    current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    csv_results = "lf_check{}-{}.csv".format(args.outfile,current_time)
    csv_results = report.file_add_path(csv_results)
    outfile = "lf_check-{}-{}".format(args.outfile,current_time)
    outfile = report.file_add_path(outfile)

    # lf_check() class created
    check = lf_check(_csv_results = csv_results,
                    _outfile = outfile)

    # get the git sha 
    process = subprocess.Popen(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)
    (commit_hash, err) = process.communicate()
    exit_code = process.wait()
    git_sha = commit_hash.decode('utf-8','ignore')

    # set up logging 
    logfile = args.logfile[:-4]
    print("logfile: {}".format(logfile))
    logfile = "{}-{}.log".format(logfile,current_time)
    logfile = report.file_add_path(logfile)
    print("logfile {}".format(logfile))
    formatter = logging.Formatter(FORMAT)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(logfile, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(logging.StreamHandler(sys.stdout)) # allows to logging to file and stdout

    logger.info("commit_hash: {}".format(commit_hash))
    logger.info("commit_hash2: {}".format(commit_hash.decode('utf-8','ignore')))

    check.read_config_contents() # CMR need mode to just print out the test config and not run 
    check.run_script_test()

    # Generate Ouptput reports
    report.set_title("LF Check: lf_check.py")
    report.build_banner()
    report.set_table_title("LF Check Test Results")
    report.build_table_title()
    report.set_text("git sha: {}".format(git_sha))
    report.build_text()
    html_results = check.get_html_results()
    #print("html_results {}".format(html_results))
    report.set_custom_html(html_results)
    report.build_custom()
    report.write_html_with_timestamp()
    report.write_pdf_with_timestamp()


if __name__ == '__main__':
    main()


