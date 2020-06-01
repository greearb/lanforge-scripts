#!env /usr/bin/python

# Extend this class to use common set of debug and request features for your script

from LANforge.LFUtils import *


class LFCliBase:
    def __init__(self, lfjson_host="localhost", lfjson_port=8080, _debug=False):
        self.debugOn = _debug
        self.lfjson_host = lfjson_host
        self.lfjson_port = lfjson_port
        self.mgr_url = f"http://{self.lfjson_host}:{self.lfjson_port}/"

    def jsonPost(self, _req_url, _data):
        lf_r = LFRequest.LFRequest(self.mgr_url + _req_url)
        _data['suppress_preexec_cli'] = True
        _data['suppress_preexec_method'] = True
        lf_r.addPostData(_data)
        json_response = lf_r.jsonPost(self.debugOn)
        # Debugging
        # if (json_response != None):
        #   print("jsonReq: response: ")
        #   LFUtils.debug_printer.pprint(vars(json_response))
        return json_response

    def jsonGet(self, _req_url):
        lf_r = LFRequest.LFRequest(self.mgr_url + _req_url)
        json_response = lf_r.getAsJson(self.debugOn)
        return json_response

# ~class
