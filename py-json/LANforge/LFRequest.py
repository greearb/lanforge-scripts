# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Class holds default settings for json requests                -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

import pprint
import urllib
import time
import traceback
from urllib import request
from urllib import error
from urllib import parse

import json
from LANforge import LFUtils


class LFRequest:
    Default_Base_URL = "http://localhost:8080"
    No_Data = {'No Data':0}
    requested_url = ""
    post_data = No_Data
    default_headers = { 'Accept': 'application/json'}
    proxies = None

    def __init__(self, url=None,
                 uri=None,
                 proxies_=None,
                 debug_=False,
                 die_on_error_=False):
        self.debug = debug_
        self.die_on_error = die_on_error_;

        # please see this discussion on ProxyHandlers:
        # https://docs.python.org/3/library/urllib.request.html#urllib.request.ProxyHandler
        # but this makes much more sense:
        # https://gist.github.com/aleiphoenix/4159510

        # if debug_:
        #     if proxies_ is None:
        #         print("LFRequest_init_: no proxies_")
        #     else:
        #         print("LFRequest: proxies_: ")
        #         pprint.pprint(proxies_)

        if (proxies_ is not None) and (len(proxies_) > 0):
            if ("http" not in proxies_) and ("https" not in proxies_):
                raise ValueError("Neither http or https set in proxy definitions. Expects proxy={'http':, 'https':, }")
            self.proxies = proxies_

        # if debug_:
        #     if self.proxies is None:
        #         print("LFRequest_init_: no proxies")
        #     else:
        #         print("LFRequest: proxies: ")
        #         pprint.pprint(self.proxies)

        if not url.startswith("http://") and not url.startswith("https://"):
            print("No http:// or https:// found, prepending http:// to "+url)
            url = "http://" + url
        if uri is not None:
            if not url.endswith('/') and not uri.startswith('/'):
                url += '/'
            self.requested_url = url + uri
        else:
            self.requested_url = url

        if self.requested_url is None:
            raise Exception("Bad LFRequest of url[%s] uri[%s] -> None" % (url, uri))

        if self.requested_url.find('//'):
            protopos = self.requested_url.find("://")
            self.requested_url = self.requested_url[:protopos + 2] + self.requested_url[protopos + 2:].replace("//", "/")

        # finding '#' prolly indicates a macvlan (eth1#0)
        # finding ' ' prolly indicates a field name that should imply %20
        if (self.requested_url.find('#') >= 1):
            self.requested_url = self.requested_url.replace('#', '%23')
        if (self.requested_url.find(' ') >= 1):
            self.requested_url = self.requested_url.replace(' ', '+')
        if self.debug:
            print("new LFRequest[%s]" % self.requested_url )

    # request first url on stack
    def formPost(self, show_error=True, debug=False, die_on_error_=False):
        return self.form_post(show_error=show_error, debug=debug, die_on_error_=die_on_error_)

    def form_post(self, show_error=True, debug=False, die_on_error_=False):
        if self.die_on_error:
            die_on_error_ = True
        if (debug == False) and (self.debug == True):
            debug = True
        responses = []
        urlenc_data = ""
        # https://stackoverflow.com/a/59635684/11014343
        if (self.proxies is not None) and (len(self.proxies) > 0):
            # https://stackoverflow.com/a/59635684/11014343
            opener = request.build_opener(request.ProxyHandler(self.proxies))
            request.install_opener(opener)


        if (debug):
            print("formPost: url: "+self.requested_url)
        if ((self.post_data != None) and (self.post_data is not self.No_Data)):
            urlenc_data = urllib.parse.urlencode(self.post_data).encode("utf-8")
            if (debug):
                print("formPost: data looks like:" + str(urlenc_data))
                print("formPost: url: "+self.requested_url)
            myrequest = request.Request(url=self.requested_url,
                                                data=urlenc_data,
                                                headers=self.default_headers)
        else:
            myrequest = request.Request(url=self.requested_url, headers=self.default_headers)
            print("No data for this formPost?")

        myrequest.headers['Content-type'] = 'application/x-www-form-urlencoded'

        resp = ''
        try:
            resp = urllib.request.urlopen(myrequest)
            responses.append(resp)
            return responses[0]
        except urllib.error.HTTPError as error:
            if (show_error):
                print("----- LFRequest::formPost:76 HTTPError: --------------------------------------------")
                print("%s: %s; URL: %s"%(error.code, error.reason, myrequest.get_full_url()))
                LFUtils.debug_printer.pprint(error.headers)
                #print("Error: ", sys.exc_info()[0])
                #print("Request URL:", request.get_full_url())
                print("Request Content-type:", myrequest.get_header('Content-type'))
                print("Request Accept:", myrequest.get_header('Accept'))
                print("Request Data:")
                LFUtils.debug_printer.pprint(myrequest.data)
                if (len(responses) > 0):
                    print("----- Response: --------------------------------------------------------")
                    LFUtils.debug_printer.pprint(responses[0].reason)

                print("------------------------------------------------------------------------")
                if die_on_error_:
                    exit(1)
        except urllib.error.URLError as uerror:
            if show_error:
                print("----- LFRequest::formPost:94 URLError: ---------------------------------------------")
                print("Reason: %s; URL: %s"%(uerror.reason, myrequest.get_full_url()))
                print("------------------------------------------------------------------------")
                if (die_on_error_ == True) or (self.die_on_error == True):
                    exit(1)
        return None

    def jsonPost(self, show_error=True, debug=False, die_on_error_=False, response_json_list_=None):
        return self.json_post(show_error=show_error, debug=debug, die_on_error_=die_on_error_, response_json_list_=response_json_list_)

    def json_post(self, show_error=True, debug=False, die_on_error_=False, response_json_list_=None, method_='POST'):
        if (debug == False) and (self.debug == True):
            debug = True
        if self.die_on_error:
            die_on_error_ = True
        responses = []
        if (self.proxies is not None) and (len(self.proxies) > 0):
            opener = request.build_opener(request.ProxyHandler(self.proxies))
            request.install_opener(opener)

        if ((self.post_data != None) and (self.post_data is not self.No_Data)):
            myrequest = request.Request(url=self.requested_url,
                                         method=method_,
                                         data=json.dumps(self.post_data).encode("utf-8"),
                                         headers=self.default_headers)
        else:
            myrequest = request.Request(url=self.requested_url, headers=self.default_headers)
            print("No data for this jsonPost?")

        myrequest.headers['Content-type'] = 'application/json'

        # https://stackoverflow.com/a/59635684/11014343

        try:
            resp = request.urlopen(myrequest)
            resp_data = resp.read().decode('utf-8')
            if (debug and die_on_error_):
                print("----- LFRequest::json_post:128 debug: --------------------------------------------")
                print("URL: %s :%d "% (self.requested_url, resp.status))
                if resp.status != 200:
                    LFUtils.debug_printer.pprint(resp.getheaders())
                print("----- resp_data:128 -------------------------------------------------")
                print(resp_data)
                print("-------------------------------------------------")
            responses.append(resp)
            if response_json_list_ is not None:
                if type(response_json_list_) is not list:
                    raise ValueError("reponse_json_list_ needs to be type list")
                j = json.loads(resp_data)
                if debug:
                    print("----- LFRequest::json_post:140 debug: --------------------------------------------")
                    LFUtils.debug_printer.pprint(j)
                    print("-------------------------------------------------")
                response_json_list_.append(j)
            return responses[0]
        except urllib.error.HTTPError as error:
            if show_error or die_on_error_ or (error.code != 404):
                print("----- LFRequest::json_post:147 HTTPError: --------------------------------------------")
                print("<%s> HTTP %s: %s" % (myrequest.get_full_url(), error.code, error.reason ))

                print("Error: ", sys.exc_info()[0])
                print("Request URL:", myrequest.get_full_url())
                print("Request Content-type:", myrequest.get_header('Content-type'))
                print("Request Accept:", myrequest.get_header('Accept'))
                print("Request Data:")
                LFUtils.debug_printer.pprint(myrequest.data)

                if error.headers:
                    # the HTTPError is of type HTTPMessage a subclass of email.message
                    # print(type(error.keys()))
                    for headername in sorted(error.headers.keys()):
                        print ("Response %s: %s "%(headername, error.headers.get(headername)))

                if len(responses) > 0:
                    print("----- Response: --------------------------------------------------------")
                    LFUtils.debug_printer.pprint(responses[0].reason)
                print("------------------------------------------------------------------------")
            if die_on_error_:
                traceback.print_stack(limit=15)
                exit(1)
        except urllib.error.URLError as uerror:
            if show_error:
                print("----- LFRequest::json_post:171 URLError: ---------------------------------------------")
                print("Reason: %s; URL: %s"%(uerror.reason, myrequest.get_full_url()))
                print("------------------------------------------------------------------------")
                if (die_on_error_ == True) or (self.die_on_error == True):
                    traceback.print_stack(limit=15)
                    exit(1)
        return None

    def json_put(self, show_error=True, debug=False, die_on_error_=False, response_json_list_=None):
       return self.json_post(show_error=show_error,
                             debug=debug,
                             die_on_error_=die_on_error_,
                             response_json_list_=response_json_list_,
                             method_='PUT')

    def json_delete(self, show_error=True, debug=False, die_on_error_=False, response_json_list_=None):
       return self.get_as_json(debug_=debug,
                             die_on_error_=die_on_error_,
                             method_='DELETE')

    def get(self, debug=False, die_on_error_=False, method_='GET'):
        if self.debug == True:
            debug = True
        if self.die_on_error == True:
            die_on_error_ = True
        if debug:
            print("LFUtils.get: url: "+self.requested_url)

        # https://stackoverflow.com/a/59635684/11014343
        if (self.proxies is not None) and (len(self.proxies) > 0):
            opener = request.build_opener(request.ProxyHandler(self.proxies))
            #opener = urllib.request.build_opener(myrequest.ProxyHandler(self.proxies))
            request.install_opener(opener)

        myrequest = request.Request(url=self.requested_url,
                                   headers=self.default_headers,
                                   method=method_)
        myresponses = []
        try:
            myresponses.append(request.urlopen(myrequest))
            return myresponses[0]
        except urllib.error.HTTPError as error:
            if debug:
                if error.code == 404:
                    print("HTTP 404: <%s>" % myrequest.get_full_url())
                else:
                    print("----- LFRequest::get:181 HTTPError: --------------------------------------------")
                    print("<%s> HTTP %s: %s"%(myrequest.get_full_url(), error.code, error.reason, ))
                    print("Error: ", sys.exc_info()[0])
                    print("E Request URL:", myrequest.get_full_url())
                    print("E Request Content-type:", myrequest.get_header('Content-type'))
                    print("E Request Accept:", myrequest.get_header('Accept'))
                    print("E Request Data:")
                    LFUtils.debug_printer.pprint(myrequest.data)
                if (error.code != 404) and error.headers:
                    # the HTTPError is of type HTTPMessage a subclass of email.message
                    # print(type(error.keys()))
                    for headername in sorted(error.headers.keys()):
                        print ("H Response %s: %s "%(headername, error.headers.get(headername)))
                if (error.code != 404) and (len(myresponses) > 0):
                    print("----- Response: --------------------------------------------------------")
                    LFUtils.debug_printer.pprint(myresponses[0].reason)
                    print("------------------------------------------------------------------------")
                if (error.code != 404) and (die_on_error_ == True):
                    traceback.print_stack(limit=15)
                    exit(1)
        except urllib.error.URLError as uerror:
            if debug:
                print("----- LFRequest::get:205 URLError: ---------------------------------------------")
                print("Reason: %s; URL: %s"%(uerror.reason, myrequest.get_full_url()))
                print("------------------------------------------------------------------------")
                if die_on_error_ == True:
                    traceback.print_stack(limit=15)
                    exit(1)
        return None

    def getAsJson(self, die_on_error_=False, debug_=False):
        return self.get_as_json(die_on_error_=die_on_error_, debug_=debug_)

    def get_as_json(self, die_on_error_=False, debug_=False, method_='GET'):
        responses = []
        j = self.get(debug=debug_, die_on_error_=die_on_error_, method_=method_)
        responses.append(j)
        if len(responses) < 1:
            return None
        if responses[0] == None:
            if debug_:
                print("No response from "+self.requested_url)
            return None
        json_data = json.loads(responses[0].read().decode('utf-8'))
        return json_data

    def addPostData(self, data):
        self.add_post_data(data=data)

    def add_post_data(self, data):
        self.post_data = data


def plain_get(url_=None, debug_=False, die_on_error_=False, proxies_=None):
    """
    This static method does not respect LFRequest.proxy, it is not set in scope here
    :param url_:
    :param debug_:
    :param die_on_error_:
    :return:
    """
    myrequest = request.Request(url=url_)
    myresponses = []
    try:
        if (proxies_ is not None) and (len(proxies_) > 0):
            # https://stackoverflow.com/a/59635684/11014343
            opener = myrequest.build_opener(myrequest.ProxyHandler(proxies_))
            myrequest.install_opener(opener)

        myresponses.append(request.urlopen(myrequest))
        return myresponses[0]

    except urllib.error.HTTPError as error:
        if debug_:
            print("----- LFRequest::get:181 HTTPError: --------------------------------------------")
            print("<%s> HTTP %s: %s"%(myrequest.get_full_url(), error.code, error.reason))
            if error.code != 404:
                print("Error: ", sys.exc_info()[0])
                print("Request URL:", myrequest.get_full_url())
                print("Request Content-type:", myrequest.get_header('Content-type'))
                print("Request Accept:", myrequest.get_header('Accept'))
                print("Request Data:")
                LFUtils.debug_printer.pprint(myrequest.data)

            if error.headers:
                # the HTTPError is of type HTTPMessage a subclass of email.message
                # print(type(error.keys()))
                for headername in sorted(error.headers.keys()):
                    print ("Response %s: %s "%(headername, error.headers.get(headername)))

            if len(myresponses) > 0:
                print("----- Response: --------------------------------------------------------")
                LFUtils.debug_printer.pprint(myresponses[0].reason)
            print("------------------------------------------------------------------------")
            if die_on_error_ == True:
                # print("--------------------------------------------- s.doe %s v doe %s ---------------------------" % (self.die_on_error, die_on_error_))
                exit(1)
    except urllib.error.URLError as uerror:
        if debug_:
            print("----- LFRequest::get:205 URLError: ---------------------------------------------")
            print("Reason: %s; URL: %s"%(uerror.reason, myrequest.get_full_url()))
            print("------------------------------------------------------------------------")
            if die_on_error_ == True:
                exit(1)
    return None


# ~LFRequest
