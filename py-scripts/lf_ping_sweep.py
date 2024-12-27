#!/usr/bin/env python3
# flake8: noqa
'''
NAME: lf_ping_sweep.py

PURPOSE:
        This Ping Sweep Test script is designed to discover devices within the network
        connectivity by measuring latency. It also detects issues like client unavailability time,
        and average latency, ensuring effective device communication and identifying
        connectivity problems
        Note:
            The script uses Nmap tool.
            If Namp not present in the system ,  it can be installed using the command: sudo apt-get install nmap
   
EXAMPLE:
 
        CLI Example1:
            python3 lf_ping_sweep.py -e eth1 -ip 192.168.1.1/24  --duration 10h --csv_name ping_sweep_1 --reporting_down_time_percentage 30%
            
        CLI Example2 - with data packets:
            python3 lf_ping_sweep.py -e eth1 -ip 192.168.1.1/24 --data_lengths 32 64 128 500  --duration 10m --csv_name ping_sweep_1 --reporting_down_time_percentage 50%

        CLI Example3 - with different root password:
            python3 lf_ping_sweep.py -e eth1 -ip 192.168.1.1/24 --data_lengths 32 64 1024  --duration 1h --csv_name ping_sweep_1  --admin_pass orangeunit --reporting_down_time_percentage 40%

        Note: --reporting_down_time_percentage is used to calculate the ips which were down more than given percentage of its duration (default is 30%).

'''

import argparse
import re
import sys
import os
import importlib
import time
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import subprocess
from datetime import datetime , timedelta

import csv
import pandas as pd
import logging

# lf_graph = importlib.import_module("lf_graph")
lf_report = importlib.import_module("lf_report")
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


logger = logging.getLogger(__name__)



if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)






class ping_sweep():
    def __init__(self,
                 eth_interface="eth1",
                 target_ip="192.168.1.1/24",
                 csv_file="ping_sweep",
                 admin_pass="lanforge",
                 data_lengths=None,
                 scan_duration=3600.0,
                 percentage="30%"):
        self.eth_interface = eth_interface
        self.target_ip = target_ip
        self.admin_pass = admin_pass
        self.csv_file = csv_file
        self.percentage = percentage
        self.data_lengths = data_lengths
        self.created_csv_files = []
        self.no_of_ping_sweeps = []
        self.scan_duration = scan_duration
        self.host_mac_list = []
        self.host_name_list = []
        self.executed_data_lengths = []
        self.last_sweep_ending_timestamp_list = []
        self.no_of_sweeps_per_ip = []
        self.report = lf_report.lf_report(_results_dir_name="ping_sweep", _output_html="Ping_Sweep.html",
                                          _output_pdf="Ping_Sweep.pdf", _path="")




    def run_ping(self):
        # print(type(self.data_lengths))
        cmd_output = False
        out_put_to_ptint = ""
        for data_length in self.data_lengths:
            host_status = {}
            start_time = time.time()
            timestamp_list = []
            # print(f"Admin password: {self.admin_pass}")
            logger.info("Ping sweep initiated for data-length: {}".format(data_length))

            command = f"sudo nmap -e {self.eth_interface} -data-length {data_length}  {self.target_ip}"
            csv_file = f'{self.csv_file}_{data_length}_{str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]}.csv'

            if data_length == "6":
                command = f"sudo nmap -e {self.eth_interface} {self.target_ip}"
                csv_file = f'{self.csv_file}_{str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]}.csv'
            #print(f"csv file name: {csv_file}")
            csv_file = os.path.join(self.report.path_date_time, csv_file)
            # print(csv_file,"----csv------")
            #print(f"command used: {command}")
            logger.info("command : {}".format(command))
            logger.info("Admin password used: {} ".format(self.admin_pass))
            logger.info("csv file name: {} ".format(csv_file))
            

            status_dict = {}
            sweep_count_dict={}
            latency_dict ={}
            mac_address_dict = {}
            ip_host_name = {}
            count =0
            existing_ips=[]
            ips_from_response=[]
            to_break_while = False

            while time.time() - start_time < self.scan_duration:
                    self.last_sweep_ending_timestamp = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
                    # print(self.last_sweep_ending_timestamp,"last_sweep_ending_timestamp-----")
                    cmd_with_expect = f'''
                        spawn {command}
                        expect -re ".*password.*"
                        send "{self.admin_pass}\\r"
                        interact
                        '''
                    process = subprocess.Popen(['expect', '-c', cmd_with_expect], text=True, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
                    # result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    #                         check=True)

                    stdout =""
                    stderr = ""
                    time_format = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")

                    try:

                        stdout, stderr = process.communicate(timeout=self.scan_duration - (time.time() - start_time))
                    except subprocess.TimeoutExpired:
                        #print("duration exceeded while waiting for output,terminating the current execution")
                        logger.info("duration exceeded while waiting for output,terminating the current execution")
                        if count == 0:
                            to_break_while = True
                            # self.data_lengths.remove(data_length)
                        process.terminate()
                        process.wait()

                    if to_break_while:
                        break
                    timestamp_list.append(time.time())
                    # stdout = result.stdout
                    # out_put_to_ptint = stdout
                    for line in stderr.splitlines():
                        # print(line,"line------------")
                        # line = line.decode("utf-8")
                        if "Failed" or "QUITTING!" in line:
                            logger.info(stderr)
                            to_break_while = True
                            break

                    # print(stdout,"-------------------------------------------------------------------------------------")
                    ip_address = ""
                    status = ""
                    latency = 0
                    #time_format = time.time()
                    for line in stdout.splitlines():
                        # print(line,"line------------")
                        # line = line.decode("utf-8")
                        if "QUITTING!" in line:
                            logger.info(stdout)
                            to_break_while = True
                            break
                        if "Starting Nmap" in line:

                            start_time_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2} \w+', line)
                            #if start_time_match:

                                #time_format = start_time_match.group().replace(' IST', '').replace(' PDT', '').replace(' PST', '')
                                #self.last_sweep_ending_timestamp = datetime.strptime(time_format,"%Y-%m-%d %H:%M")
                                #self.last_sweep_ending_timestamp = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
                                #time_format = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
                                # print(self.sweep_terminated_time,"check2----")
                        elif "Nmap scan report for" in line:
                            cmd_output = True
                            ip_address = line.split()[-1].replace("(", "").replace(")","")
                            ips_from_response.append(ip_address)
                            status_dict[ip_address] = 0
                            if ip_address in list(sweep_count_dict.keys()):
                                sweep_count_dict[ip_address] += 1
                            else:
                                sweep_count_dict[ip_address] = 1


                            latency_dict[ip_address] = 0
                            mac_address_dict[ip_address] = "N/A"
                            ip_host_name[ip_address] = "N/A"
                            if ip_address not in list(status_dict.keys()):
                                status_dict[ip_address] = 0
                            # pattern = r'Nmap scan report for(?: (\S+))?( \(\d+\.\d+\.\d+\.\d+\))?'
                            # pattern = r'Nmap scan report for (\S+)(?: \(\d+\.\d+\.\d+\.\d+\))?'
                            pattern = r'Nmap scan report for (\S+)(?: \(\d+\.\d+\.\d+\.\d+\))?'
                            match = re.search(pattern, line)
                            if match:
                                if line.split()[-2] != "for":
                                    ip_host_name[ip_address] = match.group(1)

                        elif "Host is up" in line:
                            host_status[ip_address] = 'active'
                            status_dict[ip_address] = 1
                            status = 'active'
                            latency_match = re.search(r'\((.*?) latency\)', line)
                            latency = "N/A"
                            if latency_match:
                                latency = latency_match.group(1)
                            # print(latency,"latency---")
                            latency_dict[ip_address] = latency



                        elif "MAC Address: " in line:
                            # pattern = r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
                            pattern = r'MAC Address: ([0-9A-Fa-f:]+)(?: \(([^)]+)\))?'
                            mac_match = re.search(pattern,line)
                            mac_address_dict[ip_address] = "N/A"
                            # ip_host_name[ip_address] = "N/A"

                            if mac_match:
                                mac_address_dict[ip_address] = mac_match.group(1)
                                # print(mac_match.group(0))
                                if mac_match.group(2):
                                    ip_host_name[ip_address] = mac_match.group(2)


                        elif "Nmap done" in line:
                            # print(status_dict, "status_dict")
                            last_sweep_ending_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                            self.last_sweep_ending_timestamp = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")
                            if csv_file not in self.created_csv_files and len(list(status_dict.keys())) > 0:
                                self.created_csv_files.append(csv_file)

                            new_column_data =  [start_time] + list(status_dict.keys())
                            file_exists = os.path.isfile(csv_file)
                            with open(csv_file, mode='a+', newline='') as file:
                                csv_writer = csv.writer(file)

                                if not file_exists:
                                    header = ['Host Ip']
                                    csv_writer.writerow(header)

                                    # Write the IP addresses as rows
                                    for ip in list(status_dict.keys()):
                                        csv_writer.writerow([ip])

                                file.seek(0)
                                reader = csv.reader(file)
                                data = [row for row in reader]
                                # print(data,"data---")
                                existing_ips = [row[0] for row in data]

                                # print(existing_ipm_s,"---existing")
                                # print(ips_froresponse,"---resp")
                                # if count > 0:
                                for ip in existing_ips:

                                    if ip != "Host Ip" and ip not in ips_from_response:
                                        status_dict[ip] = 0
                                # data = [row for row in reader]
                                # print(data)
                                count += 1
                                logger.info("iteration {}".format(count))
                                existing_ips = []
                                ips_from_response = []
                                # print(status_dict.keys(),"status_dict.keys()--------")
                                for ip in status_dict.keys():
                                    value_found = any(row[0] == ip for row in data)
                                    if not value_found:
                                        new_row_data = [ip] + ['0'] * (count - 1)
                                        # new_row_data.append(status_dict[ip])
                                        data.append(new_row_data)
                                for i, row in enumerate(data):

                                    if i ==0:
                                        row.append(time_format)
                                    else:
                                        if status_dict[row[0]] == 1:
                                            text = f"{status_dict[row[0]]},{latency_dict[row[0]]}"
                                        else:
                                            text = f"{status_dict[row[0]]}"

                                        row.append(text)
                                file.truncate(0)  # Clear the file contents
                                file.seek(0)
                                    # writer = csv.writer(file)
                                csv_writer.writerows(data)
                    if to_break_while:
                        break
            self.last_sweep_ending_timestamp_list.append(self.last_sweep_ending_timestamp)

            # if not cmd_output:
            #     print(out_put_to_ptint)
                # exit(0)

            if len(list(status_dict.keys())) > 0:
                for ip in list(status_dict.keys()):
                    if ip not in list(ip_host_name.keys()):
                        ip_host_name[ip] = "N/A"
                    if ip not in list(mac_address_dict.keys()):
                        mac_address_dict[ip] = "N/A"
                self.no_of_ping_sweeps.append(count)
                self.no_of_sweeps_per_ip.append(list(sweep_count_dict.values()))
                self.executed_data_lengths.append(data_length)
                self.host_mac_list.append(list(mac_address_dict.values()))
                self.host_name_list.append(list(ip_host_name.values()))
                # print(self.host_name_list)


    def get_graph_png(self,csv_name,y_labels,datasets,x_labels):

        num_ips = len(y_labels)
        num_timestamps = len(x_labels)

        # Calculate the bar width so that all bars have equal lengths
        bar_width = 1 / num_timestamps

        # fig, ax = plt.subplots()

        fig, ax = plt.subplots(figsize=(18, num_ips * .5 + 2))
        for i in range(num_ips):
            for j in range(num_timestamps):
                value = datasets[i][j]
                if value == '1':
                    ax.barh(y_labels[i], bar_width, height=0.5, left=j * bar_width, color='#70ad47')
                else:
                    ax.barh(y_labels[i], bar_width, height=0.5, left=j * bar_width, color='#ff0000')

        ax.set_xlabel('Time stamp',fontsize=13)
        ax.set_ylabel("IP's",fontsize=13)
        ax.set_yticks(y_labels)
        ax.set_yticklabels(y_labels,fontsize=12)
        # No of timestamps divided by value gives you no of labels to skip, the value is the no of x axis labels to be displayed
        timstamp_interval = max(1, num_timestamps // 30)
        ax.set_xticks([j * bar_width for j in range(0, num_timestamps, timstamp_interval)])
        ax.set_xticklabels([x_labels[j] for j in range(0, num_timestamps, timstamp_interval)], rotation=45,
                           fontsize=10,ha="right")
        plt.tight_layout()
        ax.invert_yaxis()
        legend_labels = ['Active', 'In active']
        legend_colors = ['#70ad47', '#ff0000']
        legend_elements = [Line2D([0], [0], color=color, lw=4, label=label) for color, label in
                           zip(legend_colors, legend_labels)]
        ax.legend(handles=legend_elements, loc='upper right', prop={'size': 10})
        # ax.legend(['green 1', 'red 0'])
        image_name = csv_name.split("/")[1].split(".")[0]
        # print(image_name,"imagename---")
        plt.savefig("%s.png" % image_name, dpi=96)
        plt.close()

        return "%s.png" % image_name

    def generate_report(self,test_setup_info):
        logger.info("List of CSV files created: {}".format(self.created_csv_files))
        # report = lf_report.lf_report(_results_dir_name="ping_sweep", _output_html="Ping_Sweep.html",
        #                              _output_pdf="Ping_Sweep.pdf", _path="")
        self.report.set_title("Ping Sweep Test report")
        self.report.set_date(str(datetime.now()).split(",")[0].replace(" ", "-").split(".")[0])
        self.report.build_banner()
        self.report.set_table_title("Test Setup Information")
        self.report.build_table_title()

        self.report.test_setup_table(value="Test Setup Information", test_setup_data=test_setup_info)

        self.report.set_obj_html("Objective",
                            "Candela Ping Sweep Test is designed to discover devices within the network"
                            "connectivity by measuring latency. It also detects issues like client unavailability time,"
                            "and average latency, ensuring effective device communication and identifying"
                            "connectivity problems")
        self.report.build_objective()
        # self.created_csv_files = ["ping_sweep__32_2023-11-07-21:14:21.csv","ping_sweep__128_2023-11-07-22:14:21"]
        #print(self.created_csv_files,"created_csv_files")
        individual_test_duration = self.scan_duration
        if self.scan_duration < 60:
            individual_test_duration = f"{self.scan_duration} sec"
        elif 60 <= self.scan_duration < 3600:
            minutes = self.scan_duration / 60
            individual_test_duration = f"{str(round(abs(minutes), 1))} minute" if minutes == 1.0 else f"{str(round(abs(minutes), 1))} minutes"
        else:
            hours = self.scan_duration / 3600
            individual_test_duration = f"{str(round(abs(hours), 1))} hour" if hours == 1.0 else f"{str(round(abs(hours), 1))} hours"
        for i,csv_name in enumerate(self.created_csv_files):
            file_exists = os.path.isfile(csv_name)
            if not file_exists:
                continue
            # print(csv_name,"csv_name")
            with open(csv_name, mode='r') as file:
                reader = csv.reader(file)
                data = [row for row in reader]
                # print(data)
                file.seek(0)
                csv_timestamps  = next(reader)
                x_labels = csv_timestamps[1:]
                csv_ips = [row[0] for row in data][1:]
                # print([row for row in data][1:])
                # print(csv_timestamps)
                # print(csv_ips)
                print(self.last_sweep_ending_timestamp_list[i],"--> check1 - Last Sweep end time.")
                logger.info("sweep ending timestamp: {i} --> {time} ".format(i=i,time=self.last_sweep_ending_timestamp_list[i]))
                datasets = []
                avg_latency_list = []
                disconnection_list = []
                self.actual_sweep_duration = self.last_sweep_ending_timestamp_list[i] - datetime.strptime(x_labels[0].replace(" PDT","").replace(" PST",""),"%Y-%m-%d %H:%M:%S")
                print(self.actual_sweep_duration,"--> check2 - Actual sweep duration.")
                logger.info("Actual sweep duration: {i} --> {act_time}".format(i=i,act_time = self.actual_sweep_duration))
                self.percentage_duration =  self.actual_sweep_duration * (int(self.percentage[:-1]) /100)
                # print(f"{self.percentage_duration} --> {self.percentage[:-1]} percentage of sweep duration")
                for values in [row for row in data][1:]:
                    # print(values[1:],"values------------")
                    # print([value.split(",")[0] for value in values[1:]],"status----------")
                    avg_latency = 0
                    active_over_duration = 0
                    dataset_individual_list=[]
                    first_zero_present = False
                    first_zero = 0
                    sum_of_disconnection = 0
                    next_zero_before_one = 0
                    disconnection_time = 0
                    # print(values[1:])
                    # print(x_labels)
                    for j,value in enumerate(values[1:]):
                        if value.split(",")[0] == "1":
                            active_over_duration += 1
                            try:
                                avg_latency += float(value.split(",")[1][:-1])
                            except:
                                print("no latency value in csv")
                            # print(value.split(",")[0])
                            if first_zero_present:

                                next_zero_before_one = x_labels[j]
                                disconnection_time = datetime.strptime(next_zero_before_one.replace(" PDT","").replace(" PST",""), "%Y-%m-%d %H:%M:%S") - datetime.strptime(first_zero.replace(" PDT","").replace(" PST",""), "%Y-%m-%d %H:%M:%S")
                                disconnection_time=disconnection_time.total_seconds()
                                sum_of_disconnection += disconnection_time
                                first_zero_present = False
                        elif value.split(",")[0] == "0":
                            if not first_zero_present:
                                first_zero = x_labels[j]

                            if j+1 != len(values[1:]):
                                first_zero_present = True

                        if j+1 == len(values[1:]) and first_zero_present:
                            # print(first_zero)
                            # print(x_labels[j])

                            disconnection_time = datetime.strptime(x_labels[j].replace(" PDT","").replace(" PST",""),
                                                                   "%Y-%m-%d %H:%M:%S") - datetime.strptime(first_zero.replace(" PDT","").replace(" PST",""),
                                                                                                         "%Y-%m-%d %H:%M:%S")
                            disconnection_time = disconnection_time.total_seconds()

                            sum_of_disconnection += disconnection_time
                        # print(sum_of_disconnection,"=====")
                        elif j+1 == len(values[1:]) and not first_zero_present:
                            if value.split(",")[0] == "0":
                                # print(self.last_sweep_ending_timestamp)
                                disconnection_time = self.last_sweep_ending_timestamp_list[i] - datetime.strptime(x_labels[j].replace(" PDT","").replace(" PST",""),"%Y-%m-%d %H:%M:%S")
                                disconnection_time = disconnection_time.total_seconds()
                                #print(disconnection_time,"disconnection_time")
                                sum_of_disconnection += disconnection_time
                        dataset_individual_list.append(value.split(",")[0])
                    avg_latency_list.append(avg_latency / active_over_duration)
                    datasets.append(dataset_individual_list)
                    # print(sum_of_disconnection,"---")
                    disconnection_list.append(sum_of_disconnection)
                    dataset_individual_list = []

                y_labels = csv_ips
                graph_png = self.get_graph_png(csv_name,y_labels,datasets,x_labels)
                # print(self.data_lengths ,"self.data_lengths[i] ")
                if self.executed_data_lengths[i] == "6":
                    self.report.set_graph_title(f"Individual Ping Sweep Graph for {individual_test_duration} duration:")
                else:
                    self.report.set_graph_title(f"Individual Ping Sweep Graph with {self.executed_data_lengths[i]} data-packet size for {individual_test_duration} duration:")
                self.report.build_graph_title()
                self.report.set_graph_image(graph_png)
                self.report.move_graph_image()
                self.report.build_graph()

        # for i,csv_name in enumerate(self.created_csv_files):
        #     file_exists = os.path.isfile(csv_name)
        #     with open(csv_name, mode='r') as file:
        #         reader = csv.reader(file)
        #         file.seek(0)
                data = [row for row in reader]
                # print(data)
                file.seek(0)
                csv_timestamps  = next(reader)
                x_labels = csv_timestamps[1:]
                # print(data,"data----")
                csv_ips = [row[0] for row in data]
                # print(csv_ips,"=========")
                # print([row[0] for row in data])
                if self.executed_data_lengths[i] == "6":
                    self.report.set_table_title(
                        f"Individual client table report:")
                else:
                    self.report.set_table_title(
                        f"Individual client table report for {self.executed_data_lengths[i]} data-packet size:")
                # report.set_table_title(f"Individual client table report for {self.data_lengths[i]} data-packet size")
                self.report.build_table_title()
                # print(avg_latency_list)
                # print([i for i in range(1,len(csv_ips)+1)])
                # print(len(csv_ips),"ips length")
                # print(len(disconnection_list))
                # print(self.host_mac_list,"self.host_mac_list")
                # print(len(self.host_name_list),"self.host_name_list")
                # print(csv_ips,"csv_ips")
                # print(len(self.host_mac_list),"self.host_mac_list")
                # print(len(avg_latency_list),"len(avg_latency_list)")
                # print(len(disconnection_list),"disconnection_list")
                # print(self.no_of_sweeps_per_ip,"active sweeps ")
                dataframe = pd.DataFrame({
                    'Sl.no.': [i for i in range(1,len(csv_ips)+1)],
                    'Device name':self.host_name_list[i],
                    'IP Address': csv_ips,
                    'Client MAC': self.host_mac_list[i],
                    'Total Sweeps': [self.no_of_ping_sweeps[i]] * len(avg_latency_list),
                    'Active Sweeps': self.no_of_sweeps_per_ip[i],
                    "Avg Latency[ms]": avg_latency_list,
                    "Client unreachability Time[sec]":disconnection_list
                })
                self.report.set_table_dataframe(dataframe)
                self.report.build_table()
                ips = []
                unavail_percent = []
                device_name = []
                client_macs=[]
                sorted_disconnection_list = sorted(disconnection_list,reverse=True)
                # print(self.actual_sweep_duration.total_seconds(),"self.actual_sweep_duration.total_seconds()")
    
                for index,dur in enumerate(disconnection_list):
                    round((dur/self.actual_sweep_duration.total_seconds())*100,2)
                    if float(self.percentage[:-1]) < round((dur/self.actual_sweep_duration.total_seconds())*100,2):
                        ips.append(csv_ips[index])
                        device_name.append(self.host_name_list[i][index])
                        client_macs.append(self.host_mac_list[i][index])
                        unavail_percent.append(round((dur/self.actual_sweep_duration.total_seconds())*100,2))
                    # unavail_percent.append(round((disconnection_list[index]/600)*100,2))

                self.report.set_table_title(f"Summary table:")   
                self.report.build_table_title()     
                dataframe1 = pd.DataFrame({
                    'Sl.no.': [i for i in range(1,len(ips)+1)],
                    'Device name':device_name,
                    'IP Address': ips,
                    'Client MAC': client_macs,
                    "Client unavailability perccentage":unavail_percent,
                    "Reason": ["host down, received no-response"] * len(ips)
                })
                self.report.set_table_dataframe(dataframe1)
                self.report.build_table()
        self.report.build_footer()
        html_file = self.report.write_html()
        #print("returned html file {}".format(html_file))
        logger.info("returned html file {}".format(html_file))
        
        # print(html_file)
        self.report.write_pdf()




def main():
    parser = argparse.ArgumentParser(
        prog="lf_ping_sweep.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
----------------------------------------------------------------------------------------------
Objective:
    This Ping Sweep Test script is designed to discover devices within the network
    connectivity by measuring latency. It also detects issues like client unavailability time,
    and average latency, ensuring effective device communication and identifying
    connectivity problems
    Note:
        The script uses Nmap tool.
        If Namp not present in the system , then it can be installed using the command: sudo apt-get install nmap
----------------------------------------------------------------------------------------------
CLI Example1:
    python3 lf_ping_sweep.py -e eth1 -ip 192.168.1.1/24  --duration 10h --csv_name ping_sweep_1 --reporting_down_time_percentage 30%
    
CLI Example2 - with data packets:
    python3 lf_ping_sweep.py -e eth1 -ip 192.168.1.1/24 --data_lengths 32 64 128 500  --duration 10m --csv_name ping_sweep_1 --reporting_down_time_percentage 50%

CLI Example3 - with different root password:
    python3 lf_ping_sweep.py -e eth1 -ip 192.168.1.1/24 --data_lengths 32 64 1024  --duration 1h --csv_name ping_sweep_1  --admin_pass orangeunit --reporting_down_time_percentage 40%

Note: --reporting_down_time_percentage is used to calculate the ips which were down more than given percentage of its duration (default is 30%).

----------------------------------------------------------------------------------------------
""")
    parser.add_argument("-e", "--ethernet_interface", type=str, help="ethernet interface ")
    parser.add_argument("-ip","--target_ip",help="mention the target ip or network subnet")
    parser.add_argument("-dur", "--duration", type=str, help="provide the scanning duration in either hours or minutes or seconds,ex: 2h or 30m or 50s")
    parser.add_argument("-csv", "--csv_name", type=str, help="provide the file name  in which the csv should be created",default="ping_sweep")
    parser.add_argument("-data_len","--data_lengths",  type=str, nargs='+', help="List of data lengths",default=["6"])
    parser.add_argument("-admin_password","--admin_pass",  type=str, help="provide the admin/root password",default="lanforge")
    parser.add_argument("-reporting_down_time_percentage","--reporting_down_time_percentage",  type=str, help="provide the percentage for calculation of ips which were down more than the percentage of duration, default is 30",default="30%")


    args = parser.parse_args()
    logger_config = lf_logger_config.lf_logger_config()
    scan_duration = 60
    # print(args.data_lengths)
    # print(type(args.data_lengths))
    duration_suffixes = {'s': 1, 'S': 1, 'm': 60, 'M': 60, 'h': 3600, 'H': 3600}
    if args.duration.endswith(tuple(duration_suffixes.keys())):
        test_duration_suffix = args.duration[-1]
        multiplier = duration_suffixes[test_duration_suffix]
        scan_duration = int(args.duration[:-1]) * multiplier
    
    logger.info("Test Initaited.")
    ping_sweep_obj = ping_sweep(eth_interface=args.ethernet_interface,
                                target_ip=args.target_ip,
                                csv_file=args.csv_name,
                                admin_pass=args.admin_pass,
                                data_lengths=args.data_lengths,
                                scan_duration=scan_duration,
                                percentage= args.reporting_down_time_percentage
                                )
    ping_sweep_obj.run_ping()
    test_duration = timedelta(seconds=scan_duration * len(args.data_lengths))
    individual_test_duration = scan_duration
    if scan_duration < 60:
        individual_test_duration = f"{scan_duration} sec"
    elif 60 <= scan_duration < 3600:
        minutes = scan_duration / 60
        individual_test_duration = f"{str(round(abs(minutes), 1))} minute" if minutes == 1.0 else f"{str(round(abs(minutes), 1))} minutes"
    else:
        hours = scan_duration / 3600
        individual_test_duration = f"{str(round(abs(hours), 1))} hour" if hours == 1.0 else f"{str(round(abs(hours), 1))} hours"

    if args.data_lengths == ["6"]:

        test_setup_info = {
            "Total test Duration (HH:MM:SS)": test_duration,
            "Packet size": "Default",
            "Target ip": args.target_ip,
            "Reporting down-time %":args.reporting_down_time_percentage

        }
    else:
        test_setup_info = {
            "Total test Duration (HH:MM:SS)": test_duration,
            "Packet size": args.data_lengths ,
            "Duration per packet length": individual_test_duration,
            "Target ip": args.target_ip,
            "Reporting down-time %":args.reporting_down_time_percentage

        }    
    if len(ping_sweep_obj.created_csv_files) > 0:
        logger.info("Generating Report.")
        ping_sweep_obj.generate_report(test_setup_info=test_setup_info)









if __name__ == "__main__":
    main()
