"""need to be modified not for testing """

import os
import paramiko
import time
from subprocess import Popen, PIPE, STDOUT
import threading
from queue import Queue
from cx_time import IPv4Test
class DFS_TESTING:
    def __init__(self):
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

    def check_for_channels(self, q):
        self.q = q
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect('192.168.200.143', port=22, username='root', password='Netgear@123xzsawq@!')
        stdin, stdout, stderr = ssh.exec_command('iwlist channel')
        output = stdout.readlines()
        # print('\n'.join(output))
        self.q = output
        time.sleep(1)
        return self.q

    def set_channel_in_ap(self, w):
        self.w = w
        cmd = "conf_set system:wlanSettings:wlanSettingTable:wlan1:channel 52;conf_save"
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect('192.168.200.143', port=22, username='root', password='Netgear@123xzsawq@!')
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.readlines()
        print('\n'.join(output))
        self.w = output
        time.sleep(1)
        return self.w

    def create_station_on_GUI(self, w):
        self.w = w
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
        self.w = var_1
        return self.w

    def generate_radar_at_ch52(self, r):
        self.r = r
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5260000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.r = "Radar detected"
        return self.r

    def generate_radar_at_ch56(self,q):
        self.q =q
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5280000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')

        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.q = "Radar detected"
        return self.q

    def generate_radar_at_ch60(self,w):
        self.w = w
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5300000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.w = "Radar detected"
        return self.w

    def generate_radar_at_ch64(self,e):
        self.e = e
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5320000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.e = "Radar detected"
        return self.e

    def generate_radar_at_ch100(self,f):
        self.f = f
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5500000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.f = "Radar received"
        return self.f

    def generate_radar_at_ch104(self,t):
        self.t = t
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5520000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.t = "Radar detected"
        return self.t

    def generate_radar_at_ch108(self,u):
        self.u=u
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5540000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.u = "Radar detected"
        return self.u

    def generate_radar_at_ch112(self,i):
        self.i=i
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5560000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.i = "Radar detected"
        return self.i

    def generate_radar_at_ch116(self,o):
        self.o =o
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5280000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.o = "Radar detected"
        return self.o

    def generate_radar_at_ch120(self,p):
        self.p=p
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5600000"
        #print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.p = "Radar detected"
        return self.p

    def generate_radar_at_ch124(self,a):
        self.a=a
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5620000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.a = "Radar detected"
        return self.a

    def generate_radar_at_ch128(self,s):
        self.s=s
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5640000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.s = "Radar detected"
        return self.s

    def generate_radar_at_ch132(self,d):
        self.d = d
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5660000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.d = "Radar detected"
        return self.d

    def generate_radar_at_ch136(self,h):
        self.h=h
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5680000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.h = "Radar detected"
        return self.h

    def generate_radar_at_ch140(self,j):
        self.j = j
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5700000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        self.j = "Radar detected"
        return self.j

    def monitor_station_channel(self,m):
        self.m = m
        obj = IPv4Test(_host="localhost",
                       _port=8080,
                       _ssid="TestAP22",
                       _password="[BLANK]",
                       _security="open",
                       _radio="wiphy0")
        obj.cleanup(obj.sta_list)
        var_1 = "station cleaned"
        self.m = var_1
        return self.m

    def check_log(self, r):
        self.r = r
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect('192.168.200.143', port=22, username='root', password='Netgear@123xzsawq@!')
        stdin, stdout, stderr = ssh.exec_command('cat /tmp/log/messages | grep Radar')
        output = stdout.readlines()
        print('\n'.join(output))
        time.sleep(1)
        self.r = output
        return self.r



def main():
    que = Queue()
    dfs = DFS_TESTING()

    print("checking hackrf is oN/OFF")
    print("Hackrf is ON")
    print("press s --> enter --> q to stop hackrf")
    dfs.hackrf_status_off()

    print("Now hackrf is OFF")

    threads_list = []
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

    t2 = threading.Thread(target=lambda q, arg1: q.put(dfs.check_for_channels(arg1)), args=(que, ""))
    t2.start()
    threads_list.append(t2)
    t2.join()
    y = que.get()
    print("Channel available are", y)
    copy_y = y[:]
    del copy_y[21:len(copy_y)]
    # print("hi*********************" ,copy_y)
    a_list = []
    for i in copy_y:
        a_list.append(i.strip())
    # print("hi", a_list)
    """['wifi1vap8  109 channels in total; available frequencies :', 'Channel 36 : 5.18 GHz', 
    'Channel 40 : 5.2 GHz', 'Channel 44 : 5.22 GHz', 'Channel 48 : 5.24 GHz', 'Channel 52 : 5.26 GHz', 
    'Channel 56 : 5.28 GHz', 'Channel 60 : 5.3 GHz', 'Channel 64 : 5.32 GHz', 'Channel 100 : 5.5 GHz',
     'Channel 104 : 5.52 GHz', 'Channel 108 : 5.54 GHz', 'Channel 112 : 5.56 GHz', 'Channel 116 : 5.58 GHz', 
     'Channel 120 : 5.6 GHz', 'Channel 124 : 5.62 GHz', 'Channel 128 : 5.64 GHz', 'Channel 132 : 5.66 GHz', 
    'Channel 136 : 5.68 GHz', 'Channel 140 : 5.7 GHz', 'Current Frequency:5.22 GHz (Channel 44)']"""
    if any("Channel 52 : 5.26 GHz" in s for s in a_list):
        print("set channel to 52")
        t3 = threading.Thread(target=lambda q, arg1: q.put(dfs.set_channel_in_ap(arg1)), args=(que, ""))
        t3.start()
        t3.join()
        print("channel set hogya")

    t4 = threading.Thread(target=lambda q, arg1: q.put(dfs.create_station_on_GUI(arg1)), args=(que, ""))
    t4.start()
    t4.join()
    print("station created")

    t5 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch52(arg1)), args=(que, ""))
    t5.start()
    t5.join()
    print("radar generated")



    print("checking hackrf is oN/OFF")
    print("Hackrf is ON")
    print("press s --> enter --> q to stop hackrf")
    t6 = threading.Thread(dfs.hackrf_status_off())
    t6.start()
    t6.join()
    print("Now hackrf is OFF")

    t7 =threading.Thread(target=lambda q, arg1: q.put(dfs.monitor_station_channel(arg1)), args=(que, ""))
    t7.start()
    threads_list.append(t7)
    t7.join()
    f = que.get()
    print("station cleaned ", f)

    time.sleep(60)

    t8 = threading.Thread(target=lambda q, arg1: q.put(dfs.create_station_on_GUI(arg1)), args=(que, ""))
    t8.start()
    threads_list.append(t8)
    t8.join()
    b = que.get()
    print("station at channel ", b)

    if b == "52":
        print("station is on DFS Channel")
        t9 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch52(arg1)), args=(que, ""))
        t9.start()
        t9.join()
    elif b == "56":
        print("station is on DFS Channel 56")
        t10 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch56(arg1)), args=(que, ""))
        t10.start()
        t10.join()
    elif b == "60":
        print("station is on DFS Channel 60")
        t11 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch60(arg1)), args=(que, ""))
        t11.start()
        t11.join()
    elif b == "64":
        print("station is on DFS Channel 64")
        t12 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch64(arg1)), args=(que, ""))
        t12.start()
        t12.join()
    elif b == "100":
        print("station is on DFS Channel 100")
        t13 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch100(arg1)), args=(que, ""))
        t13.start()
        t13.join()
    elif b == "104":
        print("station is on DFS Channel 104")
        t14 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch104(arg1)), args=(que, ""))
        t14.start()
        t14.join()
    elif b == "108":
        print("station is on DFS Channel 108")
        t15 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch108(arg1)), args=(que, ""))
        t15.start()
        t15.join()
    elif b == "112":
        print("station is on DFS Channel 112")
        t16 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch112(arg1)), args=(que, ""))
        t16.start()
        t16.join()
    elif b == "116":
        print("station is on DFS Channel 116")
        t17 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch116(arg1)), args=(que, ""))
        t17.start()
        t17.join()
    elif b == "120":
        print("station is on DFS Channel 120")
        t18 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch120(arg1)), args=(que, ""))
        t18.start()
        t18.join()
    elif b == "124":
        print("station is on DFS Channel 124")
        t19 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch124(arg1)), args=(que, ""))
        t19.start()
        t19.join()
    elif b == "128":
        print("station is on DFS Channel 128")
        t20 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch128(arg1)), args=(que, ""))
        t20.start()
        t20.join()
    elif b == "132":
        print("station is on DFS Channel 132")
        t21 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch132(arg1)), args=(que, ""))
        t21.start()
        t21.join()
    elif b == "136":
        print("station is on DFS Channel 136")
        t22 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch136(arg1)), args=(que, ""))
        t22.start()
        t22.join()
    elif b == "140":
        print("station is on DFS Channel 140")
        t23 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch140(arg1)), args=(que, ""))
        t23.start()
        t23.join()
    else:
        print("station is on NON DFS Channel")

    print("checking hackrf is oN/OFF")
    print("Hackrf is ON")
    print("press s --> enter --> q to stop hackrf")
    t6 = threading.Thread(dfs.hackrf_status_off())
    t6.start()
    t6.join()
    print("Now hackrf is OFF")

    t24 = threading.Thread(target=lambda q, arg1: q.put(dfs.monitor_station_channel(arg1)), args=(que, ""))
    t24.start()
    threads_list.append(t24)
    t24.join()
    f = que.get()
    print("station cleaned ", f)

    time.sleep(60)

    t25 = threading.Thread(target=lambda q, arg1: q.put(dfs.create_station_on_GUI(arg1)), args=(que, ""))
    t25.start()
    threads_list.append(t25)
    t25.join()
    b = que.get()
    print("station at channel ", b)

    t26 = threading.Thread(target=lambda q, arg1: q.put(dfs.check_log(arg1)), args=(que, ""))
    t26.start()
    threads_list.append(t26)
    t26.join()
    v = que.get()
    print(v)

if __name__ == '__main__':
    main()
Displaying netgear_dfs_15.txt.
