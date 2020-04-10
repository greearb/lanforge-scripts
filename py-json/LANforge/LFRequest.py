# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Class holds default settings for json requests                -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import email.message
import http.client
import urllib.request
import urllib.error
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
        resp = ''
        try:
            resp = urllib.request.urlopen(request);
            responses.append(resp)
            return responses[0]
        except urllib.error.HTTPError as error:
            if (show_error):
                print("----- formPost() HTTPError: --------------------------------------------")
                print("%s: %s; URL: %s"%(error.code, error.reason, request.get_full_url()))
                LFUtils.debug_printer.pprint(error.headers())
                #print("Error: ", sys.exc_info()[0])
                #print("Request URL:", request.get_full_url())
                print("Request Content-type:", request.get_header('Content-type'))
                print("Request Accept:", request.get_header('Accept'))
                print("Request Data:")
                LFUtils.debug_printer.pprint(request.data)
                if (len(responses) > 0):
                    print("----- Response: --------------------------------------------------------")
                    LFUtils.debug_printer.pprint(responses[0].reason)

                print("------------------------------------------------------------------------")
        except urllib.error.URLError as uerror:
            if (show_error):
                print("----- formPost() URLError: ---------------------------------------------")
                print("Reason: %s; URL: %s"%(uerror.reason, request.get_full_url()))
                print("------------------------------------------------------------------------")

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
            resp = urllib.request.urlopen(request);
            responses.append(resp)
            return responses[0]
        except urllib.error.HTTPError as error:
            if (show_error):
                print("----- jsonPost() HTTPError: --------------------------------------------")
                print("<%s> HTTP %s: %s"%(request.get_full_url(), error.code, error.reason, ))

                print("Error: ", sys.exc_info()[0])
                print("Request URL:", request.get_full_url())
                print("Request Content-type:", request.get_header('Content-type'))
                print("Request Accept:", request.get_header('Accept'))
                print("Request Data:")
                LFUtils.debug_printer.pprint(request.data)

                if (error.headers):
                    # the HTTPError is of type HTTPMessage a subclass of email.message
                    #print(type(error.keys()))
                    for headername in sorted(error.headers.keys()):
                        print ("Response %s: %s "%(headername, error.headers.get(headername)))

                if (len(responses) > 0):
                    print("----- Response: --------------------------------------------------------")
                    LFUtils.debug_printer.pprint(responses[0].reason)
                print("------------------------------------------------------------------------")
        except urllib.error.URLError as uerror:
            if (show_error):
                print("----- jsonPost() URLError: ---------------------------------------------")
                print("Reason: %s; URL: %s"%(uerror.reason, request.get_full_url()))
                print("------------------------------------------------------------------------")
        return None


    def get(self, show_error=True):
        myrequest = urllib.request.Request(url=self.requested_url, headers=self.default_headers)
        myresponses = []
        try:
            myresponses.append(urllib.request.urlopen(myrequest))
            return myresponses[0]
        except urllib.error.HTTPError as error:
            if (show_error):
                print("----- jsonPost() HTTPError: --------------------------------------------")
                print("<%s> HTTP %s: %s"%(myrequest.get_full_url(), error.code, error.reason, ))

                print("Error: ", sys.exc_info()[0])
                print("Request URL:", myrequest.get_full_url())
                print("Request Content-type:", myrequest.get_header('Content-type'))
                print("Request Accept:", myrequest.get_header('Accept'))
                print("Request Data:")
                LFUtils.debug_printer.pprint(myrequest.data)

                if (error.headers):
                    # the HTTPError is of type HTTPMessage a subclass of email.message
                    #print(type(error.keys()))
                    for headername in sorted(error.headers.keys()):
                        print ("Response %s: %s "%(headername, error.headers.get(headername)))

                if (len(myresponses) > 0):
                    print("----- Response: --------------------------------------------------------")
                    LFUtils.debug_printer.pprint(responses[0].reason)
                print("------------------------------------------------------------------------")
        except urllib.error.URLError as uerror:
            if (show_error):
                print("----- jsonPost() URLError: ---------------------------------------------")
                print("Reason: %s; URL: %s"%(uerror.reason, myrequest.get_full_url()))
                print("------------------------------------------------------------------------")
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
        json_data = json.loads(responses[0].read().decode('utf-8'))
        return json_data

    def addPostData(self, data):
        self.post_data = data

# ~LFRequest
