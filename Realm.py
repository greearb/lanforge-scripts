#!/usr/bin/env python3
import os
import sys
import time
sys.path.append('py-json')
import json
import pprint
from LANforge import LFRequest
from LANforge import LFUtils
import re

def jsonPost(mgrURL, reqURL, data, debug=False):
   lf_r = LFRequest.LFRequest(mgrURL + reqURL)
   lf_r.addPostData(data)
   json_response = lf_r.jsonPost(debug)
   LFUtils.debug_printer.pprint(json_response)
   sys.exit(1)


class Realm:

   def __init__(self, mgrURL="localhost:8080"):
      self.mgrURL = mgrURL

   def cxList(self):
      #Returns json response from webpage of all layer 3 cross connects
      lf_r = LFRequest.LFRequest(self.mgrURL + "/cx")
      response = lf_r.getAsJson(True)
      return response

   def stationList(self):
      #Returns list of all stations with "sta" in their name
      list = []
      lf_r = LFRequest.LFRequest(self.mgrURL + "/port/list?fields=_links,alias")
      response = lf_r.getAsJson(True)

      for x in range(len(response['interfaces'])):
         for k,v in response['interfaces'][x].items():
            if "sta" in v['alias']:
               list.append(response['interfaces'][x])

      return list

   def vapList(self):
      #Returns list of all VAPs with "vap" in their name
      list = []
      lf_r = LFRequest.LFRequest(self.mgrURL + "/port/list?fields=_links,alias")
      response = lf_r.getAsJson(True)

      for x in range(len(response['interfaces'])):
         for k,v in response['interfaces'][x].items():
            if "vap" in v['alias']:
               list.append(response['interfaces'][x])

      return list


   def findPortsLike(self, pattern=""):
      #Searches for ports that match a given pattern and returns a list of names
      list = []
      lf_r = LFRequest.LFRequest(self.mgrURL + "/port/list?fields=_links,alias")
      response = lf_r.getAsJson(True)
      for x in range(len(response['interfaces'])):
         for k,v in response['interfaces'][x].items():
            if v['alias'] != "NA":
               list.append(v['alias'])

      matchedList = []

      for name in list:
         if (pattern.index("+") > 0):
            match1 = re.search(r"^[^+]+[+]$", name)
            if match1:
               print(match1)
               matchedList.append(name)
         elif (pattern.index("*") > 0):
            match2 = re.search(r"^[^\*]+[\*]$", name)
            if match2:
               print(match2)
               matchedList.append(name)
            if (pattern.index("[") > 0):
               match3 = re.search(r"^[\[]+\[\d+\.\.\d+\]$", name)
               if match3:
                  print(match3)
                  matchedList.append(name)

      return matchedList

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
	   print("Not yet implemented") 
