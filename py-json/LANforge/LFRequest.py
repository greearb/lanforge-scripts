# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Class holds default settings for json requests                -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import urllib.request
from urllib import error
import urllib.parse
import json
import LANforge
from LANforge import LFUtils

class LFRequest:
    Default_Base_URL = "http://localhost:8080"
    No_Data = {'No Data':0}
    requested_url = ""
    post_data = No_Data
    default_headers = {
        'Accept': 'application/json'}

    def __init__(self, url):
        self.requested_url = url

    # request first url on stack
    def formPost(self, show_error=True):
        responses = []
        urlenc_data = ""
        if ((self.post_data != None) and (self.post_data is not self.No_Data)):
            urlenc_data = urllib.parse.urlencode(self.post_data).encode("utf-8")
            #print("data looks like:" + str(urlenc_data))
            request = urllib.request.Request(url=self.requested_url,
                                             data=urlenc_data,
                                             headers=self.default_headers)
        else:
            request = urllib.request.Request(url=self.requested_url, headers=self.default_headers)
            print("No data for this jsonPost?")

        request.headers['Content-type'] = 'application/x-www-form-urlencoded'
        try:
            responses.append(urllib.request.urlopen(request))
            return responses[0]
        except urllib.error.HTTPError as error:
            if (show_error):
                print("-------------------------------------------------------------")
                print("%s URL: %s"%(error.code, request.get_full_url()))
                #print("Error: ", sys.exc_info()[0])
                print("Request URL:", request.get_full_url())
                print("Request Content-type:", request.get_header('Content-type'))
                print("Request Accept:", request.get_header('Accept'))
                print("Request Data:")
                LFUtils.debug_printer.pprint(request.data)
                if (len(responses) > 0):
                    print("-------------------------------------------------------------")
                    print("Response:")
                    LFUtils.debug_printer.pprint(responses[0].reason)
                    print("-------------------------------------------------------------")

        return None

    def jsonPost(self, show_error=True):
        responses = []
        if ((self.post_data != None) and (self.post_data is not self.No_Data)):
            request = urllib.request.Request(url=self.requested_url,
                                             data=json.dumps(self.post_data).encode("utf-8"),
                                             headers=self.default_headers)
        else:
            request = urllib.request.Request(url=self.requested_url, headers=self.default_headers)
            print("No data for this jsonPost?")

        request.headers['Content-type'] = 'application/json'
        try:
            responses.append(urllib.request.urlopen(request))
            return responses[0]
        except urllib.error.HTTPError as error:
            if (show_error):
                print("-------------------------------------------------------------")
                print("%s URL: %s"%(error.code, request.get_full_url()))
                #print("Error: ", sys.exc_info()[0])
                print("Request URL:", request.get_full_url())
                print("Request Content-type:", request.get_header('Content-type'))
                print("Request Accept:", request.get_header('Accept'))
                print("Request Data:")
                LFUtils.debug_printer.pprint(request.data)
                if (len(responses) > 0):
                    print("-------------------------------------------------------------")
                    print("Response:")
                    LFUtils.debug_printer.pprint(responses[0].reason)
                    print("-------------------------------------------------------------")
        return None


    def get(self, show_error=True):
        myrequest = urllib.request.Request(url=self.requested_url, headers=self.default_headers)
        myresponses = []
        try:
            myresponses.append(urllib.request.urlopen(myrequest))
            return myresponses[0]
        except:
            if (show_error):
                print("Url: "+myrequest.get_full_url())
                print("Error: ", sys.exc_info()[0])

        return None

    def getAsJson(self, show_error=True):
        responses = []
        responses.append(self.get(show_error))
        if (len(responses) < 1):
            return None
        if (responses[0] == None):
            if (show_error):
                print("No response from "+self.requested_url)
            return None
        json_data = json.loads(responses[0].read())
        return json_data

    def addPostData(self, data):
        self.post_data = data

# ~LFRequest
