import argparse
import sys
import os

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))
import wlan_test
# main method

def main():
    ap = argparse.ArgumentParser(description="WLAN Capacity Calculator")

    # Station : 11abg

    ap.add_argument("-sta", "--station", help="Enter Station Name : [11abg,11n,11ac](by Default 11abg)")
    ap.add_argument("-t", "--traffic", help="Enter the Traffic Type : [Data,Voice](by Default Data)")
    ap.add_argument("-p", "--phy",
                    help="Enter the PHY Bit Rate of Data Flow : [1, 2, 5.5, 11, 6, 9, 12, 18, 24, 36, 48, 54](by Default 54)")
    ap.add_argument("-e", "--encryption", help="Enter the Encryption  : [None,  WEP ,  TKIP, CCMP](by Default None)")
    ap.add_argument("-q", "--qos", help="Enter the QoS = : [No,  Yes](by Default [No for 11abg] and [Yes for 11n])")
    ap.add_argument("-m", "--mac",
                    help="Enter the 802.11 MAC Frame  : [Any Value](by Default [106 for 11abg] and [1538 for 11n])")
    ap.add_argument("-b", "--basic", nargs='+',
                    help="Enter the Basic Rate Set : [1,2, 5.5, 11, 6, 9, 12, 18, 24, 36, 48, 54]"
                         " (by Default [1 2 5.5 11 6 12] for 11abg, [6 12 24] for 11n/11ac])")
    ap.add_argument("-pre", "--preamble", help="Enter Preamble value : [ Short, Long, N/A](by Default Short)")
    ap.add_argument("-s", "--slot", help="Enter the Slot Time  : [Short,  Long, N/A](by Default Short)")
    ap.add_argument("-co", "--codec", help="Enter the Codec Type (Voice Traffic): {[ G.711 ,  G.723 ,  G.729]"
                                           "by Default G.723 for 11abg, G.711 for 11n} and"
                                           "{['Mixed','Greenfield'] by Default Mixed for 11ac}")
    ap.add_argument("-r", "--rts", help="Enter the RTS/CTS Handshake : [No,  Yes](by Default No)")
    ap.add_argument("-c", "--cts", help="Enter the CTS-to-self (protection)	: [No,  Yes](by Default No)")

    # Station : 11n and 11ac

    ap.add_argument("-d", "--data",
                    help="Enter the Data/Voice MCS Index : ['0','1','2','3','4','5','6','7','8','9','10',"
                         "'11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26',"
                         "'27','28','29','30','31']by Default 7")
    ap.add_argument("-ch", "--channel", help="Enter the Channel Bandwidth = : ['20','40'] by Default 40 for 11n and "
                                             "['20','40','80'] by Default 80 for 11ac")
    ap.add_argument("-gu", "--guard", help="Enter the Guard Interval = : ['400','800'] (by Default 400)")
    ap.add_argument("-high", "--highest",
                    help="Enter the Highest Basic MCS = : ['0','1','2','3','4','5','6','7','8','9',"
                         "'10','11','12','13','14','15','16','17','18','19','20','21','22','23','24',"
                         "'25','26','27','28','29','30','31'](by Default 1)")
    ap.add_argument("-pl", "--plcp",
                    help="Enter the PLCP Configuration = : ['Mixed','Greenfield'] (by Default Mixed) for 11n")
    ap.add_argument("-ip", "--ip", help="Enter the IP Packets per A-MSDU = : ['0','1','2','3','4','5','6','7','8','9',"
                                        "'10','11','12','13','14','15','16','17','18','19','20'] (by Default 0)")
    ap.add_argument("-mc", "--mc",
                    help="Enter the MAC Frames per A-MPDU = : ['0','1','2','3','4','5','6','7','8',"
                         "'9','10','11','12','13','14','15','16','17','18','19','20','21','22','23',"
                         "'24','25','26','27','28','29','30','31','32','33','34','35','36','37','38',"
                         "'39','40','41','42','43','44','45','46','47','48','49','50','51','52','53',"
                         "'54','55','56','57','58','59','60','61','62','63','64'](by Default [42 for 11n] and [64 for 11ac])")
    ap.add_argument("-cw", "--cwin", help="Enter the CWmin (leave alone for default) = : [Any Value] (by Default 15)")
    ap.add_argument("-spa", "--spatial", help="Enter the Spatial Streams  = [1,2,3,4] (by Default 4)")
    ap.add_argument("-rc", "--rtscts", help="Enter the RTS/CTS Handshake and CTS-to-self "
                                            "  = ['No','Yes'] (by Default No for 11ac)")

    try:
        args = ap.parse_args()
        # Station
        if (args.station is not None):
            Calculator_name = args.station
        else:
            Calculator_name = "11abg"

        # Traffic Type
        if (args.traffic is not None):
            traffic_name = args.traffic
        else:
            traffic_name = "Data"

        # PHY Bit Rate
        if (args.phy is not None):
            phy_name = args.phy
        else:
            phy_name = "54"

        # Encryption
        if (args.encryption is not None):
            encryption_name = args.encryption
        else:
            encryption_name = "None"

        # QoS

        if (args.qos is not None):
            qos_name = args.qos
        else:
            if "11abg" in Calculator_name:
                qos_name = "No"
            if "11n" in Calculator_name or "11ac" in Calculator_name:
                qos_name = "Yes"

        # 802.11 MAC Frame

        if (args.mac is not None):
            mac_name = args.mac
        else:
            mac_name = "1518"

        # Basic Rate Set

        if (args.basic is not None):
            basic_name = args.basic
        else:
            basic_name = ['1', '2', '5.5', '11', '6', '12', '24']

        # Preamble value

        if (args.preamble is not None):
            preamble_name = args.preamble
        else:
            preamble_name = "Short"

        # Slot Time

        if (args.slot is not None):
            slot_name = args.slot
        else:
            slot_name = "Short"

        # Codec Type (Voice Traffic)

        if (args.codec is not None):
            codec_name = args.codec
        else:
            if "11abg" in Calculator_name:
                codec_name = "G.723"
            if "11n" in Calculator_name:
                codec_name = "G.711"
            if "11ac" in Calculator_name:
                codec_name = "Mixed"

        # RTS/CTS Handshake

        if (args.rts is not None):
            rts_name = args.rts
        else:
            rts_name = "No"

        # CTS - to - self(protection)

        if (args.cts is not None):
            cts_name = args.cts
        else:
            cts_name = "No"

        # station = 11n and 11ac

        # Data/Voice MCS Index

        if (args.data is not None):
            data_name = args.data
        else:
            if "11n" in Calculator_name:
                data_name = "7"
            if "11ac" in Calculator_name:
                data_name = "9"

        # Channel Bandwidth

        if (args.channel is not None):
            channel_name = args.channel
        else:
            if "11n" in Calculator_name:
                channel_name = "40"
            if "11ac" in Calculator_name:
                channel_name = "80"

        # Guard Interval

        if (args.guard is not None):
            guard_name = args.guard
        else:
            guard_name = "400"

        # Highest Basic MCS

        if (args.highest is not None):
            highest_name = args.highest
        else:
            highest_name = '1'

        # PLCP Configuration

        if (args.plcp is not None):
            plcp_name = args.plcp
        else:
            plcp_name = "Mixed"

        # IP Packets per A-MSDU

        if (args.ip is not None):
            ip_name = args.ip
        else:
            ip_name = "0"

        # MAC Frames per A-MPDU

        if (args.mc is not None):
            mc_name = args.mc
        else:
            if "11n" in Calculator_name:
                mc_name = '42'
            if "11ac" in Calculator_name:
                mc_name = '64'

        # CWmin (leave alone for default)

        if (args.cwin is not None):
            cwin_name = args.cwin
        else:
            cwin_name = '15'

        # Spatial Streams

        if (args.spatial is not None):
            spatial_name = args.spatial
        else:
            spatial_name = '4'

        # RTS/CTS Handshake and CTS-to-self

        if (args.rtscts is not None):
            rtscts_name = args.rtscts
        else:
            rtscts_name = 'No'


    except Exception as e:
        logging.exception(e)
        exit(2)

    # Select station(802.11a/b/g/n/ac standards)

    if "11abg" in Calculator_name:
        Station1 = wlan_test.abg11_calculator(traffic_name, phy_name, encryption_name, qos_name, mac_name, basic_name,
                                    preamble_name, slot_name, codec_name, rts_name, cts_name)
        Station1.input_parameter()
    if "11n" in Calculator_name:
        Station2 = wlan_test.n11_calculator(traffic_name, data_name, channel_name, guard_name, highest_name, encryption_name,
                                  qos_name, ip_name,
                                  mc_name, basic_name, mac_name,
                                  codec_name, plcp_name, cwin_name, rts_name, cts_name)
        Station2.input_parameter()
    if "11ac" in Calculator_name:
        Station3 = wlan_test.ac11_calculator(traffic_name, data_name, spatial_name, channel_name, guard_name, highest_name,
                                   encryption_name
                                   , qos_name, ip_name, mc_name, basic_name, mac_name,
                                   codec_name, cwin_name, rtscts_name)
        Station3.input_parameter()


if __name__ == "__main__":
    main() 