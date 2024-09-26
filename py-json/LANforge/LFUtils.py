#!/usr/bin/env python3
# flake8: noqa

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Define useful common methods                                  -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import sys
import os
import importlib
import pprint
import time
from time import sleep
from random import seed, randint
import re
import ipaddress
import math
import logging


if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../../")))

LFRequest = importlib.import_module("py-json.LANforge.LFRequest")
logger = logging.getLogger(__name__)


debug_printer = pprint.PrettyPrinter(indent=2)

seed(int(round(time.time() * 1000)))
NA = "NA"  # used to indicate parameter to skip
ADD_STA_FLAGS_DOWN_WPA2 = 68719477760
REPORT_TIMER_MS_FAST = 1500
REPORT_TIMER_MS_SLOW = 3000

COUNTRY_NAMES_NUMBERS = {
    "United States": 840,
    "Albania": 8,
    "Algeria": 12,
    "Argentina": 32,
    "Bangladesh": 50,
    "Armenia": 51,
    "Australia": 36,
    "Austria": 40,
    "Azerbaijan": 31,
    "Bahrain": 48,
    "Barbados": 52,
    "Belarus": 112,
    "Belgium": 56,
    "Belize": 84,
    "Bolivia": 68,
    "BiH": 70,
    "Brazil": 76,
    "Brunei": 96,
    "Bulgaria": 100,
    "Canada": 124,
    "Chile": 152,
    "China": 156,
    "Colombia": 170,
    "Costa Rica": 188,
    "Croatia": 191,
    "Cyprus": 196,
    "Czech Rep": 203,
    "Denmark": 208,
    "Dominican Rep": 214,
    "Ecuador": 218,
    "Egypt": 818,
    "El Salvador": 222,
    "Estonia": 233,
    "Finland": 246,
    "France": 250,
    "Georgia": 268,
    "Germany": 276,
    "Greece": 300,
    "Guatemala": 320,
    "Haiti": 332,
    "Honduras": 340,
    "Hong Kong": 344,
    "Hungary": 348,
    "Iceland": 352,
    "India": 356,
    "Indonesia": 360,
    "Iran": 364,
    "Ireland": 372,
    "Israel": 376,
    "Italy": 380,
    "Jamaica": 388,
    "Japan": 392,
    "Japan (JP1)": 393,
    "Japan (JP0)": 394,
    "Japan (JP1-1)": 395,
    "Japan (JE1)": 396,
    "Japan (JE2)": 397,
    "Jordan": 400,
    "Kazakhstan": 398,
    "North Korea": 408,
    "South Korea 410": 410,
    "South Korea 411": 411,
    "Kuwait": 414,
    "Latvia": 428,
    "Lebanon": 422,
    "Liechtenstein": 438,
    "Lithuania": 440,
    "Luxembourg": 442,
    "Macau": 446,
    "Macedonia": 807,
    "Malaysia": 458,
    "Mexico": 484,
    "Monaco": 492,
    "Morocco": 504,
    "Netherlands": 528,
    "Aruba": 533,
    "New Zealand": 554,
    "Norway": 578,
    "Oman": 512,
    "Pakistan": 586,
    "Panama": 591,
    "Peru": 604,
    "Philippines": 608,
    "Poland": 616,
    "Portugal": 620,
    "Pueto Rico": 630,
    "Qatar": 634,
    "Romania": 642,
    "Russia": 643,
    "Saudi Arabia": 682,
    "Singapore": 702,
    "Slovak Republic": 703,
    "Slovenia": 705,
    "South Africa": 710,
    "Spain": 724,
    "Sweden": 752,
    "Switzerland": 756,
    "Syria": 760,
    "Taiwan": 158,
    "Thailand": 764,
    "Trinidad &Tobago": 780,
    "Tunisia": 788,
    "Turkey": 792,
    "U.A.E.": 784,
    "Ukraine": 804,
    "United Kingdom": 826,
    "Uruguay": 858,
    "Uzbekistan": 860,
    "Venezuela": 862,
    "Vietnam": 704,
    "Yemen": 887,
    "Zimbabwe": 716,
}
# these were looked up on various websites and where those were not forthcoming
# the ISO 3166-1 alpha-2 chart on wikipedia was consulted
COUNTRY_CODES_NUMBERS = {
    "US": 840,
    "AL": 8,
    "DZ": 12,
    "AR": 32,
    "BD": 50,
    "AM": 51,
    "AU": 36,
    "AT": 40,
    "AZ": 31,
    "BH": 48,
    "BB": 52,
    "BY": 112,
    "BE": 56,
    "BZ": 84,
    "BO": 68,
    "BA": 70,  # Bosnia / Herzegovina
    "BR": 76,
    "BN": 96,
    "BG": 100,
    "CA": 124,
    "CL": 152,
    "CN": 156,
    "CO": 170,
    "CR": 188,
    "HR": 191,
    "CY": 196,
    "CZ": 203,
    "DK": 208,
    "DO": 214,
    "EC": 218,
    "EG": 818,
    "SV": 222,
    "EE": 233,
    "FI": 246,
    "FR": 250,
    "GE": 268,
    "DE": 276,
    "GR": 300,
    "GT": 320,
    "HT": 332,
    "HN": 340,
    "HK": 344,
    "HU": 348,
    "IS": 352,
    "IN": 356,
    "ID": 360,
    "IR": 364,
    "IE": 372,
    "IL": 376,
    "IT": 380,
    "JM": 388,
    "JP3": 392,
    "JP1": 393,
    "JP0": 394,
    "JP1-1": 395,
    "JE1": 396,
    "JE2": 397,
    "JO": 400,
    "KZ": 398,
    "KP": 408,
    "KR 410": 410,
    "KR 411": 411,
    "KW": 414,
    "LV": 428,
    "LB": 422,
    "LI": 438,
    "LT": 440,
    "LU": 442,
    "MO": 446,
    # macedonia is a region including Greece, North Macedonia, Bulgaria, Albania, Serbia, Kosovo
    # North Macedonia is MK
    "MK": 807,
    "MY": 458,
    "MX": 484,
    "MC": 492,
    "MA": 504,
    "NL": 528,
    "AW": 533,
    "NZ": 554,
    "NO": 578,
    "OM": 512,
    "PK": 586,
    "PA": 591,
    "PE": 604,
    "PH": 608,
    "PL": 616,
    "PT": 620,
    "PR": 630,
    "QA": 634,
    "RO": 642,
    "RU": 643,
    "SA": 682,
    "SG": 702,
    "SK": 703,
    "SI": 705,
    "ZA": 710,
    "ES": 724,
    "SE": 752,
    "CH": 756,
    "SY": 760,
    "TW": 158,
    "TH": 764,
    "TT": 780,
    "TN": 788,
    "TR": 792,
    "AE": 784,
    "UA": 804,
    "GB": 826,
    "UY": 858,
    "UZ": 860,
    "VE": 862,
    "VN": 704,
    "YE": 887,
    "ZW": 716,
}

# Used for Speed
def parse_size_bps(size_val):
    if isinstance(size_val, str):
        size_val.upper()
        # print(size_string)
        pattern = re.compile(r"^(\d+)([MGKmgk]?)bps$")
        td = pattern.match(size_val)
        if td is not None:
            size = int(td.group(1))
            unit = str(td.group(2)).lower()
            # print(1, size, unit)
            if unit == 'g':
                size *= 10000000
            elif unit == 'm':
                size *= 100000
            elif unit == 'k':
                size *= 1000
            # print(2, size, unit)
            return size
    else:
        return size_val


# Used for Size of file
def parse_size(size_val):
    if isinstance(size_val, str):
        size_val.upper()
        pattern = re.compile(r"^(\d+)([MGKmgk]?b?$)")
        td = pattern.match(size_val)
        if td is not None:
            size = int(td.group(1))
            unit = str(td.group(2)).lower()
            # print(1, size, unit)
            if unit == 'g':
                size *= 1073741824
            elif unit == 'm':
                size *= 1048576
            elif unit == 'k':
                size *= 1024
            # print(2, size, unit)
            return size
    else:
        return size_val


class PortEID:
    shelf = 1
    resource = 1
    port_id = 0
    port_name = ""

    def __init__(self, json_response):
        if json_response is None:
            raise Exception("No json input")
        json_s = json_response
        if json_response['interface'] is not None:
            json_s = json_response['interface']

        logger.info(debug_printer.pformat(json_s))


# end class PortEID

def staNewDownStaRequest(sta_name, resource_id=1, radio="wiphy0", ssid="", passphrase="", debug_on=False):
    return sta_new_down_sta_request(sta_name, resource_id, radio, ssid, passphrase, debug_on)


def sta_new_down_sta_request(sta_name, resource_id=1, radio="wiphy0", ssid="", passphrase="", debug_on=False):
    """
    For use with add_sta. If you don't want to generate mac addresses via patterns (xx:xx:xx:xx:81:*)
    you can generate octets using random_hex.pop(0)[2:] and gen_mac(parent_radio_mac, octet)
    See http://localhost:8080/help/add_sta
    :param resource_id:
    :param radio:
    :param debug_on:
    :param passphrase:
    :param ssid:
    :type sta_name: str
    """
    data = {
        "shelf": 1,
        "resource": resource_id,
        "radio": radio,
        "sta_name": sta_name,
        "flags": ADD_STA_FLAGS_DOWN_WPA2,  # note flags for add_sta do not match set_port
        "ssid": ssid,
        "key": passphrase,
        "mac": "xx:xx:xx:xx:*:xx",  # "NA", #gen_mac(parent_radio_mac, random_hex.pop(0))
        "mode": 0,
        "rate": "DEFAULT"
    }
    if debug_on:
        logger.debug(debug_printer.pformat(data))
    return data


def portSetDhcpDownRequest(resource_id, port_name, debug_on=False):
    return port_set_dhcp_down_request(resource_id, port_name, debug_on)


def port_set_dhcp_down_request(resource_id, port_name, debug_on=False):
    """
    See http://localhost:8080/help/set_port
    :param debug_on:
    :param resource_id:
    :param port_name:
    :return:
    """
    print("portSetDhcpDownRequest")
    data = {
        "shelf": 1,
        "resource": resource_id,
        "port": port_name,
        "current_flags": 2147483649,  # 0x1 = interface down + 2147483648 use DHCP values
        "interest": 75513858,  # includes use_current_flags + dhcp + dhcp_rls + ifdown
        "report_timer": REPORT_TIMER_MS_FAST
    }
    if debug_on:
        logger.debug(debug_printer.pformat(data))
    return data


def portDhcpUpRequest(resource_id, port_name, debug_on=False):
    return port_dhcp_up_request(resource_id, port_name, debug_on)


def port_dhcp_up_request(resource_id, port_name, debug_on=False):
    """
    See http://localhost:8080/help/set_port
    :param debug_on:
    :param resource_id:
    :param port_name:
    :return:
    """
    if debug_on:
        logger.debug("portDhcpUpRequest")
    data = {
        "shelf": 1,
        "resource": resource_id,
        "port": port_name,
        "current_flags": 2147483648,  # vs 0x1 = interface down + use_dhcp
        "interest": 75513858,  # includes use_current_flags + dhcp + dhcp_rls + ifdown
        "report_timer": REPORT_TIMER_MS_FAST,
    }
    if debug_on:
        logger.debug(debug_printer.pformat(data))
    return data

# Return json request object, does not actually attempt to admin up a port
def portUpRequest(resource_id, port_name, debug_on=False):
    return port_up_request(resource_id, port_name, debug_on=debug_on)


# Return json request object, does not actually attempt to admin up a port
def port_up_request(resource_id, port_name, debug_on=False):
    """
    See http://localhost:8080/help/set_port
    :param debug_on:
    :param resource_id:
    :param port_name:
    :return:
    """

    if port_name:
        eid = name_to_eid(port_name)
        if resource_id == None:
            resource_id = eid[1]
            port_name = eid[2]

    data = {
        "shelf": 1,
        "resource": resource_id,
        "port": port_name,
        "current_flags": 0,  # vs 0x1 = interface down
        "interest": 8388610,  # includes use_current_flags + dhcp + dhcp_rls + ifdown
        "report_timer": REPORT_TIMER_MS_FAST,
    }
    if debug_on:
        logger.debug("Port up request")
        logger.debug(debug_printer.pformat(data))
    return data


def portDownRequest(resource_id, port_name, debug_on=False):
    return port_down_request(resource_id, port_name, debug_on)


def port_down_request(resource_id, port_name, debug_on=False):
    """
    Does not change the use_dhcp flag
    See http://localhost:8080/help/set_port
    :param debug_on:
    :param resource_id:
    :param port_name:
    :return:
    """

    data = {
        "shelf": 1,
        "resource": resource_id,
        "port": port_name,
        "current_flags": 1,  # vs 0x0 = interface up
        "interest": 8388610,  # = current_flags + ifdown
        "report_timer": REPORT_TIMER_MS_FAST,
    }
    if debug_on:
        logger.debug("Port down request")
        logger.debug(debug_printer.pformat(data))
    return data


def port_reset_request(resource_id, port_name, debug_on=False):
    """
    Does not change the use_dhcp flag
    See http://localhost:8080/help/reset_port
    :param debug_on:
    :param resource_id:
    :param port_name:
    :return:
    """

    data = {
        "shelf": 1,
        "resource": resource_id,
        "port": port_name
    }
    if debug_on:
        logger.debug("Port reset request")
        logger.debug(debug_printer.pformat(data))
    return data


def generateMac(parent_mac, random_octet, debug=False):
    return generate_mac(parent_mac=parent_mac, random_octet=random_octet, debug=debug)


def generate_mac(parent_mac, random_octet, debug=False):
    if debug:
        print("************ random_octet: %s **************" % random_octet)
    my_oct = random_octet
    if len(random_octet) == 4:
        my_oct = random_octet[2:]
    octets = parent_mac.split(":")
    octets[4] = my_oct
    return ":".join(octets)


def portNameSeries(prefix_="sta", start_id_=0, end_id_=1, padding_number_=10000, radio=None):
    """
    This produces a named series similar to "sta000, sta001, sta002...sta0(end_id)"
    the padding_number is added to the start and end numbers and the resulting sum
    has the first digit trimmed, so f(0, 1, 10000) => {"0000", "0001"}
    @deprecated -- please use port_name_series
    :param radio:
    :param prefix_:
    :param start_id_:
    :param end_id_:
    :param padding_number_:
    :return:
    """
    return port_name_series(prefix=prefix_, start_id=start_id_, end_id=end_id_, padding_number=padding_number_,
                            radio=radio)


def port_name_series(prefix="sta", start_id=0, end_id=1, padding_number=10000, radio=None):
    """
    This produces a named series similar to "sta000, sta001, sta002...sta0(end_id)"
    the padding_number is added to the start and end numbers and the resulting sum
    has the first digit trimmed, so f(0, 1, 10000) => {"0000", "0001"}
    @deprecated -- please use port_name_series
    :param radio:
    :param prefix: defaults to 'sta'
    :param start_id: beginning id
    :param end_id: ending_id
    :param padding_number: used for width of resulting station number
    :return: list of stations
    """

    eid = None
    if radio is not None:
        eid = name_to_eid(radio)

    name_list = []
    for i in range((padding_number + start_id), (padding_number + end_id + 1)):
        sta_name = "%s%s" % (prefix, str(i)[1:])
        if eid is None:
            name_list.append(sta_name)
        else:
            name_list.append("%i.%i.%s" % (eid[0], eid[1], sta_name))
    return name_list


def gen_ip_series(ip_addr, netmask, num_ips=None):
    ip_list = [str(ip) for ip in ipaddress.IPv4Network(ip_addr + '/' + netmask, strict=False)]
    chosen_ips = []
    if num_ips is None:
        return ip_list
    else:
        for i in range(ip_list.index(ip_addr), num_ips + ip_list.index(ip_addr)):
            chosen_ips.append(ip_list[i])
        return chosen_ips


def generateRandomHex():
    return generate_random_hex()


# generate random hex if you need it for mac addresses
def generate_random_hex():
    # generate a few random numbers and convert them into hex:
    random_hex = []
    for rn in range(0, 254):
        random_dec = randint(0, 254)
        random_hex.append(hex(random_dec))
    return random_hex


# return reverse map of aliases to port records
#
# expect nested records, which is an artifact of some ORM
# that other customers expect:
# [
#   {
#       "1.1.eth0": {
#           "alias":"eth0"
#       }
#   },
#   { ... }
def portListToAliasMap(json_list, debug_=False):
    return port_list_to_alias_map(json_list=json_list, debug_=debug_)


def port_list_to_alias_map(json_list, debug_=False):
    reverse_map = {}
    if (json_list is None) or (len(json_list) < 1):
        if debug_:
            print("port_list_to_alias_map: no json_list provided")
            raise ValueError("port_list_to_alias_map: no json_list provided")
        return reverse_map

    json_interfaces = json_list
    if 'interfaces' in json_list:
        json_interfaces = json_list['interfaces']

    for record in json_interfaces:
        if len(record.keys()) < 1:
            continue
        record_keys = record.keys()
        k2 = ""
        # we expect one key in record keys, but we can't expect [0] to be populated
        json_entry = None
        for k in record_keys:
            k2 = k
            json_entry = record[k]
        # skip uninitialized port records
        if k2.find("Unknown") >= 0:
            continue
        reverse_map[k2] = json_entry

    return reverse_map


def list_to_alias_map(json_list=None, from_element=None, debug_=False):
    reverse_map = {}
    if (json_list is None) or (len(json_list) < 1):
        if debug_:
            print("port_list_to_alias_map: no json_list provided")
            raise ValueError("port_list_to_alias_map: no json_list provided")
        return reverse_map

    if debug_:
        pprint.pprint(("list_to_alias_map:json_list: ", json_list))
    json_interfaces = json_list
    if from_element in json_list:
        json_interfaces = json_list[from_element]

    for record in json_interfaces:
        if debug_:
            pprint.pprint(("list_to_alias_map: %s record:" % from_element, record))
        if len(record.keys()) < 1:
            if debug_:
                print("list_to_alias_map: no record.keys")
            continue
        record_keys = record.keys()
        k2 = ""
        # we expect one key in record keys, but we can't expect [0] to be populated
        json_entry = None
        for k in record_keys:
            k2 = k
            json_entry = record[k]
        # skip uninitialized port records
        if k2.find("Unknown") >= 0:
            continue
        reverse_map[k2] = json_entry
    if debug_:
        pprint.pprint(("list_to_alias_map: reverse_map", reverse_map))
    return reverse_map


def findPortEids(resource_id=1, base_url="http://localhost:8080", port_names=(), debug=False):
    return find_port_eids(resource_id=resource_id, base_url=base_url, port_names=port_names, debug=debug)


def find_port_eids(resource_id=1, base_url="http://localhost:8080", port_names=(), debug=False):
    port_eids = []
    if len(port_names) < 0:
        return []
    port_url = "/port/1"
    for port_name in port_names:
        uri = "%s/%s/%s" % (port_url, resource_id, port_name)
        lf_r = LFRequest.LFRequest(base_url, uri, debug_=debug)
        response = lf_r.get_as_json()
        if response is None:
            print("Not found: " + port_name)
        else:
            port_eids.append(PortEID(response))
    return port_eids


def waitUntilPortsAdminDown(resource_id=1, base_url="http://localhost:8080", port_list=()):
    return wait_until_ports_admin_down(resource_id=resource_id, base_url=base_url, port_list=port_list)


def wait_until_ports_admin_down(resource_id=1, base_url="http://localhost:8080", debug_=False, port_list=(), timeout_sec=360):
    print("Waiting until ports appear admin-down...")
    port_url = "/port/1"
    for _ in range(0, timeout_sec):
        up_stations = []
        for port_name in port_list:
            uri = "%s/%s/%s?fields=device,down" % (port_url, resource_id, port_name)
            lf_r = LFRequest.LFRequest(base_url, uri, debug_=debug_)
            json_response = lf_r.get_as_json()
            if json_response is None:
                if debug_:
                    print("port %s disappeared" % port_name)
                continue
            if "interface" in json_response:
                json_response = json_response['interface']
            if json_response['down'] == "false":
                up_stations.append(port_name)
        if len(up_stations) == 0:
            return True
        sleep(1)

    return False


def waitUntilPortsAdminUp(resource_id=0, base_url="http://localhost:8080", port_list=()):
    return wait_until_ports_admin_up(resource_id=resource_id, base_url=base_url, port_list=port_list)


def wait_until_ports_admin_up(resource_id=0, base_url="http://localhost:8080", port_list=(), debug_=False, timeout=300):
    if debug_:
        print("Waiting until %s ports appear admin-up..." % (len(port_list)))
    down_stations = port_list.copy()
    port_url = "/port"
    loops = 0

    # url = /%s/%s?fields=device,down" % (resource_id, port_name)
    for _ in range(0, timeout):
        down_stations = []
        for port_name in port_list:
            eid = name_to_eid(port_name)
            rid = resource_id
            if rid == 0:  # TODO: this allows user to pass in resource_id, but probably should remove resource_id entirely.
                rid = eid[1]  # use resource-id from the eid instead.
            uri = "%s/%s/%s/%s?fields=device,down" % (port_url, eid[0], rid, eid[2])
            lf_r = LFRequest.LFRequest(base_url, uri, debug_=debug_)
            json_response = lf_r.get_as_json()

            if debug_:
                print("uri: %s response:\n%s" % (uri, json_response))

            if json_response is None:
                if debug_:
                    print("port response is None for port name: %s" % port_name)
                down_stations.append(port_name)
                continue

            if "interface" in json_response:
                json_response = json_response['interface']
            else:
                if debug_:
                    print("interface not found in json response:")
                    pprint(json_response)
                down_stations.append(port_name)
                continue

            if json_response['down']:  # This is a boolean object, not a string
                if debug_:
                    logger.info("waiting for port: %s to go admin up." % port_name)
                down_stations.append(port_name)
            else:
                if debug_:
                    logger.debug("port %s is admin up" % port_name)

        if len(down_stations) > 0:
            sleep(1)
        else:
            return True

        loops += 1

    logger.warning("Not all ports went admin up within %s+ seconds" % timeout)
    return False

def speed_to_int(speed):
    # Parse speed into a number.  Initial implementation is for ping output, but
    # add more as needed.
    tokens = speed.split(" ")
    rv = float(tokens[0])
    if len(tokens) > 1:
        units = tokens[1]
        if units == "B":
            return int(rv)
        elif units == "KB":
            return int(rv * 1000)
        elif units == "MB":
            return int(rv * 1000000)
        elif units == "GB":
            return int(rv * 1000000000)
        else:
            raise ValueError("Un-handled units -:%s:-" % (units))

def waitUntilPortsDisappear(base_url="http://localhost:8080", port_list=(), debug=False, timeout=360):
    wait_until_ports_disappear(base_url, port_list, debug=debug, timeout_sec=timeout)


def wait_until_ports_disappear(base_url="http://localhost:8080", port_list=(), debug=False, timeout_sec=360):
    if (port_list is None) or (len(port_list) < 1):
        if debug:
            logger.debug("LFUtils: wait_until_ports_disappear: empty list, returning")
        return True  # no ports to remove, so we are done

    logger.info("LFUtils: Waiting until {len_port_list} ports disappear...".format(len_port_list=len(port_list)))
    url = "/port/1"

    temp_names_by_resource = {1: []}
    temp_query_by_resource = {1: ""}
    for port_eid in port_list:
        eid = name_to_eid(port_eid)
        # shelf = eid[0]
        resource_id = eid[1]
        if resource_id == 0:
            continue
        if resource_id not in temp_names_by_resource.keys():
            temp_names_by_resource[resource_id] = []
        port_name = eid[2]
        temp_names_by_resource[resource_id].append(port_name)
        temp_query_by_resource[resource_id] = "%s/%s/%s?fields=alias" % (
            url, resource_id, ",".join(temp_names_by_resource[resource_id]))
    if debug:
        logger.debug(pprint.pformat(("temp_query_by_resource", temp_query_by_resource)))
    sec_elapsed = 0
    rm_ports_iteration = math.ceil(timeout_sec / 4)
    if rm_ports_iteration > 30:
        rm_ports_iteration = 30
    if rm_ports_iteration == 0:
        rm_ports_iteration = 1

    found_stations = []
    for _ in range(0, timeout_sec):
        found_stations = []
        for (resource, check_url) in temp_query_by_resource.items():
            if debug:
                pprint.pprint([
                    ("base_url", base_url),
                    ("check_url", check_url),
                ])
            lf_r = LFRequest.LFRequest(base_url, check_url, debug_=debug)
            json_response = lf_r.get_as_json()
            if json_response is None:
                logger.info("LFUtils::wait_until_ports_disappear:: Request returned None: [{}]".format(base_url + check_url))
            else:
                if debug:
                    pprint.pprint(("wait_until_ports_disappear json_response:", json_response))
                if "interface" in json_response:
                    found_stations.append(json_response["interface"])
                elif "interfaces" in json_response:
                    mapped_list = list_to_alias_map(json_response, from_element="interfaces", debug_=debug)
                    found_stations.extend(mapped_list.keys())
            if debug:
                logger.debug(pprint.pformat([("port_list", port_list), ("found_stations", found_stations)]))
        if len(found_stations) > 0:
            if debug:
                logger.debug(pprint.pformat(("wait_until_ports_disappear found_stations:", found_stations)))
        else:
            return True

        if (sec_elapsed + 1) % rm_ports_iteration == 0:
            for port in found_stations:
                if debug:
                    logger.debug('removing port %s' % '.'.join(port))
                remove_port(port[1], port[2], base_url)
        sleep(1)  # check for ports once per second

    logger.critical('%s ports were still found' % found_stations)
    return False


def waitUntilPortsAppear(base_url="http://localhost:8080", port_list=(), debug=False):
    """
    Deprecated
    :param base_url:
    :param port_list:
    :param debug:
    :return:
    """
    return wait_until_ports_appear(base_url, port_list, debug=debug)

def eid_to_str(eid_list : list = None, shrink_zeros: bool = True) -> str:
    if shrink_zeros:
        return f"{int(eid_list[0])}.{int(eid_list[1])}.{int(eid_list[2])}"
    return f"{eid_list[0]}.{eid_list[1]}.{eid_list[2]}"

def name_to_eid(eid_input, non_port=False):
    rv = [1, 1, "", ""]
    if (eid_input is None) or (eid_input == ""):
        logger.critical("name_to_eid wants eid like 1.1.sta0 but given[%s]" % eid_input)
        raise ValueError("name_to_eid wants eid like 1.1.sta0 but given[%s]" % eid_input)
    if type(eid_input) is not str:
        logger.critical(
            "name_to_eid wants string formatted like '1.2.name', not a tuple or list or [%s]" % type(eid_input))
        raise ValueError(
            "name_to_eid wants string formatted like '1.2.name', not a tuple or list or [%s]" % type(eid_input))

    info = eid_input.split('.')
    if len(info) == 1:
        rv[2] = info[0]  # just port name
        return rv

    if (len(info) == 2) and info[0].isnumeric() and not info[1].isnumeric():  # resource.port-name
        rv[1] = int(info[0])
        rv[2] = info[1]
        return rv

    elif (len(info) == 2) and not info[0].isnumeric():  # port-name.qvlan
        rv[2] = info[0] + "." + info[1]
        return rv

    if (len(info) == 3) and info[0].isnumeric() and info[1].isnumeric():  # shelf.resource.port-name
        rv[0] = int(info[0])
        rv[1] = int(info[1])
        rv[2] = info[2]
        return rv

    elif (len(info) == 3) and info[0].isnumeric() and not info[1].isnumeric():  # resource.port-name.qvlan
        rv[1] = int(info[0])
        rv[2] = info[1] + "." + info[2]
        return rv

    if non_port:
        # Maybe attenuator or similar shelf.card.atten.index
        rv[0] = int(info[0])
        rv[1] = int(info[1])
        rv[2] = int(info[2])
        if len(info) >= 4:
            rv[3] = int(info[3])
        return rv

    if len(info) == 4:  # shelf.resource.port-name.qvlan
        rv[0] = int(info[0])
        rv[1] = int(info[1])
        rv[2] = info[2] + "." + info[3]

    if len(info) == 5:
        rv[0] = int(info[0])
        rv[1] = int(info[1])
        rv[2] = int(info[2])
        rv[3] = int(info[3])
        #rv[4] = int(info[4])  # need to do more testing for the 5 th element

    return rv


def wait_until_ports_appear(base_url="http://localhost:8080", port_list=(), debug=False, timeout=300):
    """
    Wait until ports are found and non phantom, or if timeout expires.
    Returns True if all are found and non phantom, returns False if timeout expires first.
    :param timeout:
    :param base_url:
    :param port_list: list or str. Pass a list of multiple port EIDs, or a single EID string.
    :param debug:
    :return:
    """
    if debug:
        logger.debug("Waiting until ports appear...")
        existing_stations = LFRequest.LFRequest(base_url, '/ports', debug_=debug)
        # logger.debug('existing ports')
        # logger.debug(pprint.pformat(existing_stations)) # useless
    port_url = "/port/1"
    show_url = "/cli-json/show_ports"
    found_stations = set()
    if base_url.endswith('/'):
        port_url = port_url[1:]
        show_url = show_url[1:]
    if type(port_list) is not list:
        port_list = [port_list]
    if debug:
        current_ports = LFRequest.LFRequest(base_url, '/ports', debug_=debug).get_as_json()
        logger.debug("LFUtils:wait_until_ports_appear, full port listing: %s" % pprint.pformat(current_ports))
        for port in current_ports['interfaces']:
            if list(port.values())[0]['phantom']:
                logger.debug("LFUtils:waittimeout_until_ports_appear: %s is phantom" % list(port.values())[0]['alias'])
    for attempt in range(0, int(timeout / 2)):
        found_stations = set()
        for port_eid in port_list:
            eid = name_to_eid(port_eid)
            shelf = eid[0]
            resource_id = eid[1]
            port_name = eid[2]
            # TODO:  If port_name happens to be a number, especialy '1', then the request below
            # gets a list instead of a single item...and see a few lines down.
            uri = "%s/%s/%s" % (port_url, resource_id, port_name)
            #print("port-eid: %s uri: %s" % (port_eid, uri))
            lf_r = LFRequest.LFRequest(base_url, uri, debug_=debug)
            json_response = lf_r.get_as_json()
            if json_response is not None:
                #pprint.pprint(json_response)
                # TODO:  If a list was (accidentally) requested, this code below will blow up.
                # This can currently happen if someone manages to name a port 1.1.vap0, ie using
                # an EID as a name.
                # TODO:  Fix name_to_eid to somehow detect this and deal with it.
                if not json_response['interface']['phantom']:
                    found_stations.add("%s.%s.%s" % (shelf, resource_id, port_name))
            else:
                lf_r = LFRequest.LFRequest(base_url, show_url, debug_=debug)
                lf_r.addPostData({"shelf": shelf, "resource": resource_id, "port": port_name, "probe_flags": 5})
                lf_r.jsonPost()
        if len(found_stations) < len(port_list):
            sleep(2)
            logger.info('Found %s out of %s ports in %s out of %s tries in wait_until_ports_appear' % (len(found_stations), len(port_list), attempt, timeout/2))
        else:
            logger.info('All %s ports appeared' % len(found_stations))
            return True
    if debug:
        logger.debug("These ports appeared: " + ", ".join(found_stations))
        logger.debug("These ports did not appear: " + ",".join(set(port_list) - set(found_stations)))
        logger.debug(pprint.pformat(LFRequest.LFRequest("%s/ports" % base_url)))
    return False


def wait_until_endps(base_url="http://localhost:8080", endp_list=(), debug=False, timeout=360):
    """

    :param base_url:
    :param endp_list:
    :param debug:
    :return:
    """
    print("Waiting until endpoints appear...")
    port_url = "/port/1"
    ncshow_url = "/cli-form/show_endp"
    if base_url.endswith('/'):
        port_url = port_url[1:]
        ncshow_url = ncshow_url[1:]
    found_stations = []
    for _ in range(0, int(timeout / 2)):
        found_stations = []
        for port_eid in endp_list:

            eid = name_to_eid(port_eid)
            shelf = eid[0]
            resource_id = eid[1]
            port_name = eid[2]

            uri = "%s/%s/%s" % (port_url, resource_id, port_name)
            lf_r = LFRequest.LFRequest(base_url, uri, debug_=debug)
            json_response = lf_r.get_as_json()
            if json_response is not None:
                found_stations.append(port_name)
            else:
                lf_r = LFRequest.LFRequest(base_url, ncshow_url, debug_=debug)
                lf_r.addPostData({"shelf": shelf, "resource": resource_id, "port": port_name, "flags": 1})
                lf_r.formPost()
        if len(found_stations) < len(endp_list):
            sleep(2)
        else:
            return True
    if debug:
        logger.debug("These stations appeared: " + ", ".join(found_stations))
    return


def removePort(resource, port_name, baseurl="http://localhost:8080/", debug=False):
    remove_port(resource=resource, port_name=port_name, baseurl=baseurl, debug=debug)


def remove_port(resource, port_name, baseurl="http://localhost:8080/", debug=False):
    if debug:
        print("Removing port %d.%s" % (resource, port_name))
    url = "/cli-json/rm_vlan"
    lf_r = LFRequest.LFRequest(baseurl, url, debug_=debug)
    lf_r.addPostData({
        "shelf": 1,
        "resource": resource,
        "port": port_name
    })
    lf_r.jsonPost(debug)


def removeCX(baseurl, cx_names, debug=False):
    remove_cx(baseurl=baseurl, cx_names=cx_names, debug=debug)


def remove_cx(baseurl, cx_names, debug=False):
    if debug:
        print("Removing cx %s" % ", ".join(cx_names))
    url = "/cli-json/rm_cx"
    for name in cx_names:
        data = {
            "test_mgr": "all",
            "cx_name": name
        }
        lf_r = LFRequest.LFRequest(baseurl, url, debug_=debug)
        lf_r.addPostData(data)
        lf_r.jsonPost(debug)


def removeEndps(baseurl, endp_names, debug=False):
    remove_endps(baseurl=baseurl, endp_names=endp_names, debug=debug)


def remove_endps(baseurl, endp_names, debug=False):
    if debug:
        logger.debug("Removing endp %s" % ", ".join(endp_names))
    url = "/cli-json/rm_endp"
    lf_r = LFRequest.LFRequest(baseurl, url, debug_=debug)
    for name in endp_names:
        data = {
            "endp_name": name
        }
        lf_r.addPostData(data)
        lf_r.jsonPost(debug)


def execWrap(cmd):
    exec_wrap(cmd=cmd)


def exec_wrap(cmd):
    if os.system(cmd) != 0:
        print("\nError with '" + cmd + "', bye\n")
        exit(1)


def expand_endp_histogram(distribution_payload=None):
    """
    Layer 3 endpoints can contain DistributionPayloads that appear like
     "rx-silence-5m" : {
               # "histo_category_width" : 1,
               # "histogram" : [
               #    221,
               #    113,
               #    266,
               #    615,
               #    16309,
               #    56853,
               #    7954,
               #    1894,
               #    29246,
               #    118,
               #    12,
               #    2,
               #    0,
               #    0,
               #    0,
               #    0
               # ],
               # "time window ms" : 300000,
               # "window avg" : 210.285,
               # "window max" : 228,
               # "window min" : 193

    These histogbrams are a set of linear categorys roughly power-of-two categories.
    :param distribution_payload: dictionary requiring histo_category_width and histogram
    :return: dictionary containing expanded category ranges and values for categories
    """
    if distribution_payload is None:
        return None
    if ("histogram" not in distribution_payload) \
            or ("histo_category_width" not in distribution_payload):
        logger.critical("Unexpected histogram format.")
        raise ValueError("Unexpected histogram format.")
    multiplier = int(distribution_payload["histo_category_width"])
    formatted_dict = {
        # "00000 <= x <= 00001" : "0"
    }
    for bucket_index in range(len(distribution_payload["histogram"]) - 1):
        pow1 = (2 ** bucket_index) * multiplier
        pow2 = (2 ** (bucket_index + 1)) * multiplier
        if bucket_index == 0:
            category_name = "00000 <= x <= {:-05.0f}".format(pow2)
        else:
            category_name = "{:-05.0f} < x <= {:-05.0f}".format(pow1, pow2)
        formatted_dict[category_name] = distribution_payload["histogram"][bucket_index]

    logger.info(pprint.pformat([("historgram", distribution_payload["histogram"]), ("formatted", formatted_dict)]))
    return formatted_dict
###

