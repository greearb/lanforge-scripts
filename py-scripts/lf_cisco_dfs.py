#!/usr/bin/env python3

import sys
import os
import pexpect

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

import argparse
#from LANforge.lfcli_base import LFCliBase
from LANforge import LFUtils
#import realm
from realm import Realm
import time
import datetime
import subprocess
import re
import csv
import random
import logging

# Check for the logs channel switching time and radar detected


FORMAT = '%(asctime)s %(name)s %(levelname)s: %(message)s'

# see https://stackoverflow.com/a/13306095/11014343
class FileAdapter(object):
    def __init__(self, logger):
        self.logger = logger
    def write(self, data):
        # NOTE: data can be a partial line, multiple lines
        data = data.strip() # ignore leading/trailing whitespace
        if data: # non-blank
           self.logger.info(data)
    def flush(self):
        pass  # leave it to logging to flush properly


################################################################################
# cisco controller class :This class will be left in this file to allow for the
# Scaling and Performance to be self contained and not impact other tests
################################################################################

class CreateCtlr():
    def __init__(self,
                _scheme,
                _port,
                _series,
                _ctlr,
                _prompt,
                _user,
                _passwd,
                _ap,
                _band,
                _chan_5ghz,
                _chan_24ghz,
                _chan_width,
                _ap_mode,
                _tx_power,
                _client_density,
                _cap_ctl_out):

        self.scheme = _scheme
        self.port   = _port
        self.series = _series
        self.ctlr = _ctlr
        self.prompt = _prompt
        self.user = _user
        self.passwd = _passwd
        self.ap = _ap
        self.band = _band
        self.chan_5ghz = _chan_5ghz
        self.chan_24ghz = _chan_24ghz
        self.chan_width = _chan_width
        self.ap_mode = _ap_mode
        self.tx_power = _tx_power
        self.cap_ctl_out = _cap_ctl_out
        self.client_density = 0

    def verify_controller(self,client_density):
        self.client_density = client_density
        try:
            logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {}".format(self.scheme,
                self.ctlr,self.port,self.prompt,self.user,
                self.passwd,self.ap,self.series,self.band,"summary"))

            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                       self.user, "-p", self.passwd,
                                       "-a", self.ap,"--series", self.series,"--action", "summary"], capture_output=True)
            pss = ctl_output.stdout.decode('utf-8', 'ignore')
            logg.info(pss)
        except subprocess.CalledProcessError as process_error:
            logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}"
                 .format(process_error.returncode, process_error.output))
            time.sleep(1)
            exit(1)
    

        # Find our station count
        searchap = False
        for line in pss.splitlines():
            if (line.startswith("---------")):
                searchap = True
                continue
            #TODO need to test with 9800 series to chelck the values
            if (searchap):
                pat = "%s\s+\S+\s+\S+\s+\S+\s+\S+.*  \S+\s+\S+\s+(\S+)\s+\["%(self.ap)
                #logg.info("AP line: %s"%(line))
                m = re.search(pat, line)
                if (m != None):
                    sta_count = m.group(1)
                    logg.info("AP line: %s"%(line))
                    logg.info("sta-count: %s"%(sta_count))
                    if (int(sta_count) != int(self.client_density)):
                        logg.info("WARNING: Cisco Controller reported %s stations, should be %s"%(sta_count, self.client_density))

    #show summary (to get AP) (3400/9800)
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 --action summary --series 9800 --log stdout
    def controller_show_summary(self):
        pss = ""
        try:
            logg.info("\
                    scheme: {} \
                    ctlr: {} \
                    port: {} \
                    prompt: {} \
                    user: {}  \
                    passwd: {} \
                    AP: {} \
                    series: {} \
                    band: {} \
                    action: {}".format(
                    self.scheme,
                    self.ctlr,
                    self.port,
                    self.prompt,
                    self.user,
                    self.passwd,
                    self.ap,
                    self.series,
                    self.band,
                    "summary"))

            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", 
                                        "--scheme", self.scheme, 
                                        "--prompt", self.prompt, 
                                        "--port", self.port, 
                                        "-d", self.ctlr, 
                                        "-u", self.user, 
                                        "-p", self.passwd,
                                        "-a", self.ap,
                                        "--series", self.series, 
                                        "--band", self.band, 
                                        "--action", "summary"], 
                                        capture_output=self.cap_ctl_out, 
                                        check=True)
            if self.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                logg.info(pss)

        except subprocess.CalledProcessError as process_error:
                logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}"
                    .format(process_error.returncode, process_error.output))
                time.sleep(1)
                exit(1)

        return pss

    #show ap dot11 5ghz summary (band defaults to 5ghz) --band a
    #show ap dot11 24ghz summary use --band b for 2.4 ghz
    #action advanced  (3400/9800)
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 --action advanced --series 9800 --log stdout
    def controller_show_ap_summary(self):
        pss = ""
        try:
            logg.info("\
                scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {}".format(self.scheme,
                self.ctlr,self.port,self.prompt,self.user,
                self.passwd,self.ap,self.series,self.band,"advanced"))

            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                    self.user, "-p", self.passwd,
                                    "-a", self.ap,"--series", self.series, "--band", self.band, "--action", "advanced"], 
                                    capture_output=True, check=True)

            pss = ctl_output.stdout.decode('utf-8', 'ignore')
            logg.info(pss)

        except subprocess.CalledProcessError as process_error:
            logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)
        return pss

    #show wlan summary
    def controller_show_wlan_summary(self):
        try:
            logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {}".format(self.scheme,
                self.ctlr,self.port,self.prompt,self.user,
                self.passwd,self.ap,self.series,self.band,"show wlan summary"))

            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                    self.user, "-p", self.passwd,
                                    "-a", self.ap,"--series", self.series, "--band", self.band, "--action", "show_wlan_summary"], 
                                    capture_output=self.cap_ctl_out, check=True)

            if self.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                logg.info(pss)

        except subprocess.CalledProcessError as process_error:
            logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)

    #disable AP
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action disable --series 9800
    def controller_disable_ap(self):
        try:
            logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {}".format(self.scheme,
                self.ctlr,self.port,self.prompt,self.user,
                self.passwd,self.ap,self.series,self.band,"disable"))

            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", 
                                    self.ctlr, "-u",self.user, "-p", self.passwd,
                                    "-a", self.ap,"--series", self.series, "--band", self.band, "--action", "disable"], 
                                    capture_output=self.cap_ctl_out, check=True)

            if self.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                logg.info(pss)

        except subprocess.CalledProcessError as process_error:
            logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)


    #disable wlan
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action disable_wlan --series 9800
    def controller_disable_wlan(self):
        try:
            logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} wlan: {} action: {}".format(self.scheme,
                self.ctlr,self.port,self.prompt,self.user,
                self.passwd,self.ap,self.series,self.band,self.wlan,"disable_wlan"))

            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                    self.user, "-p", self.passwd,
                                    "-a", self.ap,"--series", self.series, "--band", self.band,"--wlan", self.wlan, "--action", "disable_wlan"], 
                                    capture_output=self.cap_ctl_out, check=True)

            if self.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                logg.info(pss)

        except subprocess.CalledProcessError as process_error:
            logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)


    #disable network 5ghz
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action disable_network_5ghz --series 9800
    def controller_disable_network_5ghz(self):
        if self.series == "9800":
            try:
                logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {}".format(self.scheme,
                    self.ctlr,self.port,self.prompt,self.user,
                    self.passwd,self.ap,self.series,self.band,"disable_network_5ghz"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                        self.user, "-p", self.passwd,
                                        "-a", self.ap,"--series", self.series, "--band", self.band, "--action", "disable_network_5ghz"], 
                                        capture_output=self.cap_ctl_out, check=True)

                if self.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    logg.info(pss)

            except subprocess.CalledProcessError as process_error:
                logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            try:
                logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {} value: {}".format(self.scheme,
                    self.ctlr,self.port,self.prompt,self.user,self.passwd, self.ap, self.series,
                    self.band,"cmd","config 802.11a disable network"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                        self.user, "-p", self.passwd,
                                        "-a", self.ap,"--series", self.series, "--band", self.band, "--action", "cmd", "--value", "config 802.11a disable network"], 
                                        capture_output=self.cap_ctl_out, check=True)

                if self.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    logg.info(pss)

            except subprocess.CalledProcessError as process_error:
                logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)


    #disable network 24ghz
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action disable_network_24ghz --series 9800
    def controller_disable_network_24ghz(self):
        if self.series == "9800":
            try:
                logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {}".format(self.scheme,
                    self.ctlr,self.port,self.prompt,self.user,
                    self.passwd,self.ap,self.series,self.band,"disable_network_24ghz"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                        self.user, "-p", self.passwd,
                                        "-a", self.ap,"--series", self.series, "--band", self.band, "--action", "disable_network_24ghz"], 
                                        capture_output=self.cap_ctl_out, check=True)

                if self.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    logg.info(pss)

            except subprocess.CalledProcessError as process_error:
                logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            try:
                logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {} value: {}".format(self.scheme,
                    self.ctlr,self.port,self.prompt,self.user,self.passwd, self.ap, self.series,
                    self.band,"cmd","config 802.11b disable network"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                        self.user, "-p", self.passwd,
                                        "-a", self.ap,"--series", self.series, "--band", self.band, "--action", "cmd", "--value", "config 802.11b disable network"], 
                                        capture_output=self.cap_ctl_out, check=True)

                if self.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    logg.info(pss)

            except subprocess.CalledProcessError as process_error:
                logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)



    #set manual mode - Series 9800 must be set to manual mode
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action manual --series 9800
    # ap name <AP NAME> dot11 5ghz radio role manual client-serving
    def controller_role_manual(self):
        if self.series == "9800":
            try:
                logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {}".format(self.scheme,
                    self.ctlr,self.port,self.prompt,self.user,
                    self.passwd,self.ap,self.series,self.band,"manual"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                        self.user, "-p", self.passwd,
                                        "-a", self.ap,"--series", self.series, "--band", self.band, "--action", "manual"], 
                                        capture_output=self.cap_ctl_out, check=True)

                if self.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    logg.info(pss)

            except subprocess.CalledProcessError as process_error:
                logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            logg.info("Check the cisco_scheme used attemping 9800 series on 3504 controller: {}".format(self.scheme))

    #set manual mode - Series 9800 must be set to auto mode
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action auto --series 9800
    # ap name <AP NAME> dot11 5ghz radio role manual client-serving
    def controller_role_auto(self):
        if self.series == "9800":
            try:
                logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {}".format(self.scheme,
                    self.ctlr,self.port,self.prompt,self.user,
                    self.passwd,self.ap,self.series,self.band,"auto"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                        self.user, "-p", self.passwd,
                                        "-a", self.ap,"--series", self.series, "--band", self.band, "--action", "auto"], 
                                        capture_output=self.cap_ctl_out, check=True)

                if self.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    logg.info(pss)

            except subprocess.CalledProcessError as process_error:
                logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            logg.info("Check the cisco_scheme used attemping 9800 series on 3504 controller: {}".format(self.scheme))

    #test parameters summary (txPower 1-8)
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action txPower  --value 5 --series 9800
    def controller_set_tx_power(self):
        try:
            logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {} value {}".format(self.scheme,
                self.ctlr,self.port,self.prompt,self.user,self.passwd, self.ap, self.series, 
                self.band,"txPower", self.tx_power ))  # TODO fix txPower to tx_power in cisco_wifi_ctl.py
            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                    self.user, "-p", self.passwd,
                                    "-a", self.ap,"--series", self.series, "--band", self.band, 
                                    "--action", "txPower","--value", self.tx_power], 
                                    capture_output=self.cap_ctl_out, check=True)

            if self.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                logg.info(pss)

        except subprocess.CalledProcessError as process_error:
            logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)


    #set channel [36, 64, 100]
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action channel  --value 36 --series 9800
    # 9800 : ap name <AP> dot11 [5ghz | 24ghz] channel <channel>
    # 3504 : (Cisco Controller) >config 802.11a channel ap APA453.0E7B.CF9C  52
    def controller_set_channel(self):
        try:
            if (self.band == "a"):
                cisco_channel = self.chan_5ghz
            else:
                cisco_channel = self.chan_24ghz

            logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {} value {}".format(self.scheme,
                self.ctlr,self.port,self.prompt,self.user,self.passwd, self.ap, self.series, 
                self.band,"channel", cisco_channel ))
            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                    self.user, "-p", self.passwd,
                                    "-a", self.ap,"--series", self.series, "--band", self.band, 
                                    "--action", "channel","--value", cisco_channel], 
                                    capture_output=self.cap_ctl_out, check=True)

            if self.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                logg.info(pss)

        except subprocess.CalledProcessError as process_error:
            logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)

    def controller_set_bandwidth_20(self):
        cisco_chan_width_20 = "20"
        try:
            logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {} value {}".format(self.scheme,
                self.ctlr,self.port,self.prompt,self.user,self.passwd, self.ap, self.series, 
                self.band,"channel", cisco_chan_width_20 ))
            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                    self.user, "-p", self.passwd,
                                    "-a", self.ap,"--series", self.series, "--band", self.band, 
                                    "--action", "channel","--value", cisco_chan_width_20], 
                                    capture_output=self.cap_ctl_out, check=True)

            if self.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                logg.info(pss)
            
        except subprocess.CalledProcessError as process_error:
            logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)



    #set bandwidth [20 40 80 160]
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action bandwidth  --value 40 --series 9800
    def controller_set_bandwidth(self):
        try:
            logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {} value {}".format(self.scheme,
                self.ctlr,self.port,self.prompt,self.user,self.passwd, self.ap, self.series, 
                self.band,"channel", self.chan_width ))
            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                    self.user, "-p", self.passwd,
                                    "-a", self.ap,"--series", self.series, "--band", self.band, 
                                    "--action", "channel","--value", self.chan_width], 
                                    capture_output=self.cap_ctl_out, check=True)

            if self.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                logg.info(pss)
            
        except subprocess.CalledProcessError as process_error:
            logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)


    #create wlan
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action create_wlan  --wlan "open-wlan"  --wlanID 1 --series 9800
    def controller_create_wlan(self):
        if self.series == "9800":
            try:
                logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {} wlan {} wlanID {} wlanSSID {}".format(self.scheme,
                    self.ctlr,self.port,self.prompt,self.user,self.passwd, self.ap, self.series, 
                    self.band,"create_wlan", self.wlan, self.wlanID, self.wlanSSID ))
                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                        self.user, "-p", self.passwd,
                                        "-a", self.ap,"--series", self.series, "--band", self.band, 
                                        "--action", "create_wlan","--wlan", self.wlan, "--wlanID", self.wlanID, "--wlanSSID", self.wlanSSID], 
                                        capture_output=self.cap_ctl_out, check=True)

                if self.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    logg.info(pss)
                
            except subprocess.CalledProcessError as process_error:
                logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            logg.info("Check the cisco_scheme used attemping 9800 series on 3504 controller: {}".format(self.scheme))

    #create wireless tag policy  --9800 series needs to have wireless tag policy set
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action wireless_tag_policy --series 9800
    def controller_set_wireless_tag_policy(self):
        if self.series == "9800":
            try:
                logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {}".format(self.scheme,
                    self.ctlr,self.port,self.prompt,self.user,self.passwd, self.ap, self.series, 
                    self.band,"wireless_tag_policy" ))
                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                        self.user, "-p", self.passwd,
                                        "-a", self.ap,"--series", self.series, "--band", self.band, 
                                        "--action", "wireless_tag_policy"], 
                                        capture_output=self.cap_ctl_out, check=True)

                if self.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    logg.info(pss)

            except subprocess.CalledProcessError as process_error:
                logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            logg.info("Check the cisco_scheme used attemping 9800 series on 3504 controller: {}".format(self.scheme))


    #enable wlan
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action enable_wlan --series 9800
    def controller_enable_wlan(self):
        try:
            logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} wlan: {} action: {}".format(self.scheme,
                self.ctlr,self.port,self.prompt,self.user,self.passwd, self.ap, self.series, 
                self.band, self.wlan,"enable_wlan"))
            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                    self.user, "-p", self.passwd,
                                    "-a", self.ap,"--series", self.series, "--band", self.band, "--wlan", self.wlan,
                                    "--action", "enable_wlan"], 
                                    capture_output=self.cap_ctl_out, check=True)

            if self.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                logg.info(pss)
            
        except subprocess.CalledProcessError as process_error:
            logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)


    #enable 5ghz
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action enable_network_5ghz --series 9800
    def controller_enable_network_5ghz(self):
        if self.series == "9800":
            try:
                logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {}".format(self.scheme,
                    self.ctlr,self.port,self.prompt,self.user,self.passwd, self.ap, self.series, 
                    self.band,"enable_network_5ghz"))
                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                        self.user, "-p", self.passwd,
                                        "-a", self.ap,"--series", self.series, "--band", self.band, 
                                        "--action", "enable_network_5ghz"], 
                                        capture_output=self.cap_ctl_out, check=True)

                if self.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    logg.info(pss)
                
            except subprocess.CalledProcessError as process_error:
                logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            try:
                logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {} value: {}".format(self.scheme,
                    self.ctlr,self.port,self.prompt,self.user,self.passwd, self.ap, self.series,
                    self.band,"cmd","config 802.11a enable network"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                        self.user, "-p", self.passwd,
                                        "-a", self.ap,"--series", self.series, "--band", self.band, "--action", "cmd", "--value", "config 802.11a enable network"], 
                                        capture_output=self.cap_ctl_out, check=True)

                if self.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    logg.info(pss)

            except subprocess.CalledProcessError as process_error:
                logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)



    #enable 24ghz
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action enable_network_24ghz --series 9800
    def controller_enable_network_24ghz(self):
        if self.series == "9800":
            try:
                logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {}".format(self.scheme,
                    self.ctlr,self.port,self.prompt,self.user,self.passwd, self.ap, self.series, 
                    self.band,"enable_network_24ghz"))
                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                        self.user, "-p", self.passwd,
                                        "-a", self.ap,"--series", self.series, "--band", self.band, 
                                        "--action", "enable_network_24ghz"], 
                                        capture_output=self.cap_ctl_out, check=True)

                if self.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    logg.info(pss)

            except subprocess.CalledProcessError as process_error:
                logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            try:
                logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {} value: {}".format(self.scheme,
                    self.ctlr,self.port,self.prompt,self.user,self.passwd, self.ap, self.series,
                    self.band,"cmd","config 802.11b enable network"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                        self.user, "-p", self.passwd,
                                        "-a", self.ap,"--series", self.series, "--band", self.band, "--action", "cmd", "--value", "config 802.11b enable network"], 
                                        capture_output=self.cap_ctl_out, check=True)

                if self.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    logg.info(pss)

            except subprocess.CalledProcessError as process_error:
                logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)



    #enable (band a)
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action enable --series 9800
    def controller_enable_ap(self):
        try:
            logg.info("scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {}".format(self.scheme,
                self.ctlr,self.port,self.prompt,self.user,self.passwd, self.ap, self.series, 
                self.band,"enable"))
            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                    self.user, "-p", self.passwd,
                                    "-a", self.ap,"--series", self.series, "--band", self.band, 
                                    "--action", "enable"], 
                                    capture_output=self.cap_ctl_out, check=True)

            if self.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                logg.info(pss)

        except subprocess.CalledProcessError as process_error:
            logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)


    #advanced (showes summary)
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action advanced --series 9800
    def controller_show_ap_channel(self):
        advanced = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                   self.user, "-p", self.passwd,
                                   "-a", self.ap,"--series", self.series, "--action", "ap_channel"], capture_output=True)

        pss = advanced.stdout.decode('utf-8', 'ignore')
        logg.info(pss)

        if self.series == "9800":
            if (self.band == "a"):
                cisco_channel = self.chan_5ghz
            else:
                cisco_channel = self.chan_24ghz

            for line in pss.splitlines():
                search_str = self.ap
                logg.info("line {}".format(line))
                element_list = line.lstrip().split()
                logg.info("element_list {}".format(element_list))
                if (line.lstrip().startswith(search_str)):
                    logg.info("line {}".format(line))
                    element_list = line.lstrip().split()
                    logg.info("element_list {}".format(element_list))
                    # AP Name (0) mac (1) slot (2) Admin State [enable/disable] (3) Oper State [Up/Down] (4) Width (5) Txpwr (6,7) channel (8) mode (9)
                    logg.info("ap: {} slof {} channel {}  chan_width {}".format(element_list[0],element_list[2],element_list[8],element_list[5]))
                    if (str(cisco_channel) in str(element_list[8])) and (str(self.chan_width) in str(element_list[5])):
                        logg.info("ap {} configuration successful: channel {} in expected {}  chan_width {} in expected {}"
                        .format(element_list[0],cisco_channel,element_list[8],self.chan_width,element_list[5])) 
                    else:
                        logg.info("WARNING ap {} configuration: channel {} in expected {}  chan_width {} in expected {}"
                        .format(element_list[0],cisco_channel,element_list[8],self.chan_width,element_list[5])) 
                    break
        else:
            logg.info("checking for 802.11{}".format(self.band))
            if (self.band == "a"):
                cisco_channel = self.chan_5ghz
            else:
                cisco_channel = self.chan_24ghz

            for line in pss.splitlines():
                #logg.info("line {}".format(line))
                search_str = "802.11{}".format(self.band)
                if (line.lstrip().startswith(search_str)):
                    logg.info("line {}".format(line))
                    element_list = line.lstrip().split()
                    logg.info("element_list {}".format(element_list))
                    logg.info("ap: {} channel {}  chan_width {}".format(self.ap,element_list[4],element_list[5]))
                    if (str(cisco_channel) in str(element_list[4])) and (str(self.chan_width) in str(element_list[5])):
                        logg.info("ap configuration successful: channel {} in expected {}  chan_width {} in expected {}"
                        .format(cisco_channel,element_list[4],self.chan_width,element_list[5])) 
                    else:
                        logg.info("AP WARNING: channel {} expected {}  chan_width {} expected {}"
                        .format(element_list[4],cisco_channel,element_list[5],self.chan_width)) 
                    break
        
        logg.info("configure ap {} channel {} chan_width {}".format(self.ap,self.channel,self.chan_width))
        # Verify channel and channel width. 



##########################################        
# End of cisco controller class
##########################################

##########################################        
# Traffic Generation Begin
##########################################

class L3VariableTime(Realm):
    def __init__(self, 
                args,
                _dfs,
                _dfs_time, 
                _scheme,
                _port,
                _series,
                _ctlr,
                _prompt,
                _user,
                _passwd,
                _ap,
                _ap_slot,
                _band,
                _chan_5ghz,
                _chan_24ghz,
                _chan_width,
                _ap_mode,
                _tx_power,
                _client_density,
                _cap_ctl_out,
                endp_type, 
                tos, 
                side_b, 
                radio_name_list, 
                number_of_stations_per_radio_list,
                ssid_list, 
                ssid_password_list, 
                ssid_security_list, 
                wifimode_list,
                station_lists, 
                name_prefix, 
                debug_on, 
                outfile, 
                results,
                test_keys,
                test_config,
                reset_port_enable_list,
                reset_port_time_min_list,
                reset_port_time_max_list,
                csv_started=False,
                side_a_min_bps=560000, 
                side_a_max_bps=0,
                side_a_min_pdu=1518,
                side_a_max_pdu=0,
                side_b_min_bps=560000, 
                side_b_max_bps=0,
                side_b_min_pdu=1518,
                side_b_max_pdu=0,
                number_template="00",
                test_duration="256s",
                polling_interval="60s",
                lfclient_host="localhost",
                lfclient_port=8080,
                debug=False,
                wait_timeout=120,
                _halt_on_error=False,
                _exit_on_error=False,
                _exit_on_fail=False,
                _proxy_str=None,
                _capture_signal_list=[]):
        super().__init__(lfclient_host=lfclient_host,
                         lfclient_port=lfclient_port,
                         debug_=debug,
                         halt_on_error_=_halt_on_error,
                         _exit_on_error=_exit_on_error,
                         _exit_on_fail=_exit_on_fail,
                         _proxy_str=_proxy_str,
                         _capture_signal_list=_capture_signal_list)
        self.dfs = _dfs
        self.dfs_time = _dfs_time
        self.dfs_time_seconds = self.duration_time_to_seconds(_dfs_time)
        self.scheme = _scheme
        self.port   = _port
        self.series = _series
        self.ctlr   = _ctlr
        self.prompt = _prompt
        self.user   = _user
        self.passwd = _passwd
        self.ap     = _ap
        self.ap_slot = _ap_slot
        self.band   = _band
        self.chan_5ghz  = _chan_5ghz
        self.chan_24ghz = _chan_24ghz
        self.chan_width = _chan_width
        self.ap_mode = _ap_mode
        self.tx_power = _tx_power
        self.cap_ctl_out = _cap_ctl_out
        self.client_density = _client_density
        self.tos = tos.split()
        self.endp_type = endp_type
        self.side_b = side_b
        self.ssid_list = ssid_list
        self.ssid_password_list = ssid_password_list
        self.station_lists = station_lists       
        self.ssid_security_list = ssid_security_list
        self.wifimode_list = wifimode_list
        self.reset_port_enable_list = reset_port_enable_list
        self.reset_port_time_min_list = reset_port_time_min_list
        self.reset_port_time_max_list = reset_port_time_max_list
        self.number_template = number_template
        self.name_prefix = name_prefix
        self.test_duration = test_duration
        self.radio_name_list = radio_name_list
        self.number_of_stations_per_radio_list =  number_of_stations_per_radio_list
        #self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port, debug_=debug_on)
        self.polling_interval_seconds = self.duration_time_to_seconds(polling_interval)
        self.cx_profile = self.new_l3_cx_profile()
        self.multicast_profile = self.new_multicast_profile()
        self.multicast_profile.name_prefix = "MLT-"
        self.station_profiles = []
        self.args = args
        self.outfile = outfile
        self.results = results
        self.csv_started = csv_started
        self.epoch_time = int(time.time())
        self.dfs_epoch_start  = 0
        self.dfs_epoch_detect = 0
        self.debug = debug_on
        self.wait_timeout = wait_timeout
        self.test_keys = test_keys
        self.test_config = test_config

        self.test_config_dict = dict(map(lambda x: x.split('=='), str(self.test_config).replace('[','').replace(']','').replace("'","").split()))


        # Full spread-sheet data
        if self.outfile is not None:
            self.csv_file = open(self.outfile, "a+") 
            self.csv_writer = csv.writer(self.csv_file, delimiter=",")
        
        if self.results is not None:
            self.csv_results = open(self.results, "a+") 
            self.csv_results_writer = csv.writer(self.csv_results, delimiter=",")

        for (radio_, ssid_, ssid_password_, ssid_security_, wifimode_,\
            reset_port_enable_, reset_port_time_min_, reset_port_time_max_) \
            in zip(radio_name_list, ssid_list, ssid_password_list, ssid_security_list, wifimode_list,\
            reset_port_enable_list, reset_port_time_min_list, reset_port_time_max_list):
            self.station_profile = self.new_station_profile()
            self.station_profile.lfclient_url = self.lfclient_url
            self.station_profile.ssid = ssid_
            self.station_profile.ssid_pass = ssid_password_
            self.station_profile.security = ssid_security_
            self.station_profile.mode = wifimode_ 
            self.station_profile.number_template = self.number_template
            self.station_profile.mode = wifimode_  
            self.station_profile.set_reset_extra(reset_port_enable=reset_port_enable_,\
                test_duration=self.duration_time_to_seconds(self.test_duration),\
                reset_port_min_time=self.duration_time_to_seconds(reset_port_time_min_),\
                reset_port_max_time=self.duration_time_to_seconds(reset_port_time_max_))
            self.station_profiles.append(self.station_profile)
        
        self.multicast_profile.host = self.lfclient_host
        self.cx_profile.host = self.lfclient_host
        self.cx_profile.port = self.lfclient_port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = side_a_min_bps
        self.cx_profile.side_a_max_bps = side_a_min_bps
        self.cx_profile.side_a_min_pdu = side_a_min_pdu
        self.cx_profile.side_a_max_pdu = side_a_max_pdu
        self.cx_profile.side_b_min_bps = side_b_min_bps
        self.cx_profile.side_b_max_bps = side_b_min_bps
        self.cx_profile.side_b_min_pdu = side_b_min_pdu
        self.cx_profile.side_b_max_pdu = side_b_max_pdu

    def __get_rx_values(self):
        endp_list = self.json_get("endp?fields=name,rx+bytes,rx+drop+%25", debug_=False)
        endp_rx_drop_map = {}
        endp_rx_map = {}
        our_endps = {}
        for e in self.multicast_profile.get_mc_names():
            our_endps[e] = e
        for e in self.cx_profile.created_endp.keys():
            our_endps[e] = e
        for endp_name in endp_list['endpoint']:
            if endp_name != 'uri' and endp_name != 'handler':
                for item, value in endp_name.items():
                    if item in our_endps:
                        for value_name, value_rx in value.items():
                            if value_name == 'rx bytes':
                                endp_rx_map[item] = value_rx
                        for value_name, value_rx_drop in value.items():
                            if value_name == 'rx drop %':
                                endp_rx_drop_map[item] = value_rx_drop

        return endp_rx_map, endp_rx_drop_map

    def time_stamp(self):
        return time.strftime('%Y-%m-%d %H %M %S', time.localtime(self.epoch_time))

    def __record_rx_dropped_percent(self,rx_drop_percent):
        csv_rx_drop_percent_data = []
        print("test_keys {}".format(self.test_keys))
        print("self.test_config_dict {}".format(self.test_config_dict))
        for key in self.test_keys:
            csv_rx_drop_percent_data.append(self.test_config_dict[key])

        csv_rx_drop_percent_data.extend([self.epoch_time, self.time_stamp(),'rx_drop_percent'])
        # remove multi cast since downstream only if selected
        for key in [key for key in rx_drop_percent if "mtx" in key]: del rx_drop_percent[key]

        if "upstream" in self.test_config_dict.values():
            for key in [key for key in rx_drop_percent if "-A" in key]: del rx_drop_percent[key]
        elif "downstream" in self.test_config_dict.values():
            for key in [key for key in rx_drop_percent if "-B" in key]: del rx_drop_percent[key]


        filtered_values = [v for _, v in rx_drop_percent.items() if v !=0]
        average_rx_drop_percent = sum(filtered_values) / len(filtered_values) if len(filtered_values) != 0 else 0

        csv_performance_rx_drop_percent_values=sorted(rx_drop_percent.items(), key=lambda x: (x[1],x[0]), reverse=False)
        csv_performance_rx_drop_percent_values=self.csv_validate_list(csv_performance_rx_drop_percent_values,5)
        for i in range(5):
            csv_rx_drop_percent_data.append(str(csv_performance_rx_drop_percent_values[i]).replace(',',';'))
        for i in range(-1,-6,-1):
            csv_rx_drop_percent_data.append(str(csv_performance_rx_drop_percent_values[i]).replace(',',';'))

        csv_rx_drop_percent_data.append(average_rx_drop_percent)

        for item, value in rx_drop_percent.items():
            #logg.info(item, "rx drop percent: ", rx_drop_percent[item])
            csv_rx_drop_percent_data.append(rx_drop_percent[item])

        self.csv_add_row(csv_rx_drop_percent_data,self.csv_writer,self.csv_file)
        self.csv_add_row(csv_rx_drop_percent_data,self.csv_results_writer,self.csv_results)

    def __compare_vals(self, old_list, new_list):
        passes = 0
        expected_passes = 0
        csv_performance_values = []
        csv_rx_headers = []
        csv_rx_row_data = []
        csv_result_row_data = []
        csv_rx_delta_row_data = []
        csv_rx_delta_dict = {}
        test_id = ""

        #for key in self.test_keys:
        #    csv_rx_row_data.append(self.test_config_dict[key])
        #    csv_rx_delta_row_data.append(self.test_config_dict[key])


        for key in [key for key in old_list if "mtx" in key]: del old_list[key]
        for key in [key for key in new_list if "mtx" in key]: del new_list[key]

        filtered_values = [v for _, v in new_list.items() if v !=0]
        average_rx= sum(filtered_values) / len(filtered_values) if len(filtered_values) != 0 else 0

        # only evaluate upstream or downstream 
        new_evaluate_list = new_list.copy()
        print("new_evaluate_list before",new_evaluate_list) 
        if "upstream" in self.test_config_dict.values():
            for key in [key for key in new_evaluate_list if "-A" in key]: del new_evaluate_list[key]
            print("upstream in dictionary values")
        elif "downstream" in self.test_config_dict.values():   
            for key in [key for key in new_evaluate_list if "-B" in key]: del new_evaluate_list[key]
            print("downstream in dictionary values")
        #follow code left in for now, provides the best 5 worst 5
        '''print("new_evaluate_list after",new_evaluate_list)
        csv_performance_values=sorted(new_evaluate_list.items(), key=lambda x: (x[1],x[0]), reverse=False)
        csv_performance_values=self.csv_validate_list(csv_performance_values,5)
        for i in range(5):
            csv_rx_row_data.append(str(csv_performance_values[i]).replace(',',';'))
        for i in range(-1,-6,-1):
            csv_rx_row_data.append(str(csv_performance_values[i]).replace(',',';'))

        csv_rx_row_data.append(average_rx)'''

        old_evaluate_list = old_list.copy()
        if "upstream" in self.test_config_dict.values():
            for key in [key for key in old_evaluate_list if "-A" in key]: del old_evaluate_list[key]
            print("upstream in dictionary values")
        elif "downstream" in self.test_config_dict.values():   
            for key in [key for key in old_evaluate_list if "-B" in key]: del old_evaluate_list[key]
            print("downstream in dictionary values")

        if len(old_evaluate_list) == len(new_evaluate_list):
            for item, value in old_evaluate_list.items():
                expected_passes +=1
                print("ITEM: {} VALUE: {}".format(item, value))
                if new_evaluate_list[item] > old_evaluate_list[item]:
                    passes += 1
                    #if self.debug: logg.info(item, new_evaluate_list[item], old_evaluate_list[item], " Difference: ", new_evaluate_list[item] - old_evaluate_list[item])
                    print(item, new_evaluate_list[item], old_evaluate_list[item], " Difference: ", new_evaluate_list[item] - old_evaluate_list[item])
                else:
                    print("Failed to increase rx data: ", item, new_evaluate_list[item], old_evaluate_list[item])
                if not self.csv_started:
                    csv_rx_headers.append(item)
                csv_rx_delta_dict.update({item:(new_evaluate_list[item] - old_evaluate_list[item])})
                

            if not self.csv_started:
                csv_header = self.csv_generate_column_headers()
                csv_header += csv_rx_headers
                logg.info(csv_header)
                self.csv_add_column_headers(csv_header)
                csv_results = self.csv_generate_column_results_headers()
                #csv_results += csv_rx_headers
                self.csv_add_column_headers_results(csv_results)
                print("###################################")
                print(csv_results)
                print("###################################")

                self.csv_started = True

            # need to generate list first to determine worst and best
            filtered_values = [v for _, v in csv_rx_delta_dict.items() if v !=0]
            #average_rx_delta= sum(filtered_values) / len(filtered_values) if len(filtered_values) != 0 else 0
            for key in self.test_keys:
                csv_rx_row_data.append(self.test_config_dict[key])
                csv_result_row_data.append(self.test_config_dict[key])
                csv_rx_delta_row_data.append(self.test_config_dict[key])
                
            max_tp_mbps      = sum(filtered_values)
            csv_rx_row_data.append(max_tp_mbps)
            csv_result_row_data.append(max_tp_mbps)

            #To do  needs to be read or passed in based on test type
            expected_tp_mbps = max_tp_mbps  
            csv_rx_row_data.append(expected_tp_mbps)
            csv_result_row_data.append(expected_tp_mbps)


            #Generate TestID
            for key in self.test_keys:
                test_id = test_id + "_" + self.test_config_dict[key]

            print("test_id: {}".format(test_id))
            csv_rx_row_data.append(test_id)
            csv_result_row_data.append(test_id)

            # Todo pass or fail
            # Todo have a pass_fail for channel
            # have pass_fail for data
            '''if max_tp_mbps == expected_tp_mbps:
                csv_rx_row_data.append("pass")
                csv_result_row_data.append("pass")
            else:
                csv_rx_row_data.append("fail")
                csv_result_row_data.append("fail")'''

            csv_rx_row_data.extend([self.epoch_time, self.time_stamp(),'rx_delta'])
            csv_result_row_data.extend([self.epoch_time, self.time_stamp()])

            print("csv_rx_row_data {}".format(csv_rx_row_data))
            #TODO:  may want to pass in the information that needs to be in the csv file into the class
            '''
            csv_rx_row_data.extend([self.epoch_time, self.time_stamp(),'rx'])
            csv_rx_delta_row_data.extend([self.epoch_time, self.time_stamp(),'rx_delta'])

            csv_performance_delta_values=sorted(csv_rx_delta_dict.items(), key=lambda x: (x[1],x[0]), reverse=False)
            csv_performance_delta_values=self.csv_validate_list(csv_performance_delta_values,5)
            for i in range(5):
                csv_rx_delta_row_data.append(str(csv_performance_delta_values[i]).replace(',',';'))
            for i in range(-1,-6,-1):
                csv_rx_delta_row_data.append(str(csv_performance_delta_values[i]).replace(',',';'))

            csv_rx_delta_row_data.append(average_rx_delta)'''
            
            for item, value in old_evaluate_list.items():
                expected_passes +=1
                if new_evaluate_list[item] > old_evaluate_list[item]:
                    passes += 1
                    #if self.debug: logg.info(item, new_evaluate_list[item], old_evaluate_list[item], " Difference: ", new_evaluate_list[item] - old_evaluate_list[item])
                    print(item, new_evaluate_list[item], old_evaluate_list[item], " Difference: ", new_evaluate_list[item] - old_evaluate_list[item])
                else:
                    print("Failed to increase rx data: ", item, new_evaluate_list[item], old_evaluate_list[item])
                if not self.csv_started:
                    csv_rx_headers.append(item)
                # note need to have all upstream and downstream in the csv table thus new_list and old_list
                #csv_rx_row_data.append(new_list[item])
                # provide delta
                csv_rx_row_data.append(new_list[item] - old_list[item])

            self.csv_add_row(csv_rx_row_data,self.csv_writer,self.csv_file)
            #self.csv_add_row(csv_rx_row_data,self.csv_results_writer,self.csv_results)

            #self.csv_add_row(csv_rx_delta_row_data,self.csv_writer,self.csv_file)

            if passes == expected_passes:
                return True, max_tp_mbps, csv_result_row_data
            else:
                return False, max_tp_mbps, csv_result_row_data
        else:
            print("Old-list length: %i  new: %i does not match in compare-vals."%(len(old_list), len(new_list)))
            print("old-list:",old_list)
            print("new-list:",new_list)
            return False, None, None # check to see if this is valid


    def reset_port_check(self):
        for station_profile in self.station_profiles:
            if station_profile.reset_port_extra_data['reset_port_enable']:
                if station_profile.reset_port_extra_data['reset_port_timer_started'] == False:
                    logg.info("reset_port_time_min: {}".format(station_profile.reset_port_extra_data['reset_port_time_min']))
                    logg.info("reset_port_time_max: {}".format(station_profile.reset_port_extra_data['reset_port_time_max']))
                    station_profile.reset_port_extra_data['seconds_till_reset'] = \
                    random.randint(station_profile.reset_port_extra_data['reset_port_time_min'],\
                                   station_profile.reset_port_extra_data['reset_port_time_max'])
                    station_profile.reset_port_extra_data['reset_port_timer_started'] = True
                    logg.info("on radio {} seconds_till_reset {}".format(station_profile.add_sta_data['radio'],station_profile.reset_port_extra_data['seconds_till_reset']))
                else:
                    station_profile.reset_port_extra_data['seconds_till_reset'] = station_profile.reset_port_extra_data['seconds_till_reset'] - 1
                    if self.debug: logg.info("radio: {} countdown seconds_till_reset {}".format(station_profile.add_sta_data['radio']  ,station_profile.reset_port_extra_data['seconds_till_reset']))
                    if ((station_profile.reset_port_extra_data['seconds_till_reset']  <= 0)):
                        station_profile.reset_port_extra_data['reset_port_timer_started'] = False
                        port_to_reset = random.randint(0,len(station_profile.station_names)-1)
                        logg.info("reset on radio {} station: {}".format(station_profile.add_sta_data['radio'],station_profile.station_names[port_to_reset]))
                        self.reset_port(station_profile.station_names[port_to_reset])

    def pre_cleanup(self):
        self.cx_profile.cleanup_prefix()
        self.multicast_profile.cleanup_prefix()
        self.total_stas = 0
        for station_list in self.station_lists:
            for sta in station_list:
                self.rm_port(sta, check_exists=True)
                self.total_stas += 1

        # Make sure they are gone
        count = 0
        while (count < 10):
            more = False
            for station_list in self.station_lists:
                for sta in station_list:
                    rv = self.rm_port(sta, check_exists=True)
                    if (rv):
                        more = True
            if not more:
                break
            count += 1
            time.sleep(5)

    def build(self):
        index = 0
        for station_profile in self.station_profiles:
            station_profile.use_security(station_profile.security, station_profile.ssid, station_profile.ssid_pass)
            station_profile.set_number_template(station_profile.number_template)
            logg.info("Creating stations")

            station_profile.create(radio=self.radio_name_list[index], sta_names_=self.station_lists[index], debug=self.debug, sleep_time=0)
            index += 1

            # 12/4/2020 put back in multi cast
            #for etype in self.endp_types:
            #    if etype == "mc_udp" or etype == "mc_udp6":
            #        logg.info("Creating Multicast connections for endpoint type: %s"%(etype))
            #        self.multicast_profile.create_mc_tx(etype, self.side_b, etype)
            #        self.multicast_profile.create_mc_rx(etype, side_rx=station_profile.station_names)
            
            for _tos in self.tos:
                logg.info("Creating connections for endpoint type: {} TOS: {} stations_names {}".format(self.endp_type, _tos, station_profile.station_names))
                self.cx_profile.create(endp_type=self.endp_type, side_a=station_profile.station_names, side_b=self.side_b, sleep_time=0, tos=_tos)
        self._pass("PASS: Stations build finished")        
        
    def station_bringup(self):
        client_density = 0
        logg.info("Bringing up stations")
        self.admin_up(self.side_b) 
        for station_profile in self.station_profiles:
            for sta in station_profile.station_names:
                logg.info("Bringing up station %s"%(sta))
                self.admin_up(sta)
                client_density += 1


        temp_stations_list = []
        temp_stations_list.append(self.side_b)
        for station_profile in self.station_profiles:
            temp_stations_list.extend(station_profile.station_names.copy())
        # need algorithm for setting time default 
        if self.wait_for_ip(temp_stations_list, timeout_sec=self.wait_timeout, debug=self.debug):
            logg.info("ip's acquired")
        else:
            logg.info("print failed to get IP's")
            exit(1) # why continue
        
        return client_density

    def read_channel(self):

        logg.info("read_channel: cisco_wifi_ctl.py action advanced")
        pss = ""
        try:
            logg.info("\
                scheme: {} ctlr: {} port: {} prompt: {} user: {}  passwd: {} AP: {} series: {} band: {} action: {}".format(self.scheme,
                self.ctlr,self.port,self.prompt,self.user,
                self.passwd,self.ap,self.series,self.band,"advanced"))

            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.scheme, "--prompt", self.prompt, "--port", self.port, "-d", self.ctlr, "-u",
                                    self.user, "-p", self.passwd,
                                    "-a", self.ap,"--series", self.series, "--band", self.band, "--action", "advanced"], 
                                    capture_output=True, check=True)

            pss = ctl_output.stdout.decode('utf-8', 'ignore')
            logg.info(pss)

        except subprocess.CalledProcessError as process_error:
            logg.info("Command Error, Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)

        logg.info("controller_show_ap_summary:::  pss {}".format(pss))
        if self.series == "9800":
            searchap = False
            cc_mac = ""
            cc_ch = ""
            cc_bw = ""
            cc_power = ""
            cc_dbm = ""
            for line in pss.splitlines():
                if (line.startswith("---------")):
                    searchap = True
                    continue
                # if the pattern changes save the output of the advanced command and re parse https://regex101.com
                if (searchap):
                    pat = "%s\s+(\S+)\s+(%s)\s+\S+\s+\S+\s+(\S+)\s+(\S+)\s+(\S+)\s+dBm\)+\s+(\S+)+\s"%(self.ap,self.ap_slot)
                    m = re.search(pat, line)
                    if (m != None):
                        if(m.group(2) == self.ap_slot):
                            cc_mac = m.group(1)
                            cc_slot = m.group(2)
                            cc_ch = m.group(6);  # (132,136,140,144)
                            cc_power = m.group(4)
                            cc_power = cc_power.replace("/", " of ") # spread-sheets turn 1/8 into a date
                            cc_dbm = m.group(5)
                            cc_dbm = cc_dbm.replace("(","")
                            cc_ch_count = cc_ch.count(",") + 1
                            cc_bw = m.group(3)
                            logg.info("group 1: {} 2: {} 3: {} 4: {} 5: {} 6: {}".format(m.group(1),m.group(2),m.group(3),m.group(4),m.group(5),m.group(6)))
                            logg.info("9800 test_parameters cc_mac: read : {}".format(cc_mac))
                            logg.info("9800 test_parameters cc_slot: read : {}".format(cc_slot))
                            logg.info("9800 test_parameters cc_count: read : {}".format(cc_ch_count))
                            logg.info("9800 test_parameters cc_bw: read : {}".format(cc_bw))
                            logg.info("9800 test_parameters cc_power: read : {}".format(cc_power))
                            logg.info("9800 test_parameters cc_dbm: read : {}".format(cc_dbm))
                            logg.info("9800 test_parameters cc_ch: read : {}".format(cc_ch))
                            break
        else:
            searchap = False
            cc_mac = ""
            cc_ch = ""
            cc_bw = ""
            cc_power = ""
            cc_dbm = ""
            ch_count = ""
            for line in pss.splitlines():
                if (line.startswith("---------")):
                    searchap = True
                    continue
                
                if (searchap):
                    pat = "%s\s+(\S+)\s+\S+\s+\S+\s+\S+\s+(\S+)\s+(\S+)\s+\(\s*(\S+)\s+dBm"%(self.ap)
                    m = re.search(pat, line)
                    if (m != None):
                        cc_mac = m.group(1)
                        cc_ch = m.group(2);  # (132,136,140,144)
                        cc_power = m.group(3)
                        cc_power = cc_power.replace("/", " of ", 1) # spread-sheets turn 1/8 into a date
                        cc_dbm = m.group(4)
                        ch_count = cc_ch.count(",")
                        cc_bw = 20 * (ch_count + 1)
                        
                        logg.info("3504 test_parameters cc_mac: read : {}".format(cc_mac))
                        logg.info("3504 test_parameters cc_count: read : {}".format(ch_count))
                        logg.info("3504 test_parameters cc_bw: read : {}".format(cc_bw))
                        logg.info("3504 test_parameters cc_power: read : {}".format(cc_power))
                        logg.info("3504 test_parameters cc_dbm: read : {}".format(cc_dbm))
                        logg.info("3504 test_parameters cc_ch: read : {}".format(cc_ch))

        return cc_ch    

    def dfs_get_frequency(self,channel):
        # possibly have a dictionary

        if   channel == "36":
            frequency = "5180000"
        elif channel == "38":
            frequency = "5190000"
        elif channel == "40":
            frequency = "5200000"
        elif channel == "42":
            frequency = "5210000"
        elif channel == "44":
            frequency = "5220000"
        elif channel == "46":
            frequency = "5230000"
        elif channel == "48":
            frequency = "5240000"
        # DFS Channels US
        elif channel == "52":
            frequency = "5260000"
        elif channel == "56":
            frequency = "5280000"
        elif channel == "60":
            frequency = "5300000"
        elif channel == "64":
            frequency = "5320000"
        elif channel == "100":
            frequency = "5500000"
        elif channel == "104":
            frequency = "5520000"
        elif channel == "108":
            frequency = "5540000"
        elif channel == "112":
            frequency = "5560000"
        elif channel == "116":
            frequency = "5580000"
        elif channel == "120":
            frequency = "5600000"
        elif channel == "124":
            frequency = "5620000"
        elif channel == "128":
            frequency = "5640000"
        elif channel == "132":
            frequency = "5660000"
        elif channel == "136":
            frequency = "5680000"
        elif channel == "140":
            frequency = "5700000"
        elif channel == "144":
            frequency = "5720000"
        elif channel == "149":
            frequency = "5745000"
        elif channel == "153":
            frequency = "5765000"
        elif channel == "157":
            frequency = "5785000"
        elif channel == "161":
            frequency = "5805000"
        elif channel == "165":
            frequency = "5825000"
        elif channel == "169":
            frequency = "5845000"
        elif channel == "173":
            frequency = "5865000"
        else:
            logg.info("Invalid Channel")
            exit(1)
        return frequency
        

    def dfs_send_radar(self,channel):
        # Hard coded to FCC0 - need to support others
        width_ = "1"
        interval_ = "1428"
        count_ = "18"
        frequency_ = "5260000"  # channel 52
        #sweep_time_ = "1000"
        sweep_time_ = "0"
        if_gain_ = "40"
        bb_gain_ = "20"
        gain_ = "0"

        frequency_ = self.dfs_get_frequency(channel)
        if frequency_ == None:
            logg.info("frequency_ is : {}".format(frequency_))
            exit(1)

        logg.info("dfs_send_radar channel: {}  frequency: {}".format(channel, frequency_))

        # spawn bash for lf_hackrf.py
        child = pexpect.spawn('bash')
        time.sleep(0.4)

        # for testing bash
        i = child.expect([r'\$',pexpect.TIMEOUT],timeout=2)
        if i == 0:
            logg.info("i: {} received bash prompt for hackrf command".format(i))
        if i == 1:
            logg.info("i: {} TIMEOUT in bash prompt".format(i))
        '''
        child.sendline('ls -lrt')
        child.expect([pexpect.TIMEOUT], timeout=1)  # do not delete this for it allows for subprocess to see output
        print(child.before.decode('utf-8', 'ignore')) # do not delete this for it  allows for subprocess to see output

        child.expect(r'\$')
        '''

        # no timeouts
        '''command_hackRF = "sudo python lf_hackrf.py --pulse_width {} --pulse_interval {} --pulse_count {} --sweep_time {} --freq {} --if_gain {} --bb_gain {} --gain {}".format(width_,interval_,count_,sweep_time_,frequency_,if_gain_,bb_gain_,gain_)
        print("hackrf command {}".format(command_hackRF))
        child.sendline(command_hackRF)
        child.expect([pexpect.TIMEOUT], timeout=1)  # do not delete this for it allows for subprocess to see output
        print(child.before.decode('utf-8', 'ignore')) # do not delete this for it  allows for subprocess to see output

        child.expect('lanforge:')
        print(child.before.decode('utf-8', 'ignore'))
        child.sendline('lanforge')
        time.sleep(5)
        child.expect('>>>')
        print(child.before.decode('utf-8', 'ignore'))
        child.sendline('s')
        child.expect('>>>')
        print(child.before.decode('utf-8', 'ignore'))
        child.sendline('q')
        time.sleep(1)'''

        # with timeouts
        command_hackRF = "sudo python lf_hackrf.py --pulse_width {} --pulse_interval {} --pulse_count {} --sweep_time {} --freq {} --if_gain {} --bb_gain {} --gain {}".format(width_,interval_,count_,sweep_time_,frequency_,if_gain_,bb_gain_,gain_)
        logg.info("hackrf command {}".format(command_hackRF))
        child.sendline(command_hackRF)
        time.sleep(0.4)
        i = child.expect(['lanforge:',pexpect.TIMEOUT], timeout=2) 
        if i == 0:
            logg.info("lanforge prompt received i: {} before {} after {}".format(i,child.before.decode('utf-8', 'ignore'),child.after.decode('utf-8', 'ignore')))
            child.sendline('lanforge')
            time.sleep(0.4)
            self.dfs_epoch_start = int(time.time())
            j = child.expect(['>>>',pexpect.TIMEOUT], timeout=5) 
            if j == 0:
                logg.info(">>> prompt received i: {} j: {} before {} after {}".format(i,j,child.before.decode('utf-8', 'ignore'),child.after.decode('utf-8', 'ignore')))
                logg.info("Let the radar run for 5 sec")
                time.sleep(5)
                child.sendline('s') # stop
                time.sleep(0.4)
                k = child.expect(['>>>',pexpect.TIMEOUT], timeout=2) 
                if k == 0:
                    logg.info(">>> prompt received i: {} j: {} k: {} before {} after {}".format(i,j,k,child.before.decode('utf-8', 'ignore'),child.after.decode('utf-8', 'ignore')))
                    child.sendline('q')
                    time.sleep(1)
                if k == 1:
                    logg.info("TIMEOUT hackrf >>> prompt i: {} j: {} k: {} before {} after {}".format(i,j,k,child.before.decode('utf-8', 'ignore'),child.after))
            if j == 1:
                logg.info("TIMEOUT hackrf >>> prompt i: {} j: {} before {} after {}".format(i,j,child.before.decode('utf-8', 'ignore'),child.after))
        if i == 1:
            logg.info("TIMEOUT lanforge password prompt i: {} before {} after {}".format(i,child.before.decode('utf-8', 'ignore'),child.after))

    def start(self, print_pass=False, print_fail=False):  
        best_max_tp_mbps = 0
        best_csv_rx_row_data = " "
        max_tp_mbps = 0
        csv_rx_row_data = " "
        Result = False

        # verify controller channel , see if a DFS channel
        initial_channel = self.read_channel()

        logg.info("###########################################")
        logg.info("# INITIAL CHANNEL: {}".format(initial_channel))
        logg.info("###########################################")

        if (initial_channel != self.chan_5ghz):
            logg.warn("##################################################################")
            logg.warn("# DFS LOCKOUT?  COMMAND LINE CHANNEL: {} NOT EQUAL INITIAL CONTROLLER CHANNEL: {}".format(self.chan_5ghz,initial_channel))
            logg.warn("##################################################################")

        time.sleep(30)
        
        logg.info("Starting multicast traffic (if any configured)")
        self.multicast_profile.start_mc(debug_=self.debug)
        self.multicast_profile.refresh_mc(debug_=self.debug)
        logg.info("Starting layer-3 traffic (if any configured)")
        self.cx_profile.start_cx()
        self.cx_profile.refresh_cx()

        cur_time = datetime.datetime.now()
        logg.info("Getting initial values.")
        old_rx_values, rx_drop_percent = self.__get_rx_values()

        end_time = self.parse_time(self.test_duration) + cur_time

        logg.info("Monitoring throughput for duration: %s"%(self.test_duration))

        passes = 0
        expected_passes = 0
        logg.info("polling_interval_seconds {}".format(self.polling_interval_seconds))

        logg.info("dfs_time_seconds {}".format(self.dfs_time_seconds))
        dfs_time = cur_time + datetime.timedelta(seconds=self.dfs_time_seconds)
        dfs_radar_sent = False
        while cur_time < end_time:
            interval_time = cur_time + datetime.timedelta(seconds=self.polling_interval_seconds)

            while cur_time < interval_time:
                cur_time = datetime.datetime.now()
                self.reset_port_check()
                if((cur_time > dfs_time) and dfs_radar_sent == False):
                    self.dfs_send_radar(initial_channel)
                    dfs_radar_sent = True
                time.sleep(1)
            
            self.epoch_time = int(time.time())
            new_rx_values, rx_drop_percent = self.__get_rx_values()

            expected_passes += 1
            '''
            #self.csv_add_row(csv_rx_row_data,self.csv_results_writer,self.csv_results)


            if passes == expected_passes:
                return True, max_tp_mbps, csv_rx_row_data
            else:
                return False, max_tp_mbps, csv_rx_row_data
            '''
            # __compare_vals - does the calculations
            Result, max_tp_mbps, csv_rx_row_data = self.__compare_vals(old_rx_values, new_rx_values)
            if max_tp_mbps > best_max_tp_mbps:
                best_max_tp_mbps = max_tp_mbps
                best_csv_rx_row_data = csv_rx_row_data

            # need to check the expected max_tp_mbps
            if Result:
                passes += 1
            else:
                self._fail("FAIL: Not all stations increased traffic", print_fail)
            old_rx_values = new_rx_values

            #percentage dropped not needed for scaling and performance , needed for longevity
            #self.__record_rx_dropped_percent(rx_drop_percent)

            cur_time = datetime.datetime.now()


        final_channel = self.read_channel()

        logg.info("###########################################")
        logg.info("# FINAL CHANNEL : {}".format(final_channel))
        logg.info("###########################################")

        dfs_channel_bw20_values = [52, 56, 60, 64, 68, 96, 100, 104, 108, 112, 116, 120, 124 ,128, 132, 136, 140, 144]

        pass_fail = "pass"
        if int(final_channel) in dfs_channel_bw20_values:
            logg.info("FAIL: The DFS channel did not change or initial channel was not DFS")
            pass_fail = "fail"

        if (initial_channel != self.chan_5ghz):
            logg.info("FAIL: channel set on command line: {} not configured in controller: {} is there a DFS lockout condition".format(self.chan_5ghz,initial_channel))
            pass_fail = "fail"

        best_csv_rx_row_data.append(initial_channel)
        best_csv_rx_row_data.append(final_channel)
        best_csv_rx_row_data.append(pass_fail)
        self.csv_add_row(best_csv_rx_row_data,self.csv_results_writer,self.csv_results)

        # TO DO check to see if the data is still being transmitted
        if passes == expected_passes:
            self._pass("PASS: All tests passed", print_pass)

    def stop(self):
        self.cx_profile.stop_cx()
        self.multicast_profile.stop_mc()
        for station_list in self.station_lists:
            for station_name in station_list:
                self.admin_down(station_name)

    def cleanup(self):
        self.cx_profile.cleanup()
        self.multicast_profile.cleanup()
        for station_profile in self.station_profiles:
            station_profile.cleanup()
        
                                        
    def csv_generate_column_headers(self):
        csv_rx_headers = self.test_keys.copy() 
        csv_rx_headers.extend 
        csv_rx_headers.extend(['max_tp_mbps','expected_tp','test_id','epoch_time','time','monitor','pass_fail'])
        '''for i in range(1,6):
            csv_rx_headers.append("least_rx_data {}".format(i))
        for i in range(1,6):
            csv_rx_headers.append("most_rx_data_{}".format(i))
        csv_rx_headers.append("average_rx_data")'''
        return csv_rx_headers

    def csv_generate_column_results_headers(self):
        csv_rx_headers = self.test_keys.copy() 
        csv_rx_headers.extend 
        csv_rx_headers.extend(['max_tp_mbps','expected_tp','test_id','epoch_time','time','initial_channel','final_channel','pass_fail'])
        '''for i in range(1,6):
            csv_rx_headers.append("least_rx_data {}".format(i))
        for i in range(1,6):
            csv_rx_headers.append("most_rx_data_{}".format(i))
        csv_rx_headers.append("average_rx_data")'''
        return csv_rx_headers


    def csv_add_column_headers(self,headers):
        if self.csv_file is not None:
            self.csv_writer.writerow(headers)
            self.csv_file.flush()

    def csv_add_column_headers_results(self,headers):
        if self.csv_results is not None:
            self.csv_results_writer.writerow(headers)
            self.csv_results.flush()    

    def csv_validate_list(self, csv_list, length):
        if len(csv_list) < length:
            csv_list = csv_list + [('no data','no data')] * (length - len(csv_list))
        return csv_list

    def csv_add_row(self,row,writer,csv_file): # can make two calls eventually
        if csv_file is not None:
            writer.writerow(row)
            csv_file.flush()

#########################################
# 
# AP helper functions
# 
# #######################################            

def valid_endp_types(_endp_type):
    etypes = _endp_type.split()
    for endp_type in etypes:
        valid_endp_type=['lf_udp','lf_udp6','lf_tcp','lf_tcp6','mc_udp','mc_udp6']
        if not (str(endp_type) in valid_endp_type):
            logg.info('invalid endp_type: %s. Valid types lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6' % endp_type)
            exit(1)
    return _endp_type

##########################################        
# Traffic Generation End
##########################################


def main():
    global logg
    lfjson_host = "localhost"
    lfjson_port = 8080
    endp_types = "lf_udp"
    debug_on = False

    parser = argparse.ArgumentParser(
        prog='lf_cisco_dfs.py',
        #formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Scaling and Performance
            ''',
        
        description='''\
lf_cisco_dfs.py:
--------------------

##################################################################################
Task Description:
##################################################################################
-----------------

DFS Testing can do multiple clients at once and various radios

Our ultimate aim is to achieve the following things:

1. 1 to 200 client DFS on 11ac (1, 50 and 200 client count tests)
      1. 5 Ghz with different channel widths
      2. Data encryption enabled/disabled
      3. Local/central switching and authentication combinations
2. 1 to 37 client DFS on 11ax (1, 10 and 37 client count tests) eventually 200 clients
      1. Different channel widths
      2. Data encryption enabled/disabled
      3. Local/central switching and authentication combinations
      4. MU-MIMO and OFDMA enabled/disabled combination
3. CI/CD implementation
      1. Download latest WLC images and upload them to the controller
      2. Start the test suite
      3. Generate a report per release
      4. Display and graph all result data according to each release along with each testcase historical graph
      5. Review overall AP performance across multiple AP platforms


Summary : 
----------
create stations, create traffic between upstream port and stations,  run traffic. 
The traffic on the stations will be checked once per minute to verify that traffic is transmitted
and recieved.

Generic command layout:
-----------------------
python .\\lf_cisco_dfs.py --test_duration <duration> --endp_type <traffic types> --upstream_port <port> 
        --radio "radio==<radio> stations==<number staions> ssid==<ssid> ssid_pw==<ssid password> security==<security type: wpa2, open, wpa3> wifimode==AUTO" --debug

Multiple radios may be entered with individual --radio switches

generiic command with controller setting channel and channel width test duration 30 sec
python3 lf_cisco_dfs.py --cisco_ctlr <IP> --cisco_dfs True/False --mgr <Lanforge IP> 
    --cisco_chan_5ghz <channel> --cisco_chan_width <20,40,80,120> --endp_type 'lf_udp lf_tcp mc_udp' --upstream_port <1.ethX> 
    --radio "radio==<radio 0 > stations==<number stations> ssid==<ssid> ssid_pw==<ssid password> security==<wpa2 , open> wifimode==<AUTO>" 
    --radio "radio==<radio 1 > stations==<number stations> ssid==<ssid> ssid_pw==<ssid password> security==<wpa2 , open> wifimode==<AUTO>" 
    --duration 5m

wifimode:
   <a  b   g   abg   abgn   bgn   bg   abgnAC   anAC   an   bgnAC   abgnAX   bgnAX   anAX 


<duration>: number followed by one of the following 
d - days
h - hours
m - minutes
s - seconds

<traffic type>: 
lf_udp  : IPv4 UDP traffic
lf_tcp  : IPv4 TCP traffic
lf_udp6 : IPv6 UDP traffic
lf_tcp6 : IPv6 TCP traffic
mc_udp  : IPv4 multi cast UDP traffic
mc_udp6 : IPv6 multi cast UDP traffic

<tos>: 
BK, BE, VI, VO:  Optional wifi related Tos Settings.  Or, use your preferred numeric values.

#################################
#Command switches
#################################
--cisco_ctlr <IP of Cisco Controller>',default=None
--cisco_user <User-name for Cisco Controller>',default="admin"
--cisco_passwd <Password for Cisco Controller>',default="Cisco123
--cisco_prompt <Prompt for Cisco Controller>',default="(Cisco Controller) >
--cisco_ap <Cisco AP in question>',default="APA453.0E7B.CF9C"
    
--cisco_dfs <True/False>',default=False
--cisco_chan_5ghz <channel>',default=None  , no change
--cisco_chan_width <20 40 80 160>',default="20",choices=["20","40","80","160"]
--cisco_band <a | b | abgn>',default="a",choices=["a", "b", "abgn"]

--mgr <hostname for where LANforge GUI is running>',default='localhost'
-d  / --test_duration <how long to run>  example --time 5d (5 days) default: 3m options: number followed by d, h, m or s',default='3m'
--tos:  Support different ToS settings: BK | BE | VI | VO | numeric',default="BE"
--debug:  Enable debugging',default=False
-t  / --endp_type <types of traffic> example --endp_type \"lf_udp lf_tcp mc_udp\"  Default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6',
                        default='lf_udp', type=valid_endp_types
-u / --upstream_port <cross connect upstream_port> example: --upstream_port eth1',default='eth1')
-o / --outfile <Output file for csv data>", default='dfs'

#########################################
# Examples
# #######################################            
Example #1  running traffic with two radios
1. Test duration 4 minutes
2. Traffic IPv4 TCP
3. Upstream-port eth1
4. Radio #0 wiphy0 has 32 stations, ssid = candelaTech-wpa2-x2048-4-1, ssid password = candelaTech-wpa2-x2048-4-1
5. Radio #1 wiphy1 has 64 stations, ssid = candelaTech-wpa2-x2048-5-3, ssid password = candelaTech-wpa2-x2048-5-3
6. Create connections with TOS of BK and VI

Command: (remove carriage returns)
python3 .\\lf_cisco_dfs.py --test_duration 4m --endp_type \"lf_tcp lf_udp mc_udp\" --tos \"BK VI\" --upstream_port eth1 
--radio "radio==wiphy0 stations==32 ssid==candelaTech-wpa2-x2048-4-1 ssid_pw==candelaTech-wpa2-x2048-4-1 security==wpa2"
--radio "radio==wiphy1 stations==64 ssid==candelaTech-wpa2-x2048-5-3 ssid_pw==candelaTech-wpa2-x2048-5-3 security==wpa2"

Example #2 using cisco controller
1.  cisco controller at 192.168.100.112
2.  cisco dfs True
3.  cisco channel 52  
4.  cisco channel width 20
5.  traffic 'lf_udp lf_tcp mc_udp'
6.  upstream port eth3
7.  radio #0 wiphy0 stations  3 ssid test_candela ssid_pw [BLANK] secruity Open
8.  radio #1 wiphy1 stations 16 ssid test_candela ssid_pw [BLANK] security Open
9.  lanforge manager at 192.168.100.178
10. duration 5m

Command:
python3 lf_cisco_dfs.py --cisco_ctlr 192.168.100.112 --cisco_dfs True --mgr 192.168.100.178 
    --cisco_chan_5ghz 52 --cisco_chan_width 20 --endp_type 'lf_udp lf_tcp mc_udp' --upstream_port 1.eth3 
    --radio "radio==1.wiphy0 stations==3 ssid==test_candela ssid_pw==[BLANK] security==open" 
    --radio "radio==1.wiphy1 stations==16 ssid==test_candela ssid_pw==[BLANK] security==open"
    --test_duration 5m

##############################################################################
Detailed test loop description 10/9/2020 - Karthik Recommendation
##############################################################################
Script logic loops:

AP {Axel, Vanc} Dynamic
      frequency {24ghz, 5ghz} Common (band)  : 24ghz == b , 5ghz == a
            wifimode{11ax (2.4 ghz or 5 ghz), 11ac (5 ghz only), 11n (2.4 ghz or 5ghz), 11bg(2.4 ghz)} Common  (an anAX anAC abgn bg)
                  Bandwidth {20, 40, 80, 160}
                        data-encryption {enable/disable} Common
                              AP-mode {local/flexconnect} Common
                                    client-density {1, 10, 20, 50, 100, 200} Dynamic
                                          Packet-type {TCP, UDP} Common
                                                Direction {Downstream, Upstream}
                                                      Packet-size { 88, 512, 1370, 1518}   Common
                                                            Time (4 iterations of 30 sec and get the best average TP out of it) 

Notes:
#############################################
CandelaTech Radios and what supports
#############################################

Radio descriptions:
ax200: so if AP is /n, then ax200 will connect at /n.  But if AP is /AX, we have no way to force ax200 to act like /n
ax200: is dual band, supporting at least /b/g/n/AX on 2.4Ghz, and /a/n/ac/AX on 5Ghz.  2.4Ghz doesn't officially support /AC, but often chips will do /AC there anyway

ath10K: if they want /AC or /n or /abg stations, then our ath10k radios can support that need (and ath9k if they have any, can do /n and /abg)
ath10K(998x)  - wave -1 , dual band card it can be ac, n , a/b/g modes, up to 3x3 spacial streams
ath10K(9884) - wave-2 supports 4x4  802.11an-AC  5ghz  (can act as ac , an)

Note: wave-2 radios can act as ac, an, (802.11an-AC) or legacy a/b/g (802.11bgn-AC)

#############################################
wifimodes needed to support
#############################################
11ax (2.4 ghz or 5 ghz), 11ac (5 ghz only), 11n (2.4ghz or 5 ghz), 11bg (2.4 ghz)  (Cisco)

#############################################
5 Ghz
#############################################
Wifi mode: 11ax  - 5ghz
Radios   :  ax200  :        802.11 /a/n/ac/AX

Wifi mode: 11ac - 5ghz
Radios   :  ath10K(9984)    802.11an-AC (9984 are single band)

Wifi mode: 11n - 5ghz
Radios   :  ath10K(9984)    802.11an-AC (9984 are single band)

#############################################
24 Ghz
#############################################
Wifi mode: 11ax - 24ghz
Radios   :  ax200 -         802.11 /b/g/n/AX     

Wifi mode: 11ac - 24ghz
Radios   :  ax200           802.11 /b/g/n/AX (2.4Ghz doesn't officially support /AC, but often chips will do /AC there anyway) (invalid)

Wifi mode: 11n - 24ghz 
Radios   :  ax200           802.11 /b/g/n/AX

Wifi mode: 11bg - 24ghz
Radios   :  ax200           802.11 /b/g/n/AX

############################################
Radio support for specific Modes
############################################
cisco_wifimode == "anAX" or cisco_wifimode == "abgn" or cisco_wifimode == "bg":
        radios = radio_AX200_abgn_ax_dict[cisco_client_density]
                                                
cisco_wifimode == "an" or cisco_wifimode == "anAC":
        radios = radio_ath10K_9984_an_AC_dict[cisco_client_density]


############################################
Eventual Realm at Cisco
############################################

1.wiphy0  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
1.wiphy1  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
1.wiphy2  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
1.wiphy3  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
1.wiphy4  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
1.wiphy5  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
1.wiphy6  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
1.wiphy7  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
1.wiphy8  802.11an-AC    ath10k(9984)    523 - 64 stations - 5ghz 
1.wiphy9  802.11an-AC    ath10k(9984)    523 - 64 stations - 5ghz

2.wiphy0  802.11abgn-ax  iwlwifi(AX200)  521 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
2.wiphy1  802.11abgn-ax  iwlwifi(AX200)  521 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn 

3.wiphy0  802.11abgn-ax  iwlwifi(AX200)  521 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
3.wiphy1  802.11abgn-ax  iwlwifi(AX200)  521 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn

4.wiphy0  802.11abgn-ax  iwlwifi(AX200)  521 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
4.wiphy1  802.11abgn-ax  iwlwifi(AX200)  521 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn

5.wiphy0  802.11abgn-ax  iwlwifi(AX200)  521 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
5.wiphy1  802.11abgn-ax  iwlwifi(AX200)  521 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn

6.wiphy0  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
6.wiphy1  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
6.wiphy2  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
6.wiphy3  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
6.wiphy4  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
6.wiphy5  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
6.wiphy6  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
6.wiphy7  802.11abgn-ax  iwlwifi(AX200)  523 - 1  stations - 5ghz/24ghz use only for 802.11ax - 24gz abgn
6.wiphy8  802.11an-AC    ath10k(9984)    523 - 64 stations - 5ghz
6.wiphy9  802.11an-AC    ath10k(9984)    523 - 64 stations - 5ghz

       
Sample script 2/11/2021

   ./lf_cisco_dfs.py -cc 192.168.100.112 -cu admin -cpw Cisco123 -cca APA453.0E7B.CF9C -ccf "a" -cwm "auto" -cc5 "52" -ccw "20" -ccd "1" -cs "3504" --endp_type 'lf_udp' --upstream_port eth2  --cisco_wlan "test_candela" --cisco_wlanID 1 --cisco_wlanSSID "test_candela" --cisco_directions "upstream" --cisco_prompt "(Cisco Controller)" --radio "radio==1.wiphy0 stations==1  ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto" --ap_info "ap_scheme==serial ap_prompt==APA453.0E7B.CF9C ap_ip==0 ap_port==0 ap_user==admin ap_pw==Admin123 ap_tty==/dev/ttyUSB2 ap_baud==9600"
    
       
        ''')

    # reorder to follow looping

    parser.add_argument('-ca'  ,'--cisco_all', help='--cisco_all flag present default to all tests',action="store_true")
    parser.add_argument('-ct'  ,'--cisco_test', help='--cisco_test flag present default to subset tests',action="store_true")
    parser.add_argument('-ct2' ,'--cisco_test2', help='--cisco_test2 flag present default to subset tests',action="store_true")
    parser.add_argument('-cca' ,'--cisco_ap', help='--cisco_ap List of APs to test  default:  Axel',default="APA453.0E7B.CF9C")
    parser.add_argument('-ccf' ,'--cisco_band', help='--cisco_band <a | b | abgn> default a',default="a")
    # cisco wanted 11ax , 11ac, 11n, 11gb
    parser.add_argument('-cwm' ,'--cisco_wifimode', help='List of of wifi mode to test <11ax 11ac 11n 11gb> default: an',default="an",
                        choices=[ "auto", "a", "b", "g", "abg", "abgn", "bgn", "bg", "abgnAC", "anAC", "an", "bgnAC", "abgnAX", "bgnAX", "anAX"])

    parser.add_argument('-cc5','--cisco_chan_5ghz', help='--cisco_chan_5ghz <36 40 ...> default 36',default="36")
    parser.add_argument('-cc2','--cisco_chan_24ghz', help='--cisco_chan_24ghz <1 2 ...> default 1',default="1")
    parser.add_argument('-ccw','--cisco_chan_width', help='--cisco_chan_width <20 40 80 160> default: 20',default="20")
    parser.add_argument('-cam','--cisco_ap_mode', help='--cisco_ap_mode <local flexconnect> default local',default="local")
    parser.add_argument('-cps','--cisco_packet_size', help='--cisco_packet_size List of packet sizes <88 512 1370 1518> default 1518 ',default="1518" )
    parser.add_argument('-ctd','--cisco_directions', help='--cisco_directions <upstream downstream both> default: upstream downstream ',default="upstream downstream" )
    parser.add_argument('-ccd','--cisco_client_density', help='--cisco_client_density List of client densities <1 10 20 50 100 200> default 1 ',
                            default="1" )
    #TODO set str for ones that are str
    parser.add_argument('-cde','--cisco_data_encryption', help='--cisco_data_encryption \"enable disable\"',default="disable" )
    parser.add_argument('-cs' ,'--cisco_series', help='--cisco_series <9800 | 3504>',default="3504",choices=["9800","3504"])
    parser.add_argument('-ccp','--cisco_prompt',    type=str,help="controller prompt default WLC",default="WLC")
    parser.add_argument('-cas','--cisco_ap_slot',    type=str,help="AP slot, default 1",default="1")

    parser.add_argument('-cc' ,'--cisco_ctlr', help='--cisco_ctlr <IP of Cisco Controller> default 192.168.100.178',default="192.168.100.178")
    parser.add_argument('-cp' ,'--cisco_port', help='--cisco_port <port of Cisco Controller> ssh default 22',default="22")
    parser.add_argument('-cu' ,'--cisco_user', help='--cisco_user <User-name for Cisco Controller>',default="admin")
    parser.add_argument('-cpw','--cisco_passwd', help='--cisco_passwd <Password for Cisco Controller>',default="Cisco123")
    parser.add_argument('-ccs','--cisco_scheme', help='--cisco_scheme (serial|telnet|ssh): connect via serial, ssh or telnet',default="ssh",choices=["serial","telnet","ssh"])
    parser.add_argument('-cw' ,'--cisco_wlan', help='--cisco_wlan <wlan name> ',required=True)
    parser.add_argument('-cwi','--cisco_wlanID', help='--cisco_wlanID <wlanID> ',required=True)
    parser.add_argument('-cws' ,'--cisco_wlanSSID', help='--cisco_wlanSSID <wlan ssid>',required=True)

    parser.add_argument('-ctp','--cisco_tx_power', help='--cisco_tx_power <1 | 2 | 3 | 4 | 5 | 6 | 7 | 8>  1 is highest power default NA NA means no change',default="NA"
                        ,choices=["1","2","3","4","5","6","7","8","NA"])
    parser.add_argument('-dfs','--cisco_dfs',  help='--cisco_dfs, switch to enable dfs testing', action='store_true')
    parser.add_argument('-dft','--cisco_dfs_time',  help='--cisco_dfs_time, time to wait prior to sending radar signal default 30s', default='30s')
    parser.add_argument('-cco','--cap_ctl_out',  help='--cap_ctl_out , switch the cisco controller output will be captured', action='store_true')
                            

    parser.add_argument('-apr','--amount_ports_to_reset', help='--amount_ports_to_reset \"<min amount ports> <max amount ports>\" ', default=None)
    parser.add_argument('-prs','--port_reset_seconds', help='--ports_reset_seconds \"<min seconds> <max seconds>\" ', default="10 30")

    parser.add_argument('-lm','--mgr', help='--mgr <hostname for where LANforge GUI is running>',default='localhost')
    parser.add_argument('-d','--test_duration', help='--test_duration <how long to run>  example --time 5d (5 days) default: 2m options: number followed by d, h, m or s',default='2m')
    parser.add_argument('-pi','--polling_interval', help="--polling_interval <seconds>", default='30s')
    parser.add_argument('--tos', help='--tos:  Support different ToS settings: BK | BE | VI | VO | numeric',default="BE")
    parser.add_argument('-db','--debug', help='--debug:  Enable debugging',action='store_true')
    parser.add_argument('-t', '--endp_type', help='--endp_type <types of traffic> example --endp_type \"lf_udp lf_tcp mc_udp\"  Default: lf_tcp, options: lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6',
                        default='lf_tcp', type=valid_endp_types)
    parser.add_argument('-u', '--upstream_port', help='--upstream_port <cross connect upstream_port> example: --upstream_port eth1',default='eth1')
    parser.add_argument('-o','--csv_outfile', help="--csv_outfile <Output file for csv data>", default='dfs')
    parser.add_argument("-l", "--log",        action='store_true', help="create logfile for messages, default stdout")
    parser.add_argument('-c','--csv_output', help="Generate csv output", default=True) 

    #to do add wifimode
    parser.add_argument('-r','--radio', action='append', nargs=1, help='--radio  \
                        \"radio==<number_of_wiphy stations=<=number of stations> ssid==<ssid> ssid_pw==<ssid password> security==<security> wifimode==<wifimode>\" '\
                        , required=False)
    parser.add_argument('-amr','--side_a_min_bps',  help='--side_a_min_bps, station min tx bits per second default 9600', default=9600)
    parser.add_argument('-amp','--side_a_min_pdu',   help='--side_a_min_pdu ,  station ipdu size default 1518', default=1518)
    parser.add_argument('-bmr','--side_b_min_bps',  help='--side_b_min_bps , upstream min tx rate default 256000', default=9600)
    parser.add_argument('-bmp','--side_b_min_pdu',   help='--side_b_min_pdu ,  upstream pdu size default 1518', default=1518)

    # AP parameters
    parser.add_argument('-api','--ap_info',   action='append', nargs=1, type=str, \
        help='(enter 0 if does not apply) --ap_info \"ap_scheme==<telnet,ssh or serial> ap_prompt==<ap_prompt> ap_ip==<ap ip> ap_port==<ap port number> ap_user==<ap user> ap_pw==<ap password> ap_tty==<tty serial device>\" ')
    #--ap_info "ap_scheme==serial ap_prompt==APA53.0E7B.CF9C ap_ip==0 ap_port==0 ap_user==admin ap_pw==Admin123 ap_tty==/dev/ttyUSB2"

    '''./lf_cisco_dfs.py -cc 192.168.100.112 -cu admin -cpw Cisco123 -cca APA453.0E7B.CF9C -ccf "a" -cwm "auto" -cc5 "36" \
    -ccw "20" -ccd "1" -cs "3504" --endp_type 'lf_udp' --upstream_port eth2  --cisco_wlan "test_candela" --cisco_wlanID 1 \
    --cisco_wlanSSID "test_candela" --cisco_directions "upstream" --cisco_prompt "(Cisco Controller)" \
    --radio "radio==1.wiphy0 stations==1  ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto" \
    --ap_info "ap_scheme==serial ap_prompt--APA53.0E7B.EF9C ap_ip==0 ap_port==0 ap_baud==9600 ap_user==admin ap_pw==Admin123 ap_tty==/dev/ttyUSB2" '''   


    # Parameters that allow for testing
    parser.add_argument('-noc','--no_controller',  help='--no_controller no configuration of the controller', action='store_true')
    parser.add_argument('-nos','--no_stations',    help='--no_stations , no stations', action='store_true')
    parser.add_argument('-wto','--wait_timeout',   help='--wait_timeout , time to wait for stations to get IP ', default="120")

    args = parser.parse_args()

    cisco_args = args

    #logg.info("args: {}".format(args))
    debug_on = args.debug

    ##################################################################
    # Gather Test Data
    #################################################################
 
    if args.test_duration:
        test_duration = args.test_duration

    if args.polling_interval:
        polling_interval = args.polling_interval

    if args.endp_type:
        endp_types = args.endp_type

    if args.mgr:
        lfjson_host = args.mgr

    if args.upstream_port:
        side_b = args.upstream_port

    if args.radio:
        radios = args.radio

    if args.csv_outfile != None:
        current_time = time.strftime("%m_%d_%Y_%H_%M_%S", time.localtime())
        csv_outfile = "{}_{}.csv".format(args.csv_outfile,current_time)
        csv_results = "results_{}_{}.csv".format(args.csv_outfile,current_time)
        print("csv output file : {}".format(csv_outfile))
      
    if args.log:
        outfile_log = "{}_{}_output_log.log".format(args.outfile,current_time)
        print("output file log: {}".format(outfile_log))
    else:
        outfile_log = "stdout"
        print("output file log: {}".format(outfile_log))    

    if args.wait_timeout:
        wait_timeout = int(args.wait_timeout)        

    if args.cisco_scheme:
        __scheme = args.cisco_scheme

    if args.cisco_port:
        __port = args.cisco_port

    if args.cisco_ctlr:
        __ctlr = args.cisco_ctlr

    if args.cisco_prompt:
        __prompt = args.cisco_prompt

    if args.cisco_series:
        __series = args.cisco_series    

    if args.cisco_user:
        __user = args.cisco_user

    if args.cisco_passwd:
        __passwd = args.cisco_passwd

    if args.cap_ctl_out:
        __cap_ctl_out = args.cap_ctl_out
    else:
        __cap_ctl_out = False
    
    if args.cisco_ap_slot:
        __ap_slot = args.cisco_ap_slot

    if args.cisco_dfs:
        __dfs = args.cisco_dfs
    else:
        __dfs = False

    if args.cisco_dfs_time:
        __dfs_time = args.cisco_dfs_time

    ap_dict = []
    if args.ap_info:
        ap_info = args.ap_info
        for _ap_info in ap_info:
            print("ap_info {}".format(_ap_info))
            ap_keys = ['ap_scheme','ap_prompt','ap_ip','ap_port','ap_user','ap_pw', 'ap_tty', 'ap_baud']
            ap_dict = dict(map(lambda x: x.split('=='), str(_ap_info).replace('[','').replace(']','').replace("'","").split()))
            for key in ap_keys:
                if key not in ap_dict:
                    print("missing ap config, for the {}, all these need to be set {} ".format(key,ap_keys))
                    exit(1)
            print("ap_dict: {}".format(ap_dict))


    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(FORMAT)
    logg = logging.getLogger(__name__)
    logg.setLevel(logging.DEBUG)
    file_handler = None
    if (args.log):
        file_handler = logging.FileHandler(outfile_log, "w")

        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logg.addHandler(file_handler)
        logg.addHandler(logging.StreamHandler(sys.stdout)) # allows to logging to file and stderr
        # if loggin.basicConfig is called this will result in duplicating log entries
        # logging.basicConfig(format=FORMAT, handlers=[file_handler])
    else:
        # stdout logging
        logging.basicConfig(format=FORMAT, handlers=[console_handler])


    ####################################################
    #
    #  Static Configuration Cisco Realm one lanforge
    #
    ####################################################
    radio_AX200_abgn_ax_list_001_one    = [['radio==1.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]

    radio_AX200_abgn_ax_list_010_one    = [['radio==1.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy2 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy3 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy4 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy5 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy6 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy7 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]


    radio_AX200_abgn_ax_dict_one = {'1'   : radio_AX200_abgn_ax_list_001_one, 
                                    '8'   : radio_AX200_abgn_ax_list_010_one} 

    
    radio_ath10K_9984_an_AC_list_001_one     = [['radio==1.wiphy8 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]
    radio_ath10K_9984_an_AC_list_010_one     = [['radio==1.wiphy8 stations==10 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]
    radio_ath10K_9984_an_AC_list_020_one     = [['radio==1.wiphy8 stations==20 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]

    radio_ath10K_9984_an_AC_dict_one = {'1'  : radio_ath10K_9984_an_AC_list_001_one,
                                        '10' : radio_ath10K_9984_an_AC_list_010_one,
                                        '20' : radio_ath10K_9984_an_AC_list_020_one}


    ####################################################
    #
    #  Static Configuration Cisco Realm
    #
    ####################################################
    radio_AX200_abgn_ax_list_001        = [['radio==1.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]

    radio_AX200_abgn_ax_list_010        = [['radio==1.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy2 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy3 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy4 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy5 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy6 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy7 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==2.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==2.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]


    radio_AX200_abgn_ax_list_020        =  [['radio==1.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy2 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy3 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy4 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy5 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy6 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy7 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==2.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==2.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==3.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==3.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==4.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==4.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==5.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==5.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==6.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==6.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==6.wiphy2 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==6.wiphy3 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ]

    radio_AX200_abgn_ax_list_024        =  [['radio==1.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy2 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy3 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy4 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy5 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy6 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==1.wiphy7 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==2.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==2.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==3.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==3.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==4.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==4.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==5.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==5.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==6.wiphy0 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==6.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==6.wiphy2 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==6.wiphy3 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==6.wiphy4 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==6.wiphy5 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==6.wiphy6 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ['radio==6.wiphy7 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                           ]


    radio_AX200_abgn_ax_dict = {'1'   : radio_AX200_abgn_ax_list_001, 
                                '10'  : radio_AX200_abgn_ax_list_010, 
                                '24'  : radio_AX200_abgn_ax_list_024}

    
    radio_ath10K_9984_an_AC_list_001     = [['radio==1.wiphy8 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]
    radio_ath10K_9984_an_AC_list_010     = [['radio==1.wiphy8 stations==10 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]
    radio_ath10K_9984_an_AC_list_020     = [['radio==1.wiphy8 stations==20 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]
    radio_ath10K_9984_an_AC_list_050     = [['radio==1.wiphy8 stations==50 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]
    radio_ath10K_9984_an_AC_list_100     = [['radio==1.wiphy8 stations==50 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                            ['radio==1.wiphy9 stations==50 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]
    radio_ath10K_9984_an_AC_list_200     = [['radio==1.wiphy8 stations==50 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                            ['radio==1.wiphy9 stations==50 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                            ['radio==6.wiphy8 stations==50 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto'],
                                            ['radio==6.wiphy9 stations==50 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]

    radio_ath10K_9984_an_AC_dict = {'1'  : radio_ath10K_9984_an_AC_list_001,
                                    '50' : radio_ath10K_9984_an_AC_list_050,
                                    '200': radio_ath10K_9984_an_AC_list_200}

    ####################################################
    #
    #  Static dictionaries for radios on 191.168.100.178
    #  Static Configuration Candela Tech Realm ()
    #
    ####################################################
    #iwlwifi(AX200) 521
    radio_AX200_abgn_ax_list_001_wiphy2  = [['radio==1.wiphy2 stations==1 ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto']]


    radio_AX200_abgn_ax_list_001     = [['radio==1.wiphy2 stations==1 ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto']]
    radio_AX200_abgn_ax_list_004     = [['radio==1.wiphy2 stations==1 ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto'],
                                        ['radio==1.wiphy3 stations==1 ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto'],
                                        ['radio==1.wiphy4 stations==1 ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto'],
                                        ['radio==1.wiphy5 stations==1 ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto']]

    radio_AX200_abgn_ax_dict_test   = {'1' : radio_AX200_abgn_ax_list_001,
                                       '4': radio_AX200_abgn_ax_list_004}

    radio_AX200_abgn_ax_dict_test_wiphy2 = {'1' : radio_AX200_abgn_ax_list_001_wiphy2}


    radio_ath10K_9984_an_AC_list_001    = [['radio==1.wiphy0 stations==1   ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto']]
    radio_ath10K_9984_an_AC_list_010    = [['radio==1.wiphy0 stations==10  ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto']]
    radio_ath10K_9984_an_AC_list_020    = [['radio==1.wiphy0 stations==20  ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto']]
    radio_ath10K_9984_an_AC_list_050    = [['radio==1.wiphy0 stations==50  ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto']]
    radio_ath9K_9984_an_AC_list_200     = [['radio==1.wiphy1 stations==200 ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto']]

    radio_ath10K_9984_an_AC_list_001_wiphy0  = [['radio==1.wiphy0 stations==1    ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto']]
    radio_ath10K_9984_an_AC_list_010_wiphy0  = [['radio==1.wiphy0 stations==10   ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto']]


    radio_ath10K_9984_an_AC_dict_test   = {'1'  : radio_ath10K_9984_an_AC_list_001,
                                          '10'  : radio_ath10K_9984_an_AC_list_010,
                                          '50'  : radio_ath10K_9984_an_AC_list_050,
                                          '200' : radio_ath9K_9984_an_AC_list_200}
    
    radio_ath10K_9984_an_AC_dict_test_wiphy0  = {'1'  : radio_ath10K_9984_an_AC_list_001_wiphy0,
                                                '10'  : radio_ath10K_9984_an_AC_list_010_wiphy0}

    MAX_NUMBER_OF_STATIONS = 200
    
    radio_name_list = []
    number_of_stations_per_radio_list = []
    ssid_list = []
    ssid_password_list = []
    ssid_security_list = []
    wifimode_list = []

    #optional radio configuration
    reset_port_enable_list = []
    reset_port_time_min_list = []
    reset_port_time_max_list = []

    wifi_mode_dict = {
        "auto"   : "0",
        "a"      : "1",
        "b"      : "2",
        "g"      : "3",
        "abg"    : "4",
        "abgn"   : "5",
        "bgn"    : "6",
        "bg"     : "7",
        "abgnAC" : "8",
        "anAC"   : "9",
        "an"     : "10",
        "bgnAC"  : "11",
        "abgnAX" : "12",
        "bgnAX"  : "13",
        "anAX"   : "14"
        }

    dfs_channel_bw20_values = [52, 56, 60, 64, 68, 96, 100, 104, 108, 112, 116, 120, 124 ,128, 132, 136, 140, 144]

    if args.cisco_all:
#        cisco_aps              = "APA453.0E7B.CF9C".split()
        cisco_aps              = "vanc-e".split()
#        cisco_bands            = "a b".split()
        cisco_bands            = "a ".split()
#        cisco_wifimodes        = "an anAX anAC abgn bg".split()
        cisco_wifimodes        = "an".split()
        cisco_tx_powers        = "3".split()
        cisco_chan_5ghzs       = "36".split()
        cisco_chan_24ghzs      = "1".split()
        cisco_chan_widths      = "20".split()
#        cisco_ap_modes         = "local flex".split()
        cisco_ap_modes         = "local".split()
        cisco_data_encryptions = "disable".split()
        cisco_packet_types     = "lf_udp lf_tcp".split()
        cisco_directions       = "upstream downstream".split()
        cisco_packet_sizes     = "1518".split()
        cisco_client_densities = "1".split()
        cisco_data_encryptions = "disable".split()

        cisco_side_a_min_bps  = 256000
        cisco_side_b_min_bps  = 256000

        radio_AX200_abgn_ax_dict     = radio_AX200_abgn_ax_dict_one
        radio_ath10K_9984_an_AC_dict = radio_ath10K_9984_an_AC_dict_one

    elif args.cisco_test:
        # Note the local system only supports 802.11-abgn , 802.11a
        cisco_aps              = "APA453.0E7B.CF9C".split()
        cisco_bands            = "a".split()
        #cisco_wifimodes        = "an anAX anAC abgn bg".split()
        cisco_wifimodes        = "an".split()
        cisco_tx_powers        = "3".split()
        cisco_chan_5ghzs       = "36".split()
        cisco_chan_24ghzs      = "1".split()
        cisco_chan_widths      = "20".split()
        cisco_ap_modes         = "local".split()
        cisco_data_encryptions = "disable".split()
        #cisco_packet_types     = "lf_udp lf_tcp".split()
        cisco_packet_types     = "lf_udp".split()
        #cisco_directions       = "upstream downstream".split()
        cisco_directions       = "upstream downstream".split()
        #cisco_packet_sizes     = "88 512 1370 1518".split()
        cisco_packet_sizes     = "1518".split()
        cisco_client_densities = "10".split()
        cisco_data_encryptions = "disable".split()

        cisco_side_a_min_bps  = 256000
        cisco_side_b_min_bps  = 256000

        radio_AX200_abgn_ax_dict     = radio_AX200_abgn_ax_dict_test
        radio_ath10K_9984_an_AC_dict = radio_ath10K_9984_an_AC_dict_test

    elif args.cisco_test2:
        # Note the local system only supports 802.11-abgn , 802.11a
        cisco_aps              = "APA453.0E7B.CF9C".split()
        cisco_bands            = "a".split()
        #cisco_wifimodes        = "an anAX anAC abgn bg".split()
        cisco_wifimodes        = "an".split()
        cisco_tx_powers        = "3".split()
        cisco_chan_5ghzs       = "52".split()
        cisco_chan_24ghzs      = "1".split()
        cisco_chan_widths      = "20".split()
        cisco_ap_modes         = "local".split()
        cisco_data_encryptions = "disable".split()
        #cisco_packet_types     = "lf_udp lf_tcp".split()
        cisco_packet_types     = "lf_udp".split()
        #cisco_directions       = "upstream downstream".split()
        cisco_directions       = "upstream downstream".split()
        #cisco_packet_sizes     = "88 512 1370 1518".split()
        cisco_packet_sizes     = "1518".split()
        cisco_client_densities = "1".split()
        cisco_data_encryptions = "disable".split()

        cisco_side_a_min_bps  = 256000
        cisco_side_b_min_bps  = 256000

        radio_AX200_abgn_ax_dict     = radio_AX200_abgn_ax_dict_test_wiphy2
        radio_ath10K_9984_an_AC_dict = radio_ath10K_9984_an_AC_dict_test_wiphy0

    else:    
        cisco_aps             = args.cisco_ap.split()
        cisco_bands           = args.cisco_band.split()
        cisco_wifimodes       = args.cisco_wifimode.split()
        for mode in cisco_wifimodes:
            if mode in wifi_mode_dict.keys():
                pass
            else:
                logg.info("wifimode [{}] not recognised. Please use: auto, a, b, g, abg, abgn, bgn, bg, abgnAC, anAC, an, bgnAC, abgnAX, bgnAX, anAX".format(mode))
                exit(1)
        cisco_tx_powers          = "3".split()
        cisco_chan_5ghzs         = args.cisco_chan_5ghz.split()
        cisco_chan_24ghzs        = args.cisco_chan_24ghz.split()
        cisco_chan_widths        = args.cisco_chan_width.split()
        cisco_ap_modes           = args.cisco_ap_mode.split()
        cisco_client_densities   = args.cisco_client_density.split()
        cisco_packet_types       = args.endp_type.split()
        cisco_directions         = args.cisco_directions.split()
        #cisco_directions         = "upstream".split()
        cisco_packet_sizes       = args.cisco_packet_size.split()
        cisco_data_encryptions   = args.cisco_data_encryption.split()

        cisco_side_a_min_bps    = args.side_a_min_bps
        cisco_side_b_min_bps    = args.side_b_min_bps

    
    logg.info(cisco_aps)
    logg.info(cisco_bands)
    logg.info(cisco_wifimodes)
    logg.info(cisco_tx_powers)
    logg.info(cisco_chan_5ghzs)
    logg.info(cisco_chan_24ghzs)
    logg.info(cisco_chan_widths)
    logg.info(cisco_ap_modes)
    logg.info(cisco_client_densities)
    logg.info(cisco_packet_types)
    logg.info(cisco_packet_sizes)
    logg.info(cisco_client_densities)
    logg.info(cisco_data_encryptions)
    if bool(ap_dict):
        logg.info("ap_dict {}".format(ap_dict))
    else:
        logg.info("AP NO login information")


    __ap_set          = None
    __band_set        = None
    __chan_width_set  = None
    __ap_mode_set     = None
    __tx_power_set    = None
    __chan_5ghz_set   = None
    __chan_24ghz_set  = None
    __csv_started     = False

    __dfs_channel     = None
    __cac_timer_time  = 0
    __dfs_chan_switch_to = None

    
    for cisco_ap in cisco_aps:
        for cisco_band in cisco_bands:  # frequency
            for cisco_wifimode in cisco_wifimodes:
                # check for valid frequency and wifi_mode combination put here to simplify logic since all radios do not support all modes
                # "an anAX anAC abgn bg"
                if((cisco_band == "a" and cisco_wifimode == "bg") or (cisco_band == "b" and cisco_wifimode == "anAC")):
                    logg.info("#######################################################################")
                    logg.info("# Skipping combination cisco_band {} cisco_wifimode {}".format(cisco_band,cisco_wifimode))
                    logg.info("#######################################################################")
                    pass # invalid combination continue  
                else:
                    # TODO the following 
                    #[(x, y, z) for x in [1,2,3] for y in [4,5,6] for z in [7,8,9] if x != z]:
                    for cisco_tx_power in cisco_tx_powers:
                        for cisco_chan_5ghz in cisco_chan_5ghzs:
                            for cisco_chan_24ghz in cisco_chan_24ghzs:
                                for cisco_chan_width in cisco_chan_widths: #bandwidth
                                    for cisco_data_encryption in cisco_data_encryptions:
                                        for cisco_ap_mode in cisco_ap_modes:
                                            for cisco_client_density in cisco_client_densities:
                                                for cisco_packet_type in cisco_packet_types:
                                                    for cisco_direction in cisco_directions:
                                                        for cisco_packet_size in cisco_packet_sizes:
                                                            logg.info("#####################################################")
                                                            logg.info("# TEST RUNNING ,  TEST RUNNING ######################")
                                                            logg.info("#####################################################")
                                                            test_config = "AP=={} Band=={} chan_5ghz=={} chan_24ghz=={} wifi_mode=={} BW=={} encryption=={} ap_mode=={} clients=={} packet_type=={} direction=={} packet_size=={}".format(
                                                                cisco_ap,cisco_band,cisco_chan_5ghz,cisco_chan_24ghz,cisco_wifimode,cisco_chan_width,cisco_data_encryption,cisco_ap_mode,cisco_client_density,
                                                                cisco_packet_type,cisco_direction,cisco_packet_size)
                                                            test_keys = ['AP','Band','wifi_mode','chan_5ghz','chan_24ghz','BW','encryption','ap_mode','clients','packet_type','direction','packet_size'] 
                                                            logg.info("# Cisco run settings: {}".format(test_config))
                                                            if(args.no_controller):
                                                                logg.info("################################################")
                                                                logg.info("# NO CONTROLLER SET , TEST MODE")
                                                                logg.info("################################################")
                                                            else:
                                                                if( cisco_ap            != __ap_set or 
                                                                    cisco_band          != __band_set or
                                                                    cisco_chan_width    != __chan_width_set or
                                                                    cisco_ap_mode       != __ap_mode_set or
                                                                    cisco_tx_power      != __tx_power_set or
                                                                    cisco_chan_5ghz     != __chan_5ghz_set or
                                                                    cisco_chan_24ghz    != __chan_24ghz_set
                                                                    ):
                                                                    logg.info("###############################################")
                                                                    logg.info("# NEW CONTROLLER CONFIG")
                                                                    logg.info("###############################################")
                                                                    __ap_set          = cisco_ap
                                                                    __band_set        = cisco_band
                                                                    __chan_width_set  = cisco_chan_width
                                                                    __ap_mode_set     = cisco_ap_mode
                                                                    __tx_power_set    = cisco_tx_power
                                                                    __chan_5ghz_set   = cisco_chan_5ghz
                                                                    __chan_24ghz_set  = cisco_chan_24ghz
                                                                    __client_density  = cisco_client_density
                                                                    cisco = CreateCtlr(
                                                                                    _scheme=__scheme,
                                                                                    _port=__port,
                                                                                    _series=__series,
                                                                                    _ctlr=__ctlr,
                                                                                    _prompt=__prompt,
                                                                                    _user=__user,
                                                                                    _passwd=__passwd,
                                                                                    _ap=__ap_set,
                                                                                    _band=__band_set,
                                                                                    _chan_5ghz=__chan_5ghz_set,
                                                                                    _chan_24ghz=__chan_24ghz_set,
                                                                                    _chan_width=__chan_width_set,
                                                                                    _ap_mode=__ap_mode_set,
                                                                                    _tx_power=__tx_power_set,
                                                                                    _client_density=__client_density,
                                                                                    _cap_ctl_out=__cap_ctl_out
                                                                                    )
                                                                    #Disable AP
                                                                    #
                                                                    # Controller Configuration
                                                                    #
                                                                    #if cisco_args.cisco_series == "9800":
                                                                    #    cisco_controller_no_loggin_console()
                                                                    pss = cisco.controller_show_ap_summary()
                                                                    logg.info("pss {}".format(pss))
                                                                    cisco.controller_disable_ap()
                                                                    if cisco_args.cisco_series == "9800":
                                                                        cisco.controller_disable_wlan()
                                                                        cisco.controller_disable_network_5ghz()
                                                                        cisco.controller_disable_network_24ghz()
                                                                        cisco.controller_role_manual()
                                                                    else:
                                                                        cisco.controller_disable_network_5ghz()
                                                                        cisco.controller_disable_network_24ghz()
                                                                    cisco.controller_set_tx_power()
                                                                    cisco.controller_set_bandwidth_20()
                                                                    cisco.controller_set_channel()
                                                                    cisco.controller_set_bandwidth()
                                                                    if cisco_args.cisco_series == "9800":
                                                                        cisco.controller_create_wlan()
                                                                        cisco.controller_set_wireless_tag_policy()
                                                                        cisco.controller_enable_wlan()
                                                                    if cisco_band == "a":    
                                                                        cisco.controller_enable_network_5ghz()
                                                                    else:    
                                                                        cisco.controller_enable_network_24ghz()
                                                                    # clear logs on AP  /dev/ttyUSB2 - candelatech
                                                                    if(bool(ap_dict)):
                                                                        logg.info("ap_dict {}".format(ap_dict))
                                                                        logg.info("Read AP action: {} ap_scheme: {} ap_ip: {} ap_port: {} ap_user: {} ap_pw: {} ap_tty: {} ap_baud: {}".format("show_log",ap_dict['ap_scheme'],ap_dict['ap_ip'],ap_dict["ap_port"],
                                                                                ap_dict['ap_user'],ap_dict['ap_pw'],ap_dict['ap_tty'],ap_dict['ap_baud']))

                                                                        # clear log  (AP)
                                                                        try:
                                                                            logg.info("cisco_ap_ctl.py: clear log")
                                                                            # TODO remove position dependence if in tree 
                                                                            ap_info= subprocess.run(["./../cisco_ap_ctl.py", "--scheme", ap_dict['ap_scheme'], "--prompt", ap_dict['ap_prompt'],"--dest", ap_dict['ap_ip'], "--port", ap_dict["ap_port"],
                                                                                                      "--user", ap_dict['ap_user'], "--passwd", ap_dict['ap_pw'],"--tty", ap_dict['ap_tty'],"--baud", ap_dict['ap_baud'],"--action", "clear_log"],capture_output=True, check=True)#stdout=subprocess.PIPE)
                                                                            try:
                                                                                pss = ap_info.stdout.decode('utf-8', 'ignore')
                                                                            except:
                                                                                logg.info("ap_info was of type NoneType will set pss empty")
                                                                                pss = "empty"
                                                                        except subprocess.CalledProcessError as process_error:
                                                                            logg.info("####################################################################################################") 
                                                                            logg.info("# CHECK IF AP HAS CONNECTION ALREADY ACTIVE") 
                                                                            logg.info("####################################################################################################") 
                                                                            logg.info("####################################################################################################") 
                                                                            logg.info("# Unable to commicate to AP error code: {} output {}".format(process_error.returncode, process_error.output)) 
                                                                            logg.info("####################################################################################################") 
                                                                        logg.info(pss)

                                                                        # show log  (AP)
                                                                        try:
                                                                            logg.info("cisco_ap_ctl.py: show log")
                                                                            # TODO remove position dependence if in tree 
                                                                            ap_info= subprocess.run(["./../cisco_ap_ctl.py", "--scheme", ap_dict['ap_scheme'], "--prompt", ap_dict['ap_prompt'],"--dest", ap_dict['ap_ip'], "--port", ap_dict["ap_port"],
                                                                                                      "--user", ap_dict['ap_user'], "--passwd", ap_dict['ap_pw'],"--tty", ap_dict['ap_tty'],"--baud", ap_dict['ap_baud'],"--action", "show_log"],capture_output=True, check=True) #stdout=subprocess.PIPE
                                                                            try:
                                                                                pss = ap_info.stdout.decode('utf-8', 'ignore')
                                                                            except:
                                                                                logg.info("ap_info was of type NoneType will set pss empty")
                                                                                pss = "empty"
                                                                        except subprocess.CalledProcessError as process_error:
                                                                            logg.info("####################################################################################################") 
                                                                            logg.info("# CHECK IF AP HAS CONNECTION ALREADY ACTIVE") 
                                                                            logg.info("####################################################################################################") 
                                                                            logg.info("####################################################################################################") 
                                                                            logg.info("# Unable to commicate to AP error code: {} output {}".format(process_error.returncode, process_error.output)) 
                                                                            logg.info("####################################################################################################") 
                                                                        logg.info(pss)

                                                                    cisco.controller_enable_ap()
                                                                    # need to actually check the CAC timer 
                                                                    time.sleep(10)
                                                                    # When the AP moves to another DFS channel, the wait time is 60 second
                                                                    # the CAC (Channel Avaiability Check Time) 
                                                                    if (int(__chan_5ghz_set) in dfs_channel_bw20_values):
                                                                        logg.info("DFS 5ghz channel {} being set wait CAC time 60, 2.4 ghz: {} : ".format(__chan_5ghz_set, __chan_24ghz_set))
                                                                        # read AP to verify CAC timer set
                                                                        # will need to use time to verify CAC from AP - need in results
                                                                        cac_sleeptime = "65" # 65
                                                                        logg.info("CAC start sleeptime: {}".format(cac_sleeptime))
                                                                        time.sleep(int(cac_sleeptime))
                                                                        logg.info("CAC done  sleeptime: {}".format(cac_sleeptime))
                                                                        if(bool(ap_dict)):
                                                                            # will need to verify that timer has timed out on AP - need in results
                                                                            logg.info("DFS channel 5ghz {} done waiting CAC time, 2.4 ghz: {}".format(__chan_5ghz_set, __chan_24ghz_set))
                                                                            logg.info("####################################################################################################") 
                                                                            logg.info("# READ changed to DFS channel {}, running CAC for 60 seconds.".format(__chan_5ghz_set))
                                                                            logg.info("# READ AP CAC_EXPIRY_EVT:  CAC finished on DFS channel <channel>") 
                                                                            logg.info("####################################################################################################") 

                                                                            logg.info("ap_dict {}".format(ap_dict))
                                                                            logg.info("Read AP action: {} ap_scheme: {} ap_ip: {} ap_port: {} ap_user: {} ap_pw: {} ap_tty: {} ap_baud: {}".format("show_log",ap_dict['ap_scheme'],ap_dict['ap_ip'],ap_dict["ap_port"],
                                                                                    ap_dict['ap_user'],ap_dict['ap_pw'],ap_dict['ap_tty'],ap_dict['ap_baud'],))

                                                                            try:
                                                                                logg.info("cisco_ap_ctl.py: read for CAC timer and CAC_EXPIRY_EVT")
                                                                                # TODO remove position dependence if in tree 
                                                                                ap_info= subprocess.run(["./../cisco_ap_ctl.py", "--scheme", ap_dict['ap_scheme'], "--prompt", ap_dict['ap_prompt'],"--dest", ap_dict['ap_ip'], "--port", ap_dict["ap_port"],
                                                                                                          "--user", ap_dict['ap_user'], "--passwd", ap_dict['ap_pw'],"--tty", ap_dict['ap_tty'],"--baud", ap_dict['ap_baud'],"--action", "cac_expiry_evt"],capture_output=True, check=True)
                                                                                try:
                                                                                    pss = ap_info.stdout.decode('utf-8', 'ignore')
                                                                                except:
                                                                                    logg.info("ap_info was of type NoneType will set pss empty")
                                                                                    pss = "empty"

                                                                            except subprocess.CalledProcessError as process_error:
                                                                                logg.info("####################################################################################################") 
                                                                                logg.info("# CHECK IF AP HAS CONNECTION ALREADY ACTIVE") 
                                                                                logg.info("####################################################################################################") 

                                                                                logg.info("####################################################################################################") 
                                                                                logg.info("# Unable to commicate to AP error code: {} output {}".format(process_error.returncode, process_error.output)) 
                                                                                logg.info("####################################################################################################") 

                                                                            logg.info(pss)
                                                                            # find the DFS Channel
                                                                            for line in pss.splitlines():
                                                                                logg.info("ap: {}".format(line))
                                                                                pat = 'CAC_EXPIRY_EVT:\s+\S+\s+\S+\s+\S+\s\S+\s\S+\s(\S+)'
                                                                                m = re.search(pat, line)
                                                                                if (m != None):
                                                                                    __dfs_channel = m.group(1)
                                                                                    logg.info("__dfs_channel: {}".format(__dfs_channel))
                                                                                    logg.info("__dfs_channel line: {}".format(line))
                                                                                    break
                                                                    else:
                                                                        logg.info("Non-DFS 5ghz channel {} being set sleep 30, 2.4 ghz: {} ".format(__chan_5ghz_set, __chan_24ghz_set))
                                                                        time.sleep(30)
                                                                    ##########################################
                                                                    # end of cisco controller code 
                                                                    ##########################################   
                                                                    
                                                                else:
                                                                    logg.info("###############################################")
                                                                    logg.info("# NO CHANGE TO CONTROLLER CONFIG")
                                                                    logg.info("###############################################")
                                                                    logg.info("cisco_ap: {} cisco_band: {} cisco_chan_width: {} cisco_ap_mode: {} cisco_tx_power: {} cisco_chan_5ghz: {} cisco_chan_24ghz: {}"
                                                                        .format(cisco_ap,cisco_band, cisco_chan_width, cisco_ap_mode, cisco_tx_power, cisco_chan_5ghz, cisco_chan_24ghz))
                                                                    logg.info("__ap_set: {} __band_set: {} __chan_width_set: {} __ap_mode_set: {} __tx_power_set: {} __chan_5ghz_set: {} __chan_24ghz_set: {}"
                                                                        .format(__ap_set,__band_set, __chan_width_set, __ap_mode_set, __tx_power_set, __chan_5ghz_set, __chan_24ghz_set))
                                                                logg.info("cisco_wifi_mode {}".format(cisco_wifimode))
                                                                pss = cisco.controller_show_ap_summary()
                                                                logg.info("controller_show_ap_summary:::  pss {}".format(pss))
                                                                if args.cisco_series == "9800":
                                                                    searchap = False
                                                                    cc_mac = ""
                                                                    cc_ch = ""
                                                                    cc_bw = ""
                                                                    cc_power = ""
                                                                    cc_dbm = ""
                                                                    for line in pss.splitlines():
                                                                        if (line.startswith("---------")):
                                                                            searchap = True
                                                                            continue
                                                                        # if the pattern changes save the output of the advanced command and re parse https://regex101.com
                                                                        if (searchap):
                                                                            pat = "%s\s+(\S+)\s+(%s)\s+\S+\s+\S+\s+(\S+)\s+(\S+)\s+(\S+)\s+dBm\)+\s+(\S+)+\s"%(__ap_set,__ap_slot)
                                                                            m = re.search(pat, line)
                                                                            if (m != None):
                                                                                if(m.group(2) == __ap_slot):
                                                                                    cc_mac = m.group(1)
                                                                                    cc_slot = m.group(2)
                                                                                    cc_ch = m.group(6);  # (132,136,140,144)
                                                                                    cc_power = m.group(4)
                                                                                    cc_power = cc_power.replace("/", " of ") # spread-sheets turn 1/8 into a date
                                                                                    cc_dbm = m.group(5)
                                                                                    cc_dbm = cc_dbm.replace("(","")
                                          
                                                                                    cc_ch_count = cc_ch.count(",") + 1
                                                                                    cc_bw = m.group(3)
                                                                                    logg.info("group 1: {} 2: {} 3: {} 4: {} 5: {} 6: {}".format(m.group(1),m.group(2),m.group(3),m.group(4),m.group(5),m.group(6)))
                                          
                                                                                    logg.info("9800 test_parameters cc_mac: read : {}".format(cc_mac))
                                                                                    logg.info("9800 test_parameters cc_slot: read : {}".format(cc_slot))
                                                                                    logg.info("9800 test_parameters cc_count: read : {}".format(cc_ch_count))
                                                                                    logg.info("9800 test_parameters cc_bw: read : {}".format(cc_bw))
                                                                                    logg.info("9800 test_parameters cc_power: read : {}".format(cc_power))
                                                                                    logg.info("9800 test_parameters cc_dbm: read : {}".format(cc_dbm))
                                                                                    logg.info("9800 test_parameters cc_ch: read : {}".format(cc_ch))
                                                                                    break
                                                                else:
                                                                    searchap = False
                                                                    cc_mac = ""
                                                                    cc_ch = ""
                                                                    cc_bw = ""
                                                                    cc_power = ""
                                                                    cc_dbm = ""
                                                                    ch_count = ""
                                                                    for line in pss.splitlines():
                                                                        if (line.startswith("---------")):
                                                                            searchap = True
                                                                            continue
                                                                        
                                                                        if (searchap):
                                                                            pat = "%s\s+(\S+)\s+\S+\s+\S+\s+\S+\s+(\S+)\s+(\S+)\s+\(\s*(\S+)\s+dBm"%(__ap_set)
                                                                            m = re.search(pat, line)
                                                                            if (m != None):
                                                                                cc_mac = m.group(1)
                                                                                cc_ch = m.group(2);  # (132,136,140,144)
                                                                                cc_power = m.group(3)
                                                                                cc_power = cc_power.replace("/", " of ", 1) # spread-sheets turn 1/8 into a date
                                                                                cc_dbm = m.group(4)
                                             
                                                                                ch_count = cc_ch.count(",")
                                                                                cc_bw = 20 * (ch_count + 1)
                                                                                
                                                                                logg.info("3504 test_parameters cc_mac: read : {}".format(cc_mac))
                                                                                logg.info("3504 test_parameters cc_count: read : {}".format(ch_count))
                                                                                logg.info("3504 test_parameters cc_bw: read : {}".format(cc_bw))
                                                                                logg.info("3504 test_parameters cc_power: read : {}".format(cc_power))
                                                                                logg.info("3504 test_parameters cc_dbm: read : {}".format(cc_dbm))
                                                                                logg.info("3504 test_parameters cc_ch: read : {}".format(cc_ch))
                                                                                break

                                                                if(cc_ch != cisco_chan_5ghz):
                                                                    logg.info("configured channel {} not equal controller channel {}".format(cisco_chan_5ghz,cc_ch))
                                                                ######################################################
                                                                # end of cisco controller code no change to controller
                                                                ######################################################                                                                
                                                                if args.radio:
                                                                    radios = args.radio
                                                                elif cisco_band == "a":
                                                                    if cisco_wifimode == "anAX" or cisco_wifimode == "abgn":
                                                                        #AX200 dual band
                                                                        radios = radio_AX200_abgn_ax_dict[cisco_client_density]
                                                                    elif cisco_wifimode == "an" or cisco_wifimode == "anAC" or cisco_wifimode =="auto":
                                                                        #ath10K only supports 5Ghz
                                                                        radios = radio_ath10K_9984_an_AC_dict[cisco_client_density]
                                                                    else:
                                                                        logg.info("##################################")
                                                                        logg.info("# INVALID COMBINATION 5ghz")
                                                                        logg.info("# Cisco run settings: {}".format(test_config))
                                                                        logg.info("##################################")
                                                                        exit(1)
                                                                else: # cisco_band == "b"
                                                                    if cisco_wifimode == "an" or cisco_wifimode == "anAX" or cisco_wifimode == "abgn" or  cisco_wifimode == "bg" or cisco_wifimode == "auto":
                                                                        #AX200 dual band
                                                                        radios = radio_AX200_abgn_ax_dict[cisco_client_density]
                                                                    else:
                                                                        logg.info("##################################")
                                                                        logg.info("# INVALID COMBINATION 24 ghz")
                                                                        logg.info("# Cisco run settings: {}".format(test_config))
                                                                        logg.info("##################################")
                                                                        exit(1)
                                                                logg.info("radios {}".format(radios))
                                                                for radio_ in radios:
                                                                    radio_keys = ['radio','stations','ssid','ssid_pw','security','wifimode']
                                                                    radio_info_dict = dict(map(lambda x: x.split('=='), str(radio_).replace('[','').replace(']','').replace("'","").split()))
                                                                    logg.info("radio_dict {}".format(radio_info_dict))
                                                                    for key in radio_keys:
                                                                        if key not in radio_info_dict:
                                                                            logg.info("missing config, for the {}, all of the following need to be present {} ".format(key,radio_keys))
                                                                            exit(1)
                                                                    radio_name_list.append(radio_info_dict['radio'])
                                                                    ssid_list.append(radio_info_dict['ssid'])
                                                                    ssid_password_list.append(radio_info_dict['ssid_pw'])
                                                                    ssid_security_list.append(radio_info_dict['security'])
                                                                    if args.radio:
                                                                        number_of_stations_per_radio_list.append(radio_info_dict['stations'])
                                                                        wifimode_list.append(int(wifi_mode_dict[radio_info_dict['wifimode']]))
                                                                    else: 
                                                                        number_of_stations_per_radio_list.append(radio_info_dict['stations'])
                                                                        wifimode_list.append(int(wifi_mode_dict[radio_info_dict['wifimode']]))
                                                                    optional_radio_reset_keys = ['reset_port_enable']
                                                                    radio_reset_found = True
                                                                    for key in optional_radio_reset_keys:
                                                                        if key not in radio_info_dict:
                                                                            #logg.info("port reset test not enabled")
                                                                            radio_reset_found = False
                                                                            break
                                                                        
                                                                    if radio_reset_found:
                                                                        reset_port_enable_list.append(True)
                                                                        reset_port_time_min_list.append(radio_info_dict['reset_port_time_min'])
                                                                        reset_port_time_max_list.append(radio_info_dict['reset_port_time_max'])
                                                                    else:
                                                                        reset_port_enable_list.append(False)
                                                                        reset_port_time_min_list.append('0s')
                                                                        reset_port_time_max_list.append('0s')
                                                            # no stations for testing reconfiguration of the controller - 
                                                            if(args.no_stations):
                                                                logg.info("##################################")
                                                                logg.info("# NO STATIONS")
                                                                logg.info("##################################")
                                                            else:
                                                                index = 0
                                                                station_lists = []
                                                                for (radio_name_, number_of_stations_per_radio_) in zip(radio_name_list,number_of_stations_per_radio_list):
                                                                    number_of_stations = int(number_of_stations_per_radio_)
                                                                    if number_of_stations > MAX_NUMBER_OF_STATIONS:
                                                                        logg.info("number of stations per radio exceeded max of : {}".format(MAX_NUMBER_OF_STATIONS))
                                                                        quit(1)
                                                                    station_list = LFUtils.portNameSeries(prefix_="sta", start_id_= 1 + index*1000, end_id_= number_of_stations + index*1000,
                                                                                                          padding_number_=10000, radio=radio_name_)
                                                                    station_lists.append(station_list)
                                                                    index += 1
                                                                # Run Traffic Upstream (STA to AP)
                                                                if(cisco_direction == "upstream"):
                                                                    side_a_min_bps = cisco_side_a_min_bps 
                                                                    side_b_min_bps = 0  
                                                                # Run Traffic Downstream (AP to STA)    
                                                                else:
                                                                    side_a_min_bps = 0 
                                                                    side_b_min_bps = cisco_side_b_min_bps  
                                                                # current default is to have a values
                                                                ip_var_test = L3VariableTime(
                                                                                                args=args,
                                                                                                _dfs=__dfs,
                                                                                                _dfs_time=__dfs_time,
                                                                                                _scheme=__scheme,
                                                                                                _port=__port,
                                                                                                _series=__series,
                                                                                                _ctlr=__ctlr,
                                                                                                _prompt=__prompt,
                                                                                                _user=__user,
                                                                                                _passwd=__passwd,
                                                                                                _ap=__ap_set,
                                                                                                _ap_slot=__ap_slot,
                                                                                                _band=__band_set,
                                                                                                _chan_5ghz=__chan_5ghz_set,
                                                                                                _chan_24ghz=__chan_24ghz_set,
                                                                                                _chan_width=__chan_width_set,
                                                                                                _ap_mode=__ap_mode_set,
                                                                                                _tx_power=__tx_power_set,
                                                                                                _client_density=__client_density,
                                                                                                _cap_ctl_out=__cap_ctl_out,
                                                                                                endp_type=cisco_packet_type,
                                                                                                tos=args.tos,
                                                                                                side_b=side_b,
                                                                                                radio_name_list=radio_name_list,
                                                                                                number_of_stations_per_radio_list=number_of_stations_per_radio_list,
                                                                                                ssid_list=ssid_list,
                                                                                                ssid_password_list=ssid_password_list,
                                                                                                ssid_security_list=ssid_security_list, 
                                                                                                wifimode_list=wifimode_list, 
                                                                                                station_lists= station_lists,
                                                                                                name_prefix="LT-",
                                                                                                debug_on=debug_on, 
                                                                                                wait_timeout=wait_timeout,
                                                                                                outfile=csv_outfile,
                                                                                                results=csv_results,
                                                                                                test_keys=test_keys,
                                                                                                test_config=test_config,
                                                                                                reset_port_enable_list=reset_port_enable_list,
                                                                                                reset_port_time_min_list=reset_port_time_min_list,
                                                                                                reset_port_time_max_list=reset_port_time_max_list,
                                                                                                csv_started=__csv_started,
                                                                                                side_a_min_bps =side_a_min_bps, 
                                                                                                side_a_max_bps =0,
                                                                                                side_a_min_pdu =cisco_packet_size, 
                                                                                                side_a_max_pdu =0,
                                                                                                side_b_min_bps =side_b_min_bps, 
                                                                                                side_b_max_bps =0,
                                                                                                side_b_min_pdu =cisco_packet_size, 
                                                                                                side_b_max_pdu = 0,
                                                                                                number_template="00", 
                                                                                                test_duration=test_duration,
                                                                                                polling_interval= polling_interval,
                                                                                                lfclient_host=lfjson_host,
                                                                                                lfclient_port=lfjson_port)
                                                                __csv_started = True
                                                                ip_var_test.pre_cleanup()
                                                                ip_var_test.build()
                                                                if not ip_var_test.passes():
                                                                    logg.info("build step failed.")
                                                                    logg.info(ip_var_test.get_fail_message())
                                                                    exit(1) 
                                                                client_density = ip_var_test.station_bringup()    
                                                                #cisco.verify_controller(client_density)
                                                                ip_var_test.start(False, False)
                                                                ip_var_test.stop()
                                                                if not ip_var_test.passes():
                                                                    logg.info("stop test failed")
                                                                    logg.info(ip_var_test.get_fail_message())
                                                                # clean up 
                                                                radio_name_list = []
                                                                number_of_stations_per_radio_list = []
                                                                ssid_list = []
                                                                ssid_password_list = []
                                                                ssid_security_list = []
                                                                wifimode_list = []
                                                                ip_var_test.cleanup()
                                                                if ( args.no_stations):
                                                                    pass
                                                                else:
                                                                    ip_var_test.passes()
                                                                    logg.info("Test Complete")

if __name__ == "__main__":
    main()


''' 
SAMPLE Command 2/15/2021
./lf_cisco_dfs.py -cc 192.168.100.112 -cu admin -cpw Cisco123 -cca APA453.0E7B.CF9C -ccf "a" -cwm "auto" -cc5 "52 56 60 64 68 96 100 104 108 112 116 120 124 128 132 136 140 144" -ccw "20" -ccd "1" -cs "3504" --endp_type 'lf_udp' --upstream_port eth2  --cisco_wlan "test_candela" --cisco_wlanID 1 --cisco_wlanSSID "test_candela" --cisco_directions "upstream" --cisco_prompt "(Cisco Controller)" --radio "radio==1.wiphy0 stations==1  ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto" 

SAMPLE Command with AP
 ./lf_cisco_dfs.py -cc 192.168.100.112 -cu admin -cpw Cisco123 -cca APA453.0E7B.CF9C -ccf "a" -cwm "auto" -cc5 "52" -ccw "20" -ccd "1" -cs "3504" --endp_type 'lf_udp' --upstream_port eth2  --cisco_wlan "test_candela" --cisco_wlanID 1 --cisco_wlanSSID "test_candela" --cisco_directions "upstream" --cisco_prompt "(Cisco Controller)" --radio "radio==1.wiphy0 stations==1  ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto" --ap_info "ap_scheme==serial ap_prompt==APA453.0E7B.CF9C ap_ip==0 ap_port==0 ap_user==admin ap_pw==Admin123 ap_tty==/dev/ttyUSB2 ap_baud==9600"
'''

