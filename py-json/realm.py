#!/usr/bin/env python3
import re
import time
import pprint
from pprint import pprint
from LANforge import LFRequest
from LANforge import LFUtils
from LANforge import set_port
from LANforge import add_sta
from LANforge import add_dut
from LANforge import lfcli_base
from LANforge import add_vap
from LANforge.lfcli_base import LFCliBase
from generic_cx import GenericCx
from LANforge import add_monitor
from LANforge.add_monitor import *
import os
import datetime
import base64

def wpa_ent_list():
    return [
        "DEFAULT",
        "NONE",
        "WPA-PSK",
        "FT-PSK",
        "FT-EAP",
        "FT-SAE",
        "FT-EAP-SHA384",
        "WPA-EAP",
        "OSEN",
        "IEEE8021X",
        "WPA-PSK-SHA256",
        "WPA-EAP-SHA256",
        "WPA-PSK WPA-EAP",
        "WPA-PSK-SHA256 WPA-EAP-SHA256",
        "WPA-PSK WPA-EAP WPA-PSK-SHA256 WPA-EAP-SHA256"
        "SAE",
        "WPA-EAP-SUITE-B",
        "WPA-EAP-SUITE-B-192",
        "FILS-SHA256",
        "FILS-SHA384",
        "OWE"
    ]

class Realm(LFCliBase):
    def __init__(self,
                 lfclient_host="localhost",
                 lfclient_port=8080,
                 debug_=False,
                 halt_on_error_=False,
                 _exit_on_error=False,
                 _exit_on_fail=False,
                 _local_realm=None,
                 _proxy_str=None,
                 _capture_signal_list=[]):
        super().__init__(_lfjson_host=lfclient_host,
                         _lfjson_port=lfclient_port,
                         _debug=debug_,
                         _halt_on_error=halt_on_error_,
                         _exit_on_error=_exit_on_error,
                         _exit_on_fail=_exit_on_fail,
                         _proxy_str=_proxy_str,
                         _capture_signal_list=_capture_signal_list)
        # self.lfclient_url = "http://%s:%s" % (lfclient_host, lfclient_port)
        super().__init__(lfclient_host,
                         lfclient_port,
                 _debug=debug_,
                 _halt_on_error=halt_on_error_,
                 _exit_on_error=_exit_on_error,
                 _exit_on_fail=_exit_on_fail,
                 #_local_realm=self,
                 _proxy_str=_proxy_str,
                 _capture_signal_list=_capture_signal_list)

        self.debug = debug_
        # if debug_:
        #     print("Realm _proxy_str: %s" % _proxy_str)
        #     pprint(_proxy_str)
        self.check_connect()
        self.chan_to_freq = {}
        self.freq_to_chan = {}
        freq = 0
        chan = 1
        for freq in range( 2412, 2472, 5):
            self.freq_to_chan[freq] = chan
            self.chan_to_freq[chan] = freq
            chan += 1

        self.chan_to_freq[14] = 2484
        self.chan_to_freq[34] = 5170
        self.chan_to_freq[36] = 5180
        self.chan_to_freq[38] = 5190
        self.chan_to_freq[40] = 5200
        self.chan_to_freq[42] = 5210
        self.chan_to_freq[44] = 5220
        self.chan_to_freq[46] = 5230
        self.chan_to_freq[48] = 5240
        self.chan_to_freq[52] = 5260
        self.chan_to_freq[56] = 5280
        self.chan_to_freq[60] = 5300
        self.chan_to_freq[64] = 5320
        self.chan_to_freq[100] = 5500
        self.chan_to_freq[104] = 5520
        self.chan_to_freq[108] = 5540
        self.chan_to_freq[112] = 5560
        self.chan_to_freq[116] = 5580
        self.chan_to_freq[120] = 5600
        self.chan_to_freq[124] = 5620
        self.chan_to_freq[128] = 5640
        self.chan_to_freq[132] = 5660
        self.chan_to_freq[136] = 5680
        self.chan_to_freq[140] = 5700
        self.chan_to_freq[144] = 5720
        self.chan_to_freq[149] = 5745
        self.chan_to_freq[153] = 5765
        self.chan_to_freq[157] = 5785
        self.chan_to_freq[161] = 5805
        self.chan_to_freq[165] = 5825
        self.chan_to_freq[169] = 5845
        self.chan_to_freq[173] = 5865

        self.freq_to_chan[2484] = 14
        self.freq_to_chan[5170] = 34
        self.freq_to_chan[5180] = 36
        self.freq_to_chan[5190] = 38
        self.freq_to_chan[5200] = 40
        self.freq_to_chan[5210] = 42
        self.freq_to_chan[5220] = 44
        self.freq_to_chan[5230] = 46
        self.freq_to_chan[5240] = 48
        self.freq_to_chan[5260] = 52
        self.freq_to_chan[5280] = 56
        self.freq_to_chan[5300] = 60
        self.freq_to_chan[5320] = 64
        self.freq_to_chan[5500] = 100
        self.freq_to_chan[5520] = 104
        self.freq_to_chan[5540] = 108
        self.freq_to_chan[5560] = 112
        self.freq_to_chan[5580] = 116
        self.freq_to_chan[5600] = 120
        self.freq_to_chan[5620] = 124
        self.freq_to_chan[5640] = 128
        self.freq_to_chan[5660] = 132
        self.freq_to_chan[5680] = 136
        self.freq_to_chan[5700] = 140
        self.freq_to_chan[5720] = 144
        self.freq_to_chan[5745] = 149
        self.freq_to_chan[5765] = 153
        self.freq_to_chan[5785] = 157
        self.freq_to_chan[5805] = 161
        self.freq_to_chan[5825] = 165
        self.freq_to_chan[5845] = 169
        self.freq_to_chan[5865] = 173

        # 4.9Ghz police band
        self.chan_to_freq[183] = 4915
        self.chan_to_freq[184] = 4920
        self.chan_to_freq[185] = 4925
        self.chan_to_freq[187] = 4935
        self.chan_to_freq[188] = 4940
        self.chan_to_freq[189] = 4945
        self.chan_to_freq[192] = 4960
        self.chan_to_freq[194] = 4970
        self.chan_to_freq[196] = 4980

        self.freq_to_chan[4915] = 183
        self.freq_to_chan[4920] = 184
        self.freq_to_chan[4925] = 185
        self.freq_to_chan[4935] = 187
        self.freq_to_chan[4940] = 188
        self.freq_to_chan[4945] = 189
        self.freq_to_chan[4960] = 192
        self.freq_to_chan[4970] = 194
        self.freq_to_chan[4980] = 196

    def wait_until_ports_appear(self, sta_list=None, debug_=False):
        if (sta_list is None) or (len(sta_list) < 1):
            print("realm.wait_until_ports_appear: no stations provided")
            return
        LFUtils.wait_until_ports_appear(base_url=self.lfclient_url,
                                        port_list=sta_list,
                                        debug=debug_)

    def rm_port(self, port_eid, check_exists=True, debug_=False):
        debug_ |= self.debug
        req_url = "/cli-json/rm_vlan"
        eid = self.name_to_eid(port_eid)
        do_rm = True
        if check_exists:
            if not self.port_exists(port_eid):
                do_rm = False
        if do_rm:
            data = {
                "shelf": eid[0],
                "resource": eid[1],
                "port": eid[2]
            }
            rsp = self.json_post(req_url, data, debug_=debug_)
            return True
        return False

    def port_exists(self, port_eid):
        data = {}
        eid = self.name_to_eid(port_eid)
        data["shelf"] = eid[0]
        data["resource"] = eid[1]
        data["port"] = eid[2]
        current_stations = self.json_get("/port/%s/%s/%s?fields=alias" % (eid[0], eid[1], eid[2]))
        if not current_stations is None:
            return True
        return False

    def admin_up(self, port_eid):
        # print("186 admin_up port_eid: "+port_eid)
        eid = self.name_to_eid(port_eid)
        shelf = eid[0]
        resource = eid[1]
        port = eid[2]
        request = LFUtils.port_up_request(resource_id=resource, port_name=port)
        # print("192.admin_up request: resource: %s port_name %s"%(resource, port))
        # time.sleep(2)
        self.json_post("/cli-json/set_port", request)

    def admin_down(self, port_eid):
        eid = self.name_to_eid(port_eid)
        shelf = eid[0]
        resource = eid[1]
        port = eid[2]
        request = LFUtils.port_down_request(resource_id=resource, port_name=port)
        self.json_post("/cli-json/set_port", request)

    def reset_port(self, port_eid):
        eid = self.name_to_eid(port_eid)
        shelf = eid[0]
        resource = eid[1]
        port = eid[2]
        request = LFUtils.port_reset_request(resource_id=resource, port_name=port)
        self.json_post("cli-json/reset_port", request)

    def rm_cx(self, cx_name):
        req_url = "cli-json/rm_cx"
        data = {
            "test_mgr": "ALL",
            "cx_name": cx_name
            }
        self.json_post(req_url, data)

    def rm_endp(self, ename, debug_=False, suppress_related_commands_=True):
        req_url = "cli-json/rm_endp"
        data = {
            "endp_name": ename
            }
        self.json_post(req_url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands_)

    def set_endp_tos(self, ename, _tos, debug_=False, suppress_related_commands_=True):
        req_url = "cli-json/set_endp_tos"
        tos = _tos
        # Convert some human readable values to numeric needed by LANforge.
        if _tos == "BK":
            tos = "64"
        if _tos == "BE":
            tos = "96"
        if _tos == "VI":
            tos = "128"
        if _tos == "VO":
            tos = "192"
        data = {
            "name": ename,
            "tos": tos
            }
        self.json_post(req_url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands_)

    def stop_cx(self, cx_name):
        self.json_post("/cli-json/set_cx_state", {
            "test_mgr": "ALL",
            "cx_name": cx_name,
            "cx_state": "STOPPED"
            }, debug_=self.debug)

    def cleanup_cxe_prefix(self, prefix):
        cx_list = self.cx_list()
        if cx_list is not None:
            for cx_name in cx_list:
                if cx_name.startswith(prefix):
                    self.rm_cx(cx_name)

        endp_list = self.json_get("/endp/list")
        if endp_list is not None:
            if 'endpoint' in endp_list:
                endp_list = list(endp_list['endpoint'])
                for idx in range(len(endp_list)):
                    endp_name = list(endp_list[idx])[0]
                    if endp_name.startswith(prefix):
                        self.rm_endp(endp_name)
            else:
                if self.debug: 
                    print("cleanup_cxe_prefix no endpoints: endp_list{}".format(endp_list) )

    def channel_freq(self, channel_=0):
        return self.chan_to_freq[channel_]

    def freq_channel(self, freq_=0):
        return self.freq_to_chan[freq_]

    # checks for OK or BUSY when querying cli-json/cv+is_built
    def wait_while_building(self, debug_=False):
        response_json=[]
        data = {
            "cmd": "cv is_built"
        }
        last_response = "BUSY"
        dbg_param = ""
        if debug_:
            dbg_param = "?__debug=1"

        while (last_response != "YES"):
            response = self.json_post("/gui-json/cmd%s" % dbg_param, data, debug_=debug_, response_json_list_=response_json)
            #LFUtils.debug_printer.pprint(response_json)
            last_response = response_json[0]["LAST"]["response"]
            if (last_response != "YES"):
                last_response = None
                response_json = []
                time.sleep(1)
            else:
                return
        return

    # loads a database
    def load(self, name):
        if (name is None) or (name == ""):
            raise ValueError("Realm::load: wants a test scenario database name, please find one in the Status tab of the GUI")

        data = {
            "name": name,
            "action":"overwrite",
            "clean_dut":"yes",
            "clean_chambers": "yes"
        }
        self.json_post("/cli-json/load", _data=data, debug_=self.debug)
        time.sleep(1)

    # Returns json response from webpage of all layer 3 cross connects
    def cx_list(self):
        response = self.json_get("/cx/list")
        return response

    def waitUntilEndpsAppear(self, these_endp, debug=False):
        return self.wait_until_endps_appear(these_endp, debug=debug)

    def wait_until_endps_appear(self, these_endp, debug=False):
        wait_more = True
        count = 0
        while wait_more:
            time.sleep(1)
            wait_more = False
            endp_list = self.json_get("/endp/list")
            found_endps = {}
            if (endp_list is not None) and ("items" not in endp_list):
                endp_list = list(endp_list['endpoint'])
                for idx in range(len(endp_list)):
                    name = list(endp_list[idx])[0]
                    found_endps[name] = name

            for req in these_endp:
                if not req in found_endps:
                    if debug:
                        print("Waiting on endpoint: %s"%(req))
                    wait_more = True
            count += 1
            if (count > 100):
                break

        return not wait_more

    def waitUntilCxsAppear(self, these_cx, debug=False):
        return self.wait_until_cxs_appear(these_cx, debug=debug)

    def wait_until_cxs_appear(self, these_cx, debug=False):
        wait_more = True
        count = 0
        while wait_more:
            time.sleep(1)
            wait_more = False
            found_cxs = {}
            cx_list = self.cx_list()
            not_cx = ['warnings', 'errors', 'handler', 'uri', 'items']
            if cx_list is not None:
                for cx_name in cx_list:
                    if cx_name in not_cx:
                        continue
                    found_cxs[cx_name] = cx_name

            for req in these_cx:
                if not req in found_cxs:
                    if debug:
                        print("Waiting on CX: %s"%(req))
                    wait_more = True
            count += 1
            if (count > 100):
                break

        return not wait_more

    # Returns map of all stations with port+type == WIFI-STATION
    def station_map(self):
        response = super().json_get("/port/list?fields=port,_links,alias,device,port+type")
        if (response is None) or ("interfaces" not in response):
            pprint(response)
            print("station_list: incomplete response, halting")
            exit(1)
        sta_map = {}
        temp_map = LFUtils.portListToAliasMap(response)
        for k, v in temp_map.items():
            if (v['port type'] == "WIFI-STA"):
                sta_map[k] = v
        temp_map.clear()
        del temp_map
        del response
        return sta_map

    # Returns list of all stations with port+type == WIFI-STATION
    def station_list(self):
        sta_list = []
        response = super().json_get("/port/list?fields=_links,alias,device,port+type")
        if (response is None) or ("interfaces" not in response):
            print("station_list: incomplete response:")
            pprint(response)
            exit(1)

        for x in range(len(response['interfaces'])):
            for k, v in response['interfaces'][x].items():
                if v['port type'] == "WIFI-STA":
                    sta_list.append(response['interfaces'][x])
        del response
        return sta_list

    # Returns list of all VAPs with "vap" in their name
    def vap_list(self):
        sta_list = []
        response = super().json_get("/port/list?fields=_links,alias,device,port+type")
        for x in range(len(response['interfaces'])):
            for k, v in response['interfaces'][x].items():
                if "vap" in v['device']:
                    sta_list.append(response['interfaces'][x])

        return sta_list

    # removes port by eid/eidpn
    def remove_vlan_by_eid(self, eid):
        if (eid is None) or ("" == eid):
            raise ValueError("removeVlanByEid wants eid like 1.1.sta0 but given[%s]" % eid)
        hunks = eid.split('.')
        # print("- - - - - - - - - - - - - - - - -")
        # pprint(hunks)
        # pprint(self.lfclient_url)
        # print("- - - - - - - - - - - - - - - - -")
        if (len(hunks) > 3) or (len(hunks) < 2):
            raise ValueError("removeVlanByEid wants eid like 1.1.sta0 but given[%s]" % eid)
        elif len(hunks) == 3:
            LFUtils.removePort(hunks[1], hunks[2], self.lfclient_url)
        else:
            LFUtils.removePort(hunks[0], hunks[1], self.lfclient_url)

    # Searches for ports that match a given pattern and returns a list of names
    def find_ports_like(self, pattern="", _fields="_links,alias,device,port+type", resource=0, debug_=False):
        if resource == 0:
            url = "/port/1/list?fields=%s" % _fields
        else:
            url = "/port/1/%s/list?fields=%s" % (resource, _fields)
        response = self.json_get(url)
        if debug_:
            print("# find_ports_like r:%s, u:%s #" % (resource, url))
            pprint(response)
        alias_map = LFUtils.portListToAliasMap(response, debug_=debug_)
        if debug_:
            pprint(alias_map)
        prelim_map = {}
        matched_map = {}
        for name, record in alias_map.items():
            try:
                if debug_:
                    print("- prelim - - - - - - - - - - - - - - - - - - -")
                    pprint(record)
                if (record["port type"] == "WIFI-STA"):
                    prelim_map[name] = record

            except Exception as x:
                self.error(x)

        prefix = ""
        try:
            if pattern.find("+") > 0:
                match = re.search(r"^([^+]+)[+]$", pattern)
                if match.group(1):
                    prefix = match.group(1)
                for port_eid, record in prelim_map.items():
                    if debug_:
                        print("name:", port_eid, " Group 1: ", match.group(1))
                    if port_eid.find(prefix) >= 0:
                        matched_map[port_eid] = record

            elif pattern.find("*") > 0:
                match = re.search(r"^([^\*]+)[*]$", pattern)
                if match.group(1):
                    prefix = match.group(1)
                    if debug_:
                        print("group 1: ", prefix)
                for port_eid, record in prelim_map.items():
                    if port_eid.find(prefix) >= 0:
                        matched_map[port_eid] = record

            elif pattern.find("[") > 0:
                # TODO: regex below might have too many hack escapes
                match = re.search(r"^([^\[]+)\[(\d+)\.\.(\d+)\]$", pattern)
                if match.group(0):
                    if debug_:
                        print("[group1]: ", match.group(1))
                        print("[group2]: ", match.group(2))
                        print("[group3]: ", match.group(3))
                    prefix = match.group(1)
                    for port_eid, record in prelim_map.items():
                        if port_eid.find(prefix) >= 0:
                            port_suf = record["device"][len(prefix):]
                            if (port_suf >= match.group(2)) and (port_suf <= match.group(3)):
                                # print("%s: suffix[%s] between %s:%s" % (port_name, port_name, match.group(2), match.group(3))
                                matched_map[port_eid] = record
        except ValueError as e:
            self.error(e)

        return matched_map

    def name_to_eid(self, eid):
        return LFUtils.name_to_eid(eid)

    def wait_for_ip(self, station_list=None, ipv4=True, ipv6=False, timeout_sec=60, debug=False):
        print("Waiting for ips, timeout: %i..."%(timeout_sec))
        #print(station_list)
        waiting_states = ["0.0.0.0", "NA", ""]

        if (station_list is None) or (len(station_list) < 1):
            raise ValueError("wait_for_ip: expects non-empty list of ports")

        wait_more = True
        while wait_more and timeout_sec != 0:
            wait_more = False

            for sta_eid in station_list:
                if debug:
                    print("checking sta-eid: %s"%(sta_eid))
                eid = self.name_to_eid(sta_eid)

                response = super().json_get("/port/%s/%s/%s?fields=alias,ip,port+type,ipv6+address" %
                                            (eid[0], eid[1], eid[2]))
                #pprint(response)

                if (response is None) or ("interface" not in response):
                    print("station_list: incomplete response:")
                    pprint(response)
                    wait_more = True
                    break

                if ipv4:
                    v = response['interface']
                    if (v['ip'] in waiting_states):
                        wait_more = True
                        if debug:
                            print("Waiting for port %s to get IPv4 Address."%(sta_eid))
                    else:
                        if debug:
                            print("Found IP: %s on port: %s"%(v['ip'], sta_eid))

                if ipv6:
                    v = response['interface']
                    #print(v)
                    if v['ipv6 address'] != 'DELETED' and not v['ipv6 address'].startswith('fe80') \
                           and v['ipv6 address'] != 'AUTO':
                        if debug:
                            print("Found IPv6: %s on port: %s" % (v['ipv6 address'], sta_eid))
                    else:
                        wait_more = True
                        if debug:
                            print("Waiting for port %s to get IPv6 Address."%(sta_eid))

            if wait_more:
                time.sleep(1)
                timeout_sec -= 1

        return not wait_more

    def get_curr_num_ips(self,num_sta_with_ips=0,station_list=None, ipv4=True, ipv6=False, debug=False):
        if debug:
            print("checking number of stations with ips...")
        waiting_states = ["0.0.0.0", "NA", ""]
        if (station_list is None) or (len(station_list) < 1):
            raise ValueError("check for num curr ips expects non-empty list of ports")
        for sta_eid in station_list:
            if debug:
                print("checking sta-eid: %s"%(sta_eid))
            eid = self.name_to_eid(sta_eid)
            response = super().json_get("/port/%s/%s/%s?fields=alias,ip,port+type,ipv6+address" %
                 (eid[0], eid[1], eid[2]))
            if debug:
                pprint(response)
            if (response is None) or ("interface" not in response):
                print("station_list: incomplete response:")
                pprint(response)
                #wait_more = True
                break
            if ipv4:
                v = response['interface']
                if (v['ip'] in waiting_states):
                    if debug:
                        print("Waiting for port %s to get IPv4 Address."%(sta_eid))
                else:
                    if debug:
                        print("Found IP: %s on port: %s"%(v['ip'], sta_eid))
                        print("Incrementing stations with IP addresses found")
                        num_sta_with_ips+=1
                    else:
                        num_sta_with_ips+=1 
            if ipv6:
                v = response['interface']
                if (v['ip'] in waiting_states):
                    if debug:
                        print("Waiting for port %s to get IPv6 Address."%(sta_eid))
                    
                else:
                    if debug:
                        print("Found IP: %s on port: %s"%(v['ip'], sta_eid))
                        print("Incrementing stations with IP addresses found")
                        num_sta_with_ips+=1
                    else:
                        num_sta_with_ips+=1   
        return num_sta_with_ips


    def duration_time_to_seconds(self, time_string):
        if isinstance(time_string, str):
            pattern = re.compile("^(\d+)([dhms]$)")
            td = pattern.match(time_string)
            if td is not None:
                dur_time = int(td.group(1))
                dur_measure = str(td.group(2))
                if dur_measure == "d":
                    duration_sec = dur_time * 24 * 60 * 60 
                elif dur_measure == "h":
                    duration_sec = dur_time * 60 * 60
                elif dur_measure == "m":
                    duration_sec = dur_time * 60
                else:
                    duration_sec = dur_time * 1
            else:
                raise ValueError("Unknown value for time_string: %s" % time_string)
        else:
            raise ValueError("time_string must be of type str. Type %s provided" % type(time_string))
        return duration_sec

    def parse_time(self, time_string):
        if isinstance(time_string, str):
            pattern = re.compile("^(\d+)([dhms]$)")
            td = pattern.match(time_string)
            if td is not None:
                dur_time = int(td.group(1))
                dur_measure = str(td.group(2))
                if dur_measure == "d":
                    duration_time = datetime.timedelta(days=dur_time)
                elif dur_measure == "h":
                    duration_time = datetime.timedelta(hours=dur_time)
                elif dur_measure == "m":
                    duration_time = datetime.timedelta(minutes=dur_time)
                else:
                    duration_time = datetime.timedelta(seconds=dur_time)
            else:
                raise ValueError("Unknown value for time_string: %s" % time_string)
        else:
            raise ValueError("time_string must be of type str. Type %s provided" % type(time_string))
        return duration_time

    def remove_all_stations(self, resource):
        port_list = self.station_list()
        sta_list = []
        if sta_list is not None:
            print("Removing all stations")
            for item in list(port_list):
                if "sta" in list(item)[0]:
                    sta_list.append(self.name_to_eid(list(item)[0])[2])

            for sta_name in sta_list:
                req_url = "cli-json/rm_vlan"
                data = {
                    "shelf": 1,
                    "resource": resource,
                    "port": sta_name
                }
                self.json_post(req_url, data)

    def remove_all_endps(self):
        endp_list = self.json_get("/endp/list")
        if "items" in endp_list or "empty" in endp_list:
            return
        if endp_list is not None or endp_list :
            print("Removing all endps")
            endp_list = list(endp_list['endpoint'])
            for endp_name in range(len(endp_list)):
                name = list(endp_list[endp_name])[0]
                req_url = "cli-json/rm_endp"
                data = {
                    "endp_name": name
                }
                self.json_post(req_url, data)

    def remove_all_cxs(self,remove_all_endpoints=False):
        # remove cross connects
        # remove endpoints
        # nc show endpoints
        # nc show cross connects
        try:
            cx_list = list(self.cx_list())
            not_cx = ['warnings', 'errors', 'handler', 'uri', 'items', 'empty']
            if cx_list is not None:
                print("Removing all cxs")
                for cx_name in cx_list:
                    if cx_name in not_cx:
                        continue
                    req_url = "cli-json/rm_cx"
                    data = {
                        "test_mgr": "default_tm",
                        "cx_name": cx_name
                    }
                    self.json_post(req_url, data)
        except:
            print("no cxs to remove")

        if remove_all_endpoints:
            self.remove_all_endps()
            req_url = "cli-json/nc_show_endpoints"
            data = {
                "endpoint":"all"
            }
            self.json_post(req_url, data)
            req_url = "cli-json/show_cx"
            data ={
                "test_mgr":"all",
                "cross_connect":"all"
            }

    def parse_link(self, link):
        link = self.lfclient_url + link
        info = ()

    def new_station_profile(self):
        station_prof = StationProfile(self.lfclient_url, local_realm=self, debug_=self.debug, up=False)
        return station_prof

    def new_multicast_profile(self):
        multi_prof = MULTICASTProfile(self.lfclient_host, self.lfclient_port,
                                  local_realm=self, debug_=self.debug, report_timer_=3000)
        return multi_prof

    def new_wifi_monitor_profile(self, resource_=1, debug_=False, up_=False):
        wifi_mon_prof = WifiMonitor(self.lfclient_url,
                                    local_realm=self,
                                    resource_=resource_,
                                    up=up_,
                                    debug_=(self.debug or debug_))
        return wifi_mon_prof

    def new_l3_cx_profile(self):
        cx_prof = L3CXProfile(self.lfclient_host,
                              self.lfclient_port,
                              local_realm=self,
                              debug_=self.debug,
                              report_timer_=3000)
        return cx_prof

    def new_l4_cx_profile(self):
        cx_prof = L4CXProfile(self.lfclient_host, self.lfclient_port, local_realm=self, debug_=self.debug)
        return cx_prof

    def new_generic_endp_profile(self):
        endp_prof = GenCXProfile(self.lfclient_host, self.lfclient_port, local_realm=self, debug_=self.debug)
        return endp_prof

    def new_generic_cx_profile(self):
        """
        @deprecated
        :return: new GenCXProfile
        """
        cx_prof = GenCXProfile(self.lfclient_host, self.lfclient_port, local_realm=self, debug_=self.debug)
        return cx_prof

    def new_vap_profile(self):
        vap_prof = VAPProfile(lfclient_host=self.lfclient_host, lfclient_port=self.lfclient_port, local_realm=self, debug_=self.debug)
        return vap_prof

    def new_vr_profile(self):
        vap_prof = VRProfile(lfclient_host=self.lfclient_host, lfclient_port=self.lfclient_port, local_realm=self, debug_=self.debug)
        return vap_prof

    def new_http_profile(self):
        http_prof = HTTPProfile(self.lfclient_host, self.lfclient_port, local_realm=self, debug_=self.debug)
        return http_prof

    def new_fio_endp_profile(self):
        cx_prof = FIOEndpProfile(self.lfclient_host, self.lfclient_port, local_realm=self, debug_=self.debug)
        return cx_prof

    def new_dut_profile(self):
        return DUTProfile(self.lfclient_host, self.lfclient_port, local_realm=self, debug_=self.debug)

    def new_mvlan_profile(self):
        return MACVLANProfile(self.lfclient_host, self.lfclient_port, local_realm=self, debug_=self.debug)

    def new_test_group_profile(self):
        return TestGroupProfile(self.lfclient_host, self.lfclient_port, local_realm=self, debug_=self.debug)

class MULTICASTProfile(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port, local_realm,
                 report_timer_=3000, name_prefix_="Unset", number_template_="00000", debug_=False):
        """

        :param lfclient_host:
        :param lfclient_port:
        :param local_realm:
        :param name_prefix_: prefix string for connection
        :param number_template_: how many zeros wide we padd, possibly a starting integer with left padding
        :param debug_:
        """
        super().__init__(lfclient_host, lfclient_port, debug_, _halt_on_error=True)
        self.lfclient_url = "http://%s:%s" % (lfclient_host, lfclient_port)
        self.debug = debug_
        self.local_realm = local_realm
        self.report_timer = report_timer_
        self.created_mc = {}
        self.name_prefix = name_prefix_
        self.number_template = number_template_

    def get_mc_names(self):
        return self.created_mc.keys()

    def refresh_mc(self, debug_=False):
        for endp_name in self.get_mc_names():
            self.json_post("/cli-json/show_endpoints", {
                 "endpoint": endp_name
            }, debug_=debug_)

    def start_mc(self, suppress_related_commands=None, debug_ = False):
        if self.debug:
            debug_=True

        for endp_name in self.get_mc_names():
            print("Starting mcast endpoint: %s"%(endp_name))
            json_data = {
                "endp_name":endp_name
            }
            url = "cli-json/start_endp"
            self.local_realm.json_post(url, json_data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

        pass

    def stop_mc(self, suppress_related_commands=None, debug_ = False):
        if self.debug:
            debug_=True

        for endp_name in self.get_mc_names():
            json_data = {
                "endp_name":endp_name
            }
            url = "cli-json/stop_endp"
            self.local_realm.json_post(url, json_data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

        pass

    def cleanup_prefix(self):
        self.local_realm.cleanup_cxe_prefix(self.name_prefix)

    def cleanup(self, suppress_related_commands=None, debug_ = False):
        if self.debug:
            debug_=True

        for endp_name in self.get_mc_names():
            self.local_realm.rm_endp(endp_name, debug_=debug_, suppress_related_commands_=suppress_related_commands)

    def create_mc_tx(self, endp_type, side_tx, suppress_related_commands=None, debug_=False):
        if self.debug:
            debug_=True

        side_tx_info = self.local_realm.name_to_eid(side_tx)
        side_tx_shelf = side_tx_info[0]
        side_tx_resource = side_tx_info[1]
        side_tx_port = side_tx_info[2]
        side_tx_name = "%smtx-%s-%i"%(self.name_prefix, side_tx_port, len(self.created_mc))

        json_data = []

        #add_endp mcast-xmit-sta 1 1 side_tx mc_udp -1 NO 4000000 0 NO 1472 0 INCREASING NO 32 0 0
        json_data = {
                        'alias':side_tx_name,
                        'shelf':side_tx_shelf,
                        'resource':side_tx_resource,
                        'port':side_tx_port,
                        'type':endp_type,
                        'ip_port':-1,
                        'is_rate_bursty':
                        'NO','min_rate':256000,
                        'max_rate':0,
                        'is_pkt_sz_random':'NO',
                        'min_pkt':1472,
                        'max_pkt':0,
                        'payload_pattern':'INCREASING',
                        'use_checksum':'NO',
                        'ttl':32,
                        'send_bad_crc_per_million':0,
                        'multi_conn':0
                    }

        url = "/cli-json/add_endp"
        self.local_realm.json_post(url, json_data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

        #set_mc_endp mcast-xmit-sta 32 224.9.9.9 9999 No  # critical
        json_data = {
                        'name':side_tx_name,
                        'ttl':32,
                        'mcast_group':'224.9.9.9',
                        'mcast_dest_port':9999,
                        'rcv_mcast':'No'
                    }

        url = "cli-json/set_mc_endp"
        self.local_realm.json_post(url, json_data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

        self.created_mc[side_tx_name] = side_tx_name

        these_endp = [side_tx_name]
        self.local_realm.wait_until_endps_appear(these_endp, debug=debug_)


    def create_mc_rx(self, endp_type, side_rx, suppress_related_commands=None, debug_ = False):
        if self.debug:
            debug_=True

        these_endp = []

        for port_name in side_rx:
            side_rx_info = self.local_realm.name_to_eid(port_name)
            side_rx_shelf = side_rx_info[0]
            side_rx_resource = side_rx_info[1]
            side_rx_port = side_rx_info[2]
            side_rx_name = "%smrx-%s-%i"%(self.name_prefix, side_rx_port, len(self.created_mc))
            # add_endp mcast-rcv-sta-001 1 1 sta0002 mc_udp 9999 NO 0 0 NO 1472 0 INCREASING NO 32 0 0
            json_data = {
                            'alias':side_rx_name,
                            'shelf':side_rx_shelf,
                            'resource':side_rx_resource,
                            'port':side_rx_port,
                            'type':endp_type,
                            'ip_port':9999,
                            'is_rate_bursty':'NO',
                            'min_rate':0,
                            'max_rate':0,
                            'is_pkt_sz_random':'NO',
                            'min_pkt':1472,
                            'max_pkt':0,
                            'payload_pattern':'INCREASING',
                            'use_checksum':'NO',
                            'ttl':32,
                            'send_bad_crc_per_million':0,
                            'multi_conn':0
                        }

            url = "cli-json/add_endp"
            self.local_realm.json_post(url, json_data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

            json_data = {
                            'name':side_rx_name,
                            'ttl':32,
                            'mcast_group':'224.9.9.9',
                            'mcast_dest_port':9999,
                            'rcv_mcast':'Yes'
                        }
            url = "cli-json/set_mc_endp"
            self.local_realm.json_post(url, json_data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

            self.created_mc[side_rx_name] = side_rx_name
            these_endp.append(side_rx_name)

        self.local_realm.wait_until_endps_appear(these_endp, debug=debug_)

    def to_string(self):
        pprint.pprint(self)



class L3CXProfile(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port, local_realm,
                 side_a_min_bps=None, side_b_min_bps=None,
                 side_a_max_bps=0, side_b_max_bps=0,
                 side_a_min_pdu=-1, side_b_min_pdu=-1,
                 side_a_max_pdu=0, side_b_max_pdu=0,
                 report_timer_=3000, name_prefix_="Unset", number_template_="00000", debug_=False):
        """
        :param lfclient_host:
        :param lfclient_port:
        :param local_realm:
        :param side_a_min_bps:
        :param side_b_min_bps:
        :param side_a_max_bps:
        :param side_b_max_bps:
        :param side_a_min_pdu:
        :param side_b_min_pdu:
        :param side_a_max_pdu:
        :param side_b_max_pdu:
        :param name_prefix_: prefix string for connection
        :param number_template_: how many zeros wide we padd, possibly a starting integer with left padding
        :param debug_:
        """
        super().__init__(lfclient_host, lfclient_port, debug_, _halt_on_error=True)
        self.lfclient_url = "http://%s:%s" % (lfclient_host, lfclient_port)
        self.debug = debug_
        self.local_realm = local_realm
        self.side_a_min_pdu = side_a_min_pdu
        self.side_b_min_pdu = side_b_min_pdu
        self.side_a_max_pdu = side_a_max_pdu
        self.side_b_max_pdu = side_b_max_pdu
        self.side_a_min_bps = side_a_min_bps
        self.side_b_min_bps = side_b_min_bps
        self.side_a_max_bps = side_a_max_bps
        self.side_b_max_bps = side_b_max_bps
        self.report_timer = report_timer_
        self.created_cx = {}
        self.created_endp = {}
        self.name_prefix = name_prefix_
        self.number_template = number_template_

    def get_cx_names(self):
        return self.created_cx.keys()

    def get_cx_report(self):
        self.data = {}
        for cx_name in self.get_cx_names():
            self.data[cx_name] = self.json_get("/cx/" + cx_name).get(cx_name)
        return self.data    

    def monitor(self, duration_sec=60,
                interval_sec=1,
                col_names=None,
                show=True,
                report_file=None):
        if (duration_sec is None) or (duration_sec <= 1):
            raise ValueError("L3CXProfile::monitor wants duration_sec > 1 second")
        if (interval_sec is None) or (interval_sec < 1):
            raise ValueError("L3CXProfile::monitor wants interval_sec >= 1 second")
        if (duration_sec <= interval_sec ):
            raise ValueError("L3CXProfile::monitor wants duration_sec > interval_sec")
        if col_names is None:
            raise ValueError("L3CXProfile::monitor wants a list of column names to monitor")
        endps = ",".join(self.created_cx.keys())
        time_results = {}
        fields=",".join(col_names)
        report_fh = None
        if (report_file is not None) and (report_file != ""):
            report_fh = open(report_file, "w")

        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(seconds=duration_sec)

        while datetime.datetime.now() < end_time_d:
            response = self.json_get("/endp/%s?fields=%s" % (endps, fields), debug_=self.debug)
            if "endpoint" not in response:
                pprint.pprint(response)
                raise ValueError("no endpoint?")
            value_map = {}
            if show:
                print("Show stuff here")

            if datetime.datetime.now() > end_time_d:
                break;
            time.sleep(interval_sec)
        if report_fh is not None:
            report_fh.close()


    def refresh_cx(self):
        for cx_name in self.created_cx.keys():
            self.json_post("/cli-json/show_cxe", {
                 "test_mgr": "ALL",
                 "cross_connect": cx_name
            }, debug_=self.debug)
            print(".", end='')

    def start_cx(self):
        print("Starting CXs...")
        for cx_name in self.created_cx.keys():
            if self.debug:
                print("cx-name: %s"%(cx_name))
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
                "cx_state": "RUNNING"
            }, debug_=self.debug)
            print(".", end='')
        print("")

    def stop_cx(self):
        print("Stopping CXs...")
        for cx_name in self.created_cx.keys():
            self.local_realm.stop_cx(cx_name)
            print(".", end='')
        print("")

    def cleanup_prefix(self):
        self.local_realm.cleanup_cxe_prefix(self.name_prefix)

    def cleanup(self):
        print("Cleaning up cxs and endpoints")
        if len(self.created_cx) != 0:
            for cx_name in self.created_cx.keys():
                if self.debug:
                    print("Cleaning cx: %s"%(cx_name))
                self.local_realm.rm_cx(cx_name)

                for side in range(len(self.created_cx[cx_name])):
                    ename = self.created_cx[cx_name][side]
                    if self.debug:
                        print("Cleaning endpoint: %s"%(ename))
                    self.local_realm.rm_endp(self.created_cx[cx_name][side])

    def create(self, endp_type, side_a, side_b, sleep_time=0.03, suppress_related_commands=None, debug_=False, tos=None):
        if self.debug:
            debug_=True

        cx_post_data = []
        timer_post_data = []
        these_endp = []
        these_cx = []

        # print(self.side_a_min_rate, self.side_a_max_rate)
        # print(self.side_b_min_rate, self.side_b_max_rate)
        if (self.side_a_min_bps is None) \
                or (self.side_a_max_bps is None) \
                or (self.side_b_min_bps is None) \
                or (self.side_b_max_bps is None):
            raise ValueError("side_a_min_bps, side_a_max_bps, side_b_min_bps, and side_b_max_bps must all be set to a value")

        if type(side_a) == list and type(side_b) != list:
            side_b_info = self.local_realm.name_to_eid(side_b)
            side_b_shelf = side_b_info[0]
            side_b_resource = side_b_info[1]

            for port_name in side_a:
                side_a_info = self.local_realm.name_to_eid(port_name)
                side_a_shelf = side_a_info[0]
                side_a_resource = side_a_info[1]
                if port_name.find('.') < 0:
                    port_name = "%d.%s" % (side_a_info[1], port_name)

                cx_name = "%s%s-%i"%(self.name_prefix, side_a_info[2], len(self.created_cx))

                endp_a_name = cx_name + "-A"
                endp_b_name = cx_name + "-B"
                self.created_cx[ cx_name ] = [endp_a_name, endp_b_name]
                self.created_endp[endp_a_name] = endp_a_name
                self.created_endp[endp_b_name] = endp_b_name
                these_cx.append(cx_name)
                these_endp.append(endp_a_name)
                these_endp.append(endp_b_name)
                endp_side_a = {
                    "alias": endp_a_name,
                    "shelf": side_a_shelf,
                    "resource": side_a_resource,
                    "port": side_a_info[2],
                    "type": endp_type,
                    "min_rate": self.side_a_min_bps,
                    "max_rate": self.side_a_max_bps,
                    "min_pkt": self.side_a_min_pdu,
                    "max_pkt": self.side_a_max_pdu,
                    "ip_port": -1
                }
                endp_side_b = {
                    "alias": endp_b_name,
                    "shelf": side_b_shelf,
                    "resource": side_b_resource,
                    "port": side_b_info[2],
                    "type": endp_type,
                    "min_rate": self.side_b_min_bps,
                    "max_rate": self.side_b_max_bps,
                    "min_pkt": self.side_b_min_pdu,
                    "max_pkt": self.side_b_max_pdu,
                    "ip_port": -1
                }

                url = "/cli-json/add_endp"
                self.local_realm.json_post(url, endp_side_a, debug_=debug_, suppress_related_commands_=suppress_related_commands)
                self.local_realm.json_post(url, endp_side_b, debug_=debug_, suppress_related_commands_=suppress_related_commands)
                #print("napping %f sec"%sleep_time)
                time.sleep(sleep_time)

                url = "cli-json/set_endp_flag"
                data = {
                    "name": endp_a_name,
                    "flag": "AutoHelper",
                    "val": 1
                }
                self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands)
                data["name"] = endp_b_name
                self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

                if (endp_type == "lf_udp") or (endp_type == "udp") or (endp_type == "lf_udp6") or (endp_type == "udp6"):
                    data["name"] = endp_a_name
                    data["flag"] = "UseAutoNAT"
                    self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands)
                    data["name"] = endp_b_name
                    self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

                if tos != None:
                    self.local_realm.set_endp_tos(endp_a_name, tos)
                    self.local_realm.set_endp_tos(endp_b_name, tos)

                data = {
                    "alias": cx_name,
                    "test_mgr": "default_tm",
                    "tx_endp": endp_a_name,
                    "rx_endp": endp_b_name,
                }
                #pprint(data)
                cx_post_data.append(data)
                timer_post_data.append({
                    "test_mgr":"default_tm",
                    "cx_name":cx_name,
                    "milliseconds":self.report_timer
                })

        elif type(side_b) == list and type(side_a) != list:
            side_a_info = self.local_realm.name_to_eid(side_a)
            side_a_shelf = side_a_info[0]
            side_a_resource = side_a_info[1]
            #side_a_name = side_a_info[2]

            for port_name in side_b:
                print(side_b)
                side_b_info = self.local_realm.name_to_eid(port_name)
                side_b_shelf = side_b_info[0]
                side_b_resource = side_b_info[1]
                side_b_name = side_b_info[2]

                cx_name = "%s%s-%i" % (self.name_prefix, port_name, len(self.created_cx))
                endp_a_name = cx_name + "-A"
                endp_b_name = cx_name + "-B"
                self.created_cx[ cx_name ] = [endp_a_name, endp_b_name]
                self.created_endp[endp_a_name] = endp_a_name
                self.created_endp[endp_b_name] = endp_b_name
                these_cx.append(cx_name)
                these_endp.append(endp_a_name)
                these_endp.append(endp_b_name)
                endp_side_a = {
                    "alias": endp_a_name,
                    "shelf": side_a_shelf,
                    "resource": side_a_resource,
                    "port": side_a_info[2],
                    "type": endp_type,
                    "min_rate": self.side_a_min_bps,
                    "max_rate": self.side_a_max_bps,
                    "min_pkt": self.side_a_min_pdu,
                    "max_pkt": self.side_a_max_pdu,
                    "ip_port": -1
                }
                endp_side_b = {
                    "alias": endp_b_name,
                    "shelf": side_b_shelf,
                    "resource": side_b_resource,
                    "port": side_b_info[2],
                    "type": endp_type,
                    "min_rate": self.side_b_min_bps,
                    "max_rate": self.side_b_max_bps,
                    "min_pkt": self.side_b_min_pdu,
                    "max_pkt": self.side_b_max_pdu,
                    "ip_port": -1
                }

                url = "/cli-json/add_endp"
                self.local_realm.json_post(url, endp_side_a, debug_=debug_, suppress_related_commands_=suppress_related_commands)
                self.local_realm.json_post(url, endp_side_b, debug_=debug_, suppress_related_commands_=suppress_related_commands)
                #print("napping %f sec" %sleep_time )
                time.sleep(sleep_time)

                url = "cli-json/set_endp_flag"
                data = {
                    "name": endp_a_name,
                    "flag": "autohelper",
                    "val": 1
                }
                self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

                url = "cli-json/set_endp_flag"
                data = {
                    "name": endp_b_name,
                    "flag": "autohelper",
                    "val": 1
                }
                self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands)
                #print("CXNAME451: %s" % cx_name)
                data = {
                    "alias": cx_name,
                    "test_mgr": "default_tm",
                    "tx_endp": endp_a_name,
                    "rx_endp": endp_b_name,
                }
                cx_post_data.append(data)
                timer_post_data.append({
                    "test_mgr":"default_tm",
                    "cx_name":cx_name,
                    "milliseconds":self.report_timer
                })
        else:
            raise ValueError("side_a or side_b must be of type list but not both: side_a is type %s side_b is type %s" % (type(side_a), type(side_b)))

        self.local_realm.wait_until_endps_appear(these_endp, debug=debug_)

        for data in cx_post_data:
            url = "/cli-json/add_cx"
            self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands)
            time.sleep(0.01)

        self.local_realm.wait_until_cxs_appear(these_cx, debug=debug_)

    def to_string(self):
        pprint.pprint(self)


class L4CXProfile(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port, local_realm, debug_=False):
        super().__init__(lfclient_host, lfclient_port, debug_, _halt_on_error=True)
        self.lfclient_url = "http://%s:%s" % (lfclient_host, lfclient_port)
        self.debug = debug_
        self.url = "http://localhost/"
        self.requests_per_ten = 600
        self.local_realm = local_realm
        self.created_cx = {}
        self.created_endp = []

    def check_errors(self, debug=False):
        fields_list = ["!conn", "acc.+denied", "bad-proto", "bad-url", "other-err", "total-err", "rslv-p", "rslv-h",
                       "timeout", "nf+(4xx)", "http-r", "http-p", "http-t", "login-denied"]
        endp_list = self.json_get("layer4/list?fields=%s" % ','.join(fields_list))
        debug_info = {}
        if endp_list is not None and endp_list['endpoint'] is not None:
            endp_list = endp_list['endpoint']
            expected_passes = len(endp_list)
            passes = len(endp_list)
            for item in range(len(endp_list)):
                for name, info in endp_list[item].items():
                    for field in fields_list:
                        if info[field.replace("+", " ")] > 0:
                            passes -= 1
                            debug_info[name] = {field: info[field.replace("+", " ")]}
            if debug:
                print(debug_info)
            if passes == expected_passes:
                return True
            else:
                print(list(debug_info), " Endps in this list showed errors getting to %s " % self.url)
                return False

    def start_cx(self):
        print("Starting CXs...")
        for cx_name in self.created_cx.keys():
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": self.created_cx[cx_name],
                "cx_state": "RUNNING"
            }, debug_=self.debug)
            print(".", end='')
        print("")

    def stop_cx(self):
        print("Stopping CXs...")
        for cx_name in self.created_cx.keys():
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": self.created_cx[cx_name],
                "cx_state": "STOPPED"
            }, debug_=self.debug)
            print(".", end='')
        print("")

    def cleanup(self):
        print("Cleaning up cxs and endpoints")
        if len(self.created_cx) != 0:
            for cx_name in self.created_cx.keys():
                req_url = "cli-json/rm_cx"
                data = {
                    "test_mgr": "default_tm",
                    "cx_name": self.created_cx[cx_name]
                }
                self.json_post(req_url, data)
                #pprint(data)
                req_url = "cli-json/rm_endp"
                data = {
                    "endp_name": cx_name
                }
                self.json_post(req_url, data)
                #pprint(data)

    def create(self, ports=[], sleep_time=.5, debug_=False, suppress_related_commands_=None):
        cx_post_data = []
        for port_name in ports:
            if len(self.local_realm.name_to_eid(port_name)) == 3:
                shelf = self.local_realm.name_to_eid(port_name)[0]
                resource = self.local_realm.name_to_eid(port_name)[1]
                name = self.local_realm.name_to_eid(port_name)[2]
            else:
                raise ValueError("Unexpected name for port_name %s" % port_name)
            endp_data = {
                "alias": name + "_l4",
                "shelf": shelf,
                "resource": resource,
                "port": name,
                "type": "l4_generic",
                "timeout": 10,
                "url_rate": self.requests_per_ten,
                "url": self.url,
                "proxy_auth_type": 0x200
            }
            url = "cli-json/add_l4_endp"
            self.local_realm.json_post(url, endp_data, debug_=debug_, suppress_related_commands_=suppress_related_commands_)
            time.sleep(sleep_time)

            endp_data = {
                "alias": "CX_" + name + "_l4",
                "test_mgr": "default_tm",
                "tx_endp": name + "_l4",
                "rx_endp": "NA"
            }
            cx_post_data.append(endp_data)
            self.created_cx[name + "_l4"] = "CX_" + name + "_l4"

        for cx_data in cx_post_data:
            url = "/cli-json/add_cx"
            self.local_realm.json_post(url, cx_data, debug_=debug_, suppress_related_commands_=suppress_related_commands_)
            time.sleep(sleep_time)


class GenCXProfile(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port, local_realm, debug_=False):
        super().__init__(lfclient_host, lfclient_port, debug_, _halt_on_error=True)
        self.lfclient_host = lfclient_host
        self.lfclient_port = lfclient_port
        self.lfclient_url = "http://%s:%s" % (lfclient_host, lfclient_port)
        self.debug = debug_
        self.type = "lfping"
        self.dest = "127.0.0.1"
        self.interval = 1
        self.cmd = ""
        self.local_realm = local_realm
        self.name_prefix = "generic"
        self.created_cx = []
        self.created_endp = []

    def parse_command(self, sta_name):
        if self.type == "lfping":
            if ((self.dest is not None) or (self.dest != "")) and ((self.interval is not None) or (self.interval > 0)):
                self.cmd = "%s  -i %s -I %s %s" % (self.type, self.interval, sta_name, self.dest)
                #print(self.cmd)
            else:
                raise ValueError("Please ensure dest and interval have been set correctly")
        elif self.type == "generic":
            if self.cmd == "":
                raise ValueError("Please ensure cmd has been set correctly")
        elif self.type == "speedtest":
            self.cmd = "vrf_exec.bash %s speedtest-cli --json --share" % (sta_name)
        elif self.type == "iperf3" and self.dest is not None:
            self.cmd = "iperf3 --forceflush --format k --precision 4 -c %s -t 60 --tos 0 -b 1K --bind_dev %s -i 1 " \
                       "--pidfile /tmp/lf_helper_iperf3_test.pid" % (self.dest, sta_name)
        else:
            raise ValueError("Unknown command type")

    def start_cx(self):
        print("Starting CXs...")
        #print(self.created_cx)
        #print(self.created_endp)
        for cx_name in self.created_cx:
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
                "cx_state": "RUNNING"
            }, debug_=self.debug)
            print(".", end='')
        print("")

    def stop_cx(self):
        print("Stopping CXs...")
        for cx_name in self.created_cx:
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
                "cx_state": "STOPPED"
            }, debug_=self.debug)
            print(".", end='')
        print("")

    def cleanup(self):
        print("Cleaning up cxs and endpoints")
        for cx_name in self.created_cx:
            req_url = "cli-json/rm_cx"
            data = {
                "test_mgr": "default_tm",
                "cx_name": cx_name
            }
            self.json_post(req_url, data)

        for endp_name in self.created_endp:
            req_url = "cli-json/rm_endp"
            data = {
                "endp_name": endp_name
            }
            self.json_post(req_url, data)

    def create(self, ports=[], sleep_time=.5, debug_=False, suppress_related_commands_=None):
        if self.debug:
            debug_ = True
        post_data = []
        endp_tpls = []
        for port_name in ports:
            port_info = self.local_realm.name_to_eid(port_name)
            if len(port_info) == 2:
                resource = 1
                shelf = port_info[0]
                name = port_info[-1]
            elif len(port_info) == 3:
                resource = port_info[0]
                shelf = port_info[1]
                name = port_info[-1]
            else:
                raise ValueError("Unexpected name for port_name %s" % port_name)

            # this naming convention follows what you see when you use
            # lf_firemod.pl --action list_endp after creating a generic endpoint
            gen_name_a = "%s-%s"%(self.name_prefix, name)
            gen_name_b = "D_%s-%s"%(self.name_prefix, name)
            endp_tpls.append( (resource, name, gen_name_a, gen_name_b))

        for endp_tpl in endp_tpls:
            resource    = endp_tpl[0]
            name        = endp_tpl[1]
            gen_name_a  = endp_tpl[2]
            #gen_name_b  = endp_tpl[3]
            genl = GenericCx(lfclient_host=self.lfclient_host, lfclient_port=self.lfclient_port, debug_=self.debug)
            # (self, alias=None, shelf=1, resource=1, port=None, type=None):
            genl.create_gen_endp(alias=gen_name_a, shelf=shelf, resource=resource, port=name)
            # genl.create_gen_endp(alias=gen_name_b, shelf=shelf, resource=resource, port=name)

        self.local_realm.json_post("/cli-json/nc_show_endpoints", {"endpoint": "all"})
        time.sleep(sleep_time)
        
        for endp_tpl in endp_tpls:
            gen_name_a  = endp_tpl[2]
            gen_name_b  = endp_tpl[3]
            genl.set_flags(gen_name_a, "ClearPortOnStart", 1)
            # genl.set_flags(gen_name_b, "ClearPortOnStart", 1)
            # genl.set_flags(gen_name_b, "Unmanaged", 1)
        time.sleep(sleep_time)

        for endp_tpl in endp_tpls:
            name        = endp_tpl[1]
            gen_name_a  = endp_tpl[2]
            # gen_name_b  = endp_tpl[3]
            self.parse_command(name)
            genl.set_cmd(gen_name_a, self.cmd)
        time.sleep(sleep_time)

        for endp_tpl in endp_tpls:
            name        = endp_tpl[1]
            gen_name_a  = endp_tpl[2]
            gen_name_b  = endp_tpl[3]
            cx_name     = "CX_%s-%s"%(self.name_prefix, name)
            data = {
                "alias": cx_name,
                "test_mgr": "default_tm",
                "tx_endp": gen_name_a,
                "rx_endp": gen_name_b
            }
            post_data.append(data)
            self.created_cx.append(cx_name)
            self.created_endp.append(gen_name_a)
            self.created_endp.append(gen_name_b)

        time.sleep(sleep_time)

        for data in post_data:
            url = "/cli-json/add_cx"
            if self.debug:
                pprint(data)
            self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands_)
            time.sleep(10)
        time.sleep(sleep_time)
        for data in post_data:
            self.local_realm.json_post("/cli-json/show_cx", {
                "test_mgr":"default_tm",
                "cross_connect": data["alias"]
            })
        time.sleep(sleep_time)

class WifiMonitor:
    def __init__(self, lfclient_url, local_realm, up=True, debug_=False, resource_=1):
        self.debug = debug_
        self.lfclient_url = lfclient_url
        self.up = up
        self.local_realm = local_realm
        self.monitor_name = None
        self.resource = resource_
        self.flag_names = []
        self.flag_mask_names = []
        self.flags_mask = add_monitor.default_flags_mask
        self.aid = "NA" # used when sniffing /ax radios
        self.bsssid = "00:00:00:00:00:00" # used when sniffing on /ax radios

    def create(self, resource_=1, channel=None, radio_="wiphy0", name_="moni0" ):
        print("Creating monitor " + name_)
        self.monitor_name = name_
        computed_flags = 0
        for flag_n in self.flag_names:
            computed_flags += add_monitor.flags[flag_n]

        # we want to query the existing country code of the radio
        # there's no reason to change it but we get hollering from server
        # if we don't provide a value for the parameter
        jr = self.local_realm.json_get("/radiostatus/1/%s/%s?fields=channel,frequency,country"%(resource_, radio_), debug_=self.debug)
        if jr is None:
            raise ValueError("No radio %s.%s found"%(resource_, radio_))

        eid = "1.%s.%s"%(resource_, radio_)
        frequency = 0
        country = 0
        if eid in jr:
            country = jr[eid]["country"]

        data = {
            "shelf": 1,
            "resource": resource_,
            "radio": radio_,
            "mode": 0, #"NA", #0 for AUTO or "NA"
            "channel": channel,
            "country": country,
            "frequency": self.local_realm.channel_freq(channel_=channel)
        }
        self.local_realm.json_post("/cli-json/set_wifi_radio", _data=data)
        time.sleep(1)
        self.local_realm.json_post("/cli-json/add_monitor", {
            "shelf": 1,
            "resource": resource_,
            "radio": radio_,
            "ap_name": self.monitor_name,
            "flags": computed_flags,
            "flags_mask": self.flags_mask
        })

    def set_flag(self, param_name, value):
        if (param_name not in add_monitor.flags):
            raise ValueError("Flag '%s' does not exist for add_monitor, consult add_monitor.py" % param_name)
        if (value == 1) and (param_name not in self.flag_names):
            self.flag_names.append(param_name)
        elif (value == 0) and (param_name in self.flag_names):
            del self.flag_names[param_name]
            self.flags_mask |= add_monitor.flags[param_name]

    def cleanup(self, resource_=1, desired_ports=None):
        print("Cleaning up monitors")
        if (desired_ports is None) or (len(desired_ports) < 1):
            if (self.monitor_name is None) or (self.monitor_name == ""):
                print("No monitor name set to delete")
                return
            LFUtils.removePort(resource=resource_,
                               port_name=self.monitor_name,
                               baseurl=self.lfclient_url,
                               debug=self.debug)
        else:
            names = ",".join(desired_ports)
            existing_ports = self.local_realm.json_get("/port/1/%d/%s?fields=alias"%(resource_, names), debug_=False)
            if (existing_ports is None) or ("interfaces" not in existing_ports) or ("interface" not in existing_ports):
                print("No monitor names found to delete")
                return
            if ("interfaces" in existing_ports):
                for eid,info in existing_ports["interfaces"].items():
                    LFUtils.removePort(resource=resource_,
                                       port_name=info["alias"],
                                       baseurl=self.lfclient_url,
                                       debug=self.debug)
            if ("interface" in existing_ports):
                for eid,info in existing_ports["interface"].items():
                    LFUtils.removePort(resource=resource_,
                                       port_name=info["alias"],
                                       baseurl=self.lfclient_url,
                                       debug=self.debug)



    def admin_up(self):
        up_request = LFUtils.port_up_request(resource_id=self.resource, port_name=self.monitor_name)
        self.local_realm.json_post("/cli-json/set_port", up_request)

    def admin_down(self):
        down_request = LFUtils.portDownRequest(resource_id=self.resource, port_name=self.monitor_name)
        self.local_realm.json_post("/cli-json/set_port", down_request)

    def start_sniff(self, capname=None, duration_sec=60):
        if capname is None:
            raise ValueError("Need a capture file name")
        data = {
                "shelf": 1,
                "resource": 1,
                "port": self.monitor_name,
                "display": "NA",
                "flags": 0x2,
                "outfile": capname,
                "duration": duration_sec
            }
        self.local_realm.json_post("/cli-json/sniff_port", _data= data)


               # "sniff_port 1 %s %s NA %s %s.pcap %i"%(r, m, sflags, m, int(dur))

class VAPProfile(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port, local_realm, vap_name="", ssid="NA", ssid_pass="NA", mode=0, debug_=False):
        super().__init__(_lfjson_host=lfclient_host, _lfjson_port=lfclient_port, _debug=debug_)
        self.debug = debug_
        #self.lfclient_url = lfclient_url # done in super()
        self.ssid = ssid
        self.ssid_pass = ssid_pass
        self.mode = mode
        self.local_realm = local_realm
        self.vap_name = vap_name
        self.COMMANDS = ["add_vap", "set_port"]
        self.desired_add_vap_flags = ["wpa2_enable", "80211u_enable", "create_admin_down"]
        self.desired_add_vap_flags_mask = ["wpa2_enable", "80211u_enable", "create_admin_down"]

        self.add_vap_data = {
            "shelf": 1,
            "resource": 1,
            "radio": None,
            "ap_name": None,
            "flags": 0,
            "flags_mask": 0,
            "mode": 0,
            "ssid": None,
            "key": None,
            "mac": "xx:xx:xx:xx:*:xx"
        }

        self.desired_set_port_cmd_flags = []
        self.desired_set_port_current_flags = ["if_down"]
        self.desired_set_port_interest_flags = ["current_flags", "ifdown"]
        self.set_port_data = {
            "shelf": 1,
            "resource": 1,
            "port": None,
            "current_flags": 0,
            "interest": 0,  # (0x2 + 0x4000 + 0x800000)  # current, dhcp, down
        }
        self.wifi_extra_data_modified = False
        self.wifi_extra_data = {
            "shelf": 1,
            "resource": 1,
            "port": None,
            "key_mgmt": None,
            "eap": None,
            "hessid": None,
            "identity": None,
            "password": None,
            "realm": None,
            "domain": None
        }

    def set_wifi_extra(self,
                       key_mgmt="WPA-EAP",
                       pairwise="DEFAULT",
                       group="DEFAULT",
                       psk="[BLANK]",
                       eap="TTLS",
                       identity="testuser",
                       passwd="testpasswd",
                       realm="localhost.localdomain",
                       domain="localhost.localdomain",
                       hessid="00:00:00:00:00:01"):
        self.wifi_extra_data_modified = True
        self.wifi_extra_data["key_mgmt"] = key_mgmt
        self.wifi_extra_data["eap"] = eap
        self.wifi_extra_data["identity"] = identity
        self.wifi_extra_data["password"] = passwd
        self.wifi_extra_data["realm"] = realm
        self.wifi_extra_data["domain"] = domain
        self.wifi_extra_data["hessid"] = hessid

    def admin_up(self, resource):
        set_port_r = LFRequest.LFRequest(self.lfclient_url, "/cli-json/set_port", debug_=self.debug)
        req_json = LFUtils.portUpRequest(resource, None, debug_on=self.debug)
        req_json["port"] = self.vap_name
        set_port_r.addPostData(req_json)
        json_response = set_port_r.jsonPost(self.debug)
        time.sleep(0.03)

    def admin_down(self, resource):
        set_port_r = LFRequest.LFRequest(self.lfclient_url, "/cli-json/set_port", debug_=self.debug)
        req_json = LFUtils.port_down_request(resource, None, debug_on=self.debug)
        req_json["port"] = self.vap_name
        set_port_r.addPostData(req_json)
        json_response = set_port_r.jsonPost(self.debug)
        time.sleep(0.03)

    def use_security(self, security_type, ssid=None, passwd=None):
        types = {"wep": "wep_enable", "wpa": "wpa_enable", "wpa2": "wpa2_enable", "wpa3": "use-wpa3", "open": "[BLANK]"}
        self.add_vap_data["ssid"] = ssid
        if security_type in types.keys():
            if (ssid is None) or (ssid == ""):
                raise ValueError("use_security: %s requires ssid" % security_type)
            if (passwd is None) or (passwd == ""):
                raise ValueError("use_security: %s requires passphrase or [BLANK]" % security_type)
            for name in types.values():
                if name in self.desired_add_vap_flags and name in self.desired_add_vap_flags_mask:
                    self.desired_add_vap_flags.remove(name)
                    self.desired_add_vap_flags_mask.remove(name)
            if security_type != "open":
                self.desired_add_vap_flags.append(types[security_type])
                self.desired_add_vap_flags_mask.append(types[security_type])
            else:
                passwd = "[BLANK]"
            self.set_command_param("add_vap", "ssid", ssid)
            self.set_command_param("add_vap", "key", passwd)
            # unset any other security flag before setting our present flags
            if security_type == "wpa3":
                self.set_command_param("add_vap", "ieee80211w", 2)

    def set_command_flag(self, command_name, param_name, value):
        # we have to check what the param name is
        if (command_name is None) or (command_name == ""):
            return
        if (param_name is None) or (param_name == ""):
            return
        if command_name not in self.COMMANDS:
            print("Command name name [%s] not defined in %s" % (command_name, self.COMMANDS))
            return
        if command_name == "add_vap":
            if (param_name not in add_vap.add_vap_flags):
                print("Parameter name [%s] not defined in add_vap.py" % param_name)
                if self.debug:
                    pprint(add_vap.add_vap_flags)
                return
            if (value == 1) and (param_name not in self.desired_add_vap_flags):
                self.desired_add_vap_flags.append(param_name)
                self.desired_add_vap_flags_mask.append(param_name)
            elif value == 0:
                self.desired_add_vap_flags.remove(param_name)
                self.desired_add_vap_flags_mask.append(param_name)

        elif command_name == "set_port":
            if (param_name not in set_port.set_port_current_flags) and (param_name not in set_port.set_port_cmd_flags) and (param_name not in set_port.set_port_interest_flags):
                print("Parameter name [%s] not defined in set_port.py" % param_name)
                if self.debug:
                    pprint(set_port.set_port_cmd_flags)
                    pprint(set_port.set_port_current_flags)
                    pprint(set_port.set_port_interest_flags)
                return
            if param_name in set_port.set_port_cmd_flags:
                if (value == 1) and (param_name not in self.desired_set_port_cmd_flags):
                    self.desired_set_port_cmd_flags.append(param_name)
                elif value == 0:
                    self.desired_set_port_cmd_flags.remove(param_name)
            elif param_name in set_port.set_port_current_flags:
                if (value == 1) and (param_name not in self.desired_set_port_current_flags):
                    self.desired_set_port_current_flags.append(param_name)
                elif value == 0:
                    self.desired_set_port_current_flags.remove(param_name)
            elif param_name in set_port.set_port_interest_flags:
                if (value == 1) and (param_name not in self.desired_set_port_interest_flags):
                    self.desired_set_port_interest_flags.append(param_name)
                elif value == 0:
                    self.desired_set_port_interest_flags.remove(param_name)
            else:
                raise ValueError("Unknown param name: " + param_name)

    def set_command_param(self, command_name, param_name, param_value):
        # we have to check what the param name is
        if (command_name is None) or (command_name == ""):
            return
        if (param_name is None) or (param_name == ""):
            return
        if command_name not in self.COMMANDS:
            self.error("Command name name [%s] not defined in %s" % (command_name, self.COMMANDS))
            return
        if command_name == "add_vap":
            self.add_vap_data[param_name] = param_value
        elif command_name == "set_port":
            self.set_port_data[param_name] = param_value

    def add_named_flags(self, desired_list, command_ref):
        if desired_list is None:
            raise ValueError("addNamedFlags wants a list of desired flag names")
        if len(desired_list) < 1:
            print("addNamedFlags: empty desired list")
            return 0
        if (command_ref is None) or (len(command_ref) < 1):
            raise ValueError("addNamedFlags wants a maps of flag values")

        result = 0
        for name in desired_list:
            if (name is None) or (name == ""):
                continue
            if name not in command_ref:
                if self.debug:
                    pprint(command_ref)
                raise ValueError("flag %s not in map" % name)
            #print("add-named-flags: %s  %i"%(name, command_ref[name]))
            result |= command_ref[name]

        return result

    def create(self, resource, radio, channel=None, up_=None, debug=False, use_ht40=True, use_ht80=True, use_ht160=False,
               suppress_related_commands_=True, use_radius=False, hs20_enable=False):
        port_list = self.local_realm.json_get("port/1/1/list")
        if port_list is not None:
            port_list = port_list['interfaces']
            for port in port_list:
                for k,v in port.items():
                    if v['alias'] == self.vap_name:
                        self.local_realm.rm_port(k, check_exists=True)
        if use_ht160:
            self.desired_add_vap_flags.append("enable_80211d")
            self.desired_add_vap_flags_mask.append("enable_80211d")
            self.desired_add_vap_flags.append("80211h_enable")
            self.desired_add_vap_flags_mask.append("80211h_enable")
            self.desired_add_vap_flags.append("ht160_enable")
            self.desired_add_vap_flags_mask.append("ht160_enable")
        if not use_ht40:
            self.desired_add_vap_flags.append("disable_ht40")
            self.desired_add_vap_flags_mask.append("disable_ht40")
        if not use_ht80:
            self.desired_add_vap_flags.append("disable_ht80")
            self.desired_add_vap_flags_mask.append("disable_ht80")
        if use_radius:
            self.desired_add_vap_flags.append("8021x_radius")
            self.desired_add_vap_flags_mask.append("8021x_radius")
        if hs20_enable:
            self.desired_add_vap_flags.append("hs20_enable")
            self.desired_add_vap_flags_mask.append("hs20_enable")

        #print("MODE ========= ", self.mode)

        jr = self.local_realm.json_get("/radiostatus/1/%s/%s?fields=channel,frequency,country" % (resource, radio), debug_=self.debug)
        if jr is None:
            raise ValueError("No radio %s.%s found" % (resource, radio))

        eid = "1.%s.%s" % (resource, radio)
        frequency = 0
        country = 0
        if eid in jr:
            country = jr[eid]["country"]

        data = {
            "shelf": 1,
            "resource": resource,
            "radio": radio,
            "mode": self.mode, #"NA", #0 for AUTO or "NA"
            "channel": channel,
            "country": country,
            "frequency": self.local_realm.channel_freq(channel_=channel)
        }
        self.local_realm.json_post("/cli-json/set_wifi_radio", _data=data)
        if up_ is not None:
            self.up = up_
        if self.up:
            if "create_admin_down" in self.desired_add_vap_flags:
                del self.desired_add_vap_flags[self.desired_add_vap_flags.index("create_admin_down")]
        elif "create_admin_down" not in self.desired_add_vap_flags:
            self.desired_add_vap_flags.append("create_admin_down")

        # create vaps down, do set_port on them, then set vaps up
        self.add_vap_data["mode"] = self.mode
        self.add_vap_data["flags"] = self.add_named_flags(self.desired_add_vap_flags, add_vap.add_vap_flags)
        self.add_vap_data["flags_mask"] = self.add_named_flags(self.desired_add_vap_flags_mask, add_vap.add_vap_flags)
        self.add_vap_data["radio"] = radio

        self.add_vap_data["resource"] = resource
        self.set_port_data["current_flags"] = self.add_named_flags(self.desired_set_port_current_flags,
                                                                   set_port.set_port_current_flags)
        self.set_port_data["interest"] = self.add_named_flags(self.desired_set_port_interest_flags,
                                                              set_port.set_port_interest_flags)
        # these are unactivated LFRequest objects that we can modify and
        # re-use inside a loop, reducing the number of object creations
        add_vap_r = LFRequest.LFRequest(self.lfclient_url + "/cli-json/add_vap")
        set_port_r = LFRequest.LFRequest(self.lfclient_url + "/cli-json/set_port")
        wifi_extra_r = LFRequest.LFRequest(self.lfclient_url + "/cli-json/set_wifi_extra")
        if suppress_related_commands_:
            self.add_vap_data["suppress_preexec_cli"] = "yes"
            self.add_vap_data["suppress_preexec_method"] = 1
            self.set_port_data["suppress_preexec_cli"] = "yes"
            self.set_port_data["suppress_preexec_method"] = 1

        # pprint(self.station_names)
        # exit(1)
        self.set_port_data["port"] = self.vap_name
        self.add_vap_data["ap_name"] = self.vap_name
        add_vap_r.addPostData(self.add_vap_data)
        if debug:
            print("- 1502 - %s- - - - - - - - - - - - - - - - - - " % self.vap_name)
            pprint(self.add_vap_data)
            pprint(self.set_port_data)
            pprint(add_vap_r)
            print("- ~1502 - - - - - - - - - - - - - - - - - - - ")

        json_response = add_vap_r.jsonPost(debug)
        # time.sleep(0.03)
        time.sleep(2)
        set_port_r.addPostData(self.set_port_data)
        json_response = set_port_r.jsonPost(debug)
        time.sleep(0.03)

        self.wifi_extra_data["resource"] = resource
        self.wifi_extra_data["port"] = self.vap_name
        if self.wifi_extra_data_modified:
            wifi_extra_r.addPostData(self.wifi_extra_data)
            json_response = wifi_extra_r.jsonPost(debug)
       

        port_list = self.local_realm.json_get("port/1/1/list")
        if port_list is not None:
            port_list = port_list['interfaces']
            for port in port_list:
                for k,v in port.items():
                    if v['alias'] == 'br0':
                        self.local_realm.rm_port(k, check_exists=True)
                        time.sleep(5)

        # create bridge
        data = {
            "shelf": 1,
            "resource": resource,
            "port": "br0",
            "network_devs": "eth1,%s" % self.vap_name
        }
        self.local_realm.json_post("cli-json/add_br", data)

        bridge_set_port = {
            "shelf": 1,
            "resource": 1,
            "port": "br0",
            "current_flags": 0x80000000,
            "interest": 0x4000  # (0x2 + 0x4000 + 0x800000)  # current, dhcp, down
        }
        self.local_realm.json_post("cli-json/set_port", bridge_set_port)



        if (self.up):
            self.admin_up(1)

    def cleanup(self, resource, delay=0.03):
        print("Cleaning up VAPs")
        desired_ports = ["1.%s.%s" % (resource, self.vap_name), "1.%s.br0" % resource]

        del_count = len(desired_ports)

        # First, request remove on the list.
        for port_eid in desired_ports:
            self.local_realm.rm_port(port_eid, check_exists=True)

        # And now see if they are gone
        LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=desired_ports)

class VRProfile(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port, local_realm, ssid="NA", ssid_pass="NA", mode=0, debug_=False):
        super().__init__(_lfjson_host=lfclient_host, _lfjson_port=lfclient_port, _debug=debug_)
        #self.debug = debug_
        # self.lfclient_url = lfclient_url
        self.ssid = ssid
        self.ssid_pass = ssid_pass
        self.mode = mode
        self.local_realm = local_realm
        self.vr_name = None

        self.created_rdds = []
        self.created_vrcxs = []

        self.add_vr_data = {
            "alias": None,
            "shelf": 1,
            "resource": 1,
            "x": 100,
            "y": 100,
            "width": 250,
            "height": 250,
            "flags": 0
        }

        self.vrcx_data = {
            'shelf': 1,
            'resource': 1,
            'vr-name': None,
            'local_dev': None, # outer rdd
            'remote_dev': None, # inner rdd
            "x": 0,
            "y": 0,
            "width": 10,
            "height": 10,
            'flags': 0,
            "subnets": None,
            "nexthop": None,
            "vrrp_ip": "0.0.0.0"
        }

        self.set_port_data = {
            "shelf": 1,
            "resource": 1,
            "port": None,
            "ip_addr": None,
            "netmask": None,
            "gateway": None
        }

    def create_rdd(self, resource, ip_addr, netmask, gateway, suppress_related_commands_=True, debug_=False):
        rdd_data = {
            "shelf": 1,
            "resource": resource,
            "port": "rdd0",
            "peer_ifname": "rdd1"
        }
        # print("creating rdd0")
        self.local_realm.json_post("add_rdd", rdd_data, suppress_related_commands_=suppress_related_commands_, debug_=debug_)

        rdd_data = {
            "shelf": 1,
            "resource": resource,
            "port": "rdd1",
            "peer_ifname": "rdd0"
        }
        # print("creating rdd1")
        self.local_realm.json_post("add_rdd", rdd_data, suppress_related_commands_=suppress_related_commands_, debug_=debug_)

        self.set_port_data["port"] = "rdd0"
        self.set_port_data["ip_addr"] = gateway
        self.set_port_data["netmask"] = netmask
        self.set_port_data["gateway"] = gateway
        self.local_realm.json_post("set_port", self.set_port_data, suppress_related_commands_=suppress_related_commands_, debug_=debug_)

        self.set_port_data["port"] = "rdd1"
        self.set_port_data["ip_addr"] = ip_addr
        self.set_port_data["netmask"] = netmask
        self.set_port_data["gateway"] = gateway
        self.local_realm.json_post("set_port", self.set_port_data, suppress_related_commands_=suppress_related_commands_, debug_=debug_)

        self.created_rdds.append("rdd0")
        self.created_rdds.append("rdd1")

    def create_vrcx(self, resource, local_dev, remote_dev, subnets, nexthop, flags, suppress_related_commands_=True, debug_=False):
        if self.vr_name is not None:
            self.vrcx_data["resource"] = resource
            self.vrcx_data["vr_name"] = self.vr_name
            self.vrcx_data["local_dev"] = local_dev
            self.vrcx_data["remote_dev"] = remote_dev
            self.vrcx_data["subnets"] = subnets
            self.vrcx_data["nexthop"] = nexthop
            self.vrcx_data["flags"] = flags
            self.local_realm.json_post("add_vrcx", self.vrcx_data, suppress_related_commands_=suppress_related_commands_, debug_=debug_)
        else:
            raise ValueError("vr_name must be set. Current name: %s" % self.vr_name)


    def create(self, resource, upstream_port="eth1", debug=False,
               upstream_subnets="20.20.20.0/24", upstream_nexthop="20.20.20.1",
               local_subnets="10.40.0.0/24", local_nexthop="10.40.3.198",
               rdd_ip="20.20.20.20", rdd_gateway="20.20.20.1", rdd_netmask="255.255.255.0",
               suppress_related_commands_=True):

        # Create vr
        if self.vr_name is not None:
            self.add_vr_data["alias"] = self.vr_name
            self.local_realm.json_post("add_vr", self.add_vr_data, debug_=debug)
        else:
            raise ValueError("vr_name must be set. Current name: %s" % self.vr_name)
        # Create 1 rdd pair
        self.create_rdd(resource=resource, ip_addr=rdd_ip, gateway=rdd_gateway, netmask=rdd_netmask)   # rdd0, rdd1; rdd0 gateway, rdd1 connected to network

        # connect rdds and upstream
        self.create_vrcx(resource=resource, local_dev=upstream_port, remote_dev="NA", subnets=upstream_subnets, nexthop=upstream_nexthop,
                         flags=257, suppress_related_commands_=suppress_related_commands_, debug_=debug)
        self.create_vrcx(resource=resource, local_dev="rdd0", remote_dev="rdd1", subnets=local_subnets, nexthop=local_nexthop,
                         flags=1, suppress_related_commands_=suppress_related_commands_, debug_=debug)

    def cleanup(self, resource, delay=0.03):
        # TODO: Cleanup for VRProfile
        pass

class DUTProfile(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port, local_realm, debug_=False):
        super().__init__(lfclient_host, lfclient_port, debug_, _halt_on_error=True, _local_realm=local_realm)
        self.name            = "NA"
        self.flags           = "NA"
        self.img_file        = "NA"
        self.sw_version      = "NA"
        self.hw_version      = "NA"
        self.model_num       = "NA"
        self.serial_num      = "NA"
        self.serial_port     = "NA"
        self.wan_port        = "NA"
        self.lan_port        = "NA"
        self.ssid1           = "NA"
        self.ssid2           = "NA"
        self.ssid3           = "NA"
        self.passwd1         = "NA"
        self.passwd2         = "NA"
        self.passwd3         = "NA"
        self.mgt_ip          = "NA"
        self.api_id          = "NA"
        self.flags_mask      = "NA"
        self.antenna_count1  = "NA"
        self.antenna_count2  = "NA"
        self.antenna_count3  = "NA"
        self.bssid1          = "NA"
        self.bssid2          = "NA"
        self.bssid3          = "NA"
        self.top_left_x      = "NA"
        self.top_left_y      = "NA"
        self.eap_id          = "NA"
        self.flags           = 0
        self.flags_mask      = 0
        self.notes           = []
        self.append          = []

    def set_param(self, name, value):
        if (name in self.__dict__):
            self.__dict__[name] = value

    def create(self, name=None, param_=None, flags=None, flags_mask=None, notes=None):
        data = {}
        if (name is not None) and (name != ""):
            data["name"] = name
        elif (self.name is not None) and (self.name != ""):
            data["name"] = self.name
        else:
            raise ValueError("cannot create/update DUT record lacking a name")

        for param in add_dut.dut_params:
            if (param.name in self.__dict__):
                if (self.__dict__[param.name] is not None) \
                    and (self.__dict__[param.name] != "NA"):
                    data[param.name] = self.__dict__[param.name]
            else:
                print("---------------------------------------------------------")
                pprint(self.__dict__[param.name])
                print("---------------------------------------------------------")
                raise ValueError("parameter %s not in dut_profile"%param)

        if (flags is not None) and (int(flags) > -1):
            data["flags"] = flags
        elif (self.flags is not None) and (self.flags > -1):
            data["flags"] = self.flags

        if (flags_mask is not None) and (int(flags_mask) > -1):
            data["flags_mask"] = flags_mask
        elif (self.flags_mask is not None) and (int(self.flags_mask) > -1):
            data["flags_mask"] = self.flags_mask

        url = "/cli-json/add_dut"
        if self.debug:
            print("---- DATA -----------------------------------------------")
            pprint(data)
            pprint(self.notes)
            pprint(self.append)
            print("---------------------------------------------------------")
        self.json_post(url, data, debug_=self.debug)

        if (self.notes is not None) and (len(self.notes)>0):
            self.json_post("/cli-json/add_dut_notes", {
                "dut": self.name,
                "text": "[BLANK]"
            }, self.debug)
            notebytes = None
            for line in self.notes:
                notebytes = base64.b64encode(line.encode('ascii'))
                if self.debug:
                    print("------ NOTES ---------------------------------------------------")
                    pprint(self.notes)
                    pprint(str(notebytes))
                    print("---------------------------------------------------------")
                self.json_post("/cli-json/add_dut_notes", {
                    "dut": self.name,
                    "text-64": notebytes.decode('ascii')
                }, self.debug)
        if (self.append is not None) and (len(self.append)>0):
            notebytes = None
            for line in self.append:
                notebytes = base64.b64encode(line.encode('ascii'))
                if self.debug:
                    print("----- APPEND ----------------------------------------------------")
                    pprint(line)
                    pprint(str(notebytes))
                    print("---------------------------------------------------------")
                self.json_post("/cli-json/add_dut_notes", {
                    "dut": self.name,
                    "text-64": notebytes.decode('ascii')
                }, self.debug)

class TestGroupProfile(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port, local_realm, test_group_name=None, debug_=False):
        super().__init__(lfclient_host, lfclient_port, debug_, _halt_on_error=True)
        self.local_realm = local_realm
        self.group_name = test_group_name
        self.cx_list = []

    def start_group(self):
        if self.group_name is not None:
            self.local_realm.json_post("/cli-json/start_group", {"name": self.group_name})
        else:
            raise ValueError("test_group name must be set.")

    def quiesce_group(self):
        if self.group_name is not None:
                self.local_realm.json_post("/cli-json/quiesce_group", {"name": self.group_name})
        else:
            raise ValueError("test_group name must be set.")

    def stop_group(self):
        if self.group_name is not None:
            self.local_realm.json_post("/cli-json/stop_group", {"name": self.group_name})
        else:
            raise ValueError("test_group name must be set.")

    def create_group(self):
        if self.group_name is not None:
            self.local_realm.json_post("/cli-json/add_group", {"name": self.group_name})
        else:
            raise ValueError("test_group name must be set.")

    def rm_group(self):
        if self.group_name is not None:
            self.local_realm.json_post("/cli-json/rm_group", {"name": self.group_name})
        else:
            raise ValueError("test_group name must be set.")

    def add_cx(self, cx_name):
        self.local_realm.json_post("/cli-json/add_tgcx", {"tgname": self.group_name, "cxname": cx_name})

    def rm_cx(self, cx_name):
        self.local_realm.json_post("/cli-json/rm_tgcx", {"tgname": self.group_name, "cxname": cx_name})

    def check_group_exists(self):
        test_groups = self.local_realm.json_get("/testgroups/all")
        if test_groups is not None and "groups" in test_groups:
            test_groups = test_groups["groups"]
            for group in test_groups:
                for k,v in group.items():
                    if v['name'] == self.group_name:
                        return True
        else:
            return False

    def list_groups(self):
        test_groups = self.local_realm.json_get("/testgroups/all")
        tg_list = []
        if test_groups is not None:
            test_groups = test_groups["groups"]
            for group in test_groups:
                for k, v in group.items():
                    tg_list.append(v['name'])
        return tg_list

    def list_cxs(self):
        test_groups = self.local_realm.json_get("/testgroups/all")
        if test_groups is not None:
            test_groups = test_groups["groups"]
            for group in test_groups:
                for k,v in group.items():
                    if v['name'] == self.group_name:
                        return v['cross connects']

        else:
            return []


class FIOEndpProfile(LFCliBase):
    """
    Very often you will create the FileIO writer profile first so that it creates the data
    that a reader profile will subsequently use.
    """
    def __init__(self, lfclient_host, lfclient_port, local_realm, io_direction="write", debug_=False):
        super().__init__(lfclient_host, lfclient_port, debug_, _halt_on_error=True)
        self.local_realm = local_realm
        self.fs_type = "fe_nfsv4"
        self.min_rw_size = 128 * 1024
        self.max_rw_size = 128 * 1024
        self.min_file_size = 10 * 1024 * 1024
        self.max_file_size = 10 * 1024 * 1024

        self.min_read_rate_bps = 10 * 1000 * 1000
        self.max_read_rate_bps = 10 * 1000 * 1000
        self.min_write_rate_bps = 1000 * 1000 * 1000
        self.max_write_rate_bps = 1000 * 1000 * 1000

        self.file_num = 10           # number of files to write
        self.directory = None       # directory like /mnt/lf/$endp_name

        # this refers to locally mounted directories presently used for writing
        # you would set this when doing read tests simultaneously to write tests
        # so like, if your endpoint names are like wo_300GB_001, your Directory value
        # defaults to /mnt/lf/wo_300GB_001; but reader enpoint would be named
        # /mnt/lf/ro_300GB_001, this overwrites a readers directory name to wo_300GB_001
        self.mount_dir = "AUTO"

        self.server_mount = None    # like cifs://10.0.0.1/bashful or 192.168.1.1:/var/tmp
        self.mount_options = None
        self.iscsi_vol = None
        self.retry_timer_ms = 2000
        self.io_direction = io_direction # read / write
        self.quiesce_ms = 3000
        self.pattern = "increasing"
        self.file_prefix = "AUTO" # defaults to endp_name
        self.cx_prefix = "wo_"

        self.created_cx = {}
        self.created_endp = []

    def start_cx(self):
        print("Starting CXs...")
        for cx_name in self.created_cx.keys():
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": self.created_cx[cx_name],
                "cx_state": "RUNNING"
            }, debug_=self.debug)
            print(".", end='')
        print("")

    def stop_cx(self):
        print("Stopping CXs...")
        for cx_name in self.created_cx.keys():
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": self.created_cx[cx_name],
                "cx_state": "STOPPED"
            }, debug_=self.debug)
            print(".", end='')
        print("")

    def create_ro_profile(self):
        ro_profile = self.local_realm.new_fio_endp_profile()
        ro_profile.realm = self.local_realm

        ro_profile.fs_type = self.fs_type
        ro_profile.min_read_rate_bps = self.min_write_rate_bps
        ro_profile.max_read_rate_bps = self.max_write_rate_bps
        ro_profile.min_write_rate_bps = self.min_read_rate_bps
        ro_profile.max_write_rate_bps = self.max_read_rate_bps
        ro_profile.file_num = self.file_num
        ro_profile.directory = self.directory
        ro_profile.mount_dir = self.directory
        ro_profile.server_mount = self.server_mount
        ro_profile.mount_options = self.mount_options
        ro_profile.iscsi_vol = self.iscsi_vol
        ro_profile.retry_timer_ms = self.retry_timer_ms
        ro_profile.io_direction = "read"
        ro_profile.quiesce_ms = self.quiesce_ms
        ro_profile.pattern = self.pattern
        ro_profile.file_prefix = self.file_prefix
        ro_profile.cx_prefix = "ro_"
        return ro_profile

    def cleanup(self):
        print("Cleaning up cxs and endpoints")
        if len(self.created_cx) != 0:
            for cx_name in self.created_cx.keys():
                req_url = "cli-json/rm_cx"
                data = {
                    "test_mgr": "default_tm",
                    "cx_name": self.created_cx[cx_name]
                }
                self.json_post(req_url, data)
                #pprint(data)
                req_url = "cli-json/rm_endp"
                data = {
                    "endp_name": cx_name
                }
                self.json_post(req_url, data)
                #pprint(data)

    def create(self, ports=[], connections_per_port=1, sleep_time=.5, debug_=False, suppress_related_commands_=None):
        cx_post_data = []
        for port_name in ports:
            for num_connection in range(connections_per_port):
                if len(self.local_realm.name_to_eid(port_name)) == 3:
                    shelf = self.local_realm.name_to_eid(port_name)[0]
                    resource = self.local_realm.name_to_eid(port_name)[1]
                    name = self.local_realm.name_to_eid(port_name)[2]
                else:
                    raise ValueError("Unexpected name for port_name %s" % port_name)
                if self.directory is None or self.server_mount is None or self.fs_type is None:
                    raise ValueError("directory [%s], server_mount [%s], and type [%s] must not be None" % (self.directory, self.server_mount, self.fs_type))
                endp_data = {
                    "alias": self.cx_prefix + name + "_" + str(num_connection) + "_fio" ,
                    "shelf": shelf,
                    "resource": resource,
                    "port": name,
                    "type": self.fs_type,
                    "min_read_rate": self.min_read_rate_bps,
                    "max_read_rate": self.max_read_rate_bps,
                    "min_write_rate": self.min_write_rate_bps,
                    "max_write_rate": self.max_write_rate_bps,
                    "directory": self.directory,
                    "server_mount": self.server_mount,
                    "mount_dir": self.mount_dir,
                    "prefix": self.file_prefix,
                    "payload_pattern": self.pattern,

                }
                # Read direction is copy of write only directory
                if self.io_direction == "read":
                    endp_data["prefix"] = "wo_" + name + "_" + str(num_connection) + "_fio"
                    endp_data["directory"] = "/mnt/lf/wo_" + name + "_" + str(num_connection) + "_fio"

                url = "cli-json/add_file_endp"
                self.local_realm.json_post(url, endp_data, debug_=False, suppress_related_commands_=suppress_related_commands_)
                time.sleep(sleep_time)

                data = {
                    "name": self.cx_prefix + name + "_" + str(num_connection) + "_fio" ,
                    "io_direction": self.io_direction,
                    "num_files": 5
                }
                self.local_realm.json_post("cli-json/set_fe_info", data, debug_=debug_,
                                           suppress_related_commands_=suppress_related_commands_)

        self.local_realm.json_post("/cli-json/nc_show_endpoints", {"endpoint": "all"})
        for port_name in ports:
            for num_connection in range(connections_per_port):
                if len(self.local_realm.name_to_eid(port_name)) == 3:
                    shelf = self.local_realm.name_to_eid(port_name)[0]
                    resource = self.local_realm.name_to_eid(port_name)[1]
                    name = self.local_realm.name_to_eid(port_name)[2]

                endp_data = {
                    "alias": "CX_" + self.cx_prefix + name + "_" + str(num_connection) + "_fio" ,
                    "test_mgr": "default_tm",
                    "tx_endp": self.cx_prefix + name + "_" + str(num_connection) + "_fio" ,
                    "rx_endp": "NA"
                }
                cx_post_data.append(endp_data)
                self.created_cx[self.cx_prefix + name + "_" + str(num_connection) + "_fio" ] = "CX_" + self.cx_prefix + name + "_" + str(num_connection) + "_fio"

        for cx_data in cx_post_data:
            url = "/cli-json/add_cx"
            self.local_realm.json_post(url, cx_data, debug_=debug_, suppress_related_commands_=suppress_related_commands_)
            time.sleep(sleep_time)


class MACVLANProfile(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port,
                 local_realm,
                 macvlan_parent="eth1",
                 num_macvlans=1,
                 admin_down=False,
                 dhcp=False,
                 debug_=False):
        super().__init__(lfclient_host, lfclient_port, debug_, _halt_on_error=True)
        self.local_realm = local_realm
        self.num_macvlans = num_macvlans
        self.macvlan_parent = macvlan_parent
        self.resource = 1
        self.shelf = 1
        self.desired_macvlans = []
        self.created_macvlans = []
        self.dhcp = dhcp
        self.netmask = None
        self.first_ip_addr = None
        self.gateway = None
        self.ip_list = []
        self.COMMANDS = ["set_port"]
        self.desired_set_port_cmd_flags = []
        self.desired_set_port_current_flags = [] # do not default down, "if_down"
        self.desired_set_port_interest_flags = ["current_flags"] # do not default down, "ifdown"
        self.set_port_data = {
            "shelf": 1,
            "resource": 1,
            "port": None,
            "current_flags": 0,
            "interest": 0,  # (0x2 + 0x4000 + 0x800000)  # current, dhcp, down,
        }

    def add_named_flags(self, desired_list, command_ref):
        if desired_list is None:
            raise ValueError("addNamedFlags wants a list of desired flag names")
        if len(desired_list) < 1:
            print("addNamedFlags: empty desired list")
            return 0
        if (command_ref is None) or (len(command_ref) < 1):
            raise ValueError("addNamedFlags wants a maps of flag values")

        result = 0
        for name in desired_list:
            if (name is None) or (name == ""):
                continue
            if name not in command_ref:
                if self.debug:
                    pprint(command_ref)
                raise ValueError("flag %s not in map" % name)
            result += command_ref[name]

        return result

    def set_command_param(self, command_name, param_name, param_value):
        # we have to check what the param name is
        if (command_name is None) or (command_name == ""):
            return
        if (param_name is None) or (param_name == ""):
            return
        if command_name not in self.COMMANDS:
            raise ValueError("Command name name [%s] not defined in %s" % (command_name, self.COMMANDS))
            # return
        if command_name == "set_port":
            self.set_port_data[param_name] = param_value

    def set_command_flag(self, command_name, param_name, value):
        # we have to check what the param name is
        if (command_name is None) or (command_name == ""):
            return
        if (param_name is None) or (param_name == ""):
            return
        if command_name not in self.COMMANDS:
            print("Command name name [%s] not defined in %s" % (command_name, self.COMMANDS))
            return

        elif command_name == "set_port":
            if (param_name not in set_port.set_port_current_flags) and (
                    param_name not in set_port.set_port_cmd_flags) and (
                    param_name not in set_port.set_port_interest_flags):
                print("Parameter name [%s] not defined in set_port.py" % param_name)
                if self.debug:
                    pprint(set_port.set_port_cmd_flags)
                    pprint(set_port.set_port_current_flags)
                    pprint(set_port.set_port_interest_flags)
                return
            if (param_name in set_port.set_port_cmd_flags):
                if (value == 1) and (param_name not in self.desired_set_port_cmd_flags):
                    self.desired_set_port_cmd_flags.append(param_name)
                elif value == 0:
                    self.desired_set_port_cmd_flags.remove(param_name)
            elif (param_name in set_port.set_port_current_flags):
                if (value == 1) and (param_name not in self.desired_set_port_current_flags):
                    self.desired_set_port_current_flags.append(param_name)
                elif value == 0:
                    self.desired_set_port_current_flags.remove(param_name)
            elif (param_name in set_port.set_port_interest_flags):
                if (value == 1) and (param_name not in self.desired_set_port_interest_flags):
                    self.desired_set_port_interest_flags.append(param_name)
                elif value == 0:
                    self.desired_set_port_interest_flags.remove(param_name)
            else:
                raise ValueError("Unknown param name: " + param_name)

    def create(self, admin_down=False, debug=False, sleep_time=1):
        print("Creating MACVLANs...")
        req_url = "/cli-json/add_mvlan"

        if not self.dhcp and self.first_ip_addr is not None and self.netmask is not None and self.gateway is not None:
            self.desired_set_port_interest_flags.append("ip_address")
            self.desired_set_port_interest_flags.append("ip_Mask")
            self.desired_set_port_interest_flags.append("ip_gateway")
            self.ip_list = LFUtils.gen_ip_series(ip_addr=self.first_ip_addr, netmask=self.netmask, num_ips=self.num_macvlans)

        self.set_port_data["current_flags"] = self.add_named_flags(self.desired_set_port_current_flags,
                                                                   set_port.set_port_current_flags)
        self.set_port_data["interest"] = self.add_named_flags(self.desired_set_port_interest_flags,
                                                              set_port.set_port_interest_flags)
        set_port_r = LFRequest.LFRequest(self.lfclient_url + "/cli-json/set_port")

        if self.dhcp:
            print("Using DHCP")
            self.desired_set_port_current_flags.append("use_dhcp")
            self.desired_set_port_interest_flags.append("dhcp")

        for i in range(len(self.desired_macvlans)):
            data = {
                "shelf": self.shelf,
                "resource": self.resource,
                "mac": "xx:xx:xx:*:*:xx",
                "port": self.local_realm.name_to_eid(self.macvlan_parent)[2],
                "index": int(self.desired_macvlans[i][self.desired_macvlans[i].index('#')+1:]),
                "flags": None
            }
            if admin_down:
                data["flags"] = 1
            else:
                data["flags"] = 0
            self.created_macvlans.append("%s.%s.%s#%d" % (self.shelf, self.resource,
                                                          self.macvlan_parent, int(self.desired_macvlans[i][self.desired_macvlans[i].index('#')+1:])))
            self.local_realm.json_post(req_url, data)
            time.sleep(sleep_time)

        LFUtils.wait_until_ports_appear(base_url=self.lfclient_url,  port_list=self.created_macvlans)
        print(self.created_macvlans)

        time.sleep(5)

        for i in range(len(self.created_macvlans)):
            eid = self.local_realm.name_to_eid(self.created_macvlans[i])
            name = eid[2]
            self.set_port_data["port"] = name  # for set_port calls.
            if not self.dhcp and self.first_ip_addr is not None and self.netmask is not None \
                    and self.gateway is not None:
                self.set_port_data["ip_addr"] = self.ip_list[i]
                self.set_port_data["netmask"] = self.netmask
                self.set_port_data["gateway"] = self.gateway
            set_port_r.addPostData(self.set_port_data)
            json_response = set_port_r.jsonPost(debug)
            time.sleep(sleep_time)

    def cleanup(self):
        print("Cleaning up MACVLANs...")
        print(self.created_macvlans)
        for port_eid in self.created_macvlans:
            self.local_realm.rm_port(port_eid, check_exists=True)
            time.sleep(.2)
        # And now see if they are gone


    def admin_up(self):
        for macvlan in self.created_macvlans:
            self.local_realm.admin_up(macvlan)

    def admin_down(self):
        for macvlan in self.created_macvlans:
            self.local_realm.admin_down(macvlan)

class PacketFilter():

    def get_filter_wlan_assoc_packets(self, ap_mac, sta_mac):
        filter = "-T fields -e wlan.fc.type_subtype -e wlan.addr -e wlan.fc.pwrmgt " \
                 "-Y \"(wlan.addr==%s or wlan.addr==%s) and wlan.fc.type_subtype<=3\" " % (ap_mac, sta_mac)
        return filter

    def get_filter_wlan_null_packets(self, ap_mac, sta_mac):
        filter = "-T fields -e wlan.fc.type_subtype -e wlan.addr -e wlan.fc.pwrmgt " \
                 "-Y \"(wlan.addr==%s or wlan.addr==%s) and wlan.fc.type_subtype==44\" " % (ap_mac, sta_mac)
        return filter

    def run_filter(self, pcap_file, filter):
        filename = "/tmp/tshark_dump.txt"
        cmd = "tshark -r %s %s > %s" % (pcap_file, filter, filename)
        # print("CMD: ", cmd)
        os.system(cmd)
        lines = []
        with open(filename) as tshark_file:
            for line in tshark_file:
                lines.append(line.rstrip())

        return lines

class PortUtils():
    def __init__(self, local_realm):
        self.local_realm = local_realm

    def set_ftp(self, port_name="", resource=1, on=False):
        if port_name != "":
            data = {
                "shelf": 1,
                "resource": resource,
                "port": port_name,
                "current_flags": 0,
                "interest": 0
            }

            if on:
                data["current_flags"] = 0x400000000000
                data["interest"] = 0x10000000
            else:
                data["interest"] = 0x10000000

            self.local_realm.json_post("cli-json/set_port", data)
        else:
            raise ValueError("Port name required")

    def set_http(self, port_name="", resource=1, on=False):
        if port_name != "":
            data = {
                "shelf": 1,
                "resource": resource,
                "port": port_name,
                "current_flags": 0,
                "interest": 0
            }

            if on:
                data["current_flags"] = 0x200000000000
                data["interest"] = 0x8000000
            else:
                data["interest"] = 0x8000000

            self.local_realm.json_post("cli-json/set_port", data)
        else:
            raise ValueError("Port name required")

class HTTPProfile(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port, local_realm, debug_=False):
        super().__init__(lfclient_host, lfclient_port, debug_, _halt_on_error=True)
        self.lfclient_url = "http://%s:%s" % (lfclient_host, lfclient_port)
        self.debug = debug_
        self.requests_per_ten = 600
        self.local_realm = local_realm
        self.created_cx = {}
        self.created_endp = []
        self.ip_map = {}
        self.direction = "dl"
        self.dest = "/dev/null"
        self.port_util = PortUtils(self.local_realm)

    def check_errors(self, debug=False):
        fields_list = ["!conn", "acc.+denied", "bad-proto", "bad-url", "other-err", "total-err", "rslv-p", "rslv-h",
                       "timeout", "nf+(4xx)", "http-r", "http-p", "http-t", "login-denied"]
        endp_list = self.json_get("layer4/list?fields=%s" % ','.join(fields_list))
        debug_info = {}
        if endp_list is not None and endp_list['endpoint'] is not None:
            endp_list = endp_list['endpoint']
            expected_passes = len(endp_list)
            passes = len(endp_list)
            for item in range(len(endp_list)):
                for name, info in endp_list[item].items():
                    for field in fields_list:
                        if info[field.replace("+", " ")] > 0:
                            passes -= 1
                            debug_info[name] = {field: info[field.replace("+", " ")]}
            if debug:
                print(debug_info)
            if passes == expected_passes:
                return True
            else:
                print(list(debug_info), " Endps in this list showed errors getting to its URL") #   %s") % self.url)
                return False

    def start_cx(self):
        print("Starting CXs...")
        for cx_name in self.created_cx.keys():
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": self.created_cx[cx_name],
                "cx_state": "RUNNING"
            }, debug_=self.debug)
            print(".", end='')
        print("")

    def stop_cx(self):
        print("Stopping CXs...")
        for cx_name in self.created_cx.keys():
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": self.created_cx[cx_name],
                "cx_state": "STOPPED"
            }, debug_=self.debug)
            print(".", end='')
        print("")

    def cleanup(self):
        print("Cleaning up cxs and endpoints")
        if len(self.created_cx) != 0:
            for cx_name in self.created_cx.keys():
                req_url = "cli-json/rm_cx"
                data = {
                    "test_mgr": "default_tm",
                    "cx_name": self.created_cx[cx_name]
                }
                self.json_post(req_url, data)
                #pprint(data)
                req_url = "cli-json/rm_endp"
                data = {
                    "endp_name": cx_name
                }
                self.json_post(req_url, data)
                #pprint(data)

    def map_sta_ips(self, sta_list=[]):
        for sta_eid in sta_list:
            eid = self.local_realm.name_to_eid(sta_eid)
            sta_list = self.json_get("/port/%s/%s/%s?fields=alias,ip" %
                                        (eid[0], eid[1], eid[2]))
            if sta_list['interface'] is not None:
                self.ip_map[sta_list['interface']['alias']] = sta_list['interface']['ip']

    def create(self, ports=[], sleep_time=.5, debug_=False, suppress_related_commands_=None, http=False, ftp=False,
               user=None, passwd=None, source=None):
        cx_post_data = []
        self.map_sta_ips(ports)
        for i in range(len(list(self.ip_map))):
            url = None
            if i != len(list(self.ip_map)) - 1:
                port_name = list(self.ip_map)[i]
                ip_addr = self.ip_map[list(self.ip_map)[i+1]]
            else:
                port_name = list(self.ip_map)[i]
                ip_addr = self.ip_map[list(self.ip_map)[0]]

            if (ip_addr is None) or (ip_addr == ""):
                raise ValueError("HTTPProfile::create encountered blank ip/hostname")

            if len(self.local_realm.name_to_eid(port_name)) == 3:
                shelf = self.local_realm.name_to_eid(port_name)[0]
                resource = self.local_realm.name_to_eid(port_name)[1]
                name = self.local_realm.name_to_eid(port_name)[2]
            else:
                raise ValueError("Unexpected name for port_name %s" % port_name)

            if http:
                self.port_util.set_http(port_name=name, resource=resource, on=True)
                url = "%s http://%s/ %s" % (self.direction, ip_addr, self.dest)
            if ftp:
                self.port_util.set_ftp(port_name=name, resource=resource, on=True)
                if user is not None and passwd is not None and source is not None:
                    url = "%s ftp://%s:%s@%s%s %s" % (self.direction, user, passwd,  ip_addr, source, self.dest)
                else:
                    raise ValueError("user: %s, passwd: %s, and source: %s must all be set" % (user, passwd, source))
            if not http and not ftp:
                raise ValueError("Please specify ftp and/or http")

            if (url is None) or (url == ""):
                raise ValueError("HTTPProfile::create: url unset")

            endp_data = {
                "alias": name + "_l4",
                "shelf": shelf,
                "resource": resource,
                "port": name,
                "type": "l4_generic",
                "timeout": 10,
                "url_rate": self.requests_per_ten,
                "url": url,
                "proxy_auth_type": 0x200
            }
            url = "cli-json/add_l4_endp"
            self.local_realm.json_post(url, endp_data, debug_=debug_, suppress_related_commands_=suppress_related_commands_)
            time.sleep(sleep_time)

            endp_data = {
                "alias": "CX_" + name + "_l4",
                "test_mgr": "default_tm",
                "tx_endp": name + "_l4",
                "rx_endp": "NA"
            }
            cx_post_data.append(endp_data)
            self.created_cx[name + "_l4"] = "CX_" + name + "_l4"

        for cx_data in cx_post_data:
            url = "/cli-json/add_cx"
            self.local_realm.json_post(url, cx_data, debug_=debug_, suppress_related_commands_=suppress_related_commands_)
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
    def __init__(self, lfclient_url, local_realm,
                 ssid="NA",
                 ssid_pass="NA",
                 security="open",
                 number_template_="00000",
                 mode=0,
                 up=True,
                 resource=1,
                 shelf=1,
                 dhcp=True,
                 debug_=False,
                 use_ht160=False):
        self.debug = debug_
        self.lfclient_url = lfclient_url
        self.ssid = ssid
        self.ssid_pass = ssid_pass
        self.mode = mode
        self.up = up
        self.resource=resource
        self.shelf=shelf
        self.dhcp = dhcp
        self.security = security
        self.local_realm = local_realm
        self.use_ht160 = use_ht160
        self.COMMANDS = ["add_sta", "set_port"]
        self.desired_add_sta_flags      = ["wpa2_enable", "80211u_enable", "create_admin_down"]
        self.desired_add_sta_flags_mask = ["wpa2_enable", "80211u_enable", "create_admin_down"]
        self.number_template = number_template_
        self.station_names = []  # eids, these are created station names
        self.add_sta_data = {
            "shelf": 1,
            "resource": 1,
            "radio": None,
            "sta_name": None,
            "ssid": None,
            "key": None,
            "mode": 0,
            "mac": "xx:xx:xx:xx:*:xx",
            "flags": 0,  # (0x400 + 0x20000 + 0x1000000000)  # create admin down
        }
        self.desired_set_port_cmd_flags = []
        self.desired_set_port_current_flags = ["if_down"]
        self.desired_set_port_interest_flags = ["current_flags", "ifdown"]
        if self.dhcp:
            self.desired_set_port_current_flags.append("use_dhcp")
            self.desired_set_port_interest_flags.append("dhcp")

        self.set_port_data = {
            "shelf": 1,
            "resource": 1,
            "port": None,
            "current_flags": 0,
            "interest": 0,  # (0x2 + 0x4000 + 0x800000)  # current, dhcp, down,
        }
        self.wifi_extra_data_modified = False
        self.wifi_extra_data = {
            "shelf": 1,
            "resource": 1,
            "port": None,
            "key_mgmt": None,
            "eap": None,
            "hessid": None,
            "identity": None,
            "password": None,
            "realm": None,
            "domain": None
        }

        self.reset_port_extra_data = {
            "shelf": 1,
            "resource": 1,
            "port": None,
            "test_duration": 0,
            "reset_port_enable": False,
            "reset_port_time_min": 0,
            "reset_port_time_max": 0,
            "reset_port_timer_started": False,
            "port_to_reset": 0,
            "seconds_till_reset": 0
        }

    def set_wifi_extra(self, key_mgmt="WPA-EAP",
                       pairwise="CCMP TKIP",
                       group="CCMP TKIP",
                       psk="[BLANK]",
                       wep_key="[BLANK]",  #wep key
                       ca_cert="[BLANK]",
                       eap="TTLS",
                       identity="testuser",
                       anonymous_identity="[BLANK]",
                       phase1="NA",  # outter auth
                       phase2="NA",  # inner auth
                       passwd="testpasswd",  # eap passphrase
                       pin="NA",
                       pac_file="NA",
                       private_key="NA",
                       pk_password="NA",  # priv key password
                       hessid="00:00:00:00:00:01",
                       realm="localhost.localdomain",
                       client_cert="NA",
                       imsi="NA",
                       milenage="NA",
                       domain="localhost.localdomain",
                       roaming_consortium="NA",
                       venue_group="NA",
                       network_type="NA",
                       ipaddr_type_avail="NA",
                       network_auth_type="NA",
                       anqp_3gpp_cell_net="NA"
                       ):
        self.wifi_extra_data_modified = True
        self.wifi_extra_data["key_mgmt"] = key_mgmt
        self.wifi_extra_data["pairwise"] = pairwise
        self.wifi_extra_data["group"] = group
        self.wifi_extra_data["psk"] = psk
        self.wifi_extra_data["key"] = wep_key
        self.wifi_extra_data["ca_cert"] = ca_cert
        self.wifi_extra_data["eap"] = eap
        self.wifi_extra_data["identity"] = identity
        self.wifi_extra_data["anonymous_identity"] = anonymous_identity
        self.wifi_extra_data["phase1"] = phase1
        self.wifi_extra_data["phase2"] = phase2
        self.wifi_extra_data["password"] = passwd
        self.wifi_extra_data["pin"] = pin
        self.wifi_extra_data["pac_file"] = pac_file
        self.wifi_extra_data["private_key"] = private_key
        self.wifi_extra_data["pk_passwd"] = pk_password
        self.wifi_extra_data["hessid"] = hessid
        self.wifi_extra_data["realm"] = realm
        self.wifi_extra_data["client_cert"] = client_cert
        self.wifi_extra_data["imsi"] = imsi
        self.wifi_extra_data["milenage"] = milenage
        self.wifi_extra_data["domain"] = domain
        self.wifi_extra_data["roaming_consortium"] = roaming_consortium
        self.wifi_extra_data["venue_group"] = venue_group
        self.wifi_extra_data["network_type"] = network_type
        self.wifi_extra_data["ipaddr_type_avail"] = ipaddr_type_avail
        self.wifi_extra_data["network_auth_type"] = network_auth_type
        self.wifi_extra_data["anqp_3gpp_cell_net"] = anqp_3gpp_cell_net

    def set_reset_extra(self, reset_port_enable=False, test_duration=0, reset_port_min_time=0, reset_port_max_time=0,
                        reset_port_timer_start=False, port_to_reset=0, time_till_reset=0):
        self.reset_port_extra_data["reset_port_enable"] = reset_port_enable
        self.reset_port_extra_data["test_duration"] = test_duration
        self.reset_port_extra_data["reset_port_time_min"] = reset_port_min_time
        self.reset_port_extra_data["reset_port_time_max"] = reset_port_max_time

    def use_security(self, security_type, ssid=None, passwd=None):
        types = {"wep": "wep_enable", "wpa": "wpa_enable", "wpa2": "wpa2_enable", "wpa3": "use-wpa3", "open": "[BLANK]"}
        self.add_sta_data["ssid"] = ssid
        if security_type in types.keys():
            if (ssid is None) or (ssid == ""):
                raise ValueError("use_security: %s requires ssid" % security_type)
            if (passwd is None) or (passwd == ""):
                raise ValueError("use_security: %s requires passphrase or [BLANK]" % security_type)
            for name in types.values():
                if name in self.desired_add_sta_flags and name in self.desired_add_sta_flags_mask:
                    self.desired_add_sta_flags.remove(name)
                    self.desired_add_sta_flags_mask.remove(name)
            if security_type != "open":
                self.desired_add_sta_flags.append(types[security_type])
                #self.set_command_flag("add_sta", types[security_type], 1)
                self.desired_add_sta_flags_mask.append(types[security_type])
            else:
                passwd = "[BLANK]"
            self.set_command_param("add_sta", "ssid", ssid)
            self.set_command_param("add_sta", "key", passwd)
            # unset any other security flag before setting our present flags
            if security_type == "wpa3":
                self.set_command_param("add_sta", "ieee80211w", 2)

            #self.add_sta_data["key"] = passwd

    def set_command_param(self, command_name, param_name, param_value):
        # we have to check what the param name is
        if (command_name is None) or (command_name == ""):
            return
        if (param_name is None) or (param_name == ""):
            return
        if command_name not in self.COMMANDS:
            raise ValueError("Command name name [%s] not defined in %s" % (command_name, self.COMMANDS))
            # return
        if command_name == "add_sta":
            self.add_sta_data[param_name] = param_value
        elif command_name == "set_port":
            self.set_port_data[param_name] = param_value

    def set_command_flag(self, command_name, param_name, value):
        # we have to check what the param name is
        if (command_name is None) or (command_name == ""):
            return
        if (param_name is None) or (param_name == ""):
            return
        if command_name not in self.COMMANDS:
            print("Command name name [%s] not defined in %s" % (command_name, self.COMMANDS))
            return
        if command_name == "add_sta":
            if (param_name not in add_sta.add_sta_flags) and (param_name not in add_sta.add_sta_modes):
                print("Parameter name [%s] not defined in add_sta.py" % param_name)
                if self.debug:
                    pprint(add_sta.add_sta_flags)
                return
            if (value == 1) and (param_name not in self.desired_add_sta_flags):
                self.desired_add_sta_flags.append(param_name)
                self.desired_add_sta_flags_mask.append(param_name)
            elif value == 0:
                self.desired_add_sta_flags.remove(param_name)
                self.desired_add_sta_flags_mask.append(param_name)

        elif command_name == "set_port":
            if (param_name not in set_port.set_port_current_flags) and (param_name not in set_port.set_port_cmd_flags) and (param_name not in set_port.set_port_interest_flags):
                print("Parameter name [%s] not defined in set_port.py" % param_name)
                if self.debug:
                    pprint(set_port.set_port_cmd_flags)
                    pprint(set_port.set_port_current_flags)
                    pprint(set_port.set_port_interest_flags)
                return
            if (param_name in set_port.set_port_cmd_flags):
                if (value == 1) and (param_name not in self.desired_set_port_cmd_flags):
                    self.desired_set_port_cmd_flags.append(param_name)
                elif value == 0:
                    self.desired_set_port_cmd_flags.remove(param_name)
            elif (param_name in set_port.set_port_current_flags):
                if (value == 1) and (param_name not in self.desired_set_port_current_flags):
                    self.desired_set_port_current_flags.append(param_name)
                elif value == 0:
                    self.desired_set_port_current_flags.remove(param_name)
            elif (param_name in set_port.set_port_interest_flags):
                if (value == 1) and (param_name not in self.desired_set_port_interest_flags):
                    self.desired_set_port_interest_flags.append(param_name)
                elif value == 0:
                    self.desired_set_port_interest_flags.remove(param_name)
            else:
                raise ValueError("Unknown param name: "+param_name)
    # use this for hinting station name; stations begin with 'sta', the
    # stations created with a prefix '0100' indicate value 10100 + n with
    # resulting substring(1,) applied; station 900 becomes 'sta1000'
    def set_number_template(self, pref):
        self.number_template = pref

    def add_named_flags(self, desired_list, command_ref):
        if desired_list is None:
            raise ValueError("addNamedFlags wants a list of desired flag names")
        if len(desired_list) < 1:
            print("addNamedFlags: empty desired list")
            return 0
        if (command_ref is None) or (len(command_ref) < 1):
            raise ValueError("addNamedFlags wants a maps of flag values")

        result = 0
        for name in desired_list:
            if (name is None) or (name == ""):
                continue
            if name not in command_ref:
                if self.debug:
                    pprint(command_ref)
                raise ValueError("flag %s not in map" % name)
            result += command_ref[name]

        return result

    def admin_up(self):
        for eid in self.station_names:
            # print("3139: admin_up sta "+eid)
            # time.sleep(2)
            self.local_realm.admin_up(eid)
            time.sleep(0.005)

    def admin_down(self):
        for sta_name in self.station_names:
            self.local_realm.admin_down(sta_name)

    def cleanup(self, desired_stations=None, delay=0.03, debug_=False):
        print("Cleaning up stations")

        if (desired_stations is None):
            desired_stations = self.station_names

        if len(desired_stations) < 1:
            print("ERROR:  StationProfile cleanup, list is empty")
            return

        # First, request remove on the list.
        for port_eid in desired_stations:
            self.local_realm.rm_port(port_eid, check_exists=True, debug_=debug_)

        # And now see if they are gone
        LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url,  port_list=desired_stations)


    # Checks for errors in initialization values and creates specified number of stations using init parameters
    def create(self, radio,
               num_stations=0,
               sta_names_=None,
               dry_run=False,
               up_=None,
               debug=False,
               suppress_related_commands_=True,
               use_radius=False,
               hs20_enable=False,
               sleep_time=0.02):
        if (radio is None) or (radio == ""):
            raise ValueError("station_profile.create: will not create stations without radio")
        radio_eid = self.local_realm.name_to_eid(radio)
        radio_shelf = radio_eid[0]
        radio_resource = radio_eid[1]
        radio_port = radio_eid[2]

        if self.use_ht160:
            self.desired_add_sta_flags.append("ht160_enable")
            self.desired_add_sta_flags_mask.append("ht160_enable")
        if self.mode is not None:
            self.add_sta_data["mode"] = self.mode
        if use_radius:
            self.desired_add_sta_flags.append("8021x_radius")
            self.desired_add_sta_flags_mask.append("8021x_radius")
        if hs20_enable:
            self.desired_add_sta_flags.append("hs20_enable")
            self.desired_add_sta_flags_mask.append("hs20_enable")
        if up_ is not None:
            self.up = up_

        if (sta_names_ is None) and (num_stations == 0):
            raise ValueError("StationProfile.create needs either num_stations= or sta_names_= specified")

        if self.up:
            if "create_admin_down" in self.desired_add_sta_flags:
                del self.desired_add_sta_flags[self.desired_add_sta_flags.index("create_admin_down")]
        elif "create_admin_down" not in self.desired_add_sta_flags:
            self.desired_add_sta_flags.append("create_admin_down")

        # create stations down, do set_port on them, then set stations up
        self.add_sta_data["flags"]      = self.add_named_flags(self.desired_add_sta_flags,      add_sta.add_sta_flags)
        self.add_sta_data["flags_mask"] = self.add_named_flags(self.desired_add_sta_flags_mask, add_sta.add_sta_flags)
        self.add_sta_data["radio"] = radio_port

        self.add_sta_data["resource"] = radio_resource
        self.add_sta_data["shelf"] = radio_shelf
        self.set_port_data["resource"] = radio_resource
        self.set_port_data["shelf"] = radio_shelf
        self.set_port_data["current_flags"] = self.add_named_flags(self.desired_set_port_current_flags,
                                                                   set_port.set_port_current_flags)
        self.set_port_data["interest"] = self.add_named_flags(self.desired_set_port_interest_flags,
                                                              set_port.set_port_interest_flags)
        self.wifi_extra_data["resource"] = radio_resource
        self.wifi_extra_data["shelf"] = radio_shelf
        self.reset_port_extra_data["resource"] = radio_resource
        self.reset_port_extra_data["shelf"] = radio_shelf

        # these are unactivated LFRequest objects that we can modify and
        # re-use inside a loop, reducing the number of object creations
        add_sta_r = LFRequest.LFRequest(self.lfclient_url + "/cli-json/add_sta", debug_=debug)
        set_port_r = LFRequest.LFRequest(self.lfclient_url + "/cli-json/set_port",debug_=debug)
        wifi_extra_r = LFRequest.LFRequest(self.lfclient_url + "/cli-json/set_wifi_extra",debug_=debug)
        my_sta_names = []
        #add radio here
        if (num_stations > 0) and (len(sta_names_) < 1):
            #print("CREATING MORE STA NAMES == == == == == == == == == == == == == == == == == == == == == == == ==")
            my_sta_names = LFUtils.portNameSeries("sta", 0, num_stations - 1, int("1" + self.number_template))
            #print("CREATING MORE STA NAMES == == == == == == == == == == == == == == == == == == == == == == == ==")
        else:
            my_sta_names = sta_names_

        if (len(my_sta_names) >= 15) or (suppress_related_commands_ == True):
            self.add_sta_data["suppress_preexec_cli"] = "yes"
            self.add_sta_data["suppress_preexec_method"] = 1
            self.set_port_data["suppress_preexec_cli"] = "yes"
            self.set_port_data["suppress_preexec_method"] = 1

        num = 0
        if debug:
            print("== == Created STA names == == == == == == == == == == == == == == == == == == == == == == == ==")
            pprint(self.station_names)
            print("== == vs Pending STA names == ==")
            pprint(my_sta_names)
            print("== == == == == == == == == == == == == == == == == == == == == == == == == ==")

        # track the names of stations in case we have stations added multiple times
        finished_sta = []

        for eidn in my_sta_names:
            if eidn in self.station_names:
                print("Station %s already created, skipping." % eidn)
                continue

            # print (" EIDN "+eidn);
            if eidn in finished_sta:
                # pprint(my_sta_names)
                # raise ValueError("************ duplicate ****************** "+eidn)
                if self.debug:
                    print("Station %s already created" % eidn)
                continue

            eid = self.local_realm.name_to_eid(eidn)
            name = eid[2]
            num += 1
            self.add_sta_data["shelf"] = radio_shelf
            self.add_sta_data["resource"] = radio_resource
            self.add_sta_data["radio"] = radio_port
            self.add_sta_data["sta_name"] = name # for create station calls
            self.set_port_data["port"] = name  # for set_port calls.
            self.set_port_data["shelf"] = radio_shelf
            self.set_port_data["resource"] = radio_resource

            add_sta_r.addPostData(self.add_sta_data)
            if debug:
                print("- 3254 - %s- - - - - - - - - - - - - - - - - - " % eidn)
                pprint(add_sta_r.requested_url)
                pprint(add_sta_r.proxies)
                pprint(self.add_sta_data)
                pprint(self.set_port_data)
                print("- ~3254 - - - - - - - - - - - - - - - - - - - ")
            if dry_run:
                print("dry run: not creating "+eidn)
                continue

            # print("- 3264 - ## %s ##  add_sta_r.jsonPost - - - - - - - - - - - - - - - - - - "%eidn)
            json_response = add_sta_r.jsonPost(debug=self.debug)
            finished_sta.append(eidn)
            # print("- ~3264 - %s - add_sta_r.jsonPost - - - - - - - - - - - - - - - - - - "%eidn)
            time.sleep(0.01)
            set_port_r.addPostData(self.set_port_data)
            #print("- 3270 -- %s --  set_port_r.jsonPost - - - - - - - - - - - - - - - - - - "%eidn)
            json_response = set_port_r.jsonPost(debug)
            #print("- ~3270 - %s - set_port_r.jsonPost - - - - - - - - - - - - - - - - - - "%eidn)
            time.sleep(0.01)

            self.wifi_extra_data["resource"] = radio_resource
            self.wifi_extra_data["port"] = name
            if self.wifi_extra_data_modified:
                wifi_extra_r.addPostData(self.wifi_extra_data)
                json_response = wifi_extra_r.jsonPost(debug)

            # append created stations to self.station_names
            self.station_names.append("%s.%s.%s" % (radio_shelf, radio_resource, name))
            time.sleep(sleep_time)

        #print("- ~3287 - waitUntilPortsAppear - - - - - - - - - - - - - - - - - - "%eidn)
        LFUtils.wait_until_ports_appear(self.lfclient_url, my_sta_names)

        # and set ports up
        if dry_run:
            return
        if (self.up):
            self.admin_up()

        # for sta_name in self.station_names:
        #     req = LFUtils.portUpRequest(resource, sta_name, debug_on=False)
        #     set_port_r.addPostData(req)
        #     json_response = set_port_r.jsonPost(debug)
        #     time.sleep(0.03)
        if self.debug:
            print("created %s stations" % num)

#
