"""
This script will create 40 clients on 5Ghz , 2.4Ghz and Both and generate layer4 traffic on LANforge ,The Webpage Download Test is designed to test the performance of the  Access Point.The goal is to  check whether the
webpage loading time meets the expectation when clients connected on single radio as well as dual radio.

how to run -
sudo python3 web.py --upstream_port eth1 --num_stations 40 --security open --ssid ASUSAP --passwd [BLANK] --target_per_ten 1 --bands 5G  --file_size 10Mb  --fiveg_radio wiphy0 --twog_radio wiphy1 --duration 1
Copyright 2021 Candela Technologies Inc
04 - April - 2021
"""

import sys
import time
import paramiko
import argparse

if 'py-json' not in sys.path:
    sys.path.append('../py-json')
from LANforge import LFUtils
from LANforge import lfcli_base
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
import realm
from realm import Realm
from realm import PortUtils

from webpage_report import *
from lf_report import *
from lf_graph import *

class HttpDownload(Realm):
    def __init__(self, lfclient_host, lfclient_port, upstream, num_sta, security, ssid, password,
                 target_per_ten, file_size, bands, start_id=0, twog_radio=None, fiveg_radio=None, _debug_on=False, _exit_on_error=False,
                 _exit_on_fail=False):
        self.host = lfclient_host
        self.port = lfclient_port
        self.upstream = upstream
        self.num_sta = num_sta
        #self.radio = radio
        self.security = security
        self.ssid = ssid
        self.sta_start_id = start_id
        self.password = password
        #self.url = url
        self.twog_radio = twog_radio
        self.fiveg_radio = fiveg_radio
        self.target_per_ten = target_per_ten
        self.file_size = file_size
        self.bands = bands
        self.debug = _debug_on
        print(bands)

        self.local_realm = realm.Realm(lfclient_host=self.host, lfclient_port=self.port)
        self.station_profile = self.local_realm.new_station_profile()
        self.http_profile = self.local_realm.new_http_profile()
        self.http_profile.requests_per_ten = self.target_per_ten
        #self.http_profile.url = self.url
        self.port_util = PortUtils(self.local_realm)
        self.http_profile.debug = _debug_on
        self.created_cx = {}

    def set_values(self):
        # This method will set values according user input
        if self.bands == "5G":
            self.radio = [self.fiveg_radio]
        elif self.bands == "2.4G":
            self.radio = [self.twog_radio]
        elif self.bands == "Both":
            self.radio = [self.fiveg_radio, self.twog_radio]
            print("hello", self.radio)
            self.num_sta = self.num_sta // 2

    def precleanup(self):
        self.count = 0
        try:
            self.local_realm.load("BLANK")
        except:
            print("couldn't load 'BLANK' Test Configuration")

        #print("hi", self.radio)

        for rad in self.radio:
            print("radio", rad)
            if rad == self.fiveg_radio:
                # select an mode
                self.station_profile.mode = 10
                self.count = self.count + 1
            elif rad == self.twog_radio:
                # select an mode
                self.station_profile.mode = 6
                self.count = self.count + 1

            if self.count == 2:
                self.sta_start_id = self.num_sta
                self.num_sta = 2 * (self.num_sta)
                self.station_profile.mode = 10
                self.http_profile.cleanup()
                self.station_list1 = LFUtils.portNameSeries(prefix_="sta", start_id_=self.sta_start_id,
                                                            end_id_=self.num_sta - 1, padding_number_=10000,
                                                            radio=rad)
                # cleanup station list which started sta_id 20
                self.station_profile.cleanup(self.station_list1, debug_=self.local_realm.debug)
                LFUtils.wait_until_ports_disappear(base_url=self.local_realm.lfclient_url,
                                                   port_list=self.station_list,
                                                   debug=self.local_realm.debug)
                return
            # clean dlayer4 ftp traffic
            self.http_profile.cleanup()
            self.station_list = LFUtils.portNameSeries(prefix_="sta", start_id_=self.sta_start_id,
                                                       end_id_=self.num_sta - 1, padding_number_=10000,
                                                       radio=rad)
            # cleans stations
            self.station_profile.cleanup(self.station_list, delay=1, debug_=self.local_realm.debug)
            LFUtils.wait_until_ports_disappear(base_url=self.local_realm.lfclient_url,
                                               port_list=self.station_list,
                                               debug=self.local_realm.debug)
            time.sleep(1)
        print("precleanup done")

    def build(self):
        # enable http on ethernet
        self.port_util.set_http(port_name=self.local_realm.name_to_eid(self.upstream)[2], resource=1, on=True)

        # enable dhcp to ethernet
        data = {
            "shelf": 1,
            "resource": 1,
            "port": "eth1",
            "current_flags": 2147483648,
            "interest": 16384

        }
        url = "/cli-json/set_port"
        self.local_realm.json_post(url, data, debug_=True)
        time.sleep(10)

        for rad in self.radio:

            # station build
            self.station_profile.use_security(self.security, self.ssid, self.password)
            self.station_profile.set_command_flag("add_sta", "create_admin_down", 1)
            self.station_profile.set_command_param("set_port", "report_timer", 1500)
            self.station_profile.set_command_flag("set_port", "rpt_timer", 1)
            self.station_profile.create(radio=rad, sta_names_=self.station_list, debug=self.local_realm.debug)
            self.local_realm.wait_until_ports_appear(sta_list=self.station_list)
            self.station_profile.admin_up()
            if self.local_realm.wait_for_ip(self.station_list,timeout_sec=60):
                self.local_realm._pass("All stations got IPs")
            else:
                self.local_realm._fail("Stations failed to get IPs")
            # building layer4
            self.http_profile.direction = 'dl'
            self.http_profile.dest = '/dev/null'
            data = self.local_realm.json_get("ports/list?fields=IP")

            # getting eth ip
            for i in data["interfaces"]:
                for j in i:
                    if "1.1." + self.upstream == j:
                        ip_upstream = i["1.1." + self.upstream]['ip']

            # create http profile
            self.http_profile.create(ports=self.station_profile.station_names, sleep_time=.5,
                                     suppress_related_commands_=None, http=True,
                                     http_ip=ip_upstream + "/webpage.html")
            if self.count == 2:
                self.station_list = self.station_list1
                self.station_profile.mode = 6
        print("Test Build done")

    def start(self):
        print("Test Started")
        self.http_profile.start_cx()
        try:
            for i in self.http_profile.created_cx.keys():
                while self.local_realm.json_get("/cx/" + i).get(i).get('state') != 'Run':
                    continue
        except Exception as e:
            pass

    def my_monitor(self):
        # data in json format
        data = self.local_realm.json_get("layer4/list?fields=uc-avg")
        data1 = []
        for i in range(len(data['endpoint'])):
            data1.append(str(list(data['endpoint'][i]))[2:-2])
        # print(data1)
        data2 = []
        for i in range(self.num_sta):
            data = self.local_realm.json_get("layer4/list?fields=uc-avg")
            # print(type(data['endpoint'][i][data1[i]]['uc-avg']))
            data2.append((data['endpoint'][i][data1[i]]['uc-avg']))

        # print("downloading time for all clients", data2)
        return data2

    def postcleanup(self):
        # for rad in self.radio
        self.http_profile.cleanup()
        self.station_profile.cleanup()
        LFUtils.wait_until_ports_disappear(base_url=self.lfclient_url, port_list=self.station_profile.station_names,
                                           debug=self.debug)

    def file_create(self):
        os.chdir('/usr/local/lanforge/nginx/html/')
        if os.path.isfile("/usr/local/lanforge/nginx/html/webpage.html"):
            os.system("sudo rm /usr/local/lanforge/nginx/html/webpage.html")
        os.system("sudo fallocate -l " + self.file_size + " /usr/local/lanforge/nginx/html/webpage.html")
        print("File creation done", self.file_size)

def main():
    parser = argparse.ArgumentParser(description="lanforge webpage download Test Script")
    parser.add_argument('--mgr', help='hostname for where LANforge GUI is running', default='localhost')
    parser.add_argument('--mgr_port', help='port LANforge GUI HTTP service is running on', default=8080)
    parser.add_argument('--upstream_port', help='non-station port that generates traffic: eg: eth1', default='eth2')
    parser.add_argument('--num_stations', type=int, help='number of stations to create', default=1)
    parser.add_argument('--twog_radio', help='specify radio for 2.4G clients', default='wiphy3')
    parser.add_argument('--fiveg_radio', help='specify radio for 5 GHz client', default='wiphy0')
    parser.add_argument('--security', help='WiFi Security protocol: {open|wep|wpa2|wpa3')
    parser.add_argument('--ssid', help='WiFi SSID for script object to associate to')
    parser.add_argument('--passwd', help='WiFi passphrase/password/key')
    parser.add_argument('--target_per_ten', help='number of request per 10 minutes', default=100)
    parser.add_argument('--file_size', type=str, help='specify the size of file you want to download', default='5Mb')
    parser.add_argument('--bands', nargs="+", help='--bands', default=["5G", "2.4G", "Both"])
    parser.add_argument('--duration', type=int, help='time to run traffic')
    parser.add_argument('--threshold_5g',help="Enter the threshold value for 5G Pass/Fail criteria", default="60")
    parser.add_argument('--threshold_2g',help="Enter the threshold value for 2.4G Pass/Fail criteria",default="90")
    parser.add_argument('--threshold_both',help="Enter the threshold value for Both Pass/Fail criteria" , default="50")
    parser.add_argument('--ap_name', help="specify the ap model ", default="TestAP")

    args = parser.parse_args()
    test_time = datetime.datetime.now()
    test_time = test_time.strftime("%b %d %H:%M:%S")
    print("Test started at ", test_time)
    list5G = []
    list2G = []
    Both = []
    dict_keys = []
    dict_keys.extend(args.bands)
    # print(dict_keys)
    final_dict = dict.fromkeys(dict_keys)
    # print(final_dict)
    dict1_keys = ['dl_time', 'min', 'max', 'avg']
    for i in final_dict:
        final_dict[i] = dict.fromkeys(dict1_keys)
    print(final_dict)
    min5 = []
    min2 = []
    min_both = []
    max5 = []
    max2 = []
    max_both = []
    avg2 = []
    avg5 = []
    avg_both = []

    #ap = AP_automate(args.ap_ip, args.user, args.pswd)
    for bands in args.bands:
        http = HttpDownload(lfclient_host=args.mgr, lfclient_port=args.mgr_port,
                            upstream=args.upstream_port, num_sta=args.num_stations,
                            security=args.security,
                            ssid=args.ssid, password=args.passwd,
                            target_per_ten=args.target_per_ten,
                            file_size=args.file_size, bands=bands,
                            twog_radio=args.twog_radio,
                            fiveg_radio=args.fiveg_radio
                            )
        #chttp.file_create()
        http.set_values()
        http.precleanup()
        http.build()
        http.start()
        duration = args.duration
        duration = 60 * duration
        print("time in seconds ", duration)
        time.sleep(duration)
        value = http.my_monitor()

        if bands == "5G":
            list5G.extend(value)
            # print("5G", list5G)
            final_dict['5G']['dl_time'] = list5G
            min5.append(min(list5G))
            final_dict['5G']['min'] = min5
            max5.append(max(list5G))
            final_dict['5G']['max'] = max5
            avg5.append((sum(list5G) / args.num_stations))
            final_dict['5G']['avg'] = avg5
        elif bands == "2.4G":
            list2G.extend(value)
            print("2.4G", list2G)
            final_dict['2.4G']['dl_time'] = list2G
            min2.append(min(list2G))
            final_dict['2.4G']['min'] = min2
            max2.append(max(list2G))
            final_dict['2.4G']['max'] = max2
            avg2.append((sum(list2G) / args.num_stations))
            final_dict['2.4G']['avg'] = avg2
        elif bands == "Both":
            Both.extend(value)
            print("both", Both)
            final_dict['Both']['dl_time'] = Both
            min_both.append(min(Both))
            final_dict['Both']['min'] = min_both
            max_both.append(max(Both))
            final_dict['Both']['max'] = max_both
            avg_both.append((sum(Both) /args.num_stations))
            final_dict['Both']['avg'] = avg_both
    print("final list", final_dict)
    result_data = final_dict
    print("result", result_data)
    print("Test Finished")
    test_end = datetime.datetime.now()
    test_end = test_end.strftime("%b %d %H:%M:%S")
    print("Test ended at ", test_end)
    s1 = test_time
    s2 = test_end  # for example
    FMT = '%b %d %H:%M:%S'
    test_duration = datetime.datetime.strptime(s2, FMT) - datetime.datetime.strptime(s1, FMT)
    #test_duration = "2:04:34"
    print("total test duration ", test_duration)
    date = str(datetime.datetime.now()).split(",")[0].replace(" ", "-").split(".")[0]
    test_setup_info = {
            "DUT Name": args.ap_name,
            "SSID": args.ssid,
            "Test Duration": test_duration,

        }
    test_input_infor={
        "File Size" : args.file_size,
        "Bands" : args.bands,
        "Upstream": args.upstream_port,
        "Stations": args.num_stations,
        "SSID" :args.ssid,
        "Security": args.security,
        "Duration" : args.duration,
        "Contact": "support@candelatech.com"
    }

    report = lf_report(_results_dir_name="webpage_test")
    report.set_title("WEBPAGE DOWNLOAD TEST")
    report.set_date(date)
    report.build_banner()
    report.set_table_title("Test Setup Information")
    report.build_table_title()
    report.test_setup_table(value="Device under test",test_setup_data= test_setup_info)

    report.set_obj_html("Objective",
                        "The Webpage Download Test is designed to test the performance of the Access Point.The goal is to check whether the webpage loading time meets the expectation when clients connected on single radio as well as dual radio")
    report.build_objective()
    report.set_obj_html("Download Time Graph","The below graph provides information about the average download time taken by each client for duration of  "+ str(args.duration) + " min")
    report.build_objective()

    download_time = dict.fromkeys(result_data.keys())
    for i in download_time:
        try:
            download_time[i] = result_data[i]['dl_time']
        except:
            download_time[i] = []
    print(download_time)
    lst = []
    lst1 = []
    lst2 = []
    dwnld_time = dict.fromkeys(result_data.keys())
    dataset = []
    for i in download_time:
        if i == "5G":
            for j in download_time[i]:
                x = (j / 1000)
                y = round(x, 2)
                lst.append(y)
            print(lst)
            dwnld_time["5G"] = lst
            dataset.append(dwnld_time["5G"])
        if i == "2.4G":
            for j in download_time[i]:
                x = (j / 1000)
                y = round(x, 2)
                lst1.append(y)
            print(lst)
            dwnld_time["2.4G"] = lst1
            dataset.append(dwnld_time["2.4G"])
        if i == "Both":
            # print("yes", download_time[i])
            for j in download_time[i]:
                x = (j / 1000)
                y = round(x, 2)
                lst2.append(y)
            # print(lst2)
            dwnld_time["Both"] = lst2
            dataset.append(dwnld_time["Both"] )

    print("download time",dwnld_time)
    #dataset = [dwnld_time['5G'], dwnld_time['2.4G'], dwnld_time['Both']]
    lis = []
    for i in range(1, args.num_stations + 1):
        print(i)
        lis.append(i)

    graph = lf_bar_graph(_data_set=dataset, _xaxis_name="Stations", _yaxis_name="Time in Seconds",
                         _xaxis_categories=lis, _label=args.bands, _xticks_font=7,
                         _graph_image_name="webpage",
                         _color=['forestgreen', 'darkorange', 'blueviolet'], _color_edge='black', _figsize=(10, 5),
                         _grp_title="Download time taken by each client", _xaxis_step=1, )
    graph_png = graph.build_bar_graph()
    print("graph name {}".format(graph_png))
    report.set_graph_image(graph_png)
    report.move_graph_image()
    report.build_graph()

    report.set_obj_html("Summary Table Description",
                        "This Table shows you the summary result of Webpage Download Test as PASS or FAIL criteria. If the average time taken by " + str(args.num_stations) + " clients to access the webpage is less than " + str(args.threshold_2g) + "s it's a PASS criteria for 2.4 ghz clients, If the average time taken by " + "" + str(args.num_stations) + " clients to access the webpage is less than " +  str(args.threshold_5g) + "s it's a PASS criteria for 5 ghz clients and If the average time taken by " + str(args.num_stations) + " clients to access the webpage is less than " + str(args.threshold_both) + "s it's a PASS criteria for 2.4 ghz and 5ghz clients")

    report.build_objective()
    x1= []
    html_struct = dict.fromkeys(list(result_data.keys()))
    for fcc in list(result_data.keys()):
        fcc_type = result_data[fcc]["avg"]
        print(fcc_type)
        for i in fcc_type:
            x1.append(i)
        # print(x)
    y11 = []
    for i in x1:
        i = i / 1000
        y11.append(i)
    # print(y)
    z11 = []
    for i in y11:
        i = str(round(i, 2))
        z11.append(i)
    print(z11)
    pass_fail_list = []
    # print(list(result_data.keys()))
    sumry2 = []
    sumry5 = []
    sumryB = []
    data = []
    if args.bands == ["5G", "2.4G", "Both"]:
        print("yes")
        # 5G
        if float(z11[0]) < float(args.threshold_5g):
            print("PASS")
            pass_fail_list.append("PASS")
            sumry5.append("PASS")
        elif float(z11[0]) == 0.0 or float(z11[0]) > float(args.threshold_5g):
            print("FAIL")
            pass_fail_list.append("FAIL")
            sumry5.append("FAIL")
        # 2.4g
        if float(z11[1]) < float(args.threshold_2g):
            var = "PASS"
            pass_fail_list.append(var)
            sumry2.append("PASS")
        elif float(z11[1]) == 0.0 or float(z11[1]) > float(args.threshold_2g):
            pass_fail_list.append("FAIL")
            sumry2.append("FAIL")
        # BOTH
        if float(z11[2]) < float(args.threshold_both):
            var = "PASS"
            pass_fail_list.append(var)
            sumryB.append("PASS")
        elif float(z11[2]) == 0.0 or  float(z11[2]) > float(args.threshold_both):
            pass_fail_list.append("FAIL")
            sumryB.append("FAIL")

        data.append(','.join(sumry5))
        data.append(','.join(sumry2))
        data.append(','.join(sumryB))

    elif args.bands == ['5G']:
        if float(z11[0]) < float(args.threshold_5g):
            print("PASS")
            pass_fail_list.append("PASS")
            sumry5.append("PASS")
        elif float(z11[0]) == 0.0  or float(z11[0]) > float(args.threshold_5g):
            print("FAIL")
            pass_fail_list.append("FAIL")
            sumry5.append("FAIL")
        data.append(','.join(sumry5))

    elif args.bands == ['2.4G']:
        if float(z11[0]) < float(args.threshold_2g):
            var = "PASS"
            pass_fail_list.append(var)
            sumry2.append("PASS")
        elif float(z11[0]) == 0.0  or float(z11[0]) > float(args.threshold_2g):
            pass_fail_list.append("FAIL")
            sumry2.append("FAIL")
        data.append(','.join(sumry2))
    elif args.bands == ["Both"]:
        if float(z11[0]) < float(args.threshold_both):
            var = "PASS"
            pass_fail_list.append(var)
            sumryB.append("PASS")
        elif float(z11[0]) == 0.0  or float(z11[0]) > float(args.threshold_both):
            pass_fail_list.append("FAIL")
            sumryB.append("FAIL")
        data.append(','.join(sumryB))
    elif args.bands == ['5G', '2.4G']:
        if float(z11[0]) < float(args.threshold_5g):
            print("PASS")
            pass_fail_list.append("PASS")
            sumry5.append("PASS")
        elif float(z11[0]) == 0.0 or float(z11[0]) > float(args.threshold_5g):
            print("FAIL")
            pass_fail_list.append("FAIL")
            sumry5.append("FAIL")
        # 2.4g
        if float(z11[1]) < float(args.threshold_2g):
            var = "PASS"
            pass_fail_list.append(var)
            sumry2.append("PASS")
        elif float(z11[1]) == 0.0 or float(z11[1]) > float(args.threshold_2g):
            pass_fail_list.append("FAIL")
            sumry2.append("FAIL")
        data.append(','.join(sumry5))
        data.append(','.join(sumry2))

    elif args.bands == ['5G', 'Both']:
        if float(z11[0]) < float(args.threshold_5g):
            print("PASS")
            pass_fail_list.append("PASS")
            sumry5.append("PASS")
        elif float(z11[0]) == 0.0 or float(z11[0]) > float(args.threshold_5g):
            print("FAIL")
            pass_fail_list.append("FAIL")
            sumry5.append("FAIL")
        if float(z11[1]) < float(args.threshold_both):
            var = "PASS"
            pass_fail_list.append(var)
            sumryB.append("PASS")
        elif float(z11[1]) == 0.0 or float(z11[1]) > float(args.threshold_both):
            pass_fail_list.append("FAIL")
            sumryB.append("FAIL")

        data.append(','.join(sumry5))
        data.append(','.join(sumryB))

    elif args.bands == ['2.4G', 'Both']:
        if float(z11[0]) < float(args.threshold_2g):
            var = "PASS"
            pass_fail_list.append(var)
            sumry2.append("PASS")
        elif float(z11[0]) == 0.0  or float(z11[0]) > float(args.threshold_2g):
            pass_fail_list.append("FAIL")
            sumry2.append("FAIL")
        if float(z11[1]) < float(args.threshold_both):
            var = "PASS"
            pass_fail_list.append(var)
            sumryB.append("PASS")
        elif float(z11[1]) == 0.0 or float(z11[1]) > float(args.threshold_both):
            pass_fail_list.append("FAIL")
            sumryB.append("FAIL")
        data.append(','.join(sumry2))
        data.append(','.join(sumryB))

    #print("SUMMARRY",sumry2, sumry5, sumryB)
    #print(data)
    #[result_data.keys()]
    summary_table_value = {
        "": args.bands,
        "PASS/FAIL": data
    }
    test_setup1 = pd.DataFrame(summary_table_value)
    report.set_table_dataframe(test_setup1)
    report.build_table()

    report.set_obj_html("Download Time Table Description",
                        "This Table will provide you information of the minimum, maximum and the average time taken by clients to download a webpage in seconds")

    report.build_objective()
    x = []
    for fcc in list(result_data.keys()):
        fcc_type = result_data[fcc]["min"]
        #print(fcc_type)
        for i in fcc_type:
            x.append(i)
        #print(x)
    y = []
    for i in x:
        i = i / 1000
        y.append(i)
    z = []
    for i in y:
        i = str(round(i, 2))
        z.append(i)
    #rint(z)
    x1 = []

    for fcc in list(result_data.keys()):
        fcc_type = result_data[fcc]["max"]
        #print(fcc_type)
        for i in fcc_type:
            x1.append(i)
        #print(x1)
    y1 = []
    for i in x1:
        i = i / 1000
        y1.append(i)
    z1 = []
    for i in y1:
        i = str(round(i, 2))
        z1.append(i)
    #print(z1)
    x2 = []

    for fcc in list(result_data.keys()):
        fcc_type = result_data[fcc]["avg"]
        #print(fcc_type)
        for i in fcc_type:
            x2.append(i)
        #print(x2)
    y2 = []
    for i in x2:
        i = i / 1000
        y2.append(i)
    z2 = []
    for i in y2:
        i = str(round(i, 2))
        z2.append(i)
    #print(z2)
    #[result_data.keys()]
    download_table_value= {
        "" : args.bands,
        "Minimum" : z,
        "Maximum" : z1,
        "Average" : z2

    }
    test_setup = pd.DataFrame(download_table_value)
    report.set_table_dataframe(test_setup)
    report.build_table()
    report.set_table_title("Test input Information")
    report.build_table_title()
    report.test_setup_table(value="Information", test_setup_data=test_input_infor)
    report.build_footer()
    html_file = report.write_html()
    print("returned file {}".format(html_file))
    print(html_file)
    report.write_pdf()

if __name__ == '__main__':
    main()
