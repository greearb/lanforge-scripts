#!env /usr/bin/python

import traceback
# Extend this class to use common set of debug and request features for your script
from pprint import pprint

import LANforge.LFUtils
from LANforge.LFUtils import *
import argparse


class LFCliBase:
    # do not use `super(LFCLiBase,self).__init__(self, host, port, _debug)
    # that is py2 era syntax and will force self into the host variable, making you
    # very confused.
    def __init__(self, _lfjson_host, _lfjson_port,
                 _debug=False,
                 _halt_on_error=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        self.fail_pref = "FAILED: "
        self.pass_pref = "PASSED: "
        self.lfclient_host = _lfjson_host
        self.lfclient_port = _lfjson_port
        self.debug = _debug

        self.lfclient_url = "http://%s:%s" % (self.lfclient_host, self.lfclient_port)
        self.test_results = []
        self.halt_on_error = _halt_on_error
        self.exit_on_error = _exit_on_error
        self.exit_on_fail = _exit_on_fail
        # toggle using preexec_cli, preexec_method; the preexec_X parameters are useful
        # when you desire the lfclient to check for existance of entities to run commands on,
        # like when developing; you might toggle this with use_preexec = _debug
        # Otherwise, preexec methods use more processing time because they add an extra CLI call
        # into the queue, and inspect it -- typically nc_show_port
        self.suppress_related_commands = None

    def clear_test_results(self):
        self.test_results.clear()

    def json_post(self, _req_url, _data, debug_=False, suppress_related_commands_=None, response_json_list_=None):
        """
        send json to the LANforge client
        :param _req_url: requested url
        :param _data: json data to send
        :param debug_: turn on debugging output
        :param suppress_related_commands_: when False, override self.preexec; when True use
        :param response_json_list_: array for json results in the response object, (alternative return method)
        :return: http response object
        """
        json_response = None
        try:
            lf_r = LFRequest.LFRequest(self.lfclient_url, _req_url, debug_=self.debug, die_on_error_=self.exit_on_error)
            if suppress_related_commands_ is None:
                if 'suppress_preexec_cli' in _data:
                    del _data['suppress_preexec_cli']
                if 'suppress_preexec_method' in _data:
                    del _data['suppress_preexec_method']
                if 'suppress_postexec_cli' in _data:
                    del _data['suppress_postexec_cli']
                if 'suppress_postexec_method' in _data:
                    del _data['suppress_postexec_method']
            elif suppress_related_commands_ == False:
                _data['suppress_preexec_cli'] = False
                _data['suppress_preexec_method'] = False
                _data['suppress_postexec_cli'] = False
                _data['suppress_postexec_method'] = False
            elif self.suppress_related_commands or suppress_related_commands_:
                _data['suppress_preexec_cli'] = False
                _data['suppress_preexec_method'] = False
                _data['suppress_postexec_cli'] = True
                _data['suppress_postexec_method'] = True

            lf_r.addPostData(_data)
            if debug_ or self.debug:
                LANforge.LFUtils.debug_printer.pprint(_data)
            json_response = lf_r.jsonPost(show_error=self.debug,
                                          debug=(self.debug or debug_),
                                          response_json_list_=response_json_list_,
                                          die_on_error_=self.exit_on_error)
            if debug_ and (response_json_list_ is not None):
                pprint.pprint(response_json_list_)
        except Exception as x:
            if self.debug or self.halt_on_error or self.exit_on_error:
                print("jsonPost posted to %s" % _req_url)
                pprint.pprint(_data)
                print("Exception %s:" % x)
                traceback.print_exception(Exception, x, x.__traceback__, chain=True)
            if self.halt_on_error or self.exit_on_error:
                exit(1)

        return json_response

    def json_get(self, _req_url, debug_=False):
        if self.debug or debug_:
            print("URL: "+_req_url)
        json_response = None
        try:
            lf_r = LFRequest.LFRequest(self.lfclient_url, _req_url, debug_=(self.debug or debug_), die_on_error_=self.exit_on_error)
            json_response = lf_r.getAsJson(debug_=self.debug, die_on_error_=self.halt_on_error)
            #debug_printer.pprint(json_response)
            if (json_response is None) and (self.debug or debug_):
                print("LFCliBase.json_get: no entity/response, probabily status 404")
                return None
        except ValueError as ve:
            if self.debug or self.halt_on_error or self.exit_on_error:
                print("jsonGet asked for " + _req_url)
                print("Exception %s:" % ve)
                traceback.print_exception(ValueError, ve, ve.__traceback__, chain=True)
            if self.halt_on_error or self.exit_on_error:
                sys.exit(1)

        return json_response

    @staticmethod
    def response_list_to_map(json_list, key, debug_=False):
        reverse_map = {}
        if (json_list is None) or (len(json_list) < 1):
            if debug_:
                print("response_list_to_map: no json_list provided")
                raise ValueError("response_list_to_map: no json_list provided")
            return reverse_map

        json_interfaces = json_list
        if key in json_list:
            json_interfaces = json_list[key]

        for record in json_interfaces:
            if len(record.keys()) < 1:
                continue
            record_keys = record.keys()
            k2 = ""
            # we expect one key in record keys, but we can't expect [0] to be populated
            json_entry = None
            for k in record_keys:
                k2 = k
                json_entry = record[k]
            # skip uninitialized port records
            if k2.find("Unknown") >= 0:
                continue
            port_json = record[k2]
            reverse_map[k2] = json_entry

        return reverse_map

    def error(self, exception):
        # print("lfcli_base error: %s" % exception)
        pprint.pprint(exception)
        traceback.print_exception(Exception, exception, exception.__traceback__, chain=True)
        if self.halt_on_error:
            print("halting on error")
            sys.exit(1)
        # else:
        #    print("continuing...")

    def check_connect(self):
        if self.debug:
            print("Checking for LANforge GUI connection: %s" % self.lfclient_url)
        response = self.json_get("/", debug_=self.debug)
        duration = 0
        while (response is None) and (duration < 300):
            print("LANforge GUI connection not found sleeping 5 seconds, tried: %s" % self.lfclient_url)
            duration += 2
            time.sleep(2)
            response = self.json_get("", debug_=self.debug)

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

    def get_all_message(self):
        return "\n".join(self.test_results)

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
        if print_ or self.exit_on_fail:
            print(self.fail_pref + message)
        if self.exit_on_fail:
            sys.exit(1)

    # use this inside the class to log a pass result
    def _pass(self, message, print_=False):
        self.test_results.append(self.pass_pref + message)
        if print_:
            print(self.pass_pref + message)

    @staticmethod
    def create_basic_argparse(prog=None, formatter_class=None, epilog=None, description=None):
        if (prog is not None) or (formatter_class is not None) or (epilog is not None) or (description is not None):
            parser = argparse.ArgumentParser(prog=prog, formatter_class=formatter_class, epilog=epilog,
                                             description=description)
        else:
            parser = argparse.ArgumentParser()

        parser.add_argument('--mgr',            help='hostname for where LANforge GUI is running', default='localhost')
        parser.add_argument('--mgr_port',       help='port LANforge GUI HTTP service is running on', default=8080)
        parser.add_argument('-u', '--upstream_port',
                            help='non-station port that generates traffic: <resource>.<port>, e.g: 1.eth1',
                            default='1.eth1')
        parser.add_argument('--radio',          help='radio EID, e.g: 1.wiphy2', default='wiphy2')
        parser.add_argument('--security',       help='WiFi Security protocol: <open | wep | wpa | wpa2 | wpa3 >', default='wpa2')
        parser.add_argument('--ssid',           help='SSID for stations to associate to', default='jedway-wpa2-160')
        parser.add_argument('--passwd',         help='WiFi passphrase', default='jedway-wpa2-160')
        parser.add_argument('--num_stations',   help='Number of stations to create', default=2)
        parser.add_argument('--debug',          help='Enable debugging', default=False, action="store_true")


        return parser

# ~class
