#!/usr/bin/env python3

'''

    This script is a frontend to run tests using the wlan_theoretical_output library

'''
import sys
if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)
if 'py-json' not in sys.path:
    sys.path.append('../py-json')


import argparse
import time
from LANforge import LFUtils
from LANforge import lfcli_base
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
import realm
import wlan_theoretical_sta

from realm import Realm
import logging

class TheoreticalStation(LFCliBase):
    def abg11(self):
        abg11_calc=wlan_theoretical_sta.abg11_calculator(Traffic_Type='Data',
                                                         PHY_Bit_Rate=32,
                                                         Encryption='WPA2',
                                                         QoS='Yes',
                                                         MAC_Frame_802_11=128,
                                                         Basic_Rate_Set='1',
                                                         Preamble='Short',
                                                         slot_name="Short",
                                                         Codec_Type="G.711",
                                                         RTS_CTS_Handshake='Yes',
                                                         CTS_to_self='Yes')
        abg11_calc.create_argparse()
        abg11_calc.calculate()
        abg11_calc.get_result()
    def n11(self):
        n11_calc=wlan_theoretical_sta.abg11_calculator(Traffic_Type='Data',
                                                       PHY_Bit_Rate=32,
                                                       Encryption='WPA2',
                                                       QoS='Yes',
                                                       MAC_Frame_802_11=128,
                                                       Basic_Rate_Set='1',
                                                       Preamble='Short',
                                                       slot_name="Short",
                                                       Codec_Type="G.711",
                                                       RTS_CTS_Handshake='Yes',
                                                       CTS_to_self='Yes')
        n11_calc.create_argparse()
        n11_calc.calculate()
        n11_calc.get_result()
    def ac11(self):
        ac11_calc=wlan_theoretical_sta.abg11_calculator(Traffic_Type='Data',
                                                        PHY_Bit_Rate=32,
                                                        Encryption='WPA2',
                                                        QoS='Yes',
                                                        MAC_Frame_802_11=128,
                                                        Basic_Rate_Set='1',
                                                        Preamble='Short',
                                                        slot_name="Short",
                                                        Codec_Type="G.711",
                                                        RTS_CTS_Handshake='Yes',
                                                        CTS_to_self='Yes')
        ac11_calc.create_argparse()
        ac11_calc.calculate()
        ac11_calc.get_result()

#main method
def main():
    parser = LFCliBase.create_basic_argparse(
        prog='test_ipv4_variable_time.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Create stations to test connection and traffic on VAPs of varying security types (WEP, WPA, WPA2, WPA3, Open)
            ''',

        description='''\
test_ipv4_variable_time.py:
--------------------
Generic command layout:

python3 ./test_ipv4_variable_time.py
    --upstream_port eth1
    --radio wiphy0
    --num_stations 32
    --security {open|wep|wpa|wpa2|wpa3}
    --mode   1
        {"auto"   : "0",
        "a"      : "1",
        "b"      : "2",
        "g"      : "3",
        "abg"    : "4",
        "abgn"   : "5",
        "bgn"    : "6",
        "bg"     : "7",
        "abgnAC" : "8",
        "anAC"   : "9",
        "an"     : "10",
        "bgnAC"  : "11",
        "abgnAX" : "12",
        "bgnAX"  : "13"}
    --ssid netgear
    --password admin123
    --test_duration 2m (default)
    --a_min 3000
    --b_min 1000
    --ap "00:0e:8e:78:e1:76"
    --output_format csv
    --report_file ~/Documents/results.csv                       (Example of csv file output  - please use another extension for other file formats)
    --compared_report ~/Documents/results_prev.csv              (Example of csv file retrieval - please use another extension for other file formats) - UNDER CONSTRUCTION
    --col_names 'name','tx bytes','rx bytes','dropped'          (column names from the GUI to print on report -  please read below to know what to put here according to preferences)
    --debug
===============================================================================
 ** FURTHER INFORMATION **
    Using the col_names flag:

    Currently the output function does not support inputting the columns in col_names the way they are displayed in the GUI. This quirk is under construction. To output
    certain columns in the GUI in your final report, please match the according GUI column display to it's counterpart to have the columns correctly displayed in
    your report.

    GUI Column Display       Col_names argument to type in (to print in report)

    Name                |  'name'
    EID                 |  'eid'
    Run                 |  'run'
    Mng                 |  'mng'
    Script              |  'script'
    Tx Rate             |  'tx rate'
    Tx Rate (1 min)     |  'tx rate (1&nbsp;min)'
    Tx Rate (last)      |  'tx rate (last)'
    Tx Rate LL          |  'tx rate ll'
    Rx Rate             |  'rx rate'
    Rx Rate (1 min)     |  'rx rate (1&nbsp;min)'
    Rx Rate (last)      |  'rx rate (last)'
    Rx Rate LL          |  'rx rate ll'
    Rx Drop %           |  'rx drop %'
    Tx PDUs             |  'tx pdus'
    Tx Pkts LL          |  'tx pkts ll'
    PDU/s TX            |  'pdu/s tx'
    Pps TX LL           |  'pps tx ll'
    Rx PDUs             |  'rx pdus'
    Rx Pkts LL          |  'pps rx ll'
    PDU/s RX            |  'pdu/s tx'
    Pps RX LL           |  'pps rx ll'
    Delay               |  'delay'
    Dropped             |  'dropped'
    Jitter              |  'jitter'
    Tx Bytes            |  'tx bytes'
    Rx Bytes            |  'rx bytes'
    Replays             |  'replays'
    TCP Rtx             |  'tcp rtx'
    Dup Pkts            |  'dup pkts'
    Rx Dup %            |  'rx dup %'
    OOO Pkts            |  'ooo pkts'
    Rx OOO %            |  'rx ooo %'
    RX Wrong Dev        |  'rx wrong dev'
    CRC Fail            |  'crc fail'
    RX BER              |  'rx ber'
    CX Active           |  'cx active'
    CX Estab/s          |  'cx estab/s'
    1st RX              |  '1st rx'
    CX TO               |  'cx to'
    Pattern             |  'pattern'
    Min PDU             |  'min pdu'
    Max PDU             |  'max pdu'
    Min Rate            |  'min rate'
    Max Rate            |  'max rate'
    Send Buf            |  'send buf'
    Rcv Buf             |  'rcv buf'
    CWND                |  'cwnd'
    TCP MSS             |  'tcp mss'
    Bursty              |  'bursty'
    A/B                 |  'a/b'
    Elapsed             |  'elapsed'
    Destination Addr    |  'destination addr'
    Source Addr         |  'source addr'
            ''')
    for group in parser._action_groups:
        if group.title == "required arguments":
            required_args=group
            break
    #if required_args is not None:

    optional_args=None
    for group in parser._action_groups:
        if group.title == "optional arguments":
            optional_args=group
            break
    if optional_args is not None:
        optional_args.add_argument('--mode', help='Which mode do you wish to use, options include abg11, n11, ac11')
    for group in parser._action_groups:
        if group.title == "optional arguments":
            optional_args=group
            break
    #if optional_args is not None:
    args = parser.parse_args()

    theoreticalstation = TheoreticalStation(_lfjson_host=args.mgr,
                                            _lfjson_port=args.mgr_port)
    if args.mode == 'abg11':
        theoreticalstation.abg11()
    if args.mode == 'n11':
        theoreticalstation.n11()
    if args.mode == 'ac11':
        theoreticalstation.ac11()




if __name__ == '__main__':
    main()