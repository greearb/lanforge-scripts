#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Class holds default settings for json requests               -
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import urllib.request
import json

class LFRequest:
   Default_Base_URL = "http://localhost:8080"
   requested_urls = []
   default_headers = {
      'Accept': 'application/json' }


   def __init__(self, urls):
      self.requested_urls.append(urls)

   # request first url on stack
   def get(self):
      myrequest = urllib.request.Request(url=self.requested_urls.pop(0), headers=self.default_headers)
      myresponse = urllib.request.urlopen(myrequest)

      #print(json_response)
      return myresponse

   def getAsJson(self):
      response = self.get();
      json_data = json.loads(response.read())
      return json_data

# ~LFRequest
