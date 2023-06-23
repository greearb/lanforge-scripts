#!/usr/bin/env python3
"""
    NAME:       lf_sniff_radio.py
    PURPOSE:    This script will sniff a Radio after changing the Radio settings.

                Radio settings: channel radio mode  AUTO, 802.11a, 802.11b, etc... refer
                                        py-json/LANforge/set_wifi_radio.py for different modes

    EXAMPLE:    python3 lf_sniff_radio.py
                        --mgr localhost
                        --mgr_port 8080
                        --outfile /home/lanforge/test_sniff.pcap
                        --duration 20
                        --channel 52
                        --radio_mode AUTO
                        --monitor_name moni0a

    NOTES:

    The configuration of the monitor is: sudo iw dev <monitor> info
    Sample:

    [lanforge@ct523c-3b7b ~]$ sudo iw dev SNIFF_5G_40 info
    Interface SNIFF_5G_40
    ifindex 2413
    wdev 0x900000002
    addr 04:f0:21:85:62:22
    type monitor
    wiphy 9
    channel 36 (5180 MHz), width: 20 MHz (no HT), center1: 5180 MHz
    txpower 0.00 dBm
    [lanforge@ct523c-3b7b ~]$

    # manual way to set the center frequency
     iw dev moni10a set freq <control frequency> <Band width> <center frequency>

    # sometimes the radio wiphy 9 (above) may not match the wiphy radio
        when iw parent is not matching, can be show with command:
        cat /sys/class/ieee80211/wiphy0/index

    IK:  two features from lf_sniff that are needed for ofdma sniffing is obtaining the AID
    and using multiple sniffer radios for targeting multiple stations

"""
import sys
import os
import importlib
import argparse
import time
import paramiko
import logging


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
                 sniff_flags=None):
        super().__init__(lfclient_host, lfclient_port)
        self.lfclient_host = lfclient_host
        self.lfclient_port = lfclient_port
        self.debug = debug_on_
        # self.local_realm = realm.Realm(lfclient_host=self.lfclient_host,
        #                                lfclient_port=self.lfclient_port,
        #                                debug_=self.debug)
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
        self.sniff_snapshot_bytes = sniff_snapshot_bytes # default to max size
        self.sniff_flags = sniff_flags # will default to dumpcap, see wifi_monitor_profile::SNIFF_X constants

        # TODO allow the channel_frequency to be entered
        # if self.channel is None and self.channel_freq is None:
        #    print("either --channel or --channel_freq needs to be set")
        #    exit(1)
        # elif self.channel_freq is not None:
        #    self.freq = self.channel_freq
        if self.channel_freq is not None:
            self.freq = self.channel_freq
            logger.info("channel frequency {freq}".format(freq=self.channel_freq))
        # conversion of 6e channel to frequency
        # ch_6e = (f - 5000 )  / 5
        # f = (ch_6e * 5) + 5000
        elif self.channel is not None:
            if self.channel != 'AUTO':
                if 'e' in self.channel:
                    channel_6e = self.channel.replace('e', '')
                    self.freq = ((int(channel_6e) + 190) * 5) + 5000
                    lf_6e_chan = int(channel_6e) + 190
                    logger.info("6e_chan: {chan} lf_6e_chan: {lf_chan} frequency: {freq}".format(chan=self.channel, lf_chan=lf_6e_chan, freq=self.freq))
                    self.channel = lf_6e_chan
                else:
                    if int(self.channel) <= 13:
                        # channel 1 is 2412 ,
                        self.freq = 2407 + int(self.channel) * 5
                    elif int(self.channel) == 14:
                        self.freq = 2484
                    # 5g or 6g Candela numbering
                    else:
                        self.freq = int(self.channel) * 5 + 5000
                    logger.info("channel: {chan}  frequency: {freq}".format(chan=self.channel, freq=self.freq))

        if self.channel_bw != '20':
            if self.center_freq is None:
                logger.info("--center_freq need to be set for bw greater the 20")
                exit(1)

    def setup(self, ht40_value, ht80_value, ht160_value):
        # TODO: Store original channel settings so that radio can be set back to original values.
        self.monitor.set_flag(param_name="disable_ht40", value=ht40_value)
        self.monitor.set_flag(param_name="disable_ht80", value=ht80_value)
        self.monitor.set_flag(param_name="ht160_enable", value=ht160_value)
        self.monitor.create(radio_=self.radio, channel=self.channel, frequency=self.freq, mode=self.mode, name_=self.monitor_name)

    def start(self):
        self.monitor.admin_up()
        LFUtils.wait_until_ports_appear(self.lfclient_url, self.monitor_name, debug=self.debug)
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

    def get_sniff_info(self):
        try:
            # creating shh client object we use this object to connect to router
            ssh = paramiko.SSHClient()
            # automatically adds the missing host key
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.lfclient_host, port=22, username='lanforge', password='lanforge',
                        allow_agent=False, look_for_keys=False, banner_timeout=600)
            command = "sudo iw dev {sniffer} info".format(sniffer=self.monitor_name)
            stdin, stdout, stderr = ssh.exec_command(command)
            self.monitor_info = stdout.readlines()
            logger.info("sudo iw dev {sniffer} info: \n {monitor_info}".format(sniffer=self.monitor_name, monitor_info=self.monitor_info))
            # self.monitor_info = [line.replace(
            #    '\n', '') for line in self.monitor_info]
            ssh.close()
            time.sleep(1)
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print("####", e, "####")
            exit(1)
        except TimeoutError as e:
            print("####", e, "####")
            exit(1)

        return self.monitor_info

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


def main():
    parser = argparse.ArgumentParser(
        prog="lf_sniff_radio.py",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            lf_sniff_radio.py will create a monitor on LANforge (cli command add_monitor)

            ''',

        description='''\
        This script will sniff a Radio following modifications to its settings.
         lf_sniff_radio.py will create a monitor and be able to capture wireshark pcap files:

        The monitor also uses iw commands to set up the proper bw and frequency to be monitored

        Note:

        iw [options] dev <devname> set freq <freq> [NOHT|HT20|HT40+|HT40-|5MHz|10MHz|80MHz]
        dev <devname> set freq <control freq> [5|10|20|40|80|80+80|160] [<center1_freq> [<center2_freq>]]

        Example to monitor channel 36 (5180)
        sudo iw dev <monitor/devname> set freq 5180 40 5190

        for bw of 20 do not need to set the control frequency

        Verify the configuration with :(need to do sudo)
        iw dev <monitor/devname> info

        example:
        [lanforge@ct523c-3ba3 ~]$ sudo iw dev SNIFF_5G_40 info
        [sudo] password for lanforge:
        Interface SNIFF_5G_40
            ifindex 49
            wdev 0x2
            addr d8:f8:83:36:4c:a0
            type monitor
            wiphy 0
            channel 36 (5180 MHz), width: 20 MHz, center1: 5180 MHz
            txpower 0.00 dBm
        [lanforge@ct523c-3ba3 ~]$


        Help: 5Ghz frequencies

        Tested on 02/16/2023:
         kernel version: 5.19.17+
         gui version: 5.4.6
         the script modified a radio and created a pcap file as expected when ran directly on a lanforge system (ct523c & ct521a).

        ''',

        usage="""./lf_sniff_radio.py
        --mgr localhost
        --mgr_port 8080
        --radio wiphy0
        --outfile /home/lanforge/test_sniff.pcap
        --duration 1
        --channel 36
        --channel_bw 40
        --center_freq 5190
        --radio_mode AUTO
        --monitor_name Sniffer0

        AX210 sniff command
        ===================
        
        ./lf_sniff_radio.py
        --mgr 192.168.0.104
        --mgr_port 8080
        --radio wiphy7
        --outfile /home/lanforge/sniff_6G_80.pcap
        --duration 20
        //--channel 1e
        --channel_bw 80
        --channel_freq 5955
        --center_freq 5985
        --radio_mode AUTO
        --monitor_name SNIFF_6G_80
        --disable_ht40 0
        --disable_ht80 0
        --ht160_enable 0
        --ax210
        --num_stations 1
        --security wpa2
        --ssid axe11000_5g
        --password lf_axe11000_5g
        --ax210_scan_time 10


        """)

    parser.add_argument('--mgr', type=str, help='--mgr: IP Address of LANforge', default="localhost")
    parser.add_argument('--mgr_port', type=int, help='--mgr_port: HTTP Port of LANforge', default=8080)
    parser.add_argument('--radio', type=str, help='--radio: Radio to sniff', default="wiphy0")
    parser.add_argument('--outfile', type=str, help='--outfile: give the filename with path',
                        default="/home/lanforge/test_pcap.pcap")
    parser.add_argument('--duration', type=int, help='--duration duration in sec, for which you want to capture',
                        default=60)
    parser.add_argument('--channel', type=str, help='''
                                    --channel Set channel pn selected Radio, the channel [52, 56 ...]
                                    channel will get converted to the control frequency.
                                    Must enter Channel
                                    ''',
                        default='36')
    parser.add_argument('--channel_freq', type=str, help='''
                                   --channel_freq  this is the frequency that the channel operates at
                                   Must enter --channel or --channel_freq
                                   --channel_freq takes presidence if both entered if value not zero
                                   ''')
    parser.add_argument('--channel_bw', type=str, help='--channel_bw select the bandwidth to be monitored, [ [20|40|80|80+80|160]], default=20',
                        default='20')
    parser.add_argument('--center_freq', type=str, help='''
                        --center_freq  select the bandwidth to be monitored, not needed if bw is 20
                        ''',
                        default=None)

    parser.add_argument('--radio_mode', type=str, help='--radio_mode select the radio mode [AUTO, 802.11a, 802.11b, '
                                                       '802.11ab ...]', default="AUTO")
    parser.add_argument('--monitor_name', type=str, help='Wi-Fi monitor name', default="sniffer0")
    parser.add_argument('--disable_ht40', type=str, help='Enable/Disable \"disable_ht40\" [0-disable,1-enable]',
                        default=0)
    parser.add_argument('--disable_ht80', type=str, help='Enable/Disable \"disable_ht80\" [0-disable,1-enable]',
                        default=0)
    parser.add_argument('--ht160_enable', type=str, help='Enable/Disable \"ht160_enable\\ [0-disable,1-enable]" ',
                        default=0)

    parser.add_argument('--ax210', help='--ax210 will create a station on the ax210 to get the regulatory domain for 6g and admin down the station then create the monitor for 6g on the AX210 radio', action='store_true')
    parser.add_argument('--number_template', help='Start the station numbering with a particular number. Default is 0000', default=0000)
    parser.add_argument('--station_list', help='Optional: User defined station names, can be a comma or space separated list', nargs='+', default=None)
    parser.add_argument('--upstream_port', help='--upstream_port upstream port default: eth2', default='eth2')
    parser.add_argument('--side_a_min_rate', help='--side_a_min_rate bps rate minimum for side_a default: 1024000', default=1024000)
    parser.add_argument('--side_b_min_rate', help='--side_b_min_rate bps rate minimum for side_b default: 1024000', default=1024000)
    parser.add_argument('--sta_prefix', help='--sta_prefix <station prefix>   --sta_prefix  sta   : default: wlan', default='wlan')
    parser.add_argument('--security', help='WiFi Security protocol: < open | wep | wpa | wpa2 | wpa3 >', default='open')
    parser.add_argument('--ssid', help='WiFi SSID for script objects to associate to', default='axe11000_5g')
    parser.add_argument('--password', help='WiFi passphrase/password/key', default='[BLANK]')
    parser.add_argument('--mode', help='Used to force mode of stations default: 0 (auto)', default=0)
    parser.add_argument('--num_stations', type=int, default=1, help='Number of stations to create default 1 for AX210 sniffing')
    parser.add_argument('--ax210_scan_time', default='20', help='Time to wait for scan')
    parser.add_argument('--ap', help='Used to force a connection to a particular AP')

    # Logging information
    # logging configuration
    parser.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')
    parser.add_argument("--lf_logger_config_json", help="--lf_logger_config_json <json file> , json configuration of logger")

    parser.add_argument('--sniff_bytes', default=None, help='keep this many bytes per packet, helps to reduce overall capture size')
    parser.add_argument('--sniff_using', default=None,
                        help="""Default sniffer is wireshark, which is only useful from a desktop setting.
                        Combine options with a comma: dumpcap,mate_xterm
        tshark:             headless tshark utility
        dumpcap:            headless dumpcap utility
        mate_terminal:      make tshark/dumpcap interactive in a MATE terminal
        mate_xterm:         make tshark/dumpcap interactive in an xterm
        mate_kill_dumpcap:  kill previously issued dumpcap""")
    args = parser.parse_args()

    logger_config = lf_logger_config.lf_logger_config()
    # set the logger level to requested value
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    # if args.channel is None and args.channel_freq is None:
    #    print('--channel or --channel_freq most be entered')

    if args.ax210:
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
        # allow 10 seconds for a scan
        logger.info("wait {scan_time} for scan on AX210".format(scan_time=args.ax210_scan_time))
        for i in range(0, int(args.ax210_scan_time)):
            logger.info("AX210 scan network, PLease wait: {scan_time}".format(scan_time=(int(args.ax210_scan_time) - i)))
            time.sleep(1)
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
        except:
            print(f"Strange sniff length [{args.sniff_bytes}], please choose a positive value")
            exit(1)
    obj = SniffRadio(lfclient_host=args.mgr,
                     lfclient_port=args.mgr_port,
                     radio=args.radio,
                     outfile=args.outfile,
                     duration=args.duration,
                     channel=args.channel,
                     channel_freq=args.channel_freq,
                     channel_bw=args.channel_bw,
                     center_freq=args.center_freq,
                     radio_mode=args.radio_mode,
                     monitor_name=args.monitor_name,
                     sniff_flags=sniff_flags_choice,
                     sniff_snapshot_bytes=sniff_snaplen_choice)
    obj.setup(int(args.disable_ht40), int(args.disable_ht80), int(args.ht160_enable))

    if args.ax210:
        create_l3.stop()

    # TODO: Add wait-for logic instead of a sleep
    time.sleep(5)

    # check
    obj.start()

    # the informaiton is gotten during start
    # obj.get_sniff_info()

    obj.cleanup()

    if args.ax210:
        create_l3.cleanup()

    # TODO:  Check if passed or not.


if __name__ == '__main__':
    main()
