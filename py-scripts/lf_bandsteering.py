#!/usr/bin/env python3
"""
    NAME: lf_bandsteering.py

    PURPOSE: The Automated Band Steering Test uses selected real client devices mounted on CanBEE to evaluate band-steering behavior
            during movement. The test continuously monitors each device’s connected BSSID while the robot moves through user-defined
            points. Whenever a BSSID change occurs, the system records the exact robot position and path segment between which the
            change happened, enabling clear identification of where band-steering decisions were made.

    EXAMPLE-1:
    Command Line Interface to run bandsteering test
    python3 lf_bandsteering.py --robot_ip 192.168.204.76 --coordinates 3,4 --mgr_ip 192.168.207.78 --port 8080 --total_cycles 1

    EXAMPLE-2:
    Command Line Interface to run bandsteering test with specified BSSID's
    python3 lf_bandsteering.py --robot_ip 192.168.204.76 --coordinates 3,4 --mgr_ip 192.168.207.78 --port 8080 --total_cycles 1 --bssids 94:A6:7E:74:26:22, 94:A6:7E:74:26:31

    SCRIPT_CLASSIFICATION :  Test

    SCRIPT_CATEGORIES:   Performance,  Functional, Report Generation

    NOTES:
    1.Use './lf_bandsteering.py --help' to see command line usage and options
    2.After passing cli, a list will be displayed on terminal which contains available resources to run test.
    The following sentence will be displayed
    Enter the desired resources to run the test:
    Please enter the port numbers seperated by commas ','.
    Example:
    Enter the desired resources to run the test:1.10,1.11,1.12,1.13,1.202,1.203,1.303

    STATUS: BETA RELEASE

    VERIFIED_ON:
    Working date - 09/04/2026
    Build version - 5.5.2
    kernel version - 6.15.6+

    License: Free to distribute and modify. LANforge systems must be licensed.
    Copyright (C) 2020-2026 Candela Technologies Inc.

"""
from lf_base_robo import RobotClass
import argparse
import csv
import logging
import sys
from datetime import datetime
import importlib
import os
import pandas as pd
import threading
from lf_report import lf_report
from lf_graph import lf_bar_graph
from collections import Counter

througput_test = importlib.import_module("py-scripts.lf_interop_throughput")
realm = importlib.import_module("py-json.realm")
logger = logging.getLogger(__name__)


class BandSteeringTest(RobotClass):
    def __init__(self, robo_ip="", coordinates="", total_cycles=-1,
                 ssid="", security="", mgr_ip="", port="8080",
                 duration=60, test_name="", upstream_port="eth1",
                 device_list=None, dowebgui=False, result_dir=None, bssids="", duration_to_skip="1"):
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
        self.upstream_port = upstream_port
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
        self.time_to_reach = int(duration_to_skip) * 60

    def get_bandsteering_stats(self, report=None, df=None, device_name=None):
        """
        Retrieves and adds bandsteering statistics to the report.
        Args:
            report (lf_report): The report object to which the statistics will be added.
            df (DataFrame): The DataFrame containing the bandsteering data for a specific device.
            device_name (str): The name of the device for which the statistics are being generated.
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
            if (len(self.bssids) > 0):
                x_axis = self.bssids
                y_axis = [[float(bssid_counts.get(bssid, 0))] for bssid in self.bssids]

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
        """ Generates the HTML and PDF report for the bandsteering test. """
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
            # Get bandsteering stats and build the corresponding section in the report for each device
            self.get_bandsteering_stats(report=self.report, df=df, device_name=usernames[i])
            self.report.set_obj_html(_obj_title=f"Band Steering Stats: {usernames[i]}({self.throughput_tester.input_devices_list[i]})",
                                     _obj="")
            self.report.build_objective()
            # Build a table with the relevant columns from the DataFrame and add it to the report for each device
            dataframe = {
                "Sequence No.": df["Sequence No."],
                "MAC": df["MAC"],
                "Channel": df["Channel"],
                "BSSID": df["BSSID"],
                "Signal": df["Signal"],
                "From Coordinate": df["From Coordinate"],
                "To Coordinate": df["To Coordinate"],
                "Timestamp": df["Timestamp"]
            }
            self.report.set_table_dataframe(pd.DataFrame(dataframe))
            self.report.build_table()

        self.report.build_footer()
        self.report.write_html()
        self.report.write_pdf(_orientation="Landscape")

    def create_testname_folder(self):
        """ Creates a folder for the test results based on the test name and current timestamp. """
        self.report = lf_report(
            _output_pdf="bandsteering.pdf",
            _output_html="bandsteering.html",
            _path=self.result_dir,
            _results_dir_name="Bandsteering_Test_Report"
        )

        # Use the actual generated report directory
        report_path = self.report.get_path_date_time()
        # If dowebgui is True, use the provided result_dir as the report path. Otherwise, create a new directory for the report.
        if self.dowebgui:
            report_path = self.result_dir
        else:
            os.makedirs(report_path, exist_ok=True)
        self.report_folder_path = report_path
        # Create individual CSV files for each device to store the bandsteering data, and write the header row to each file.
        for i in self.throughput_tester.input_devices_list:
            file_path = os.path.join(report_path, f"{i}.csv")
            with open(file_path, "w") as f:
                f.write("Sequence No.,Timestamp,MAC,Channel,BSSID,Signal,Robot x,Robot y,From Coordinate,To Coordinate\n")

    def perform_robot_movement(self):
        """
         Performs the robot movement through the specified coordinates and monitors the AP BSSID for each device during the movement.

        """
        try:
            # Create a folder for storing test results/logs
            self.create_testname_folder()
            # Initialize roam count
            self.roam_count = 0
            # Flag to check if user stopped the test manually
            self.coordinate_list = self.coordinates_list
            # Get coordinates based on number of cycles
            coordinate_list_with_robo = self.get_coordinates_list()
            curr_cycle = 1
            logger.info("Starting cycle %s", curr_cycle)
            # Loop through each coordinate
            for coordinate in coordinate_list_with_robo:
                # Wait/check battery before moving
                pause, stopped, all_df = self.wait_for_battery(monitor_function=self.monitor_ap_bssid)
                if stopped:
                    break
                # Move robot to the current coordinate
                matched, abort = self.move_to_coordinate(coordinate, monitor_function=self.monitor_ap_bssid)
                # If test is aborted by user, break the loop and stop the test
                if abort:
                    logger.info("Testing stopped by user")
                    break
                # Skip the current coordinate if it fails to reach the current coordinate
                if not matched:
                    continue
                if coordinate == self.coordinates_list[0]:
                    curr_cycle += 1
                    # Check if all cycles are completed
                    if curr_cycle > self.total_cycles:
                        logger.info("Completed all {} cycles".format(self.total_cycles))
                    else:
                        logger.info("current cycle {}".format(curr_cycle))

            self.roam_count += 1
            # Stop monitoring once movement is done
            self.monitor_ap_bssid(test_status="STOPPED")

        except KeyboardInterrupt:
            logger.info("Test interrupted by user")
        finally:
            # Always generate report at the end
            self.generate_report()
            logger.info("Test completed")

    def check_devices_status(self):
        """
        Checks the status of the devices before starting the test.

        """
        self.runtime_dir = self.result_dir
        self.ip = self.mgr_ip
        self.testname = self.test_name
        try:
            self.throughput_tester = througput_test.Throughput(
                host=self.mgr_ip,
                port=self.port,
                upstream=self.upstream_port,
                tos="Best_Efforts",
                incremental_capacity=[],
                device_list=self.device_list
            )
            self.throughput_tester.os_type()
            self.throughput_tester.phantom_check()

        except KeyboardInterrupt:
            logger.info("Test interrupted by user")
        finally:
            logger.info("Test completed")

    def monitor_ap_bssid(self, test_status="Running"):
        """
        Monitors the AP BSSID for each device and logs the data to CSV files.
        Args:
            test_status (str): The current status of the test, used for logging purposes.
        Returns:
            device_dict (dict): A dictionary containing the collected data for each device.
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            port_manager_data_lists = [self.throughput_tester.mac_id_list]
            # Get signal strength, channel, mode, link speed, RX rate, and BSSID data
            # for the specified devices and store them in separate lists.
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
                # Get the robot's current position and the coordinates between which it is moving, and extend the data list with this information.
                robot_x, robot_y, from_coordinate, to_coordinate = self.get_robot_pose()
                data.extend([robot_x, robot_y, from_coordinate, to_coordinate])
                file_path = os.path.join(self.report_folder_path, f"{device}.csv")
                last_bssid = None

                # Reading the last line of the corresponding CSV file for the device to check if the BSSID has changed since the last entry.
                with open(file_path, "r") as f:
                    lines = f.readlines()

                    last_line = lines[-1]
                    last_bssid = last_line.strip().split(",")[4]
                    index_number = len(lines)
                # If bssid has not changed, skip writing to the file.
                if last_bssid is not None and last_bssid == data[3]:
                    continue
                data.insert(0, index_number)

                if self.bssids and data[4] != "BSSID" and data[4] not in self.bssids:
                    continue
                with open(file_path, "a") as f:
                    f.write(",".join(map(str, data)) + "\n")
            return device_dict

        except Exception as e:
            logger.error("Throughput error: %s", e)

    def get_signal_and_channel_data(self, station_names):
        """
        Retrieves signal strength, channel, mode, and link speed data for the specified stations.
        Args:
            station_names (list): A list of station names for which to retrieve data.
        Returns:
            Six lists containing channel, BSSID, signal strength, mode, link speed, and RX rate data for the specified stations.

        """

        # Initialize lists to store data for each station
        signal_list, channel_list, mode_list, link_speed_list, rx_rate_list, bssid_list = [], [], [], [], [], []
        interfaces_dict = dict()
        # Fetch port data from the throughput tester and organize it into a dictionary for easy access
        try:
            port_data = self.throughput_tester.json_get('/ports/all/')['interfaces']
        except KeyError:
            logger.error("Error: 'interfaces' key not found in port data")
            exit(1)
        # Update the interfaces_dict with the port data for easy lookup
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
        description="""

        NAME: lf_bandsteering.py

        PURPOSE: The Automated Band Steering Test uses selected real client devices mounted on CanBEE to evaluate band-steering behavior
                during movement. The test continuously monitors each device’s connected BSSID while the robot moves through user-defined
                points. Whenever a BSSID change occurs, the system records the exact robot position and path segment between which the
                change happened, enabling clear identification of where band-steering decisions were made.

        EXAMPLE-1:
        Command Line Interface to run bandsteering test
        python3 lf_bandsteering.py --robot_ip 192.168.204.76 --coordinates 3,4 --mgr_ip 192.168.207.78 --port 8080 --total_cycles 1

        EXAMPLE-2:
        Command Line Interface to run bandsteering test with specified BSSID's
        python3 lf_bandsteering.py --robot_ip 192.168.204.76 --coordinates 3,4 --mgr_ip 192.168.207.78 --port 8080 --total_cycles 1 --bssids 94:A6:7E:74:26:22, 94:A6:7E:74:26:31

        SCRIPT_CLASSIFICATION :  Test

        SCRIPT_CATEGORIES:   Performance,  Functional, Report Generation

        NOTES:
        1.Use './lf_bandsteering.py --help' to see command line usage and options
        2.After passing cli, a list will be displayed on terminal which contains available resources to run test.
        The following sentence will be displayed
        Enter the desired resources to run the test:
        Please enter the port numbers seperated by commas ','.
        Example:
        Enter the desired resources to run the test:1.10,1.11,1.12,1.13,1.202,1.203,1.303

        STATUS: BETA RELEASE

        VERIFIED_ON:
        Working date - 09/04/2026
        Build version - 5.5.2
        kernel version - 6.15.6+

        License: Free to distribute and modify. LANforge systems must be licensed.
        Copyright (C) 2020-2026 Candela Technologies Inc.

    """)
    early_args, remaining_args = base_parser.parse_known_args()
    help_summary = """\

    The Automated Band Steering Test uses selected real client devices mounted on CanBEE to evaluate band-steering behavior
    during movement. The test continuously monitors each device’s connected BSSID while the robot moves through user-defined
    points. Whenever a BSSID change occurs, the system records the exact robot position and path segment between which the
    change happened, enabling clear identification of where band-steering decisions were made.
    """
    if early_args.help_summary:
        print(help_summary)
        sys.exit(0)

    # Parameters
    parser.add_argument('--robot_ip', type=str, help='IP address of the Roam robot')
    parser.add_argument('--coordinates', type=str, default='', help="The coordinate contains list of coordinates to be ")
    parser.add_argument('--duration_to_skip', help='Robot wait duration in seconds at obstacle', default="1")
    parser.add_argument('--total_cycles', type=int, default=-1, help='Total number of cycles to perform')
    parser.add_argument('--test_name', type=str, help='Name of the test', default="")
    parser.add_argument('--mgr_ip', type=str, default='', help='Lanforge IP address')
    parser.add_argument('--port', type=str, default=8080, help='Manager port')
    parser.add_argument('--upstream_port', '-u', default='eth1', help='non-station port that generates traffic: <resource>.<port>, e.g: 1.eth1')
    parser.add_argument('--device_list', help="Enter the devices on which the test should be run", default=[])
    parser.add_argument('--dowebgui', help="If true will execute script for webgui", action='store_true')
    parser.add_argument('--result_dir', help='Specify the result dir to store the runtime logs', default='')
    parser.add_argument('--bssids', type=str, help='Comma-separated BSSIDs to filter, only these will be considered for steering checks.', default="")

    args = parser.parse_args(remaining_args)

    bandsteering_obj = BandSteeringTest(
        robo_ip=args.robot_ip,
        coordinates=args.coordinates,
        total_cycles=args.total_cycles,
        mgr_ip=args.mgr_ip,
        port=args.port,
        test_name=args.test_name,
        upstream_port=args.upstream_port,
        device_list=args.device_list,
        dowebgui=args.dowebgui,
        result_dir=args.result_dir,
        bssids=args.bssids,
        duration_to_skip=args.duration_to_skip
    )
    # Check the status of the devices before starting the test, and then perform the robot movement while monitoring the AP BSSID for each device.
    bandsteering_obj.check_devices_status()
    bandsteering_obj.perform_robot_movement()


if __name__ == "__main__":
    # Configure logging to include timestamps and set the log level to INFO
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    main()
