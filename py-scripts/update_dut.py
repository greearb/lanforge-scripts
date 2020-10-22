#!/usr/bin/env python3
"""
This script updates a Device Under Test (DUT) entry in the LANforge test scenario.
A common reason to use this would be to update MAC addresses in a DUT when you switch
between different items of the same make/model of a DUT.
"""
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append('../py-json')

import argparse
import pprint
from pprint import pprint
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
from LANforge import add_dut
from LANforge import LFUtils
import argparse
import realm
import time
import datetime


class UpdateDUT(LFCliBase):
    def __init__(self, host, port,
                _debug_on=False,
                _exit_on_error=False,
                _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.host       = host
        self.port       = port
        self.notes      = "NA"
        self.params     = {}
        self.flags      = 0x0
        self.flags_mask = 0x0
        self.data       = {}
        self.url        = "/cli-json/add_dut"

    def build(self):

        for param in self.params:
            print("param: %s: %s"%(param, self.params[param]))

        for flag in self.flags:
            print("flags: %s: %s"%(flag, self.flags[flag]))

    def start(self, print_pass=False, print_fail=False):
        self.json_post(self.url, self.data)
        self._pass("DUT updated")
        pass

    def stop(self):
        pass

    def cleanup(self, sta_list):
        pass

def main():
    lfjson_host = "localhost"
    lfjson_port = 8080

    param_string = " "
    for param in add_dut.dut_params:
        param_string += "%s, "%param.name

    flags_string = " "
    for flag in add_dut.dut_flags:
        flags_string += "%s, "%flag.name

    parser = LFCliBase.create_bare_argparse( prog='update_dut.py',
        formatter_class=argparse.RawTextHelpFormatter,
        description='''{file}
--------------------
Generic command layout:
python ./{file} --dut [DUT name]     # update existing DUT record
                --entry [key,value]     # update/add entry by specifying key and value
                --flag [flag,0|1]       # toggle a flag on 1 or off 0
                --notes "going to mars...."
DUT Parameters:
    {params}
DUT Flags:
    {flags}
    
Command Line Example: 
python3 {file} --mgr 192.168.100.24 --update Pathfinder \
    --entry MAC1,"00:00:ae:f0:b1:b9" \
    --notes "build 2901" \
    --flag STA_MODE,0
    --flag AP_MODE,1

'''.format(file=__file__, params=param_string, flags=flags_string),
         epilog="See",
    )
    parser.add_argument("-d", "--dut",      type=str, help="name of DUT record")
    parser.add_argument("-p", "--param",    type=str, action="append", help="name,value pair to set parameter")
    parser.add_argument("-f", "--flag",     type=str, action="append", help="name,1/0/True/False pair to turn parameter on or off")
    parser.add_argument("--notes",          type=str, help="add notes to the DUT")
    args = parser.parse_args()

    update_dut = UpdateDUT(args.mgr, lfjson_port, _debug_on=args.debug)
    pprint.pprint(args)
    for param in args.param:
        (name,value) = param.split(",")
        update_dut.params[name] = value

    for flag in args.flags:
        (name,value) = flag.split(",")
        update_dut.flags[name] = (False,True)[value]
        update_dut.flags_mask[name] = True

    if (args.notes is not None) and (args.notes != ""):
        update_dut.notes = args.notes

    update_dut.build()
    update_dut.start()


if __name__ == "__main__":
    main()
