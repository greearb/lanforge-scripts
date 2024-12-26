#!/usr/bin/env python3

'''
NAME:
lf_rfgen_info.py

PURPOSE:
This script will read the configuration settings of the RF-Generators connected to a LANforge.
May be used as a module

EXAMPLE:

./lf_rfgen_info --mgr <ip>

NOTES:

# https://docs.python.org/3.8/library/telnetlib.html


'''


# https://docs.python.org/3.8/library/telnetlib.html

import argparse
import telnetlib
import logging
import importlib


logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("lf_logger_config")


class lf_rfgen_info():
    def __init__(self,
                 _mgr='localhost',
                 _port='4001'):
        self.mgr = _mgr
        self.port = _port
        self.rfgen_info = ''

    def get_rfgen_info(self):
        tn = telnetlib.Telnet(self.mgr, port=self.port)  # Telnet(host=None, port=0[, timeout])

        # command to read all
        CMD = b'show_rfgen'

        tn.read_until(b">>")
        tn.write(CMD + b"\n")
        tn.write(b"exit\n")

        self.rfgen_info = tn.read_all().decode('ascii')

        logger.info(self.rfgen_info)
        return self.rfgen_info


def main():
    help_summary = '''\
This script will read the configuration settings of the RF-Generators connected to a LANforge.
'''

    # arguments
    parser = argparse.ArgumentParser(
        prog='lf_rfgen_info.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            lf_rfgen_info.py
            ''',
        description='''\
NAME:
lf_rfgen_info.py

PURPOSE:
Read the rfgen_info from lanforge
May be used as a module

EXAMPLE:

./lf_rfgen_info --mgr <ip>

NOTES:

# https://docs.python.org/3.8/library/telnetlib.html

            ''')

    parser.add_argument(
        '--mgr',
        help="--mgr <lanforge ip>",
        default="localhost")
    parser.add_argument(
        '--port',
        help="--port <lanforge telnet port>",
        default="4001")

    parser.add_argument('--log_level',
                        default=None,
                        help='Set logging level: debug | info | warning | error | critical')
    # help summary
    parser.add_argument('--help_summary',
                        default=None,
                        action="store_true",
                        help='Show summary of what this script does')

    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    logger_config = lf_logger_config.lf_logger_config()

    if args.log_level:
        logger_config.set_level(level=args.log_level)

    rfgen = lf_rfgen_info(_mgr=args.mgr, _port=args.port)

    rf_info = rfgen.get_rfgen_info()

    logger.info(rf_info)


if __name__ == '__main__':
    main()
