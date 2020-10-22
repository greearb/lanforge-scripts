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
        self.params     = {}
        self.flags      = 0x0
        self.flags_mask = 0x0

    def add_flag(self, ):
        pass

    def build(self):
        pass

    def start(self, print_pass=False, print_fail=False):
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
        epilog="Update parameters of a DUT record",
        description='''{file}
--------------------
Generic command layout:
python ./{file} --create [name] # create new DUT record
--update [name]   # update existing DUT record
--entry [key,value] # update/add entry by specifying key and value

Command Line Example: 
python3 ./{file} --mgr 192.168.100.24 --update Pathfinder --entry MAC1,"00:00:ae:f0:b1:b9" --entry api,"build 2901"

DUT Parameters:
{params}
DUT Flags:
{flags}
'''.format(file=__file__, params=param_string, flags=flags_string)
    )

    args = parser.parse_args()

    update_dut = UpdateDUT(args.mgr, lfjson_port, _debug_on=args.debug)

    update_dut.build()
    update_dut.start()


if __name__ == "__main__":
    main()
