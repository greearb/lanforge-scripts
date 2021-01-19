"""under progress"""

import os
import paramiko
import time
import threading
from queue import Queue
from cx_time import IPv4Test
import datetime


class DFS_TESTING:
    def _init_(self):
        pass

    def hackrf_status_off(self):
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5220000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)

    def check_radio_on_off(self, x):
        self.x = x
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect('192.168.200.143', port=22, username='root', password='Netgear@123xzsawq@!')
        stdin, stdout, stderr = ssh.exec_command('conf_get system:wlanSettings:wlanSettingTable:wlan0:radioStatus')
        output = stdout.readlines()
        print('\n'.join(output))
        self.x = output
        time.sleep(1)
        return self.x

    def exit_from_ap(self):
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect('192.168.200.143', port=22, username='root', password='Netgear@123xzsawq@!')
        stdin, stdout, stderr = ssh.exec_command('exit')
        time.sleep(1)

    def check_for_channels(self, q):
        self.q = q
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect('192.168.200.143', port=22, username='root', password='Netgear@123xzsawq@!')
        stdin, stdout, stderr = ssh.exec_command('iwlist wifi1vap0 channel ')
        output = stdout.readlines()
        # print('\n'.join(output))
        self.q = output
        time.sleep(1)
        return self.q

    def set_channel_in_ap_at_52(self):
        # cmd = "conf_set system:wlanSettings:wlanSettingTable:wlan1:channel ;conf_save"
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect('192.168.200.143', port=22, username='root', password='Netgear@123xzsawq@!')
        stdin, stdout, stderr = ssh.exec_command("conf_set system:wlanSettings:wlanSettingTable:wlan1:channel 52")
        output = stdout.readlines()
        print('\n'.join(output))
        time.sleep(20)

    def set_channel_in_ap_at_100(self):
        # cmd = "conf_set system:wlanSettings:wlanSettingTable:wlan1:channel ;conf_save"
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect('192.168.200.143', port=22, username='root', password='Netgear@123xzsawq@!')
        stdin, stdout, stderr = ssh.exec_command("conf_set system:wlanSettings:wlanSettingTable:wlan1:channel 100")
        output = stdout.readlines()
        print('\n'.join(output))
        time.sleep(20)

    def set_channel_in_ap_at_116(self):
        # cmd = "conf_set system:wlanSettings:wlanSettingTable:wlan1:channel ;conf_save"
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect('192.168.200.143', port=22, username='root', password='Netgear@123xzsawq@!')
        stdin, stdout, stderr = ssh.exec_command("conf_set system:wlanSettings:wlanSettingTable:wlan1:channel 116")
        output = stdout.readlines()
        print('\n'.join(output))
        time.sleep(20)

    def set_channel_in_ap_at_136(self):
        # cmd = "conf_set system:wlanSettings:wlanSettingTable:wlan1:channel ;conf_save"
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect('192.168.200.143', port=22, username='root', password='Netgear@123xzsawq@!')
        stdin, stdout, stderr = ssh.exec_command("conf_set system:wlanSettings:wlanSettingTable:wlan1:channel 136")
        output = stdout.readlines()
        print('\n'.join(output))
        time.sleep(20)

    def create_station_on_GUI_1(self):
        obj = IPv4Test(_host="localhost",
                       _port=8080,
                       _ssid="TestAP22",
                       _password="[BLANK]",
                       _security="open",
                       _radio="wiphy0")
        obj.cleanup(obj.sta_list)
        obj.build()
        obj.station_profile.admin_up()
        obj.local_realm.wait_for_ip(obj.sta_list)
        time.sleep(5)
        var = obj.json_get("/port/1/1/sta0000?fields=channel")
        var_1 = (var['interface']['channel'])
        print(var_1)


    def generate_radar_at_ch52(self, r):
        self.r = r
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5260000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.r = "Radar detected"
        return self.r

    def generate_radar_at_ch56(self, q):
        self.q = q
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5280000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')

        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.q = "Radar detected"
        return self.q

    def generate_radar_at_ch60(self, w):
        self.w = w
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5300000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.w = "Radar detected"
        return self.w

    def generate_radar_at_ch64(self, e):
        self.e = e
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5320000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.e = "Radar detected"
        return self.e

    def generate_radar_at_ch100(self, f):
        self.f = f
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5500000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.f = "Radar received"
        return self.f

    def generate_radar_at_ch104(self, t):
        self.t = t
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5520000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.t = "Radar detected"
        return self.t

    def generate_radar_at_ch108(self, u):
        self.u = u
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5540000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.u = "Radar detected"
        return self.u

    def generate_radar_at_ch112(self, i):
        self.i = i
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5560000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.i = "Radar detected"
        return self.i

    def generate_radar_at_ch116(self, o):
        self.o = o
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5580000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.o = "Radar detected"
        return self.o

    def generate_radar_at_ch120(self, p):
        self.p = p
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5600000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.p = "Radar detected"
        return self.p

    def generate_radar_at_ch124(self, a):
        self.a = a
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5620000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.a = "Radar detected"
        return self.a

    def generate_radar_at_ch128(self, s):
        self.s = s
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5640000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.s = "Radar detected"
        return self.s

    def generate_radar_at_ch132(self, d):
        self.d = d
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5660000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.d = "Radar detected"
        return self.d

    def generate_radar_at_ch136(self, h):
        self.h = h
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5680000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.h = "Radar detected"
        return self.h

    def generate_radar_at_ch140(self, j):
        self.j = j
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5700000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.j = "Radar detected"
        return self.j

    def station_clean(self):
        obj = IPv4Test(_host="localhost",
                       _port=8080,
                       _ssid="TestAP22",
                       _password="[BLANK]",
                       _security="open",
                       _radio="wiphy0")
        obj.cleanup(obj.sta_list)
        var_1 = "station cleaned"
        print(var_1)

    def wait_for_ip(self):
        obj = IPv4Test(_host="localhost",
                        _port=8080,
                        _ssid="TestAP22",
                        _password="[BLANK]",
                        _security="open",
                        _radio="wiphy0")

        obj.local_realm.wait_for_ip(obj.sta_list)
        time.sleep(5)

    def check_log_channel(self, r):
        self.r = r
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect('192.168.200.143', port=22, username='root', password='Netgear@123xzsawq@!')
        stdin, stdout, stderr = ssh.exec_command('cat /tmp/log/messages | grep channel')
        output = stdout.readlines()
        print('\n'.join(output))
        time.sleep(1)
        self.r = output
        return self.r

    def check_for_all_logs(self, r):
        self.r = r
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect('192.168.200.143', port=22, username='root', password='Netgear@123xzsawq@!')
        stdin, stdout, stderr = ssh.exec_command('cat /tmp/log/messages')
        output = stdout.readlines()
        print('\n'.join(output))
        time.sleep(1)
        self.r = output
        return self.r



def main():
    que = Queue()
    threads_list = []
    dfs = DFS_TESTING()

    print("checking hackrf is oN/OFF")
    print("Hackrf is ON")
    print("press s --> enter --> q to stop hackrf")
    dfs.hackrf_status_off()

    print("Now hackrf is OFF")

    time.sleep(2)

    print("checking if all radios is ON/OFF")
    t1 = threading.Thread(target=lambda q, arg1: q.put(dfs.check_radio_on_off(arg1)), args=(que, ""))
    t1.start()
    threads_list.append(t1)
    t1.join()
    x = que.get()
    # print("result", x)
    new_list = []
    new_list_1 = []
    for element in x:
        new_list.append(element.strip())
    # print(new_list[0])
    new_list_1 = new_list[0].split()
    # print("elements", new_list_1)

    if (new_list_1[1] == "1"):
        print("Radio is ON")
    else:
        print("Radio is OFF")

    time.sleep(2)

    thr_1 = threading.Thread(target=dfs.exit_from_ap())
    thr_1.start()
    thr_1.join()
    print("exit")

    time.sleep(10)

    t2 = threading.Thread(target=lambda q, arg1: q.put(dfs.check_for_channels(arg1)), args=(que, ""))
    t2.start()
    threads_list.append(t2)
    t2.join()
    y = que.get()
    # print("Channel available are", y)
    # print(type(y))
    a_list = []
    for i in y:
        a_list.append(i.strip())
    print("hi", a_list)

    if any("Channel 52 : 5.26 GHz" in s for s in a_list):
        print("set channel to 52")
    else:
        print("check for some another channel")

    time.sleep(2)

    thr_2 = threading.Thread(target=dfs.exit_from_ap())
    thr_2.start()
    thr_2.join()
    print("exit")

    time.sleep(20)

    t3 = threading.Thread(target=dfs.set_channel_in_ap_at_52())
    t3.start()
    t3.join()
    print("channel set to 52")

    time.sleep(10)

    thr_3 = threading.Thread(target=dfs.exit_from_ap())
    thr_3.start()
    thr_3.join()
    print("exit")

    time.sleep(10)

    t4 = threading.Thread(target=dfs.create_station_on_GUI_1())
    t4.start()
    t4.join()
    print("station created")

    time.sleep(30)

    t5 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch52(arg1)), args=(que, ""))
    t5.start()
    t5.join()
    print("radar generated")

    time.sleep(60)

    t10 = threading.Thread(target=dfs.wait_for_ip())
    t10.start()
    t10.join()

    print("checking hackrf is oN/OFF")
    print("Hackrf is ON")
    print("press s --> enter --> q to stop hackrf")
    t6 = threading.Thread(dfs.hackrf_status_off())
    t6.start()
    t6.join()
    print("Now hackrf is OFF")

    print("setting channel to 100")

    t7 = threading.Thread(target=dfs.set_channel_in_ap_at_100())
    t7.start()
    t7.join()
    print("channel set  at 100")

    time.sleep(30)

    t8 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch100(arg1)), args=(que, ""))
    t8.start()
    t8.join()
    print("radar generated")

    time.sleep(60)

    t11 = threading.Thread(target=dfs.wait_for_ip())
    t11.start()
    t11.join()

    print("done")

    t12 = threading.Thread(target=dfs.set_channel_in_ap_at_116())
    t12.start()
    t12.join()
    print("channel set hogya at 116")

    time.sleep(30)

    t13 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch116(arg1)), args=(que, ""))
    t13.start()
    t13.join()
    print("radar generated")

    time.sleep(60)

    t14 = threading.Thread(target=dfs.wait_for_ip())
    t14.start()
    t14.join()

    print("done")

    t15 = threading.Thread(target=dfs.set_channel_in_ap_at_136())
    t15.start()
    t15.join()

    time.sleep(30)

    t16 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch136(arg1)), args=(que, ""))
    t16.start()
    t16.join()
    print("radar generated")

    time.sleep(60)

    t17 = threading.Thread(target=dfs.wait_for_ip())
    t17.start()
    t17.join()

    print("done")

    t18 = threading.Thread(target=lambda q, arg1: q.put(dfs.check_log_channel(arg1)), args=(que, ""))
    t18.start()
    threads_list.append(t18)
    t18.join()
    var = que.get()
    print(type(var))
    for i in range(len(var)):
        var[i] = var[i] + "<br>"
        #print(var[i])
    print(var)

    listToStr = ' '.join([str(elem) for elem in var])
    print(listToStr)

    t19 = threading.Thread(target=lambda q, arg1: q.put(dfs.check_for_all_logs(arg1)), args=(que, ""))
    t19.start()
    threads_list.append(t19)
    t19.join()
    var_4 = que.get()

    for i in range(len(var_4)):
        var_4[i] = var_4[i] + "<br>"

    all_log = ' '.join([str(elem) for elem in var_4])

    now = datetime.datetime.now()
    print("Current date and time : ")
    date = now.strftime("%Y-%m-%d %H:%M:%S")

    html_content = "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>DFS TEST </title></head><body><div class='Section report_banner-1000x205' style='background-image:url(\"/home/lanforge/LANforgeGUI_5.4.3/images/OrangeReportHeader.jpg\"); background-size: 1000px; height: 200px;'><div class='HeaderStyle'><br><h1 class='TitleFontPrint' style='color:darkgreen;'>  Dynamic Frequency Selection  </h1><h3 class='TitleFontPrint' style='color:darkgreen;'>" + date + "</h3></div></div><br> <br><h2 align='left'>Objective</h2> <p align='left' width='900'>The DFS Test is designed to test the Performance of the Access Point.Dynamic frequency selection is a technology that is designed to ensure that wireless devices operating in the unlicensed WLAN 5 GHz bands are able to detect when they may be interfering with military and weather radar systems and automatically switch over to another frequency where they will not cause any disturbance. <br><table width='700px' border='1' cellpadding='2' cellspacing='0' style='border-top-color: gray; border-top-style: solid; border-top-width: 1px; border-right-color: gray; border-right-style: solid; border-right-width: 1px; border-bottom-color: gray; border-bottom-style: solid; border-bottom-width: 1px; border-left-color: gray; border-left-style: solid; border-left-width: 1px'><tr><th colspan='2'>Test Setup Information</th></tr><tr><td>Device Under Test</td><td><table width='100%' border='0' cellpadding='2' cellspacing='0' style='border-top-color: gray; border-top-style: solid; border-top-width: 1px; border-right-color: gray; border-right-style: solid; border-right-width: 1px; border-bottom-color: gray; border-bottom-style: solid; border-bottom-width: 1px; border-left-color: gray; border-left-style: solid; border-left-width: 1px'><tr><td>AP Name</td><td colspan='3'>Netgear WAC505</td></tr><tr><td>SSID</td><td colspan='3'>TestAP22</td></tr><tr><td>Number of Clients</td><td colspan='3'>1</td></tr></table></td></tr></table><br> <h2>Testing Results</h2><meta name='viewport' content='width=device-width, initial-scale=1'><style>.accordion {background-color: #eee;color: #444;cursor: pointer;padding: 18px;width: 100%;border: none;text-align: left;outline: none;font-size: 15px;transition: 0.4s;}.active, .accordion:hover {background-color: #ccc;}.panel {padding: 0 18px;display: none;background-color: white;overflow: hidden;}</style><h2></h2><button class='accordion'>All Logs</button><div class='panel'><p>" + all_log + "</p></div><button class='accordion'>Channel logs</button><div class='panel'><p>" + listToStr + "</p></div><script>var acc = document.getElementsByClassName('accordion');var i;for (i = 0; i < acc.length; i++) {acc[i].addEventListener('click', function() {this.classList.toggle('activ');var panel = this.nextElementSibling;if (panel.style.display === 'block') {panel.style.display = 'none';} else {panel.style.display = 'block';}});}</script></body></html>"


    file = open("sample.html", "w")
    file.write(html_content)
    file.close()

    print("Test Finished")

if __name__ == '__main__':
    main()
