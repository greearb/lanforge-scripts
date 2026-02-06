from lf_base_robo import RobotClass
import argparse
import csv
from lf_base_robo import RobotClass
import time
import logging
import sys
from datetime import datetime, timedelta
import importlib
import os
import lf_report
import shutil
import json
import pandas as pd
from lf_interop_throughput import Throughput
import threading
from lf_report import lf_report
from lf_graph import lf_bar_graph
from collections import Counter
througput_test=importlib.import_module("py-scripts.lf_interop_throughput")
realm = importlib.import_module("py-json.realm")
logger = logging.getLogger(__name__)



class ROAMThroughput(RobotClass):
    def __init__(self, robo_ip="", coordinates="", total_cycles=-1,
                 ssid="", security="", mgr_ip="", port="8080",
                 duration=60, test_name="", upstream_port="eth1",
                 upload="2560", download="2560", traffic_type=None, packet_size="-1", device_list=None, dowebgui=False, result_dir=None, bssids=""):
        super().__init__()
        self.robo_ip = robo_ip
        self.coordinates = coordinates
        self.total_cycles = total_cycles
        self.mgr_ip = mgr_ip
        self.port = port

        self.coordinates_list = [c for c in self.coordinates.split(",") if c]
        self.create_waypointlist()
        self.roam_count = 0
        self.created_cx_lists_keys = []
        self.download = download
        self.upload = upload
        self.traffic_type = traffic_type
        self.upstream_port = upstream_port
        self.ssid = ssid
        self.security = security
        self.packet_size = packet_size
        self.throughput_tester = None
        self.stop_event = threading.Event()
        self.roam_robo_thread = None
        self.roam_throughput_thread = None
        self.device_list = device_list if device_list else []
        self.result_dir = result_dir
        self.report = None
        self.folder_path = None
        self.dowebgui = dowebgui
        self.test_name = test_name
        self.bssids = [b.strip() for b in bssids.split(",")] if bssids else []
        # open("robot_x_y.csv", "w").write("timestamp,x,y\n")
        self.perform_throughput_test()
        logger.info("Moving robot to first coordinate to start the test")
        self.move_to_coordinate(self.coordinates_list[0])
        self.perform_roam_robot()

    def get_bandsteering_stats(self, report=None, df=None, device_name=None):
        """
        Retrieves and adds bandsteering statistics to the report.
        """

        # Get all BSSID columns
        bssid_cols = df.columns[df.columns.str.startswith('BSSID')]
        channel_cols = [c for c in df.columns if c.startswith("Channel")]
        bssid_to_channel = {
            bssid_col: next(
                ch for ch in channel_cols
                if ch.replace("Channel", "").strip() ==
                bssid_col.replace("BSSID", "").strip()
            )
            for bssid_col in bssid_cols
        }
        for col in bssid_cols:
            channel_col = bssid_to_channel[col]
            # Detect BSSID changes
            mask = df[col] != df[col].shift()
            filtered_df = df.loc[mask]
            if self.bssids:
                filtered_df = df.loc[mask & df[col].isin(self.bssids)]
            bssid_list = filtered_df[col].tolist()
            channel_list = filtered_df[channel_col].tolist()
            timestamp_list = filtered_df['Timestamp'].tolist()
            from_coordinate_list = filtered_df['From Coordinate'].tolist()
            to_coordinate_list = filtered_df['To Coordinate'].tolist()
            # Count BSSID occurrences at change points
            bssid_counts = Counter(bssid_list)

            # X and Y axis (preserve missing BSSIDs with 0)
            x_axis = list(bssid_counts.keys())
            y_axis = [[float(i)] for i in list(bssid_counts.values())]
            print("BSSID COUNTS:", x_axis,bssid_counts)
            if(len(self.bssids)>0):
                x_axis = self.bssids
                y_axis = [[float(bssid_counts.get(bssid, 0))] for bssid in self.bssids]
            print("AFTER BSSID COUNTS:", x_axis,y_axis)

            # Build graph objective
            report.set_obj_html(
                _obj_title=f"BSSID Change Count Of The Client {device_name}",
                _obj=" "
            )
            report.build_objective()

            # Create bar graph
            graph = lf_bar_graph(
                _data_set=y_axis,
                _xaxis_name="BSSID",
                _yaxis_name="Number of Changes",
                _xaxis_categories=[""],
                _xaxis_label=x_axis,
                _graph_image_name=f"bssid_change_count_{device_name}_{col}",
                _label=x_axis,
                _xaxis_step=1,
                _graph_title=f"BSSID change count – {device_name}",
                _title_size=16,
                _color_edge='black',
                _bar_width=0.15,
                _figsize=(18, 6),
                _legend_loc="best",
                _legend_box=(1.0, 1.0),
                _dpi=96,
                _show_bar_value=True,
                _enable_csv=True,
                _color=['orange', 'lightcoral', 'steelblue', 'lightgrey'],
                _color_name=['orange', 'lightcoral', 'steelblue', 'lightgrey'],
            )

            # Build graph and export
            graph_png = graph.build_bar_graph()
            report.set_graph_image(graph_png)
            report.move_graph_image()
            report.set_csv_filename(graph_png)
            report.move_csv_file()
            report.build_graph()

            report.set_obj_html(
                _obj_title=f"Band Steering Results for {device_name}",
                _obj=" "
            )
            report.build_objective()

            # Build table
            table_df = pd.DataFrame({
                "Timestamp": timestamp_list,
                "BSSID": bssid_list,
                "Channel": channel_list,
                "From Coordinate": from_coordinate_list,
                "To Coordinate": to_coordinate_list
            })

            report.set_table_dataframe(table_df)
            report.build_table()
 
    def generate_report(self):
        self.report.set_title("Automated Band Steering Test")
        self.report.build_banner()
        self.report.set_obj_html(_obj_title="Objective",
                    _obj="The Automated Band Steering Test uses selected real client devices mounted on CanBEE to evaluate band-steering behavior " 
                    " during movement. The test continuously monitors each device’s connected BSSID while the robot moves through user-defined" 
                    " points. Whenever a BSSID change occurs, the system records the exact robot position and path segment between which the"
                    " change happened, enabling clear identification of where band-steering decisions were made.")
        self.report.build_objective()
        self.report.set_obj_html(_obj_title="Input Parameters",
                            _obj="The below tables provides the input parameters for the test")
        self.report.build_objective()
        test_setup_info = {
                    "Test name": self.testname,
                    "Robot IP": self.robo_ip,
                    "No of Devices": len(self.throughput_tester.input_devices_list),
                    "Total Cycles": self.total_cycles,
                }
        self.report.test_setup_table(test_setup_data=test_setup_info, value="Test Configuration")
        usernames = []
        for j in range(len(self.throughput_tester.real_client_list)):
            usernames.append(self.throughput_tester.real_client_list[j].split(" ")[-1])
        for i in range(len(self.throughput_tester.input_devices_list)):
            file_path = os.path.join(self.report_folder_path, f"{self.throughput_tester.input_devices_list[i]}.csv")
            df = pd.read_csv(file_path)
            self.get_bandsteering_stats(report=self.report, df=df,device_name=usernames[i])
            self.report.set_obj_html(_obj_title=f"Band Steering Stats: {usernames[i]}({self.throughput_tester.input_devices_list[i]})",
                    _obj="")
            self.report.build_objective()
            dataframe = {
                "Sequence No.": df["Sequence No."],
                "MAC":df["MAC"],
                "Channel":df["Channel"],
                "BSSID":df["BSSID"],
                "Signal":df["Signal"],
                "From Coordinate":df["From Coordinate"],
                "To Coordinate":df["To Coordinate"],
                "Timestamp":df["Timestamp"]
            }
            self.report.set_table_dataframe(pd.DataFrame(dataframe))
            self.report.build_table()
            

        self.report.build_footer()
        self.report.write_html()
        self.report.write_pdf(_orientation="Landscape")
    
    def create_testname_folder(self):
        self.report = lf_report(
            _output_pdf="bandsteering.pdf",
            _output_html="bandsteering.html",
            _path=self.result_dir,
            _results_dir_name="Bandsteering_Test_Report"
        )

        # Use the actual generated report directory
        report_path = self.report.get_path_date_time()
        if self.dowebgui:
            report_path = self.result_dir
        else:
            os.makedirs(report_path, exist_ok=True)
        self.report_folder_path = report_path
            

        for i in self.throughput_tester.input_devices_list:
            file_path = os.path.join(report_path, f"{i}.csv")
            with open(file_path, "w") as f:
                f.write("Sequence No.,Timestamp,MAC,Channel,BSSID,Signal,Robot x,Robot y,From Coordinate,To Coordinate\n")

    def perform_roam_robot(self):
        try:
            self.create_testname_folder()
            self.roam_count = 0
            first_coordinate = self.coordinates_list[0]
            test_stopped_by_user = False


            logger.info("Starting roam cycle %s", self.roam_count + 1)
            coordinate_list_with_robo = [self.coordinates_list[(1 + i) % len(self.coordinates_list)] for i in range(int(self.total_cycles) * len(self.coordinates_list))]
            for coordinate in coordinate_list_with_robo:
                pause, stopped, all_df = self.wait_for_battery(monitor_function=self.monitor_ap_bssid)
                # print("Battery pause:", pause, "stopped:", stopped)
                if stopped:
                    break
                # if pause:
                #     self.throughput_tester.start_specific(self.created_cx_lists_keys)
                matched, abort =self.move_to_coordinate(coordinate, monitor_function=self.monitor_ap_bssid)
                if abort:
                    logger.info("Testing stopped by user")
                    test_stopped_by_user = True
                    break
            # pause, stopped = self.wait_for_battery()
            # if pause:
            #     self.throughput_tester.start_specific(self.created_cx_lists_keys)
            # matched, abort = self.move_to_coordinate(first_coordinate, monitor_function=self.monitor_ap_bssid)


            self.roam_count += 1
            # logger.info("Completed roam cycle %s", self.roam_count)
            self.monitor_ap_bssid(test_status="STOPPED")

        except KeyboardInterrupt:
            logger.info("Test interrupted by user")
        finally:
            self.generate_report()
            logger.info("Test completed")

    def perform_throughput_test(self):
        self.runtime_dir = self.result_dir
        self.ip = self.mgr_ip
        self.testname = self.test_name
        try:
            if self.download and self.upload:
                loads = {'upload': str(self.upload).split(","), 'download': str(self.download).split(",")}
                loads_data = loads["download"]
            elif self.download:
                loads = {'upload': [], 'download': str(self.download).split(",")}
                for _ in range(len(self.download)):
                    loads['upload'].append(2560)
                loads_data = loads["download"]
            else:
                if self.upload:
                    loads = {'upload': str(self.upload).split(","), 'download': []}
                    for _ in range(len(self.upload)):
                        loads['download'].append(2560)
                    loads_data = loads["upload"]
            for index in range(len(loads_data)):
                self.throughput_tester = througput_test.Throughput(
                    host=self.mgr_ip,
                    ip=self.mgr_ip,
                    port=self.port,
                    ssid=self.ssid,
                    security=self.security,
                    upstream=self.upstream_port,
                    tos="Best_Efforts",
                    traffic_type=self.traffic_type,
                    side_a_min_rate=int(loads['upload'][index]),
                    side_b_min_rate=int(loads['download'][index]),
                    side_a_min_pdu=int(self.packet_size),
                    side_b_min_pdu=int(self.packet_size),
                    incremental_capacity=[],
                    device_list= self.device_list
                )
                self.throughput_tester.os_type()
                self.throughput_tester.phantom_check()
                # self.throughput_tester.check_incremental_list()
                # self.throughput_tester.build()
                # time.sleep(10)
                # self.roam_robo_thread.start()
                # to_run_cxs, to_run_cxs_len, self.created_cx_lists_keys, incremental_capacity_list = self.throughput_tester.get_incremental_capacity_list()
                # print("Starting Throughput Test",created_cx_lists_keys)
                # self.throughput_tester.start_specific(self.created_cx_lists_keys)
                # time.sleep(10)
                # open("roam_throughput.csv","w").write("Timestamp,MAC,Channel,BSSID,Signal,Download (Mbps),Upload (Mbps)\n")


        except KeyboardInterrupt:
            logger.info("Test interrupted by user")
        finally:
            logger.info("Test completed")
    
    def monitor_throughput(self):
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            port_manager_data_lists = [self.throughput_tester.mac_id_list]
            port_manager_data_lists.extend(
                self.get_signal_and_channel_data(
                    self.throughput_tester.input_devices_list
                )
            )

            layer3_data = self.throughput_tester.get_layer3_endp_data()

            device_dict = {}

            for device in self.throughput_tester.input_devices_list:
                device_dict[device] = [timestamp]

            for i, device in enumerate(self.throughput_tester.input_devices_list):
                for extra in port_manager_data_lists[:4]:
                    device_dict[device].append(extra[i])

            for i, device in enumerate(self.throughput_tester.input_devices_list):
                v = layer3_data[i]
                data = v[:2]
                if v[4] != 'Run':
                    data.extend([0, 0])
                device_dict[device].extend(data)

            # for _, data in device_dict.items():
            #     open("roam_throughput.csv", "a").write(
            #         ",".join(map(str, data)) + "\n"
            #     )
            return device_dict  

        except Exception as e:
            logger.error("Throughput error: %s", e)

    def monitor_ap_bssid(self, test_status="Running"):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            port_manager_data_lists = [self.throughput_tester.mac_id_list]
            channel_list, bssid_list, signal_list, mode_list, link_speed_list, rx_rate_list = self.get_signal_and_channel_data(
                    self.throughput_tester.input_devices_list
                )
            port_manager_data_lists.extend([channel_list, bssid_list, signal_list, mode_list, link_speed_list, rx_rate_list])
            device_dict = {}
            for device in self.throughput_tester.input_devices_list:
                device_dict[device] = [timestamp]

            for i, device in enumerate(self.throughput_tester.input_devices_list):
                for extra in port_manager_data_lists[:4]:
                    device_dict[device].append(extra[i])

            file_path = os.path.join(self.report_folder_path, "bandsteering.csv")


            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)

                writer.writerow(["timestamp", "client", "bssid", "status"])

                for (device, data), bssid in zip(device_dict.items(), bssid_list):
                    row = [
                        data[0],       
                        device,         
                        bssid,          
                        test_status       
                    ]
                    writer.writerow(row)

            for device, data in device_dict.items():
                robot_x, robot_y, from_coordinate, to_coordinate = self.get_robot_pose()
                data.extend([robot_x, robot_y, from_coordinate, to_coordinate])
                file_path = os.path.join(self.report_folder_path, f"{device}.csv")
                
                last_bssid = None

                with open(file_path, "r") as f:
                    lines = f.readlines()

                    # if len(lines) > 1: 
                    last_line = lines[-1]
                    last_bssid = last_line.strip().split(",")[4] 
                    index_number = len(lines) 
                    # else:
                    #     index_number = 1
   
                if last_bssid is not None and last_bssid == data[3]:
                    continue
                data.insert(0, index_number)

                if self.bssids and data[4]!="BSSID" and data[4] not in self.bssids:
                    continue
                with open(file_path, "a") as f:
                    f.write(",".join(map(str, data)) + "\n")
            return device_dict
        
        except Exception as e:
            logger.error("Throughput error: %s", e)

    def get_signal_and_channel_data(self, station_names):
        """
        Retrieves signal strength, channel, mode, and link speed data for the specified stations.

        """
        signal_list, channel_list, mode_list, link_speed_list, rx_rate_list, bssid_list = [], [], [], [], [], []
        interfaces_dict = dict()
        try:
            port_data = self.throughput_tester.json_get('/ports/all/')['interfaces']
        except KeyError:
            logger.error("Error: 'interfaces' key not found in port data")
            exit(1)

        for port in port_data:
            interfaces_dict.update(port)
        for sta in station_names:
            if sta in interfaces_dict:
                if "dBm" in interfaces_dict[sta]['signal']:
                    signal_list.append(interfaces_dict[sta]['signal'].split(" ")[0])
                else:
                    signal_list.append(interfaces_dict[sta]['signal'])
            else:
                signal_list.append('-')
        for sta in station_names:
            if sta in interfaces_dict:
                channel_list.append(interfaces_dict[sta]['channel'])
            else:
                channel_list.append('-')
        for sta in station_names:
            if sta in interfaces_dict:
                mode_list.append(interfaces_dict[sta]['mode'])
            else:
                mode_list.append('-')
        for sta in station_names:
            if sta in interfaces_dict:
                link_speed_list.append(interfaces_dict[sta]['tx-rate'])
            else:
                link_speed_list.append('-')
        for sta in station_names:
            if sta in interfaces_dict:
                rx_rate_list.append(interfaces_dict[sta]['rx-rate'])
            else:
                rx_rate_list.append('-')
        for sta in station_names:
            if sta in interfaces_dict:
                bssid_list.append(interfaces_dict[sta]['ap'])
            else:
                bssid_list.append('-')
        return channel_list, bssid_list, signal_list, mode_list, link_speed_list, rx_rate_list

def main():
    base_parser = argparse.ArgumentParser(add_help=True)

    base_parser.add_argument(
        '--help_summary',
        action="store_true",
        help='Show summary of what this script does'
    )
    parser = argparse.ArgumentParser(
        prog='lf_bandsteering.py',
        description='Control a Roam robot using lf_base_robo functionalities.'
    )
    early_args, remaining_args = base_parser.parse_known_args()
    help_summary = """\

    EXAMPLE CLI: python3 lf_bandsteering.py --robot_ip 192.168.200.169 --coordinates 3,4 --mgr_ip 192.168.207.78 --port 8080 --total_cycles 3
    """
    if early_args.help_summary:
        print(help_summary)
        sys.exit(0)

    # Robot parameters
    parser.add_argument('--robot_ip', type=str, help='IP address of the Roam robot')
    parser.add_argument('--coordinates', type=str, default='', help="The coordinate contains list of coordinates to be ")
    parser.add_argument('--duration', type=int, default=60, help='Ping duration in seconds')
    


    parser.add_argument('--total_cycles', type=int, default=-1, help='Total number of cycles to perform')
    parser.add_argument('--ssid', type=str, help='SSID used for the test')
    parser.add_argument('--security', type=str, help='Security type used for the test')
    parser.add_argument('--test_name', type=str, help='Name of the test', default="")

    # Throughput parameters
    parser.add_argument('--mgr_ip', type=str, default='',  help='Lanforge IP address')
    parser.add_argument('--port', type=str, default=8080, help='Manager port')
    parser.add_argument('--upstream_port', '-u', default='eth1', help='non-station port that generates traffic: <resource>.<port>, e.g: 1.eth1')
    parser.add_argument('--upload', help='--upload traffic load per connection (upload rate)', default='2560')
    parser.add_argument('--download', help='--download traffic load per connection (download rate)', default='2560')
    parser.add_argument('--traffic_type', help='Select the Traffic Type [lf_udp, lf_tcp]', required=False, default='lf_tcp')
    parser.add_argument('--packet_size', help='Packet size for throughput test', default='-1')
    parser.add_argument('--device_list', help="Enter the devices on which the test should be run", default=[])
    parser.add_argument('--dowebgui', help="If true will execute script for webgui", action='store_true')
    parser.add_argument('--result_dir', help='Specify the result dir to store the runtime logs', default='')
    parser.add_argument('--bssids', type=str, help='Comma separated list of BSSIDs to be used for the test', default="")


    args = parser.parse_args(remaining_args)

    ROAMThroughput(
        robo_ip=args.robot_ip,
        coordinates=args.coordinates,
        total_cycles=args.total_cycles,
        ssid=args.ssid,
        security=args.security,
        mgr_ip=args.mgr_ip,
        port=args.port,
        duration=args.duration,
        test_name=args.test_name,
        upstream_port=args.upstream_port,
        upload=args.upload,
        download=args.download,
        traffic_type=args.traffic_type,
        device_list=args.device_list,
        dowebgui=args.dowebgui,
        result_dir=args.result_dir,
        bssids=args.bssids
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    main()