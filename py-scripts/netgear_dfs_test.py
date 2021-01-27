import os
import paramiko
import time
import threading
from cx_time import IPv4Test
import argparse
from threading import Thread
from itertools import islice
import datetime
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt


class DFS_Test:

    def __init__(self, ip, user, pswd, host, ssid, passwd, security, radio):
        self.ip = ip
        self.user = user
        self.pswd = pswd
        self.host = host
        self.ssid = ssid
        self.passwd = passwd
        self.security = security
        self.radio = radio

    def check_last_time_ap(self, ip, user, pswd):
        self.ip = ip
        self.user = user
        self.pswd = pswd
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(ip, port=22, username=user, password=pswd)
        stdin, stdout, stderr = ssh.exec_command('cat /tmp/log/messages')
        output = stdout.readlines()
        # print('\n'.join(output))
        time.sleep(10)
        return output

    def create_station_on_GUI_1(self, host, ssid, passwd, security, radio):
        self.host = host
        self.ssid = ssid
        self.passwd = passwd
        self.security = security
        self.radio = radio

        obj = IPv4Test(_host=host,
                       _port=8080,
                       _ssid=ssid,
                       _password=passwd,
                       _security=security,
                       _radio=radio)
        obj.cleanup(obj.sta_list)
        obj.build()
        obj.station_profile.admin_up()
        obj.local_realm.wait_for_ip(obj.sta_list)
        time.sleep(5)
        var = obj.json_get("/port/1/1/sta0000?fields=channel")
        var_1 = (var['interface']['channel'])
        # print(var_1)

        return var_1

    def monitor_station_52(self, host, ssid, passwd, security, radio):
        self.host = host
        self.ssid = ssid
        self.passwd = passwd
        self.security = security
        self.radio = radio

        obj = IPv4Test(_host=host,
                       _port=8080,
                       _ssid=ssid,
                       _password=passwd,
                       _security=security,
                       _radio=radio)
        var = obj.json_get("/port/1/1/sta0000?fields=channel")
        var_1 = (var['interface']['channel'])
        if var_1 == "52":
            print("channel at 52")
        else:
            print("wait untill channel assigned")
            timeout = time.time() + 60 * 15
            while var_1 != "52":
                var = obj.json_get("/port/1/1/sta0000?fields=channel")
                var_1 = var['interface']['channel']
                time.sleep(1)
                if time.time() > timeout:
                    break

        return var_1

    def monitor_station_100(self, host, ssid, passwd, security, radio):
        self.host = host
        self.ssid = ssid
        self.passwd = passwd
        self.security = security
        self.radio = radio

        obj = IPv4Test(_host=host,
                       _port=8080,
                       _ssid=ssid,
                       _password=passwd,
                       _security=security,
                       _radio=radio)
        var = obj.json_get("/port/1/1/sta0000?fields=channel")
        var_1 = (var['interface']['channel'])
        if var_1 == "100":
            print("channel at 100")
        else:
            print("wait untill channel assigned")
            timeout = time.time() + 60 * 15
            while var_1 != "100":
                var = obj.json_get("/port/1/1/sta0000?fields=channel")
                var_1 = var['interface']['channel']
                time.sleep(1)
                if time.time() > timeout:
                    break

        return var_1

    def monitor_station_120(self, host, ssid, passwd, security, radio):
        self.host = host
        self.ssid = ssid
        self.passwd = passwd
        self.security = security
        self.radio = radio

        obj = IPv4Test(_host=host,
                       _port=8080,
                       _ssid=ssid,
                       _password=passwd,
                       _security=security,
                       _radio=radio)
        var = obj.json_get("/port/1/1/sta0000?fields=channel")
        var_1 = (var['interface']['channel'])
        if var_1 == "120":
            print("channel at 120")
        else:
            print("wait untill channel assigned")
            timeout = time.time() + 60 * 15
            while var_1 != "120":
                var = obj.json_get("/port/1/1/sta0000?fields=channel")
                var_1 = var['interface']['channel']
                time.sleep(1)
                if time.time() > timeout:
                    break

        return var_1

    def monitor_station_140(self, host, ssid, passwd, security, radio):
        self.host = host
        self.ssid = ssid
        self.passwd = passwd
        self.security = security
        self.radio = radio

        obj = IPv4Test(_host=host,
                       _port=8080,
                       _ssid=ssid,
                       _password=passwd,
                       _security=security,
                       _radio=radio)
        var = obj.json_get("/port/1/1/sta0000?fields=channel")
        var_1 = (var['interface']['channel'])
        if var_1 == "140":
            print("channel at 140")
        else:
            print("wait untill channel assigned")
            timeout = time.time() + 60 * 2
            while var_1 != "140":
                var = obj.json_get("/port/1/1/sta0000?fields=channel")
                var_1 = var['interface']['channel']
                time.sleep(1)
                if time.time() > timeout:
                    break

        return var_1

    def monitor_untill_channel_assigned(self, host, ssid, passwd, security, radio):
        self.host = host
        self.ssid = ssid
        self.passwd = passwd
        self.security = security
        self.radio = radio

        obj = IPv4Test(_host=host,
                       _port=8080,
                       _ssid=ssid,
                       _password=passwd,
                       _security=security,
                       _radio=radio)
        var = obj.json_get("/port/1/1/sta0000?fields=channel")
        var_1 = (var['interface']['channel'])

        timeout = time.time() + 60 * 5
        while var_1 == "-1":
            var = obj.json_get("/port/1/1/sta0000?fields=channel")
            var_1 = var['interface']['channel']
            time.sleep(1)
            if time.time() > timeout:
                break

        return var_1

    def set_channel_in_ap_at_52(self, ip, user, pswd):
        self.ip = ip
        self.user = user
        self.pswd = pswd
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(ip, port=22, username=user, password=pswd)
        stdin, stdout, stderr = ssh.exec_command('conf_set system:wlanSettings:wlanSettingTable:wlan1:channel 52')
        output = stdout.readlines()
        # print('\n'.join(output))
        time.sleep(10)

    def generate_radar_at_ch52(self):
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5260000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        print("Radar detected")
        time.sleep(1)

    def check_log_channel(self, ip, user, pswd):
        self.ip = ip
        self.user = user
        self.pswd = pswd
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(ip, port=22, username=user, password=pswd)
        stdin, stdout, stderr = ssh.exec_command('cat /tmp/log/messages | grep channel')
        output = stdout.readlines()
        # print('\n'.join(output))
        time.sleep(30)
        return output

    def check_log_info(self, ip, user, pswd):
        self.ip = ip
        self.user = user
        self.pswd = pswd
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(ip, port=22, username=user, password=pswd)
        stdin, stdout, stderr = ssh.exec_command('cat /tmp/log/messages | grep OTHER')
        output = stdout.readlines()
        # print('\n'.join(output))
        time.sleep(30)
        return output

    def check_log_associated(self, ip, user, pswd):
        self.ip = ip
        self.user = user
        self.pswd = pswd
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(ip, port=22, username=user, password=pswd)
        stdin, stdout, stderr = ssh.exec_command('cat /tmp/log/messages | grep associated')
        output = stdout.readlines()
        # print('\n'.join(output))
        time.sleep(30)
        return output

    """def check_log_associated(self, ip, user, pswd):
        self.ip = ip
        self.user = user
        self.pswd = pswd
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(ip, port=22, username=user, password=pswd)
        stdin, stdout, stderr = ssh.exec_command('cat /tmp/log/messages | grep Trig')
        output = stdout.readlines()
        # print('\n'.join(output))
        time.sleep(30)
        return output"""

    def check_for_channels(self, ip, user, pswd):
        self.ip = ip
        self.user = user
        self.pswd = pswd
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(ip, port=22, username=user, password=pswd)
        stdin, stdout, stderr = ssh.exec_command('iwlist wifi1vap0 channel')
        output = stdout.readlines()
        # print('\n'.join(output))
        time.sleep(1)
        return output

    def set_channel_in_ap_at_100(self, ip, user, pswd):
        self.ip = ip
        self.user = user
        self.pswd = pswd
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(ip, port=22, username=user, password=pswd)
        stdin, stdout, stderr = ssh.exec_command('conf_set system:wlanSettings:wlanSettingTable:wlan1:channel 100')
        output = stdout.readlines()
        # print('\n'.join(output))
        time.sleep(30)

    def generate_radar_at_ch100(self):
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5500000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        print("Radar detected")
        time.sleep(20)

    def set_channel_in_ap_at_120(self, ip, user, pswd):
        self.ip = ip
        self.user = user
        self.pswd = pswd
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(ip, port=22, username=user, password=pswd)
        stdin, stdout, stderr = ssh.exec_command('conf_set system:wlanSettings:wlanSettingTable:wlan1:channel 120')
        output = stdout.readlines()
        # print('\n'.join(output))
        time.sleep(30)

    def set_channel_in_ap_at_140(self, ip, user, pswd):
        self.ip = ip
        self.user = user
        self.pswd = pswd
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(ip, port=22, username=user, password=pswd)
        stdin, stdout, stderr = ssh.exec_command('conf_set system:wlanSettings:wlanSettingTable:wlan1:channel 140')
        output = stdout.readlines()
        # print('\n'.join(output))
        time.sleep(30)

    def generate_radar_at_ch120(self):

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5600000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)

    def generate_radar_at_ch140(self):

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5700000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)

    def station_clean(self, host, ssid, passwd, security, radio):
        self.host = host
        self.ssid = ssid
        self.passwd = passwd
        self.security = security
        self.radio = radio

        obj = IPv4Test(_host=host,
                       _port=8080,
                       _ssid=ssid,
                       _password=passwd,
                       _security=security,
                       _radio=radio)
        obj.cleanup(obj.sta_list)
        var_1 = "station cleaned"
        print(var_1)

    def monitor_untill_connection_time(self, host, ssid, passwd, security, radio):
        self.host = host
        self.ssid = ssid
        self.passwd = passwd
        self.security = security
        self.radio = radio

        obj = IPv4Test(_host=host,
                       _port=8080,
                       _ssid=ssid,
                       _password=passwd,
                       _security=security,
                       _radio=radio)
        var = obj.json_get("/port/1/1/sta0000?fields=cx%20time%20(us)")
        var_1 = (var['interface']['cx time (us)'])
        return var_1

    def convert_to_sec(self, time_string):
        self.time_string = time_string
        date_time = datetime.datetime.strptime(self.time_string, "%H:%M:%S")

        print(date_time)

        a_timedelta = date_time - datetime.datetime(1900, 1, 1)
        seconds = a_timedelta.total_seconds()
        return seconds


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        # print(type(self._target))
        if self._target is not None:
            # self._return = self._target(*self._args, **self._kwargs)
            self._return = self._target

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def main():
    parser = argparse.ArgumentParser(description="Netgear AP DFS Test Script")
    parser.add_argument('-i', '--ip', type=str, help='AP ip')
    parser.add_argument('-u', '--user', type=str, help='credentials login/username')
    parser.add_argument('-p', '--pswd', type=str, help='credential password')
    parser.add_argument('-hst', '--host', type=str, help='host name')
    parser.add_argument('-s', '--ssid', type=str, help='ssid for client')
    parser.add_argument('-pwd', '--passwd', type=str, help='password to connect to ssid')
    parser.add_argument('-sec', '--security', type=str, help='security')
    parser.add_argument('-rad', '--radio', type=str, help='radio at which client will be connected')

    args = parser.parse_args()

    dfs = DFS_Test(args.ip, args.user, args.pswd, args.host, args.ssid, args.passwd, args.security, args.radio)

    # check for last timesnap of ap logs

    th = ThreadWithReturnValue(target=dfs.check_last_time_ap(args.ip, args.user, args.pswd))
    th.start()
    th.join()
    val = th.join()
    N = 1
    res = list(islice(reversed(val), 0, N))
    res.reverse()
    x_list = res
    var_1 = ""
    for i in x_list[0][10:20]:
        var_1 = var_1 + i

    var_1 = var_1.strip()
    print(var_1)
    print("timesnap for last log is ", var_1)

    print("creating station on GUI")
    t1 = ThreadWithReturnValue(
        target=dfs.create_station_on_GUI_1(args.host, args.ssid, args.passwd, args.security, args.radio))
    t1.start()
    t1.join()
    val_1 = t1.join()
    val_1 = val_1.strip()
    print("station is at channel", val_1)

    time.sleep(2)

    print("set channel to 52")
    t2 = ThreadWithReturnValue(target=dfs.set_channel_in_ap_at_52(args.ip, args.user, args.pswd))
    t2.start()
    t2.join()

    print("channel set checking....")
    t3 = ThreadWithReturnValue(target=dfs.monitor_station_52(args.host, args.ssid, args.passwd, args.security, args.radio))
    t3.start()
    t3.join()
    print(t3.join())

    var_5 = ""
    time_1 = ""
    channel = ""
    cx_time = ""
    while True:
        if t3.join() == "52":
            print("station allocated to 52")
            print("now generate radar on 52")

            t4 = threading.Thread(target=dfs.generate_radar_at_ch52())
            t4.start()
            t4.join()

            # time.sleep(80)

            print("checking channel assigned...")
            th_1 = ThreadWithReturnValue(target=dfs.monitor_untill_channel_assigned(args.host, args.ssid, args.passwd, args.security,args.radio))
            th_1.start()
            th_1.join()
            print(th_1.join())
            channel = th_1.join()
            print("after radar channel is at ", channel)

            if channel == "-1":
                print("TEST Fail")
                print("AP is at AUTO Channel")
                break
            else:
                print("Test Pass")

                th_2 = ThreadWithReturnValue(target=dfs.monitor_untill_connection_time(args.host, args.ssid, args.passwd, args.security,args.radio))
                th_2.start()
                th_2.join()
                print(th_2.join())
                cx_time = th_2.join()
                print("after radar station time is ", cx_time)
            break
        else:
            print("stop")
            break

    time.sleep(120)
    t9 = ThreadWithReturnValue(target=dfs.check_for_channels(args.ip, args.user, args.pswd))
    t9.start()
    t9.join()
    var1 = t9.join()
    a_list = []
    for i in var1:
        a_list.append(i.strip())
    # print("hi", a_list)

    time_11 = ""
    var5 = ""
    channel_1 = ""
    cx_time1 = ""
    if any("Channel 100 : 5.5 GHz" in s for s in a_list):
        print("set channel to 100")
        t10 = threading.Thread(target=dfs.set_channel_in_ap_at_100(args.ip, args.user, args.pswd))
        t10.start()
        t10.join()
        print("channel set to 100")

        print("channel set checking....")
        t31 = ThreadWithReturnValue(
            target=dfs.monitor_station_100(args.host, args.ssid, args.passwd, args.security, args.radio))
        t31.start()
        t31.join()
        print(t31.join())

        while True:
            if t31.join() == "100":
                print("station allocated to 100")
                print("now generate radar on 100")

                t11 = threading.Thread(target=dfs.generate_radar_at_ch100())
                t11.start()
                t11.join()

                # time.sleep(80)
                print("checking channel assigned...")
                th_1a = ThreadWithReturnValue(
                    target=dfs.monitor_untill_channel_assigned(args.host, args.ssid, args.passwd, args.security,
                                                               args.radio))

                th_1a.start()
                th_1a.join()
                print(th_1a.join())
                channel_1 = th_1a.join()
                print("after radar channel is at ", channel_1)

                if th_1a.join() == "-1":
                    print("TEST Fail")
                    break
                else:
                    print("Test Pass")
                    th_3 = ThreadWithReturnValue(
                        target=dfs.monitor_untill_connection_time(args.host, args.ssid, args.passwd, args.security,
                                                                  args.radio))
                    th_3.start()
                    th_3.join()
                    print(th_3.join())
                    cx_time1 = th_3.join()
                    print("after radar station connection time i ", cx_time1)
                    break

            else:
                print("check for some another channel")
                break

    time.sleep(120)

    t19 = ThreadWithReturnValue(target=dfs.check_for_channels(args.ip, args.user, args.pswd))
    t19.start()
    t19.join()
    var11 = t19.join()
    b_list = []
    for i in var11:
        b_list.append(i.strip())
    # print("hi", a_list)

    time_12 = ""
    var51 = ""
    channel_2 = ""
    cx_time2 = ""
    if any("Channel 120 : 5.6 GHz" in s for s in b_list):
        print("set channel to 120")

        t15 = threading.Thread(target=dfs.set_channel_in_ap_at_120(args.ip, args.user, args.pswd))
        t15.start()
        t15.join()
        print("channel set to 120")

        print("channel set checking....")
        t32 = ThreadWithReturnValue(
            target=dfs.monitor_station_120(args.host, args.ssid, args.passwd, args.security, args.radio))
        t32.start()
        t32.join()
        print(t32.join())
        while True:
            if t32.join() == "120":
                print("station allocated to 120")
                print("now generate radar on 120")

                t16 = threading.Thread(target=dfs.generate_radar_at_ch120())
                t16.start()
                t16.join()

                # time.sleep(80)

                print("checking channel assigned...")
                thr1 = ThreadWithReturnValue(
                    target=dfs.monitor_untill_channel_assigned(args.host, args.ssid, args.passwd, args.security,
                                                               args.radio))
                thr1.start()
                thr1.join()
                print(thr1.join())
                channel_2 = thr1.join()
                print("after radar channel is at ", channel_2)

                if thr1.join() == "-1":
                    print("TEST Fail")
                    break
                else:
                    print("Test Pass")
                    th_4 = ThreadWithReturnValue(
                        target=dfs.monitor_untill_connection_time(args.host, args.ssid, args.passwd, args.security,
                                                                  args.radio))
                    th_4.start()
                    th_4.join()
                    print(th_4.join())
                    cx_time2 = th_4.join()
                    print("after radar station connection time is ", cx_time2)
                    break
            else:
                print("stop")
                break

    # channel list
    ch_list = []
    ch_list.extend((channel, channel_1, channel_2))
    print("after radar switched channel list ", ch_list)

    cha_list = ["52", "100", "120"]
    print("test channel list", cha_list)

    time_ass = []
    time_ass.extend((cx_time, cx_time1, cx_time2))
    print("list of connection time", time_ass)


    """ch_list = ['44', '36', '120']
    for n, i in enumerate(ch_list):
        if i == '':
            ch_list[n] = '0'

    # print(ch_list)
    for i in range(0, len(ch_list)):
        ch_list[i] = int(ch_list[i])

        # print(ch_list)
    cha_list = ['52', '100', '120']
    y_pos = np.arange(len(cha_list))

    # Create bars and choose color
    plt.bar(y_pos, ch_list, color=(0.5, 0.1, 0.5, 0.6))

    # Add title and axis names
    plt.title('channel association')
    plt.xlabel('Channels')
    plt.ylabel('channel assigned')

    # Limits for the Y axis
    plt.ylim(0, 140)

    # Create names
    plt.xticks(y_pos, cha_list)

    # Show graphic
    #plt.show()
    plt.savefig("channel.png")"""

    ###############################################################################

    time_ass = ['23348', '19126', '']
    for n, i in enumerate(time_ass):
        if i == '':
            time_ass[n] = '0'

    # print(ch_list)
    for i in range(0, len(time_ass)):
        time_ass[i] = int(time_ass[i])

        # seconds = microseconds ÷ 1,000,000
    for i in range(0, len(time_ass)):
        time_ass[i] = time_ass[i] / 1000

    cha_list = ['52', '100', '120']
    y_pos = np.arange(len(cha_list))

    # Create bars and choose color
    plt.bar(y_pos, time_ass, color=(0.5, 0.1, 0.5, 0.6))

    # Add title and axis names
    plt.title('connection time')
    plt.xlabel('Channels')
    plt.ylabel('association time (milliseconds)')

    # Limits for the Y axis
    plt.ylim(0, 100)

    # Create names
    plt.xticks(y_pos, cha_list)

    # Show graphic
    #plt.show()
    plt.savefig("/home/lanforge/lanforge-scripts/py-scripts/time.png")
    '''data = "pass"
    data_1 = "Fail"
    data_2 = "pass"
    ch_list = ['44', '36', '120']'''
    for i in range(0, len(time_ass)):
        time_ass[i] = str(time_ass[i])

    if ch_list[0] == "52" or ch_list[0] == "-1" or ch_list[0] == "" or ch_list[0] == "0":
        data = "FAIL"
    else:
        data = "PASS"

    if ch_list[1] == "100" or ch_list[1] == "-1" or ch_list[1] == "" or ch_list[1] == "0":
        data_1 = "FAIL"
    else:
        data_1 = "PASS"

    if ch_list[2] == "120" or ch_list[2] == "-1" or ch_list[2] == "" or ch_list[2] == "0":
        data_2 = "FAIL"
    else:
        data_2 = "PASS"



    now = datetime.now()
    print("Current date and time : ")
    date_1 = now.strftime("%Y-%m-%d %H:%M:%S")

    html_content = "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>DFS TEST </title></head><body><div class='Section report_banner-1000x205' style='background-image:url(\"/home/lanforge/LANforgeGUI_5.4.3/images/OrangeReportHeader.jpg\"); background-size: 1000px; height: 200px;'><div class='HeaderStyle'><br><h1 class='TitleFontPrint' style='color:darkgreen;'>  Dynamic Frequency Selection  </h1>" \
                   "<h3 class='TitleFontPrint' style='color:darkgreen;'>" + date_1 + "</h3></div></div><br> <br><h3 align='left'>Objective</h3> <p align='left' width='900'>The DFS Test is designed to test the Performance of the Netgear Access Point.Dynamic frequency selection is a technology that is designed to ensure that wireless devices operating in the unlicensed WLAN 5 GHz bands are able to detect when they may be interfering with military and weather radar systems and automatically switch over to another frequency where they will not cause any disturbance. <br><table width='700px' border='1' cellpadding='2' cellspacing='0' style='border-top-color: gray; border-top-style: solid; border-top-width: 1px; border-right-color: gray; border-right-style: solid; border-right-width: 1px; border-bottom-color: gray; border-bottom-style: solid; border-bottom-width: 1px; border-left-color: gray; border-left-style: solid; border-left-width: 1px'><tr><th colspan='2'>Test Setup Information</th></tr><tr><td>Device Under Test</td><td><table width='100%' border='0' cellpadding='2' cellspacing='0' style='border-top-color: gray; border-top-style: solid; border-top-width: 1px; border-right-color: gray; border-right-style: solid; border-right-width: 1px; border-bottom-color: gray; border-bottom-style: solid; border-bottom-width: 1px; border-left-color: gray; border-left-style: solid; border-left-width: 1px'><tr><td>AP Name</td><td colspan='3'>Netgear WAC505</td></tr><tr><td>SSID</td><td colspan='3'>TestAP22</td></tr><tr><td>Number of Clients</td><td colspan='3'>1</td></tr></table></td></tr></table> " \
                                                                                     "<br><h3>Graph</h3> <img align='center' style='padding:15;margin:5;width:400px;' src='time.png' border='0' /> <br><table width='1000px' border='1' cellpadding='2' cellspacing='0' ><tr><th colspan='2'>Detailed Results</th></tr><table width='1000px' border='1'><tr><th>Client Name</th><th>Channel</th><th>Switched Channel</th><th>station association time(milliseconds)</th><th>Result</th></tr><tr><td>sta0000</td><td>52</td><td>"+ ch_list[0] +"</td><td>"+ time_ass[0] +"</td><td>"+ data +"</td></tr><tr><td>sta0000</td><td>100</td><td>"+ ch_list[1] + "</td><td>"+ time_ass[1] +"</td><td>"+ data_1 +"</td></tr><tr><td>sta0000</td><td>120</td><td>"+ ch_list[2] +"</td><td>"+ time_ass[2] +"</td><td>"+ data_2 +"</td></tr></table>"

    file = open("dfs.html", "w")
    file.write(html_content)
    file.close()

    print("Test Finished")

if __name__ == '__main__':
    main()
