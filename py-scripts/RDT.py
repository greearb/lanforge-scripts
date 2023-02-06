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

from lf_we_can_wifi_capacity import WeCanWiFiCapacityTest
from lf_we_can_wifi_capacity import LfInteropWifiCapacity

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
base = importlib.import_module('py-scripts.lf_base_interop_profile')


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
        comd=subprocess.Popen('ping '+host+' -w 1000 -n 1',shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE)
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
        print("\n Ok...now validating Layer-3 CX \n")
        lf_query_cx = self.json_get("/cx/all")
        lf_query_endps=self.json_get('/endp')
        print(list(lf_query_cx)[2])
        if 'empty' in list(lf_query_cx)[2]:
            print('cx connects do not exist')
        else:
            print('cx connects exist')
            for j in range(len(list(lf_query_cx))):
                for i in [lf_query_cx]:
                    if 'handler'!=list(i)[j] and 'uri' != list(i)[j]:
                        cx_name=list(i)[j]  
                        temp=i.get(list(i)[j])
                        print(cx_name+' is in stop state:-','Stopped' in temp.get('state'))

                        # if 'Stopped' or 'PHANTOM' in temp.get('state'):
                        if True:
                            req_url = "cli-json/rm_cx"
                            data = {
                                "test_mgr": "default_tm",
                                "cx_name": cx_name
                            }
                            print('Cleaning ',cx_name,' cross connect')
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
                                    print('Delete ',list(endp)[0])
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
        dataframe.values.tolist()

        return dataframe
    def run(self):
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
        self.getData()

    def wct_trigger(self):
            self.restart_wifi(device=self.deviceName())
            time.sleep(1)
            self.run()
            print(self.protocol," test completed! attempting the consequent test")
            

df = pd.read_json(r"c:/Users/CTINDLAP43/Documents/scripts/lanforge-scripts/py-scripts/practice.json")

for x,y in df.items():
    print('\n\n\nInitiated the ',y)
    if x == 'traffic-generator-config':
        mgr_ip=df['traffic-generator-config']['manager-ip']
        port=df['traffic-generator-config']['port']
        upstream=df['traffic-generator-config']['upstream']
    Instance=RDT(lfclient_host=mgr_ip)
    aps,ap_hosts=Instance.ap_list(file_path='C:/Users/CTINDLAP43/Desktop/TEST_APs.xlsx')
    if x != 'traffic-generator-config':
        for i,j in aps.items():
            Instance.cleanup_cx()
            print("Test initiated with ",i)
            Instance.ap_up(api=str(j)+'on')
            Instance.AP_status(apname=i,aphost=ap_hosts[i])
            print(i,' is turned on, attempting test from test config.json')
            if(df[x]['TCP'] is True):
                Test_instance=RDT(lfclient_host=mgr_ip,lf_port=port,upstream=upstream,upload_rate=df[x]['Upload-rate'],download_rate=df[x]['Download-rate'],duration=df[x]['Test-duration'],protocol='TCP-IPv4')
                print("triggering TCP test")
                Test_instance.wct_trigger()
            if(df[x]['UDP'] is True):
                Test_instance=RDT(lfclient_host=mgr_ip,lf_port=port,upstream=upstream,upload_rate=df[x]['Upload-rate'],download_rate=df[x]['Download-rate'],duration=df[x]['Test-duration'],protocol='UDP-IPv4')
                print("triggering UDP test")
                Test_instance.wct_trigger()
            print("Tests completed with ",i,"\n attempting to turn it down ")
            Instance.ap_down(api=str(j)+'off')
            time.sleep(0.5)
            Instance.AP_status(apname=i,aphost=ap_hosts[i])
            print(i,' is turned off, attempting to swap ap and start test from test config.json')
    print('\n \n \n Completed the ',y)



