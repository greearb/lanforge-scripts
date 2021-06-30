#!/usr/bin/python3

# Create and modify WAN Links Using LANforge JSON AP : http://www.candelatech.com/cookbook.php?vol=cli&book=JSON:+Managing+WANlinks+using+JSON+and+Python

# Written by Candela Technologies Inc.
# Updated by:

import sys
import urllib

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import time
from time import sleep
from urllib import error
import pprint
import LANforge
from LANforge import LFRequest
from LANforge import LFUtils
from LANforge.LFUtils import NA

j_printer = pprint.PrettyPrinter(indent=2)
# typically you're using resource 1 in stand alone realm
resource_id = 1

def main(base_url="http://localhost:8080"):
   json_post = ""
   json_response = ""
   num_wanlinks = -1
   # see if there are old wanlinks to remove
   lf_r = LFRequest.LFRequest(base_url+"/wl/list")
   print(lf_r.get_as_json())

   port_a ="rd0a"
   port_b ="rd1a"
   try:
      json_response = lf_r.getAsJson()
      LFUtils.debug_printer.pprint(json_response)
      for key,value in json_response.items():
         if (isinstance(value, dict) and "_links" in value):
            num_wanlinks = 1
   except urllib.error.HTTPError as error:
      num_wanlinks = 0;

   # remove old wanlinks
   if (num_wanlinks > 0):
      lf_r = LFRequest.LFRequest(base_url+"/cli-json/rm_cx")
      lf_r.addPostData({
         'test_mgr': 'all',
         'cx_name': 'wl_eg1'
      })
      lf_r.jsonPost()
      sleep(0.05)

      lf_r = LFRequest.LFRequest(base_url+"/cli-json/rm_endp")
      lf_r.addPostData({
         'endp_name': 'wl_eg1-A'
      })
      lf_r.jsonPost()
      sleep(0.05)

      lf_r = LFRequest.LFRequest(base_url+"/cli-json/rm_endp")
      lf_r.addPostData({
         'endp_name': 'wl_eg1-B'
      })
      lf_r.jsonPost()
      sleep(0.05)

   # create wanlink 1a
   lf_r = LFRequest.LFRequest(base_url+"/cli-json/add_wl_endp")
   lf_r.addPostData({
      'alias': 'wl_eg1-A',
      'shelf': 1,
      'resource': '1',
      'port': port_a,
      'latency': '75',
      'max_rate': '128000',
      'description': 'cookbook-example'
   })
   lf_r.jsonPost()
   sleep(0.05)

   # create wanlink 1b
   lf_r = LFRequest.LFRequest(base_url+"/cli-json/add_wl_endp")
   lf_r.addPostData({
      'alias': 'wl_eg1-B',
      'shelf': 1,
      'resource': '1',
      'port': port_b,
      'latency': '95',
      'max_rate': '256000',
      'description': 'cookbook-example'
   })
   lf_r.jsonPost()
   sleep(0.05)

   # create cx
   lf_r = LFRequest.LFRequest(base_url+"/cli-json/add_cx")
   lf_r.addPostData({
      'alias': 'wl_eg1',
      'test_mgr': 'default_tm',
      'tx_endp': 'wl_eg1-A',
      'rx_endp': 'wl_eg1-B',
   })
   lf_r.jsonPost()
   sleep(0.05)

   # start wanlink once we see it
   seen = 0
   while (seen < 1):
      sleep(1)
      lf_r = LFRequest.LFRequest(base_url+"/wl/wl_eg1?fields=name,state,_links")
      try:
         json_response = lf_r.getAsJson()
         if (json_response is None):
            continue
         LFUtils.debug_printer.pprint(json_response)
         for key,value in json_response.items():
            if (isinstance(value, dict)):
               if ("_links" in value):
                  if (value["name"] == "wl_eg1"):
                     seen = 1
                  #else:
                  #   print(" name was not wl_eg1")
               #else:
               #   print("value lacks _links")
            #else:
            #   print("value not a dict")

      except urllib.error.HTTPError as error:
         print("Error code "+error.code)
         continue

   print("starting wanlink:")
   lf_r = LFRequest.LFRequest(base_url+"/cli-json/set_cx_state")
   lf_r.addPostData({
      'test_mgr': 'all',
      'cx_name': 'wl_eg1',
      'cx_state': 'RUNNING'
   })
   lf_r.jsonPost()


   running = 0
   while (running < 1):
      sleep(1)
      lf_r = LFRequest.LFRequest(base_url+"/wl/wl_eg1?fields=name,state,_links")
      try:
         json_response = lf_r.getAsJson()
         if (json_response is None):
            continue
         for key,value in json_response.items():
            if (isinstance(value, dict)):
               if ("_links" in value):
                  if (value["name"] == "wl_eg1"):
                     if (value["state"].startswith("Run")):
                        LFUtils.debug_printer.pprint(json_response)
                        running = 1

      except urllib.error.HTTPError as error:
         print("Error code "+error.code)
         continue

   print("Wanlink is running, wait one sec...")
   sleep(1)
   # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   # Now we can alter the delay and speed of the wanlink by
   # updating its endpoints see https://www.candelatech.com/lfcli_ug.php#set_wanlink_info
   # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   print("Updating Wanlink...")
   lf_r = LFRequest.LFRequest(base_url+"/cli-json/set_wanlink_info")
   lf_r.addPostData({
      'name': 'wl_eg1-A',
      'speed': 265333,
      'latency': 30,
      'reorder_freq': 3200,   # thats 3200/1000000
      'drop_freq': 2000,      #  2000/1000000
      'dup_freq': 1325,       #  1325/1000000
      'jitter_freq': 25125,   # 25125/1000000
   })
   lf_r.jsonPost()
   sleep(1)

   # stop wanlink
   lf_r = LFRequest.LFRequest(base_url+"/cli-json/set_cx_state")
   lf_r.addPostData({
      'test_mgr': 'all',
      'cx_name': 'wl_eg1',
      'cx_state': 'STOPPED'
   })
   lf_r.jsonPost()
   running = 1
   while (running > 0):
      sleep(1)
      lf_r = LFRequest.LFRequest(base_url+"/wl/wl_eg1?fields=name,eid,state,_links")
      LFUtils.debug_printer.pprint(json_response)
      try:
         json_response = lf_r.getAsJson()
         if (json_response is None):
            continue
         for key,value in json_response.items():
            if (isinstance(value, dict)):
               if ("_links" in value):
                  if (value["name"] == "wl_eg1"):
                     if (value["state"].startswith("Stop")):
                        LFUtils.debug_printer.pprint(json_response)
                        running = 0

      except urllib.error.HTTPError as error:
         print("Error code "+error.code)
         continue

   print("Wanlink is stopped.")

   print("Wanlink info:")
   lf_r = LFRequest.LFRequest(base_url+"/wl/wl_eg1")
   json_response = lf_r.getAsJson()
   LFUtils.debug_printer.pprint(json_response)

   lf_r = LFRequest.LFRequest(base_url+"/wl_ep/wl_eg1-A")
   json_response = lf_r.getAsJson()
   LFUtils.debug_printer.pprint(json_response)

   lf_r = LFRequest.LFRequest(base_url+"/wl_ep/wl_eg1-B")
   json_response = lf_r.getAsJson()
   LFUtils.debug_printer.pprint(json_response)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()

