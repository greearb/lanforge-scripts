#!/usr/bin/env python3

import sys
import os

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

import argparse
from LANforge.lfcli_base import LFCliBase
from LANforge import LFUtils
import realm
import time
import datetime
import subprocess
import re
import csv
import random


######################################

class cisco_():
    def __init__(self, args):
        self.args = args

    #show summary (to get AP) (3400/9800)
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 --action summary --series 9800 --log stdout
    def controller_show_summary(self):
        try:
            print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,self.args.cisco_user,
                self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, self.args.cisco_band,"summary"))

            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                    self.args.cisco_user, "-p", self.args.cisco_passwd,
                                    "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, "--action", "summary"], 
                                    capture_output=self.args.cap_ctl_out, check=True)
            if self.args.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                print(pss)

        except subprocess.CalledProcessError as process_error:
                print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}"
                    .format(process_error.returncode, process_error.output))
                time.sleep(1)
                exit(1)


    #show ap dot11 5ghz summary (band defaults to 5ghz) --band a
    #show ap dot11 24ghz summary use --band b for 2.4 ghz
    #action advanced  (3400/9800)
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 --action advanced --series 9800 --log stdout
    def controller_show_ap_summary(self):
        try:
            print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,self.args.cisco_user,
                self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, self.args.cisco_band,"advanced"))

            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                    self.args.cisco_user, "-p", self.args.cisco_passwd,
                                    "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, "--action", "advanced"], 
                                    capture_output=self.args.cap_ctl_out, check=True)
            if self.args.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                print(pss)

        except subprocess.CalledProcessError as process_error:
            print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)

    #show wlan summary
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 --action show_wlan_summary --series 9800 --log stdout
    def controller_show_wlan_summary(self):
        try:
            print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,self.args.cisco_user,
                self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, self.args.cisco_band,"show wlan summary"))

            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                    self.args.cisco_user, "-p", self.args.cisco_passwd,
                                    "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, "--action", "show_wlan_summary"], 
                                    capture_output=self.args.cap_ctl_out, check=True)

            if self.args.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                print(pss)

        except subprocess.CalledProcessError as process_error:
            print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)

    #disable AP
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action disable --series 9800
    def controller_disable_ap(self):
        try:
            print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,self.args.cisco_user,
                self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, self.args.cisco_band,"disable"))

            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                    self.args.cisco_user, "-p", self.args.cisco_passwd,
                                    "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, "--action", "disable"], 
                                    capture_output=self.args.cap_ctl_out, check=True)

            if self.args.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                print(pss)

        except subprocess.CalledProcessError as process_error:
            print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)


    #disable wlan
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action disable_wlan --series 9800
    def controller_disable_wlan(self):
        try:
            print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,self.args.cisco_user,
                self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, self.args.cisco_band,"disable_wlan"))

            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                    self.args.cisco_user, "-p", self.args.cisco_passwd,
                                    "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, "--action", "disable_wlan"], 
                                    capture_output=self.args.cap_ctl_out, check=True)

            if self.args.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                print(pss)

        except subprocess.CalledProcessError as process_error:
            print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)


    #disable network 5ghz
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action disable_network_5ghz --series 9800
    def controller_disable_network_5ghz(self):
        if self.args.cisco_series == "9800":
            try:
                print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,self.args.cisco_user,
                    self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, self.args.cisco_band,"disable_network_5ghz"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                        self.args.cisco_user, "-p", self.args.cisco_passwd,
                                        "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, "--action", "disable_network_5ghz"], 
                                        capture_output=self.args.cap_ctl_out, check=True)

                if self.args.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    print(pss)

            except subprocess.CalledProcessError as process_error:
                print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            try:
                print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {} value: {}".format(self.args.cisco_scheme,
                    self.args.cisco_ctlr,self.args.cisco_user,self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series,
                    self.args.cisco_band,"cmd","config 802.11a disable network"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                        self.args.cisco_user, "-p", self.args.cisco_passwd,
                                        "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, "--action", "cmd", "--value", "config 802.11a disable network"], 
                                        capture_output=self.args.cap_ctl_out, check=True)

                if self.args.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    print(pss)

            except subprocess.CalledProcessError as process_error:
                print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)


    #disable network 24ghz
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action disable_network_24ghz --series 9800
    def controller_disable_network_24ghz(self):
        if self.args.cisco_series == "9800":
            try:
                print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,self.args.cisco_user,
                    self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, self.args.cisco_band,"disable_network_24ghz"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                        self.args.cisco_user, "-p", self.args.cisco_passwd,
                                        "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, "--action", "disable_network_24ghz"], 
                                        capture_output=self.args.cap_ctl_out, check=True)

                if self.args.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    print(pss)

            except subprocess.CalledProcessError as process_error:
                print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            try:
                print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {} value: {}".format(self.args.cisco_scheme,
                    self.args.cisco_ctlr,self.args.cisco_user,self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series,
                    self.args.cisco_band,"cmd","config 802.11b disable network"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                        self.args.cisco_user, "-p", self.args.cisco_passwd,
                                        "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, "--action", "cmd", "--value", "config 802.11b disable network"], 
                                        capture_output=self.args.cap_ctl_out, check=True)

                if self.args.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    print(pss)

            except subprocess.CalledProcessError as process_error:
                print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)



    #set manual mode - Series 9800 must be set to manual mode
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action manual --series 9800
    # ap name <AP NAME> dot11 5ghz radio role manual client-serving
    def controller_role_manual(self):
        if self.args.cisco_series == "9800":
            try:
                print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,self.args.cisco_user,
                    self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, self.args.cisco_band,"manual"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                        self.args.cisco_user, "-p", self.args.cisco_passwd,
                                        "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, "--action", "manual"], 
                                        capture_output=self.args.cap_ctl_out, check=True)

                if self.args.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    print(pss)

            except subprocess.CalledProcessError as process_error:
                print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            print("Check the cisco_scheme used attemping 9800 series on 3504 controller: {}".format(self.args.cisco_scheme))

    #set manual mode - Series 9800 must be set to auto mode
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action auto --series 9800
    # ap name <AP NAME> dot11 5ghz radio role manual client-serving
    def controller_role_auto(self):
        if self.args.cisco_series == "9800":
            try:
                print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,self.args.cisco_user,
                    self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, self.args.cisco_band,"auto"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                        self.args.cisco_user, "-p", self.args.cisco_passwd,
                                        "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, "--action", "auto"], 
                                        capture_output=self.args.cap_ctl_out, check=True)

                if self.args.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    print(pss)

            except subprocess.CalledProcessError as process_error:
                print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            print("Check the cisco_scheme used attemping 9800 series on 3504 controller: {}".format(self.args.cisco_scheme))

    #test parameters summary (txPower 1-8)
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action txPower  --value 5 --series 9800
    def controller_set_tx_power(self):
        try:
            print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {} value {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,
                self.args.cisco_user,self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, 
                self.args.cisco_band,"txPower", self.args.cisco_tx_power ))  # TODO fix txPower to tx_power in cisco_wifi_ctl.py
            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                    self.args.cisco_user, "-p", self.args.cisco_passwd,
                                    "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, 
                                    "--action", "txPower","--value", self.args.cisco_tx_power], 
                                    capture_output=self.args.cap_ctl_out, check=True)

            if self.args.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                print(pss)

        except subprocess.CalledProcessError as process_error:
            print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)


    #set channel [36, 64, 100]
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action channel  --value 36 --series 9800
    # 9800 : ap name <AP> dot11 [5ghz | 24ghz] channel <channel>
    # 3504 : (Cisco Controller) >config 802.11a channel ap APA453.0E7B.CF9C  52
    def controller_set_channel(self):
        try:
            print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {} value {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,
                self.args.cisco_user,self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, 
                self.args.cisco_band,"channel", self.args.cisco_channel ))
            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                    self.args.cisco_user, "-p", self.args.cisco_passwd,
                                    "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, 
                                    "--action", "channel","--value", self.args.cisco_channel], 
                                    capture_output=self.args.cap_ctl_out, check=True)

            if self.args.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                print(pss)

        except subprocess.CalledProcessError as process_error:
            print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)


    #set bandwidth [20 40 80 160]
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action bandwidth  --value 40 --series 9800
    def controller_set_bandwidth(self):
        try:
            print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {} value {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,
                self.args.cisco_user,self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, 
                self.args.cisco_band,"channel", self.args.cisco_chan_width ))
            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                    self.args.cisco_user, "-p", self.args.cisco_passwd,
                                    "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, 
                                    "--action", "channel","--value", self.args.cisco_chan_width], 
                                    capture_output=self.args.cap_ctl_out, check=True)

            if self.args.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                print(pss)
            
        except subprocess.CalledProcessError as process_error:
            print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)


    #create wlan
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action create_wlan  --wlan "open-wlan"  --wlanID 1 --series 9800
    def controller_create_wlan(self):
        if self.args.cisco_series == "9800":
            try:
                print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {} wlan {} wlanID {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,
                    self.args.cisco_user,self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, 
                    self.args.cisco_band,"create_wlan", self.args.cisco_wlan, self.args.cisco_wlanID ))
                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                        self.args.cisco_user, "-p", self.args.cisco_passwd,
                                        "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, 
                                        "--action", "create_wlan","--wlan", self.args.cisco_wlan, "--wlanID", self.args.cisco_wlanID], 
                                        capture_output=self.args.cap_ctl_out, check=True)

                if self.args.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    print(pss)
                
            except subprocess.CalledProcessError as process_error:
                print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            print("Check the cisco_scheme used attemping 9800 series on 3504 controller: {}".format(self.args.cisco_scheme))

    #create wireless tag policy  --9800 series needs to have wireless tag policy set
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action wireless_tag_policy --series 9800
    def controller_set_wireless_tag_policy(self):
        if self.args.cisco_series == "9800":
            try:
                print("scheme {} ctlr {} user {} passwd {} AP {} series {} band {} action {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,
                    self.args.cisco_user,self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, 
                    self.args.cisco_band,"wireless_tag_policy" ))
                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                        self.args.cisco_user, "-p", self.args.cisco_passwd,
                                        "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, 
                                        "--action", "wireless_tag_policy"], 
                                        capture_output=self.args.cap_ctl_out, check=True)

                if self.args.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    print(pss)

            except subprocess.CalledProcessError as process_error:
                print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            print("Check the cisco_scheme used attemping 9800 series on 3504 controller: {}".format(self.args.cisco_scheme))


    #enable wlan
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action enable_wlan --series 9800
    def controller_enable_wlan(self):
        try:
            print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,
                self.args.cisco_user,self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, 
                self.args.cisco_band,"enable_wlan"))
            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                    self.args.cisco_user, "-p", self.args.cisco_passwd,
                                    "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, 
                                    "--action", "enable_wlan"], 
                                    capture_output=self.args.cap_ctl_out, check=True)

            if self.args.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                print(pss)
            
        except subprocess.CalledProcessError as process_error:
            print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)


    #enable 5ghz
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action enable_network_5ghz --series 9800
    def controller_enable_network_5ghz(self):
        if self.args.cisco_series == "9800":
            try:
                print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,
                    self.args.cisco_user,self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, 
                    self.args.cisco_band,"enable_network_5ghz"))
                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                        self.args.cisco_user, "-p", self.args.cisco_passwd,
                                        "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, 
                                        "--action", "enable_network_5ghz"], 
                                        capture_output=self.args.cap_ctl_out, check=True)

                if self.args.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    print(pss)
                
            except subprocess.CalledProcessError as process_error:
                print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            try:
                print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {} value: {}".format(self.args.cisco_scheme,
                    self.args.cisco_ctlr,self.args.cisco_user,self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series,
                    self.args.cisco_band,"cmd","config 802.11a enable network"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                        self.args.cisco_user, "-p", self.args.cisco_passwd,
                                        "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, "--action", "cmd", "--value", "config 802.11a enable network"], 
                                        capture_output=self.args.cap_ctl_out, check=True)

                if self.args.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    print(pss)

            except subprocess.CalledProcessError as process_error:
                print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)



    #enable 24ghz
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action enable_network_24ghz --series 9800
    def controller_enable_network_24ghz(self):
        if self.args.cisco_series == "9800":
            try:
                print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,
                    self.args.cisco_user,self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, 
                    self.args.cisco_band,"enable_network_24ghz"))
                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                        self.args.cisco_user, "-p", self.args.cisco_passwd,
                                        "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, 
                                        "--action", "enable_network_24ghz"], 
                                        capture_output=self.args.cap_ctl_out, check=True)

                if self.args.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    print(pss)

            except subprocess.CalledProcessError as process_error:
                print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)
        else:
            try:
                print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {} value: {}".format(self.args.cisco_scheme,
                    self.args.cisco_ctlr,self.args.cisco_user,self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series,
                    self.args.cisco_band,"cmd","config 802.11b enable network"))

                ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                        self.args.cisco_user, "-p", self.args.cisco_passwd,
                                        "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, "--action", "cmd", "--value", "config 802.11b enable network"], 
                                        capture_output=self.args.cap_ctl_out, check=True)

                if self.args.cap_ctl_out:
                    pss = ctl_output.stdout.decode('utf-8', 'ignore')
                    print(pss)

            except subprocess.CalledProcessError as process_error:
                print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                    format(process_error.returncode, process_error.output))
                time.sleep(1) 
                exit(1)



    #enable (band a)
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action enable --series 9800
    def controller_enable_ap(self):
        try:
            print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,
                self.args.cisco_user,self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, 
                self.args.cisco_band,"enable"))
            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                    self.args.cisco_user, "-p", self.args.cisco_passwd,
                                    "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--band", self.args.cisco_band, 
                                    "--action", "enable"], 
                                    capture_output=self.args.cap_ctl_out, check=True)

            if self.args.cap_ctl_out:
                pss = ctl_output.stdout.decode('utf-8', 'ignore')
                print(pss)

        except subprocess.CalledProcessError as process_error:
            print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}".
                format(process_error.returncode, process_error.output))
            time.sleep(1) 
            exit(1)


    #advanced (showes summary)
    #./cisco_wifi_ctl.py --scheme ssh -d 172.19.36.168 -p <controller_pw> --port 23 -a "9120-Chamber-1" --band a --action advanced --series 9800
    def controller_show_ap_channel(self):
        advanced = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                   self.args.cisco_user, "-p", self.args.cisco_passwd,
                                   "-a", self.args.cisco_ap,"--series", self.args.cisco_series, "--action", "ap_channel"], capture_output=True)

        pss = advanced.stdout.decode('utf-8', 'ignore')
        print(pss)

        if self.args.cisco_series == "9800":
            for line in pss.splitlines():
                search_str = self.args.cisco_ap
                print("line {}".format(line))
                element_list = line.lstrip().split()
                print("element_list {}".format(element_list))
                if (line.lstrip().startswith(search_str)):
                    print("line {}".format(line))
                    element_list = line.lstrip().split()
                    print("element_list {}".format(element_list))
                    # AP Name (0) mac (1) slot (2) Admin State [enable/disable] (3) Oper State [Up/Down] (4) Width (5) Txpwr (6,7) channel (8) mode (9)
                    print("ap: {} slof {} channel {}  chan_width {}".format(element_list[0],element_list[2],element_list[8],element_list[5]))
                    if (str(self.args.cisco_channel) in str(element_list[8])) and (str(self.args.cisco_chan_width) in str(element_list[5])):
                        print("ap {} configuration successful: channel {} in expected {}  chan_width {} in expected {}"
                        .format(element_list[0],self.args.cisco_channel,element_list[8],self.args.cisco_chan_width,element_list[5])) 
                    else:
                        print("WARNING ap {} configuration: channel {} in expected {}  chan_width {} in expected {}"
                        .format(element_list[0],self.args.cisco_channel,element_list[8],self.args.cisco_chan_width,element_list[5])) 
                    break
        else:
            print("checking for 802.11{}".format(self.args.cisco_band))

            for line in pss.splitlines():
                #print("line {}".format(line))
                search_str = "802.11{}".format(self.args.cisco_band)
                if (line.lstrip().startswith(search_str)):
                    print("line {}".format(line))
                    element_list = line.lstrip().split()
                    print("element_list {}".format(element_list))
                    print("ap: {} channel {}  chan_width {}".format(self.args.cisco_ap,element_list[4],element_list[5]))
                    if (str(self.args.cisco_channel) in str(element_list[4])) and (str(self.args.cisco_chan_width) in str(element_list[5])):
                        print("ap configuration successful: channel {} in expected {}  chan_width {} in expected {}"
                        .format(self.args.cisco_channel,element_list[4],self.args.cisco_chan_width,element_list[5])) 
                    else:
                        print("AP WARNING: channel {} expected {}  chan_width {} expected {}"
                        .format(element_list[4],self.cisco_channel,element_list[5],self.args.cisco_chan_width)) 
                    break
        
        print("configure ap {} channel {} chan_width {}".format(self.args.cisco_ap,self.args.cisco_channel,self.args.cisco_chan_width))
        # Verify channel and channel width. 

##########################################

class L3VariableTime(LFCliBase):
    def __init__(self, host, port, endp_types, args, tos, side_b, radio_name_list, number_of_stations_per_radio_list,
                 ssid_list, ssid_password_list, ssid_security_list, wifimode_list,station_lists, name_prefix, debug_on, outfile,
                 reset_port_enable_list,
                 reset_port_time_min_list,
                 reset_port_time_max_list,
                 side_a_min_rate=560000, side_a_max_rate=0,
                 side_b_min_rate=560000, side_b_max_rate=0,
                 number_template="00", test_duration="256s",
                 polling_interval="60s",
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.port = port
        self.tos = tos.split()
        self.endp_types = endp_types.split()
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
        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port, debug_=debug_on)
        self.polling_interval_seconds = self.local_realm.duration_time_to_seconds(polling_interval)
        self.cx_profile = self.local_realm.new_l3_cx_profile()
        self.multicast_profile = self.local_realm.new_multicast_profile()
        self.multicast_profile.name_prefix = "MLT-";
        self.station_profiles = []
        self.args = args
        self.outfile = outfile
        self.csv_started = False
        self.epoch_time = int(time.time())
        self.debug = debug_on
        

        # Some checking on the duration
        #self.local_realm.parse_time(self.test_duration)
        #if (    (radio_info_dict['reset_port_time_min'] >= args.test_duration)  
        #    or  (radio_info_dict['reset_port_time_max'] >= args.test_duration)):
        #    print("port reset times min {} max {} mismatched with test duration {}"\
        #        .format(radio_info_dict['reset_port_time_min'],radio_info_dict['reset_port_time_max'],args.test_duration)))
        #    exit(1)


        # Full spread-sheet data
        if self.outfile is not None:
            self.csv_file = open(self.outfile, "w") 
            self.csv_writer = csv.writer(self.csv_file, delimiter=",")
        
        for (radio_, ssid_, ssid_password_, ssid_security_, wifimode_,\
            reset_port_enable_, reset_port_time_min_, reset_port_time_max_) \
            in zip(radio_name_list, ssid_list, ssid_password_list, ssid_security_list, wifimode_list,\
            reset_port_enable_list, reset_port_time_min_list, reset_port_time_max_list):
            self.station_profile = self.local_realm.new_station_profile()
            self.station_profile.lfclient_url = self.lfclient_url
            self.station_profile.ssid = ssid_
            self.station_profile.ssid_pass = ssid_password_
            self.station_profile.security = ssid_security_
            self.station_profile.mode = wifimode_ 
            self.station_profile.number_template = self.number_template
            self.station_profile.mode = wifimode_  
            self.station_profile.set_reset_extra(reset_port_enable=reset_port_enable_,\
                test_duration=self.local_realm.duration_time_to_seconds(self.test_duration),\
                reset_port_min_time=self.local_realm.duration_time_to_seconds(reset_port_time_min_),\
                reset_port_max_time=self.local_realm.duration_time_to_seconds(reset_port_time_max_))
            self.station_profiles.append(self.station_profile)
        
        self.multicast_profile.host = self.host
        self.cx_profile.host = self.host
        self.cx_profile.port = self.port
        self.cx_profile.name_prefix = self.name_prefix
        self.cx_profile.side_a_min_bps = side_a_min_rate
        self.cx_profile.side_a_max_bps = side_a_max_rate
        self.cx_profile.side_b_min_bps = side_b_min_rate
        self.cx_profile.side_b_max_bps = side_b_max_rate

    def __get_rx_values(self):
        endp_list = self.json_get("endp?fields=name,rx+bytes,rx+drop+%25", debug_=False)
        endp_rx_drop_map = {}
        endp_rx_map = {}
        our_endps = {}
        for e in self.multicast_profile.get_mc_names():
            our_endps[e] = e;
        for e in self.cx_profile.created_endp.keys():
            our_endps[e] = e;
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

        csv_rx_drop_percent_data = [self.epoch_time, self.time_stamp(),'rx_drop_percent']
        for key in [key for key in rx_drop_percent if "mtx" in key]: del rx_drop_percent[key]

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
            #print(item, "rx drop percent: ", rx_drop_percent[item])
            csv_rx_drop_percent_data.append(rx_drop_percent[item])

        self.csv_add_row(csv_rx_drop_percent_data,self.csv_writer,self.csv_file)

    def __compare_vals(self, old_list, new_list):
        passes = 0
        expected_passes = 0
        csv_performance_values = []
        csv_rx_headers = []
        csv_rx_delta_dict = {}

        # this may need to be a list as more monitoring takes place.
        csv_rx_row_data = [self.epoch_time, self.time_stamp(),'rx']
        csv_rx_delta_row_data = [self.epoch_time, self.time_stamp(),'rx_delta']

        for key in [key for key in old_list if "mtx" in key]: del old_list[key]
        for key in [key for key in new_list if "mtx" in key]: del new_list[key]

        filtered_values = [v for _, v in new_list.items() if v !=0]
        average_rx= sum(filtered_values) / len(filtered_values) if len(filtered_values) != 0 else 0

        csv_performance_values=sorted(new_list.items(), key=lambda x: (x[1],x[0]), reverse=False)
        csv_performance_values=self.csv_validate_list(csv_performance_values,5)
        for i in range(5):
            csv_rx_row_data.append(str(csv_performance_values[i]).replace(',',';'))
        for i in range(-1,-6,-1):
            csv_rx_row_data.append(str(csv_performance_values[i]).replace(',',';'))

        csv_rx_row_data.append(average_rx)

        if len(old_list) == len(new_list):
            for item, value in old_list.items():
                expected_passes +=1
                if new_list[item] > old_list[item]:
                    passes += 1
                    #if self.debug: print(item, new_list[item], old_list[item], " Difference: ", new_list[item] - old_list[item])
                    print(item, new_list[item], old_list[item], " Difference: ", new_list[item] - old_list[item])
                else:
                    print("Failed to increase rx data: ", item, new_list[item], old_list[item])
                if not self.csv_started:
                    csv_rx_headers.append(item)
                csv_rx_delta_dict.update({item:(new_list[item] - old_list[item])})
                

            if not self.csv_started:
                csv_header = self.csv_generate_column_headers()
                csv_header += csv_rx_headers
                print(csv_header)
                self.csv_add_column_headers(csv_header)
                self.csv_started = True

            # need to generate list first to determine worst and best
            filtered_values = [v for _, v in csv_rx_delta_dict.items() if v !=0]
            average_rx_delta= sum(filtered_values) / len(filtered_values) if len(filtered_values) != 0 else 0

            csv_performance_delta_values=sorted(csv_rx_delta_dict.items(), key=lambda x: (x[1],x[0]), reverse=False)
            csv_performance_delta_values=self.csv_validate_list(csv_performance_delta_values,5)
            for i in range(5):
                csv_rx_delta_row_data.append(str(csv_performance_delta_values[i]).replace(',',';'))
            for i in range(-1,-6,-1):
                csv_rx_delta_row_data.append(str(csv_performance_delta_values[i]).replace(',',';'))

            csv_rx_delta_row_data.append(average_rx_delta)
            
            for item, value in old_list.items():
                expected_passes +=1
                if new_list[item] > old_list[item]:
                    passes += 1
                    #if self.debug: print(item, new_list[item], old_list[item], " Difference: ", new_list[item] - old_list[item])
                    print(item, new_list[item], old_list[item], " Difference: ", new_list[item] - old_list[item])
                else:
                    print("Failed to increase rx data: ", item, new_list[item], old_list[item])
                if not self.csv_started:
                    csv_rx_headers.append(item)
                csv_rx_row_data.append(new_list[item])
                csv_rx_delta_row_data.append(new_list[item] - old_list[item])

            self.csv_add_row(csv_rx_row_data,self.csv_writer,self.csv_file)
            self.csv_add_row(csv_rx_delta_row_data,self.csv_writer,self.csv_file)

            if passes == expected_passes:
                return True
            else:
                return False
        else:
            print("Old-list length: %i  new: %i does not match in compare-vals."%(len(old_list), len(new_list)))
            print("old-list:",old_list)
            print("new-list:",new_list)
            return False

    def verify_controller(self):
        if self.args == None:
            return

        if self.args.cisco_ctlr == None:
            return

        try:
            print("scheme: {} ctlr: {} user: {} passwd: {} AP: {} series: {} band: {} action: {}".format(self.args.cisco_scheme,self.args.cisco_ctlr,self.args.cisco_user,
                self.args.cisco_passwd, self.args.cisco_ap, self.args.cisco_series, self.args.cisco_band,"summary"))

            ctl_output = subprocess.run(["../cisco_wifi_ctl.py", "--scheme", self.args.cisco_scheme, "--port", self.args.cisco_port, "-d", self.args.cisco_ctlr, "-u",
                                       self.args.cisco_user, "-p", self.args.cisco_passwd,
                                       "-a", self.args.cisco_ap,"--series", self.args.cisco_series,"--action", "summary"], capture_output=True)
            pss = ctl_output.stdout.decode('utf-8', 'ignore')
            print(pss)
        except subprocess.CalledProcessError as process_error:
            print("Controller unable to commicate to AP or unable to communicate to controller error code: {} output {}"
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
                pat = "%s\s+\S+\s+\S+\s+\S+\s+\S+.*  \S+\s+\S+\s+(\S+)\s+\["%(self.args.cisco_ap)
                #print("AP line: %s"%(line))
                m = re.search(pat, line)
                if (m != None):
                    sta_count = m.group(1)
                    print("AP line: %s"%(line))
                    print("sta-count: %s"%(sta_count))
                    if (int(sta_count) != int(self.total_stas)):
                        print("WARNING: Cisco Controller reported %s stations, should be %s"%(sta_count, self.total_stas))


    def verify_cac_on_ap(self):
        pass
        # Do this after you get the configuration Verify CAC
        # use pySerial to check if the AP is configured:
        # 1. You can grep for "DFS CAC timer enabled time 60" 
        # 2. and "changed to DFS channel 52, running CAC for 60 seconds
        # Wait for 60 sec and check for this log "CAC_EXPIRY_EVT: CAC finished on DFS channel 52"
        #"make a note of the time and check the CAC timer expired in 60-61 seconds."

        # After CAC expires Verify Traffic. (the loop should start up may want some special detection)

    def lf_hackrf_enable(self):
        # hard coded for now
        # need json and update to realm
        #if os.path.isfile(self.args.hackrf):
        #    print("hack rf file found {}".format(self.args.hackrf))
        #else:
        #    print("WARNING: hack rf file not found at {}".format(self.args.hackrf))

        # look for lf_hackrf.py in local directory the look for in 
        pass

    def verify_radar_detected_on_ap(self):
        pass
        #You will see logs as below in the AP:(show logging will help you getting this info)

        #[*07/07/2020 23:44:27.7630] wcp/dfs :: RadarDetection: radar detected
        #[*07/07/2020 23:44:27.7630] wcp/dfs :: RadarDetection: sending packet out to capwapd, slotId=1, msgLen=386, chanCnt=1 -100
        #[*07/07/2020 23:44:27.7900] DOT11_DRV[1]: DFS CAC timer disabled time 0
        #[*07/07/2020 23:44:27.7960] Enabling Channel and channel width Switch Announcement on current channel 
        #[*07/07/2020 23:44:27.8060] DOT11_DRV[1]: set_dfs Channel set to 36/20, CSA count 10
        #[*07/07/2020 23:44:27.8620] DOT11_DRV[1]: DFS CAC timer enabled time 60

    def verify_black_list_time_ap(self):
        pass

    def lf_hackrf_disable(self):
        pass
        #need to save the process id

    # dfs dynamic frequency selection
    def dfs(self):
        if self.args == None:
            return
        if self.args.cisco_ctlr == None:
            return
        if self.args.cisco_dfs == False:
            return
        if self.args.cisco_channel == None:
            return
        if self.args.cisco_chan_width == None:
            return
        print("testing dfs")
        self.controller_show_ap_channel()
        self.controller_disable_ap()
        self.controller_set_channel_ap()
        self.controller_set_chan_width_ap()
        self.controller_enable_ap()
        self.verify_cac_on_ap()                 
        self.lf_hackrf_enable()
        self.verify_radar_detected_on_ap()
        self.verify_black_list_time_ap()
        self.lf_hackrf_disable()

        # For Testing  only - since hackrf not causing channel changes
        self.controller_disable_ap()
        self.controller_set_channel_ap_36()
        #self.dfs_set_chan_width_ap()
        self.controller_enable_ap()
        #check the AP for 52 is configured or not ,  check the CAC timer 
        # verify the clien can connect back to the AP once the CAC expires (check all connections)

    def controller_channel_chan_width_config(self):
        if self.args == None:
            return
        if self.args.cisco_ctlr == None:
            return
        if self.args.cisco_channel == None:
            return
        self.controller_disable_ap()
        self.controller_set_channel_ap()
        self.controller_set_chan_width_ap()
        self.controller_enable_ap()
        self.controller_show_ap_channel()
        # need to actually check the CAC timer
        time.sleep(60)

    def reset_port_check(self):
        for station_profile in self.station_profiles:
            if station_profile.reset_port_extra_data['reset_port_enable']:
                if station_profile.reset_port_extra_data['reset_port_timer_started'] == False:
                    print("reset_port_time_min: {}".format(station_profile.reset_port_extra_data['reset_port_time_min']))
                    print("reset_port_time_max: {}".format(station_profile.reset_port_extra_data['reset_port_time_max']))
                    station_profile.reset_port_extra_data['seconds_till_reset'] = \
                    random.randint(station_profile.reset_port_extra_data['reset_port_time_min'],\
                                   station_profile.reset_port_extra_data['reset_port_time_max'])
                    station_profile.reset_port_extra_data['reset_port_timer_started'] = True
                    print("on radio {} seconds_till_reset {}".format(station_profile.add_sta_data['radio'],station_profile.reset_port_extra_data['seconds_till_reset']))
                else:
                    station_profile.reset_port_extra_data['seconds_till_reset'] = station_profile.reset_port_extra_data['seconds_till_reset'] - 1
                    if self.debug: print("radio: {} countdown seconds_till_reset {}".format(station_profile.add_sta_data['radio']  ,station_profile.reset_port_extra_data['seconds_till_reset']))
                    if ((station_profile.reset_port_extra_data['seconds_till_reset']  <= 0)):
                        station_profile.reset_port_extra_data['reset_port_timer_started'] = False
                        port_to_reset = random.randint(0,len(station_profile.station_names)-1)
                        print("reset on radio {} station: {}".format(station_profile.add_sta_data['radio'],station_profile.station_names[port_to_reset]))
                        self.local_realm.reset_port(station_profile.station_names[port_to_reset])

    def pre_cleanup(self):
        self.cx_profile.cleanup_prefix()
        self.multicast_profile.cleanup_prefix()
        self.total_stas = 0
        for station_list in self.station_lists:
            for sta in station_list:
                self.local_realm.rm_port(sta, check_exists=True)
                self.total_stas += 1

        # Make sure they are gone
        count = 0
        while (count < 10):
            more = False
            for station_list in self.station_lists:
                for sta in station_list:
                    rv = self.local_realm.rm_port(sta, check_exists=True)
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
            print("Creating stations")

            station_profile.create(radio=self.radio_name_list[index], sta_names_=self.station_lists[index], debug=self.debug, sleep_time=0)
            index += 1

            for etype in self.endp_types:
                if etype == "mc_udp" or etype == "mc_udp6":
                    print("Creating Multicast connections for endpoint type: %s"%(etype))
                    self.multicast_profile.create_mc_tx(etype, self.side_b, etype)
                    self.multicast_profile.create_mc_rx(etype, side_rx=station_profile.station_names)
                else:
                    for _tos in self.tos:
                        print("Creating connections for endpoint type: %s TOS: %s"%(etype, _tos))
                        self.cx_profile.create(endp_type=etype, side_a=station_profile.station_names, side_b=self.side_b, sleep_time=0, tos=_tos)
        self._pass("PASS: Stations build finished")        
        
    def start(self, print_pass=False, print_fail=False):
        print("Bringing up stations")
        self.local_realm.admin_up(self.side_b) 
        for station_profile in self.station_profiles:
            for sta in station_profile.station_names:
                print("Bringing up station %s"%(sta))
                self.local_realm.admin_up(sta)

        temp_stations_list = []
        temp_stations_list.append(self.side_b)
        for station_profile in self.station_profiles:
            temp_stations_list.extend(station_profile.station_names.copy())

        if self.local_realm.wait_for_ip(temp_stations_list, timeout_sec=120, debug=self.debug):
            print("ip's acquired")
        else:
            print("print failed to get IP's")
            exit(1) #why continue
        time.sleep(30)
        self.verify_controller()
        print("Starting multicast traffic (if any configured)")
        self.multicast_profile.start_mc(debug_=self.debug)
        self.multicast_profile.refresh_mc(debug_=self.debug)
        print("Starting layer-3 traffic (if any configured)")
        self.cx_profile.start_cx()
        self.cx_profile.refresh_cx()

        cur_time = datetime.datetime.now()
        print("Getting initial values.")
        old_rx_values, rx_drop_percent = self.__get_rx_values()

        end_time = self.local_realm.parse_time(self.test_duration) + cur_time

        print("Monitoring throughput for duration: %s"%(self.test_duration))

        passes = 0
        expected_passes = 0
        while cur_time < end_time:
            #interval_time = cur_time + datetime.timedelta(seconds=5)
            interval_time = cur_time + datetime.timedelta(seconds=self.polling_interval_seconds)
            #print("polling_interval_seconds {}".format(self.polling_interval_seconds))
            while cur_time < interval_time:
                cur_time = datetime.datetime.now()
                self.reset_port_check()
                time.sleep(1)
            
            self.epoch_time = int(time.time())
            new_rx_values, rx_drop_percent = self.__get_rx_values()

            expected_passes += 1
            if self.__compare_vals(old_rx_values, new_rx_values):
                passes += 1
            else:
                self._fail("FAIL: Not all stations increased traffic", print_fail)
            old_rx_values = new_rx_values

            self.__record_rx_dropped_percent(rx_drop_percent)

            cur_time = datetime.datetime.now()

        if passes == expected_passes:
            self._pass("PASS: All tests passed", print_pass)

    def stop(self):
        self.cx_profile.stop_cx()
        self.multicast_profile.stop_mc()
        for station_list in self.station_lists:
            for station_name in station_list:
                self.local_realm.admin_down(station_name)

    def cleanup(self):
        self.cx_profile.cleanup()
        self.multicast_profile.cleanup()
        for station_profile in self.station_profiles:
            station_profile.cleanup()
                                        
    def csv_generate_column_headers(self):
        csv_rx_headers = ['Time epoch','Time','Monitor']
        for i in range(1,6):
            csv_rx_headers.append("least_rx_data {}".format(i))
        for i in range(1,6):
            csv_rx_headers.append("most_rx_data_{}".format(i))
        csv_rx_headers.append("average_rx_data")
        return csv_rx_headers

    def csv_add_column_headers(self,headers):
        if self.csv_file is not None:
            self.csv_writer.writerow(headers)
            self.csv_file.flush()

    def csv_validate_list(self, csv_list, length):
        if len(csv_list) < length:
            csv_list = csv_list + [('no data','no data')] * (length - len(csv_list))
        return csv_list

    def csv_add_row(self,row,writer,csv_file):
        if self.csv_file is not None:
            writer.writerow(row)
            csv_file.flush()

def valid_endp_types(_endp_type):
    etypes = _endp_type.split()
    for endp_type in etypes:
        valid_endp_type=['lf_udp','lf_udp6','lf_tcp','lf_tcp6','mc_udp','mc_udp6']
        if not (str(endp_type) in valid_endp_type):
            print('invalid endp_type: %s. Valid types lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6' % endp_type)
            exit(1)
    return _endp_type

def main():
    lfjson_host = "localhost"
    lfjson_port = 8080
    endp_types = "lf_udp"
    debug_on = False

    parser = argparse.ArgumentParser(
        prog='lf_cisco_snp.py',
        #formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        Useful Information:
            1. Polling interval for checking traffic is fixed at 1 minute
            2. The test will generate csv file 
            3. The tx/rx rates are fixed at 256000 bits per second
            4. Maximum stations per radio is 64
            ''',
        
        description='''\
lf_cisco_snp.py:
--------------------

Summary : 
----------
create stations, create traffic between upstream port and stations,  run traffic. 
The traffic on the stations will be checked once per minute to verify that traffic is transmitted
and recieved.

Generic command layout:
-----------------------
python .\\lf_cisco_snp.py --test_duration <duration> --endp_type <traffic types> --upstream_port <port> 
        --radio "radio==<radio> stations==<number staions> ssid==<ssid> ssid_pw==<ssid password> security==<security type: wpa2, open, wpa3> wifimode==AUTO" --debug

Multiple radios may be entered with individual --radio switches

generiic command with controller setting channel and channel width test duration 5 min
python3 lf_cisco_snp.py --cisco_ctlr <IP> --cisco_dfs True/False --mgr <Lanforge IP> 
    --cisco_channel <channel> --cisco_chan_width <20,40,80,120> --endp_type 'lf_udp lf_tcp mc_udp' --upstream_port <1.ethX> 
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
--cisco_channel <channel>',default=None  , no change
--cisco_chan_width <20 40 80 160>',default="20",choices=["20","40","80","160"]
--cisco_band <a | b | abgn>',default="a",choices=["a", "b", "abgn"]

--mgr <hostname for where LANforge GUI is running>',default='localhost'
-d  / --test_duration <how long to run>  example --time 5d (5 days) default: 3m options: number followed by d, h, m or s',default='3m'
--tos:  Support different ToS settings: BK | BE | VI | VO | numeric',default="BE"
--debug:  Enable debugging',default=False
-t  / --endp_type <types of traffic> example --endp_type \"lf_udp lf_tcp mc_udp\"  Default: lf_udp , options: lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6',
                        default='lf_udp', type=valid_endp_types
-u / --upstream_port <cross connect upstream_port> example: --upstream_port eth1',default='eth1')
-o / --outfile <Output file for csv data>", default='snp'

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
python3 .\\lf_cisco_snp.py --test_duration 4m --endp_type \"lf_tcp lf_udp mc_udp\" --tos \"BK VI\" --upstream_port eth1 
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
python3 lf_cisco_snp.py --cisco_ctlr 192.168.100.112 --cisco_dfs True --mgr 192.168.100.178 
    --cisco_channel 52 --cisco_chan_width 20 --endp_type 'lf_udp lf_tcp mc_udp' --upstream_port 1.eth3 
    --radio "radio==1.wiphy0 stations==3 ssid==test_candela ssid_pw==[BLANK] security==open" 
    --radio "radio==1.wiphy1 stations==16 ssid==test_candela ssid_pw==[BLANK] security==open"
    --test_duration 5m




TODO:
11a     5ghz
11b     24ghz
11g     24ghz
11bg    24ghz

11n     5ghz/24ghz

11ac    5ghz


TODO:
##############################################################################
Detailed test loop description 10/9/2020 - Karthik Recommendation
##############################################################################
Script logic loops:

AP {Axel, Vanc} Dynamic
      frequency {24ghz, 5ghz} Common (band)
            wifimode{11ax, 11ac, 11n, 11bg} Common  (an anAX anAC abgn bg)
                  Bandwidth {20, 40, 80, 160}
                        data-encryption {enable/disable} Common
                              AP-mode {local/flexconnect} Common
                                    client-density {1, 10, 20, 50, 100, 200} Dynamic
                                          Packet-type {TCP, UDP} Common
                                                Direction {Downstream, Upstream}
                                                      Packet-size { 88, 512, 1370, 1518}   Common
                                                            Time (4 iterations of 30 sec and get the best average TP out of it) 

Notes:



Radio descriptions:
ax200: so if AP is /n, then ax200 will connect at /n.  But if AP is /AX, we have no way to force ax200 to act like /n
ax200: is dual band, supporting at least /b/g/n/AX on 2.4Ghz, and /a/n/ac/AX on 5Ghz.  2.4Ghz doesn't officially support /AC, but often chips will do /AC there anyway

ath10K: if they want /AC or /n or /abg stations, then our ath10k radios can support that need (and ath9k if they have any, can do /n and /abg)
ath10K(998x)  - wave -1 , dual band card it can be ac, n , a/b/g modes, up to 3x3 spacial streams
ath10K(9884) - wave-2 supports 4x4  802.11an-AC  5ghz  (can act as ac , an)

Note: wave-2 radios can act as ac, an, (802.11an-AC) or legacy a/b/g (802.11bgn-AC)


wifimode:
11ax, 11ac, 11n, 11bg

#############################################
5 Ghz
#############################################
Wifi mode: ax  - 5ghz
Radios   :  ax200  :        802.11 /a/n/ac/AX

Wifi mode: 11ac - 5ghz
Radios   :  ath10K(9984)    802.11an-AC

Wifi mode: 11n - 5ghz
Radios   :  ath10K(9984)    802.11an-AC

#############################################
24 Ghz
#############################################

Wifi mode: 11ax - 24ghz
Radios   :  ax200 -         802.11 /b/g/n/AX     

Wifi mode: 11ac - 24ghz
Radios   :  ax200           802.11 /b/g/n/AX (2.4Ghz doesn't officially support /AC, but often chips will do /AC there anyway)

Wifi mode: 11n - 24ghz 
Radios   :  ax200           802.11 /b/g/n/AX

Wifi mode: 11bg - 24ghz
Radios   :  ax200           802.11 /b/g/n/AX

Wifi mode: 11bg





TODO: Radio descriptions in realm , the 1. refers to the chassi hopefully corresponds to the shelf

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

        ''')

    # reorder to follow looping

    parser.add_argument('-ca','--cisco_all', help='--cisco_all flag present default to all tests',action="store_true")
    parser.add_argument('-ct','--cisco_test', help='--cisco_test flag present default to subset tests',action="store_true")
    parser.add_argument('-cca','--cisco_ap', help='--cisco_ap List of APs to test  default:  Axel',default="APA453.0E7B.CF9C")
    parser.add_argument('-ccf','--cisco_band', help='--cisco_band <a | b | abgn>',default="a b abgn")
    # cisco wanted 11ax , 11ac, 11n, 11gb
    parser.add_argument('-cwm','--cisco_wifimode', help='List of of wifi mode to test default: 11ax 11ac 11n 11gb',default="an anAX anAC abgn bg",
                        choices=[ "auto", "a", "b", "g", "abg", "abgn", "bgn", "bg", "abgnAC", "anAC", "an", "bgnAC", "abgnAX", "bgnAX", "anAX"])
    parser.add_argument('-ccc','--cisco_channel', help='--cisco_channel <channel> default 36',default="36")
    parser.add_argument('-ccw','--cisco_chan_width', help='--cisco_chan_width <20 40 80 160> default: \"20 40 80 160\"',default="20 40 80 160")
    parser.add_argument('-cam','--cisco_ap_mode', help='--cisco_ap_mode <local flexconnect>',default="local flexconnect")
    parser.add_argument('-cps','--cisco_packet_size', help='--cisco_packet_size List of packet sizes default \"88 512 1370 1518\"',default="88 512 1370 1518" )
    parser.add_argument('-ccd','--cisco_client_density', help='--cisco_client_density List of client densities defaults 1 10 20 50 100 200 ',
                            default="1 10 20 50 100 200" )
    parser.add_argument('-cde','--cisco_data_encryption', help='--cisco_data_encryption \"enable disable\"',default="disable" )

    parser.add_argument('-cs','--cisco_series', help='--cisco_series <9800 | 3504>',default="3504",choices=["9800","3504"])
    parser.add_argument('-cc','--cisco_ctlr', help='--cisco_ctlr <IP of Cisco Controller> default 192.168.100.178',default="192.168.100.178")
    parser.add_argument('-cp','--cisco_port', help='--cisco_port <port of Cisco Controller> ssh default 22',default="22")
    parser.add_argument('-cu','--cisco_user', help='--cisco_user <User-name for Cisco Controller>',default="admin")
    parser.add_argument('-cpw','--cisco_passwd', help='--cisco_passwd <Password for Cisco Controller>',default="Cisco123")
    parser.add_argument('-ccp','--cisco_prompt', help='--cisco_prompt <Prompt for Cisco Controller>',default="\(Cisco Controller\) >")
    parser.add_argument('-cd','--cisco_dfs', help='--cisco_dfs <True/False>',default=False)
    parser.add_argument('-ccs','--cisco_scheme', help='--cisco_scheme (serial|telnet|ssh): connect via serial, ssh or telnet',default="ssh",choices=["serial","telnet","ssh"])
    parser.add_argument('-cw','--cisco_wlan', help='--cisco_wlan <wlan name> default: NA, NA means no change',default="NA")
    parser.add_argument('-cwi','--cisco_wlanID', help='--cisco_wlanID <wlanID> default: NA , NA means not change',default="NA")
    parser.add_argument('-ctp','--cisco_tx_power', help='--cisco_tx_power <1 | 2 | 3 | 4 | 5 | 6 | 7 | 8>  1 is highest power default NA NA means no change',default="NA"
                        ,choices=["1","2","3","4","5","6","7","8","NA"])
    parser.add_argument('-cco','--cap_ctl_out',  help='--cap_ctl_out , switch the cisco controller output will be captured', action='store_true')
                            

    parser.add_argument('-apr','--amount_ports_to_reset', help='--amount_ports_to_reset \"<min amount ports> <max amount ports>\" ', default=None)
    parser.add_argument('-prs','--port_reset_seconds', help='--ports_reset_seconds \"<min seconds> <max seconds>\" ', default="10 30")

    parser.add_argument('-lm','--mgr', help='--mgr <hostname for where LANforge GUI is running>',default='localhost')
    parser.add_argument('-d','--test_duration', help='--test_duration <how long to run>  example --time 5d (5 days) default: 2m options: number followed by d, h, m or s',default='2m')
    parser.add_argument('--tos', help='--tos:  Support different ToS settings: BK | BE | VI | VO | numeric',default="BE")
    parser.add_argument('-db','--debug', help='--debug:  Enable debugging',action='store_true')
    parser.add_argument('-t', '--endp_type', help='--endp_type <types of traffic> example --endp_type \"lf_udp lf_tcp mc_udp\"  Default: lf_udp lf_tcp, options: lf_udp, lf_udp6, lf_tcp, lf_tcp6, mc_udp, mc_udp6',
                        default='lf_udp lf_tcp', type=valid_endp_types)
    parser.add_argument('-u', '--upstream_port', help='--upstream_port <cross connect upstream_port> example: --upstream_port eth1',default='eth1')
    parser.add_argument('-o','--csv_outfile', help="--csv_outfile <Output file for csv data>", default='snp')
    parser.add_argument('-pi','--polling_interval', help="--polling_interval <seconds>", default='30s')
    parser.add_argument('-c','--csv_output', help="Generate csv output", default=False) 

    #to do add wifimode
    parser.add_argument('-r','--radio', action='append', nargs=1, help='--radio  \
                        \"radio==<number_of_wiphy stations=<=number of stations> ssid==<ssid> ssid_pw==<ssid password> security==<security> wifimode==<wifimode>\" '\
                        , required=False)
    parser.add_argument('-amr','--side_a_min_rate',  help='--side_a_min_rate, station transfer rate default 256000', default=256000)
    parser.add_argument('-bmr','--side_b_min_rate',  help='--side_b_min_rate , upstream min tx rate default 256000', default=256000)

    args = parser.parse_args()

    cisco_args = args

    #print("args: {}".format(args))
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


    # static dictionaries for radios on 191.168.100.178

    # radios on 192.168.100.178 
    #--ssid test_candela --ssidpw [BLANK] --security open 
    #iwlwifi(AX200) 521
    radio_AX200_abgn_ax_dict = [['radio==1.wiphy3 stations==1 ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto'],
    ['radio==1.wiphy4 stations==1 ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto'],
    ['radio==1.wiphy5 stations==1 ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto'],
    ['radio==1.wiphy6 stations==1 ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto']]
    #radio_AX200_abgn_ax_dict = [['radio==1.wiphy1 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]
    #ath10k(9984) 523
    radio_ath10K_9984_an_AC_dict  = [['radio==1.wiphy0 stations==1 ssid==test_candela ssid_pw==[BLANK] security==open wifimode==auto']]
    #radio_ath10K_9984_an_AC_dict  = [['radio==6.wiphy8 stations==1 ssid==test-can ssid_pw==[BLANK] security==open wifimode==auto']]

    radios1 = [['radio==1.wiphy1 stations==1 ssid==jedway-wpa2-x2048-4-1 ssid_pw==jedway-wpa2-x2048-4-1 security==wpa2 wifimode==abgn'], 
    ['radio==1.wiphy2 stations==1 ssid==jedway-wpa2-x2048-5-1 ssid_pw==jedway-wpa2-x2048-5-1 security==wpa2 wifimode==an']]

    if args.csv_outfile != None:
        current_time = time.strftime("%m_%d_%Y_%H_%M_%S", time.localtime())
        csv_outfile = "{}_{}.csv".format(args.csv_outfile,current_time)
        print("csv output file : {}".format(csv_outfile))
        

    MAX_NUMBER_OF_STATIONS = 64
    
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

    if args.cisco_all:
        cisco_aps              = "APA453.0E7B.CF9C".split()
        cisco_bands            = "a b".split()
        cisco_wifimodes        = "an anAX anAC abgn bg".split()
        cisco_tx_power         = "3"
        cisco_chan_5ghz        = "36".split()
        cisco_chan_24ghz       = "1".split()
        cisco_chan_widths      = "20".split()
        cisco_ap_modes         = "local flex".split()
        cisco_data_encryptions = "disable".split()
        endp_types             = "lf_udp lf_tcp"
        cisco_packet_sizes     = "1518".split()
        cisco_client_densities = "1".split()
        cisco_data_encryptions = "disable".split()
    elif args.cisco_test:
        cisco_aps              = "APA453.0E7B.CF9C".split()
        cisco_bands            = "a b".split()
        cisco_wifimodes        = "an anAX anAC abgn bg".split()
        cisco_tx_power         = "3"
        cisco_chan_5ghz        = "36".split()
        cisco_chan_24ghz       = "1".split()
        cisco_chan_widths      = "20".split()
        cisco_ap_modes         = "local flex".split()
        cisco_data_encryptions = "disable".split()
        endp_types             = "lf_udp lf_tcp"
        cisco_packet_sizes     = "1518".split()
        cisco_client_densities = "1 ".split()
        cisco_data_encryptions = "disable".split()
    else:    
        cisco_aps             = args.cisco_ap.split()
        cisco_bands           = args.cisco_band.split()
        cisco_wifimodes       = args.cisco_wifimode.split()
        for mode in cisco_wifimodes:
            if mode in wifi_mode_dict.keys():
                pass
            else:
                print("wifimode [{}] not recognised. Please use: auto, a, b, g, abg, abgn, bgn, bg, abgnAC, anAC, an, bgnAC, abgnAX, bgnAX, anAX".format(mode))
                exit(1)
        cisco_tx_power           = "3"
        cisco_chan_5ghz          = "36".split()
        cisco_chan_24ghz         = "1".split()
        cisco_chan_widths        = args.cisco_chan_width.split()
        cisco_ap_modes           = args.cisco_ap_mode.split()
        cisco_client_densities   = args.cisco_client_density.split()
        endp_types               = "lf_udp lf_tcp".split()
        cisco_packet_types       = args.endp_type.split()
        cisco_packet_sizes       = args.cisco_packet_size.split()
        cisco_client_densities   = args.cisco_client_density.split()
        cisco_data_encryptions   = args.cisco_data_encryption.split()
    
    print(cisco_aps)
    print(cisco_bands)
    print(cisco_wifimodes)
    print(cisco_chan_widths)
    print(cisco_chan_widths)
    print(cisco_ap_modes)
    print(cisco_client_densities)
    print(endp_types)
    print(cisco_packet_sizes)
    print(cisco_client_densities)
    print(cisco_data_encryptions)

    for cisco_ap in cisco_aps:
        for cisco_band in cisco_bands:  # frequency
            for cisco_wifimode in cisco_wifimodes:
                for cisco_chan_width in cisco_chan_widths: #bandwidth
                    for cisco_data_encryption in cisco_data_encryptions:
                        for cisco_ap_mode in cisco_ap_modes:
                            for cisco_client_density in cisco_client_densities:
                                for endp_type in endp_types:
                                    for cisco_packet_size in cisco_packet_sizes:
                                        print("Cisco run: AP {} band: {}  wifimode {} tx_power {} chan_5ghz {} chan_24ghz {} chan_width {} cisco_ap_mode {}  cisco_packet_size {}".format(cisco_ap, 
                                        cisco_band, cisco_wifimode, cisco_tx_power, cisco_chan_5ghz, cisco_chan_24ghz,  cisco_chan_width, cisco_ap_mode, cisco_packet_size))
                                        # over write the configurations of args for controller
                                        cisco_args.cisco_ap            = cisco_ap
                                        cisco_args.cisco_band          = cisco_band
                                        if cisco_band == "a":
                                            cisco_args.cisco_chan      = cisco_chan_5ghz
                                        else:
                                            cisco_args.cisco_chan      = cisco_chan_24ghz    
                                        cisco_args.cisco_chan_width    = cisco_chan_width
                                        cisco_args.cisco_ap_mode       = cisco_ap_mode
                                        cisco_args.cisco_tx_power      = cisco_tx_power 
                                        print(cisco_args)

                                        cisco = cisco_(cisco_args)
                                        #Disable AP
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
                                        cisco.controller_set_channel()
                                        cisco.controller_set_bandwidth()

                                        if cisco_args.cisco_series == "9800":
                                            cisco.controller_create_wlan()
                                            cisco.controller_set_wireless_tag_policy()
                                            cisco.controller_enable_wlan()

                                        cisco.controller_enable_network_5ghz()
                                        cisco.controller_enable_network_24ghz()
                                        cisco.controller_enable_ap()

                                        # need to actually check the CAC timer
                                        time.sleep(30)

                                        # TODO may need a static list of radios read for scaling and performance
                                        print("cisco_wifi_mode {}".format(cisco_wifimode))
                                        if args.radio:
                                            radios = args.radio
                                        elif cisco_wifimode == "anAX" or cisco_wifimode == "abgn" or cisco_wifimode == "bg":
                                            radios = radio_AX200_abgn_ax_dict
                                        elif cisco_wifimode == "an" or cisco_wifimode == "anAC":
                                            radios = radio_ath10K_9984_an_AC_dict

                                        print("radios {}".format(radios))
                                        for radio_ in radios:
                                            radio_keys = ['radio','stations','ssid','ssid_pw','security','wifimode']
                                            radio_info_dict = dict(map(lambda x: x.split('=='), str(radio_).replace('[','').replace(']','').replace("'","").split()))
                                            print("radio_dict {}".format(radio_info_dict))

                                            for key in radio_keys:
                                                if key not in radio_info_dict:
                                                    print("missing config, for the {}, all of the following need to be present {} ".format(key,radio_keys))
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

                                            #####################
                                            # temp removal of loop
                                            ######################
                                            optional_radio_reset_keys = ['reset_port_enable']
                                            radio_reset_found = True
                                            for key in optional_radio_reset_keys:
                                                if key not in radio_info_dict:
                                                    #print("port reset test not enabled")
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
                                        index = 0
                                        station_lists = []
                                        for (radio_name_, number_of_stations_per_radio_) in zip(radio_name_list,number_of_stations_per_radio_list):
                                            number_of_stations = int(number_of_stations_per_radio_)
                                            if number_of_stations > MAX_NUMBER_OF_STATIONS:
                                                print("number of stations per radio exceeded max of : {}".format(MAX_NUMBER_OF_STATIONS))
                                                quit(1)
                                            station_list = LFUtils.portNameSeries(prefix_="sta", start_id_= 1 + index*1000, end_id_= number_of_stations + index*1000,
                                                                                  padding_number_=10000, radio=radio_name_)
                                            station_lists.append(station_list)
                                            index += 1

                                        #print("endp-types: %s"%(endp_types))

                                        #enstanciate the 



                                        ip_var_test = L3VariableTime(
                                                                        lfjson_host,
                                                                        lfjson_port,
                                                                        args=args,
                                                                        number_template="00", 
                                                                        station_lists= station_lists,
                                                                        name_prefix="LT-",
                                                                        endp_types=endp_types,
                                                                        tos=args.tos,
                                                                        side_b=side_b,
                                                                        radio_name_list=radio_name_list,
                                                                        number_of_stations_per_radio_list=number_of_stations_per_radio_list,
                                                                        ssid_list=ssid_list,
                                                                        ssid_password_list=ssid_password_list,
                                                                        ssid_security_list=ssid_security_list, 
                                                                        wifimode_list=wifimode_list, 
                                                                        test_duration=test_duration,
                                                                        polling_interval= polling_interval,
                                                                        reset_port_enable_list=reset_port_enable_list,
                                                                        reset_port_time_min_list=reset_port_time_min_list,
                                                                        reset_port_time_max_list=reset_port_time_max_list,
                                                                        side_a_min_rate=args.side_a_min_rate, 
                                                                        side_b_min_rate=args.side_b_min_rate, 
                                                                        debug_on=debug_on, 
                                                                        outfile=csv_outfile)


                                        ip_var_test.pre_cleanup()
                                        ip_var_test.build()
                                        if not ip_var_test.passes():
                                            print("build step failed.")
                                            print(ip_var_test.get_fail_message())
                                            exit(1) 
                                        ip_var_test.start(False, False)
                                        ip_var_test.stop()
                                        if not ip_var_test.passes():
                                            print("stop test failed")
                                            print(ip_var_test.get_fail_message())
                                        # clean up 
                                        radio_name_list = []
                                        number_of_stations_per_radio_list = []
                                        ssid_list = []
                                        ssid_password_list = []
                                        ssid_security_list = []
                                        wifimode_list = []

                                        ip_var_test.cleanup()

                            if ip_var_test.passes():
                                print("Full test passed, all connections increased rx bytes")
                                
                            ################################
                            # end of commented out loop
                            ################################

if __name__ == "__main__":
    main()
