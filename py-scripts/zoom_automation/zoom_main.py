import os
import csv
import paramiko
import time
import platform
import requests
import threading
import argparse
import pytz
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import sys
import importlib
import pandas as pd
import random
import matplotlib.pyplot as plt
import shutil
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))



lf_report = importlib.import_module("py-scripts.lf_report")
lf_report = lf_report.lf_report
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_bar_graph = lf_graph.lf_bar_graph
lf_scatter_graph = lf_graph.lf_scatter_graph
lf_bar_graph_horizontal = lf_graph.lf_bar_graph_horizontal
lf_line_graph = lf_graph.lf_line_graph
lf_stacked_graph = lf_graph.lf_stacked_graph
lf_horizontal_stacked_graph = lf_graph.lf_horizontal_stacked_graph
class ZoomAutomation:
    def __init__(self, hosts_file='hosts.csv', credential_file='credentials.txt',ssid="SSID",band="5G",security="wpa2",apname="AP Name",
                 sigin_email=None,sigin_passwd= None, duration=1, participants = 3 ,audio = True, video = True,lanforge_ip="localhost",wait_time = 30):
        self.hosts_file = os.path.join(os.path.dirname(__file__),hosts_file)
        self.credential_file = os.path.join(os.path.dirname(__file__),credential_file)
        self.flask_ip = lanforge_ip
        self.app = Flask(__name__)
        self.windows = 0
        self.linux = 0
        self.mac = 0
        self.clients = self.read_clients_from_csv()
        self.read_client_details_from_resources()
        print(self.clients)
        self.password_status = False  # Initially set to False
        self.login_completed = False  # Initially set to False
        self.remote_login_url = ""  # Initialize remote login URL
        self.remote_login_passwd = ""  # Initialize remote login password
        
        self.test_start = False
        self.start_time = None
        self.end_time = None
        self.participants_joined = 0
        
        self.ap_name = apname
        self.ssid = ssid
        self.band = band
        self.security = security
        self.tz = pytz.timezone('Asia/Kolkata')
        # self.path = "/home/lanforge/lanforge-scripts/py-scripts/zoom_automation/test_results"
        self.not_processed_clients = []
        self.clients_disconnected = False
        self.audio = audio
        self.video = video
        self.wait_time = wait_time

        self.sigin_email = sigin_email
        self.sigin_passwd = sigin_passwd
        self.duration = duration
        self.participants_req = participants

        # Get the current working directory
        current_dir = os.getcwd()
        print("Current Working Directory:", current_dir)

        # Define the additional directory you want to add
        additional_dir = "test_results"

        # Combine the current directory with the additional directory
        self.path = os.path.join(os.path.dirname(__file__), additional_dir)

        print("New Path:", self.path )

        os.makedirs(self.path, exist_ok=True)

    # def read_clients_from_csv(self):
    #     self.clients = []
    #     try:
    #         with open(self.hosts_file, 'r', newline='') as csvfile:
    #             reader = csv.DictReader(csvfile)
    #             for row in reader:
    #                 client = {
    #                     'hostname': row.get('hostname', 'N/A'),
    #                     'IP': row.get('IP', 'N/A'),
    #                     'username': row.get('username', 'N/A'),
    #                     'password': row.get('password', 'N/A'),
    #                     'os_type': row.get('os_type', 'N/A'),
    #                     'type': row.get('type', 'N/A')
    #                 }
    #                 self.clients.append(client)
    #         return self.clients
    #     except FileNotFoundError:
    #         print(f"Error: File '{self.hosts_file}' not found.")
    #         return []
    #     except csv.Error as e:
    #         print(f"Error: Failed to read CSV file '{self.hosts_file}': {e}")
    #         return []
    def read_clients_from_csv(self):
        self.clients = []
        try:
            with open(self.hosts_file, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    client = {
                        'res': row.get('res', 'N/A'),
                        'username': row.get('username', 'N/A'),
                        'password': row.get('password', 'N/A'),
                        'type': row.get('type', 'N/A')
                    }
                    self.clients.append(client)
            return self.clients
        except FileNotFoundError:
            print(f"Error: File '{self.hosts_file}' not found.")
            return []
        except csv.Error as e:
            print(f"Error: Failed to read CSV file '{self.hosts_file}': {e}")
            return []
        
    def read_client_details_from_resources(self):
        try:
            client_array = []
            resource_data = requests.get(f'http://{self.flask_ip}:8080/resource/all')
            resource_data = resource_data.json()
            rsources = resource_data["resources"]
           
            for client in self.clients:
                for res in rsources:
                    if client["res"] == list(res.keys())[0]:
                        key = list(res.keys())[0]
                        client["IP"] = res[key]["ctrl-ip"]
                        client["hostname"] = res[key]["hostname"]
                        print(res[key]["hw version"])
                        client["os_type"] = "mac" if "Apple/" in res[key]["hw version"] else ("windows" if "Win/" in res[key]["hw version"] else ("linux" if "Linux/" in res[key]["hw version"] else "others"))
                        client_array.append(client.copy())
                        break


            self.clients = client_array
        except Exception as e:
            print("error while updating client details from resource",e)
    
    def write_credentials_to_file(self):
        try:
            with open(self.credential_file, 'w') as f:
                f.write(f"lanforge_ip={self.flask_ip}:5000\n")
            print(f"Credentials written to '{self.credential_file}' successfully.")
        except Exception as e:
            print(f"Error writing credentials to file: {e}")

    def ssh_and_transfer_files(self, hostname, ip, username, password, os_type, client_type,obj):
        client = None
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=ip, username=username, password=password)
                   
            file_to_transfer = 'zoom_host.py' if client_type == 'host' else 'zoom_client.py'
            remote_dir = self.get_remote_dir(os_type, username)
            
            local_path = os.path.join(os.path.dirname(__file__), file_to_transfer)
            remote_path = os.path.join(remote_dir, file_to_transfer)
            print(local_path)
            print(remote_path)
            with open(local_path, 'rb') as f:
                file_data = f.read()
                sftp = client.open_sftp()
                sftp.put(local_path, remote_path)
                sftp.put(self.credential_file, os.path.join(remote_dir, 'credentials.txt'))  # Transfer credentials.txt
                sftp.close()
                print(f"  - Successfully transferred '{file_to_transfer}' to {hostname}:{remote_path}")
        
        except Exception as e:
            print(f"Error while processing {hostname}: {e}")
            self.not_processed_clients.append(obj)
        
        finally:
            if client:
                client.close()

    def get_csv_files(self,local_path):
        for client_to_get in self.clients:
            hostname = client_to_get.get('hostname', 'N/A')
            ip = client_to_get.get('IP', 'N/A')
            username = client_to_get.get('username', 'N/A')
            password = client_to_get.get('password', 'N/A')
            os_type = client_to_get.get('os_type', 'N/A')
            client = None
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname=ip, username=username, password=password)

                


                file_to_transfer = '{}.csv'.format(hostname)
                remote_dir = self.get_remote_dir_not_inc(os_type, username)
                
                                 
                sftp = client.open_sftp()
                
                file_prefix = '{}'.format(hostname)
                # List files in the remote directory
                remote_files = sftp.listdir(remote_dir)

                # Filter files that match the specified prefix
                matching_files = [file for file in remote_files if file.startswith(file_prefix)]
                
                for file in matching_files:
                    remote_file_path = os.path.join(remote_dir, file)
                   
                    # Download the matching file
                    sftp.get(remote_file_path, local_path+file_to_transfer)
                    sftp.close()
                    print(f"  - Successfully fetched '{file_to_transfer}' from {hostname}:{remote_file_path}")
                    break
            
            except Exception as e:
                print(f"Error while fetching csv file for {hostname}: {e}<-----------------------no csv files")
                try:
                    os.remove(local_path+file_to_transfer)
                    print("removing not found")
                except:
                    pass
                
            finally:
                if client:
                    client.close()

    def get_remote_dir(self, os_type, username):
        os_type = os_type.lower()
        if os_type == "linux":
            self.linux += 1
            return f"/home/{username}/Documents/zoom_automation/"
        elif os_type == "windows":
            self.windows += 1
            return f"C:/Users/{username}/Documents/zoom_automation/"
        elif os_type == "mac":
            self.mac += 1
            return f"/Users/{username}/Documents/zoom_automation/"
        else:
            raise ValueError(f"Unsupported os_type: {os_type}")

    def get_remote_dir_not_inc(self, os_type, username):
        os_type = os_type.lower()
        if os_type == "linux":
            return f"/home/{username}/Documents/zoom_automation/"
        elif os_type == "windows":
            return f"C:/Users/{username}/Documents/zoom_automation/"
        elif os_type == "mac":
            return f"/Users/{username}/Documents/zoom_automation/"
        else:
            raise ValueError(f"Unsupported os_type: {os_type}")

    def start_flask_server(self):
        @self.app.route('/login_url', methods=['GET', 'POST'])
        def login_url():
            if request.method == 'GET':
                return jsonify({"login_url": self.remote_login_url})
            elif request.method == 'POST':
                data = request.json
                self.remote_login_url = data.get('login_url', '')
                return jsonify({"message": f"Updated login_url to {self.remote_login_url}"})

        @self.app.route('/login_passwd', methods=['GET', 'POST'])
        def login_passwd():
            if request.method == 'GET':
                return jsonify({"login_passwd": self.remote_login_passwd})
            elif request.method == 'POST':
                data = request.json
                self.remote_login_passwd = data.get('login_passwd', '')
                return jsonify({"message": "Password updated successfully."})

        @self.app.route('/login_completed', methods=['GET', 'POST'])
        def login_completed():
            if request.method == 'GET':
                return jsonify({"login_completed": self.login_completed})
            elif request.method == 'POST':
                data = request.json
                self.login_completed = data.get('login_completed', False)
                return jsonify({"message": f"Updated login_completed status to {self.login_completed}"})
        
        @self.app.route('/get_host_email', methods=['GET'])
        def get_host_email():
            print(self.sigin_email,"email login")
            return jsonify({"host_email":self.sigin_email})

        @self.app.route('/get_host_passwd', methods=['GET'])
        def get_host_passwd():
            return jsonify({"host_passwd":self.sigin_passwd})
        
        @self.app.route('/get_participants_joined', methods=['GET'])
        def get_participants_joined():
            return jsonify({"participants":self.participants_joined})
        
        @self.app.route('/set_participants_joined', methods=['POST'])
        def set_participants_joined():
            data = request.json
            self.participants_joined = data.get('participants_joined', None)
            return jsonify({"message": f"Updated participants jopind status to {self.participants_joined}"})
        
        @self.app.route('/get_participants_req', methods=['GET'])
        def get_participants_req():
            return jsonify({"participants":self.participants_req})
        
        @self.app.route('/test_started', methods=['GET', 'POST'])
        def test_started():
            print("inside test started")
            if request.method == 'GET':
                print("inside test started get")
                return jsonify({"test_started": self.test_start})
            elif request.method == 'POST':
                print("inside test started post")
                print("sdfsdfsdfsd")
                data = request.json
                print(data)
                self.test_start = data.get('test_started', False)
                return jsonify({"message": f"Updated test_start status to {self.test_start}"})
        
        @self.app.route('/clients_disconnected', methods=['POST'])
        def client_disconnected():
            print("inside client disconnected  post")
            data = request.json
            print(data)
            self.clients_disconnected = data.get('clients_disconnected', False)
            return jsonify({"message": f"Updated clients_disconnected status to {self.clients_disconnected}"})

        @self.app.route('/get_start_end_time', methods=['GET'])
        def get_start_end_time():
            return jsonify({
                "start_time": self.start_time.isoformat() if self.start_time is not None else None,
                "end_time": self.end_time.isoformat() if self.end_time is not None else None
            })
        @self.app.route('/stats_opt', methods=['GET'])
        def stats_to_be_collected():
            return jsonify({
                'audio_stats':self.audio,
                "video_stats":self.video
            })
        try:
            self.app.run(host=self.flask_ip, port=5000, debug=True, threaded=True, use_reloader=False)
        except Exception as e:
            print(f"Error starting Flask server: {e}")
    
    def set_start_time(self):
        self.start_time = datetime.now(self.tz) + timedelta(seconds=30)
        self.end_time = self.start_time + timedelta(minutes=self.duration)
        return [self.start_time,self.end_time]
        
    def run(self):
        # Store the email and password in the instance
        
        flask_thread = threading.Thread(target=self.start_flask_server)
        flask_thread.daemon = True
        flask_thread.start()

        # Give the Flask server some time to start
        time.sleep(5)

        self.write_credentials_to_file()

        for client in self.clients:
            hostname = client.get('hostname', 'N/A')
            ip = client.get('IP', 'N/A')
            username = client.get('username', 'N/A')
            password = client.get('password', 'N/A')
            os_type = client.get('os_type', 'N/A')
            client_type = client.get('type', 'N/A')
            
            if client_type == 'host':
                print(f"Processing Host ({hostname})")
                self.ssh_and_transfer_files(hostname, ip, username, password, os_type, client_type,client)
        login_tries = 0    
        while not self.login_completed:
            time.sleep(5)
            login_tries += 1
            if login_tries > 30:
                print("Unable to login in host. Exiting the test")
                return
            
            # try:
            #     response = requests.get(f"http://{self.flask_ip}:5000/login_completed")
            #     data = response.json()
            #     self.login_completed = data.get('login_completed', False)
            #     time.sleep(5)
            # except Exception as e:
            #     print(f"Error while checking login_completed status: {e}")
            #     time.sleep(5)

        for client in self.clients:
            hostname = client.get('hostname', 'N/A')
            ip = client.get('IP', 'N/A')
            username = client.get('username', 'N/A')
            password = client.get('password', 'N/A')
            os_type = client.get('os_type', 'N/A')
            client_type = client.get('type', 'N/A')
            
            if client_type == 'client':
                print(f"Processing Client ({hostname})")
                self.ssh_and_transfer_files(hostname, ip, username, password, os_type, client_type,client)
        not_excluded = []
        for client in self.clients:
            if client not in self.not_processed_clients:
                not_excluded.append(client)
        
        print("excluded clients are...",str(self.not_processed_clients))
        self.clients = not_excluded
        while not self.test_start:
            print(self.test_start)
            print("waiting for the test to be started")
            time.sleep(5)

        self.set_start_time()  
        print("test will be starting")
        while datetime.now(self.tz) < self.end_time:
            if datetime.now(self.tz) > self.start_time:
                print("monitoring the test")
            time.sleep(5)
        print("waiting for clients to get disconnected")
        tries = 0
        while not self.clients_disconnected:
            tries += 1
            if tries > 25:
                print("disconnection time exceeded")
                break
            time.sleep(5)
        print("waiting for some time for file transfer")
        time.sleep(self.wait_time)
        print("generating report")
        self.generate_report()
        print("test_completed")
        
        

    def move_files(self,source_file, dest_dir):
        # Ensure the source file exists
        if not os.path.isfile(source_file):
            print(f"Source file '{source_file}' does not exist or is not a regular file.")
            return
        
        # Ensure the destination directory exists
        if not os.path.exists(dest_dir):
            print(f"Destination directory '{dest_dir}' does not exist.")
            return
        
        try:
            # Extract the filename from the source file path
            filename = os.path.basename(source_file)
            
            # Construct the destination file path
            dest_file = os.path.join(dest_dir, filename)
            
            # Move the file
            shutil.move(source_file, dest_file)
            
            print(f"Successfully moved '{source_file}' to '{dest_file}'.")
        except Exception as e:
            print(f"Failed to move '{source_file}' to '{dest_dir}': {e}")


    def generate_report(self):
        report = lf_report(_path=self.path)
        report_path = report.get_path()
        report_path_date_time = report.get_path_date_time()

        print("path: {}".format(report_path))
        print("path_date_time: {}".format(report_path_date_time))
        self.get_csv_files(local_path=report_path_date_time+"/")
        report.set_title("Zoom Call Automated Report")
        report.build_banner()

        report.set_table_title("Objective:")
        report.build_table_title()
        report.set_text("The objective is to conduct automated Zoom call tests across multiple laptops to gather statistics on sent audio, video, and received audio, video performance. The test will collect these statistics and store them in a CSV file. Additionally, automated graphs will be generated using the collected data.")
        report.build_text_simple()

        report.set_table_title("Test Parameters:")
        report.build_table_title()
        test_parameters = pd.DataFrame([{
            'AP Name': self.ap_name,
            'SSID': self.ssid,
            'Band': self.band,
            'Security': self.security,
            'No of Clients': f'W({self.windows}),L({self.linux}),M({self.mac})',
            'Test Duration(min)': self.duration
        }])
        report.set_table_dataframe(test_parameters)
        report.build_table()
        
        client_array = []
        accepted_clients = []
        no_csv_client = []
        rejected_clients = []
        final_dataset = []
        max_audio_jitter_s,min_audio_jitter_s = [] , []
        max_audio_jitter_r,min_audio_jitter_r = [] , []
        max_audio_latency_s,min_audio_latency_s = [] , []
        max_audio_latency_r,min_audio_latency_r = [] , []
        max_audio_pktloss_s,min_audio_pktloss_s = [] , []
        max_audio_pktloss_r,min_audio_pktloss_r = [] , []

        max_video_jitter_s,min_video_jitter_s = [] , []
        max_video_jitter_r,min_video_jitter_r = [] , []
        max_video_latency_s,min_video_latency_s = [] , []
        max_video_latency_r,min_video_latency_r = [] , []
        max_video_pktloss_s,min_video_pktloss_s = [] , []
        max_video_pktloss_r,min_video_pktloss_r = [] , []
        max_video_quality_s,min_video_quality_s = [] , []
        max_video_quality_r,min_video_quality_r = [] , []
        for client in self.clients:
            temp_max_audio_jitter_s,temp_min_audio_jitter_s = 0.0,0.0
            temp_max_audio_jitter_r,temp_min_audio_jitter_r = 0.0,0.0
            temp_max_audio_latency_s,temp_min_audio_latency_s = 0.0,0.0
            temp_max_audio_latency_r,temp_min_audio_latency_r = 0.0,0.0
            temp_max_audio_pktloss_s,temp_min_audio_pktloss_s = 0.0,0.0
            temp_max_audio_pktloss_r,temp_min_audio_pktloss_r = 0.0,0.0

            temp_max_video_jitter_s,temp_min_video_jitter_s = 0.0,0.0
            temp_max_video_jitter_r,temp_min_video_jitter_r = 0.0,0.0
            temp_max_video_latency_s,temp_min_video_latency_s = 0.0,0.0
            temp_max_video_latency_r,temp_min_video_latency_r = 0.0,0.0
            temp_max_video_pktloss_s,temp_min_video_pktloss_s = 0.0,0.0
            temp_max_video_pktloss_r,temp_min_video_pktloss_r = 0.0,0.0
            temp_max_video_quality_s,temp_min_video_quality_s = 0.0,0.0
            temp_max_video_quality_r,temp_min_video_quality_r = 0.0,0.0
            per_client_data = {
                "audio_jitter_s":[],
                "audio_jitter_r":[],
                "audio_latency_s":[],
                "audio_latency_r":[],
                "audio_pktloss_s":[],
                "audio_pktloss_r":[],
                "video_jitter_s":[],
                "video_jitter_r":[],
                "video_latency_s":[],
                "video_latency_r":[],
                "video_pktloss_s":[],
                "video_pktloss_r":[],
            }
            try:
                file_path = os.path.join(report_path_date_time, f'{client["hostname"]}.csv')
                with open(file_path, mode='r',encoding='utf-8', errors='ignore') as file:
                    csv_reader = csv.DictReader(file)
                    for row in csv_reader:

                        per_client_data["audio_jitter_s"].append(float(row["Sent Audio Jitter (ms)"]))
                        per_client_data["audio_jitter_r"].append(float(row["Receive Audio Jitter (ms)"]))
                        per_client_data["audio_latency_s"].append(float(row["Sent Audio Latency (ms)"]))
                        per_client_data["audio_latency_r"].append(float(row["Receive Audio Latency (ms)"]))
                        per_client_data["audio_pktloss_s"].append(float((row["Sent Audio Packet loss (%)"]).split(" ")[0].replace("%","")))
                        per_client_data["audio_pktloss_r"].append(float((row["Receive Audio Packet loss (%)"]).split(" ")[0].replace("%","")))
                        per_client_data["video_jitter_s"].append(float(row["Sent Video Jitter (ms)"]))
                        per_client_data["video_jitter_r"].append(float(row["Receive Video Jitter (ms)"]))
                        per_client_data["video_latency_s"].append(float(row["Sent Video Latency (ms)"]))
                        per_client_data["video_latency_r"].append(float(row["Receive Video Latency (ms)"]))
                        per_client_data["video_pktloss_s"].append(float((row["Sent Video Packet loss (%)"]).split(" ")[0].replace("%","")))
                        per_client_data["video_pktloss_r"].append(float((row["Receive Video Packet loss (%)"]).split(" ")[0].replace("%","")))


                        temp_max_audio_jitter_s = max(temp_max_audio_jitter_s,float(row["Sent Audio Jitter (ms)"]))
                        temp_max_audio_jitter_r = max(temp_max_audio_jitter_r,float(row["Receive Audio Jitter (ms)"]))
                        temp_max_audio_latency_s =max(temp_max_audio_latency_s,float(row["Sent Audio Latency (ms)"]))
                        temp_max_audio_latency_r =max(temp_max_audio_latency_r,float(row["Receive Audio Latency (ms)"]))
                        temp_max_audio_pktloss_s =max(temp_max_audio_pktloss_s,float((row["Sent Audio Packet loss (%)"]).split(" ")[0].replace("%","")))
                        temp_max_audio_pktloss_r =max(temp_max_audio_pktloss_r,float((row["Receive Audio Packet loss (%)"]).split(" ")[0].replace("%","")))

                        temp_max_video_jitter_s = max(temp_max_video_jitter_s,float(row["Sent Video Jitter (ms)"]))
                        temp_max_video_jitter_r = max(temp_max_video_jitter_r,float(row["Receive Video Jitter (ms)"]))
                        temp_max_video_latency_s = max(temp_max_video_latency_s,float(row["Sent Video Latency (ms)"]))
                        temp_max_video_latency_r = max(temp_max_video_latency_r,float(row["Receive Video Latency (ms)"]))
                        temp_max_video_pktloss_s =max(temp_max_video_pktloss_s,float((row["Sent Video Packet loss (%)"]).split(" ")[0].replace("%","")))
                        temp_max_video_pktloss_r =max(temp_max_video_pktloss_r,float((row["Receive Video Packet loss (%)"]).split(" ")[0].replace("%","")))

                        temp_min_audio_jitter_s = min(temp_min_audio_jitter_s,float(row["Sent Audio Jitter (ms)"])) if temp_min_audio_jitter_s > 0 and float(row["Sent Audio Jitter (ms)"]) > 0 else( float(row["Sent Audio Jitter (ms)"]) if float(row["Sent Audio Jitter (ms)"]) > 0 else temp_min_audio_jitter_s) 
                        temp_min_audio_jitter_r = min(temp_min_audio_jitter_r,float(row["Receive Audio Jitter (ms)"])) if temp_min_audio_jitter_r > 0 and float(row["Receive Audio Jitter (ms)"]) > 0 else ( float(row["Receive Audio Jitter (ms)"]) if float(row["Receive Audio Jitter (ms)"]) > 0 else temp_min_audio_jitter_r) 
                        temp_min_audio_latency_s =min(temp_min_audio_latency_s,float(row["Sent Audio Latency (ms)"])) if temp_min_audio_latency_s > 0 and float(row["Sent Audio Latency (ms)"]) > 0 else ( float(row["Sent Audio Latency (ms)"]) if float(row["Sent Audio Latency (ms)"]) > 0 else temp_min_audio_jitter_s) 
                        temp_min_audio_latency_r =min(temp_min_audio_latency_r,float(row["Receive Audio Latency (ms)"])) if temp_min_audio_latency_r > 0 and float(row["Receive Audio Latency (ms)"]) > 0 else ( float(row["Receive Audio Latency (ms)"]) if float(row["Receive Audio Latency (ms)"]) > 0 else temp_min_audio_jitter_r) 
                        
                        temp_min_audio_pktloss_s =min(temp_min_audio_pktloss_s,float((row["Sent Audio Packet loss (%)"]).split(" ")[0].replace("%",""))) if temp_min_audio_pktloss_s > 0 and float((row["Sent Audio Packet loss (%)"]).split(" ")[0].replace("%","")) > 0 else ( float((row["Sent Audio Packet loss (%)"]).split(" ")[0].replace("%","")) if float((row["Sent Audio Packet loss (%)"]).split(" ")[0].replace("%","")) > 0 else temp_min_audio_pktloss_s) 
                        temp_min_audio_pktloss_r =min(temp_min_audio_pktloss_r,float((row["Sent Audio Packet loss (%)"]).split(" ")[0].replace("%",""))) if temp_min_audio_pktloss_r > 0 and float((row["Sent Audio Packet loss (%)"]).split(" ")[0].replace("%","")) > 0 else ( float((row["Sent Audio Packet loss (%)"]).split(" ")[0].replace("%","")) if float((row["Sent Audio Packet loss (%)"]).split(" ")[0].replace("%","")) > 0 else temp_min_audio_pktloss_r) 


                        temp_min_video_jitter_s = min(temp_min_video_jitter_s,float(row["Sent Video Jitter (ms)"])) if temp_min_video_jitter_s > 0 and float(row["Sent Video Jitter (ms)"]) > 0 else( float(row["Sent Video Jitter (ms)"]) if float(row["Sent Video Jitter (ms)"]) > 0 else temp_min_video_jitter_s) 
                        temp_min_video_jitter_r = min(temp_min_video_jitter_r,float(row["Receive Video Jitter (ms)"])) if temp_min_video_jitter_r > 0 and float(row["Receive Video Jitter (ms)"]) > 0 else ( float(row["Receive Video Jitter (ms)"]) if float(row["Receive Video Jitter (ms)"]) > 0 else temp_min_video_jitter_r) 
                        temp_min_video_latency_s =min(temp_min_video_latency_s,float(row["Sent Video Latency (ms)"])) if temp_min_video_latency_s > 0 and float(row["Sent Video Latency (ms)"]) > 0 else ( float(row["Sent Video Latency (ms)"]) if float(row["Sent Video Latency (ms)"]) > 0 else temp_min_video_latency_s) 
                        temp_min_video_latency_r =min(temp_min_video_latency_r,float(row["Receive Video Latency (ms)"])) if temp_min_video_latency_r > 0 and float(row["Receive Video Latency (ms)"]) > 0 else ( float(row["Receive Video Latency (ms)"]) if float(row["Receive Video Latency (ms)"]) > 0 else temp_min_video_latency_r) 
                        
                        

                        temp_min_video_pktloss_s =min(temp_min_video_pktloss_s,float((row["Sent Video Packet loss (%)"]).split(" ")[0].replace("%",""))) if temp_min_video_pktloss_s > 0 and float((row["Sent Video Packet loss (%)"]).split(" ")[0].replace("%","")) > 0 else ( float((row["Sent Video Packet loss (%)"]).split(" ")[0].replace("%","")) if float((row["Sent Video Packet loss (%)"]).split(" ")[0].replace("%","")) > 0 else temp_min_video_pktloss_s) 
                        temp_min_video_pktloss_r =min(temp_min_video_pktloss_r,float((row["Sent Video Packet loss (%)"]).split(" ")[0].replace("%",""))) if temp_min_video_pktloss_r > 0 and float((row["Sent Video Packet loss (%)"]).split(" ")[0].replace("%","")) > 0 else ( float((row["Sent Video Packet loss (%)"]).split(" ")[0].replace("%","")) if float((row["Sent Video Packet loss (%)"]).split(" ")[0].replace("%","")) > 0 else temp_min_video_pktloss_r) 
         
            except Exception as e:
                print(f"error in reading data in client {client['hostname']}",e)
                no_csv_client.append(client['hostname'])
                rejected_clients.append(client)
            
            if client["hostname"] not in no_csv_client:
                client_array.append(client["hostname"])
                accepted_clients.append(client)
                max_audio_jitter_s.append(temp_max_audio_jitter_s)
                min_audio_jitter_s.append(temp_min_audio_jitter_s)
                max_audio_jitter_r.append(temp_max_audio_jitter_r)
                min_audio_jitter_r.append(temp_min_audio_jitter_r)
                max_audio_latency_s.append(temp_max_audio_latency_s)
                min_audio_latency_s.append(temp_min_audio_latency_s)
                max_audio_latency_r.append(temp_max_audio_latency_r)
                min_audio_latency_r.append(temp_min_audio_latency_r)
                max_video_jitter_s.append(temp_max_video_jitter_s)
                min_video_jitter_s.append(temp_min_video_jitter_s)
                max_video_jitter_r.append(temp_max_video_jitter_r)
                min_video_jitter_r.append(temp_min_video_jitter_r)
                max_video_latency_s.append(temp_max_video_latency_s)
                min_video_latency_s.append(temp_min_video_latency_s)
                max_video_latency_r.append(temp_max_video_latency_r)
                min_video_latency_r.append(temp_min_video_latency_r)

                max_audio_pktloss_s.append(temp_max_audio_pktloss_s)
                min_audio_pktloss_s.append(temp_min_audio_pktloss_s)
                max_audio_pktloss_r.append(temp_max_audio_pktloss_r)
                min_audio_pktloss_r.append(temp_min_audio_pktloss_r)
                max_video_pktloss_s.append(temp_max_video_pktloss_s)
                min_video_pktloss_s.append(temp_min_video_pktloss_s)
                max_video_pktloss_r.append(temp_max_video_pktloss_r)
                min_video_pktloss_r.append(temp_min_video_pktloss_r)

                final_dataset.append(per_client_data.copy())
        print("accepted_client",accepted_clients)
        print("nocsverror",no_csv_client)
        print("rejected_client",rejected_clients)
        report.set_table_title("Test Devices:")
        report.build_table_title()
        
        device_details = pd.DataFrame({
            'Device Name': [client['hostname'] for client in accepted_clients],
            'OS Type': [client['os_type'] for client in accepted_clients],
            'IP Address' : [client['IP'] for client in accepted_clients]
        })
        report.set_table_dataframe(device_details)
        report.build_table()

        if len(rejected_clients) > 0 or len(self.not_processed_clients) :
            report.set_table_title("Devices Excluded:")
            report.build_table_title()
            error_dataframe = []
            for client in rejected_clients:
                error_dataframe.append({
                    'Device Name':client['hostname'],
                    'OS Type' : client['os_type'],
                    'IP Address' : client['IP'],
                    'Error Type': "No csv Error"
                })
            for client in self.not_processed_clients:
                error_dataframe.append({
                    'Device Name':client['hostname'],
                    'OS Type' : client['os_type'],
                    'IP Address' : client['IP'],
                    'Error Type': "Authentication Error"
                })

            report.set_table_dataframe(pd.DataFrame(error_dataframe))
            report.build_table()
                 
        if self.audio:        
            report.set_graph_title("Audio Latency (Sent/Received)")
            report.build_graph_title()
            x_data_set = [max_audio_latency_s.copy(),min_audio_latency_s.copy(),max_audio_latency_r.copy(),min_audio_latency_r.copy()]
            y_data_set = client_array
            print(x_data_set)
            x_fig_size = 18
            y_fig_size = len(client_array)*1 + 4
            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=x_data_set,
                _xaxis_name="Latency (ms)",
                _yaxis_name="Devices",
                _yaxis_label = y_data_set,
                _yaxis_categories = y_data_set,
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=.20,
                _color_name = ["yellow","blue","orange","grey"],
                _show_bar_value=True,
                _figsize= (x_fig_size,y_fig_size),
                _graph_title="Audio Latency(sent/received)",
                _graph_image_name=f"Audio Latency(sent and received)",
                _label=["Max Sent","Min Sent","Max Recv","Min Recv"]
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            report.set_graph_image(graph_image)
            report.move_graph_image()
            report.build_graph()

            report.set_graph_title("Audio Jitter (Sent/Received)")
            report.build_graph_title()
            x_data_set = [max_audio_jitter_s.copy(),min_audio_jitter_s.copy(),max_audio_jitter_r.copy(),min_audio_jitter_r.copy()]
            y_data_set = client_array
            print(x_data_set)
            x_fig_size = 18
            y_fig_size = len(client_array)*1 + 4
            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=x_data_set,
                _xaxis_name="Jitter (ms)",
                _yaxis_name="Devices",
                _yaxis_label = y_data_set,
                _yaxis_categories = y_data_set,
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=.20,
                _color_name = ["yellow","blue","orange","grey"],
                _show_bar_value=True,
                _figsize= (x_fig_size,y_fig_size),
                _graph_title="Audio Jitter(sent/received)",
                _graph_image_name=f"Audio Jitter(sent and received)",
                _label=["Max Sent","Min Sent","Max Recv","Min Recv"]
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            report.set_graph_image(graph_image)
            report.move_graph_image()
            report.build_graph()


            report.set_graph_title("Audio Packet Loss (Sent/Received)")
            report.build_graph_title()
            x_data_set = [max_audio_pktloss_s.copy(),min_audio_pktloss_s.copy(),max_audio_pktloss_r.copy(),min_audio_pktloss_r.copy()]
            y_data_set = client_array
            print(x_data_set)
            x_fig_size = 18
            y_fig_size = len(client_array)*1 + 4
            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=x_data_set,
                _xaxis_name="Packet Loss (%)",
                _yaxis_name="Devices",
                _yaxis_label = y_data_set,
                _yaxis_categories = y_data_set,
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=.20,
                _color_name = ["yellow","blue","orange","grey"],
                _show_bar_value=True,
                _figsize= (x_fig_size,y_fig_size),
                _graph_title="Audio Packet Loss(sent/received)",
                _graph_image_name=f"Audio Packet Loss(sent and received)",
                _label=["Max Sent","Min Sent","Max Recv","Min Recv"]
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            report.set_graph_image(graph_image)
            report.move_graph_image()
            report.build_graph()


            report.set_table_title("Test Audio Results Table:")
            report.build_table_title()
            audio_test_details = pd.DataFrame({
                'Device Name': [client['hostname'] for client in accepted_clients],
                'Avg Latency Sent (ms)': [round(sum(data["audio_latency_s"])/len(data["audio_latency_s"]),2) if len(data["audio_latency_s"]) != 0 else 0 for data in final_dataset],
                'Avg Latency Recv (ms)': [round(sum(data["audio_latency_r"])/len(data["audio_latency_r"]),2) if len(data["audio_latency_r"]) != 0 else 0 for data in final_dataset],
                'Avg Jitter Sent (ms)': [round(sum(data["audio_jitter_s"])/len(data["audio_jitter_s"]),2) if len(data["audio_jitter_s"]) != 0 else 0 for data in final_dataset],
                'Avg Jitter Recv (ms)': [round(sum(data["audio_jitter_r"])/len(data["audio_jitter_r"]),2) if len(data["audio_jitter_r"]) != 0 else 0 for data in final_dataset],
                'Avg Pkt Loss Sent': [round(sum(data["audio_pktloss_s"])/len(data["audio_pktloss_s"]),2) if len(data["audio_pktloss_s"]) != 0 else 0 for data in final_dataset],
                'Avg Pkt Loss Recv': [round(sum(data["audio_pktloss_r"])/len(data["audio_pktloss_r"]),2) if len(data["audio_pktloss_r"]) != 0 else 0 for data in final_dataset],
                'CSV link': ['<a href="{}.csv" target="_blank">csv data</a>'.format(client['hostname'])  for client in accepted_clients]

            })
            report.set_table_dataframe(audio_test_details)
            report.dataframe_html = report.dataframe.to_html(index=False,
                                                     justify='center',render_links = True,escape=False)  # have the index be able to be passed in.
            report.html += report.dataframe_html
        if self.video:        
            report.set_graph_title("Video Latency (Sent/Received)")
            report.build_graph_title()
            x_data_set = [max_video_latency_s.copy(),min_video_latency_s.copy(),max_video_latency_r.copy(),min_video_latency_r.copy()]
            y_data_set = client_array
            x_fig_size = 18
            y_fig_size = len(client_array)*1 + 4
            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=x_data_set,
                _xaxis_name="Latency (ms)",
                _yaxis_name="Devices",
                _yaxis_label = y_data_set,
                _yaxis_categories = y_data_set,
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=.20,
                _color_name = ["yellow","blue","orange","grey"],
                _show_bar_value=True,
                _figsize= (x_fig_size,y_fig_size),
                _graph_title="Video Latency(sent/received)",
                _graph_image_name=f"Video Latency(sent and received)",
                _label=["Max Sent","Min Sent","Max Recv","Min Recv"]
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            report.set_graph_image(graph_image)
            report.move_graph_image()
            report.build_graph()

            report.set_graph_title("Video Jitter (Sent/Received)")
            report.build_graph_title()
            x_data_set = [max_video_jitter_s.copy(),min_video_jitter_s.copy(),max_video_jitter_r.copy(),min_video_jitter_r.copy()]
            y_data_set = client_array
            x_fig_size = 18
            y_fig_size = len(client_array)*1 + 4
            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=x_data_set,
                _xaxis_name="Jitter (ms)",
                _yaxis_name="Devices",
                _yaxis_label = y_data_set,
                _yaxis_categories = y_data_set,
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=.20,
                _color_name = ["yellow","blue","orange","grey"],
                _show_bar_value=True,
                _figsize= (x_fig_size,y_fig_size),
                _graph_title="Video Jitter(sent/received)",
                _graph_image_name=f"Video Jitter(sent and received)",
                _label=["Max Sent","Min Sent","Max Recv","Min Recv"]
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            report.set_graph_image(graph_image)
            report.move_graph_image()
            report.build_graph()

            report.set_graph_title("Video Packet Loss (Sent/Received)")
            report.build_graph_title()
            x_data_set = [max_video_pktloss_s.copy(),min_video_pktloss_s.copy(),max_video_pktloss_r.copy(),min_video_pktloss_r.copy()]
            y_data_set = client_array
            x_fig_size = 18
            y_fig_size = len(client_array)*1 + 4
            bar_graph_horizontal = lf_bar_graph_horizontal(
                _data_set=x_data_set,
                _xaxis_name="Packet Loss (%)",
                _yaxis_name="Devices",
                _yaxis_label = y_data_set,
                _yaxis_categories = y_data_set,
                _yaxis_step=1,
                _yticks_font=8,
                _bar_height=.20,
                _color_name = ["yellow","blue","orange","grey"],
                _show_bar_value=True,
                _figsize= (x_fig_size,y_fig_size),
                _graph_title="Video Packet Loss(sent/received)",
                _graph_image_name=f"Video Packet Loss(sent and received)",
                _label=["Max Sent","Min Sent","Max Recv","Min Recv"]
            )
            graph_image = bar_graph_horizontal.build_bar_graph_horizontal()
            report.set_graph_image(graph_image)
            report.move_graph_image()
            report.build_graph()

            report.set_table_title("Test Video Results Table:")
            report.build_table_title()
            video_test_details = pd.DataFrame({
                'Device Name': [client['hostname'] for client in accepted_clients],
                'Avg Latency Sent (ms)': [round(sum(data["video_latency_s"])/len(data["video_latency_s"]),2) if len(data["video_latency_s"]) != 0 else 0 for data in final_dataset],
                'Avg Latency Recv (ms)': [round(sum(data["video_latency_r"])/len(data["video_latency_r"]),2) if len(data["video_latency_r"]) != 0 else 0 for data in final_dataset],
                'Avg Jitter Sent (ms)': [round(sum(data["video_jitter_s"])/len(data["video_jitter_s"]),2) if len(data["video_jitter_s"]) != 0 else 0 for data in final_dataset],
                'Avg Jitter Recv (ms)': [round(sum(data["video_jitter_r"])/len(data["video_jitter_r"]),2) if len(data["video_jitter_r"]) != 0 else 0 for data in final_dataset],
                'Avg Pkt Loss Sent': [round(sum(data["video_pktloss_s"])/len(data["video_pktloss_s"]),2) if len(data["video_pktloss_s"]) != 0 else 0 for data in final_dataset],
                'Avg Pkt Loss Recv': [round(sum(data["video_pktloss_r"])/len(data["video_pktloss_r"]),2) if len(data["video_pktloss_r"]) != 0 else 0 for data in final_dataset],
                'CSV link': ['<a href="{}.csv" target="_blank">csv data</a>'.format(client['hostname'])  for client in accepted_clients]
            })
            report.set_table_dataframe(video_test_details)
            report.dataframe_html = report.dataframe.to_html(index=False,
                                                     justify='center',render_links = True,escape=False)  # have the index be able to be passed in.
            report.html += report.dataframe_html
            # report.build_table(render_links = True)
        report.set_custom_html("<br/><hr/>")
        report.build_custom()
        
        print(no_csv_client,"rejected")
        print(accepted_clients,"accepted")
        print(self.not_processed_clients,"auth error")
        
    
        html_file = report.write_html()
        print("returned file {}".format(html_file))
        print(html_file)
        # try other pdf formats
        # report.write_pdf()
        # report.write_pdf(_page_size = 'A3', _orientation='Landscape')
        # report.write_pdf(_page_size = 'A4', _orientation='Landscape')
        report.write_pdf(_page_size='Legal', _orientation='Landscape')
        # for client in self.clients:
        #     file_to_move_path = os.path.join(self.path, f'{client["hostname"]}.csv')
        #     print(file_to_move_path)
        #     self.move_files(file_to_move_path,report_path_date_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zoom Automation Script")
    parser.add_argument('--duration', type=int, required=True, help="Duration of the Zoom meeting in minutes")
    parser.add_argument('--lanforge_ip', type=str, required=True, help="LANforge IP address")
    parser.add_argument('--sigin_email', type=str, required=True, help="Sign-in email")
    parser.add_argument('--sigin_passwd', type=str, required=True, help="Sign-in password")
    parser.add_argument('--participants', type=int, required=True, help="no of participanrs")
    parser.add_argument('--audio',action='store_true')
    parser.add_argument('--video',action='store_true')
    parser.add_argument("--wait_time",type=int,default=30,help='time set to wait for the csv files')




    args = parser.parse_args()
    
    automation = ZoomAutomation(audio=args.audio, video=args.video, lanforge_ip=args.lanforge_ip,duration=args.duration,sigin_email= args.sigin_email,sigin_passwd = args.sigin_passwd,participants= args.participants,wait_time=args.wait_time)
    automation.run()

