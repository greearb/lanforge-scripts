# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Class holds default settings for json requests               -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import urllib.request
import json


class LFRequest:
   Default_Base_URL = "http://localhost:8080"
   requested_urls = []
   post_datas = []
   default_headers = {
      'Accept': 'application/json'}

   def __init__(self, urls):
      self.requested_urls.append(urls)

   # request first url on stack
   def post(self):
      try:
         myrequest = urllib.request.Request(url=self.requested_urls.pop(0), headers=self.default_headers)
         if ((len(self.post_datas) > 0) and (self.post_datas[0] != None)):
            myrequest.data = self.post_datas.pop(0)
            myrequest.headers['Content-type'] = 'application/json'

         myresponse = urllib.request.urlopen(myrequest)
         # print(json_response)
         return myresponse
      finally:
         print("Error: %s" % myresponse.error_code)

   def get(self):
      myrequest = urllib.request.Request(url=self.requested_urls.pop(0), headers=self.default_headers)
      myresponses = []
      try:
         myresponses.append(urllib.request.urlopen(myrequest))
         return myresponses[0]

      except:
         print("Error: ", sys.exc_info()[0])

      return None



   def getAsJson(self):
      responses = []
      responses.append(self.get())
      if (len(responses) < 1):
         return None

      if ((responses[0] == None) or (responses[0].status_code != 200)):
         print("Item not found")
         return None

      json_data = json.loads(responses[0].read())
      return json_data

   def addPostData(self, post_data):
      self.post_datas.append(post_data)

# ~LFRequest
