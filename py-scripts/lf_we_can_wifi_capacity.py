#!/usr/bin/env python3

"""
NAME: lf_we_can_wifi_capacity_test.py

PURPOSE:
    This program is used for running Wi-Fi capacity test on real clients (Phones).
    The class will generate an output directory based on date and time in the /home/lanforge/html-reports/ .

example: ./python python3 lf_we_can_wifi_capacity_test.py --mgr 192.168.200.85 --port 8080 --upstream 1.1.eth1
--batch_size 5 --duration 60000 --download_rate 1Gbps --upload_rate 1Gbps --protocol TCP-UDP-IPv4 --lf_user lanforge
--lf_password lanforge

Note: To Run this script gui should be opened with

    path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
          pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
          ./lfclient.bash -cli-socket 3990

    WE-CAN app should be installed on the phone and should be Connected to lanforge server.

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2021 Candela Technologies Inc

"""
import importlib
import os
import sys
import glob
import shutil
import math

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
                 protocol=None,
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
        self.protocol = protocol,
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

    def get_folder_name(self):
        cwd = os.getcwd()
        list_of_files = glob.glob(cwd + "/*")  # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file

    def get_data(self):
        resource_id_real, phone_name, mac_address, user_name, phone_radio, rx_rate, tx_rate = self.get_resource_data()
        folder_directory = self.get_folder_name()
        rx_rate = [(i.split(" ")[0]) if (i.split(" ")[0]) != '' else '0' for i in rx_rate]
        tx_rate = [(i.split(" ")[0]) if (i.split(" ")[0]) != '' else '0' for i in tx_rate]
        print(resource_id_real, "\n", phone_name, "\n", mac_address, "\n", user_name, "\n", phone_radio,
              "\n", rx_rate, "\n", tx_rate)
        dataframe = pd.read_csv(folder_directory + "/csv-data/data-Combined_Mbps__60_second_running_average-1.csv",
                                header=1)
        print(dataframe)
        udp_download_rate = []
        tcp_download_rate = []
        udp_upload_rate = []
        tcp_upload_rate = []
        download_rate = []
        upload_rate = []
        resource_id = []
        if self.protocol[0] == "TCP and UDP IPv4":
            for column in dataframe:
                # for each resource id getting upload and Download Data
                resource_id.append(column.split('.')[0])
                if not math.isnan(dataframe[column].loc[0]):
                    udp_download_rate.append(float("{:.2f}".format(dataframe[column].loc[0])))
                    tcp_download_rate.append(float("{:.2f}".format(dataframe[column].loc[1])))
                    udp_upload_rate.append(float("{:.2f}".format(dataframe[column].loc[2])))
                    tcp_upload_rate.append(float("{:.2f}".format(dataframe[column].loc[3])))
            # Plotting Graph 01
            rx_tx_df = pd.DataFrame({
                "udp upload": udp_upload_rate,
                "tcp upload": tcp_upload_rate,
                "udp download": udp_download_rate,
                "tcp download": tcp_download_rate,
            }, index=[i for i in phone_name])

            # Plotting Graph 03
            Band_2G_5G_df = pd.DataFrame({
                "udp download": udp_download_rate,
                "tcp download": tcp_download_rate,
                "udp upload": udp_upload_rate,
                "tcp upload": tcp_upload_rate,
            }, index=[str("( " + phone_radio[i] + " )") for i in range(len(phone_name))])

            udp_actual_rate = [float("{:.2f}".format(udp_download_rate[i] + udp_upload_rate[i])) for i in
                               range(len(udp_download_rate))]
            tcp_actual_rate = [float("{:.2f}".format(tcp_download_rate[i] + tcp_upload_rate[i])) for i in
                               range(len(udp_download_rate))]
            print(udp_actual_rate, "\n", tcp_actual_rate, "\n", rx_rate, "\n", tx_rate)
            link_rate_df = pd.DataFrame({
                "Actual UDP": udp_actual_rate,
                "Actual TCP": tcp_actual_rate,
                "Link Rate(rx)": [int(i) for i in rx_rate],
                "Link Rate(tx)": [int(i) for i in tx_rate],
            }, index=[phone_name[i] for i in range(len(phone_name))])

            # Plotting Graph  05 (User Name)
            udp_avg_rate = []
            tcp_avg_rate = []
            for i in range(len(udp_download_rate)):
                udp_avg_rate.append(float("{:.2f}".format((udp_upload_rate[i] + udp_download_rate[i]) / 2)))
                tcp_avg_rate.append(float("{:.2f}".format((tcp_upload_rate[i] + tcp_download_rate[i]) / 2)))
            # Creating DataFrames
            user_name_df = pd.DataFrame({
                "udp download": udp_download_rate,
                "udp upload": udp_upload_rate,
                "udp average ": udp_avg_rate,
                "tcp upload": tcp_upload_rate,
                "tcp download": tcp_download_rate,
                "tcp average ": tcp_avg_rate,
            }, index=[user_name[i] for i in range(len(tcp_download_rate))])

        elif self.protocol[0] == "TCP-IPv4" or self.protocol[0] == "UDP-IPv4":
            for column in dataframe:
                # for each resource id getting upload and Download Data
                resource_id.append(column.split('.')[0])
                if not math.isnan(dataframe[column].loc[0]):
                    download_rate.append(float("{:.2f}".format(dataframe[column].loc[0])))
                    upload_rate.append(float("{:.2f}".format(dataframe[column].loc[1])))
            rx_tx_df = pd.DataFrame({
                "upload": upload_rate,
                "download": download_rate,
            }, index=[i for i in phone_name])

            # Plotting Graph 03
            # Creating DataFrames
            Band_2G_5G_df = pd.DataFrame({
                "upload": upload_rate,
                "download": download_rate,
            }, index=[str("( " + phone_radio[i] + " )") for i in range(len(phone_name))])

            # Plotting Graph 04
            # Creating DataFrames
            print(rx_rate, tx_rate)
            link_rate_df = pd.DataFrame({
                "Link Rx": [int(i) for i in rx_rate],
                "Actual Rx": download_rate,
                "Link Tx": [int(i) for i in tx_rate],
                "Actual Tx": upload_rate,
            }, index=[phone_name[i] for i in range(len(upload_rate))])

            # Plotting Graph  05 (User Name)
            avg_rate = []
            for i in range(len(upload_rate)):
                avg_rate.append(float("{:.2f}".format((upload_rate[i] + download_rate[i]) / 2)))
            # Creating DataFrames
            user_name_df = pd.DataFrame({
                "upload": upload_rate,
                "download": download_rate,
                "Average": avg_rate,
            }, index=[user_name[i] for i in range(len(upload_rate))])
        #
        phone_data = [resource_id_real, phone_name, mac_address, user_name, phone_radio, rx_rate, tx_rate]
        self.generate_report(folder_directory, phone_data, rx_tx_df, Band_2G_5G_df, link_rate_df, user_name_df)

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

    def generate_report(self, file_derectory, get_data, rx_tx_df, Band_2G_5G_df, link_rate_df, user_name_df):

        resource_id = get_data[0]
        phone_name = get_data[1]
        mac_address = get_data[2]
        user_name = get_data[3]
        phone_radio = get_data[4]
        rx_rate = get_data[5]
        tx_rate = get_data[6]

        report = lf_report(_output_html="we-can-wifi-capacity.html", _output_pdf="we-can-wifi-capacity.pdf",
                           _results_dir_name="we-can wifi-capacity result")

        report_time_file = report.get_path_date_time()
        shutil.copy(file_derectory + "/chart-0-print.png", report_time_file)
        shutil.copy(file_derectory + "/kpi-chart-1-print.png", report_time_file)
        shutil.copy(file_derectory + "/chart-2-print.png", report_time_file)
        shutil.copy(file_derectory + "/chart-3-print.png", report_time_file)
        shutil.copy(file_derectory + "/chart-4-print.png", report_time_file)
        shutil.copy(file_derectory + "/chart-5-print.png", report_time_file)
        shutil.copy(file_derectory + "/chart-6-print.png", report_time_file)
        shutil.copy(file_derectory + "/chart-7-print.png", report_time_file)
        shutil.copy(file_derectory + "/chart-8-print.png", report_time_file)
        shutil.copy(file_derectory + "/chart-9-print.png", report_time_file)
        # print("Report Date time: ", report_time_file)

        report_path = report.get_path()
        report_path_date_time = report.get_path_date_time()

        print(report_path_date_time)
        print("path: {}".format(report_path))
        print("path_date_time: {}".format(report_path_date_time))

        report.set_title("WE-CAN Wi-Fi Capacity test for Real Clients")
        report.build_banner()

        report.start_content_div()
        report.set_text(
            "<h3>Objective:" + "<h5>The WE-CAN wifi-capacity Test is designed to measure the performance of an Access "
                               "Point when handling different types of real clients. The test allows the user to "
                               "increase the number of stations in user defined steps for each test iteration and "
                               "measure the per station and the overall throughput for each trial. Along with throughput"
                               "other measurements made are client connection times, Fairness, % packet loss, DHCP "
                               "times and more. The expected behavior is for the AP to be able to handle several "
                               "stations (within the limitations of the AP specs) and make sure all stations get a fair"
                               " amount of airtime both in the upstream and downstream. An AP that scales well will not"
                               " show a significant over-all throughput decrease as more stations are added. ")
        report.build_date_time()
        report.build_text()

        # report.start_content_div()
        # report.set_text("<h3>Phone Details:" + "<h4>All the Phone Details are provided in the table below.")
        # report.build_text()

        data = {
            "Resource ID": resource_id,
            "Phone Name": phone_name,
            "MAC Address": mac_address,
            "User Name": user_name,
            "Phone Radio": phone_radio,
            "Rx link Rate (Mbps) ": rx_rate,
            "Tx link Rate (Mbps)": tx_rate,
        }
        phone_details = pd.DataFrame(data)

        report.start_content_div()
        report.set_table_title("<h3>Phone Details")
        report.build_table_title()
        report.set_table_dataframe(phone_details)
        report.build_table()
        report.set_text("<h5> The above table shows a list of all the Real clients which are connected to LANForge "
                        "server in the tabular format which also show the various details of the real-client (phones) "
                        "such as phone name, MAC address, Username, Phone Radio, Rx link rate, Tx link rate and "
                        "Resource id.")
        report.build_text()

        report.start_content_div()
        report.build_chart_title("Real Time Chart")
        report.build_chart("chart-0-print.png")
        report.set_text("<h5> Total Megabits-per-second transferred. This only counts the protocol payload, so it will"
                        " not count the Ethernet, IP, UDP, TCP or other header overhead. A well behaving system will "
                        "show about the same rate as stations increase. If the rate decreases significantly as stations"
                        " increase, then it is not scaling we")
        report.build_text()

        report.save_bar_chart("Real Client", "Rx/Tx (Mbps)", rx_tx_df, "Upload and Download")
        report.start_content_div()
        report.build_chart_title("Upload/Download (Rx VS Tx) Chart")
        report.build_chart("Upload and Download.png")
        report.set_text("<h5> The Total average Upload and Download rate for TCP and UDP traffic for each phone along"
                        " with Name.")
        report.build_text()

        report.save_bar_chart("Band of Real Client", "Rx/Tx (Mbps)", Band_2G_5G_df, "2G-5G")
        report.start_content_div()
        report.build_chart_title("2G Phones vs 5G Phones")
        report.build_chart("2G-5G.png")
        report.set_text("<h5> The Total average Upload and Download rate for TCP and UDP traffic classified with phone"
                        " radios. The 2G represents that the phone only have 2G radios and 2G/5G the represents that "
                        "the phone have both 2G and 5G radios. ")
        report.build_text()

        report.save_bar_chart("Real Client", "Rx/Tx (Mbps)", link_rate_df, "link_rate")
        report.start_content_div()
        report.build_chart_title("Link Rate Chart")
        report.build_chart("link_rate.png")
        report.set_text("<h5> This chart shows that the total Link rate we got during running the script for TCP and "
                        "UDP traffic versus the real traffic we got for each phone in Mbps.")
        report.build_text()

        report.save_bar_chart("Real client Username", "Rx/Tx (Mbps)", user_name_df, "user_name")
        report.start_content_div()
        report.build_chart_title("Username based phone details")
        report.build_chart("user_name.png")
        report.set_text("<h5> The Total average Upload and Download rate for TCP and UDP traffic classified with "
                        " username. This chart shows udp download, udp upload, udp average, tcp upload, tcp download "
                        "and tcp average in Mbps.")
        report.build_text()



        report.start_content_div()
        report.build_chart_title("Real Time Chart")
        report.build_chart("kpi-chart-1-print.png")
        report.set_text("<h5> Protocol-Data-Units received. For TCP, this does not mean much, but for UDP connections, "
                        "this correlates to packet size. If the PDU size is larger than what fits into a single frame, "
                        "then the network stack will segment it accordingly. A well behaving system will show about the"
                        " same rate as stations increase. If the rate decreases significantly as stations increase, "
                        "then it is not scaling well. ")
        report.build_text()

        report.start_content_div()
        report.build_chart_title("Total Mbps Received vs Number of Stations Active")
        report.build_chart("chart-2-print.png")
        report.set_text("<h5> Station disconnect stats. These will be only for the last iteration. If the 'Clear Reset"
                        " Counters' option is selected, the stats are cleared after the initial association. Any "
                        "re-connects reported indicate a potential stability issue. Can be used for long-term stability"
                        " testing in cases where you bring up all stations in one iteration and then run the test for a"
                        " longer duration. ")
        report.build_text()

        report.start_content_div()
        report.build_chart_title("Port Reset Totals")
        report.build_chart("chart-3-print.png")
        report.set_text("<h5> Station connect time is calculated from the initial Authenticate message through the "
                        "completion of Open or RSN association/authentication. ")
        report.build_text()


        report.start_content_div()
        report.build_chart_title("Station Connect Times")
        report.build_chart("chart-4-print.png")
        # report.set_text("<h5> Total Megabits-per-second transferred. This only counts the protocol payload, so it will"
        #                 " not count the Ethernet, IP, UDP, TCP or other header overhead. A well behaving system will "
        #                 "show about the same rate as stations increase. If the rate decreases significantly as stations"
        #                 " increase, then it is not scaling we")
        # report.build_text()

        report.start_content_div()
        report.build_chart_title("Data for Combined Mbps, 60 second running average")
        report.build_chart("chart-5-print.png")
        # report.set_text("<h5> Total Megabits-per-second transferred. This only counts the protocol payload, so it will"
        #                 " not count the Ethernet, IP, UDP, TCP or other header overhead. A well behaving system will "
        #                 "show about the same rate as stations increase. If the rate decreases significantly as stations"
        #                 " increase, then it is not scaling we")
        # report.build_text()

        report.start_content_div()
        report.build_chart_title("Combined Received Megabytes, for entire 1 m run")
        report.build_chart("chart-6-print.png")
        report.set_text("<h5> This graph shows fairness. On a fair system, each station should get about the same "
                        "throughput.In the download direction, it is mostly the device-under-test that is responsible "
                        "for this behavior, but in the upload direction, LANforge itself would be the source of most "
                        "fairness issues unless the device-under-test takes specific actions to ensure fairness")
        report.build_text()

        report.start_content_div()
        report.build_chart_title("Station Maximums")
        report.build_chart("chart-7-print.png")
        # report.set_text("<h5> RF stats give an indication of how well how congested is the RF environment. Channel "
        #                 "activity is what the wifi radio reports as the busy-time for the RF environment. It is "
        #                 "expected that this be near 100% when LANforge is running at max speed, but at lower speeds, "
        #                 "this should be a lower percentage unless the RF environment is busy with other systems.")
        # report.build_text()

        report.start_content_div()
        report.build_chart_title("RF Stats for Stations")
        report.build_chart("chart-8-print.png")
        report.set_text("<h5> RF stats give an indication of how well how congested is the RF environment. Channel "
                        "activity is what the wifi radio reports as the busy-time for the RF environment. It is "
                        "expected that this be near 100% when LANforge is running at max speed, but at lower speeds, "
                        "this should be a lower percentage unless the RF environment is busy with other systems.")
        report.build_text()

        report.start_content_div()
        report.build_chart_title("Link Rate for Stations")
        report.build_chart("chart-9-print.png")
        report.set_text("<h5> Link rate stats give an indication of how well the rate-control is working. For "
                        "rate-control, the 'RX' link rate corresponds to what the device-under-test is transmitting. "
                        "If all of the stations are on the same radio, then the TX and RX encoding rates should be "
                        "similar for all stations. If there is a definite pattern where some stations do not get good "
                        "RX rate, then probably the device-under-test has rate-control problems. The TX rate is what "
                        "LANforge is transmitting at.")
        report.build_text()

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
                                ssh_port=22,
                                lf_user=args.lf_user,
                                lf_password=args.lf_password,
                                upstream=args.upstream,
                                batch_size=args.batch_size,
                                protocol=args.protocol,
                                duration=args.duration,
                                pull_report=True,
                                download_rate=args.download_rate,
                                upload_rate=args.upload_rate,
                                influx_host=args.mgr,
                                influx_port=8086,
                                local_lf_report_dir=args.local_lf_report_dir,
                                )
    # WFC_Test.setup()
    # WFC_Test.run()
    wifi_capacity = we_can_wifi_capacity(host=args.mgr, port=args.port, protocol=args.protocol)
    wifi_capacity.get_data()
    # WFC_Test.check_influx_kpi(args)


if __name__ == "__main__":
    main()
