#!/usr/bin/env python3
import pprint
import time
from pprint import pprint
import realm
from realm import Realm
import LANforge
from LANforge import LFUtils

localrealm = Realm("localhost", 8080, True)

print("** Existing Stations **")
try:
    sta_list = localrealm.station_list()
    print(f"{len(sta_list)} Stations:")
    pprint(sta_list)
    print("  Stations like sta+:")
    print(localrealm.find_ports_like("wlan+"))
    print("  Stations like sta0:")
    print(localrealm.find_ports_like("wlan0*"))
    print("  Stations between wlan0..wlan2:")
    print(localrealm.find_ports_like("wlan[0..2]"))
except Exception as x:
    pprint(x)
    exit(1)

print("** Existing vAPs **")
try:
    vap_list = localrealm.vap_list()
    print(f"{len(vap_list)} VAPs:")
    pprint(vap_list)
except Exception as x:
    pprint(x)
    exit(1)

print("** Existing CXs **")
try:
    cx_list = localrealm.cx_list()
    print(f"{len(cx_list)} CXs:")
    pprint(cx_list)
except Exception as x:
    pprint(x)
    exit(1)

print("** Removing previous stations **")
stations = localrealm.find_ports_like("sta+")
for station in stations:
    pprint(station)
    time.sleep(1)
    LFUtils.removePort(station["resource"], station["name"], localrealm.lfclient_url)

print("** Removing previous CXs **")

print("** Creating Stations **")

try:
    sta_list = localrealm.station_list()
    print(f"{len(sta_list)} Stations:")
    pprint(sta_list)
    print("  Stations like sta+:")
    print(localrealm.find_ports_like("wlan+"))
    print("  Stations like sta0:")
    print(localrealm.find_ports_like("wlan0*"))
    print("  Stations between wlan0..wlan2:")
    print(localrealm.find_ports_like("wlan[0..2]"))
except Exception as x:
    pprint(x)
    exit(1)

print("** Creating CXs **")
try:
    cxProfile = localrealm.newCXProfile()
    # set attributes of cxProfile
    cxProfile.add_ports("A", "lf_udp", localrealm.find_ports_like("sta+"))
    cxProfile.create()
except Exception as x:
    pprint(x)
    exit(1)

#
