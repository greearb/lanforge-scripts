#!/usr/bin/env python3

'''
NAME:       lf_validate_port.py

PURPOSE:    Validate the port being used for management when trying to talk to the GUI.
            Prevent 4001 and 4002 and ask for alternative.

NOTES:      # Recommended Usage in py scripts:
            args.mgr_port = validate_port(args.mgr_port)

EXAMPLE:    # Create a single wanpath on endpoint A - attemped with port 4001:
            ./lf_create_wanpath.py --mgr 192.168.101.189 --mgr_port 4001\
                --wp_name test_wp-A --wl_endp test_wl-A\
                --speed 102400 --latency 25 --max_jitter 50 --jitter_freq 6 --drop_freq 12\
                --log_level debug --debug

SCRIPT_CLASSIFICATION:
            Module

SCRIPT_CATEGORIES:
            Functional

STATUS:     Functional

VERIFIED_ON:
            16-Jan-2025
            GUI Version: 5.4.9
            Kernel Version: 6.11.11+

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README:
            False
'''

import sys
import logging
import importlib

if sys.version_info[0] != 3:
    print('This script requires Python3')
    exit()

lf_logger_config = importlib.import_module('py-scripts.lf_logger_config')
logger = logging.getLogger(__name__)


def validate_port(port):
    ''' Validate management port (not 4001 or 4002)'''
    portsRestricted = ['4001', '4002']
    if port in portsRestricted:
        logger.error('Ports 4001 and 4002 are reserved. Please choose another port. GUI is typically 8080.')
        response = input("To continue enter non-reserved port: ")
        if response != '':
            return response
        else:
            logger.error("No new port selected. Exiting...")
            exit(1)
    else:
        return port
