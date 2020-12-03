#!/usr/bin/python3

import base64
import urllib.request
from bs4 import BeautifulSoup
import ssl
import subprocess, os
from artifactory import ArtifactoryPath
import tarfile
import paramiko
from paramiko import SSHClient
from scp import SCPClient
import os
import pexpect
from pexpect import pxssh
import sys
import paramiko
from scp import SCPClient
import pprint
from pprint import pprint
from os import listdir
import re
import requests
import json
import testrail_api
import logging
import datetime
import time
from datetime import date
from shutil import copyfile

# For finding files
# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
import glob
#external_results_dir=/var/tmp/lanforge

if sys.version_info[0] != 3:
       print("This script requires Python 3")
       exit(1)
if 'py-json' not in sys.path:
       sys.path.append('../../py-json')

from LANforge.LFUtils import *
# if you lack __init__.py in this directory you will not find sta_connect module#

if 'py-json' not in sys.path:
       sys.path.append('../../py-scripts')

import sta_connect2
from sta_connect2 import StaConnect2
import testrail_api
from testrail_api import APIClient
import eap_connect
from eap_connect import EAPConnect
import lab_ap_info
import cloudsdk
from cloudsdk import CloudSDK
import ap_ssh
from ap_ssh import ssh_cli_active_fw
from ap_ssh import iwinfo_status


### Set CloudSDK URL ###
cloudSDK_url=os.getenv('CLOUD_SDK_URL')
### Directories
local_dir=os.getenv('SANITY_LOG_DIR')
report_path=os.getenv('SANITY_REPORT_DIR')
report_template=os.getenv('REPORT_TEMPLATE')

## TestRail Information
tr_user=os.getenv('TR_USER')
tr_pw=os.getenv('TR_PWD')
milestoneId=os.getenv('MILESTONE')
projectId=os.getenv('PROJECT_ID')

##Jfrog credentials
jfrog_user=os.getenv('JFROG_USER')
jfrog_pwd=os.getenv('JFROG_PWD')
##EAP Credentials
identity=os.getenv('EAP_IDENTITY')
ttls_password=os.getenv('EAP_PWD')

## AP Credentials
ap_username=os.getenv('AP_USER')

logger = logging.getLogger('Nightly_Sanity')
hdlr = logging.FileHandler(local_dir+"/Nightly_Sanity.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

client: APIClient = APIClient('https://telecominfraproject.testrail.com')
client.user = tr_user
client.password = tr_pw


###Class for jfrog Interaction
class GetBuild:
    def __init__(self):
        self.user = jfrog_user
        self.password = jfrog_pwd
        ssl._create_default_https_context = ssl._create_unverified_context

    def get_latest_image(self,url):

        auth = str(
            base64.b64encode(
                bytes('%s:%s' % (self.user, self.password), 'utf-8')
            ),
            'ascii'
        ).strip()
        headers = {'Authorization': 'Basic ' + auth}

        ''' FIND THE LATEST FILE NAME'''
        #print(url)
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        html = response.read()
        soup = BeautifulSoup(html, features="html.parser")
        ##find the last pending link on dev
        last_link = soup.find_all('a', href=re.compile("pending"))[-1]
        latest_file=last_link['href']
        latest_fw = latest_file.replace('.tar.gz','')
        return latest_fw

###Class for Tests
class RunTest:
    def Single_Client_Connectivity(self, port, radio, ssid_name, ssid_psk, security, station, test_case, rid):
        '''SINGLE CLIENT CONNECTIVITY using test_connect2.py'''
        staConnect = StaConnect2("10.10.10.201", 8080, debug_=False)
        staConnect.sta_mode = 0
        staConnect.upstream_resource = 1
        staConnect.upstream_port = port
        staConnect.radio = radio
        staConnect.resource = 1
        staConnect.dut_ssid = ssid_name
        staConnect.dut_passwd = ssid_psk
        staConnect.dut_security = security
        staConnect.station_names = station
        staConnect.sta_prefix = 'test'
        staConnect.runtime_secs = 10
        staConnect.bringup_time_sec = 60
        staConnect.cleanup_on_exit = True
        # staConnect.cleanup()
        staConnect.setup()
        staConnect.start()
        print("napping %f sec" % staConnect.runtime_secs)
        time.sleep(staConnect.runtime_secs)
        staConnect.stop()
        staConnect.cleanup()
        run_results = staConnect.get_result_list()
        for result in run_results:
            print("test result: " + result)
        # result = 'pass'
        print("Single Client Connectivity :", staConnect.passes)
        if staConnect.passes() == True:
            print("Single client connection to", ssid_name, "successful. Test Passed")
            client.update_testrail(case_id=test_case, run_id=rid, status_id=1, msg='Client connectivity passed')
            logger.info("Client connectivity to " + ssid_name + " Passed")
            return ("passed")
        else:
            client.update_testrail(case_id=test_case, run_id=rid, status_id=5, msg='Client connectivity failed')
            print("Single client connection to", ssid_name, "unsuccessful. Test Failed")
            logger.warning("Client connectivity to " + ssid_name + " FAILED")
            return ("failed")

    def Single_Client_EAP(port, sta_list, ssid_name, radio, security, eap_type, identity, ttls_password, test_case,
                          rid):
        eap_connect = EAPConnect("10.10.10.201", 8080, _debug_on=False)
        eap_connect.upstream_resource = 1
        eap_connect.upstream_port = port
        eap_connect.security = security
        eap_connect.sta_list = sta_list
        eap_connect.station_names = sta_list
        eap_connect.ssid = ssid_name
        eap_connect.radio = radio
        eap_connect.eap = eap_type
        eap_connect.identity = identity
        eap_connect.ttls_passwd = ttls_password
        eap_connect.runtime_secs = 10
        eap_connect.setup()
        eap_connect.start()
        print("napping %f sec" % eap_connect.runtime_secs)
        time.sleep(eap_connect.runtime_secs)
        eap_connect.stop()
        eap_connect.cleanup()
        run_results = eap_connect.get_result_list()
        for result in run_results:
            print("test result: " + result)
        # result = 'pass'
        print("Single Client Connectivity :", eap_connect.passes)
        if eap_connect.passes() == True:
            print("Single client connection to", ssid_name, "successful. Test Passed")
            client.update_testrail(case_id=test_case, run_id=rid, status_id=1, msg='Client connectivity passed')
            logger.info("Client connectivity to " + ssid_name + " Passed")
            return ("passed")
        else:
            client.update_testrail(case_id=test_case, run_id=rid, status_id=5, msg='Client connectivity failed')
            print("Single client connection to", ssid_name, "unsuccessful. Test Failed")
            logger.warning("Client connectivity to " + ssid_name + " FAILED")
            return ("failed")

    def testrail_retest(self, test_case, rid, ssid_name):
        client.update_testrail(case_id=test_case, run_id=rid, status_id=4, msg='Error in Client Connectivity Test. Needs to be Re-run')
        print("Error in test for single client connection to", ssid_name)
        logger.warning("ERROR testing Client connectivity to " + ssid_name)

######Testrail Project and Run ID Information ##############################

Test: RunTest = RunTest()

projId = client.get_project_id(project_name= projectId)
print("TIP WLAN Project ID is:", projId)

logger.info('Start of Nightly Sanity')

###Dictionaries
ap_latest_dict = {
  "ec420": "Unknown",
  "ea8300": "Unknown",
  "ecw5211": "unknown",
  "ecw5410": "unknown"
}

#All values start empty
ap_updated_dict = {
  "ec420": "",
  "ea8300": "",
  "ecw5211": "",
  "ecw5410": ""
}

#import json file used by throughput test
sanity_status = json.load(open("sanity_status.json"))


##Equipment IDs for Lab APs under test
from lab_ap_info import equipment_id_dict
from lab_ap_info import profile_info_dict
from lab_ap_info import cloud_sdk_models
from lab_ap_info import equipment_ip_dict
from lab_ap_info import eqiupment_credentials_dict


##Test Cases to be included in Test Runs
test_cases = [
       2233,
       2236,
       2237,
       2419,
       2420,
       4323,
       4324,
       4325,
       4326,
       5214,
       5215,
       5216,
       5217,
       5222,
       5247,
       5248,
       5249,
       5250,
       5251,
       5252,
       5253,
       5540,
       5541,
       5542,
       5543,
       5544,
       5545,
       5546,
       5547,
       5548
]

##AP models for jfrog
ap_models = ["ec420","ea8300","ecw5211","ecw5410"]
#ap_models = ["ecw5410"]

############################################################################
#################### Create Report #########################################
############################################################################

# Create Report Folder for Today
today = str(date.today())
try:
    os.mkdir(report_path+today)
except OSError:
    print ("Creation of the directory %s failed" % report_path)
else:
    print ("Successfully created the directory %s " % report_path)

logger.info('Report data can be found here: '+report_path+today)

#Copy report template to folder. If template doesn't exist, continue anyway with log
try:
    copyfile(report_template,report_path+today+'/report.php')

except:
    print("No report template created. Report data will still be saved. Continuing with tests...")

##Create report_data dictionary
tc_results = dict.fromkeys(test_cases, "not run")

report_data = dict()
report_data['cloud_sdk'] = {
               "ea8300" : "",
               "ecw5211": "",
               "ecw5410": "",
               "ec420": ""
              }
report_data["fw_available"] = dict.fromkeys(ap_models,"Unknown")
report_data["fw_under_test"] = dict.fromkeys(ap_models,"N/A")
report_data['pass_percent'] = dict.fromkeys(ap_models,"")
report_data['tests'] = {
               "ea8300" : "",
               "ecw5211": "",
               "ecw5410": "",
               "ec420": ""
              }
for key in ap_models:
       report_data['tests'][key] = dict.fromkeys(test_cases,"not run")

print(report_data)

#write to report_data contents to json file so it has something in case of unexpected fail
with open(report_path+today+'/report_data.json', 'w') as report_json_file:
    json.dump(report_data, report_json_file)

###Get Cloud Bearer Token
bearer = CloudSDK.get_bearer(cloudSDK_url)

#############################################################################
##################### CloudSDK Firmware Check ###############################
### 1) Get Token for CloudSDK ###############################################
### 2) Find Latest FW on jfrog for each AP Model ############################
### 3) Find Available FW on CloudSDK --> if Latest FW not present, upload ###
#############################################################################

###Check Latest FW Version on jfrog and CloudSDK for each model
for model in ap_models:
    apModel = model
    cloudModel = cloud_sdk_models[apModel]
    #print(cloudModel)
    ###Check Latest FW on jFrog
    jfrog_url = 'https://tip.jfrog.io/artifactory/tip-wlan-ap-firmware/'
    url = jfrog_url + apModel + "/dev/"
    Build: GetBuild = GetBuild()
    latest_image = Build.get_latest_image(url)
    print(model,"Latest FW on jFrog:",latest_image)
    ap_latest_dict[model] = latest_image

####################################################################################
############ Update FW and Run Test Cases on Each AP Variant #######################
####################################################################################
####################################################################################

for key in equipment_id_dict:
    ##Get Bearer Token to make sure its valid (long tests can require re-auth)
    bearer = CloudSDK.get_bearer(cloudSDK_url)

    ###Get Current AP Firmware and upgrade
    customer_id = "2"
    equipment_id = equipment_id_dict[key]
    ap_ip = equipment_ip_dict[key]
    ap_username = "root"
    ap_password = eqiupment_credentials_dict[key]
    print("AP MODEL UNDER TEST IS", key)
    # ap_fw = CloudSDK.ap_firmware(customer_id,equipment_id,cloudSDK_url,bearer)
    try:
        ap_cli_info = ssh_cli_active_fw(ap_ip, ap_username, ap_password)
        ap_cli_fw = ap_cli_info['active_fw']
    except:
        ap_cli_info = "ERROR"
        print("Cannot Reach AP CLI, will not test this variant")
        continue

    fw_model = ap_cli_fw.partition("-")[0]
    print('Current Active AP FW from CLI:', ap_cli_fw)
    ###Find Latest FW for Current AP Model and Get FW ID

    ##Compare Latest and Current AP FW and Upgrade
    latest_ap_image = ap_latest_dict[fw_model]
    if ap_cli_fw == latest_ap_image:
        print('FW does not require updating')
        report_data['fw_available'][key] = "No"
        logger.info(fw_model + " does not require upgrade. Not performing sanity tests for this AP variant")
        cloudsdk_cluster_info = {
            "date": "N/A",
            "commitId": "N/A",
            "projectVersion": "N/A"
        }
        report_data['cloud_sdk'][key] = cloudsdk_cluster_info

    else:
        print('FW needs updating')
        report_data['fw_available'][key] = "Yes"
        report_data['fw_under_test'][key] = latest_ap_image

        ###Create Test Run
        today = str(date.today())
        test_run_name = "Daily_Sanity_" + fw_model + "_" + today + "_" + latest_ap_image
        client.create_testrun(name=test_run_name, case_ids=test_cases, project_id=projId, milestone_id=milestoneId, description="Automated Nightly Sanity test run for new firmware build")
        rid = client.get_run_id(test_run_name="Daily_Sanity_" + fw_model + "_" + today + "_" + latest_ap_image)
        print("TIP run ID is:", rid)

        ###GetCloudSDK Version
        print("Getting CloudSDK version information...")
        try:
            cluster_ver = CloudSDK.get_cloudsdk_version(cloudSDK_url, bearer)
            print("CloudSDK Version Information:")
            print("-------------------------------------------")
            print(cluster_ver)
            print("-------------------------------------------")

            cloudsdk_cluster_info = {}
            cloudsdk_cluster_info['date'] = cluster_ver['commitDate']
            cloudsdk_cluster_info['commitId'] = cluster_ver['commitID']
            cloudsdk_cluster_info['projectVersion'] = cluster_ver['projectVersion']
            report_data['cloud_sdk'][key] = cloudsdk_cluster_info
            logger.info('CloudSDK version info: ',cluster_ver)
            client.update_testrail(case_id="5540", run_id=rid, status_id=1, msg='Read CloudSDK version from API successfully')
            report_data['tests'][key][5540] = "passed"

        except:
            cluster_ver = 'error'
            print("ERROR: CloudSDK Version Unavailable")
            logger.info('CloudSDK version Unavailable')
            cloudsdk_cluster_info = {
                "date": "unknown",
                "commitId": "unknown",
                "projectVersion": "unknown"
            }
            client.update_testrail(case_id="5540", run_id=rid, status_id=5, msg='Could not read CloudSDK version from API')
            report_data['cloud_sdk'][key] = cloudsdk_cluster_info
            report_data['tests'][key][5540] = "failed"

        with open(report_path + today + '/report_data.json', 'w') as report_json_file:
            json.dump(report_data, report_json_file)

        ###Test Create Firmware Version
        latest_image = ap_latest_dict[key]
        cloudModel = cloud_sdk_models[key]
        print(cloudModel)
        firmware_list_by_model = CloudSDK.CloudSDK_images(cloudModel, cloudSDK_url, bearer)
        print("Available", cloudModel, "Firmware on CloudSDK:", firmware_list_by_model)

        if latest_image in firmware_list_by_model:
            print("Latest Firmware", latest_image, "is already on CloudSDK, need to delete to test create FW API")
            old_fw_id = CloudSDK.get_firmware_id(latest_image, cloudSDK_url, bearer)
            delete_fw = CloudSDK.delete_firmware(str(old_fw_id), cloudSDK_url, bearer)
            fw_url = "https://" + jfrog_user + ":" + jfrog_pwd + "@tip.jfrog.io/artifactory/tip-wlan-ap-firmware/" + key + "/dev/" + latest_image + ".tar.gz"
            commit = latest_image.split("-")[-1]
            try:
                fw_upload_status = CloudSDK.firwmare_upload(commit, cloudModel, latest_image, fw_url, cloudSDK_url, bearer)
                fw_id = fw_upload_status['id']
                print("Upload Complete.", latest_image, "FW ID is", fw_id)
                client.update_testrail(case_id="5548", run_id=rid, status_id=1, msg='Create new FW version by API successful')
                report_data['tests'][key][5548] = "passed"
            except:
                fw_upload_status = 'error'
                print("Unable to upload new FW version. Skipping Sanity on AP Model")
                client.update_testrail(case_id="5548", run_id=rid, status_id=5, msg='Error creating new FW version by API')
                report_data['tests'][key][5548] = "failed"
                continue
        else:
            print("Latest Firmware is not on CloudSDK! Uploading...")
            fw_url = "https://" + jfrog_user + ":" + jfrog_pwd + "@tip.jfrog.io/artifactory/tip-wlan-ap-firmware/" + key + "/dev/" + latest_image + ".tar.gz"
            commit = latest_image.split("-")[-1]
            try:
                fw_upload_status = CloudSDK.firwmare_upload(commit, cloudModel, latest_image, fw_url, cloudSDK_url, bearer)
                fw_id = fw_upload_status['id']
                print("Upload Complete.", latest_image, "FW ID is", fw_id)
                client.update_testrail(case_id="5548", run_id=rid, status_id=1, msg='Create new FW version by API successful')
                report_data['tests'][key][5548] = "passed"
            except:
                fw_upload_status = 'error'
                print("Unable to upload new FW version. Skipping Sanity on AP Model")
                client.update_testrail(case_id="5548", run_id=rid, status_id=5, msg='Error creating new FW version by API')
                report_data['tests'][key][5548] = "failed"
                continue

        # Upgrade AP firmware
        print("Upgrading...firmware ID is: ",fw_id)
        upgrade_fw = CloudSDK.update_firmware(equipment_id, str(fw_id), cloudSDK_url, bearer)
        logger.info("Lab "+fw_model+" Requires FW update")
        print(upgrade_fw)
        if upgrade_fw["success"] == True:
            print("CloudSDK Upgrade Request Success")
            report_data['tests'][key][5547] = "passed"
            client.update_testrail(case_id="5547", run_id=rid, status_id=1, msg='Upgrade request using API successful')
            logger.info('Firmware upgrade API successfully sent')
        else:
            print("Cloud SDK Upgrade Request Error!")
            # mark upgrade test case as failed with CloudSDK error
            client.update_testrail(case_id="5547", run_id=rid, status_id=5, msg='Error requesting upgrade via API')
            report_data['tests'][key][5547] = "failed"
            logger.warning('Firmware upgrade API failed to send')
            continue

        time.sleep(300)

        # Check if upgrade success is displayed on CloudSDK
        cloud_ap_fw = CloudSDK.ap_firmware(customer_id, equipment_id, cloudSDK_url, bearer)
        print('Current AP Firmware from CloudSDK:', cloud_ap_fw)
        logger.info('AP Firmware from CloudSDK: '+cloud_ap_fw)
        if cloud_ap_fw == "ERROR":
            print("AP FW Could not be read from CloudSDK")

        elif cloud_ap_fw == latest_ap_image:
            print("CloudSDK status shows upgrade successful!")

        else:
            print("AP FW from CloudSDK status is not latest build. Will check AP CLI.")

        # Check if upgrade successful on AP CLI
        try:
            ap_cli_info = ssh_cli_active_fw(ap_ip, ap_username, ap_password)
            ap_cli_fw = ap_cli_info['active_fw']
            print("CLI reporting AP Active FW as:", ap_cli_fw)
            logger.info('Firmware from CLI: ' + ap_cli_fw)
        except:
            ap_cli_info = "ERROR"
            print("Cannot Reach AP CLI to confirm upgrade!")
            logger.warning('Cannot Reach AP CLI to confirm upgrade!')
            client.update_testrail(case_id="2233", run_id=rid, status_id=4, msg='Cannot reach AP after upgrade to check CLI - re-test required')
            continue

        if cloud_ap_fw == latest_ap_image and ap_cli_fw == latest_ap_image:
            print("CloudSDK and AP CLI both show upgrade success, passing upgrade test case")
            client.update_testrail(case_id="2233", run_id=rid, status_id=1, msg='Upgrade to ' + latest_ap_image + ' successful')
            client.update_testrail(case_id="5247", run_id=rid, status_id=1, msg='CLOUDSDK reporting correct firmware version.')
            report_data['tests'][key][2233] = "passed"
            report_data['tests'][key][5247] = "passed"
            print(report_data['tests'][key])

        elif cloud_ap_fw != latest_ap_image and ap_cli_fw == latest_ap_image:
            print("AP CLI shows upgrade success - CloudSDK reporting error!")
            ##Raise CloudSDK error but continue testing
            client.update_testrail(case_id="2233", run_id=rid, status_id=1, msg='Upgrade to ' + latest_ap_image + ' successful.')
            client.update_testrail(case_id="5247", run_id=rid, status_id=5,msg='CLOUDSDK reporting incorrect firmware version.')
            report_data['tests'][key][2233] = "passed"
            report_data['tests'][key][5247] = "failed"
            print(report_data['tests'][key])

        elif cloud_ap_fw == latest_ap_image and ap_cli_fw != latest_ap_image:
            print("AP CLI shows upgrade failed - CloudSDK reporting error!")
            # Testrail TC fail
            client.update_testrail(case_id="2233", run_id=rid, status_id=5, msg='AP failed to download or apply new FW. Upgrade to ' + latest_ap_image + ' Failed')
            client.update_testrail(case_id="5247", run_id=rid, status_id=5,msg='CLOUDSDK reporting incorrect firmware version.')
            report_data['tests'][key][2233] = "failed"
            report_data['tests'][key][5247] = "failed"
            print(report_data['tests'][key])
            continue

        elif cloud_ap_fw != latest_ap_image and ap_cli_fw != latest_ap_image:
            print("Upgrade Failed! Confirmed on CloudSDK and AP CLI. Upgrade test case failed.")
            ##fail TR testcase and exit
            client.update_testrail(case_id="2233", run_id=rid, status_id=5, msg='AP failed to download or apply new FW. Upgrade to ' + latest_ap_image + ' Failed')
            report_data['tests'][key][2233] = "failed"
            print(report_data['tests'][key])
            continue

        else:
            print("Unable to determine upgrade status. Skipping AP variant")
            # update TR testcase as error
            client.update_testrail(case_id="2233", run_id=rid, status_id=4, msg='Cannot determine upgrade status - re-test required')
            report_data['tests'][key][2233] = "error"
            print(report_data['tests'][key])
            continue

        print(report_data)

        ###Check AP Manager Status
        manager_status = ap_cli_info['state']

        if manager_status != "active":
            print("Manager status is " + manager_status + "! Not connected to the cloud.")
            print("Waiting 30 seconds and re-checking status")
            time.sleep(30)
            ap_cli_info = ssh_cli_active_fw(ap_ip, ap_username, ap_password)
            manager_status = ap_cli_info['state']
            if manager_status != "active":
                print("Manager status is", manager_status, "! Not connected to the cloud.")
                print("Manager status fails multiple checks - failing test case.")
                ##fail cloud connectivity testcase
                client.update_testrail(case_id="5222", run_id=rid, status_id=5, msg='CloudSDK connectivity failed')
                report_data['tests'][key][5222] = "failed"
                print(report_data['tests'][key])
                continue
            else:
                print("Manager status is Active. Proceeding to connectivity testing!")
                # TC522 pass in Testrail
                client.update_testrail(case_id="5222", run_id=rid, status_id=1, msg='Manager status is Active')
                report_data['tests'][key][5222] = "passed"
                print(report_data['tests'][key])
        else:
            print("Manager status is Active. Proceeding to connectivity testing!")
            # TC5222 pass in testrail
            client.update_testrail(case_id="5222", run_id=rid, status_id=1, msg='Manager status is Active')
            report_data['tests'][key][5222] = "passed"
            print(report_data['tests'][key])
            # Pass cloud connectivity test case

        ###Update report json
        with open(report_path + today + '/report_data.json', 'w') as report_json_file:
            json.dump(report_data, report_json_file)

        ###########################################################################
        ############## Bridge Mode Client Connectivity ############################
        ###########################################################################

        ###Set Proper AP Profile for Bridge SSID Tests
        test_profile_id = profile_info_dict[fw_model]["profile_id"]
        print(test_profile_id)
        ap_profile = CloudSDK.set_ap_profile(equipment_id, test_profile_id, cloudSDK_url, bearer)

        ### Wait for Profile Push
        time.sleep(180)

        ###Check if VIF Config and VIF State reflect AP Profile from CloudSDK
        ## VIF Config
        try:
            ssid_config = profile_info_dict[key]["ssid_list"]
            print("SSIDs in AP Profile:", ssid_config)

            ssid_list = ap_ssh.get_vif_config(ap_ip, ap_username, ap_password)
            print("SSIDs in AP VIF Config:", ssid_list)

            if set(ssid_list) == set(ssid_config):
                print("SSIDs in Wifi_VIF_Config Match AP Profile Config")
                client.update_testrail(case_id="5541", run_id=rid, status_id=1, msg='SSIDs in VIF Config matches AP Profile Config')
                report_data['tests'][key][5541] = "passed"
            else:
                print("SSIDs in Wifi_VIF_Config do not match desired AP Profile Config")
                client.update_testrail(case_id="5541", run_id=rid, status_id=5, msg='SSIDs in VIF Config do not match AP Profile Config')
                report_data['tests'][key][5541] = "failed"
        except:
            ssid_list = "ERROR"
            print("Error accessing VIF Config from AP CLI")
            client.update_testrail(case_id="5541", run_id=rid, status_id=4, msg='Cannot determine VIF Config - re-test required')
            report_data['tests'][key][5541] = "error"
        # VIF State
        try:
            ssid_state = ap_ssh.get_vif_state(ap_ip, ap_username, ap_password)
            print("SSIDs in AP VIF State:", ssid_state)

            if set(ssid_state) == set(ssid_config):
                print("SSIDs properly applied on AP")
                client.update_testrail(case_id="5544", run_id=rid, status_id=1, msg='SSIDs in VIF Config applied to VIF State')
                report_data['tests'][key][5544] = "passed"
            else:
                print("SSIDs not applied on AP")
                client.update_testrail(case_id="5544", run_id=rid, status_id=5, msg='SSIDs in VIF Config not applied to VIF State')
                report_data['tests'][key][5544] = "failed"
        except:
            ssid_list = "ERROR"
            print("Error accessing VIF State from AP CLI")
            print("Error accessing VIF Config from AP CLI")
            client.update_testrail(case_id="5544", run_id=rid, status_id=4, msg='Cannot determine VIF State - re-test required')
            report_data['tests'][key][5544] = "error"

        ### Set LANForge port for tests
        port = "eth2"

        #print iwinfo for information
        iwinfo = iwinfo_status(ap_ip, ap_username, ap_password)
        print(iwinfo)

        ###Run Client Single Connectivity Test Cases for Bridge SSIDs
        # TC5214 - 2.4 GHz WPA2-Enterprise
        test_case = "5214"
        radio = "wiphy0"
        sta_list = ["eap5214"]
        ssid_name = profile_info_dict[fw_model]["twoFourG_WPA2-EAP_SSID"]
        security = "wpa2"
        eap_type = "TTLS"
        try:
            test_result = RunTest.Single_Client_EAP(port, sta_list, ssid_name, radio, security, eap_type, identity, ttls_password, test_case, rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        ###Run Client Single Connectivity Test Cases for Bridge SSIDs
        # TC 2237 - 2.4 GHz WPA2
        test_case = "2237"
        radio = "wiphy0"
        station = ["test2237"]
        ssid_name = profile_info_dict[fw_model]["twoFourG_WPA2_SSID"]
        ssid_psk = profile_info_dict[fw_model]["twoFourG_WPA2_PSK"]
        security = "wpa2"
        try:
            test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case,
                                                          rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 2420 - 2.4 GHz WPA
        test_case = "2420"
        radio = "wiphy0"
        station = ["test2420"]
        ssid_name = profile_info_dict[fw_model]["twoFourG_WPA_SSID"]
        ssid_psk = profile_info_dict[fw_model]["twoFourG_WPA_PSK"]
        security = "wpa"
        try:
            test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case,
                                                          rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 2234 - 2.4 GHz Open
        # test_case = "2234"
        # radio = "wiphy0"
        # station = ["test2234"]
        # ssid_name = profile_info_dict[fw_model]["twoFourG_OPEN_SSID"]
        # ssid_psk = "BLANK"
        # security = "open"
        # test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case, rid)
        # report_data['tests'][key][int(test_case)] = test_result

        # time.sleep(10)

        # TC5215 - 5 GHz WPA2-Enterprise
        test_case = "5215"
        radio = "wiphy3"
        sta_list = ["eap5215"]
        ssid_name = profile_info_dict[fw_model]["fiveG_WPA2-EAP_SSID"]
        security = "wpa2"
        eap_type = "TTLS"
        try:
            test_result = RunTest.Single_Client_EAP(port, sta_list, ssid_name, radio, security, eap_type, identity, ttls_password, test_case, rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 2236 - 5 GHz WPA2
        test_case = "2236"
        radio = "wiphy3"
        station = ["test2236"]
        ssid_name = profile_info_dict[fw_model]["fiveG_WPA2_SSID"]
        ssid_psk = profile_info_dict[fw_model]["fiveG_WPA2_PSK"]
        security = "wpa2"
        try:
            test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case,
                                                          rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 2419 - 5 GHz WPA
        test_case = "2419"
        radio = "wiphy3"
        station = ["test2419"]
        ssid_name = profile_info_dict[fw_model]["fiveG_WPA_SSID"]
        ssid_psk = profile_info_dict[fw_model]["fiveG_WPA_PSK"]
        security = "wpa"
        try:
            test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case,
                                                          rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 2235 - 5 GHz Open
        # test_case = "2235"
        # radio = "wiphy3"
        # station = ["test2235"]
        # ssid_name = profile_info_dict[fw_model]["fiveG_OPEN_SSID"]
        # ssid_psk = "BLANK"
        # security = "open"
        # test_result = Test.Single_Client_Connectivity(radio, ssid_name, ssid_psk, security, station, test_case, rid)
        # report_data['tests'][key][int(test_case)] = test_result

        logger.info("Testing for " + fw_model + "Bridge Mode SSIDs Complete")
        with open(report_path + today + '/report_data.json', 'w') as report_json_file:
            json.dump(report_data, report_json_file)

        ###########################################################################
        ################# NAT Mode Client Connectivity ############################
        ###########################################################################

        ###Set Proper AP Profile for NAT SSID Tests
        test_profile_id = profile_info_dict[fw_model + '_nat']["profile_id"]
        print(test_profile_id)
        ap_profile = CloudSDK.set_ap_profile(equipment_id, test_profile_id, cloudSDK_url, bearer)

        ### Wait for Profile Push
        time.sleep(180)

        ###Check if VIF Config and VIF State reflect AP Profile from CloudSDK
        ## VIF Config
        try:
            ssid_config = profile_info_dict[fw_model + '_nat']["ssid_list"]
            print("SSIDs in AP Profile:", ssid_config)

            ssid_list = ap_ssh.get_vif_config(ap_ip, ap_username, ap_password)
            print("SSIDs in AP VIF Config:", ssid_list)

            if set(ssid_list) == set(ssid_config):
                print("SSIDs in Wifi_VIF_Config Match AP Profile Config")
                client.update_testrail(case_id="5542", run_id=rid, status_id=1,
                                       msg='SSIDs in VIF Config matches AP Profile Config')
                report_data['tests'][key][5542] = "passed"
            else:
                print("SSIDs in Wifi_VIF_Config do not match desired AP Profile Config")
                client.update_testrail(case_id="5542", run_id=rid, status_id=5,
                                       msg='SSIDs in VIF Config do not match AP Profile Config')
                report_data['tests'][key][5542] = "failed"
        except:
            ssid_list = "ERROR"
            print("Error accessing VIF Config from AP CLI")
            client.update_testrail(case_id="5542", run_id=rid, status_id=4,
                                   msg='Cannot determine VIF Config - re-test required')
            report_data['tests'][key][5542] = "error"
        # VIF State
        try:
            ssid_state = ap_ssh.get_vif_state(ap_ip, ap_username, ap_password)
            print("SSIDs in AP VIF State:", ssid_state)

            if set(ssid_state) == set(ssid_config):
                print("SSIDs properly applied on AP")
                client.update_testrail(case_id="5545", run_id=rid, status_id=1,
                                       msg='SSIDs in VIF Config applied to VIF State')
                report_data['tests'][key][5545] = "passed"
            else:
                print("SSIDs not applied on AP")
                client.update_testrail(case_id="5545", run_id=rid, status_id=5,
                                       msg='SSIDs in VIF Config not applied to VIF State')
                report_data['tests'][key][5545] = "failed"
        except:
            ssid_list = "ERROR"
            print("Error accessing VIF State from AP CLI")
            print("Error accessing VIF Config from AP CLI")
            client.update_testrail(case_id="5545", run_id=rid, status_id=4,
                                   msg='Cannot determine VIF State - re-test required')
            report_data['tests'][key][5545] = "error"

        ### Set LANForge port for tests
        port = "eth2"

        #Print iwinfo for logs
        iwinfo = iwinfo_status(ap_ip, ap_username, ap_password)
        print(iwinfo)

        ###Run Client Single Connectivity Test Cases for NAT SSIDs
        # TC5216 - 2.4 GHz WPA2-Enterprise NAT
        test_case = "5216"
        radio = "wiphy0"
        sta_list = ["eap5216"]
        ssid_name = profile_info_dict[fw_model + '_nat']["twoFourG_WPA2-EAP_SSID"]
        security = "wpa2"
        eap_type = "TTLS"
        try:
            test_result = RunTest.Single_Client_EAP(port, sta_list, ssid_name, radio, security, eap_type, identity, ttls_password, test_case, rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)


        # TC 4325 - 2.4 GHz WPA2 NAT
        test_case = "4325"
        radio = "wiphy0"
        station = ["test4325"]
        ssid_name = profile_info_dict[fw_model + '_nat']["twoFourG_WPA2_SSID"]
        ssid_psk = profile_info_dict[fw_model + '_nat']["twoFourG_WPA2_PSK"]
        security = "wpa2"
        try:
            test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case,
                                                          rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 4323 - 2.4 GHz WPA NAT
        test_case = "4323"
        radio = "wiphy0"
        station = ["test4323"]
        ssid_name = profile_info_dict[fw_model + '_nat']["twoFourG_WPA_SSID"]
        ssid_psk = profile_info_dict[fw_model + '_nat']["twoFourG_WPA_PSK"]
        security = "wpa"
        try:
            test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case, rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 4321 - 2.4 GHz Open NAT
        # test_case = "4321"
        # radio = "wiphy0"
        # station = ["test4321"]
        # ssid_name = profile_info_dict[fw_model+'_nat']["twoFourG_OPEN_SSID"]
        # ssid_psk = "BLANK"
        # security = "open"
        # test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case, rid)
        # report_data['tests'][key][int(test_case)] = test_result

        # time.sleep(10)

        # TC5108 - 5 GHz WPA2-Enterprise NAT
        test_case = "5217"
        radio = "wiphy3"
        sta_list = ["eap5217"]
        ssid_name = profile_info_dict[fw_model + '_nat']["fiveG_WPA2-EAP_SSID"]
        security = "wpa2"
        eap_type = "TTLS"
        try:
            test_result = RunTest.Single_Client_EAP(port, sta_list, ssid_name, radio, security, eap_type, identity, ttls_password, test_case, rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 4326 - 5 GHz WPA2 NAT
        test_case = "4326"
        radio = "wiphy3"
        station = ["test4326"]
        ssid_name = profile_info_dict[fw_model + '_nat']["fiveG_WPA2_SSID"]
        ssid_psk = profile_info_dict[fw_model]["fiveG_WPA2_PSK"]
        security = "wpa2"
        try:
            test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case,
                                                          rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 4324 - 5 GHz WPA NAT
        test_case = "4324"
        radio = "wiphy3"
        station = ["test4324"]
        ssid_name = profile_info_dict[fw_model + '_nat']["fiveG_WPA_SSID"]
        ssid_psk = profile_info_dict[fw_model]["fiveG_WPA_PSK"]
        security = "wpa"
        try:
            test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case,
                                                          rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 4322 - 5 GHz Open NAT
        # test_case = "4322"
        # radio = "wiphy3"
        # station = ["test4322"]
        # ssid_name = profile_info_dict[fw_model+'_nat']["fiveG_OPEN_SSID"]
        # ssid_psk = "BLANK"
        # security = "open"
        # test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case, rid)
        # report_data['tests'][key][int(test_case)] = test_result

        logger.info("Testing for " + fw_model + "NAT Mode SSIDs Complete")
        with open(report_path + today + '/report_data.json', 'w') as report_json_file:
            json.dump(report_data, report_json_file)

        ###########################################################################
        ################# Customer VLAN Client Connectivity #######################
        ###########################################################################

        ###Set Proper AP Profile for VLAN SSID Tests
        test_profile_id = profile_info_dict[fw_model + '_vlan']["profile_id"]
        print(test_profile_id)
        ap_profile = CloudSDK.set_ap_profile(equipment_id, test_profile_id, cloudSDK_url, bearer)

        ### Wait for Profile Push
        time.sleep(180)

        ###Check if VIF Config and VIF State reflect AP Profile from CloudSDK
        ## VIF Config
        try:
            ssid_config = profile_info_dict[fw_model + '_vlan']["ssid_list"]
            print("SSIDs in AP Profile:", ssid_config)

            ssid_list = ap_ssh.get_vif_config(ap_ip, ap_username, ap_password)
            print("SSIDs in AP VIF Config:", ssid_list)

            if set(ssid_list) == set(ssid_config):
                print("SSIDs in Wifi_VIF_Config Match AP Profile Config")
                client.update_testrail(case_id="5543", run_id=rid, status_id=1,
                                       msg='SSIDs in VIF Config matches AP Profile Config')
                report_data['tests'][key][5543] = "passed"
            else:
                print("SSIDs in Wifi_VIF_Config do not match desired AP Profile Config")
                client.update_testrail(case_id="5543", run_id=rid, status_id=5,
                                       msg='SSIDs in VIF Config do not match AP Profile Config')
                report_data['tests'][key][5543] = "failed"
        except:
            ssid_list = "ERROR"
            print("Error accessing VIF Config from AP CLI")
            client.update_testrail(case_id="5543", run_id=rid, status_id=4, msg='Cannot determine VIF Config - re-test required')
            report_data['tests'][key][5543] = "error"
        # VIF State
        try:
            ssid_state = ap_ssh.get_vif_state(ap_ip, ap_username, ap_password)
            print("SSIDs in AP VIF State:", ssid_state)

            if set(ssid_state) == set(ssid_config):
                print("SSIDs properly applied on AP")
                client.update_testrail(case_id="5546", run_id=rid, status_id=1, msg='SSIDs in VIF Config applied to VIF State')
                report_data['tests'][key][5546] = "passed"
            else:
                print("SSIDs not applied on AP")
                client.update_testrail(case_id="5546", run_id=rid, status_id=5, msg='SSIDs in VIF Config not applied to VIF State')
                report_data['tests'][key][5546] = "failed"
        except:
            ssid_list = "ERROR"
            print("Error accessing VIF State from AP CLI")
            print("Error accessing VIF Config from AP CLI")
            client.update_testrail(case_id="5546", run_id=rid, status_id=4,
                                   msg='Cannot determine VIF State - re-test required')
            report_data['tests'][key][5546] = "error"

        ### Set port for LANForge
        port = "vlan100"

        # Print iwinfo for logs
        iwinfo = iwinfo_status(ap_ip, ap_username, ap_password)
        print(iwinfo)

        ###Run Client Single Connectivity Test Cases for VLAN SSIDs
        # TC5216 - 2.4 GHz WPA2-Enterprise VLAN
        test_case = "5253"
        radio = "wiphy0"
        sta_list = ["eap5253"]
        ssid_name = profile_info_dict[fw_model + '_vlan']["twoFourG_WPA2-EAP_SSID"]
        security = "wpa2"
        eap_type = "TTLS"
        try:
            test_result = RunTest.Single_Client_EAP(port, sta_list, ssid_name, radio, security, eap_type, identity,
                                                    ttls_password, test_case, rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 4325 - 2.4 GHz WPA2 VLAN
        test_case = "5251"
        radio = "wiphy0"
        station = ["test5251"]
        ssid_name = profile_info_dict[fw_model + '_vlan']["twoFourG_WPA2_SSID"]
        ssid_psk = profile_info_dict[fw_model + '_vlan']["twoFourG_WPA2_PSK"]
        security = "wpa2"
        try:
            test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case,
                                                          rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 4323 - 2.4 GHz WPA VLAN
        test_case = "5252"
        radio = "wiphy0"
        station = ["test5252"]
        ssid_name = profile_info_dict[fw_model + '_vlan']["twoFourG_WPA_SSID"]
        ssid_psk = profile_info_dict[fw_model + '_vlan']["twoFourG_WPA_PSK"]
        security = "wpa"
        try:
            test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case, rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 4321 - 2.4 GHz Open VLAN
        # test_case = "4321"
        # radio = "wiphy0"
        # station = ["test4321"]
        # ssid_name = profile_info_dict[fw_model+'_vlan']["twoFourG_OPEN_SSID"]
        # ssid_psk = "BLANK"
        # security = "open"
        # test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case, rid)
        # report_data['tests'][key][int(test_case)] = test_result

        # time.sleep(10)

        # TC5108 - 5 GHz WPA2-Enterprise VLAN
        test_case = "5250"
        radio = "wiphy3"
        sta_list = ["eap5250"]
        ssid_name = profile_info_dict[fw_model + '_vlan']["fiveG_WPA2-EAP_SSID"]
        security = "wpa2"
        eap_type = "TTLS"
        try:
            test_result = RunTest.Single_Client_EAP(port, sta_list, ssid_name, radio, security, eap_type, identity,
                                                    ttls_password, test_case, rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 4326 - 5 GHz WPA2 VLAN
        test_case = "5248"
        radio = "wiphy3"
        station = ["test5248"]
        ssid_name = profile_info_dict[fw_model + '_vlan']["fiveG_WPA2_SSID"]
        ssid_psk = profile_info_dict[fw_model]["fiveG_WPA2_PSK"]
        security = "wpa2"
        try:
            test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case,
                                                          rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        # TC 4324 - 5 GHz WPA VLAN
        test_case = "5249"
        radio = "wiphy3"
        station = ["test5249"]
        ssid_name = profile_info_dict[fw_model + '_vlan']["fiveG_WPA_SSID"]
        ssid_psk = profile_info_dict[fw_model]["fiveG_WPA_PSK"]
        security = "wpa"
        try:
            test_result = Test.Single_Client_Connectivity(port, radio, ssid_name, ssid_psk, security, station, test_case,
                                                          rid)
        except:
            test_result = "error"
            Test.testrail_retest(test_case, rid, ssid_name)
            pass
        report_data['tests'][key][int(test_case)] = test_result
        print(report_data['tests'][key])

        time.sleep(10)

        logger.info("Testing for " + fw_model + "Custom VLAN SSIDs Complete")

        logger.info("Testing for " +fw_model+ "Complete")


        #Add indication of complete TC pass/fail to sanity_status for pass to external json used by Throughput Test
        x = all(status == "passed" for status in report_data["tests"][key].values())
        print(x)

        if x == True:
            sanity_status['sanity_status'][key] = "passed"

        else:
            sanity_status['sanity_status'][key] = "failed"

        ##Update sanity_status.json to indicate there has been a test on at least one AP model tonight
        sanity_status['sanity_run']['new_data'] = "yes"

        print(sanity_status)

        #write to json file
        with open('sanity_status.json', 'w') as json_file:
            json.dump(sanity_status, json_file)


        # write to report_data contents to json file so it has something in case of unexpected fail
        print(report_data)
        with open(report_path + today + '/report_data.json', 'w') as report_json_file:
            json.dump(report_data, report_json_file)

#Dump all sanity test results to external json file again just to be sure
with open('sanity_status.json', 'w') as json_file:
  json.dump(sanity_status, json_file)

#Calculate percent of tests passed for report
for key in ap_models:
    if report_data['fw_available'][key] is "No":
        report_data["pass_percent"][key] = "Not Run"
    else:
        no_of_tests = len(report_data["tests"][key])
        passed_tests = sum(x == "passed" for x in report_data["tests"][key].values())
        print(passed_tests)
        percent = float(passed_tests / no_of_tests) * 100
        percent_pass = round(percent, 2)
        print(key, "pass rate is", str(percent_pass) + "%")
        report_data["pass_percent"][key] = str(percent_pass)+'%'


#write to report_data contents to json file
print(report_data)
with open(report_path+today+'/report_data.json', 'w') as report_json_file:
    json.dump(report_data, report_json_file)

print(".....End of Sanity Test.....")
logger.info("End of Sanity Test run")
