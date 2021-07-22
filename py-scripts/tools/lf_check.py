#!/usr/bin/python3

'''
NAME:
lf_check.py

PURPOSE:
lf_check.py will tests based on .ini file or .json file. 
The config file may be copied from lf_check_config_template.ini, or can be generated.   
The config file name can be passed in as a configuraiton parameter.
The json file may be copied from lf_check.json and updated.  Currently all the parameters are needed to be set to a value

The --production flag determine the email list for results 

EXAMPLE:
lf_check.py  # this will use the defaults
lf_check.py --ini <unique ini file>  --test_suite <suite to use in .ini file>
lf_check.py --ini <unique ini file>  --test_suite <suite to use in .ini file> --production

lf_check.py --use_json --json <unique json file> --test_suite 
lf_check.py --use_json --json <unique json file> --production 

NOTES:
Before using lf_check.py
Using .ini:
1. copy lf_check_config_template.ini to <file name>.ini ,  this will avoid .ini being overwritten on git pull
2. update <file name>.ini to enable (TRUE) tests to be run in the test suite, the default suite is the TEST_DICTIONARY
3. update other configuration to specific test bed for example radios 

Using .json:
1. copy lf_check.json to <file name>.json this will avoide .json being overwritten on git pull
2. update lf_check.json to enable (TRUE) tests to be run in the test suite, the default TEST_DICTIONARY

NOTES: getting radio information:
1. curl -H 'Accept: application/json' http://localhost:8080/radiostatus/all | json_pp | less 
2. response = self.json_get("/radiostatus/all")

GENERIC NOTES: 
Starting LANforge:
    On local or remote system: /home/lanforge/LANforgeGUI/lfclient.bash -cli-socket 3990 -s LF_MGR 
    On local system the -s LF_MGR will be local_host if not provided

1. add server (telnet localhost 4001) build info,  GUI build sha, and Kernel version to the output. 
    A. for build information on LANforgeGUI : /home/lanforge ./btserver --version
    B. for the kernel version uname -r (just verion ), uname -a build date
    C. for getting the radio firmware:  ethtool -i wlan0 

# may need to build in a testbed reboot at the beginning of a day's testing...
# seeing some dhcp exhaustion and high latency values for testbeds that have been running 
# for a while that appear to clear up once the entire testbed is power cycled

# issue a shutdown command on the lanforge(s)
#  ssh root@lanforgex reboot (need to verify)  or do a shutdown 
# send curl command to remote power switch to reboot testbed
#   curl -s http://admin:lanforge@192.168.100.237/outlet?1=CCL -o /dev/null 2>&1
# 
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
from os import path
import shlex
import paramiko 

# lf_report is from the parent of the current file
dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path,os.pardir))
sys.path.insert(0, parent_dir_path)

from lf_report import lf_report
sys.path.append('/')

# setup logging FORMAT
FORMAT = '%(asctime)s %(name)s %(levelname)s: %(message)s'

# lf_check class contains verificaiton configuration and ocastrates the testing.
class lf_check():
    def __init__(self,
                _use_json,
                _config_ini,
                _json_data,
                _test_suite,
                _production,
                _csv_results,
                _outfile,
                _report_path):
        self.use_json = _use_json
        self.json_data = _json_data
        self.config_ini = _config_ini
        self.test_suite = _test_suite
        self.production_run  = _production
        self.report_path = _report_path
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
        self.background_blue = "background-color:blue"

        self.http_test_ip = ""
        self.ftp_test_ip = ""
        self.test_ip = ""

        # section TEST_GENERIC 
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
        self.test_timeout = 120
        self.test_timeout_default = 120
        self.use_blank_db = "FALSE"
        self.use_factory_default_db = "FALSE"
        self.use_custom_db = "FALSE"
        self.email_list_production = ""
        self.host_ip_production = None
        self.email_list_test = ""
        self.host_ip_test = None
        self.email_title_txt = ""
        self.email_txt = ""

        # lanforge configuration 
        self.lf_mgr_ip = "192.168.0.102" 
        self.lf_mgr_port = "" 
        self.lf_mgr_user = "lanforge"
        self.lf_mgr_pass =  "lanforge"

        # dut configuration 
        self.dut_name = "DUT_NAME_NOT_SET" # "ASUSRT-AX88U" note this is not dut_set_name
        self.dut_hw = "DUT_HW_NOT_SET"
        self.dut_sw = "DUT_SW_NOT_SET"
        self.dut_model = "DUT_MODEL_NOT_SET"
        self.dut_serial = "DUT_SERIAL_NOT_SET"
        self.dut_bssid_2g = "BSSID_2G_NOT_SET" #"3c:7c:3f:55:4d:64" - this is the mac for the 2.4G radio this may be seen with a scan 
        self.dut_bssid_5g = "BSSID_5G_NOT_SET" #"3c:7c:3f:55:4d:64" - this is the mac for the 5G radio this may be seen with a scan 
        self.dut_bssid_6g = "BSSID_6G_NOT_SET" #"3c:7c:3f:55:4d:64" - this is the mac for the 6G radio this may be seen with a scan 
        #NOTE:  My influx token is unlucky and starts with a '-', but using the syntax below # with '=' right after the argument keyword works as hoped.
        # --influx_token=

        # DUT , Test rig must match testbed
        self.test_rig = "CT-US-001"

        # database configuration  # database
        self.database_json = ""
        self.database_config = "True" # default to False once testing done
        self.database_host = "192.168.100.201" #"c7-grafana.candelatech.com" # influx and grafana have the same host "192.168.100.201"
        self.database_port = "8086"
        self.database_token = "-u_Wd-L8o992701QF0c5UmqEp7w7Z7YOMaWLxOMgmHfATJGnQbbmYyNxHBR9PgD6taM_tcxqJl6U8DjU1xINFQ=="
        self.database_org = "Candela"
        self.database_bucket = "lanforge_qa_testing"
        self.database_tag = 'testbed CT-US-001' # the test_rig needs to match
        self.dut_set_name = 'DUT_NAME ASUSRT-AX88U' # note the name will be set as --set DUT_NAME ASUSRT-AX88U, this is not dut_name (see above)


        # grafana configuration  #dashboard
        self.dashboard_json = ""
        self.dashboard_config = "True" # default to False once testing done
        self.dashboard_host = "192.168.100.201" #"c7-grafana.candelatech.com" # 192.168.100.201
        self.dashboard_token = "eyJrIjoiS1NGRU8xcTVBQW9lUmlTM2dNRFpqNjFqV05MZkM0dzciLCJuIjoibWF0dGhldyIsImlkIjoxfQ=="

        # ghost configuration 
        self.blog_json = ""
        self.blog_config = False
        self.blog_host = "192.168.100.153"
        self.blog_token = "60df4b0175953f400cd30650:d50e1fabf9a9b5d3d30fe97bc3bf04971d05496a89e92a169a0d72357c81f742"
        self.blog_authors = "Matthew"
        self.blog_customer = "candela"
        self.blog_user_push = "lanforge"
        self.blog_password_push = "lanforge"
        self.blog_flag = "--kpi_to_ghost"

        self.test_run = ""

    def get_scripts_git_sha(self):
        # get git sha
        process = subprocess.Popen(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)
        (commit_hash, err) = process.communicate()
        exit_code = process.wait()
        scripts_git_sha = commit_hash.decode('utf-8','ignore')
        return scripts_git_sha

    def get_lanforge_kernel_version(self):
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        #ssh.connect(self.lf_mgr_ip, port=22, username=self.lf_mgr_user, password=self.lf_mgr_pass, banner_timeout=600)
        ssh.connect(hostname=self.lf_mgr_ip, port=22, username=self.lf_mgr_user, password=self.lf_mgr_pass, banner_timeout=600)
        stdin, stdout, stderr = ssh.exec_command('uname -r')
        output = stdout.readlines()
        # print('\n'.join(output))
        ssh.close()
        time.sleep(1)
        return output

    def get_lanforge_gui_version(self):
        output = ""
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(hostname=self.lf_mgr_ip, port=22, username=self.lf_mgr_user, password=self.lf_mgr_pass, banner_timeout=600)
        stdin, stdout, stderr = ssh.exec_command('./btserver --version | grep  Version')
        output = stdout.readlines()
        # print('\n'.join(output))
        ssh.close()
        time.sleep(1)
        return output
        

    # NOT complete : will send the email results
    def send_results_email(self, report_file=None):
        if (report_file is None):
            print( "No report file, not sending email.")
            return
        report_url=report_file.replace('/home/lanforge/', '')
        if report_url.startswith('/'):
            report_url = report_url[1:]
        # following recommendation 
        # NOTE: https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-from-nic-in-python
        # Mail
        # command to check if mail running : systemctl status postfix
        #command = 'echo "$HOSTNAME mail system works!" | mail -s "Test: $HOSTNAME $(date)" chuck.rekiere@candelatech.com'
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if(self.email_txt != ""):
            message_txt = """{email_txt} lanforge target {lf_mgr_ip}
Results from {hostname}:
http://{ip}/{report}
Blog:
http://{blog}:2368
NOTE: for now to see stdout and stderr remove /home/lanforge from path.
""".format(hostname=hostname, ip=ip, report=report_url, email_txt=self.email_txt, lf_mgr_ip=self.lf_mgr_ip,blog=self.blog_host)

        else:
            message_txt = """Results from {hostname}:
http://{ip}/{report}
Blog:
blog: http://{blog}:2368
""".format(hostname=hostname, ip=ip, report=report_url,blog=self.blog_host)

        if(self.email_title_txt != ""):
            mail_subject = "{} [{hostname}] {date}".format(self.email_title_txt,hostname=hostname, date=datetime.datetime.now())
        else:
            mail_subject = "Regression Test [{hostname}] {date}".format(hostname=hostname, date=datetime.datetime.now())
        try:
            if self.production_run == True:
                msg = message_txt.format(ip=self.host_ip_production)
                # for postfix from command line  echo "My message" | mail -s subject user@candelatech.com
                command = "echo \"{message}\" | mail -s \"{subject}\" {address}".format(
                    message=msg,
                    subject=mail_subject,
                    ip=self.host_ip_production,
                    address=self.email_list_production)
            else:
                msg = message_txt.format(ip=ip)
                command = "echo \"{message}\" | mail -s \"{subject}\" {address}".format(
                    message=msg,
                    subject=mail_subject,
                    ip=ip, #self.host_ip_test,
                    address=self.email_list_test)

            print("running:[{}]".format(command))
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            # have email on separate timeout        
            process.wait(timeout=int(self.test_timeout))
        except subprocess.TimeoutExpired:
            print("send email timed out")
            process.terminate()
    
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


    def read_config(self):
        if self.use_json:
            self.read_config_json()
        else:
            self.read_config_ini()

    # there is probably a more efficient way to do this in python
    # Keeping it obvious for now, may be refactored later
    def read_config_json(self):
        #self.logger.info("read_config_json_contents {}".format(self.json_data))
        if "test_parameters" in self.json_data:
            self.logger.info("json: read test_parameters")
            #self.logger.info("test_parameters {}".format(self.json_data["test_parameters"]))
            self.read_test_parameters()
        else:
            self.logger.info("EXITING test_parameters not in json {}".format(self.json_data))
            exit(1)

        if "test_network" in self.json_data:
            self.logger.info("json: read test_network")
            #self.logger.info("test_network {}".format(self.json_data["test_network"]))
            self.read_test_network()
        else:
            self.logger.info("EXITING test_network not in json {}".format(self.json_data))
            exit(1)

        if "test_database" in self.json_data:
            self.logger.info("json: read test_database")
            #self.logger.info("test_database {}".format(self.json_data["test_database"]))
            self.read_test_database()
        else:
            self.logger.info("NOTE: test_database not found in json")
        
        if "test_dashboard" in self.json_data:
            self.logger.info("json: read test_dashboard")
            #self.logger.info("test_dashboard {}".format(self.json_data["test_dashboard"]))
            self.read_test_dashboard()
        else:
            self.logger.info("NOTE: test_dashboard not found in json")

        if "test_blog" in self.json_data:
            self.logger.info("json: read test_blog")
            #self.logger.info("test_blog {}".format(self.json_data["test_blog"]))
            self.read_test_blog()
        else:
            self.logger.info("NOTE: test_blog not found in json")

        if "test_generic" in self.json_data:
            self.logger.info("json: read test_generic")
            #self.logger.info("test_generic {}".format(self.json_data["test_generic"]))
            self.read_test_generic()
        else:
            self.logger.info("EXITING test_generic not in json {}".format(self.json_data))
            exit(1)

        if "radio_dict" in self.json_data:
            self.logger.info("json: read radio_dict")
            #self.logger.info("radio_dict {}".format(self.json_data["radio_dict"]))
            self.radio_dict = self.json_data["radio_dict"]
            self.logger.info("self.radio_dict {}".format(self.radio_dict))
        else:
            self.logger.info("EXITING radio_dict not in json {}".format(self.json_data))
            exit(1)

        if "test_suites" in self.json_data:
            self.logger.info("json: read test_suites looking for: {}".format(self.test_suite))
            #self.logger.info("test_suites {}".format(self.json_data["test_suites"]))
            if self.test_suite in self.json_data["test_suites"]:
                self.test_dict = self.json_data["test_suites"][self.test_suite]
                #self.logger.info("self.test_dict {}".format(self.test_dict))
            else:
                self.logger.info("EXITING test_suite {} Not Present in json test_suites: {}".format(self.test_suite, self.json_data["test_suites"]))
                exit(1)
        else:
            self.logger.info("EXITING test_suites not in json {}".format(self.json_data))
            exit(1)

    def read_test_parameters(self):
        if "test_timeout" in self.json_data["test_parameters"]:
            self.test_timeout = self.json_data["test_parameters"]["test_timeout"]
            self.test_timeout_default = self.test_timeout
        else:
            self.logger.info("test_timeout not in test_parameters json")
            exit(1)
        if "load_blank_db" in self.json_data["test_parameters"]:
            self.load_blank_db = self.json_data["test_parameters"]["load_blank_db"]
        else:
            self.logger.info("load_blank_db not in test_parameters json")
            exit(1)
        if "load_factory_default_db" in self.json_data["test_parameters"]:
            self.load_factory_default_db = self.json_data["test_parameters"]["load_factory_default_db"]
        else:
            self.logger.info("load_factory_default_db not in test_parameters json")
            exit(1)
        if "load_custom_db" in self.json_data["test_parameters"]:
            self.load_custom_db = self.json_data["test_parameters"]["load_custom_db"]
        else:
            self.logger.info("load_custom_db not in test_parameters json")
            exit(1)
        if "custom_db" in self.json_data["test_parameters"]:
            self.custom_db = self.json_data["test_parameters"]["custom_db"]
        else:
            self.logger.info("custom_db not in test_parameters json, if not using custom_db just put in a name")
            exit(1)
        if "email_list_production" in self.json_data["test_parameters"]:
            self.email_list_production = self.json_data["test_parameters"]["email_list_production"]
        else:
            self.logger.info("email_list_production not in test_parameters json")
            exit(1)
        if "host_ip_production" in self.json_data["test_parameters"]:
            self.host_ip_production = self.json_data["test_parameters"]["host_ip_production"]
        else:
            self.logger.info("host_ip_production not in test_parameters json")
            exit(1)
        if "email_list_test" in self.json_data["test_parameters"]:
            self.email_list_test = self.json_data["test_parameters"]["email_list_test"]
            print(self.email_list_test)
        else:
            self.logger.info("email_list_test not in test_parameters json")
            exit(1)
        if "host_ip_test" in self.json_data["test_parameters"]:
            self.host_ip_test = self.json_data["test_parameters"]["host_ip_test"]
        else:
            self.logger.info("host_ip_test not in test_parameters json")
            exit(1)
        if "email_title_txt" in self.json_data["test_parameters"]:
            self.email_title_txt = self.json_data["test_parameters"]["email_title_txt"]
        else:
            self.logger.info("email_title_txt not in test_parameters json")
        if "email_txt" in self.json_data["test_parameters"]:
            self.email_txt = self.json_data["test_parameters"]["email_txt"]
        else:
            self.logger.info("email_txt not in test_parameters json")
        if "lf_mgr_ip" in self.json_data["test_parameters"]:
            self.lf_mgr_ip = self.json_data["test_parameters"]["lf_mgr_ip"]
        else:
            self.logger.info("lf_mgr_ip not in test_parameters json")
        if "lf_mgr_port" in self.json_data["test_parameters"]:
            self.lf_mgr_port = self.json_data["test_parameters"]["lf_mgr_port"]
        else:
            self.logger.info("lf_mgr_port not in test_parameters json")
        if "dut_name" in self.json_data["test_parameters"]:
            self.dut_name = self.json_data["test_parameters"]["dut_name"]
        else:
            self.logger.info("dut_name not in test_parameters json")
        if "dut_hw" in self.json_data["test_parameters"]:
            self.dut_hw = self.json_data["test_parameters"]["dut_hw"]
        else:
            self.logger.info("dut_hw not in test_parameters json")
        if "dut_sw" in self.json_data["test_parameters"]:
            self.dut_sw = self.json_data["test_parameters"]["dut_sw"]
        else:
            self.logger.info("dut_sw not in test_parameters json")
        if "dut_model" in self.json_data["test_parameters"]:
            self.dut_model = self.json_data["test_parameters"]["dut_model"]
        else:
            self.logger.info("dut_model not in test_parameters json")
        if "dut_serial" in self.json_data["test_parameters"]:
            self.dut_serial = self.json_data["test_parameters"]["dut_serial"]
        else:
            self.logger.info("dut_serial not in test_parameters json")
        if "dut_bssid_2g" in self.json_data["test_parameters"]:
            self.dut_bssid_2g = self.json_data["test_parameters"]["dut_bssid_2g"]
        else:
            self.logger.info("dut_bssid_2G not in test_parameters json")
        if "dut_bssid_5g" in self.json_data["test_parameters"]:
            self.dut_bssid_5g = self.json_data["test_parameters"]["dut_bssid_5g"]
        else:
            self.logger.info("dut_bssid_5g not in test_parameters json")
        if "dut_bssid_6g" in self.json_data["test_parameters"]:
            self.dut_bssid_6g = self.json_data["test_parameters"]["dut_bssid_6g"]
        else:
            self.logger.info("dut_bssid_6g not in test_parameters json")

    def read_test_network(self):
        if "http_test_ip" in self.json_data["test_network"]:
            self.http_test_ip = self.json_data["test_network"]["http_test_ip"]
        else:
            self.logger.info("http_test_ip not in test_network json")
            exit(1)
        if "ftp_test_ip" in self.json_data["test_network"]:
            self.ftp_test_ip = self.json_data["test_network"]["ftp_test_ip"]
        else:
            self.logger.info("ftp_test_ip not in test_network json")
            exit(1)
        if "test_ip" in self.json_data["test_network"]:
            self.ftp_test_ip = self.json_data["test_network"]["test_ip"]
        else:
            self.logger.info("test_ip not in test_network json")
            exit(1)

    def read_test_database(self):
        if "database_config" in self.json_data["test_database"]:
            self.database_config = self.json_data["test_database"]["database_config"]
        else:
            self.logger.info("database_config not in test_database json")
        if "database_host" in self.json_data["test_database"]:
            self.database_host = self.json_data["test_database"]["database_host"]
        else:
            self.logger.info("database_host not in test_database json")
        if "database_port" in self.json_data["test_database"]:
            self.database_port = self.json_data["test_database"]["database_port"]
        else:
            self.logger.info("database_port not in test_database json")
        if "database_token" in self.json_data["test_database"]:
            self.database_token = self.json_data["test_database"]["database_token"]
        else:
            self.logger.info("database_token not in test_database json")
        if "database_org" in self.json_data["test_database"]:
            self.database_org = self.json_data["test_database"]["database_org"]
        else:
            self.logger.info("database_org not in test_database json")
        if "database_bucket" in self.json_data["test_database"]:
            self.database_bucket = self.json_data["test_database"]["database_bucket"]
        else:
            self.logger.info("database_bucket not in test_database json")
        if "database_tag" in self.json_data["test_database"]:
            self.database_tag = self.json_data["test_database"]["database_tag"]
        else:
            self.logger.info("database_tag not in test_database json")
        if "test_rig" in self.json_data["test_database"]:
            self.test_rig = self.json_data["test_database"]["test_rig"]
        else:
            self.logger.info("test_rig not in test_database json")
        if "dut_set_name" in self.json_data["test_database"]:
            self.dut_set_name = self.json_data["test_database"]["dut_set_name"]
        else:
            self.logger.info("dut_set_name not in test_database json")

    def read_test_dashboard(self):
        if "dashboard_config" in self.json_data["test_dashboard"]:
            self.dashboard_config = self.json_data["test_dashboard"]["dashboard_config"]
        else:
            self.logger.info("dashboard_config not in test_dashboard json")

        if "dashboard_host" in self.json_data["test_dashboard"]:
            self.dashboard_host = self.json_data["test_dashboard"]["dashboard_host"]
        else:
            self.logger.info("dashboard_host not in test_dashboard json")

        if "dashboard_token" in self.json_data["test_dashboard"]:
            self.dashboard_token = self.json_data["test_dashboard"]["dashboard_token"]
        else:
            self.logger.info("dashboard_token not in test_dashboard json")

    def read_test_blog(self):
        if "blog_config" in self.json_data["test_blog"]:
            self.blog_config = self.json_data["test_blog"]["blog_config"]
        else:
            self.logger.info("blog_config not in test_blog json")

        if "blog_host" in self.json_data["test_blog"]:
            self.blog_host = self.json_data["test_blog"]["blog_host"]
        else:
            self.logger.info("blog_host not in test_blog json")

        if "blog_token" in self.json_data["test_blog"]:
            self.blog_token = self.json_data["test_blog"]["blog_token"]
        else:
            self.logger.info("blog_token not in test_blog json")

        if "blog_authors" in self.json_data["test_blog"]:
            self.blog_authors = self.json_data["test_blog"]["blog_authors"]
        else:
            self.logger.info("blog_authors not in test_blog json")

        if "blog_customer" in self.json_data["test_blog"]:
            self.blog_customer = self.json_data["test_blog"]["blog_customer"]
        else:
            self.logger.info("blog_customer not in test_blog json")

        if "blog_user_push" in self.json_data["test_blog"]:
            self.blog_user_push = self.json_data["test_blog"]["blog_user_push"]
        else:
            self.logger.info("blog_user_push not in test_blog json")

        if "blog_password_push" in self.json_data["test_blog"]:
            self.blog_password_push = self.json_data["test_blog"]["blog_password_push"]
        else:
            self.logger.info("blog_password_push not in test_blog json")

        if "blog_flag" in self.json_data["test_blog"]:
            self.blog_flag = self.json_data["test_blog"]["blog_flag"]
        else:
            self.logger.info("blog_flag not in test_blog json")

    def read_test_generic(self):
        if "radio_used" in self.json_data["test_generic"]:
            self.radio_lf = self.json_data["test_generic"]["radio_used"]
        else:
            self.logger.info("radio_used not in test_generic json")
            exit(1)
        if "ssid_used" in self.json_data["test_generic"]:
            self.ssid = self.json_data["test_generic"]["ssid_used"]
        else:
            self.logger.info("ssid_used not in test_generic json")
            exit(1)
        if "ssid_pw_used" in self.json_data["test_generic"]:
            self.ssid_pw = self.json_data["test_generic"]["ssid_pw_used"]
        else:
            self.logger.info("ssid_pw_used not in test_generic json")
            exit(1)
        if "security_used" in self.json_data["test_generic"]:
            self.security = self.json_data["test_generic"]["security_used"]
        else:
            self.logger.info("security_used not in test_generic json")
            exit(1)
        if "num_sta" in self.json_data["test_generic"]:
            self.num_sta = self.json_data["test_generic"]["num_sta"]
        else:
            self.logger.info("num_sta not in test_generic json")
            exit(1)
        if "col_names" in self.json_data["test_generic"]:
            self.num_sta = self.json_data["test_generic"]["col_names"]
        else:
            self.logger.info("col_names not in test_generic json")
            exit(1)
        if "upstream_port" in self.json_data["test_generic"]:
            self.upstream_port = self.json_data["test_generic"]["upstream_port"]
        else:
            self.logger.info("upstream_port not in test_generic json")
            exit(1)

    # functions in this section are/can be overridden by descendants
    # this code reads the lf_check_config.ini file to populate the test variables
    def read_config_ini(self):
        #self.logger.info("read_config_ini_contents {}".format(self.config_ini))
        config_file = configparser.ConfigParser()
        success = True
        success = config_file.read(self.config_ini)
        self.logger.info("config_file.read result {}".format(success))

        # LF_MGR parameters not used yet
        if 'LF_MGR' in config_file.sections():
            section = config_file['LF_MGR']
            self.lf_mgr = section['LF_MGR_IP']
            self.lf_mgr_port = section['LF_MGR_PORT']
            self.logger.info("lf_mgr {}".format(self.lf_mgr))
            self.logger.info("lf_mgr_port {}".format(self.lf_mgr_port))

        if 'TEST_PARAMETERS' in config_file.sections():
            section = config_file['TEST_PARAMETERS']
            self.test_timeout = section['TEST_TIMEOUT']
            self.use_blank_db = section['LOAD_BLANK_DB']
            self.use_factory_default_db = section['LOAD_FACTORY_DEFAULT_DB']
            self.use_custom_db = section['LOAD_CUSTOM_DB']
            self.custom_db = section['CUSTOM_DB']
            self.email_list_production = section['EMAIL_LIST_PRODUCTION']
            self.host_ip_production = section['HOST_IP_PRODUCTION']
            self.email_list_test = section['EMAIL_LIST_TEST']
            self.host_ip_test = section['HOST_IP_TEST']
            self.logger.info("self.email_list_test:{}".format(self.email_list_test))

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

        if self.test_suite in config_file.sections():
            section = config_file[self.test_suite]
            # for json replace the \n and \r they are invalid json characters, allows for multiple line args 
            try:            
                self.test_dict = json.loads(section.get('TEST_DICT', self.test_dict).replace('\n',' ').replace('\r',' '))
                self.logger.info("{}:  {}".format(self.test_suite,self.test_dict))
            except:
                self.logger.info("Excpetion loading {}, is there comma after the last entry?  Check syntax".format(self.test_suite))   
        else:
            self.logger.info("EXITING... NOT FOUND Test Suite with name : {}".format(self.test_suite))   
            exit(1)

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

    # not currently used
    def load_blank_db(self):
        try:
            os.chdir(self.scripts_wd)
        except:
            self.logger.info("failed to change to {}".format(self.scripts_wd))

        # no spaces after FACTORY_DFLT
        command = "./{} {}".format("scenario.py", "--load BLANK")
        process = subprocess.Popen((command).split(' '), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    def load_custom_db(self,custom_db):
        try:
            os.chdir(self.scripts_wd)
        except:
            self.logger.info("failed to change to {}".format(self.scripts_wd))

        # no spaces after FACTORY_DFLT
        command = "./{} {}".format("scenario.py", "--load {}".format(custom_db))
        process = subprocess.Popen((command).split(' '), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        # wait for the process to terminate
        out, err = process.communicate()
        errcode = process.returncode

    def run_script_test(self):
        self.start_html_results() 
        self.start_csv_results()

        for test in self.test_dict:
            if self.test_dict[test]['enabled'] == "FALSE":
                self.logger.info("test: {}  skipped".format(test))
            # load the default database 
            elif self.test_dict[test]['enabled'] == "TRUE":
                # if args key has a value of an empty string then need to manipulate the args_list to args 
                # list does not have replace only stings do to args_list will be joined and  converted to a string and placed
                # in args.  Then the replace below will work.
                if self.test_dict[test]['args'] == "":
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace(self.test_dict[test]['args'],''.join(self.test_dict[test]['args_list']))
                # Configure Tests
                # loop through radios
                for radio in self.radio_dict:
                    # replace RADIO, SSID, PASSWD, SECURITY with actual config values (e.g. RADIO_0_CFG to values)
                    # not "KEY" is just a word to refer to the RADIO define (e.g. RADIO_0_CFG) to get the vlaues
                    # --num_stations needs to be int not string (no double quotes)
                    if self.radio_dict[radio]["KEY"] in self.test_dict[test]['args']:
                        self.test_dict[test]['args'] = self.test_dict[test]['args'].replace(self.radio_dict[radio]["KEY"],'--radio {} --ssid {} --passwd {} --security {} --num_stations {}'
                        .format(self.radio_dict[radio]['RADIO'],self.radio_dict[radio]['SSID'],self.radio_dict[radio]['PASSWD'],self.radio_dict[radio]['SECURITY'],self.radio_dict[radio]['STATIONS']))

                if 'HTTP_TEST_IP' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('HTTP_TEST_IP',self.http_test_ip)
                if 'FTP_TEST_IP' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('FTP_TEST_IP',self.ftp_test_ip)
                if 'TEST_IP' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('TEST_IP',self.test_ip)

                if 'LF_MGR_IP' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('LF_MGR_IP',self.lf_mgr_ip)
                if 'LF_MGR_PORT' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('LF_MGR_PORT',self.lf_mgr_port)

                if 'DUT_NAME' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DUT_NAME',self.dut_name)
                if 'DUT_HW' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DUT_HW',self.dut_hw)
                if 'DUT_SW' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DUT_SW',self.dut_sw)
                if 'DUT_MODEL' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DUT_MODEL',self.dut_model)
                if 'DUT_SERIAL' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DUT_SERIAL',self.dut_serial)
                if 'DUT_BSSID_2G' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DUT_BSSID_2G',self.dut_bssid_2g)
                if 'DUT_BSSID_5G' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DUT_BSSID_5G',self.dut_bssid_5g)
                if 'DUT_BSSID_6G' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DUT_BSSID_6G',self.dut_bssid_6g)

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
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('UPSTREAM_PORT',self.upstream_port)

                # lf_dataplane_test.py and lf_wifi_capacity_test.py use a parameter --local_path for the location 
                # of the reports when the reports are pulled.
                if 'REPORT_PATH' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('REPORT_PATH',self.report_path)

                # The TEST_BED is the database tag
                if 'TEST_BED' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('TEST_BED',self.database_tag)

                # database configuration
                if 'DATABASE_HOST' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DATABASE_HOST',self.database_host)
                if 'DATABASE_PORT' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DATABASE_PORT',self.database_port)
                if 'DATABASE_TOKEN' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DATABASE_TOKEN',self.database_token)
                if 'DATABASE_ORG' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DATABASE_ORG',self.database_org)
                if 'DATABASE_BUCKET' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DATABASE_BUCKET',self.database_bucket)
                if 'DATABASE_TAG' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DATABASE_TAG',self.database_tag)
                if 'DUT_SET_NAME' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DUT_SET_NAME',self.dut_set_name)

                if 'TEST_RIG' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('TEST_RIG',self.test_rig)

                # dashboard configuration
                if 'DASHBOARD_HOST' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DASHBOARD_HOST',self.dashboard_host)
                if 'DASHBOARD_TOKEN' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('DASHBOARD_TOKEN',self.dashboard_token)

                # blog configuration
                if 'BLOG_HOST' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('BLOG_HOST',self.blog_host)
                if 'BLOG_TOKEN' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('BLOG_TOKEN',self.blog_token)
                if 'BLOG_AUTHORS' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('BLOG_AUTHORS',self.blog_authors)
                if 'BLOG_CUSTOMER' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('BLOG_CUSTOMER',self.blog_customer)
                if 'BLOG_USER_PUSH' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('BLOG_USER_PUSH',self.blog_user_push)
                if 'BLOG_PASSWORD_PUSH' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('BLOG_PASSWORD_PUSH',self.blog_password_push)
                if 'BLOG_FLAG' in self.test_dict[test]['args']:
                    self.test_dict[test]['args'] = self.test_dict[test]['args'].replace('BLOG_FLAG',self.blog_flag)

                if 'timeout' in self.test_dict[test]:
                    self.logger.info("timeout : {}".format(self.test_dict[test]['timeout']))
                    self.test_timeout = int(self.test_dict[test]['timeout'])
                else:
                    self.test_timeout = self.test_timeout_default                    

                if 'load_db' in self.test_dict[test]:
                    self.logger.info("load_db : {}".format(self.test_dict[test]['load_db']))
                    if str(self.test_dict[test]['load_db']).lower() != "none" and str(self.test_dict[test]['load_db']).lower() != "skip":
                        try:
                            self.load_custom_db(self.test_dict[test]['load_db'])
                        except:
                            self.logger.info("custom database failed to load check existance and location: {}".format(self.test_dict[test]['load_db']))
                else:    
                    self.logger.info("no load_db present in dictionary, load db normally")
                    if self.use_factory_default_db == "TRUE":
                        self.load_factory_default_db()
                        sleep(3)
                        self.logger.info("FACTORY_DFLT loaded between tests with scenario.py --load FACTORY_DFLT")
                    if self.use_blank_db == "TRUE":
                        self.load_blank_db()
                        sleep(1)
                        self.logger.info("BLANK loaded between tests with scenario.py --load BLANK")
                    if self.use_custom_db == "TRUE":
                        try:
                            self.load_custom_db(self.custom_db)
                            sleep(1)
                            self.logger.info("{} loaded between tests with scenario.py --load {}".format(self.custom_db,self.custom_db))
                        except:
                            self.logger.info("custom database failed to load check existance and location: {}".format(self.custom_db))
                    else:
                        self.logger.info("no db loaded between tests: {}".format(self.use_custom_db))

                sleep(1) # DO NOT REMOVE the sleep is to allow for the database to stablize
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

                # need to take into account --raw_line parameters thus need to use shlex.split 
                # need to preserve command to have correct command syntax in command output
                command_to_run = command
                command_to_run = shlex.split(command_to_run)
                print("running {command_to_run}".format(command_to_run=command_to_run))
                try:
                    process = subprocess.Popen(command_to_run, shell=False, stdout=stdout_log, stderr=stderr_log, universal_newlines=True)
                    # if there is a better solution please propose,  the TIMEOUT Result is different then FAIL
                    try:
                        process.wait(timeout=int(self.test_timeout))
                    except subprocess.TimeoutExpired:
                        process.terminate()
                        self.test_result = "TIMEOUT"

                except:
                    print("No such file or directory with command: {}".format(command))
                    self.logger.info("No such file or directory with command: {}".format(command))

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

                # Ghost will put data in stderr 
                if('ghost' in command):
                    if(self.test_result != "TIMEOUT"):
                        self.test_result = "Success"
                        background = self.background_blue
                
                # stdout_log_link is used for the email reporting to have the corrected path
                stdout_log_link = str(stdout_log_txt).replace('/home/lanforge','')
                stderr_log_link = str(stderr_log_txt).replace('/home/lanforge','')
                self.html_results += """
                <tr><td>""" + str(test) + """</td><td class='scriptdetails'>""" + str(command) + """</td>
                <td style="""+ str(background) + """>""" + str(self.test_result) + """ 
                <td><a href=""" + str(stdout_log_link) + """ target=\"_blank\">STDOUT</a></td>"""
                if self.test_result == "Failure":
                    self.html_results += """<td><a href=""" + str(stderr_log_link) + """ target=\"_blank\">STDERR</a></td>"""
                elif self.test_result == "Time Out":
                    self.html_results += """<td><a href=""" + str(stderr_log_link) + """ target=\"_blank\">STDERR</a></td>"""
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
            lf_check.py : running scripts listed in <config>.ini or <config>.json 
            ''',
        description='''\
lf_check.py
-----------

Summary :
---------
running scripts listed in <config>.ini or <config>.json 

Example :  
./lf_check.py --ini lf_check_test.ini --suite suite_one
./lf_check.py --use_json --json lf_check_test.json --suite suite_two
---------
            ''')

    parser.add_argument('--ini', help="--ini <config.ini file>  default lf_check_config.ini", default="lf_check_config.ini")
    parser.add_argument('--json', help="--json <lf_ckeck_config.json file> ", default="lf_check_config.json")
    parser.add_argument('--use_json', help="--use_json ", action='store_true')
    parser.add_argument('--suite', help="--suite <suite name>  default TEST_DICTIONARY", default="TEST_DICTIONARY")
    parser.add_argument('--production', help="--production  stores true, sends email results to production email list", action='store_true')
    parser.add_argument('--outfile', help="--outfile <Output Generic Name>  used as base name for all files generated", default="")
    parser.add_argument('--logfile', help="--logfile <logfile Name>  logging for output of lf_check.py script", default="lf_check.log")

    args = parser.parse_args()   

    # load test config file information either <config>.json or <config>.ini
    use_json = False
    json_data = ""
    config_ini = ""
    if args.use_json:
        use_json = True
        try:
            print("args.json {}".format(args.json))
            with open(args.json, 'r') as json_config:
                json_data = json.load(json_config)
        except:
            print("Error reading {}".format(args.json))
    else:
        config_ini = os.getcwd() + '/' + args.ini
        if os.path.exists(config_ini):
            print("TEST CONFIG : {}".format(config_ini))
        else:
            print("EXITING: NOTFOUND TEST CONFIG : {} ".format(config_ini))
            exit(1)
    # select test suite 
    test_suite = args.suite
    
    if args.production:
        production = True
        print("Email to production list")
    else:
        production = False
        print("Email to email list")

    # create report class for reporting
    report = lf_report(_results_dir_name="lf_check",
                       _output_html="lf_check.html",
                       _output_pdf="lf-check.pdf")

    current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    csv_results = "lf_check{}-{}.csv".format(args.outfile,current_time)
    csv_results = report.file_add_path(csv_results)
    outfile = "lf_check-{}-{}".format(args.outfile,current_time)
    outfile_path = report.file_add_path(outfile)
    report_path = report.get_report_path()

    # lf_check() class created
    check = lf_check(_use_json = use_json,
                    _config_ini = config_ini,
                    _json_data = json_data,
                    _test_suite = test_suite,
                    _production = production,
                    _csv_results = csv_results,
                    _outfile = outfile_path,
                    _report_path = report_path)

    # get git sha
    process = subprocess.Popen(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)
    (commit_hash, err) = process.communicate()
    exit_code = process.wait()
    git_sha = commit_hash.decode('utf-8','ignore')

    try:
        scripts_git_sha = check.get_scripts_git_sha()
        print("git_sha {sha}".format(sha=scripts_git_sha))
    except:
        print("git_sha read exception ")        

    try:
        lanforge_kernel_version = check.get_lanforge_kernel_version()
        print("lanforge_kernel_version {kernel_ver}".format(kernel_ver=lanforge_kernel_version))
    except:
        print("lanforge_kernel_version exception")        

    try:
        lanforge_gui_version = check.get_lanforge_gui_version()
        print("lanforge_gui_version {gui_ver}".format(gui_ver=lanforge_gui_version))
    except:
        print("lanforge_gui_version exception")        

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

    # logger setup print out sha
    logger.info("commit_hash: {}".format(commit_hash))
    logger.info("commit_hash2: {}".format(commit_hash.decode('utf-8','ignore')))

    # read config and run tests
    check.read_config() 
    check.run_script_test()

    # read lanforge


    # generate output reports
    report.set_title("LF Check: lf_check.py")
    report.build_banner()
    report.start_content_div()
    report.set_table_title("LF Check Test Results")
    report.build_table_title()
    report.set_text("lanforge-scripts git sha: {}".format(git_sha))
    report.build_text()
    html_results = check.get_html_results()
    report.set_custom_html(html_results)
    report.build_custom()
    report.build_footer_no_png()
    html_report = report.write_html_with_timestamp()
    print("html report: {}".format(html_report))
    try:
        report.write_pdf_with_timestamp()
    except:
        print("exception write_pdf_with_timestamp()")

    report_path = os.path.dirname(html_report)
    parent_report_dir = os.path.dirname(report_path)

    # copy results to lastest so someone may see the latest.
    lf_check_latest_html = parent_report_dir + "/lf_check_latest.html"
    # duplicates html_report file up one directory
    lf_check_html_report = parent_report_dir + "/{}.html".format(outfile)

    banner_src_png =  report_path + "/banner.png"
    banner_dest_png = parent_report_dir + "/banner.png"
    CandelaLogo_src_png = report_path + "/CandelaLogo2-90dpi-200x90-trans.png"
    CandelaLogo_dest_png = parent_report_dir + "/CandelaLogo2-90dpi-200x90-trans.png"
    report_src_css = report_path + "/report.css"
    report_dest_css = parent_report_dir + "/report.css"
    custom_src_css = report_path + "/custom.css"
    custom_dest_css = parent_report_dir + "/custom.css"
    font_src_woff = report_path + "/CenturyGothic.woff"
    font_dest_woff = parent_report_dir + "/CenturyGothic.woff"

    #pprint.pprint([
    #    ('banner_src', banner_src_png),
    #    ('banner_dest', banner_dest_png),
    #    ('CandelaLogo_src_png', CandelaLogo_src_png),
    #    ('CandelaLogo_dest_png', CandelaLogo_dest_png),
    #    ('report_src_css', report_src_css),
    #    ('custom_src_css', custom_src_css)
    #])

    # copy one directory above
    try:
        shutil.copyfile(html_report,            lf_check_latest_html)
    except:
        print("check permissions on {lf_check_latest_html}".format(lf_check_latest_html=lf_check_latest_html))        
    shutil.copyfile(html_report,            lf_check_html_report)

    # copy banner and logo
    shutil.copyfile(banner_src_png,         banner_dest_png)
    shutil.copyfile(CandelaLogo_src_png,    CandelaLogo_dest_png)
    shutil.copyfile(report_src_css,         report_dest_css)
    shutil.copyfile(custom_src_css,         custom_dest_css)
    shutil.copyfile(font_src_woff,          font_dest_woff)

    # print out locations of results
    print("lf_check_latest.html: "+lf_check_latest_html)
    print("lf_check_html_report: "+lf_check_html_report)

    check.send_results_email(report_file=lf_check_html_report)

if __name__ == '__main__':
    main()


