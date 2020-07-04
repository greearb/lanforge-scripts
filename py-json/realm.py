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
from LANforge.lfcli_base import LFCliBase
from generic_cx import GenericCx
import datetime


class Realm(LFCliBase):
    def __init__(self, lfclient_host="localhost", lfclient_port=8080, debug_=False, halt_on_error_=False):
        super().__init__(_lfjson_host=lfclient_host, _lfjson_port=lfclient_port, _debug=debug_, _halt_on_error=halt_on_error_)
        # self.lfclient_url = "http://%s:%s" % (lfclient_host, lfclient_port)
        self.debug = debug_
        self.check_connect()

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
            last_response = response_json[0]["LAST"]["response"];
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


    def parse_link(self, link):
        link = self.lfclient_url + link
        info = ()

    def new_station_profile(self):
        station_prof = StationProfile(self.lfclient_url, debug_=self.debug)
        return station_prof

    def new_l3_cx_profile(self):
        cx_prof = L3CXProfile(self.lfclient_host, self.lfclient_port, \
                              local_realm=self, debug_=self.debug, report_timer_=3000)
        return cx_prof

    def new_l4_cx_profile(self):
        cx_prof = L4CXProfile(self.lfclient_host, self.lfclient_port, local_realm=self, debug_=self.debug)
        return cx_prof

    def new_generic_cx_profile(self):
        cx_prof = GenCXProfile(self.lfclient_host, self.lfclient_port,local_realm=self, debug_=self.debug)
        return cx_prof


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
                "cx_state":"RUNNING"
            }, debug_=self.debug)
            print(".", end='')
        print("")

    def stop_cx(self):
        print("Stopping CXs...")
        for cx_name in self.created_cx.keys():
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
                "cx_state":"STOPPED"
            }, debug_=self.debug)
            print(".", end='')
        print("")

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

        print("post_data", cx_post_data)
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

    def create(self, ports=[], sleep_time=.5, debug_=False, suppress_related_commands_=None):
        cx_post_data = []
        for port_name in ports:
            if len(self.local_realm.name_to_eid(port_name)) == 3:
                shelf = self.local_realm.name_to_eid(port_name)[0]
                resource = self.local_realm.name_to_eid(port_name)[1]
                name = self.local_realm.name_to_eid(port_name)[2]
            elif len(self.local_realm.name_to_eid(port_name)) == 2:
                shelf = 1
                resource = self.local_realm.name_to_eid(port_name)[0]
                name = self.local_realm.name_to_eid(port_name)[1]
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
                "alias": "CX_" + self.local_realm.name_to_eid(port_name)[-1] + "_l4",
                "test_mgr": "default_tm",
                "tx_endp": self.local_realm.name_to_eid(port_name)[-1] + "_l4",
                "rx_endp": "NA"
            }
            cx_post_data.append(endp_data)

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
        self.count = 2
        self.cmd = ""
        self.local_realm = local_realm

    def create(self, ports=[], sleep_time=.5, debug_=False, suppress_related_commands_=None):
        if self.debug:
            debug_ = True;
        post_data = []
        for port_name in ports:
            gen_name = self.local_realm.name_to_eid(port_name)[-1] + "_gen0"
            gen_name2 = self.local_realm.name_to_eid(port_name)[-1] + "_gen1"
            genl = GenericCx(lfclient_host=self.lfclient_host, lfclient_port=self.lfclient_port)
            genl.createGenEndp(gen_name, 1, 1, port_name, "gen_generic")
            genl.createGenEndp(gen_name2, 1, 1, port_name, "gen_generic")
            genl.setFlags(gen_name, "ClearPortOnStart", 1)
            genl.setFlags(gen_name2, "ClearPortOnStart", 1)
            genl.setFlags(gen_name2, "Unmanaged", 1)
            genl.setCmd(gen_name, self.cmd)
            time.sleep(sleep_time)

            data = {
                "alias": self.local_realm.name_to_eid(port_name)[-1] + "_gen_CX",
                "test_mgr": "default_tm",
                "tx_endp": gen_name,
                "rx_endp": gen_name2
            }
            post_data.append(data)

        for data in post_data:
            url = "/cli-json/add_cx"
            self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands_)
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
    def __init__(self, lfclient_url, ssid="NA", ssid_pass="NA", security="open", number_template_="00000", mode=0, up=True,
                 dhcp=True, debug_=False):
        self.debug = debug_
        self.lfclient_url = lfclient_url
        self.ssid = ssid
        self.ssid_pass = ssid_pass
        self.mode = mode
        self.up = up
        self.dhcp = dhcp
        self.security = security
        self.COMMANDS = ["add_sta", "set_port"]
        self.desired_add_sta_flags = ["wpa2_enable", "80211u_enable", "create_admin_down"]
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

    # TODO: create use_wpa3()

    def use_wpa2(self, on=False, ssid=None, passwd=None):
        self.add_sta_data["ssid"] = ssid
        if on:
            if (ssid is None) or ("" == ssid):
                raise ValueError("use_wpa2: WPA2 requires ssid")
            if (passwd is None) or ("" == passwd):
                raise ValueError("use_wpa2: WPA2 requires passphrase or [BLANK]")
            self.set_command_param("add_sta", "ssid", ssid)
            self.set_command_param("add_sta", "key", passwd)
            self.set_command_flag("add_sta", "wpa2_enable", 1)
            self.add_sta_data["key"] = passwd
        else:
            self.set_command_flag("add_sta", "wpa2_enable", 0)

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
            elif value == 0:
                self.desired_add_sta_flags.remove(param_name)

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
        for sta_name in self.station_names:
            req_json = LFUtils.portUpRequest(resource, sta_name, debug_on=False)
            set_port_r.addPostData(req_json)
            json_response = set_port_r.jsonPost(self.debug)
            time.sleep(0.03)

    # Checks for errors in initialization values and creates specified number of stations using init parameters
    def create(self, resource, radio, num_stations=0, sta_names_=None, dry_run=False, up_=None, debug=False):
        # try:
        #     resource = resource_radio[0: resource_radio.index(".")]
        #     name = resource_radio[resource_radio.index(".") + 1:]
        #     if name.index(".") >= 0:
        #         radio_name = name[name.index(".")+1 : ]
        #     print("Building %s on radio %s.%s" % (num_stations, resource, radio_name))
        # except ValueError as e:
        #     print(e)
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
        self.add_sta_data["flags"] = self.add_named_flags(self.desired_add_sta_flags, add_sta.add_sta_flags)
        self.add_sta_data["flags_mask"] = self.add_named_flags(self.desired_add_sta_flags_mask, add_sta.add_sta_flags)
        self.add_sta_data["radio"] = radio
        self.add_sta_data["resource"] = resource
        self.set_port_data["current_flags"] = self.add_named_flags(self.desired_set_port_current_flags,
                                                                   set_port.set_port_current_flags)
        self.set_port_data["interest"] = self.add_named_flags(self.desired_set_port_interest_flags,
                                                              set_port.set_port_interest_flags)

        add_sta_r = LFRequest.LFRequest(self.lfclient_url + "/cli-json/add_sta")
        set_port_r = LFRequest.LFRequest(self.lfclient_url + "/cli-json/set_port")
        self.station_names = []
        if num_stations > 0:
            self.station_names = LFUtils.portNameSeries("sta", 0, num_stations - 1, int("1" + self.number_template))
        else:
            self.station_names = sta_names_

        if len(self.station_names) >= 15:
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
            time.sleep(.03)

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
