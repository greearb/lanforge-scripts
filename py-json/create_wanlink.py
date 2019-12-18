#!/usr/bin/python3
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# example of how to create a WAN Link using JSON                              -
#                                                                             -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import sys
if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import time
from time import sleep
import pprint
import LANforge
from LANforge import LFRequest
from LANforge import LFUtils
from LANforge.LFUtils import NA

j_printer = pprint.PrettyPrinter(indent=2)
# typically you're using resource 1 in stand alone realm
resource_id = 1

def main():
   base_url = "http://localhost:8080"
   json_post = ""
   json_response = ""

   # remove old wanlinks
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
      'port': 'eth3',
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
      'port': 'eth5',
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

   # start wanlink
   lf_r = LFRequest.LFRequest(base_url+"/cli-json/set_cx_state")
   lf_r.addPostData({
      'test_mgr' = 'all',
      'cx_name' = 'wl_eg1',
      'cx_state' = 'RUNNING'
   })
   lf_r.jsonPost()
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
      'test_mgr' = 'all',
      'cx_name' = 'wl_eg1',
      'cx_state' = 'STOPPED'
   })
   lf_r.jsonPost()
   print("Wanlink is stopped.")

   print("Wanlink info:")
   json_response = LFResponse.LFRequest(base_url+"/")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()

###
###