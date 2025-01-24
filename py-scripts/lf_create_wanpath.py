#!/usr/bin/env python3

'''
NAME:       lf_create_wanpath.py

PURPOSE:    Create a wanpath using the lanforge api given an existing wanlink endpoint

EXAMPLE:    # Create a single wanpath on endpoint A:
            $ ./lf_create_wanpath.py --mgr 192.168.102.158 --mgr_port 8080\
                --wp_name test_wp-A --wl_endp test_wl-A\
                --speed 102400 --latency 25 --max_jitter 50 --jitter_freq 6 --drop_freq 12\
                --log_level debug --debug

            # Create a single wanpath on endpoint B:
            $ ./lf_create_wanpath.py --mgr 192.168.102.158 --mgr_port 8080\
                --wp_name test_wp-B --wl_endp test_wl-B\
                --speed 102400 --latency 25 --max_jitter 50 --jitter_freq 6 --drop_freq 12\
                --log_level debug --debug

            # Create a single wanpath on endpoint A and test all text fields:
            $ ./lf_create_wanpath.py --mgr 192.168.102.158 --mgr_port 8080\
                --wp_name test_wp-C --wl_endp test_wl-A\
                --source_ip 1.1.1.1 --source_ip_mask 2.2.2.2 --dest_ip 3.3.3.3 --dest_ip_mask 4.4.4.4\
                --drop_freq 5 --dup_freq 6 --extra_buffer 7 --jitter_freq 8 --latency 9 --max_drop_amt 10\
                --max_jitter 11 --max_lateness 12 --max_reorder_amt 13 --min_drop_amt 14 --min_reorder_amt 15\
                --reorder_freq 16 --speed 17 --test_mgr default_tm\
                --log_level debug --debug

NOTES:
            # Wanlink must already exist - can be created with lf_create_wanlink.py:
                $ ./lf_create_wanlink.py --mgr 192.168.102.158 --mgr_port 8080 --port_A eth1 --port_B eth2\
                    --speed_A 1024000 --speed_B 2048000 --wl_name test_wl --latency_A 24 --latency_B 32\
                    --max_jitter_A 50 --max_jitter_B 20 --jitter_freq 6 --drop_freq 12\
                    --log_level debug --debug

            # Lanforge api expects 'wanlink' but it is really looking for the endpoint name
                ie. wanlink test_wl has endpoints test_wl-A and test_wl-B.

SCRIPT_CLASSIFICATION:
            Creation

SCRIPT_CATEGORIES:
            Functional

STATUS:     Functional

VERIFIED_ON:
            14-Jan-2024
            GUI Version: 5.4.9
            Kernel Version: 6.11.11+

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2024 Candela Technologies Inc.

INCLUDE_IN_README:
            False
'''

import sys
import importlib
import argparse
import os
import logging

sys.path.append(os.path.join(os.path.abspath(__file__ + '../../../')))
lanforge_api = importlib.import_module('lanforge_client.lanforge_api')
LFUtils = importlib.import_module('py-json.LANforge.LFUtils')
lfcli_base = importlib.import_module('py-json.LANforge.lfcli_base')
LFCliBase = lfcli_base.LFCliBase
from lanforge_client.lanforge_api import LFSession          # noqa: E402
from lanforge_client.lanforge_api import LFJsonCommand      # noqa: E402
from lanforge_client.lanforge_api import LFJsonQuery        # noqa: E402

if sys.version_info[0] != 3:
    print('This script requires Python3')
    exit()

lf_logger_config = importlib.import_module('py-scripts.lf_logger_config')

logger = logging.getLogger(__name__)


class lf_create_wanpath():
    '''wanpath creation and maintenance class

    Handles initialization, creation and updating of a wanpath in lanforge api
    '''

    def __init__(self,
                 lf_mgr=None,
                 lf_port=None,
                 lf_user=None,
                 lf_passwd=None,
                 debug=False):

        '''Initializes instance based on lanforge connection parameters
        Args:
          lf_mgr:   the GUI to connect to
          lf_port:  the port to connect to
          lf_user:  lanforge username (default lanforge)
          lf_psswd: lanforge password (default lanforge)
          debug:    debug flag
        '''
        self.lf_mgr = lf_mgr
        self.lf_port = lf_port
        self.lf_user = lf_user
        self.lf_passwd = lf_passwd
        self.debug = debug

        self.session = LFSession(lfclient_url="http://%s:8080" % self.lf_mgr,
                                 debug=debug,
                                 connection_timeout_sec=4.0,
                                 stream_errors=True,
                                 stream_warnings=True,
                                 require_session=True,
                                 exit_on_error=True)

        self.command: LFJsonCommand
        self.command = self.session.get_command()
        self.query: LFJsonQuery
        self.query = self.session.get_query()

    def add_wanpath(self,
                    alias: str = None,
                    dest_ip: str = None,
                    dest_ip_mask: str = None,
                    drop_every_xth_pkt: str = None,
                    drop_freq: str = None,
                    dup_every_xth_pkt: str = None,
                    dup_freq: str = None,
                    extra_buffer: str = None,
                    follow_binomial: str = None,
                    ignore_bandwidth: str = None,
                    _ignore_dup: str = None,
                    ignore_latency: str = None,
                    ignore_loss: str = None,
                    jitter_freq: str = None,
                    latency: str = None,
                    max_drop_amt: str = None,
                    max_jitter: str = None,
                    max_lateness: str = None,
                    max_reorder_amt: str = None,
                    min_drop_amt: str = None,
                    min_reorder_amt: str = None,
                    playback_capture: str = None,
                    playback_capture_file: str = None,
                    playback_loop: str = None,
                    reorder_every_xth_pkt: str = None,
                    reorder_freq: str = None,
                    source_ip: str = None,
                    source_ip_mask: str = None,
                    speed: str = None,
                    test_mgr: str = None,
                    wanlink: str = None):

        '''adds wanpath to specified wanlink

        Args:
            alias:                     Name of WanPath [R]
            dest_ip:                   Selection filter: Destination IP
            dest_ip_mask:              Selection filter: Destination IP MASK
            drop_every_xth_pkt:        YES to periodically drop every Xth pkt, NO to drop packets randomly
            drop_freq:                 How often, out of 1,000,000 packets, should we purposefully drop a packet
            dup_every_xth_pkt:         YES to periodically duplicate every Xth pkt, NO to duplicate packets randomly
            dup_freq:                  How often, out of 1,000,000 packets, should we purposefully duplicate a packet
            extra_buffer:              Extra amount of bytes to buffer before dropping pkts (units of 1024)
            follow_binomial:           YES to have ok/drop burst lengths follow a binomial distribution
            ignore_bandwidth:          Should we ignore the bandwidth settings from the playback file? YES, NO, or NA
            ignore_dup:                Should we ignore the Duplicate Packet settings from the playback file? YES, NO, or NA
            ignore_latency:            Should we ignore the latency settings from the playback file? YES, NO, or NA
            ignore_loss:               Should we ignore the packet-loss settings from the playback file? YES, NO, or NA
            jitter_freq:               How often, out of 1,000,000 packets, should we apply random jitter
            latency:                   The base latency added to all packets (ms)
            max_drop_amt:              Maximum amount of packets to drop in a row. Default is 1. [D:1]
            max_jitter:                Maximum jitter (ms)
            max_lateness:              Maximum amount of un-intentional delay before pkt is dropped. Default is AUTO
            max_reorder_amt:           Maximum amount of packets by which to reorder, Default is 10. [D:10]
            min_drop_amt:              Minimum amount of packets to drop in a row. Default is 1. [D:1]
            min_reorder_amt:           Minimum amount of packets by which to reorder, Default is 1. [D:1]
            playback_capture:          ON or OFF, should we play back a WAN capture file?
            playback_capture_file:     Name of the WAN capture file to play back
            playback_loop:             Should we loop the playback file, YES or NO or NA
            reorder_every_xth_pk:      YES to periodically reorder every Xth pkt, NO to reorder packets randomly
            reorder_freq:              How often, out of 1,000,000 packets, should we make a packet out of order
            source_ip:                 Selection filter: Source IP
            source_ip_mask:            Selection filter: Source IP MASK
            speed:                     Maximum speed this WanLink will accept (bps)
            test_mgr:                  The name of the Test-Manager this WanPath is to use. Leave blank for no restrictions
            wanlink:                   Name of WanLink endpoint [R]
        '''

        # check for required arguments
        if wanlink is None:
            logger.error('wanlink is None. wanlink must be set to a valid existing wanlink. Exiting')
            exit(1)
        elif alias is None:
            logger.error('alias is None. alias must be set to the desired name of the wanpath. Exiting')
            exit(1)

        # add wanpath via cli command post_add_wanpath
        self.command.post_add_wanpath(alias=alias,
                                      dest_ip=dest_ip,
                                      dest_ip_mask=dest_ip_mask,
                                      drop_every_xth_pkt=drop_every_xth_pkt,
                                      drop_freq=drop_freq,
                                      dup_every_xth_pkt=dup_every_xth_pkt,
                                      dup_freq=dup_freq,
                                      extra_buffer=extra_buffer,
                                      follow_binomial=follow_binomial,
                                      ignore_bandwidth=ignore_bandwidth,
                                      ignore_dup=_ignore_dup,
                                      ignore_latency=ignore_latency,
                                      ignore_loss=ignore_loss,
                                      jitter_freq=jitter_freq,
                                      latency=latency,
                                      max_drop_amt=max_drop_amt,
                                      max_jitter=max_jitter,
                                      max_lateness=max_lateness,
                                      max_reorder_amt=max_reorder_amt,
                                      min_drop_amt=min_drop_amt,
                                      min_reorder_amt=min_reorder_amt,
                                      playback_capture=playback_capture,
                                      playback_capture_file=playback_capture_file,
                                      playback_loop=playback_loop,
                                      reorder_every_xth_pkt=reorder_every_xth_pkt,
                                      reorder_freq=reorder_freq,
                                      source_ip=source_ip,
                                      source_ip_mask=source_ip_mask,
                                      speed=speed,
                                      test_mgr=test_mgr,
                                      wanlink=wanlink)


def parse_args():

    parser = LFCliBase.create_basic_argparse(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Create Wanpaths
            ''',
        description='''\
            NAME:       lf_create_wanpath.py

            PURPOSE:    Create a wanpath using the lanforge api given an existing wanlink endpoint

            EXAMPLE:    # Create a single wanpath on endpoint A:
                        $ ./lf_create_wanpath.py --mgr 192.168.102.158 --mgr_port 8080\
                            --wp_name test_wp-A --wl_endp test_wl-A\
                            --speed 102400 --latency 25 --max_jitter 50 --jitter_freq 6 --drop_freq 12\
                            --log_level debug --debug

                        # Create a single wanpath on endpoint B:
                        $ ./lf_create_wanpath.py --mgr 192.168.102.158 --mgr_port 8080\
                            --wp_name test_wp-B --wl_endp test_wl-B\
                            --speed 102400 --latency 25 --max_jitter 50 --jitter_freq 6 --drop_freq 12\
                            --log_level debug --debug

                        # Create a single wanpath on endpoint A and test all text fields:
                        $ ./lf_create_wanpath.py --mgr 192.168.102.158 --mgr_port 8080\
                            --wp_name test_wp-C --wl_endp test_wl-A\
                            --source_ip 1.1.1.1 --source_ip_mask 2.2.2.2 --dest_ip 3.3.3.3 --dest_ip_mask 4.4.4.4\
                            --drop_freq 5 --dup_freq 6 --extra_buffer 7 --jitter_freq 8 --latency 9 --max_drop_amt 10\
                            --max_jitter 11 --max_lateness 12 --max_reorder_amt 13 --min_drop_amt 14 --min_reorder_amt 15\
                            --reorder_freq 16 --speed 17 --test_mgr default_tm\
                            --log_level debug --debug

            NOTES:
                        # Wanlink must already exist - can be created with lf_create_wanlink.py:
                            $ ./lf_create_wanlink.py --mgr 192.168.102.158 --mgr_port 8080 --port_A eth1 --port_B eth2\
                                --speed_A 1024000 --speed_B 2048000 --wl_name test_wl --latency_A 24 --latency_B 32\
                                --max_jitter_A 50 --max_jitter_B 20 --jitter_freq 6 --drop_freq 12\
                                --log_level debug --debug

                        # Lanforge api expects 'wanlink' but it is really looking for the endpoint name
                            ie. wanlink test_wl has endpoints test_wl-A and test_wl-B.

                        # Note: endp_A is associated with _tx_endp and endp_B is associated with _rx_endp

            SCRIPT_CLASSIFICATION:
                        Creation

            SCRIPT_CATEGORIES:
                        Functional

            STATUS:     Functional

            VERIFIED_ON:
                        14-Jan-2024
                        GUI Version: 5.4.9
                        Kernel Version: 6.11.11+

            LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
                        Copyright 2024 Candela Technologies Inc.

            INCLUDE_IN_README:
                        False
            '''
    )

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    # required args
    required.add_argument('--wanlink', '--wl_endp', dest='wanlink', help='(add wanpath) The name of the wanlink endpoint to which we are adding this WanPath.')
    required.add_argument('--wp_name', '--alias', dest='wp_name', help='(add wanpath) Name of the WanPath')

    # http://www.candelatech.com/lfcli_ug.php#add_wanpath
    # connection args
    optional.add_argument('--lf_user', help='lanforge user name default lanforge', default='lanforge')
    optional.add_argument('--lf_passwd', help='lanforge password defualt lanforge', default='lanforge')

    # creating wanpath args
    optional.add_argument('--dest_ip', help='(add wanpath)Selection filter: Destination IP', default='0.0.0.0')
    optional.add_argument('--dest_ip_mask', help='(add wanpath) Selection filter: Destination IP MASK', default='0.0.0.0')
    optional.add_argument('--drop_freq', help='(add wanpath) How often, out of 1,000,000 packets, should we purposefully drop a packet.', default='0')
    optional.add_argument('--dup_freq', help='(add wanpath) How often, out of 1,000,000 packets, should we purposefully duplicate a packet.', default='0')
    optional.add_argument('--extra_buffer', help='(add wanpath) The extra amount of bytes to buffer before dropping pkts, in units of 1024, use -1 for AUTO. Default: -1', default='-1')
    optional.add_argument('--jitter_freq', help='(add wanpath) How often, out of 1,000,000 packets, should we apply random jitter.', default='0')
    optional.add_argument('--latency', help='(add wanpath) The base latency added to all packets, in milliseconds (or add "us" suffix for microseconds) Default: 20', default='20')
    optional.add_argument('--max_drop_amt', help='(add wanpath) Maximum mount of packets to drop in a row. Default: 1', default='1')
    optional.add_argument('--max_jitter', help='(add wanpath) The maximum jitter, in milliseconds (or ad "us" suffix for microseconds) Default: 10', default='10')
    optional.add_argument('--max_lateness', help='(add wanpath) Maximum amount of un-intentional delay before pkt is dropped. Default: AUTO', default='AUTO')
    optional.add_argument('--max_reorder_amt', help='(add wanpath) Maximum amount of packets by which to reorder, Default is 1.', default='1')
    optional.add_argument('--min_drop_amt', help='(add wanpath) Minimum amount of packets to drop in a row. Default: 1', default='1')
    optional.add_argument('--min_reorder_amt', help='(add wanpath) Minimum amount of packets by which to reorder, Default is 1.', default='1')
    optional.add_argument('--playback_capture', help='(add wanpath) ON or OFF, should we play back a WAN capture file?', default=None)
    optional.add_argument('--playback_capture_file', help='(add wanpath) Name of the WAN capture file to play back. Deafault = None', default=None)
    optional.add_argument('--reorder_freq', help='(add wanpath) How often, out of 1,000,000 packets, should we make a packet out of order.', default=None)
    optional.add_argument('--source_ip', help='(add wanpath) Selection filter: Source IP', default='0.0.0.0')
    optional.add_argument('--source_ip_mask', help='(add wanpath) Selection filter: Source IP MASK', default='0.0.0.0')
    optional.add_argument('--speed', help='(add wanpath The maximum speed this WanLink will accept (bps).', default=1000000)
    optional.add_argument('--test_mgr', help='(add wanpath) The name of the Test-Manager this WanPath is to use. Leave blank for no restrictions.', default=None)

    # wanpath flag args
    optional.add_argument('--drop_every_xth_pkt', help='(set wanpath flag) Periodically drop every Xth pkt, Default: drop packets randomly.', action='store_true')
    optional.add_argument('--dup_every_xth_pkt', help='(set wanpath flag) Periodically duplicate every Xth pkt, Default: duplicate packets randomly.', action='store_true')
    optional.add_argument('--follow_binomial', help='(set wanpath flag) Have ok/drop burst lengths follow a binomial distribution.', action='store_true')
    optional.add_argument('--ignore_bandwidth', help='(set wanpath flag) Should we ignore the bandwidth wsettings from the playback file? Default = "False" action="store_true"', action='store_true')
    optional.add_argument('--ignore_dup', help='(set wanpath flag) Should we ignore the Duplicate Packet settings from the playback file? Default = "False" action="store_true"', action='store_true')
    optional.add_argument('--ignore_latency', help='(set wanpath flag) Should we ignore the packet-loss settings from the playback file? Default = "False" action="store_true"', action='store_true')
    optional.add_argument('-ignore_loss', help='Should we ignore the packet-loss settings from the playback file? YES, NO, or NA.', default=None)
    optional.add_argument('--playback_loop', help='(set wanpath flag) Should we loop the playback file', action='store_true')
    optional.add_argument('--reorder_every_xth_pkt', help='(set wanpath flag) Periodically reorder every Xth pkt, Default: reorder packets randomly.', action='store_true')

    return parser.parse_args()


def validate_args(args):
    '''Validate CLI arguments.'''
    if args.wanlink is None:
        logger.error('--wanlink required')
        exit(1)
    elif args.wp_name is None:
        logger.error('--alias required')
        exit(1)


def main():

    args = parse_args()

    help_summary = 'This script will create and configure a wanpath given an existing wanlink endpoint.'

    if args.help_summary:
        print(help_summary)
        exit(0)

    validate_args(args)

    # Configure logging
    logger_config = lf_logger_config.lf_logger_config()
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)
    # initialize wanlink
    wanpath = lf_create_wanpath(lf_mgr=args.mgr,
                                lf_port=8080,
                                lf_user=args.lf_user,
                                lf_passwd=args.lf_passwd,
                                debug=True)

    # create wanpath
    wanpath.add_wanpath(alias=args.wp_name,
                        dest_ip=args.dest_ip,
                        dest_ip_mask=args.dest_ip_mask,
                        drop_every_xth_pkt=args.drop_every_xth_pkt,
                        drop_freq=args.drop_freq,
                        dup_every_xth_pkt=args.dup_every_xth_pkt,
                        dup_freq=args.dup_freq,
                        extra_buffer=args.extra_buffer,
                        follow_binomial=args.follow_binomial,
                        ignore_bandwidth=args.ignore_bandwidth,
                        _ignore_dup=args.ignore_dup,
                        ignore_latency=args.ignore_latency,
                        ignore_loss=args.ignore_loss,
                        jitter_freq=args.jitter_freq,
                        latency=args.latency,
                        max_drop_amt=args.max_drop_amt,
                        max_jitter=args.max_jitter,
                        max_lateness=args.max_lateness,
                        max_reorder_amt=args.max_reorder_amt,
                        min_drop_amt=args.min_drop_amt,
                        min_reorder_amt=args.min_reorder_amt,
                        playback_capture=args.playback_capture,
                        playback_capture_file=args.playback_capture_file,
                        playback_loop=args.playback_loop,
                        reorder_every_xth_pkt=args.reorder_every_xth_pkt,
                        reorder_freq=args.reorder_freq,
                        source_ip=args.source_ip,
                        source_ip_mask=args.source_ip_mask,
                        speed=args.speed,
                        test_mgr=args.test_mgr,
                        wanlink=args.wanlink)


if __name__ == "__main__":
    main()
