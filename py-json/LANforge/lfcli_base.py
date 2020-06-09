#!env /usr/bin/python

import traceback
# Extend this class to use common set of debug and request features for your script
from pprint import pprint

import LANforge.LFUtils
from LANforge.LFUtils import *
import realm
from realm import Realm

class LFCliBase:
    # do not use `super(LFCLiBase,self).__init__(self, host, port, _debugOn)
    # that is py2 era syntax and will force self into the host variable, making you
    # very confused.
    def __init__(self, _lfjson_host, _lfjson_port, _debug=False, _halt_on_error=False):
        self.fail_pref = "FAILED: "
        self.pass_pref = "PASSED: "
        self.lfjson_host = _lfjson_host
        self.lfjson_port = _lfjson_port
        self.debugOn = _debug
        self.haltOnError = _halt_on_error
        self.mgr_url = "http://%s:%s" % (self.lfjson_host, self.lfjson_port)
        self.test_results = []
        self.realm = Realm(_lfjson_host, _lfjson_port, debug=_debug)

    def clear_test_results(self):
        self.test_results.clear()

    def json_post(self, _req_url, _data):
        json_response = None
        try:
            lf_r = LFRequest.LFRequest(self.mgr_url, _req_url, debug_=self.debugOn)
            _data['suppress_preexec_cli'] = True
            _data['suppress_preexec_method'] = True
            lf_r.addPostData(_data)
            if (self.debugOn):
                LANforge.LFUtils.debug_printer.pprint(_data)
            json_response = lf_r.jsonPost(show_error=self.debugOn, debug=self.debugOn)
        except Exception as x:
            if self.debugOn or self.haltOnError:
                print("jsonPost posted to %s" % _req_url)
                pprint(_data)
                print("Exception %s:" % x)
                traceback.print_exception(Exception, x, x.__traceback__, chain=True)
            if self.haltOnError:
                exit(1)

        return json_response

    def json_get(self, _req_url):
        if self.debugOn:
            print("URL: "+_req_url)
        json_response = None
        try:
            lf_r = LFRequest.LFRequest(self.mgr_url, _req_url)
            json_response = lf_r.getAsJson(self.debugOn)
            #debug_printer.pprint(json_response)
            if (json_response is None) and self.debugOn:
                raise ValueError(json_response)
        except ValueError as ve:
            if self.debugOn or self.haltOnError:
                print("jsonGet asked for " + _req_url)
                print("Exception %s:" % ve)
                traceback.print_exception(ValueError, ve, ve.__traceback__, chain=True)
            if self.haltOnError:
                sys.exit(1)

        return json_response

    def error(self, exception):
        # print("lfcli_base error: %s" % exception)
        pprint.pprint(exception)
        traceback.print_exception(Exception, exception, exception.__traceback__, chain=True)
        if self.haltOnError:
            print("halting on error")
            sys.exit(1)
        # else:
        #    print("continuing...")

    def check_connect(self):
        if self.debugOn:
            print("Checking for LANforge GUI connection: %s" % self.mgr_url)
        response = self.json_get("/")
        duration = 0
        while (response is None) and (duration < 300):
            print("LANforge GUI connection not found sleeping 5 seconds, tried: %s" % self.mgr_url)
            duration += 2
            time.sleep(2)
            response = self.json_get("")

        if duration >= 300:
            print("Could not connect to LANforge GUI")
            sys.exit(1)

    def get_result_list(self):
        return self.test_results

    def get_failed_result_list(self):
        fail_list = []
        for result in self.test_results:
            if not result.startswith("PASS"):
                fail_list.append(result)
        return fail_list

    def get_fail_message(self):
        fail_messages = self.get_failed_result_list()
        return "\n".join(fail_messages)

    def passes(self):
        pass_counter = 0
        fail_counter = 0
        for result in self.test_results:
            if result.startswith("PASS"):
                pass_counter += 1
            else:
                fail_counter += 1
        if (fail_counter == 0) and (pass_counter > 0):
            return True
        return False

    # use this inside the class to log a failure result
    def _fail(self, message, print_=False):
        self.test_results.append(self.fail_pref + message)
        if print_:
            print(self.fail_pref + message)

    # use this inside the class to log a pass result
    def _pass(self, message, print_=False):
        self.test_results.append(self.pass_pref + message)
        if print_:
            print(self.pass_pref + message)

# ~class
