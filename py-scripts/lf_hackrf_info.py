#!/usr/bin/env python3

'''
NAME:
lf_hackrf_info.py

PURPOSE:
Read the hackrf_info from lanforge
May be used as a module

EXAMPLE:

./lf_hackrf_info --mgr <ip>

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

class lf_hackrf_info():
    def __init__(self,
                _mgr='localhost',
                _port='4001'):
        self.mgr = _mgr
        self.port = _port
        self.hackrf_info = ''

    def get_hackrf_info(self):
        tn = telnetlib.Telnet(self.mgr,port=self.port) # Telnet(host=None, port=0[, timeout])

        # command to read all
        CMD=b'show_rfgen'

        tn.read_until(b">>")
        tn.write(CMD +b"\n")
        tn.write(b"exit\n")

        self.hackrf_info=tn.read_all().decode('ascii')

        logger.info(self.hackrf_info)
        return self.hackrf_info

def main():
    # arguments
    parser = argparse.ArgumentParser(
        prog='lf_check.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            lf_hackrf_info.py
            ''',
        description='''\
NAME:
lf_hackrf_info.py

PURPOSE:
Read the hackrf_info from lanforge
May be used as a module

EXAMPLE:

./lf_hackrf_info --mgr <ip>

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

    
    args = parser.parse_args()

    logger_config = lf_logger_config.lf_logger_config()

    if args.log_level:
        logger_config.set_level(level=args.log_level)

    hackrf = lf_hackrf_info(_mgr=args.mgr,
                            _port=args.port)

    rf_info = hackrf.get_hackrf_info()

    logger.info(rf_info)




if __name__ == '__main__':
    main()

