#!/usr/bin/env python3

import Realm


test = Realm.Realm("http://localhost:8080")

staList = test.stationList()
cxList = test.cxList()
vapList = test.vapList()


print(f"CXs: {cxList}\n")
print(f"Stations: {staList}\n")
print(f"VAPs: {vapList}\n")

cxTest = Realm.CXProfile()

cxTest.addPorts("A", "lf_udp", test.findPortsLike("sta+"))
cxTest.create()

print(test.findPortsLike("sta+"))

print(test.findPortsLike("sta0*"))

print(test.findPortsLike("sta[0000..0002]"))
