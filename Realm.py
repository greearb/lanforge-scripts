#!/usr/bin/env python3
import os
import sys
import time
sys.path.append('py-json')
import json
import pprint
from LANforge import LFRequest
from LANforge import LFUtils


def jsonPost(mgrURL, reqURL, data, debug=False):
   lf_r = LFRequest.LFRequest(mgrURL + reqURL)
   lf_r.addPostData(data)
   json_response = lf_r.jsonPost(debug)
   LFUtils.debug_printer.pprint(json_response)
   sys.exit(1)
   
def getJsonReq(mgrURL, reqURL):
   lf_r = LFRequest.LFRequest(mgrURL + reqURL)
   json_response = lf_r.getAsJson(debugOn)
   return json_response


class Realm:

   def __init__(self, mgrURL="localhost:8080"):
      self.mgrURL = mgrURL

   def cxList(self):
      print("Not yet Implemented")

   def stationList(self):
      lf_r = LFRequest.LFRequest(self.mgrURL + "/port/list?fields=_links,alias")
      response = lf_r.getAsJson(False)
      print(response)

   def vapList(self):
      print("Not yet Implemented")

   def findPortsLike(self, pattern=""):
      print("Not yet Implemented")

class CxProfile:

	def addPorts(self, side, ports=[]):
	   print("Not yet Implemented")

	def create(self):
	   print("Not yet Implemented")


class StationProfile:

	def __init__(self, ssid="NA", ssidPass="NA", mode="open", up=True, dhcp=True):
		self.ssid = ssid
		self.ssidPass = ssidPass
		self.mode = mode
		self.up = up
		self.dhcp = dhcp

	def build(self, resourceRadio, numStations):
	   print("Not yet Implemented")      
