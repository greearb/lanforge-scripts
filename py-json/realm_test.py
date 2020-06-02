#!/usr/bin/env python3

import realm


test = realm.Realm("http://localhost:8080")

sta_list = test.station_list()
cx_list = test.cx_list()
vap_list = test.vap_list()


print(f"CXs: {cx_list}\n")
print(f"Stations: {sta_list}\n")
print(f"VAPs: {vap_list}\n")

cxTest = realm.CXProfile()

cxTest.add_ports("A", "lf_udp", test.find_ports_like("sta+"))
cxTest.create()

print(test.find_ports_like("sta+"))

print(test.find_ports_like("sta0*"))

print(test.find_ports_like("sta[0000..0002]"))
