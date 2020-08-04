#!/usr/bin/env python3
import re
import time
import pprint
from pprint import pprint
from LANforge import LFRequest
from LANforge import LFUtils
from LANforge import set_port
from LANforge import add_sta
from LANforge import lfcli_base
from LANforge import add_vap
from LANforge.lfcli_base import LFCliBase
from generic_cx import GenericCx
from LANforge import add_monitor
from LANforge.add_monitor import *
import datetime


class Realm(LFCliBase):
    def __init__(self, lfclient_host="localhost", lfclient_port=8080, debug_=False, halt_on_error_=False):
        super().__init__(_lfjson_host=lfclient_host, _lfjson_port=lfclient_port, _debug=debug_, _halt_on_error=halt_on_error_)
        # self.lfclient_url = "http://%s:%s" % (lfclient_host, lfclient_port)
        self.debug = debug_
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

    def wait_until_ports_appear(self, resource_=1, sta_list=None, debug_=False):
        if (sta_list is None) or (len(sta_list) < 1):
            print("realm.wait_until_ports_appear: no stations provided")
            return
        LFUtils.wait_until_ports_appear(resource_id=resource_,
                                        base_url=self.lfclient_url,
                                        port_list=sta_list,
                                        debug=debug_)

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
        self.json_post("/cli-json/load", debug_=self.debug)
        time.sleep(1)

    # Returns json response from webpage of all layer 3 cross connects
    def cx_list(self):
        response = super().json_get("/cx")
        return response

    # Returns map of all stations with port+type == WIFI-STATION
    def station_map(self):
        response = super().json_get("/port/list?fields=_links,alias,device,port+type")
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
        info = []
        if (eid is None) or (eid == "") or ('.' not in eid):
            raise ValueError("name_to_eid wants eid like 1.1.sta0 but given[%s]" % eid)

        info = eid.split('.')
        info[0] = int(info[0])
        if len(info) == 3:
            info[1] = int(info[1])
            return info
        return [1, int(info[0]), info[1]]

    def wait_for_ip(self, resource=1, station_list=None, ipv6=False, timeout_sec=60):
        num_ports = 0
        num_ips = 0
        print("Waiting for ips...")
        if (station_list is None) or (len(station_list) < 1):
            raise ValueError("wait_for_ip: expects non-empty list of ports")
        response = super().json_get("/port/1/%s/%s?fields=alias,ip,port+type" % (resource, ",".join(station_list)))
        if (response is None) or ("interfaces" not in response):
            print("station_list: incomplete response:")
            pprint(response)
            exit(1)

        for x in range(len(response['interfaces'])):
            for k, v in response['interfaces'][x].items():
                if "wlan" not in v['alias'] and v['port type'] == "WIFI-STA" \
                        or v['port type'] == "Ethernet":
                    num_ports += 1
        if ipv6:
            num_ports -= 1  # Prevents eth0 from being counted, preventing infinite loop

        while num_ips != num_ports and timeout_sec != 0:
            num_ips = 0
            response = super().json_get("/port/1/%s/%s?fields=alias,ip,port+type,ipv6+address" %
                                        (resource, ",".join(station_list)))
            if (response is None) or ("interfaces" not in response):
                print("station_list: incomplete response:")
                pprint(response)
                exit(1)

            if not ipv6:
                for x in range(len(response['interfaces'])):
                    for k, v in response['interfaces'][x].items():
                        if "wlan" not in v['alias'] and v['port type'] == "WIFI-STA" or v['port type'] == "Ethernet":
                            if v['ip'] != '0.0.0.0':
                                num_ips += 1
                time.sleep(1)
                timeout_sec -= 1
            if ipv6:
                for x in range(len(response['interfaces'])):
                    for k, v in response['interfaces'][x].items():
                        if v['alias'] != "eth0" and "wlan" not in v['alias'] and v['port type'] == "WIFI-STA" \
                                or v['port type'] == "Ethernet":
                            if v['ipv6 address'] != 'DELETED' and not v['ipv6 address'].startswith('fe80') \
                                    and v['ipv6 address'] != 'AUTO':
                                num_ips += 1
                time.sleep(1)
                timeout_sec -= 1
        if num_ips == num_ports:
            return True
        else:
            return False

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
        endp_list = self.json_get("/endp")
        if endp_list is not None:
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
            not_cx = ['warnings', 'errors', 'handler', 'uri', 'items']
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
    # just here for now for initial coding,  move later to correct spot
    def new_multicast_profile(self):
        multi_prof = MULTICASTProfile(self.lfclient_host, self.lfclient_port, \
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

    def new_generic_cx_profile(self):
        cx_prof = GenCXProfile(self.lfclient_host, self.lfclient_port, local_realm=self, debug_=self.debug)
        return cx_prof

    def new_vap_profile(self):
        vap_prof = VAPProfile(lfclient_url=self.lfclient_url, local_realm=self, debug_=self.debug)
        return vap_prof

class MULTICASTProfile(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port, local_realm,
                 report_timer_=3000, name_prefix_="Unset", number_template_="00000", debug_=False):
        """

        :param lfclient_host:
        :param lfclient_port:
        :param local_realm:
        :param name_prefix: prefix string for connection
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

    def refresh_mc(self):
        pass

    def admin_up_mc_tx(self, resource, side_mc_tx):
        set_port_r = LFRequest.LFRequest(self.lfclient_url, "/cli-json/set_port", debug_=self.debug)
        req_json = LFUtils.portUpRequest(resource, None, debug_on=False)
        req_json["port"] = side_mc_tx
        set_port_r.addPostData(req_json)
        json_response = set_port_r.jsonPost(self.debug)
        time.sleep(0.03)

    def admin_down_mc_tx(self, resource):
        set_port_r = LFRequest.LFRequest(self.lfclient_url, "/cli-json/set_port", debug_=self.debug)
        req_json = LFUtils.portDownRequest(resource, None, debug_on=False)
        for sta_name in self.station_names:
            req_json["port"] = sta_name
            set_port_r.addPostData(req_json)
            json_response = set_port_r.jsonPost(self.debug)
            time.sleep(0.03)    

    def start_mc_tx(self, side_tx, suppress_related_commands=None, debug_ = False ):
        if self.debug:
            debut_=True

        print("starting mc_tx")
        # hard code for now
        endp_name = 'mcast-xmit-sta'

        #start the trasmitter probably should be in start 
        json_data = {
                    "endp_name":endp_name,
        }

        url = "cli-json/start_endp"
        self.local_realm.json_post(url, json_data)
 

    def start_mc_rx(self,side_rx, suppress_related_commands=None, debug_ = False):
        if self.debug:
            debug_=True

        for port_name in side_rx:
            side_rx_info = self.local_realm.name_to_eid(port_name)
            side_rx_resource = side_rx_info[2]
            side_rx_name = "%s%s"%(self.name_prefix, side_rx_info[2])

            json_data = {
                            "endp_name":side_rx_resource
            }
            url = "cli-json/start_endp"
            self.local_realm.json_post(url, json_data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

        pass

    def stop_mc(self):
        pass

    def cleanup(self):
        pass

    def create_mc_tx(self, side_tx, suppress_related_commands=None, debug_ = False ):
        if self.debug:
            debug_=True

        json_data = []
        
        # hard code for now 
        endp_name = 'mcast-xmit-sta'
        #add_endp mcast-xmit-sta 1 1 side_tx mc_udp -1 NO 4000000 0 NO 1472 0 INCREASING NO 32 0 0
        json_data = {
                        'alias':endp_name,
                        'shelf':1,
                        'resource':1,
                        'port':side_tx,
                        'type':'mc_udp',
                        'ip_port':-1,
                        'is_rate_bursty':
                        'NO','min_rate':4000000,
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
                        'name':endp_name,
                        'ttl':32,'mcast_group':'224.9.9.9',
                        'mcast_dest_port':9999,
                        'rcv_mcast':'No'
                    }

        url = "cli-json/set_mc_endp"
        self.local_realm.json_post(url, json_data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

    def create_mc_rx(self,side_rx, suppress_related_commands=None, debug_ = False):
        if self.debug:
            debug_=True

        for port_name in side_rx:
            side_rx_info = self.local_realm.name_to_eid(port_name)
            side_rx_shelf = side_rx_info[1]
            side_rx_resource = side_rx_info[2]
            side_rx_name = "%s%s"%(self.name_prefix, side_rx_info[2])
            # add_endp mcast-rcv-sta-001 1 1 sta0002 mc_udp 9999 NO 0 0 NO 1472 0 INCREASING NO 32 0 0
            json_data = {
                            'alias':side_rx_resource,
                            'shelf':side_rx_shelf,
                            'resource':1,
                            'port':side_rx_resource,
                            'type':'mc_udp',
                            'ip_port':9999,
                            'is_rate_bursty':
                            'NO','min_rate':0,
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
                            'name':side_rx_resource,
                            'ttl':32,
                            'mcast_group':'224.9.9.9',
                            'mcast_dest_port':9999,
                            'rcv_mcast':'Yes'
                        }
            url = "cli-json/set_mc_endp"
            self.local_realm.json_post(url, json_data, debug_=debug_, suppress_related_commands_=suppress_related_commands)


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
        :param name_prefix: prefix string for connection
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
        self.name_prefix = name_prefix_
        self.number_template = number_template_

    def get_cx_names(self):
        return self.created_cx.keys()

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
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
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
                    "cx_name": cx_name
                }
                self.json_post(req_url, data)

                for side in range(len(self.created_cx[cx_name])):
                    req_url = "cli-json/rm_endp"
                    data = {
                        "endp_name": self.created_cx[cx_name][side]
                    }
                    self.json_post(req_url, data)

    def create(self, endp_type, side_a, side_b, sleep_time=0.03, suppress_related_commands=None, debug_=False):
        if self.debug:
            debug_=True

        cx_post_data = []
        timer_post_data = []
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
            side_b_name = "%s%s" % (self.name_prefix, side_b_info[2])

            for port_name in side_a:
                if port_name.find('.') < 0:
                    port_name = "%d.%s" % (side_a_info[1], port_name)

                side_a_info = self.local_realm.name_to_eid(port_name)
                side_a_shelf = side_a_info[0]
                side_a_resource = side_a_info[1]
                side_a_name = "%s%s"%(self.name_prefix, side_a_info[2])

                cx_name = "%s%s" % (self.name_prefix, port_name)
                self.created_cx[ cx_name ] = [side_a_name + "-A", side_a_name + "-B"]
                endp_side_a = {
                    "alias": side_a_name + "-A",
                    "shelf": 1,
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
                    "alias": side_a_name + "-B",
                    "shelf": 1,
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
                    "name": side_a_name + "-A",
                    "flag": "autohelper",
                    "val": 1
                }
                self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

                url = "cli-json/set_endp_flag"
                data = {
                    "name": side_a_name + "-B",
                    "flag": "autohelper",
                    "val": 1
                }
                self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands)
                #print("CXNAME366:")
                #pprint(cx_name)
                data = {
                    "alias": cx_name,
                    "test_mgr": "default_tm",
                    "tx_endp": side_a_name + "-A",
                    "rx_endp": side_a_name + "-B"
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
            side_a_name = side_a_info[2]

            for port_name in side_b:
                print(side_b)
                side_b_info = self.local_realm.name_to_eid(port_name)
                side_b_shelf = side_b_info[0]
                side_b_resource = side_b_info[1]
                side_b_name = side_b_info[2]

                cx_name = "%s%s" % (self.name_prefix, port_name)
                self.created_cx[ cx_name ] = [side_a_name + "-A", side_a_name + "-B"]
                endp_side_a = {
                    "alias": side_b_name + "-A",
                    "shelf": 1,
                    "resource": side_a_resource,
                    "port": side_a_info[2],
                    "type": endp_type,
                    "min_rate": self.side_a_min_bps,
                    "max_rate": self.side_a_max_bps,
                    "min_pkt": self.side_a_min_pkt,
                    "max_pkt": self.side_a_max_pkt,
                    "ip_port": -1
                }
                endp_side_b = {
                    "alias": side_b_name + "-B",
                    "shelf": 1,
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
                    "name": side_b_name + "-A",
                    "flag": "autohelper",
                    "val": 1
                }
                self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

                url = "cli-json/set_endp_flag"
                data = {
                    "name": side_b_name + "-B",
                    "flag": "autohelper",
                    "val": 1
                }
                self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands)
                #print("CXNAME451: %s" % cx_name)
                data = {
                    "alias": cx_name,
                    "test_mgr": "default_tm",
                    "tx_endp": side_b_name + "-A",
                    "rx_endp": side_b_name + "-B"
                }
                cx_post_data.append(data)
                timer_post_data.append({
                    "test_mgr":"default_tm",
                    "cx_name":cx_name,
                    "milliseconds":self.report_timer
                })
        else:
            raise ValueError("side_a or side_b must be of type list but not both: side_a is type %s side_b is type %s" % (type(side_a), type(side_b)))

        #print("post_data", cx_post_data)
        for data in cx_post_data:
            url = "/cli-json/add_cx"
            self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands)
            #print(" napping %f sec"%sleep_time, end='')
            time.sleep(sleep_time)
        #print("")

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
                "url": self.url
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
        self.created_cx = []
        self.created_endp = []

    def parse_command(self, sta_name):
        if self.type == "lfping":
            if (self.dest is not None or self.dest != "") and (self.interval is not None or self.interval > 0):
                self.cmd = "%s  -i %s -I %s %s" % (self.type, self.interval, sta_name, self.dest)
                #print(self.cmd)
            else:
                raise ValueError("Please ensure dest and interval have been set correctly")
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

            gen_name = name + "_gen0"
            gen_name1 = name + "_gen1"
            genl = GenericCx(lfclient_host=self.lfclient_host, lfclient_port=self.lfclient_port)
            genl.createGenEndp(gen_name, shelf, resource, name, "gen_generic")
            genl.createGenEndp(gen_name1, shelf, resource, name, "gen_generic")
            genl.setFlags(gen_name, "ClearPortOnStart", 1)
            genl.setFlags(gen_name1, "ClearPortOnStart", 1)
            genl.setFlags(gen_name1, "Unmanaged", 1)
            self.parse_command(name)
            genl.setCmd(gen_name, self.cmd)
            time.sleep(sleep_time)

            data = {
                "alias": "CX_" + name + "_gen",
                "test_mgr": "default_tm",
                "tx_endp": gen_name,
                "rx_endp": gen_name1
            }
            post_data.append(data)
            self.created_cx.append("CX_" + name + "_gen")
            self.created_endp.append(gen_name)
            self.created_endp.append(gen_name1)

        for data in post_data:
            url = "/cli-json/add_cx"
            self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands_)
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

    def create(self, resource_=1,channel=None, radio_="wiphy0", name_="moni0" ):
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
    def __init__(self, lfclient_url, local_realm, vap_name="", ssid="NA", ssid_pass="NA", mode=0, use_ht160=False, debug_=False):
        self.debug = debug_
        self.lfclient_url = lfclient_url
        self.ssid = ssid
        self.ssid_pass = ssid_pass
        self.mode = mode
        self.local_realm = local_realm
        self.vap_name = vap_name
        self.use_ht160 = use_ht160
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
            result += command_ref[name]

        return result

    def create(self, resource, radio, channel=None, up_=None, debug=False, suppress_related_commands_=True):

        if self.use_ht160:
            self.desired_add_vap_flags.append("enable_80211d")
            self.desired_add_vap_flags_mask.append("enable_80211d")
            self.desired_add_vap_flags.append("80211h_enable")
            self.desired_add_vap_flags_mask.append("80211h_enable")
            self.desired_add_vap_flags.append("ht160_enable")
            self.desired_add_vap_flags_mask.append("ht160_enable")

        print("MODE ========= ", self.mode)

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

        # create bridge
        data = {
            "shelf": 1,
            "resource": resource,
            "port": "br0",
            "network_devs": "eth1,%s" % self.vap_name
        }
        self.local_realm.json_post("cli-json/add_br", data)

        if (self.up):
            self.admin_up(1)

    def cleanup(self, resource, desired_ports=None, delay=0.03):
        print("Cleaning up VAPs")
        req_url = "/cli-json/rm_vlan"
        data = {
            "shelf": 1,
            "resource": resource,
            "port": None
        }
        if (desired_ports is not None):
            if len(desired_ports) < 1:
                print("No stations requested for cleanup, returning.")
                return
            names = ','.join(desired_ports)
            current_stations = self.local_realm.json_get("/port/1/%s/%s?fields=alias" % (resource, names))
            if current_stations is None:
                return
            if "interfaces" in current_stations:
                for station in current_stations['interfaces']:
                    for eid, info in station.items():
                        data["port"] = info["alias"]
                        self.local_realm.json_post(req_url, data, debug_=self.debug)
                        time.sleep(delay)

            if "interface" in current_stations:
                data["port"] = current_stations["interface"]["alias"]
                self.local_realm.json_post(req_url, data, debug_=self.debug)

            return

        names = ','.join(self.station_names)
        current_stations = self.local_realm.json_get("/port/1/%s/%s?fields=alias" % (resource, names))
        if current_stations is None or current_stations['interfaces'] is None:
            print("No stations to clean up")
            return

        if "interfaces" in current_stations:
            for station in current_stations['interfaces']:
                for eid, info in station.items():
                    data["port"] = info["alias"]
                    self.local_realm.json_post(req_url, data, debug_=self.debug)
                    time.sleep(delay)

        if "interface" in current_stations:
            data["port"] = current_stations["interface"]["alias"]
            self.local_realm.json_post(req_url, data, debug_=self.debug)


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
    def __init__(self, lfclient_url, local_realm, ssid="NA", ssid_pass="NA", security="open", number_template_="00000", mode=0, up=True,
                 dhcp=True, debug_=False, use_ht160=False):
        self.debug = debug_
        self.lfclient_url = lfclient_url
        self.ssid = ssid
        self.ssid_pass = ssid_pass
        self.mode = mode
        self.up = up
        self.dhcp = dhcp
        self.security = security
        self.local_realm = local_realm
        self.use_ht160 = use_ht160
        self.COMMANDS = ["add_sta", "set_port"]
        self.desired_add_sta_flags      = ["wpa2_enable", "80211u_enable", "create_admin_down"]
        self.desired_add_sta_flags_mask = ["wpa2_enable", "80211u_enable", "create_admin_down"]
        self.number_template = number_template_
        self.station_names = []
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
            self.error("Command name name [%s] not defined in %s" % (command_name, self.COMMANDS))
            return
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

    def admin_up(self, resource):
        set_port_r = LFRequest.LFRequest(self.lfclient_url, "/cli-json/set_port", debug_=self.debug)
        req_json = LFUtils.portUpRequest(resource, None, debug_on=False)
        for sta_name in self.station_names:
            req_json["port"] = sta_name
            set_port_r.addPostData(req_json)
            json_response = set_port_r.jsonPost(self.debug)
            time.sleep(0.03)

    def admin_down(self, resource):
        set_port_r = LFRequest.LFRequest(self.lfclient_url, "/cli-json/set_port", debug_=self.debug)
        req_json = LFUtils.portDownRequest(resource, None, debug_on=False)
        for sta_name in self.station_names:
            req_json["port"] = sta_name
            set_port_r.addPostData(req_json)
            json_response = set_port_r.jsonPost(self.debug)
            time.sleep(0.03)

    def cleanup(self, resource, desired_stations=None, delay=0.03):
        print("Cleaning up stations")
        req_url = "/cli-json/rm_vlan"
        data = {
            "shelf": 1,
            "resource": resource,
            "port": None
        }
        if (desired_stations is not None):
            if len(desired_stations) < 1:
                print("No stations requested for cleanup, returning.")
                return
            names = ','.join(desired_stations)
            current_stations = self.local_realm.json_get("/port/1/%s/%s?fields=alias" % (resource, names))
            if current_stations is None:
                return
            if "interfaces" in current_stations:
                for station in current_stations['interfaces']:
                    for eid,info in station.items():
                        data["port"] = info["alias"]
                        self.local_realm.json_post(req_url, data, debug_=self.debug)
                        time.sleep(delay)

            if "interface" in current_stations:
                data["port"] = current_stations["interface"]["alias"]
                self.local_realm.json_post(req_url, data, debug_=self.debug)

            return

        names = ','.join(self.station_names)
        current_stations = self.local_realm.json_get("/port/1/%s/%s?fields=alias" % (resource, names))
        if current_stations is None or current_stations['interfaces'] is None:
            print("No stations to clean up")
            return

        if "interfaces" in current_stations:
            for station in current_stations['interfaces']:
                for eid,info in station.items():
                    data["port"] = info["alias"]
                    self.local_realm.json_post(req_url, data, debug_=self.debug)
                    time.sleep(delay)

        if "interface" in current_stations:
            data["port"] = current_stations["interface"]["alias"]
            self.local_realm.json_post(req_url, data, debug_=self.debug)


    # Checks for errors in initialization values and creates specified number of stations using init parameters
    def create(self, resource, radio, num_stations=0, sta_names_=None, dry_run=False, up_=None, debug=False, suppress_related_commands_=True):
        # try:
        #     resource = resource_radio[0: resource_radio.index(".")]
        #     name = resource_radio[resource_radio.index(".") + 1:]
        #     if name.index(".") >= 0:
        #         radio_name = name[name.index(".")+1 : ]
        #     print("Building %s on radio %s.%s" % (num_stations, resource, radio_name))
        # except ValueError as e:
        #     print(e)

        if self.use_ht160:
            self.desired_add_sta_flags.append("ht160_enable")
            self.desired_add_sta_flags_mask.append("ht160_enable")
        self.add_sta_data["mode"] = self.mode

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
        self.add_sta_data["radio"] = radio
       
        self.add_sta_data["resource"] = resource
        self.set_port_data["current_flags"] = self.add_named_flags(self.desired_set_port_current_flags,
                                                                   set_port.set_port_current_flags)
        self.set_port_data["interest"] = self.add_named_flags(self.desired_set_port_interest_flags,
                                                              set_port.set_port_interest_flags)
        # these are unactivated LFRequest objects that we can modify and
        # re-use inside a loop, reducing the number of object creations
        add_sta_r = LFRequest.LFRequest(self.lfclient_url + "/cli-json/add_sta")
        set_port_r = LFRequest.LFRequest(self.lfclient_url + "/cli-json/set_port")
        self.station_names = []
        if num_stations > 0:
            self.station_names = LFUtils.portNameSeries("sta", 0, num_stations - 1, int("1" + self.number_template))
        else:
            self.station_names = sta_names_

        if (len(self.station_names) >= 15) or (suppress_related_commands_ == True):
            self.add_sta_data["suppress_preexec_cli"] = "yes"
            self.add_sta_data["suppress_preexec_method"] = 1
            self.set_port_data["suppress_preexec_cli"] = "yes"
            self.set_port_data["suppress_preexec_method"] = 1

        num = 0
        #pprint(self.station_names)
        #exit(1)
        for name in self.station_names:
            self.set_port_data["port"] = name
            num += 1
            self.add_sta_data["sta_name"] = name
            add_sta_r.addPostData(self.add_sta_data)
            if debug:
                print("- 381 - %s- - - - - - - - - - - - - - - - - - " % name)
                pprint(self.add_sta_data)
                pprint(self.set_port_data)
                pprint(add_sta_r)
                print("- ~381 - - - - - - - - - - - - - - - - - - - ")
            if dry_run:
                print("dry run")
                continue

            json_response = add_sta_r.jsonPost(debug)
            # time.sleep(0.03)
            time.sleep(2)
            set_port_r.addPostData(self.set_port_data)
            json_response = set_port_r.jsonPost(debug)
            time.sleep(0.03)

        LFUtils.waitUntilPortsAppear(resource, self.lfclient_url, self.station_names)

        # and set ports up
        if dry_run:
            return
        if (self.up):
            self.admin_up(1)
            self.admin_up(1)
        # for sta_name in self.station_names:
        #     req = LFUtils.portUpRequest(resource, sta_name, debug_on=False)
        #     set_port_r.addPostData(req)
        #     json_response = set_port_r.jsonPost(debug)
        #     time.sleep(0.03)

        print("created %s stations" % num)

#
