import sys
import os
import argparse
import time
import pexpect
import paramiko
from itertools import islice

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append('../py-json')
import LANforge
from LANforge import LFUtils
from LANforge import lfcli_base
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
import realm
from realm import Realm


class STATION(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port, ssid, paswd, security, radio,sta_list=None, mode=0, use_ht160=False):
        super().__init__(lfclient_host, lfclient_port)
        self.host = lfclient_host
        self.port = lfclient_port
        self.ssid = ssid
        self.paswd = paswd
        self.security = security
        self.radio = radio
        self.mode = mode
        self.sta_list = sta_list
        #self.json_post("cli-json/set_wifi_extra2", { "post_ifup_script-64": "dGhpcyAnJyBpcyBhIGJhZCBleGFtcGxlLnNoCg=="})

        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.station_profile = self.local_realm.new_station_profile()
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.paswd,
        self.station_profile.security = self.security
        self.station_profile.use_ht160 = use_ht160
        if self.station_profile.use_ht160:
            self.station_profile.mode = 9
        self.station_profile.mode = mode

    def precleanup(self, sta_list):
        self.station_profile.cleanup(sta_list)
        LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url,
                                           port_list=sta_list,
                                           debug=self.debug)
        time.sleep(1)

    def build(self):
        self.station_profile.use_security(self.security, self.ssid, self.paswd)
        self.station_profile.create(radio=self.radio, sta_names_=self.sta_list, debug=self.debug)
        for sta_name in self.sta_list:
            each_sta_name = sta_name.split(".")

            data = {
                "shelf": 1,
                "resource": 1,
                "port": each_sta_name[2],
                "req_flush": 1,
                "post_ifup_script":"'./portal-bot.pl --user [BLANK] --bot bp_net.pm --ap_url http://192.168.208.18:3001/wifidog/ --login_action portal/2 --logout_url portal/2 --pass [BLANK] --start_url http://www.msftconnecttest.com/redirect --login_form login/1'"}
            self.json_post("cli-json/set_wifi_extra2", data)

    def start(self, sta_list):
        self.station_profile.admin_up()

    def stop(self):
        # Bring stations down
        self.station_profile.admin_down()

    def build_post_lf_up(self):
        pass



def main():
    parser = argparse.ArgumentParser(description="Netgear AP DFS Test Script")
    parser.add_argument('-hst', '--host', type=str, help='host name')
    parser.add_argument('-s', '--ssid', type=str, help='ssid for client')
    parser.add_argument('-pwd', '--passwd', type=str, help='password to connect to ssid')
    parser.add_argument('-sec', '--security', type=str, help='security')
    parser.add_argument('-rad', '--radio', type=str, help='radio at which client will be connected')
    parser.add_argument('-num_port', '--num_port', type=str, help='number of client')
    parser.add_argument("--mode", type=str, help="Used to force mode of stations.(enter 6 for 2.4GHz and 10 for 5GHz)")

    args = parser.parse_args()

    if(args.num_port is not None):
        num_sta = int(args.num_port)
    else:
        num_sta = 2

    sta_id = 0
    station_list = LFUtils.port_name_series(prefix="sta",
                                            start_id=sta_id,
                                            end_id=num_sta - 1,
                                            padding_number=100,
                                            radio=args.radio)
    station = STATION(lfclient_host=args.host, lfclient_port=8080, ssid=args.ssid, paswd=args.passwd,
                  security=args.security, radio=args.radio, sta_list=station_list,mode=args.mode)


    station.precleanup(station_list)
    station.build()
    station.start(station)
    station.local_realm.wait_for_ip(station_list)
    # python Netgear_clickthru_CaptivePortal.py -hst 192.168.200.28 -s Captive -pwd [Blank] -sec open -rad wiphy1 --num_port 5 --mode 10





if __name__ == '__main__':
    main()