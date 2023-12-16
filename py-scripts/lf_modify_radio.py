#!/usr/bin/env python3
"""
NAME: lf_modify_radio.py

PURPOSE: Set the spatial streams and channel of a radio
        To Modify eth interface such as enabling/disabling dhcp

EXAMPLE:
$ ./lf_modify_radio.py --host 192.168.100.205 --radio "1.1.wiphy0" --channel 36 --antenna 7 --debug

to enable dhcp-ipv4 on eth interface :
    ./ python3 lf_modify_radio.py --mgr 192.168.200.105 --radio 1.1.eth2 --enable_dhcp True

to disable dhcp-ipv4 on eth interface and provide static ip from arguement parsers
 ./ python3 lf_modify_radio.py --mgr 192.168.200.105 --radio 1.1.eth2 --static True

NOTES:


TO DO NOTES:

"""
import os
import sys
import importlib
import argparse
from pprint import pformat
import logging


if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
from lanforge_client.lanforge_api import LFSession
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFJsonQuery
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")

lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

logger = logging.getLogger(__name__)


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #

#http://www.candelatech.com/lfcli_ug.php#set_wifi_radio
class lf_modify_radio():
    def __init__(self,
                 lf_mgr=None,
                 lf_port=8080,
                 lf_user=None,
                 lf_passwd=None,
                 debug=False,
                 static_ip=None,
                 ip_mask=None,
                 gateway_ip=None,
                 session=None):
        self.lf_mgr = lf_mgr
        self.lf_port = lf_port
        self.lf_user = lf_user
        self.lf_passwd = lf_passwd
        self.debug = debug
        self.static_ip = static_ip
        self.ip_mask = ip_mask
        self.gateway_ip = gateway_ip

        if not session:
            self.session = LFSession(lfclient_url="http://%s:8080" % self.lf_mgr,
                                     debug=debug,
                                     connection_timeout_sec=4.0,
                                     stream_errors=True,
                                     stream_warnings=True,
                                     require_session=True,
                                     exit_on_error=True)
        # type hinting
        self.command: LFJsonCommand
        self.command = self.session.get_command()
        self.query: LFJsonQuery
        self.query = self.session.get_query()

    # TODO make a set wifi radio similiar to add_profile
    def set_wifi_radio(self,
                       _resource=None,
                       _radio=None,
                       _shelf=None,
                       _antenna=None,
                       _channel=None,
                       _txpower=None,
                       _country_code=None,
                       _flags=None):
        country_num = _country_code
        if _country_code:
            if isinstance(_country_code, str) and _country_code.isnumeric():
                country_num = int(_country_code)

            elif isinstance(country_num, str) and (country_num in LFUtils.COUNTRY_CODES_NUMBERS):
                country_num = LFUtils.COUNTRY_CODES_NUMBERS[_country_code]

        self.command.post_set_wifi_radio(resource=_resource,
                                         radio=_radio,
                                         shelf=_shelf,
                                         antenna=_antenna,
                                         channel=_channel,
                                         txpower=_txpower,
                                         country=_country_code,
                                         flags=_flags,
                                         debug=self.debug)

    def enable_dhcp_eth(self, interface="1.1.eth2"):
        port_ = interface.split(".")
        self.command.post_set_port(shelf=port_[0],
                                   resource= port_[1],
                                   port=port_[2],
                                   current_flags="2147483648",
                                   interest="8552366080",
                                   debug=self.debug)

    def disable_dhcp_static(self, interface):
        port_ = interface.split(".")
        self.command.post_set_port(shelf=port_[0],
                                   resource=port_[1],
                                   port=port_[2],
                                   ip_addr =  self.static_ip,
                                   netmask = self.ip_mask,
                                   gateway = self.gateway_ip,
                                   interest="8552366108",
                                   debug=self.debug)


def main():
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='''
        modifies radio configuration , antenna, radio, channel or txpower
            lf_modify_radio.py --mgr 192.168.0.104 --radio 1.1.wiphy6 --txpower 17 --debug
        ''')
    parser.add_argument("--host", "--mgr", dest='mgr',
                        help='specify the GUI to connect to')
    parser.add_argument("--mgr_port",
                        help="specify the GUI to connect to, default 8080", default="8080")
    parser.add_argument("--lf_user",
                        help="lanforge user name, default : lanforge", default="lanforge")
    parser.add_argument("--lf_passwd",
                        help="lanforge password, default : lanforge", default="lanforge")
    parser.add_argument("--radio",
                        help='name of the radio to modify: e.g. 1.1.wiphy0')
    parser.add_argument("--antenna",
                        help='number of spatial streams: 0 Diversity (All), 1 Fixed-A (1x1), 4 AB (2x2), 7 ABC (3x3), 8 ABCD (4x4), 9 (8x8) default = -1',
                        default='-1')
    parser.add_argument("--channel",
                        help='channel of the radio: e.g. 6 (2.4G) or 36 (5G) default: AUTO',
                        default='AUTO')
    parser.add_argument("--txpower",
                        help='radio tx power default: AUTO system defaults',
                        default='AUTO')
    country_code_list: list = list(LFUtils.COUNTRY_CODES_NUMBERS.keys())
    country_code_list.extend([str(x) for x in LFUtils.COUNTRY_CODES_NUMBERS.values()])
    parser.add_argument("--country", "--regdom", "--country_code",
                        choices=country_code_list,
                        help="Set the country code for the lanforge resource. "
                             "This needs to set all radios on the resource to the same country code. "
                             "Requires --radio (eg 1.1.wiphy0) for reference to determine resource.")
    # Logging Configuration
    parser.add_argument('--log_level', default=None,
                        help='Set logging level: debug | info | warning | error | critical')
    parser.add_argument("--lf_logger_config_json",
                        help="--lf_logger_config_json <json file> , json configuration of logger")
    parser.add_argument('--debug',
                        help='Legacy debug flag, turnn on legacy debug ',
                        action='store_true')
    parser.add_argument("--enable_dhcp", default=False,
                        help="set to True if wanted to enbale DHCP-IPv4 on eth interface")
    parser.add_argument("--static", default=False,
                        help="True if client will be created with static ip")

    parser.add_argument("--static_ip", default="192.168.2.100",
                        help="if static option is True provide static ip to client")

    parser.add_argument("--ip_mask", default="255.255.255.0",
                        help="if static is true provide ip mask to client")

    parser.add_argument("--gateway_ip", default="192.168.2.50",
                        help="if static is true provide gateway ip")

    args = parser.parse_args()

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    # set the logger level to debug
    if args.log_level:
        logger_config.set_level(level=args.log_level)

    # lf_logger_config_json will take presidence to changing debug levels
    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()


    if not args.radio:
        print("No radio name provided")
        exit(1)

    modify_radio = lf_modify_radio(lf_mgr=args.mgr,
                                   lf_port=args.mgr_port,
                                   lf_user=args.lf_user,
                                   lf_passwd=args.lf_passwd,
                                   debug=args.debug,
                                   static_ip=args.static_ip,
                                   ip_mask=args.ip_mask,
                                   gateway_ip=args.gateway_ip)
    if args.enable_dhcp == "True":
        modify_radio.enable_dhcp_eth(interface=args.radio)
    elif args.static == "True":
        modify_radio.disable_dhcp_static(interface=args.radio)
    else:
        shelf, resource, radio, *nil = LFUtils.name_to_eid(args.radio)
        country_num = None
        if args.country:
            if args.country.isnumeric():
                country_num = int(args.country)
            elif args.country in LFUtils.COUNTRY_CODES_NUMBERS:
                country_num = LFUtils.COUNTRY_CODES_NUMBERS[args.country]
            else:
                raise ValueError(f"Unknown country code: [{args.country}]")

        modify_radio.set_wifi_radio(_resource=resource,
                                    _radio=radio,
                                    _shelf=shelf,
                                    _antenna=args.antenna,
                                    _channel=args.channel,
                                    _txpower=args.txpower,
                                    _country_code=country_num)



    '''
    session = LFSession(lfclient_url="http://%s:8080" % args.host,
                        debug=args.debug,
                        connection_timeout_sec=2.0,
                        stream_errors=True,
                        stream_warnings=True,
                        require_session=True,
                        exit_on_error=True)
    command: LFJsonCommand
    command = session.get_command()
    query: LFJsonQuery
    query = session.get_query()

    shelf, resource, radio, *nil = LFUtils.name_to_eid(args.radio)
    
    command.post_set_wifi_radio(resource=resource,
                                radio=radio,
                                shelf=shelf,
                                antenna=args.antenna,
                                channel=args.channel,
                                txpower=args.txpower,
                                debug=args.debug)
    '''

if __name__ == "__main__":
    main()
#
