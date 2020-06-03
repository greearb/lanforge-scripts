#!/usr/bin/env python3
import pprint
from pprint import pprint
import realm
from realm import Realm

localrealm = Realm("localhost", 8080, True)

print("** Existing Stations **")
try:
    sta_list = localrealm.station_list()
    print(f"{len(sta_list)} Stations:")
    pprint(sta_list)
    print(localrealm.find_ports_like("sta+"))
    print(localrealm.find_ports_like("sta0*"))
    print(localrealm.find_ports_like("sta[0000..0002]"))
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

print("** Removing previous CXs **")

print("** Creating Stations **")

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
