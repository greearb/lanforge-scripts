# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Class holds default settings for json requests               -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import urllib.request
import urllib.parse
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
   def formPost(self):
      responses = []
      urlenc_data = ""
      if ((len(self.post_datas) > 0) and (self.post_datas[0] != None)):
         urlenc_data = urllib.parse.urlencode(self.post_datas.pop(0)).encode("utf-8")
         print("data looks like:"+str(urlenc_data))
         request = urllib.request.Request(url=self.requested_urls.pop(0),
                                          data=urlenc_data,
                                          headers=self.default_headers)
      else:
         request = urllib.request.Request(url=self.requested_urls.pop(0), headers=self.default_headers)
         print("No data for this jsonPost?")

      request.headers['Content-type'] = 'application/x-www-form-urlencoded'
      responses.append(urllib.request.urlopen(request))
      return responses[0]

   def jsonPost(self):
      responses = []
      if ((len(self.post_datas) > 0) and (self.post_datas[0] != None)):
         request = urllib.request.Request(url=self.requested_urls.pop(0),
                                          data=self.post_datas.pop(0),
                                          headers=self.default_headers)
      else:
         request = urllib.request.Request(url=self.requested_urls.pop(0), headers=self.default_headers)
         print("No data for this jsonPost?")

      request.headers['Content-type'] = 'application/json'
      responses.append(urllib.request.urlopen(request))
      return responses[0]

   def get(self):
      myrequest = urllib.request.Request(url=self.requested_urls.pop(0), headers=self.default_headers)
      myresponses = []
      #print(responses[0].__dict__.keys()) is how you would see parts of response
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

      if ((responses[0] == None) or (responses[0].status != 200)):
         print("Item not found")
         return None

      json_data = json.loads(responses[0].read())
      return json_data

   def addPostData(self, post_data):
      self.post_datas.append(post_data)

# ~LFRequest
