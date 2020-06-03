#!env /usr/bin/python

# Extend this class to use common set of debug and request features for your script
from pprint import pprint
import LANforge.LFUtils
from LANforge.LFUtils import *
import traceback
from traceback import extract_stack

class LFCliBase:
    # do not use `super(LFCLiBase,self).__init__(self, host, port, _debugOn)
    # that is py2 era syntax and will force self into the host variable, making you
    # very confused.
    def __init__(self, _lfjson_host, _lfjson_port, _debug=False):
        self.lfjson_host = _lfjson_host
        self.lfjson_port = _lfjson_port
        self.debugOn = _debug
        self.mgr_url = "http://%s:%s/" % (self.lfjson_host, self.lfjson_port)

    def jsonPost(self, _req_url, _data):
        json_response = None
        if self.mgr_url.endswith('/') and _req_url.startswith('/'):
            _req_url = _req_url[1:]
        try:
            lf_r = LFRequest.LFRequest(self.mgr_url + _req_url)
            _data['suppress_preexec_cli'] = True
            _data['suppress_preexec_method'] = True
            lf_r.addPostData(_data)
            if (self.debugOn):
                LANforge.LFUtils.debug_printer.pprint(_data)
            json_response = lf_r.jsonPost(self.debugOn)
        except Exception as x:
            print(f"jsonPost posted to {_req_url}")
            pprint(_data)
            print(x.__traceback__)

        # Debugging
        # if (json_response != None):
        #   print("jsonReq: response: ")
        #   LFUtils.debug_printer.pprint(vars(json_response))
        return json_response

    def jsonGet(self, _req_url):
        json_response = None
        if self.mgr_url.endswith('/') and _req_url.startswith('/'):
            _req_url = _req_url[1:]
        try:
            lf_r = LFRequest.LFRequest(self.mgr_url + _req_url)
            json_response = lf_r.getAsJson(self.debugOn)
            if (json_response is None) and self.debugOn:
                raise ValueError(json_response)
        except ValueError as ve:
            print("jsonGet asked for "+_req_url)
            print(ve.__traceback__)

        return json_response

    def checkConnect(self):
        print(f"Checking for LANforge GUI connection: {self.mgr_url}")
        response = self.jsonGet("/")
        duration = 0
        while (response is None) and (duration < 300):
            print(f"LANforge GUI connection not found sleeping 5 seconds, tried: {self.mgr_url}")
            duration += 2
            time.sleep(2)
            response = self.jsonGet("")

        if duration >= 300:
            print("Could not connect to LANforge GUI")
            sys.exit(1)

# ~class
