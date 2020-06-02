#!/usr/bin/env python3
import re
import time

from LANforge import LFRequest
from LANforge import LFUtils


class Realm:

    def __init__(self, mgr_url="http://localhost:8080"):
        self.mgrURL = mgr_url

    def cx_list(self):
        #Returns json response from webpage of all layer 3 cross connects
        lf_r = LFRequest.LFRequest(self.mgrURL + "/cx")
        response = lf_r.getAsJson(True)
        return response

    def station_list(self):
    #Returns list of all stations with "sta" in their name
        sta_list = []
        lf_r = LFRequest.LFRequest(self.mgrURL + "/port/list?fields=_links,alias,device,port+type")
        response = lf_r.getAsJson(True)
        for x in range(len(response['interfaces'])):
            for k,v in response['interfaces'][x].items():
                if "sta" in v['device']:
                    sta_list.append(response['interfaces'][x])

        return sta_list

    def vap_list(self):
        #Returns list of all VAPs with "vap" in their name
        sta_list = []
        lf_r = LFRequest.LFRequest(self.mgrURL + "/port/list?fields=_links,alias,device,port+type")
        response = lf_r.getAsJson(True)

        for x in range(len(response['interfaces'])):
            for k,v in response['interfaces'][x].items():
                if "vap" in v['device']:
                    sta_list.append(response['interfaces'][x])

        return sta_list


    def find_ports_like(self, pattern=""):
        #Searches for ports that match a given pattern and returns a list of names
        device_name_list = []
        # alias is possible but device is gauranteed
        lf_r = LFRequest.LFRequest(self.mgrURL + "/port/list?fields=_links,alias,device,port+type")
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
                        #print("name:", portname, " Group 1: ",match.group(1))
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
                        if (port_name.index(prefix)):
                            matched_list.append(port_name) # wrong but better
            except ValueError as e:
                print(e)
        return matched_list

class CXProfile:

    def __init__(self, mgr_url="http://localhost:8080"):
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


class StationProfile:

    def __init__(self, mgr_url="localhost:8080", ssid="NA", ssid_pass="NA", security="open", start_id="", mode=0, up=True, dhcp=True):
        self.mgrURL = mgr_url
        self.ssid = ssid
        self.ssid_pass = ssid_pass
        self.mode = mode
        self.up = up
        self.dhcp = dhcp
        self.security = security

    def build(self, resource_radio, num_stations):
    #Checks for errors in initialization values and creates specified number of stations using init parameters
        try:
            resource = port_name[0: resource_radio.index(".")]
            name = port_name[resource_radio.index(".") + 1:]
            if name.index(".") >= 0:
                name = name[name.index(".")+1 : ]
        except ValueError as e:
            print(e)

        lf_r = LFRequest.LFRequest(self.mgrURL + "/cli-json/add_sta")
        for num in range(num_stations):
            data = {
            "shelf":1,
            "resource":1,
            "radio":radio,
            "sta_name":f"sta{num:05}",
            "ssid":self.ssid,
            "key":self.ssid_pass,
            "mode":1,
            "mac":"xx:xx:xx:xx:*:xx",
            "flags":
            }
            lf_r.addPostData(data)
            json_response = lf_r.jsonPost(True)

