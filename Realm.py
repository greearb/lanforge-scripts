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

   def __init__(self, mgrURL="http://localhost:8080"):
      self.mgrURL = mgrURL

   def cxList(self):
      #Returns json response from webpage of all layer 3 cross connects
      lf_r = LFRequest.LFRequest(self.mgrURL + "/cx")
      response = lf_r.getAsJson(True)
      return response

   def stationList(self):
      #Returns list of all stations with "sta" in their name
      list = []
      lf_r = LFRequest.LFRequest(self.mgrURL + "/port/list?fields=_links,alias,device,port+type")
      response = lf_r.getAsJson(True)
      for x in range(len(response['interfaces'])):
         for k,v in response['interfaces'][x].items():
            if "sta" in v['device']:
               list.append(response['interfaces'][x])

      return list

   def vapList(self):
      #Returns list of all VAPs with "vap" in their name
      list = []
      lf_r = LFRequest.LFRequest(self.mgrURL + "/port/list?fields=_links,alias,device,port+type")
      response = lf_r.getAsJson(True)

      for x in range(len(response['interfaces'])):
         for k,v in response['interfaces'][x].items():
            if "vap" in v['device']:
               list.append(response['interfaces'][x])

      return list


   def findPortsLike(self, pattern=""):
      #Searches for ports that match a given pattern and returns a list of names
      list = []
      # alias is possible but device is gauranteed
      lf_r = LFRequest.LFRequest(self.mgrURL + "/port/list?fields=_links,alias,device,port+type")
      response = lf_r.getAsJson(True)
      #print(response)
      for x in range(len(response['interfaces'])):
         for k,v in response['interfaces'][x].items():
            if v['device'] != "NA":
               list.append(v['device'])

      matchedList = []

      prefix = ""
      for portname in list:
         try:
            if (pattern.index("+") > 0):

                  match = re.search(r"^([^+]+)[+]$", pattern)
                  if match.group(1):
                     print("name:", portname, " Group 1: ",match.group(1))
                     prefix = match.group(1)
                     if (portname.index(prefix) == 0):
                        matchedList.append(portname)

            elif (pattern.index("*") > 0):
                  match = re.search(r"^([^\*]+)[\*]$", pattern)
                  if match.group(1):
                     prefix = match.group(1)
                     print("group 1: ",prefix)
                     if (portname.index(prefix) == 0):
                        matchedList.append(portname)

            elif (pattern.index("[") > 0):
                  match = re.search(r"^([^\[]+)\[(\d+)\.\.(\d+)\]$", pattern)
                  if match.group(0):
                     print("[group1]: ", match.group(1))
                     prefix = match.group(1)
                     if (portname.index(prefix)):
                        matchedList.append(portname) # wrong but better
         except ValueError as e:
            print(e)
      return matchedList

class CXProfile:

   def __init__(self, mgrURL="http://localhost:8080"):
      self.mgrURL = mgrURL
      self.postData = []

   def addPorts(self, side, endpType, ports=[]):
   #Adds post data for a cross-connect between eth1 and specified list of ports, appends to array
      side = side.upper()
      endpSideA = {
      "alias":"",
      "shelf":1,
      "resource":1,
      "port":"",
      "type":endpType,
      "min_rate":0,
      "max_rate":0,
      "min_pkt":-1,
      "max_pkt":0
       }

      endpSideB = {
      "alias":"",
      "shelf":1,
      "resource":1,
      "port":"",
      "type":endpType,
      "min_rate":0,
      "max_rate":0,
      "min_pkt":-1,
      "max_pkt":0
      }

      for portName in ports:
         if side == "A":
            endpSideA["alias"] = portName+"CX-A"
            endpSideA["port"] = portName
            endpSideB["alias"] = portName+"CX-B"
            endpSideB["port"] = "eth1"
         elif side == "B":
            endpSideA["alias"] = portName+"CX-A"
            endpSideA["port"] = "eth1"
            endpSideB["alias"] = portName+"CX-B"
            endpSideB["port"] = portName

         lf_r = LFRequest.LFRequest(self.mgrURL + "/cli-json/add_endp")
         lf_r.addPostData(endpSideA)
         json_response = lf_r.jsonPost(True)
         lf_r.addPostData(endpSideB)
         json_response = lf_r.jsonPost(True)
         #LFUtils.debug_printer.pprint(json_response)
         time.sleep(.5)


         data = {
         "alias":portName+"CX",
         "test_mgr":"default_tm",
         "tx_endp":portName + "CX-A",
         "rx_endp":portName + "CX-B"
         }

         self.postData.append(data)

   def create(self, sleepTime=.5):
   #Creates cross-connect for each port specified in the addPorts function
      for data in self.postData:
         lf_r = LFRequest.LFRequest(self.mgrURL + "/cli-json/add_cx")
         lf_r.addPostData(data)
         json_response = lf_r.jsonPost(True)
         LFUtils.debug_printer.pprint(json_response)
         time.sleep(sleepTime)


class StationProfile:

   def __init__(self, ssid="NA", ssidPass="NA", mode="open", up=True, dhcp=True):
      self.ssid = ssid
      self.ssidPass = ssidPass
      self.mode = mode
      self.up = up
      self.dhcp = dhcp

   def build(self, resourceRadio, numStations):
	   print("Not yet implemented") 

