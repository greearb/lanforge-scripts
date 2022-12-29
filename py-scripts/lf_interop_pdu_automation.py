#!/usr/bin/env python3
"""
NAME: lf_interop_pdu_automation.py

PURPOSE: lf_interop_pdu_automation.py  is a stand-alone automation script which will automatically power on/off for
certain interval in loop to prevent the mobile phones over charging.

USE './python3 lf_interop_pdu_automation.py --host 192.168.200.50 --user username --password pass --current
starting_status_of_port --port all/1,2,3 --on_time integer(hours) --off_time integer(hours)
    Eg : ./python3 lf_interop_pdu_automation.py --host 192.168.200.50 --user admin --password Candela@123 --current on
    --port all --on_time 1 --off_time 1'

Note: Please ensure that PDU is powered on and has an ip assigned to it.

Copyright 2021 Candela Technologies Inc
License: Free to distribute and modify. LANforge systems must be licensed.
"""
import os
import time
import argparse
from typing import Sequence
from typing import Optional

try:
    import dlipower
except:
    print('Please wait we are installing DLI Power module for you!!!')
    os.system('pip install dlipower')
    import dlipower


class PDUAutomate:
    def __init__(self, hostname, user, password):
        self.off_time = None
        self.on_time = None
        self.port = None
        self.hostname = hostname
        self.user = user
        self.password = password
        self.power_switch = None

    def login(self):
        try:
            self.power_switch = dlipower.PowerSwitch(hostname=self.hostname, userid=self.user, password=self.password)
        except:
            print('[STATUS] PDU device is Off, please connect it and try after sometime!!!')
            exit(0)

    def start(self, port, current, on_time, off_time):
        self.on_time = int(on_time) * 60 * 60
        self.off_time = int(off_time) * 60 * 60
        while True:
            try:
                if current == "on":
                    self.login()
                    self.switch_on(port)
                    time.sleep(self.on_time)
                    self.login()
                    self.switch_off(port)
                    time.sleep(self.off_time)
                elif current == "off":
                    self.login()
                    self.switch_off(port)
                    time.sleep(self.off_time)
                    self.login()
                    self.switch_on(port)
                    time.sleep(self.on_time)
                else:
                    print("[ERROR] Wrong input")
            except KeyboardInterrupt:
                print("[STOP] Program stopped\n")
                exit(0)

    def switch_on(self, port):
        self.port = port
        if self.port != 'all':
            try:
                port = str(self.port).split(",")
                for i in port:
                    self.power_switch[int(i) - 1].state = "ON"
            except:
                self.power_switch[int(self.port) - 1].state = "ON"
        else:
            for outlet in self.power_switch:
                outlet.state = 'ON'

    def switch_off(self, port):
        self.port = port
        if self.port != 'all':
            try:
                port = str(self.port).split(",")
                for i in port:
                    self.power_switch[int(i) - 1].state = "OFF"
            except:
                self.power_switch[int(self.port) - 1].state = "OFF"
        else:
            for outlet in self.power_switch:
                outlet.state = 'OFF'

    def print_status(self):
        print("[STATUS] ", self.power_switch)


def main(argv: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='Please provide host name eg: 192.168.200.65')
    parser.add_argument('--username', help='Please provide username eg: admin')
    parser.add_argument('--password', help='Please provide password eg: 1234')
    parser.add_argument('--port', help='Port number which has to be switched eg: --port 1,2,3,4')
    parser.add_argument('--current', help='Current status after running the code eg: --current off/on')
    parser.add_argument('--on_time', help='Time in (integer)hrs for keeping power on eg: --on_time 2')
    parser.add_argument('--off_time', help='Time in (integer)hrs for keeping power off eg: --off_time 5')
    args = parser.parse_args(argv)
    dic = vars(args)

    obj = PDUAutomate(dic['host'], dic['username'], dic['password'])
    obj.start(dic['port'], dic['current'], dic['on_time'], dic['off_time'])


if __name__ == '__main__':
    main()
