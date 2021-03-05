
#!/usr/bin/env python3


from LANforge.lfcli_base import LFCliBase
from pprint import pprint
import pprint
import time

class GenCXProfile(LFCliBase):
    def __init__(self, lfclient_host, lfclient_port, local_realm, debug_=False):
        super().__init__(lfclient_host, lfclient_port, debug_, _halt_on_error=True)
        self.lfclient_host = lfclient_host
        self.lfclient_port = lfclient_port
        self.lfclient_url = "http://%s:%s" % (lfclient_host, lfclient_port)
        self.debug = debug_
        self.type = "lfping"
        self.dest = "127.0.0.1"
        self.interval = 1
        self.cmd = ""
        self.local_realm = local_realm
        self.name_prefix = "generic"
        self.created_cx = []
        self.created_endp = []
        self.file_output = "/dev/null"
        self.loop_count = 1

    def parse_command(self, sta_name):
        if self.type == "lfping":
            if ((self.dest is not None) or (self.dest != "")) and ((self.interval is not None) or (self.interval > 0)):
                self.cmd = "%s  -i %s -I %s %s" % (self.type, self.interval, sta_name, self.dest)
                # print(self.cmd)
            else:
                raise ValueError("Please ensure dest and interval have been set correctly")
        elif self.type == "generic":
            if self.cmd == "":
                raise ValueError("Please ensure cmd has been set correctly")
        elif self.type == "speedtest":
            self.cmd = "vrf_exec.bash %s speedtest-cli --json --share" % (sta_name)
        elif self.type == "iperf3" and self.dest is not None:
            self.cmd = "iperf3 --forceflush --format k --precision 4 -c %s -t 60 --tos 0 -b 1K --bind_dev %s -i 1 " \
                       "--pidfile /tmp/lf_helper_iperf3_test.pid" % (self.dest, sta_name)
        elif self.type == "lfcurl":
            if self.file_output is not None:
                self.cmd = "./scripts/lf_curl.sh  -p %s -i AUTO -o %s -n %s -d %s" % \
                           (sta_name, self.file_output, self.loop_count, self.dest)
            else:
                raise ValueError("Please ensure file_output has been set correctly")
        else:
            raise ValueError("Unknown command type")

    def start_cx(self):
        print("Starting CXs...")
        # print(self.created_cx)
        # print(self.created_endp)
        for cx_name in self.created_cx:
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
                "cx_state": "RUNNING"
            }, debug_=self.debug)
            print(".", end='')
        print("")

    def stop_cx(self):
        print("Stopping CXs...")
        for cx_name in self.created_cx:
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
                "cx_state": "STOPPED"
            }, debug_=self.debug)
            print(".", end='')
        print("")

    def cleanup(self):
        print("Cleaning up cxs and endpoints")
        for cx_name in self.created_cx:
            req_url = "cli-json/rm_cx"
            data = {
                "test_mgr": "default_tm",
                "cx_name": cx_name
            }
            self.json_post(req_url, data)

        for endp_name in self.created_endp:
            req_url = "cli-json/rm_endp"
            data = {
                "endp_name": endp_name
            }
            self.json_post(req_url, data)

    def set_flags(self, endp_name, flag_name, val):
        data = {
            "name": endp_name,
            "flag": flag_name,
            "val": val
        }
        self.json_post("cli-json/set_endp_flag", data, debug_=self.debug)

    def set_cmd(self, endp_name, cmd):
        data = {
            "name": endp_name,
            "command": cmd
        }
        self.json_post("cli-json/set_gen_cmd", data, debug_=self.debug)

    def create(self, ports=[], sleep_time=.5, debug_=False, suppress_related_commands_=None):
        if self.debug:
            debug_ = True
        post_data = []
        endp_tpls = []
        for port_name in ports:
            port_info = self.local_realm.name_to_eid(port_name)
            if len(port_info) == 2:
                resource = 1
                shelf = port_info[0]
                name = port_info[-1]
            elif len(port_info) == 3:
                resource = port_info[0]
                shelf = port_info[1]
                name = port_info[-1]
            else:
                raise ValueError("Unexpected name for port_name %s" % port_name)

            # this naming convention follows what you see when you use
            # lf_firemod.pl --action list_endp after creating a generic endpoint
            gen_name_a = "%s-%s" % (self.name_prefix, name)
            gen_name_b = "D_%s-%s" % (self.name_prefix, name)
            endp_tpls.append((shelf, resource, name, gen_name_a, gen_name_b))

        for endp_tpl in endp_tpls:
            shelf = endp_tpl[0]
            resource = endp_tpl[1]
            name = endp_tpl[2]
            gen_name_a = endp_tpl[3]
            # gen_name_b  = endp_tpl[3]
            # (self, alias=None, shelf=1, resource=1, port=None, type=None)

            data = {
                "alias": gen_name_a,
                "shelf": shelf,
                "resource": resource,
                "port": name,
                "type": "gen_generic"
            }
            if self.debug:
                pprint(data)

            self.json_post("cli-json/add_gen_endp", data, debug_=self.debug)

        self.local_realm.json_post("/cli-json/nc_show_endpoints", {"endpoint": "all"})
        time.sleep(sleep_time)

        for endp_tpl in endp_tpls:
            gen_name_a = endp_tpl[3]
            gen_name_b = endp_tpl[4]
            self.set_flags(gen_name_a, "ClearPortOnStart", 1)
        time.sleep(sleep_time)

        for endp_tpl in endp_tpls:
            name = endp_tpl[2]
            gen_name_a = endp_tpl[3]
            # gen_name_b  = endp_tpl[4]
            self.parse_command(name)
            self.set_cmd(gen_name_a, self.cmd)
        time.sleep(sleep_time)

        for endp_tpl in endp_tpls:
            name = endp_tpl[2]
            gen_name_a = endp_tpl[3]
            gen_name_b = endp_tpl[4]
            cx_name = "CX_%s-%s" % (self.name_prefix, name)
            data = {
                "alias": cx_name,
                "test_mgr": "default_tm",
                "tx_endp": gen_name_a,
                "rx_endp": gen_name_b
            }
            post_data.append(data)
            self.created_cx.append(cx_name)
            self.created_endp.append(gen_name_a)
            self.created_endp.append(gen_name_b)

        time.sleep(sleep_time)

        for data in post_data:
            url = "/cli-json/add_cx"
            if self.debug:
                pprint(data)
            self.local_realm.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands_)
            time.sleep(2)
        time.sleep(sleep_time)
        for data in post_data:
            self.local_realm.json_post("/cli-json/show_cx", {
                "test_mgr": "default_tm",
                "cross_connect": data["alias"]
            })
        time.sleep(sleep_time)