import requests
import time
import os
import sys
import pandas as pd
import importlib
import shlex
import subprocess
import json
import subprocess
import argparse
import pdfkit
import lf_report

from lf_we_can_wifi_capacity import WeCanWiFiCapacityTest
from lf_we_can_wifi_capacity import LfInteropWifiCapacity

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
base = importlib.import_module('py-scripts.lf_base_interop_profile')
lf_report = importlib.import_module("py-scripts.lf_report")
lf_report = lf_report.lf_report
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_bar_graph = lf_graph.lf_bar_graph
lf_scatter_graph = lf_graph.lf_scatter_graph
lf_stacked_graph = lf_graph.lf_stacked_graph
lf_horizontal_stacked_graph = lf_graph.lf_horizontal_stacked_graph
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm


class RDT(Realm):
    def __init__(self,
                 lfclient_host="localhost",
                 lf_port=8080,
                 ssh_port=22,
                 ssid='RDT_test',
                 passkey='sharedsecret',
                 security='wpa2',
                 lf_user="lanforge",
                 lf_password="lanforge",
                 instance_name="wct_instance",
                 config_name="wifi_config",
                 upstream="eth1",
                 batch_size="1",
                 loop_iter="1",
                 protocol="TCP-IPv4",
                 duration="15000",
                 pull_report=False,
                 load_old_cfg=False,
                 upload_rate="10Mbps",
                 download_rate="0bps",
                 sort="interleave",
                 stations="",
                 create_stations=False,
                 enables=None,
                 disables=None,
                 raw_lines=None,
                 raw_lines_file="",
                 sets=None,
                 influx_lfclient_host="locallfclient_host",
                 influx_port=8086,
                 report_dir="",
                 graph_groups=None,
                 test_rig="",
                 test_tag="",
                 local_lf_report_dir=""
                 ):
        super().__init__(lfclient_host=lfclient_host, lfclient_port=lf_port)

        if enables is None:
            enables = []
        if disables is None:
            disables = []
        if raw_lines is None:
            raw_lines = []
        if sets is None:
            sets = []
        self.lfclient_host = lfclient_host
        self.lf_port = lf_port
        self.lf_user = lf_user
        self.lf_password = lf_password
        self.ssid=ssid
        self.passkey=passkey
        self.security=security
        self.station_profile = self.new_station_profile()
        self.pull_report = pull_report
        self.load_old_cfg = load_old_cfg
        self.instance_name = instance_name
        self.config_name = config_name
        self.test_name = "WiFi Capacity"
        self.batch_size = batch_size
        self.loop_iter = loop_iter
        self.protocol = protocol
        self.duration = duration
        self.upload_rate = upload_rate
        self.download_rate = download_rate
        self.upstream = upstream
        self.sort = sort
        self.stations = stations
        self.create_stations = create_stations
        self.ssh_port = ssh_port
        self.enables = enables
        self.disables = disables
        self.raw_lines = raw_lines
        self.raw_lines_file = raw_lines_file
        self.sets = sets
        self.influx_lfclient_host = influx_lfclient_host,
        self.influx_port = influx_port
        self.report_dir = report_dir
        self.graph_groups = graph_groups
        self.test_rig = test_rig
        self.test_tag = test_tag
        self.local_lf_report_dir = local_lf_report_dir
        self.lf_query_cx = self.json_get("/cx/all")
        self.lf_query_endps=self.json_get("/endp")
        self.lf_query_ports = self.json_get("/port/all")
        self.adb_devices=[]
        self.interop = base.BaseInteropWifi(manager_ip=self.lfclient_host,
                                            port=self.lf_port,            
                                            ssid=self.ssid,
                                            passwd=self.passkey,
                                            encryption=self.security,    
                                            screen_size_prcnt = 0.4,
                                            _debug_on=False,
                                            _exit_on_error=False)

    def isoffline(self,host):
        comd=subprocess.Popen('ping '+host+' -w 250 -n 1',shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out,err =comd.communicate()
        string=out.decode('utf-8')
        x=string.split()
        #print(x)
        if x[x.index('data:')+1]=='Request' or x[x.index('data:')+4]=='Destination':
            #print('Skip IP and continue to next')
            return 1
            
        else:
            comd=subprocess.Popen('ping '+host+' -w 500 -n 1',shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            out,err =comd.communicate()
            string=out.decode('utf-8')
            x=string.split()
            #print(x)
            if x[x.index('data:')+1]=='Request' or x[x.index('data:')+4]=='Destination':
                #print('Skip IP and continue to next')
                return 1
            else:
                comd=subprocess.Popen('ping '+host+' -w 1000 -n 1',shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                out,err =comd.communicate()
                string=out.decode('utf-8')
                x=string.split()
                if x[x.index('data:')+1]=='Request' or x[x.index('data:')+4]=='Destination':
                    #print('Skip IP and continue to next')
                    return 1
                else:
                    time.sleep(0.1)
                    return 0

    def AP_ping_probe(self,aphosts):
        for x,y in aphosts.items():
            self.AP_status(apname=x,aphost=y)            
            # print("ping ",y)
        return "SUCCESS"           
    
    def AP_status(self,apname,aphost):
        response=self.isoffline(host=str(aphost))
        #print(response)
        if response == 0:
            pingstatus = "Network Active"
            ap=apname+'{'
            status='background-color:rgb(0, 221, 18);'
        else:
            pingstatus = "Network Error"
            ap=apname+'{'
            status='background-color:rgb(235, 62, 62);'

        html=f'''

        .{ap}
            
            border-color: rgb(0, 0, 0);
            border-style:solid;
            -webkit-border-radius:55px;
            border-width: 3px; 
            {status}   
        ''''''}
        '''

        with open(apname+".css","w") as html_file:
            
            html_file.write(html)
            print("Color status of", apname," is reported to UI")
            
    def ap_list(self,file_path):
        ap_data=None
        with pd.ExcelFile(file_path) as xls:
            obtained_data = pd.read_excel(xls, 'Sheet1')
            ap_data=dict(zip(obtained_data['AP'].values.tolist(),obtained_data['API'].values.tolist()))
            ap_host=dict(zip(obtained_data['AP'].values.tolist(),obtained_data['IP'].values.tolist()))
        return ap_data,ap_host

    def ap_up(self,api):
        print("http attempt ",api, " Waiting for AP to complete boot ")
        x = requests.get(api)
        print(x)
        time.sleep(90)
        return True

    def ap_down(self,api):
        print("http attempt ",api)
        x = requests.get(api)
        print(x)
        time.sleep(1)
        return True
 
    def get_last_wifi_msg(self):
        cmd = '''curl -H 'Accept: application/json' http://''' + str(self.lfclient_host) + ''':8080/wifi-msgs/last/7'''
        args = shlex.split(cmd)
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output = json.loads((stdout.decode("utf-8")))

        print("Output is ",output['wifi-messages'])
        if output['wifi-messages']==[]:
            last=None
        else:
            last = output['wifi-messages']['time-stamp']
        print("timestamp is, ",last)
        return last
    
    def restart_wifi(self,device):
        if(device==None):
            return False
        else:
            self.interop.enable_or_disable_wifi(device=device, wifi="disable")
            time.sleep(1)
            self.interop.enable_or_disable_wifi(device=device, wifi="enable")
            time.sleep(2)
            return True

    def get_time_from_wifi_msgs(self, local_dict=None, phn_name=None):
        time.sleep(6)
        timee = self.get_last_wifi_msg()
        a = self.json_get("/wifi-msgs/since=time/" + str(timee), debug_=True)
        print(a)
        values = a['wifi-messages']
        print("values", values)
        keys_list = []
        for i in range(len(values)):
            keys_list.append(list(values[i].keys())[0])

        disconnect_count = self.get_count(value=values, keys_list=keys_list, filter="Terminating...")
        print(disconnect_count)

        print(local_dict[phn_name])
        local_dict[phn_name]["Disconnected"] = disconnect_count
        print(local_dict[phn_name])
        print(local_dict)

        scan_count = self.get_count(value=values, keys_list=keys_list, filter="SCAN_STARTED")
        print(scan_count)
        local_dict[str(phn_name)]["Scanning"] = scan_count
        association_attempt = self.get_count(value=values, keys_list=keys_list, filter="ASSOCIATING")
        print(association_attempt)
        local_dict[str(phn_name)]["ConnectAttempt"] = association_attempt
        conected_count = self.get_count(value=values, keys_list=keys_list, filter="CTRL-EVENT-CONNECTED")
        print("conected_count", conected_count)
        local_dict[str(phn_name)]["Connected"] = conected_count
        assorej_count = self.get_count(value=values, keys_list=keys_list, filter="ASSOC_REJECT")
        print("asso rej", assorej_count)
        local_dict[str(phn_name)][ "Association Rejection"] = assorej_count
        print("local_dict", local_dict)
        return local_dict

    def client_connectivity_time(self):
        cmd = '''curl -H 'Accept: application/json' http://''' + str(self.lfclient_host) + ''':8080/adb/'''
        args = shlex.split(cmd)
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output = (stdout.decode("utf-8"))
        out = json.loads(output)
        final = out["devices"]
        value = []
        if type(final) == list:
            # print(len(final))
            keys_lst = []
            for i in range(len(final)):
                keys_lst.append(list(final[i].keys())[0])
            # print(keys_lst)
            for i, j in zip(range(len(keys_lst)), keys_lst):
                value.append(final[i][j]["name"])
        else:
            #  only one device is present
            value.append(final["name"])
        self.supported_devices_names = value
        self.restart_wifi(device=self.supported_devices_names[0])
        print(self.get_time_from_wifi_msgs())
        # return '100ms'
    def deviceName(self):
        cmd = '''curl -H 'Accept: application/json' http://''' + str(self.lfclient_host) + ''':8080/adb/'''
        args = shlex.split(cmd)
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output = (stdout.decode("utf-8"))
        out = json.loads(output)
        if out['devices']==[]:
            return None
        elif out["devices"]['phantom']==False:
            final = out["devices"]['name']
            return final
    
    def force_ssid(self,ssid,devices):
        user_list = []
        for i in devices:
            name = self.interop.get_device_details(query='user-name', device=i)
            user_list.append(name)

        for i, x in zip(user_list, devices):
            user_name = i
            if not user_name:
                raise ValueError("please specify a user-name when configuring this Interop device")
            cmd = "shell am start -n com.candela.wecan/com.candela.wecan.StartupActivity "
            cmd += "--es auto_start 1 --es username " + user_name
            if self.lfclient_host:
                cmd += " --es serverip " + self.lfclient_host
            if self.ssid:
                cmd += " --es ssid " + ssid
            if self.passkey:
                cmd += "--es password " + self.passkey
            if self.encryption:
                cmd += " --es encryption " + self.encryption
            self.interop.post_adb_(device=x, cmd=cmd)

        return True

    def cleanup_cx(self):
        print("\nCleaning up Layer-3 tab\n------------------------------------")
        lf_query_cx = self.json_get("/cx/all")
        lf_query_endps=self.json_get('/endp')
        if 'empty' in list(lf_query_cx)[2]:
            print('CX-connects does not exist!')
        else:
            # print('cx connects exist')
            for j in range(len(list(lf_query_cx))):
                for i in [lf_query_cx]:
                    if 'handler'!=list(i)[j] and 'uri' != list(i)[j]:
                        cx_name=list(i)[j]  
                        # temp=i.get(list(i)[j])
                        # print(cx_name+' is in stop state:-','Stopped' in temp.get('state'))
                        # if 'Stopped' or 'PHANTOM' in temp.get('state'):
                        if True:
                            req_url = "cli-json/rm_cx"
                            data = {
                                "test_mgr": "default_tm",
                                "cx_name": cx_name
                            }
                            print('Cleaning ',cx_name,' cross connect...')
                            self.json_post(req_url, data)
                            #time.sleep(1)
                            #clearing associated endps
                            endp=lf_query_endps["endpoint"]
                            for id in range(len(endp)):
                                endp=lf_query_endps["endpoint"][id]
                                if [cx_name+'-A']==list(endp) or [cx_name+'-B']==list(endp):
                                    req_url = "cli-json/rm_endp"
                                    data = {
                                    "endp_name": list(endp)[0]
                                    }
                                    self.json_post(req_url, data)
                                    print('Deleting ',list(endp)[0],'...')
        return True
                        
    def getData(self):
        get = LfInteropWifiCapacity(host=self.lfclient_host, port=self.lf_port, protocol=self.protocol,
                                    batch_size=self.batch_size, duration=self.duration, dut_model='test_dut',
                                    inp_download_rate=self.download_rate, inp_upload_rate=self.upload_rate,
                                    ssid_dut_2g='ssid_dut_2g', ssid_dut_5g='ssid_dut_5g')
        resource_id_real, phone_name, mac_address, user_name, phone_radio, rx_rate, tx_rate, signal, ssid, channel, phone_radio_bandwidth \
            = get.get_resource_data()

        folder_directory = get.get_folder_name()
        rx_rate = [(i.split(" ")[0]) if (i.split(" ")[0]) != '' else '0' for i in rx_rate]
        tx_rate = [(i.split(" ")[0]) if (i.split(" ")[0]) != '' else '0' for i in tx_rate]
        print(resource_id_real, "\n", phone_name, "\n", mac_address, "\n", user_name, "\n", phone_radio,
              "\n", rx_rate, "\n", tx_rate)
        dataframe = pd.read_csv(folder_directory + "/csv-data/data-Combined_Mbps__60_second_running_average-1.csv",
                                header=1)

        print(dataframe)
        # data=dataframe.values.tolist()
        return dataframe,signal
  
    def run(self):
        upload=0
        download=0
        Test = WeCanWiFiCapacityTest(lfclient_host=self.lfclient_host,
                                     lf_port=self.lf_port,
                                     ssh_port=self.ssh_port,
                                     lf_user=self.lf_user,
                                     lf_password=self.lf_password,
                                     upstream=self.upstream,
                                     upload_rate=self.upload_rate,
                                     download_rate=self.download_rate,
                                     batch_size=self.batch_size,
                                     protocol=self.protocol,
                                     duration=self.duration,
                                     pull_report=True,
                                     )
        Test.setup()
        Test.run()
        x,rssi=self.getData()
        for m,n in x.items():
            print("upload value is ",n[1])
            upload=n[1]
            print("Download val is ",n[0])
            download=n[0]
            break     
        # print(x,"type(x) is",type(x))
        return upload,download,rssi[0]
        
    def wct_trigger(self):
            self.restart_wifi(device=self.deviceName())
            time.sleep(1)
            upload,download,rssi=self.run()
            print(self.protocol," test completed! attempting the consequent test")
            return [upload,download,rssi]



    def generate_report(self,data,Ap_names,rssi,udp_actual_data,tcp_actual_data,tcp_expected_data,udp_expected_data):
        report = lf_report()
        report_path = report.get_path()
        report_path_date_time = report.get_path_date_time()
        report.set_title("Report for:Real Device Test on Station")
        report.build_banner()
        report.set_text("<h3 style='padding-left: 150px;'>Scenario name:"+  test_scenario_name)
        report.build_text()
        report.set_text(
            "<h3 style='padding-left: 150px;'>Test Objective:" + "<h5 style='text-align: justify;padding-left: 150px;'>The purpose of this test plan is to evaluate the basic client connectivity and throughput of a WLAN station across 30 access points (APs). ")
        report.build_text()
        report.set_text(
            "<h3 style='padding-left: 150px;'>Pre-Requisites:" + "<h5 style='text-align: justify;padding-left: 150px;'>1. 20+ APs configured with the same configuration (SSID, Password, channel, and bandwidth for both bands).")
        report.build_text()
        report.set_text(
            "<h3 style='padding-left: 150px;'>Test Procedure:" + "<h5 style='text-align: justify; padding-left: 150px; line-height: 1.8;'>1.Using automation power on only one AP at a time.<br>"
                            " 2. Connect the Station using automation to AP SSID, while connecting to AP SSID record the below values from the script.<br>"
                            " &nbsp;&nbsp; i. Time is taken from Authentication to Association (Later we have to plot a graph using these values)<br>"
                            "3. Once STA gets an IP address from the script, trigger Wi-Fi Capacity or Data Plane test and execute the test cases below.<br>"
                            " &nbsp;&nbsp; i. Run TCP- DL traffic with an intended load of 1 Gbps between the AP upstream port and 2.4 GHz client and record the below values<br>"
                            )
        report.build_text()
        ### TO PRINT DATA IN TABULAR FORM, UN-COMMENT THE FOLLOWING SECTION
        # report.set_text("Below graph contains RSSI value of a real device with Multiple AP's")
        # report.build_text()
        # dataframemain = pd.DataFrame({
        #     'station': [1, 2, 3, 4, 5, 6, 7],
        #     'time_seconds': [23, 78, 22, 19, 45, 22, 25]
        # })
        # report.set_table_title("Table based on RSSI values")
        # report.build_table_title()
        # dataframe2 = pd.DataFrame({
        #     'Access points': ["AP1","AP2","AP3","AP4", "AP5"],
        #     'RSSI Values': [23, 38, 22, 19, 45]
        # })
        # report.set_table_dataframe(dataframe2)
        # report.build_table()
        # # # APList= ["1","2","3","4", "5","6","7","8","9", "10","11","12","13","14", "15","16","17","18","19", "20","21","22","23","24", "25","26","27","28","29", "30"]
        APList=Ap_names
        # # # Rssi = [23, 38, 22, 19, 45,23, 38, 22, 19, 45,56,34,89,24,67, 19, 45,23, 38, 22,45,56,34,89,24,45,23, 38, 22,45 ]
        Rssi=rssi
        # test lf_graph in report
        datasety = [Rssi]
        x_axis_valuess = APList

        report.set_graph_title("RSSI Graph")
        report.build_graph_title()

        graph = lf_bar_graph(_data_set=datasety,
                            _xaxis_name="Access Points",
                            _yaxis_name="RSSI(dbm)",
                            _xaxis_categories=x_axis_valuess,
                            _graph_image_name="Bi-single_radio_2.4GHz",
                            _label=["RSSI"],
                            _color=['darkorange', 'forestgreen', 'blueviolet'],
                            _color_edge='red',
                            # _grp_title="RSSI Acheived",
                            _xaxis_step=1,
                            _show_bar_value=True,
                            _text_font=7,
                            _text_rotation=45,
                            _xticks_font=7,
                            _legend_loc="best",
                            _legend_box=(1, 1),
                            _legend_ncol=1,
                            _legend_fontsize=None,
                            _enable_csv=False)

        graph_png1 = graph.build_bar_graph()

        print("graph name {}".format(graph_png1))

        report.set_graph_image(graph_png1)
        # need to move the graph image to the results
        report.move_graph_image()
        if graph.enable_csv:
            report.set_csv_filename(graph_png1)
            report.move_csv_file()
        report.build_graph()

        ### Tabular form for stacked(2.4)
        # report.set_table_title("Table based on Throughput values(2.4Ghz)")
        # report.build_table_title()
        # dataframe3 = pd.DataFrame({
        #     'Access points': ["AP1","AP2","AP3","AP4", "AP5"],
        #     'Expected Values': [23, 67, 23, 12,33],
        #     'Actual Values': [12, 45, 67, 34,56]
        #
        # })
        # report.set_table_dataframe(dataframe3)
        # report.build_table()
    # stacked graph to plot throughput graphs(2.4Ghz)
        if(tcp_actual_data!=[]):
            report.set_graph_title("TCP Throughput Graph")
            report.build_graph_title()

        # # # TCP_Throughput = [["1","2","3","4", "5","6","7","8","9", "10","11","12","13","14", "15","16","17","18","19", "20","21","22","23","24", "25","26","27","28","29", "30"], [23, 38, 22, 19, 45,23, 38, 22, 19, 45,56,34,89,24,67, 19, 45,23, 38, 22,45,56,34,89,24,45,23, 38, 22,45 ],
                # # # [32, 48, 27, 29, 11,53, 28, 21, 23, 41,50,40,12,34,47, 29, 55,33, 18, 62,25,46,24,59,24,41,33, 18, 32,55 ]]
            tem=[]
            for m,n in zip(tcp_expected_data,tcp_actual_data):
                tem.append(m-n)
            tcp_expected_data=tem
            TCP_Throughput=[Ap_names,tcp_actual_data,tcp_expected_data]
            graph1 = lf_stacked_graph(_data_set=TCP_Throughput,
                                    _xaxis_name="Access Points",
                                    _yaxis_name="Throughput(Mbps)",
                                    _label=[ 'Actual throughput','Expected throughput','both'],
                                    _graph_image_name="login_pass_fail",
                                    _color=['#149ef5','#11d4b6'],
                                    _enable_csv=False)

            graph_png1 = graph1.build_stacked_graph()

            print("graph name {}".format(graph_png1))

            report.set_graph_image(graph_png1)
            report.move_graph_image()
            report.build_graph()

    #stacked new
        # report.set_table_title("Table based on Throughput values(5Ghz)")
        # report.build_table_title()
        # dataframe4 = pd.DataFrame({
        #     'Access points': ["AP1","AP2","AP3","AP4", "AP5"],
        #     'Expected Values': [11, 24, 56, 56,31],
        #     'Actual Values': [12, 45, 67, 34,56]
        #
        # })
        # report.set_table_dataframe(dataframe4)
        # report.build_table()

    # stacked graph to plot throughput graphs(5Ghz)
        if(udp_actual_data!=[]):
            report.set_graph_title("UDP Throughput Graph")
            report.build_graph_title()

            # # # Throughput5G= [["1","2","3","4", "5","6","7","8","9", "10","11","12","13","14", "15","16","17","18","19", "20","21","22","23","24", "25","26","27","28","29", "30"], [32, 48, 27, 29, 11,53, 28, 21, 23, 41,50,40,12,34,47, 29, 55,33, 18, 62,25,46,24,59,24,41,33, 18, 32,55 ],
            # # #         [32, 48, 27, 29, 11,53, 28, 21, 23, 41,50,40,12,34,47, 29, 55,33, 18, 62,25,46,24,59,24,41,33, 18, 32,55 ]]
            tem=[]
            for m,n in zip(udp_expected_data,udp_actual_data):
                tem.append(m-n)
            udp_expected_data=tem
            UDP_Throughput=[Ap_names,udp_actual_data,udp_expected_data]
            graph1 = lf_stacked_graph(_data_set=UDP_Throughput,
                                    _xaxis_name="Access Points",
                                    _yaxis_name="Throughput(Mbps)",
                                    _label=['Actual throughput','Expected throughput','both'],
                                    _graph_image_name="login_pass",
                                    _color=['#149ef5','#11d4b6'],
                                    _enable_csv=False)

            graph_png = graph1.build_stacked_graph()

            print("graph name {}".format(graph_png))

            report.set_graph_image(graph_png)
            report.move_graph_image()
            report.build_graph()

    #Client connect time Graph table------------------------------------------------------
        # report.set_table_title("Table based on Client Connect Time values")
        # report.build_table_title()
        # dataframe8 = pd.DataFrame({
        #     'Access points': ["AP1","AP2","AP3","AP4", "AP5","AP6","AP7","AP8","AP9", "AP10","AP11","AP12","AP13","AP14", "AP15","AP16","AP17","AP18","AP19", "AP20","AP21","AP22","AP23","AP24", "AP25","AP26","AP27","AP28","AP29", "AP30"],
        #     'Time': [32, 48, 27, 29, 11,53, 28, 21, 23, 41,50,40,12,34,47, 29, 55,33, 18, 62,25,46,24,59,24,41,33, 18, 32,55 ]
        # })
        # report.set_table_dataframe(dataframe8)
        # report.build_table()

    # Client connect time Graph------------------------------------------------------

        Ap_list = ["1","2","3","4", "5","6","7","8","9", "10","11","12","13","14", "15","16","17","18","19", "20","21","22","23","24", "25","26","27","28","29", "30"]
        Client_connect = [32, 48, 27, 29, 11,53, 28, 21, 23, 41,50,40,12,34,47, 29, 55,33, 18, 62,25,46,24,59,24,41,33, 18, 32,55 ]
        dataset2 = [Client_connect]
        x_axis_values2 = Ap_list

        report.set_graph_title("Client-connectivity time Graph")
        report.build_graph_title()

        graph2 = lf_bar_graph(_data_set=dataset2,
                            _xaxis_name="Access Points",
                            _yaxis_name="Time(in seconds)",
                            _xaxis_categories=x_axis_values2,
                            _graph_image_name="Client_connect_time_graph",
                            _label=["Client connect time"],
                            _color=['darkorange', 'forestgreen', 'blueviolet'],
                            _color_edge='red',
                            # _grp_title="Client Connect Time",
                            _xaxis_step=1,
                            _show_bar_value=True,
                            _text_font=7,
                            _text_rotation=45,
                            _xticks_font=7,
                            _legend_loc="best",
                            _legend_box=(1, 1),
                            _legend_ncol=1,
                            _legend_fontsize=None,
                            _enable_csv=False)

        graph_png = graph2.build_bar_graph()

        print("graph name {}".format(graph_png))

        report.set_graph_image(graph_png)
        # need to move the graph image to the results
        report.move_graph_image()
        if graph.enable_csv:
            report.set_csv_filename(graph_png)
            report.move_csv_file()
        report.build_graph() 

    #to print DUT information in tabular form:

            # print('\n\n\nInitiated the ', y)
            
        Lanforge_type=data['Traffic Generator']
        Lanforge_version=data['Lanforge-version']
        Lanforge_kernal=data['Kernal-version']
        dut_type=data['DUT_type']
        dut_version=data['Android Version']
        dut_radio_spec=data['DUT_spec']
        report_name=data['report_name']

        report.set_table_title("DUT information")
        report.build_table_title()
        DUT_info = pd.DataFrame({
            'DUT Type': dut_type,
            'Android version': dut_version,
            'DUT Specification':dut_radio_spec
        },index=[0])
        report.set_table_dataframe(DUT_info)
        report.build_table()

        report.set_table_title("Traffic Generator information")
        report.build_table_title()
        TG_info = pd.DataFrame({
            'Lanforge type': Lanforge_type,
            'build version': Lanforge_version,
            'Kernal Version':Lanforge_kernal
        },index=[0])
        report.set_table_dataframe(TG_info)
        report.build_table()


        # DUT_info_transposed = DUT_info.T
        # DUT_info_transposed
        # print(DUT_info_transposed)
        # report.set_table_dataframe(DUT_info_transposed)
        # report.build_table()



        html_file = report.write_html()
        path = "{}".format(html_file)
        print("Path of the saved file:",path)
        # Path = path
        # final = os.path.basename(Path).split('/')[-1]
        # print(os.path.basename(Path).split('/')[-1])
        print(html_file)
        # pdf_file = report.write_pdf()
        # path1 = "return file {}".format(pdf_file)
        #
        # pdfkit.from_file(path, report_name)

        return None

                 
def main():
    description = """ RDT station testing 
    run: RDT.py --config <directory of test configuration json file>
    """
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description=description)

    parser.add_argument("--config", "--test_configuration", default='./RDT_config.json',
                        help='specify the file directory of test configuration')

    
    args = parser.parse_args()
    df = pd.read_json(args.config)

    for x,y in df.items():
        if x == 'traffic-generator-config':
            mgr_ip=df['traffic-generator-config']['manager-ip']
            port=df['traffic-generator-config']['port']
            upstream=df['traffic-generator-config']['upstream']  
            Lanforge_type=df['traffic-generator-config']['Traffic Generator']
            Lanforge_version=df['traffic-generator-config']['Lanforge-version']
            Lanforge_kernal=df['traffic-generator-config']['Kernal-version']
            dut_type=df['traffic-generator-config']['DUT_type']
            dut_version=df['traffic-generator-config']['Android Version']
            dut_radio_spec=df['traffic-generator-config']['DUT_spec']
            data={
                'Traffic Generator':Lanforge_type,
                'Lanforge-version':Lanforge_version,
                'Kernal-version':Lanforge_kernal,
                'DUT_type':dut_type,
                'Android Version':dut_version,
                'DUT_spec':dut_radio_spec

            }        
        Instance=RDT(lfclient_host=mgr_ip)
        # data['report_name']='my_report'    
        # Instance.generate_report(data=data,tcp_actual_data=[],udp_actual_data=[90,70],rssi=[20,30],Ap_names=["1","2"],expected_data=[100,100])  
        # exit()
        if x != 'traffic-generator-config':
            tcp_up_throughput=[]
            udp_up_throughput=[]
            tcp_dn_throughput=[]
            udp_dn_throughput=[]
            expected_tcp=[]
            expected_udp=[]
            AP_names_list=[]
            Rssi_TCP=[]
            Rssi_UDP=[]
            client_connect_time=[]
            print('\n\n\nInitiated the ',x,'\n==============================================\n')
            ap_batch_location=df[x]['AP_batch_location']
            aps,ap_hosts=Instance.ap_list(file_path=ap_batch_location)
            probe_status=Instance.AP_ping_probe(aphosts=ap_hosts)
            print("Probing process is ",probe_status,'!')
            for i,j in aps.items():
                Instance.cleanup_cx()
                print("\n\nTest initiated with ",i,'...\n---------------------------------------------------')
                Instance.ap_up(api=str(j)+'on')
                AP_names_list.append(i)
                Instance.AP_status(apname=i,aphost=ap_hosts[i])
                print(i,' is turned on, attempting test from ',args.config,'\n--------------------------------------------------------------------------------------')

                if(df[x]['TCP'] is True):
                    expected_tcp.append(int(df[x]['Upload-rate'].replace("Mbps", ""))+int(df[x]['Download-rate'].replace("Mbps", "")))
                    Test_instance=RDT(lfclient_host=mgr_ip,lf_port=port,upstream=upstream,upload_rate=df[x]['Upload-rate'],download_rate=df[x]['Download-rate'],duration=df[x]['Test-duration'],protocol='TCP-IPv4')
                    print("triggering TCP test")
                    test=Test_instance.wct_trigger()
                    tcp_up_throughput.append(test[0])
                    expected_tcp
                    tcp_dn_throughput.append(test[1])
                    Rssi_TCP.append(int(test[2])*-1)
                if(df[x]['UDP'] is True):
                    expected_udp.append(int(df[x]['Upload-rate'].replace("Mbps", ""))+int(df[x]['Download-rate'].replace("Mbps", "")))
                    Test_instance=RDT(lfclient_host=mgr_ip,lf_port=port,upstream=upstream,upload_rate=df[x]['Upload-rate'],download_rate=df[x]['Download-rate'],duration=df[x]['Test-duration'],protocol='UDP-IPv4')
                    print("triggering UDP test")
                    test=Test_instance.wct_trigger()
                    udp_up_throughput.append(test[0])
                    udp_dn_throughput.append(test[1])
                    print("test 0,1,2 ",test[0],test[1],test[2])
                    Rssi_UDP.append(int(test[2])*-1)
                print("Tests completed with ",i,"\n attempting to turn it down ")
                Instance.ap_down(api=str(j)+'off')
                time.sleep(0.5)
                Instance.AP_status(apname=i,aphost=ap_hosts[i])
                print(i,' is turned off, attempting to swap ap and start test from test config.json')
            print("TCP dn",tcp_dn_throughput)
            print("UDP dn",udp_dn_throughput)
            print("TCP up",tcp_up_throughput)
            print("UDP up",udp_up_throughput)
            print("RSSI ",Rssi_UDP)

            data['report_name']=x
            Instance.generate_report(data=data,tcp                              _actual_data=tcp_dn_throughput,udp_actual_data=udp_dn_throughput,rssi=Rssi_UDP,Ap_names=AP_names_list,udp_expected_data=expected_udp,tcp_expected_data=expected_tcp)
            print('\n \n \n Completed the ',x,'\n=========================================')


if __name__ == '__main__':
    main()