#!/usr/bin/env python3
import re
import time

from LANforge import LFRequest
from LANforge import LFUtils
from LANforge import set_port
from LANforge import add_sta

class Realm:

    def __init__(self, lfclient_url="http://localhost:8080"):
        self.lfclient_url = lfclient_url

    def cx_list(self):
        #Returns json response from webpage of all layer 3 cross connects
        lf_r = LFRequest.LFRequest(self.lfclient_url + "/cx")
        response = lf_r.getAsJson(True)
        return response

    def station_list(self):
    #Returns list of all stations with "sta" in their name
        sta_list = []
        lf_r = LFRequest.LFRequest(self.lfclient_url + "/port/list?fields=_links,alias,device,port+type")
        response = lf_r.getAsJson(True)
        for x in range(len(response['interfaces'])):
            for k,v in response['interfaces'][x].items():
                if "sta" in v['device']:
                    sta_list.append(response['interfaces'][x])

        return sta_list

    def vap_list(self):
        #Returns list of all VAPs with "vap" in their name
        sta_list = []
        lf_r = LFRequest.LFRequest(self.lfclient_url + "/port/list?fields=_links,alias,device,port+type")
        response = lf_r.getAsJson(True)

        for x in range(len(response['interfaces'])):
            for k,v in response['interfaces'][x].items():
                if "vap" in v['device']:
                    sta_list.append(response['interfaces'][x])

        return sta_list


    def find_ports_like(self, pattern=""):
        #Searches for ports that match a given pattern and returns a list of names
        device_name_list = []
        lf_r = LFRequest.LFRequest(self.lfclient_url + "/port/list?fields=_links,alias,device,port+type")
        response = lf_r.getAsJson(True)
        #print(response)
        for x in range(len(response['interfaces'])):
            for k,v in response['interfaces'][x].items():
                if v['device'] != "NA":
                    device_name_list.append(v['device'])

        matched_list = []

        prefix = ""
        for port_name in device_name_list:
            try:
                if pattern.index("+") > 0:
                    match = re.search(r"^([^+]+)[+]$", pattern)
                    if match.group(1):
                        #print("name:", port_name, " Group 1: ",match.group(1))
                        prefix = match.group(1)
                    if port_name.index(prefix) == 0:
                        matched_list.append(port_name)

                elif pattern.index("*") > 0:
                    match = re.search(r"^([^\*]+)[\*]$", pattern)
                    if match.group(1):
                        prefix = match.group(1)
                        #print("group 1: ",prefix)
                    if port_name.index(prefix) == 0:
                        matched_list.append(port_name)

                elif pattern.index("[") > 0:
                    match = re.search(r"^([^\[]+)\[(\d+)\.\.(\d+)\]$", pattern)
                    if match.group(0):
                        #print("[group1]: ", match.group(1))
                        prefix = match.group(1)
                        if port_name.index(prefix):
                            matched_list.append(port_name) # wrong but better
            except ValueError as e:
                print(e)
        return matched_list

    def newCxProfile(self):
        cxprof = CXProfile(self.lfclient_url)
        return cxprof

class CXProfile:
    def __init__(self, mgr_url):
        self.mgr_url = mgr_url
        self.post_data = []

    def add_ports(self, side, endp_type, ports=[]):
    #Adds post data for a cross-connect between eth1 and specified list of ports, appends to array
        side = side.upper()
        endp_side_a = {
        "alias":"",
        "shelf":1,
        "resource":1,
        "port":"",
        "type":endp_type,
        "min_rate":0,
        "max_rate":0,
        "min_pkt":-1,
        "max_pkt":0
        }

        endp_side_b = {
        "alias":"",
        "shelf":1,
        "resource":1,
        "port":"",
        "type":endp_type,
        "min_rate":0,
        "max_rate":0,
        "min_pkt":-1,
        "max_pkt":0
        }

        for port_name in ports:
            if side == "A":
                endp_side_a["alias"] = port_name+"CX-A"
                endp_side_a["port"] = port_name
                endp_side_b["alias"] = port_name+"CX-B"
                endp_side_b["port"] = "eth1"
            elif side == "B":
                endp_side_a["alias"] = port_name+"CX-A"
                endp_side_a["port"] = "eth1"
                endp_side_b["alias"] = port_name+"CX-B"
                endp_side_b["port"] = port_name

            lf_r = LFRequest.LFRequest(self.mgr_url + "/cli-json/add_endp")
            lf_r.addPostData(endp_side_a)
            json_response = lf_r.jsonPost(True)
            lf_r.addPostData(endp_side_b)
            json_response = lf_r.jsonPost(True)
            #LFUtils.debug_printer.pprint(json_response)
            time.sleep(.5)


            data = {
            "alias":port_name+"CX",
            "test_mgr":"default_tm",
            "tx_endp":port_name + "CX-A",
            "rx_endp":port_name + "CX-B"
            }

            self.post_data.append(data)

    def create(self, sleep_time=.5):
    #Creates cross-connect for each port specified in the addPorts function
       for data in self.post_data:
           lf_r = LFRequest.LFRequest(self.mgr_url + "/cli-json/add_cx")
           lf_r.addPostData(data)
           json_response = lf_r.jsonPost(True)
           #LFUtils.debug_printer.pprint(json_response)
           time.sleep(sleep_time)


# use the station profile to set the combination of features you want on your stations
# once this combination is configured, build the stations with the build(resource, radio, number) call
# build() calls will fail if the station already exists. Please survey and clean your resource
# before calling build()
#       survey = Realm.findStations(resource=1)
#       Realm.removeStations(survey)
#       profile = Realm.newStationProfile()
#       profile.set...
#       profile.build(resource, radio, 64)
#
class StationProfile:
    def __init__(self, lfclient_url, ssid="NA", ssid_pass="NA", security="open", start_id="", mode=0, up=True, dhcp=True):
        self.lfclient_url = lfclient_url
        self.ssid = ssid
        self.ssid_pass = ssid_pass
        self.mode = mode
        self.up = up
        self.dhcp = dhcp
        self.security = security
        self.COMMANDS = ["add_sta", "set_port"]
        self.desired_add_sta_flags = ["wpa2_enable", "80211u_enable", "create_admin_down"]
        self.add_sta_data = {
            "shelf": 1,
            "resource": 1,
            "radio": None,
            "sta_name": None,
            "ssid": None,
            "key": None,
            "mode": 0,
            "mac": "xx:xx:xx:xx:*:xx",
            "flags": 0, # (0x400 + 0x20000 + 0x1000000000)  # create admin down
        }
        self.desired_set_port_flags = ["down", "dhcp"]
        self.set_port_data = {
            "shelf": 1,
            "resource": 1,
            "port": None,
            "current_flags": 0,
            "interest": 0, #(0x2 + 0x4000 + 0x800000)  # current, dhcp, down,
        }

    def setParam(self, cli_name, param_name, param_val):
        # we have to check what the param name is
        if (cli_name is None) or (cli_name == ""):
            return
        if (param_name is None) or (param_name == ""):
            return
        if cli_name not in self.COMMANDS:
            print(f"Command name name [{cli_name}] not defined in {self.COMMANDS}")
            return
        if cli_name == "add_sta":
            if (param_name not in add_sta.add_sta_flags) or (param_name not in add_sta.add_sta_modes):
                print(f"Parameter name [{param_name}] not defined in add_sta.py")
                return
        elif cli_name == "set_port":
            if (param_name not in set_port.set_port_current_flags) or (param_name not in set_port.set_port_cmd_flags):
                print(f"Parameter name [{param_name}] not defined in set_port.py")
                return

    # Checks for errors in initialization values and creates specified number of stations using init parameters
    def build(self, resource, resource_radio, num_stations):
        # try:
        #     resource = resource_radio[0: resource_radio.index(".")]
        #     name = resource_radio[resource_radio.index(".") + 1:]
        #     if name.index(".") >= 0:
        #         radio_name = name[name.index(".")+1 : ]
        #     print(f"Building {num_stations} on radio {resource}.{radio_name}")
        # except ValueError as e:
        #     print(e)

        # create stations down, do set_port on them, then set stations up
        self.add_sta_data["flags"] = ( 0
                + (0, add_sta.add_sta_flags["wpa_enable"])[self.desired_add_sta_flags["wpa_enable"]]
                + (0, add_sta.add_sta_flags["wep_enable"])[self.desired_add_sta_flags["wpa_enable"]]
                + (0, add_sta.add_sta_flags["wpa2_enable "])[self.desired_add_sta_flags["wpa_enable"]]
                + (0, add_sta.add_sta_flags["ht40_disable"])[self.desired_add_sta_flags["wpa_enable"]]

        )
        lf_r = LFRequest.LFRequest(self.lfclient_url + "/cli-json/add_sta")
        for num in range(num_stations):
            # data = {
            # "shelf":1,
            # "resource":resource,
            # "radio":radio_name,
            # "sta_name":f"sta{num:05}",
            # "ssid":self.ssid,
            # "key":self.ssid_pass,
            # "mode":1,
            # "mac":"xx:xx:xx:xx:*:xx",
            # "flags": self.add
            # }
            lf_r.addPostData(data)
            json_response = lf_r.jsonPost(True)

