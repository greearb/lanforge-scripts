
"""
Candela Technologies Inc.

Info : Standard Script for Webconsole test utility
Date :
Author : Shivam Thakur

"""

import sys
if 'py-json' not in sys.path:
    sys.path.append('../py-json')
from LANforge import LFUtils
from LANforge import lfcli_base
from LANforge.lfcli_base import LFCliBase
from LANforge.LFUtils import *
import realm
from realm import PortUtils
import argparse
import datetime
import time
import matplotlib.pyplot as plt
import threading
runtime_path = "../py-run/runtime.json"

class ClientVisualization(LFCliBase, threading.Thread):
    def __init__(self, lfclient_host="localhost", lfclient_port=8080, num_clients= 64, max_data= 120, thread_id=None, _debug_on=False, _exit_on_error=False, _exit_on_fail=False):
        super().__init__(lfclient_host, lfclient_port, _debug=_debug_on, _halt_on_error=_exit_on_error,
                         _exit_on_fail=_exit_on_fail)
        threading.Thread.__init__(self)
        self.num_clients = num_clients
        self.max_data = max_data
        self._stop_event = threading.Event()
        self.client_data = {"down":[], "phantom":[], "ip":[], "scanning":[]}

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        self.start_thread()

    def start_thread(self):
        while True:
            self.scanning = 0
            self.ip = 0
            self.down = 0
            self.phantom = 0
            for i in self.json_get("/port/list?fields=port,alias,parent%20dev,down,phantom,ip,port%20type")[
                'interfaces']:

                for j in i:
                    if i[j]['port type'] == "WIFI-STA" and i[j]['parent dev'] == "wiphy1" and i[j]['alias'] != 'wlan1':
                        if i[j]['down'] == False and i[j]['phantom'] == False and i[j]['ip'] == '0.0.0.0':
                            self.scanning += 1
                        elif i[j]['down'] == False and i[j]['phantom'] == True:
                            self.phantom += 1
                        elif i[j]['down'] == True and i[j]['phantom'] == True:
                            self.phantom += 1
                            self.client_data['phantom'].append(self.phantom)
                        elif i[j]['down'] == True and i[j]['phantom'] == False:
                            self.down += 1
                        elif i[j]['ip'] != "0.0.0.0":
                            self.ip += 1
                        else:
                            continue
            self.client_data['scanning'].append(self.scanning)
            self.client_data['phantom'].append(self.phantom)
            self.client_data['down'].append(self.down)
            self.client_data['ip'].append(self.ip)


            for i in self.client_data:
                if len(self.client_data[i]) >= self.max_data:
                    self.client_data[i].pop(0)
            time.sleep(1)



            if self.stopped():
                break


class CreateHTML():
    def __init__(self, path="", test_name="", time_snap="", dut_ssid="", test_conf_data={}, objective="", test_results={}, chart_data={}, chart_params={}):
        self.head = """
                      <html>
                        <head>
                            <title>Client Connectivity Test</title>
                        </head>
                        <body>
                        <div class='Section report_banner-1000x205' style='background-image:url("../../assets/brand/banner.jpg");background-repeat:no-repeat;padding:0;margin:0;min-width:1000px; min-height:205px;width:1000px; height:205px;max-width:1000px; max-height:205px;'>
                            <img align='right' style='padding:25;margin:5;width:200px;' src="../../assets/brand/logo.png" border='0' />
                                <div class='HeaderStyle'>
                                    <br>
                                    <h1 class='TitleFontPrint' style='color:darkgreen;'>"""+test_name+"""</h1>
                                    <h3 class='TitleFontPrint' style="color:darkgreen;">"""+time_snap+"""</h3>
                                </div>
                        </div>
                        <br>
                    """
        self.test_conf = """
                            <table width="700px" border="1" cellpadding="2" cellspacing="0" style="border-top-color: gray; border-top-style: solid; border-top-width: 1px; border-right-color: gray; border-right-style: solid; border-right-width: 1px; border-bottom-color: gray; border-bottom-style: solid; border-bottom-width: 1px; border-left-color: gray; border-left-style: solid; border-left-width: 1px">
                                <tr>
                                    <th colspan="2">
                                      Test Setup Information
                                    </th>
                                </tr>
                                <tr>
                                    <td>
                                      Device Under Test
                                    </td>
                                    <td>
                                    <table width="100%" border="0" cellpadding="2" cellspacing="0" style="border-top-color: gray; border-top-style: solid; border-top-width: 1px; border-right-color: gray; border-right-style: solid; border-right-width: 1px; border-bottom-color: gray; border-bottom-style: solid; border-bottom-width: 1px; border-left-color: gray; border-left-style: solid; border-left-width: 1px">
                                        <tr>
                                            <td>
                                                SSID
                                            </td>
                                            <td colspan="3">"""+dut_ssid+"""
                                            </td>
                                        </tr>
                                        """

        for i in test_conf_data:
            self.test_conf = self.test_conf + """<tr>
                                                    <td>"""+str(i)+"""
                                                    </td>
                                                    <td colspan="3">"""+test_conf_data[i]+"""
                                                    </td>
                                                 </tr>
                                               """

        self.test_conf = self.test_conf + """         </table>
                                                    </td>
                                                </tr>
                                            </table>
                                          """

        self.objective = """
                            <br><h2 align="left">Objective</h2> <p align="left" width="900">
                                """+objective+"""
                            </p>
                            <br>
                            """

        if str(test_results['summary']).__contains__("PASS"):
            self.summary_results ="""
                               <br>
                                    <table width="700px" border="1" cellpadding="2" cellspacing="0" style="border-top-color: gray; border-top-style: solid; border-top-width: 1px; border-right-color: gray; border-right-style: solid; border-right-width: 1px; border-bottom-color: gray; border-bottom-style: solid; border-bottom-width: 1px; border-left-color: gray; border-left-style: solid; border-left-width: 1px">
                                        <tr>
                                            <th colspan="2">
                                                Summary Results
                                            </th>
                                        </tr>
                                        <tr align='center' bgcolor="#90EE90">
                                            <td>
                                         """ + test_results['summary'] + """
                                            </td>
                                        </tr>
                                    </table>
                               <br>
                               """
        else:
            self.summary_results = """
                                           <br>
                                                <table width="700px" border="1" cellpadding="2" cellspacing="0" style="border-top-color: gray; border-top-style: solid; border-top-width: 1px; border-right-color: gray; border-right-style: solid; border-right-width: 1px; border-bottom-color: gray; border-bottom-style: solid; border-bottom-width: 1px; border-left-color: gray; border-left-style: solid; border-left-width: 1px">
                                                    <tr>
                                                        <th colspan="2">
                                                            Summary Results
                                                        </th>
                                                    </tr>
                                                    <tr align='center' bgcolor="orange">
                                                        <td>
                                                     """ + test_results['summary'] + """
                                                        </td>
                                                    </tr>
                                                </table>
                                           <br>
                                           """
        chart_d =[]
        chart_label =[]
        for i in chart_data:
            chart_label.append(i)
            chart_d.append(chart_data[i])




        self.detail_result = """<table width="1000px" border="1" cellpadding="2" cellspacing="0" >
                                        <tr><th colspan="2">Detailed Results</th></tr>
                                        <table width="1000px" border="1" >
                                            <tr>
                             """
        for index in test_results['detail']['keys']:
            self.detail_result =  self.detail_result+"<th colspan='2'>"+index+"</th>"
        self.detail_result = self.detail_result +"</tr>"

        for data in test_results['detail']['data']:
            self.detail_result = self.detail_result + "<tr align='center'>"
            print(data)
            for i in data:
                print(data[i])
                if str(data[i]).__contains__("PASS"):
                    self.detail_result = self.detail_result + "<th colspan='2' bgcolor='#90EE90'>" + str(data[i]) + "</th>"
                elif str(data[i]).__contains__("FAIL"):
                    self.detail_result = self.detail_result + "<th colspan='2' bgcolor='orange'>" + str(data[i]) + "</th>"
                else:
                    self.detail_result = self.detail_result + "<th colspan='2'>" + str(data[i]) + "</th>"
            self.detail_result = self.detail_result +"</tr>"

        self.chart_data = chart_data
        chart_values = []
        for i in self.chart_data:
            chart_values.append(self.chart_data[i])
        plt.bar(list(self.chart_data.keys()), chart_values, tick_label=list(self.chart_data.keys()))

        plt.xlabel(chart_params['xlabel'])
        # naming the y-axis
        plt.ylabel(chart_params['ylabel'])
        # plot title
        plt.title(chart_params['chart_head'])
        plt.xticks(rotation=90, fontsize=8)
        plt.tight_layout()
        # function to show the plot
        plt.savefig(fname=path + "plot.png")
        plt.close()

        self.chart = """<img align='center' style='padding:25;margin:5;width:600px;' src="plot.png" border='0' />"""


        self.end = """</table>
                      </table>
                      </body>
                      </html>
                   """
        self.report = self.head + self.test_conf + self.objective + self.summary_results + self.chart +self.detail_result + self.end



if __name__ == "__main__":
    thread1 = ClientVisualization(lfclient_host="192.168.200.15", thread_id=1)
    thread1.start()
    for i in range(30):
        print(thread1.client_data)
    thread1.stop()

