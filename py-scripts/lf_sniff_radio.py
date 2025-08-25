#!/usr/bin/env python3
# TODO: Multiple sniffers, grab AID from LANforge station for use in OFDMA sniffing
"""
NAME:       lf_sniff_radio.py

PURPOSE:    This script runs a WiFi packet capture using the provided radio, creating the capture
            interface as specified.

EXAMPLE:    # Capture on specified channel for 20 seconds, saving output to file
            ./lf_sniff_radio.py \
                --radio     1.1.wiphy0 \
                --channel   52 \
                --duration  20 \
                --outfile   /home/lanforge/wifi_capture.pcap \

            # Capture 6 GHz channels on AX210/BE200 radios
            # This requires workaround for firmware limitation, where radio must detect supported
            # regulatory domain before enabling 6 GHz channels
            ./lf_sniff_radio.py \
                --radio                     1.1.wiphy0 \
                --duration                  20 \
                --channel_bw                80 \
                --channel_freq              5955 \
                --center_freq               5985 \
                --6ghz_workaround           \
                --num_stations              1 \
                --security                  wpa2 \
                --ssid                      test_ssid \
                --password                  lf_axe11000_5g \
                --6ghz_workaround_scan_time 1

NOTES:      Configuration utilizes the 'iw' utility to some extent

            While monitor configuration may largely be viewed through the LANforge GUI,
            commands like 'iw moni0 info' may be useful to verify configuration.
"""
import sys
import os
import importlib
import argparse
import time
import paramiko
import logging
import traceback


logger = logging.getLogger(__name__)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
createL3 = importlib.import_module("py-scripts.create_l3_stations")
wifi_monitor_profile = importlib.import_module("py-json.wifi_monitor_profile")


class SniffRadio(Realm):
    def __init__(self,
                 lfclient_host="localhost",
                 lfclient_port=8080,
                 radio="wiphy0",
                 outfile="/home/lanforge/test_pcap.pcap",
                 duration=60,
                 channel=None,
                 channel_freq=None,
                 channel_bw=None,
                 center_freq=None,
                 radio_mode="AUTO",
                 debug_on_=True,
                 monitor_name=None,
                 sniff_snapshot_bytes=None,
                 sniff_flags=None,
                 **kwargs):
        super().__init__(lfclient_host, lfclient_port)
        self.lfclient_host = lfclient_host
        self.lfclient_port = lfclient_port
        self.debug = debug_on_

        self.monitor = self.new_wifi_monitor_profile()
        self.outfile = outfile
        self.radio = radio
        self.channel = channel
        self.channel_freq = channel_freq
        self.channel_bw = channel_bw
        self.center_freq = center_freq
        self.duration = duration
        self.mode = radio_mode
        self.monitor_name = monitor_name
        self.monitor_info = ''
        self.sniff_snapshot_bytes = sniff_snapshot_bytes  # default to max size
        self.sniff_flags = sniff_flags  # will default to dumpcap, see wifi_monitor_profile::SNIFF_X constants

        # User should enter either channel frequency in MHz or the channel number
        if self.channel_freq is not None:
            self.freq = self.channel_freq
            logger.info("channel frequency {freq}".format(freq=self.channel_freq))

        elif self.channel and self.channel != "AUTO":
            if 'e' in self.channel:
                # 6 GHz channel specified per-specification
                #
                # Conversion formulas between 6 GHz channel and frequency (in MHz):
                #   Channel   = (Frequency - 5000) / 5
                #   Frequency = (Channel * 5) + 5000
                channel_6e = self.channel.replace('e', '')
                self.freq = ((int(channel_6e) + 190) * 5) + 5000
                self.channel = int(channel_6e) + 190

                logger.debug(f"User input channel: {channel_6e}e, Calculated channel: {self.channel}, Calculated frequency: {self.freq}")
            else:
                if int(self.channel) <= 13:
                    # Standard 2.4 GHz channel
                    self.freq = 2407 + int(self.channel) * 5
                elif int(self.channel) == 14:
                    # Channel 14 in 2.4 GHz band is a special case. It doesn't follow formula
                    # for other 2.4 GHz channels and is only permitted in Japan for legacy modes
                    # (DSSS and CCK, aka 802.11b)
                    self.freq = 2484
                else:
                    # Either 5 GHz channel specified per-specification or 6 GHz channel specified per-Candela numbering
                    self.freq = int(self.channel) * 5 + 5000

                logger.debug(f"User input channel: {channel}, Calculated frequency: {self.freq}")

        # Presently center frequency is needed for channel widths larger than 20 MHz
        # TODO: Permit omission of center frequency and implement calculation in script
        if self.channel_bw != '20' and not self.center_freq:
            logger.error("Center frequency must be specified for channel widths larger than 20 MHz "
                         "using the '--center_freq' parameter. Run with '--help' for more information")
            exit(1)

    def setup(self, ht40_value, ht80_value, ht160_value):
        # TODO: Store original channel settings so that radio can be set back to original values.
        self.monitor.set_flag(param_name="disable_ht40", value=ht40_value)
        self.monitor.set_flag(param_name="disable_ht80", value=ht80_value)
        self.monitor.set_flag(param_name="ht160_enable", value=ht160_value)
        self.monitor.create(radio_=self.radio, channel=self.channel, frequency=self.freq, mode=self.mode, name_=self.monitor_name)

    def start(self):
        self.monitor.admin_up()
        monitor_eid = "1." + str(self.monitor.resource) + "." + self.monitor_name
        logger.debug("Monitor name: " + self.monitor_name + ", monitor_eid:  " + monitor_eid)
        LFUtils.wait_until_ports_appear(self.lfclient_url, monitor_eid, debug=self.debug)
        # TODO:  Use LFUtils.wait_until_ports_admin_up instead of sleep, check return code.
        # time.sleep(5)
        self.set_freq(ssh_root=self.lfclient_host, ssh_passwd='lanforge', freq=self.freq)
        self.monitor.start_sniff(capname=self.outfile, duration_sec=self.duration, flags=self.sniff_flags,
                                 snap_len_bytes=self.sniff_snapshot_bytes)
        for i in range(0, self.duration):
            logger.info("running sniffer for {duration} more seconds".format(duration=(self.duration - i)))
            time.sleep(1)
        logger.info("Sniffing Completed Success Check {outfile}".format(outfile=self.outfile))
        self.monitor.admin_down()
        time.sleep(2)

    # for 6E
    # For example for channel 7 with 80Mhz bw , here are the monitor commands possible
    # iw dev moni10a set freq 5955 80 5985
    # iw dev moni10a set freq 5975 80 5985
    # iw dev moni10a set freq 5995 80 5985
    # iw dev moni10a set freq 6015 80 5985

    # for 20 MHz the center frequency does not need to be entered since it is the same

    def set_freq(self, ssh_root, ssh_passwd, freq=0):
        if self.channel_bw == '20':
            cmd = f'. lanforge.profile\nsudo iw dev {self.monitor_name} set freq {freq}\n'
        else:
            cmd = f'. lanforge.profile\nsudo iw dev {self.monitor_name} set freq {freq} {self.channel_bw} {self.center_freq}\n'

        cmd1 = f'iw dev {self.monitor_name} info'
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ssh_root, 22, 'lanforge', ssh_passwd)
            time.sleep(10)
            stdout = ssh.exec_command(cmd, get_pty=True)
            stdout[0].write(f"{ssh_passwd}\n")
            stdout[0].flush()
            stdout = (stdout[1].readlines())
            print(stdout, "----- set channel frequency")
            stdout = ssh.exec_command(cmd1)
            stdout = (stdout[1].readlines())
            print(stdout, "----- channel frequency info")
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print("####", e, "####")
            exit(1)
        except TimeoutError as e:
            print("####", e, "####")
            exit(1)

        ssh.close()

    def cleanup(self):
        # TODO:  Add error checking to make sure monitor port really went away.
        # TODO:  Set radio back to original channel
        self.monitor.cleanup()


def parse_args():
    parser = argparse.ArgumentParser(
        prog="lf_sniff_radio.py",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='lf_sniff_radio.py will create a monitor on LANforge (cli command add_monitor)',

        description=r"""
NAME:       lf_sniff_radio.py

PURPOSE:    This script runs a WiFi packet capture using the provided radio, creating the capture
            interface as specified.

EXAMPLE:    # Capture on specified channel for 20 seconds, saving output to file
            ./lf_sniff_radio.py \
                --radio     1.1.wiphy0 \
                --channel   52 \
                --duration  20 \
                --outfile   /home/lanforge/wifi_capture.pcap \

            # Capture 6 GHz channels on AX210/BE200 radios
            # This requires workaround for firmware limitation, where radio must detect supported
            # regulatory domain before enabling 6 GHz channels
            ./lf_sniff_radio.py \
                --radio                     1.1.wiphy0 \
                --duration                  20 \
                --channel_bw                80 \
                --channel_freq              5955 \
                --center_freq               5985 \
                --6ghz_workaround           \
                --num_stations              1 \
                --security                  wpa2 \
                --ssid                      test_ssid \
                --password                  lf_axe11000_5g \
                --6ghz_workaround_scan_time 1

NOTES:      Configuration utilizes the 'iw' utility to some extent

            While monitor configuration may largely be viewed through the LANforge GUI,
            commands like 'iw moni0 info' may be useful to verify configuration.
        """)

    parser.add_argument('--mgr', type=str, help='IP Address of LANforge',
                        default="localhost")
    parser.add_argument('--mgr_port', type=int, help='HTTP Port of LANforge',
                        default=8080)
    parser.add_argument('--radio', type=str, help='Radio to sniff with',
                        default="wiphy0")
    parser.add_argument('--outfile', type=str, help='Give the filename with path',
                        default="/home/lanforge/test_pcap.pcap")
    parser.add_argument('--duration', type=int, help='Duration in sec for which you want to capture',
                        default=60)
    parser.add_argument('--channel', type=str,
                        help='Set channel pn selected Radio, the channel [52, 56 ...]\n'
                             'channel will get converted to the control frequency.\n'
                             'Must enter Channel',
                        default='36')
    parser.add_argument('--channel_freq', type=str,
                        help='Frequency that the channel operates at\n'
                             'Must enter --channel or --channel_freq\n'
                             '--channel_freq takes presidence if both entered if value not zero')
    parser.add_argument('--channel_bw', type=str, help='Select the bandwidth to be monitored, [ [20|40|80|80+80|160]], default=20',
                        default='20')
    parser.add_argument('--center_freq', type=str,
                        help='Select the bandwidth to be monitored\n'
                             '(not needed if channel width is 20MHz',
                        default=None)
    parser.add_argument('--radio_mode', type=str, help='Select the radio mode [AUTO, 802.11a, 802.11b, 802.11ab ...]',
                        default="AUTO")
    parser.add_argument('--monitor_name', type=str, help='Wi-Fi monitor name',
                        default="sniffer0")
    parser.add_argument('--disable_ht40', type=str, help='Enable/Disable \"disable_ht40\" [0-disable,1-enable]',
                        default=0)
    parser.add_argument('--disable_ht80', type=str, help='Enable/Disable \"disable_ht80\" [0-disable,1-enable]',
                        default=0)
    parser.add_argument('--ht160_enable', type=str, help='Enable/Disable \"ht160_enable\\ [0-disable,1-enable]" ',
                        default=0)
    parser.add_argument('--6ghz_workaround', '--ax210',
                        help='Perform workaround for Intel AX210 or BE200 radio 6GHz monitor mode firmware limitation\n'
                             'before sniffing packets. Radio firmware requires a scan of 6GHz-capable regulatory domain\n'
                             'before granting access to 6GHz channels on a monitor mode interface.\n',
                        dest='do_6ghz_workaround',
                        action='store_true')
    parser.add_argument('--6ghz_workaround_scan_time', '--ax210_scan_time', help='Time to wait for scan in 6GHz workaround',
                        dest='do_6ghz_workaround_scan_time',
                        default='20')
    parser.add_argument('--num_stations', type=int, help='Number of stations to create default 1 for AX210 sniffing',
                        default=1)
    parser.add_argument('--number_template', help='Start the station numbering with a particular number. Default is 0000',
                        default=0000)
    parser.add_argument('--station_list', help='Optional: User defined station names, can be a comma or space separated list', nargs='+',
                        default=None)
    parser.add_argument('--upstream_port', help='Upstream port',
                        default='eth2')
    parser.add_argument('--side_a_min_rate', help='bps rate minimum for side_a default: 1024000',
                        default=1024000)
    parser.add_argument('--side_b_min_rate', help='bps rate minimum for side_b default: 1024000',
                        default=1024000)
    parser.add_argument('--sta_prefix', help='Prefix used when creating station',
                        default='wlan')
    parser.add_argument('--security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >',
                        default='open')
    parser.add_argument('--ssid', help='WiFi SSID for script objects to associate to',
                        default='axe11000_5g')
    parser.add_argument('--password', help='WiFi passphrase/password/key',
                        default='[BLANK]')
    parser.add_argument('--mode', help='Used to force mode of stations default: 0 (auto)',
                        default=0)
    parser.add_argument('--ap', help='Used to force a connection to a particular AP')

    # Logging information
    # logging configuration
    parser.add_argument('--log_level', help='Set logging level: debug | info | warning | error | critical',
                        default=None)
    parser.add_argument("--lf_logger_config_json", help="--lf_logger_config_json <json file> , json configuration of logger")

    parser.add_argument('--sniff_bytes', help='keep this many bytes per packet, helps to reduce overall capture size',
                        default=None)
    parser.add_argument('--sniff_using',
                        help='Default sniffer is Wireshark, which is only useful from a desktop setting.\n'
                             'Combine options with a comma: dumpcap,mate_xterm\n'
                             'tshark:             headless tshark utility\n'
                             'dumpcap:            headless dumpcap utility\n'
                             'mate_terminal:      make tshark/dumpcap interactive in a MATE terminal\n'
                             'mate_xterm:         make tshark/dumpcap interactive in an xterm\n'
                             'mate_kill_dumpcap:  kill previously issued dumpcap',
                        default=None)
    parser.add_argument('--help_summary', help='shows summary of the script', action='store_true')

    return parser.parse_args()


def do_6ghz_workaround(args):
    """Workaround for Intel AX210 or BE200 radio 6GHz monitor mode firmware limitation."""
    # TODO: Decouple by removing args dependency
    if args.num_stations:
        num_sta = int(args.num_stations)
    elif args.station_list:
        num_sta = len(args.station_list)

    if not args.station_list:
        station_list = LFUtils.portNameSeries(
            prefix_=args.sta_prefix, start_id_=int(
                args.number_template), end_id_=num_sta + int(
                args.number_template) - 1, padding_number_=10000, radio=args.radio)
    else:
        if ',' in args.station_list[0]:
            station_list = args.station_list[0].split(',')
        elif ' ' in args.station_list[0]:
            station_list = args.station_list[0].split()
        else:
            station_list = args.station_list

    create_l3 = createL3.CreateL3(host=args.mgr,
                                  port=args.mgr_port,
                                  number_template=str(args.number_template),
                                  sta_list=station_list,
                                  name_prefix="VT",
                                  upstream=args.upstream_port,
                                  ssid=args.ssid,
                                  password=args.password,
                                  radio=args.radio,
                                  security=args.security,
                                  side_a_min_rate=args.side_a_min_rate,
                                  side_b_min_rate=args.side_b_min_rate,
                                  mode=args.mode,
                                  ap=args.ap,
                                  _debug_on=True)
    create_l3.build()
    create_l3.start()

    # Allow station to scan
    logger.info("wait {scan_time} for scan on AX210".format(scan_time=args.do_6ghz_workaround_scan_time))
    for i in range(0, int(args.do_6ghz_workaround_scan_time)):
        logger.info("Intel station performing scan, please wait: {scan_time}".format(scan_time=(int(args.do_6ghz_workaround_scan_time) - i)))
        time.sleep(1)

    return create_l3


def main():
    help_summary = "This script performs WiFi packet capture using the radio and channel specified " \
                   "by the user for the configured duration. When performing 6 GHz packet capture " \
                   "using an Intel AX210 or BE200 2x2 radio, a workaround is required. See the output " \
                   "when run with '--help' or the header of the script for example usage."

    args = parse_args()
    if args.help_summary:
        print(help_summary)
        exit(0)

    logger_config = lf_logger_config.lf_logger_config()
    # set the logger level to requested value
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    # if args.channel is None and args.channel_freq is None:
    #    print('--channel or --channel_freq most be entered')

    if args.do_6ghz_workaround:
        workaround_cx = do_6ghz_workaround(args)

    sniff_flags_choice = None
    if args.sniff_using:
        sniff_flags_choice = wifi_monitor_profile.flagname_to_hex(flagnames=args.sniff_using)

    sniff_snaplen_choice = None
    if args.sniff_bytes:
        try:
            bytesize = int(args.sniff_bytes)
            if bytesize > -1:
                sniff_snaplen_choice = bytesize
            else:
                raise ValueError("bad sniff_bytes")
        except Exception as x:
            traceback.print_exception(Exception, x, x.__traceback__, chain=True)
            print(f"Strange sniff length [{args.sniff_bytes}], please choose a positive value")
            exit(1)

    # The '**vars(args)' unpacks arguments into named parameters
    # of the SniffRadio initializer. Argument names must match initializer
    # parameter names to be set.
    obj = SniffRadio(lfclient_host=args.mgr,
                     lfclient_port=args.mgr_port,
                     sniff_flags=sniff_flags_choice,
                     sniff_snapshot_bytes=sniff_snaplen_choice,
                     **vars(args))

    # Perform pre-capture configuration
    obj.setup(int(args.disable_ht40), int(args.disable_ht80), int(args.ht160_enable))
    if args.do_6ghz_workaround:
        workaround_cx.stop()
    time.sleep(5)  # TODO: Add wait-for logic instead of a sleep

    # Run capture
    obj.start()

    # Capture complete, perform cleanup
    obj.cleanup()
    if args.do_6ghz_workaround:
        workaround_cx.cleanup()


if __name__ == '__main__':
    main()
