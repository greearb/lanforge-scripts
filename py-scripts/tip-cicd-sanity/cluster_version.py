##################################################################################
# Used to login to AWS and determine current CloudSDK version
# Requires user to install chromedriver and specify path
#
# Used by Nightly_Sanity #########################################################
##################################################################################

import time
from threading import Thread

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import os
import subprocess

user=os.getenv('AWS_USER')
password=os.getenv('AWS_PWD')
chromedriver_dir=os.getenv('CHROMEDRIVER_PATH')
print(chromedriver_dir)

def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=chromedriver_dir, options=chrome_options)
    driver.get("https://telecominfraproject.awsapps.com/start#")
    time.sleep(10);
    elem = driver.find_element_by_xpath('//*[@id="awsui-input-0"]')
    elem.send_keys(user);
    elem.send_keys(Keys.ENTER)

    time.sleep(5);
    elem2 = driver.find_element_by_xpath('//*[@id="awsui-input-1"]')
    elem2.send_keys(password)
    elem2.send_keys(Keys.ENTER)

    time.sleep(10);
    driver.find_element_by_xpath("//*[@id=\"app-03e8643328913682\"]").click()
    time.sleep(2);
    driver.find_element_by_xpath("//*[@id=\"ins-9f89e35be3e67abf\"]/div/div/img").click()
    time.sleep(5);

    driver.find_element_by_xpath("//*[@id=\"temp-credentials-button\"]").click()
    time.sleep(2);
    AWS_ACCESS_KEY_ID = driver.find_element_by_xpath("//*[@id=\"env-var-linux\"]/div[1]").text
    AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID[26:-1]
    AWS_SECRET_ACCESS_KEY = driver.find_element_by_xpath("//*[@id=\"env-var-linux\"]/div[2]").text
    AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY[30:-1]
    AWS_SESSION_TOKEN = driver.find_element_by_xpath("//*[@id=\"env-var-linux\"]/div[3]").text
    AWS_SESSION_TOKEN = AWS_SESSION_TOKEN[26:-1]
    driver.close()

    #print (AWS_ACCESS_KEY_ID)
    #print(AWS_SECRET_ACCESS_KEY)
    #print(AWS_SESSION_TOKEN)
    # //*[@id="env-var-linux"]/div[2]/text()
    # //*[@id="env-var-linux"]/div[3]/text()


    #os.chdir('/Users/bealla/.kube')

    os.environ['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
    os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
    os.environ['AWS_SESSION_TOKEN'] = AWS_SESSION_TOKEN

    get_pods = subprocess.check_output("kubectl -n tip get pods | grep tip-wlan-opensync-gw-cloud", shell=True, universal_newlines=True)
    #print(get_pods)

    opensync = str(get_pods.split()[0])
    #print(opensync)

    version_info = subprocess.check_output("kubectl exec -it -n tip "+opensync+" -- cat commit.properties", shell=True, universal_newlines=True)
    return version_info




