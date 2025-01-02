#!/usr/bin/env python3
# flake8: noqa
"""
NAME:       lf_atten_mod_test.py

PURPOSE:    lf_atten_mod_test.py is used to modify and/or read the LANforge Attenuator settings.

EXAMPLE:    Set channel four (zero-indexed) of all attenuators on LANforge system \'192.168.200.12\'
            to attenuation value 220 ddB (22.0 dB).
            Command: './lf_atten_mod_test.py --mgr 192.168.200.12 --atten_serno all --atten_idx 3 --atten_val 220'

            Set channel all channels of attenuator 2324 on LANforge system \'192.168.200.12\'
            to attenuation value 0 ddB (0.0 dB).
            Command: './lf_atten_mod_test.py --mgr 192.168.200.12 --atten_serno 2324 --atten_idx all --atten_val 0'

            Run with '--help' option to see full usage and all options.

Copyright 2021 Candela Technologies Inc
License: Free to distribute and modify. LANforge systems must be licensed.
"""
import sys
import os
import importlib
import argparse
import logging


if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

realm = importlib.import_module("py-json.realm")
Realm = realm.Realm

logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")



class CreateAttenuator(Realm):
    def __init__(self, host, port, serno, idx, val,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, debug_=_debug_on, _exit_on_fail=_exit_on_fail)
        self.host = host
        self.serno = serno
        self.idx = idx
        self.val = val
        self.attenuator_profile = self.new_attenuator_profile()
        self.attenuator_profile.atten_idx = self.idx
        self.attenuator_profile.atten_val = self.val
        self.attenuator_profile.atten_serno = self.serno

    def build(self):
        self.attenuator_profile.create()
        self.attenuator_profile.show()


def main():
    # create_basic_argparse defined in lanforge-scripts/py-json/LANforge/lfcli_base.py
    parser = Realm.create_bare_argparse(
        prog='lf_atten_mod_test.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=None,
        description='''\
NAME:       lf_atten_mod_test.py

PURPOSE:    lf_atten_mod_test.py is used to modify and/or read the LANforge Attenuator settings. 

EXAMPLE:    Set channel four (zero-indexed) of all attenuators on LANforge system \'192.168.200.12\'
            to attenuation value 220 ddB (22 dB).
            Command: './lf_atten_mod_test.py --mgr 192.168.200.12 --atten_serno all --atten_idx 3 --atten_val 220'

            Set channel all channels of attenuator 2324 on LANforge system \'192.168.200.12\'
            to attenuation value 0 ddB (0.0 dB).
            Command: './lf_atten_mod_test.py --mgr 192.168.200.12 --atten_serno 2324 --atten_idx all --atten_val 0'
''')
    parser.add_argument('--atten_serno', help='Serial number for requested attenuator, or \'all\'',              default='all')
    parser.add_argument('--atten_idx',   help='Attenuator index eg. For module 1 = 0, module 2 = 1, or \'all\'', default='all')
    parser.add_argument('--atten_val',   help='Requested attenuation in 1/10ths of dB (ddB).',                   default=0)

    args = parser.parse_args()
    help_summary='''\
lf_atten_mod_test.py is used to modify and/or read the LANforge Attenuator settings.
'''
    if args.help_summary:
        print(help_summary)
        exit(0)

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()
    # set the logger level to requested value
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    atten_mod_test = CreateAttenuator(host=args.mgr, port=args.mgr_port, serno=args.atten_serno, idx=args.atten_idx, val=args.atten_val, _debug_on=args.debug)
    atten_mod_test.build()


if __name__ == "__main__":
    main()
