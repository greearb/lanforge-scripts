#!/usr/bin/python3

"""
NAME:
asus_ap.py

PURPOSE:
ap_asus_module

EXAMPLE:

./ap_asus_mod.py 


NOTES:



"""

import sys

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

import argparse
import pexpect
import serial
from pexpect_serial import SerialSpawn
import importlib
from pprint import pformat
import traceback
import paramiko


sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


# see https://stackoverflow.com/a/13306095/11014343
class FileAdapter(object):
    def __init__(self, logger):
        self.logger = logger

    def write(self, data):
        # NOTE: data can be a partial line, multiple lines
        data = data.strip()  # ignore leading/trailing whitespace
        if data:  # non-blank
            self.logger.info(data)

    def flush(self):
        pass  # leave it to logging to flush properly

# LAN-1423
class create_ap_obj:
    def __init__(self,
                 ap_test_mode=False,
                 ap_ip=None,
                 ap_user=None,
                 ap_passwd=None,
                 ap_scheme='ssh',
                 ap_serial_port='/dev/ttyUSB0',
                 ap_ssh_port="22",
                 ap_telnet_port="23",
                 ap_serial_baud='115200',
                 ap_if_2g="eth6",
                 ap_if_5g="eth7",
                 ap_if_6g="eth8",
                 ap_report_dir="",
                 ap_log_file=""):
        self.ap_test_mode = _ap_test_mode
        self.ap_if_2g = ap_if_2g
        self.ap_if_5g = ap_if_5g
        self.ap_if_6g = _ap_if_6g
        self.ap_scheme = _ap_scheme
        self.ap_serial_port = _ap_serial_port
        self.ap_telnet_port = _ap_ssh_port
        self.ap_telnet = _ap_telnet_port
        self.ap_serial_baud = _ap_serial_baud
        self.ap_report_dir = _ap_report_dir
        self.ap_log_file = _ap_log_file

        self.ap_read_stats = 'wl -i INF bs_data'

    # For testing module
    def ap_action(self, ap_cmd=None, ap_file=None):

        if ap_cmd != None:
            self.ap_cmd = ap_cmd
        logger.info("ap_cmd: {}".format(ap_cmd))
        try:
            # TODO - add paramiko.SSHClient
            if self.ap_scheme == 'serial':
                # configure the serial interface
                ser = serial.Serial(self.ap_port, int(self.ap_baud), timeout=5)
                ss = SerialSpawn(ser)
                ss.sendline(str(self.ap_cmd))
                # do not detete line, waits for output
                ss.expect([pexpect.TIMEOUT], timeout=1)
                ap_results = ss.before.decode('utf-8', 'ignore')
                logger.debug("ap_stats_6g serial from AP: {}".format(ap_stats_6g))
            elif self.ap_scheme == 'ssh':
                results = self.ap_ssh(str(self.ap_cmd))
                logger.debug("ap_stats_5g ssh from AP : {}".format(ap_stats_6g))

        except Exception as x:
            traceback.print_exception(Exception, x, x.__traceback__, chain=True)
            logger.error("WARNING: ap_stats_6g unable to read AP")

        if self.ap_file is not None:
            ap_file = open(str(self.ap_file), "a")
            ap_file.write(results)
            ap_file.close()
            print("ap file written {}".format(str(self.file)))

    def ap_ssh(self, command):
        # in python3 bytes and str are two different types.  str is used to reporesnt any
        # type of string (also unicoe), when you encode()
        # something, you confvert it from it's str represnetation to it's bytes reprrestnetation for a specific 
        # endoding
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.ap_ip, port=self.ap_ssh_port, username=self.ap_user, password=self.ap_passwd, timeout=5)
        stdin, stdout, steerr = ssh.exec_command(command)
        output = stdout.read()
        logger.debug("command:  {command} output: {output}".format(command=command,output=output))
        output = output.decode('utf-8', 'ignore')
        logger.debug("after utf-8 ignoer output: {output}".format(command=command,output=output))

        ssh.close()
        return output


    # ASUS 
    def clear_stats(self, band):
        
        pass


    # ASUS bs_data,  tx_data , data transmitted from AP stats
    def tx_stats(self, band, mac):
        pass
    
    # ASUS rx_report,  rx_data  , receive statatistics at AP
    def rx_stats(self, band, mac):
        pass


    # ASUS uplink data
    def ap_ul_data(self,band):
        pass

    # ASUS rx_report
    def ap_dl_data(self, band):
        pass

    

    # ASUS chanel info (channel utilization)
    def ap_chanim(self, band):
        pass

    def ap_ul_stats(self, band):
        pass

    def ap_dl_stats(self, band):
        pass

    @taticmethod
    def ap_store_dl_scheduler_stats(band):
        if band is "6G":
            pass

    def ap_store_ul_scheduler_stats(self, band):
        pass

    def ap_ofdma_stats(self, band):
        pass


def main():
    parser = argparse.ArgumentParser(
        prog='lf_ap.py',
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        Useful Information:
            1. Useful Information goes here
            ''',

        description='''\
lf_ap.py:
--------------------
Summary : 
----------
This file is used for verification

Commands: (wl2 == 6GHz wl1 == 5GHz , wl0 == 24ghz)

read ap data:: 'wl -i wl1 bs_data'
reset scheduler's counters:: 'wl -i wl1 dump_clear'
UL scheduler statistics:: 'wl -i wl1 dump umsched'
DL scheduler statistics:: 'wl -i wl1 dump msched'

Generic command layout:
-----------------------

Notes:
------
    
        .git/bs_data Display per station band steering data
    usage: bs_data [options]
    options are:
        -comma    Use commas to separate values rather than blanks.
        -tab      Use <TAB> to separate values rather than blanks.
        -raw      Display raw values as received from driver.
        -noidle   Do not display idle stations
        -nooverall  Do not display total of all stations
        -noreset  Do not reset counters after reading

    rx_report
            Display per station live data about rx datapath
    usage: rx_report [options]
    options are:
        -sta xx:xx:xx:xx:xx:xx  only display specific mac addr.
        -comma      Use commas to separate values rather than blanks.
        -tab        Use <TAB> to separate values rather than blanks.
        -raw        Display raw values as received from driver.
        -noidle     Do not display idle stations
        -nooverall  Do not display total of all stations
        -noreset    Do not reset counters after reading
           


        ''')
    parser.add_argument('--ap_read', help='--ap_read  flag present enable reading ap', action='store_true')
    parser.add_argument('--ap_test_mode', help='--ap_mode ', default=True)

    parser.add_argument('--ap_scheme', help="--ap_scheme '/dev/ttyUSB0'", choices=['serial', 'telnet', 'ssh', 'mux_serial'], default='serial')
    parser.add_argument('--ap_port', help="--ap_port '/dev/ttyUSB0'", default='/dev/ttyUSB0')
    parser.add_argument('--ap_baud', help="--ap_baud '115200'',  default='115200", default="115200")
    parser.add_argument('--ap_ip', help='--ap_ip', default='192.168.50.1')
    parser.add_argument('--ap_ssh_port', help='--ap_ssh_port', default='1025')
    parser.add_argument('--ap_user', help='--ap_user , the user name for the ap, default = lanforge', default='lanforge')
    parser.add_argument('--ap_passwd', help='--ap_passwd, the password for the ap default = lanforge', default='lanforge')
    # ASUS interfaces
    parser.add_argument('--ap_if_2g', help='--ap_if_2g eth6', default='wl0')
    parser.add_argument('--ap_if_5g', help='--ap_if_5g eth7', default='wl1')
    parser.add_argument('--ap_if_6g', help='--ap_if_6g eth8', default='wl2')
    parser.add_argument('--ap_file', help='--ap_file \'ap_file.txt\'')

    parser.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')
    # logging configuration
    parser.add_argument("--lf_logger_config_json", help="--lf_logger_config_json <json file> , json configuration of logger")

    args = parser.parse_args()

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    if (args.log_level):
        logger_config.set_level(level=args.log_level)

    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()


    ap_dut = lf_ap(
                ap_test_mode=args.ap_test_mode,
                 ap_ip=args.ap_ip,
                 ap_user=args.ap_user,
                 ap_passwd=args.ap_passwd,
                 ap_scheme=args.ap_scheme,
                 ap_serial_port=args.ap_serial_port,
                 ap_ssh_port=args.ssh_port,
                 ap_telnet_port=args.telnet_port,
                 ap_serial_baud=args.ap_serial_baud,
                 ap_if_2g=args.ap_if_2g,
                 ap_if_5g=args.ap_if_5g,
                 ap_if_6g=args.ap_if_6g,
                 ap_report_dir="",
                 ap_log_file=""):

    ap_dut.ap_action()


if __name__ == '__main__':
    main()
