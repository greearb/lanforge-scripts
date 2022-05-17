#!/usr/bin/env python3

"""
NAME: lf_we_can_wifi_capacity_test.py

Use './lf_we_can_wifi_capacity_test.py --help' to see command line usage and options
Copyright 2021 Candela Technologies Inc
License: Free to distribute and modify. LANforge systems must be licensed.
example: ./python lf_we_can_wifi_capacity_test.py  --mgr 192.168.200.220 --mgr_port 8080 --ssid wecan --security wpa2 --radio wiphy0

Note: To Run this script gui should be opened with

    path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
          pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
          ./lfclient.bash -cli-socket 3990

"""
import importlib
import os
import sys

import pandas as pd

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

import argparse
from lf_report import lf_report

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")

cv_test_manager = importlib.import_module("py-json.cv_test_manager")
cv_test = cv_test_manager.cv_test
cv_add_base_parser = cv_test_manager.cv_add_base_parser
cv_base_adjust_parser = cv_test_manager.cv_base_adjust_parser
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_bar_graph = lf_graph.lf_bar_graph
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
from lf_wifi_capacity_test import WiFiCapacityTest


class we_can_wifi_capacity((Realm)):
    def __init__(self,
                 ssid=None,
                 security=None,
                 password=None,
                 sta_list=None,
                 upstream=None,
                 radio=None,
                 host="localhost",
                 port=8080,
                 resource=1,
                 use_ht160=False,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        if sta_list is None:
            sta_list = []
        super().__init__(lfclient_host=host,
                         lfclient_port=port),
        self.upstream = upstream
        self.host = host
        self.port = port
        self.ssid = ssid
        self.sta_list = sta_list
        self.security = security
        self.password = password
        self.radio = radio
        self.debug = _debug_on
        self.station_profile = self.new_station_profile()
        self.station_profile.lfclient_url = self.lfclient_url
        self.station_profile.ssid = self.ssid
        self.station_profile.ssid_pass = self.password
        self.station_profile.security = self.security
        self.station_profile.debug = self.debug
        self.station_profile.use_ht160 = use_ht160

    def get_data(self):
        resource_id_real, phone_name, mac_address, user_name, phone_radio, rx_rate, tx_rate = self.get_resource_data()

        rx_rate = [(i.split(" ")[0]) if (i.split(" ")[0]) != '' else '0' for i in rx_rate]
        tx_rate = [(i.split(" ")[0]) if (i.split(" ")[0]) != '' else '0' for i in tx_rate]
        print("DATAAAAAAAAAAAA:\n", resource_id_real, phone_name, mac_address, user_name, phone_radio, rx_rate, tx_rate)
        dataframe = pd.read_csv("/home/amrit-candela/Desktop/wifi-capacity-2022-04-26-10-52-21/csv-data/data-"
                                "Combined_Mbps__60_second_running_average-1.csv", header=1)
        # dataFrame.drop("Unnamed: 2",inplace=True, axis=1)
        del dataframe["Unnamed: 2"]
        print(dataframe)
        download_rate = []
        upload_rate = []
        resource_id = []
        for column in dataframe:
            # for each resource id getting upload and Download Data
            resource_id.append(column.split('.')[0])
            download_rate.append(float(dataframe[column].loc[0]))
            upload_rate.append(float(dataframe[column].loc[1]))
        # Plotting Graph 01
        # Creating DataFrames
        rx_tx_df = pd.DataFrame({
            "upload": upload_rate,
            "download": download_rate,
        }, index=[phone_name[0], phone_name[0]])

        # rx_tx_plot = rx_tx_df.plot.bar(alpha=0.5)
        # for p in rx_tx_plot.patches:
        #     height = p.get_height()
        #     rx_tx_plot.annotate('{}Mbps'.format(height),
        #             xy=(p.get_x() + p.get_width() / 2, height),
        #             xytext=(0, 10),  # 3 points vertical offset
        #             textcoords="offset points",
        #             ha='center', va='bottom')
        # plt.tight_layout()
        # plt.show()

        # Plotting Graph 03
        # Creating DataFrames
        # print(rx_rate, tx_rate)
        Band_2G_5G_df = pd.DataFrame({
            "upload": upload_rate,
            "download": download_rate,
        }, index=["( " + phone_radio[0] + " )" + phone_name[0], "( " + phone_radio[0] + " )" + phone_name[0]])
        # band_2G_5G_plot = Band_2G_5G_df.plot.bar(alpha=0.5)
        # for p in band_2G_5G_plot.patches:
        #     height = p.get_height()
        #     band_2G_5G_plot.annotate('{}'.format(height),
        #                         xy=(p.get_x() + p.get_width() / 2, height),
        #                         xytext=(0, 3),  # 3 points vertical offset
        #                         textcoords="offset points",
        #                         ha='center', va='bottom')
        # plt.tight_layout()
        # plt.show()

        # Plotting Graph 04
        # Creating DataFrames
        print(rx_rate, tx_rate)
        link_rate_df = pd.DataFrame({
            "Link Rx Rate": rx_rate,
            "Actual Rx Rate": download_rate,
            "Link Tx Rate": tx_rate,
            "Actual Tx Rate": upload_rate,
        }, index=[phone_name[0], phone_name[0]])

        # rx_tx_plot = rx_tx_df.plot.bar(alpha=0.5)
        # for p in rx_tx_plot.patches:
        #     height = p.get_height()
        #     rx_tx_plot.annotate('{}'.format(height),
        #                         xy=(p.get_x() + p.get_width() / 2, height),
        #                         xytext=(0, 3),  # 3 points vertical offset
        #                         textcoords="offset points",
        #                         ha='center', va='bottom')
        # plt.tight_layout()
        # plt.show()

        # Plotting Graph  05 (User Name)
        avg_rate = []
        for i in range(len(upload_rate)):
            avg_rate.append((upload_rate[i] + download_rate[i]) / 2)
        # Creating DataFrames
        user_name_df = pd.DataFrame({
            "upload": upload_rate,
            "download": download_rate,
            "Average": avg_rate,
        }, index=[user_name[0], user_name[0]])

        # user_name_plot = user_name_df.plot.bar(alpha=0.5)
        # for p in user_name_plot.patches:
        #     height = p.get_height()
        #     user_name_plot.annotate('{}'.format(height),
        #                             xy=(p.get_x() + p.get_width() / 2, height),
        #                             xytext=(0, 3),  # 3 points vertical offset
        #                             textcoords="offset points",
        #                             ha='center', va='bottom')
        # plt.tight_layout()
        # plt.show()
        phone_data = [resource_id_real, phone_name, mac_address, user_name, phone_radio, rx_rate, tx_rate]
        self.generate_report(phone_data, rx_tx_df, Band_2G_5G_df, link_rate_df, user_name_df)
        # exit(0)

        # Getting Resource id, phone name, mac address, username, phone radio
        # resource_id, phone_name, mac_address, user_name, phone_radio = self.get_resource_data()
        # resource_id_phone_company_dict_map = {}
        # resource_id_phone_radio_dict_map = {}
        # for i in range(len(phone_name)):
        #     resource_id_phone_company_dict_map[resource_id[i]] = phone_name[i]
        #     resource_id_phone_radio_dict_map[resource_id[i]] = phone_radio[i]
        # print("Company Name: ", resource_id_phone_company_dict_map)
        # print("Radio Name: ", resource_id_phone_radio_dict_map)
        #
        # print(self.get_resource_data())

    def generate_report(self, get_data, rx_tx_df, Band_2G_5G_df, link_rate_df, user_name_df):

        resource_id = get_data[0]
        phone_name = get_data[1]
        mac_address = get_data[2]
        user_name = get_data[3]
        phone_radio = get_data[4]
        rx_rate = get_data[5]
        tx_rate = get_data[6]

        report = lf_report(_output_html="we-can-wifi-capacity.html", _output_pdf="we-can-wifi-capacity.pdf",
                           _results_dir_name="we-can wifi-capacity result")

        report_path = report.get_path()
        report_path_date_time = report.get_path_date_time()

        print("path: {}".format(report_path))
        print("path_date_time: {}".format(report_path_date_time))

        report.set_title("WE-CAN Wi-Fi Capacity test for Real Clients")
        report.build_banner()

        report.start_content_div()
        report.set_text(
            "<h3>Objective:" + "<h4>The WE-CAN wifi-capacity Test is designed to measure the performance of an Access "
                               "Point when handling different types of real clients.")
        report.build_date_time()
        report.build_text()

        # report.start_content_div()
        # report.set_text("<h3>Phone Details:" + "<h4>All the Phone Details are providede in the table below.")
        # report.build_text()

        data = {
            "Resource ID": resource_id,
            "Phone Name": phone_name,
            "MAC Address": mac_address,
            "User Name": user_name,
            "Phone Radio": phone_radio,
            "Rx Rate (Mbps) ": rx_rate,
            "Tx Rate (Mbps)" : tx_rate,
        }
        phone_details = pd.DataFrame(data)

        report.start_content_div()
        report.set_table_title("<h3>Phone Details")
        report.build_table_title()
        report.set_table_dataframe(phone_details)
        report.build_table()

        report.save_bar_chart(rx_tx_df, "rx-tx")
        report.start_content_div()
        report.build_chart_title("Rx Tx Chart")
        report.build_chart("rx-tx.png")

        report.save_bar_chart(Band_2G_5G_df, "2G-5G")
        report.start_content_div()
        report.build_chart_title("2G vs 5G ")
        report.build_chart("2G-5G.png")

        report.save_bar_chart(link_rate_df, "link_rate")
        report.start_content_div()
        report.build_chart_title("Link Rate Chart")
        report.build_chart("link_rate.png")

        report.save_bar_chart(user_name_df, "user_name")
        report.start_content_div()
        report.build_chart_title("User Name ")
        report.build_chart("user_name.png")

        report.build_footer()
        html_file = report.write_html()
        print("returned file {}".format(html_file))
        print(html_file)

        report.write_pdf(_page_size='Legal', _orientation='Portrait')

    def get_resource_data(self):
        resource_id_list = []
        phone_name_list = []
        mac_address = []
        user_name = []
        phone_radio = []
        rx_rate = []
        tx_rate = []
        eid_data = self.json_get("ports?fields=alias,mac,mode,Parent Dev,rx-rate,tx-rate")
        for alias in eid_data["interfaces"]:
            for i in alias:
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0':
                    resource_id_list.append(i.split(".")[1])
                    resource_hw_data = self.json_get("/resource/" + i.split(".")[0] + "/" + i.split(".")[1])
                    # Getting MAC address
                    mac = alias[i]["mac"]

                    rx = alias[i]["rx-rate"]
                    tx = alias[i]["tx-rate"]
                    rx_rate.append(rx)
                    tx_rate.append(tx)
                    # Getting username
                    user = resource_hw_data['resource']['user']
                    user_name.append(user)
                    # Getting user Hardware details/Name
                    hw_name = resource_hw_data['resource']['hw version'].split(" ")
                    name = " ".join(hw_name[0:2])
                    phone_name_list.append(name)
                    mac_address.append(mac)
                if int(i.split(".")[1]) > 1 and alias[i]["alias"] == 'wlan0' and alias[i]["parent dev"] == 'wiphy0':
                    # phone_radio.append(alias[i]['mode'])
                    # Mapping Radio Name in human readable format
                    if 'a' not in alias[i]['mode'] or "20" in alias[i]['mode']:
                        phone_radio.append('2G')
                    elif 'AUTO' in alias[i]['mode']:
                        phone_radio.append("AUTO")
                    else:
                        phone_radio.append('2G/5G')
        return resource_id_list, phone_name_list, mac_address, user_name, phone_radio, rx_rate, tx_rate


def main():
    parser = argparse.ArgumentParser(
        prog="we_can_wifi_capacity_test.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
            ./we_can_wifi_capacity_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge \
                 --instance_name wct_instance --config_name wifi_config --upstream 1.1.eth1 --batch_size 1 --loop_iter 1 \
                 --protocol UDP-IPv4 --duration 6000 --pull_report --stations 1.1.sta0000,1.1.sta0001 \
                 --create_stations --radio wiphy0 --ssid test-ssid --security open --paswd [BLANK] \
                   """)

    cv_add_base_parser(parser)  # see cv_test_manager.py

    parser = argparse.ArgumentParser(description="Netgear AP DFS Test Script")
    parser.add_argument('--mgr', type=str, help='host name', default="localhost")
    parser.add_argument('--port', type=str, help='port number', default="8080")
    parser.add_argument("--upstream", type=str, default="", help="Upstream port for wifi capacity test ex. 1.1.eth1")
    parser.add_argument("--batch_size", type=str, default="", help="station increment ex. 1,2,3")
    parser.add_argument("--protocol", type=str, default="", help="Protocol ex.TCP-IPv4")
    parser.add_argument("--lf_user", type=str, default="", help="lanforge user name ex. root,lanforge")
    parser.add_argument("--lf_password", type=str, default="", help="lanforge user password ex. root,lanforge")
    parser.add_argument("--duration", type=str, default="", help="duration in ms. ex. 5000")
    parser.add_argument("--download_rate", type=str, default="10Mbps",
                        help="Select requested download rate.  Kbps, Mbps, Gbps units supported.  Default is 10Mbps")
    parser.add_argument("--upload_rate", type=str, default="10Mbps",
                        help="Select requested upload rate.  Kbps, Mbps, Gbps units supported.  Default is 10Mbps")
    parser.add_argument("--influx_host", type=str, default="localhost", help="NA")
    parser.add_argument("--local_lf_report_dir",
                        help="--local_lf_report_dir <where to pull reports to>  default '' put where dataplane script run from",
                        default="")

    args = parser.parse_args()

    WFC_Test = WiFiCapacityTest(lfclient_host=args.mgr,
                                lf_port=args.port,
                                lf_user=args.lf_user,
                                lf_password=args.lf_password,
                                upstream=args.upstream,
                                batch_size=args.batch_size,
                                protocol=args.protocol,
                                duration=args.duration,
                                # pull_report=args.pull_report,
                                download_rate=args.download_rate,
                                upload_rate=args.upload_rate,
                                influx_host=args.mgr,
                                influx_port=8086,
                                local_lf_report_dir=args.local_lf_report_dir,
                                )
    # WFC_Test.setup()
    # time1 = datetime.datetime.now() - timedelta(minutes=30)
    # print("time 12 hr format : ", (datetime.datetime.now() - timedelta(minutes=30)).strftime('%Y-%m-%d-%I-%M-%S'))
    # WFC_Test.run()
    # print("Code Stopped")
    # print("Time2:  ", (datetime.datetime.now()).strftime('%Y-%m-%d-%I-%M-%S'))
    wifi_capacity = we_can_wifi_capacity(host=args.mgr, port=args.port)
    wifi_capacity.get_data()
    # WFC_Test.check_influx_kpi(args)


if __name__ == "__main__":
    main()
