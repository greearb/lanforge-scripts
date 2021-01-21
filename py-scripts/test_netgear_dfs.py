""" file under progress not ffor testing - AP R7800
"""


import time
import threading
import os
import paramiko
from queue import Queue
from cx_time import IPv4Test



class DFS_TESTING:


    def _init_(self):
        pass


    def set_dfs_channel_in_ap(self):
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect('192.168.200.190', port=22, username='root', password='Lanforge12345!xzsawq@!')
        stdin, stdout, stderr = ssh.exec_command('conf_set system:wlanSettings:wlanSettingTable:wlan1:channel 52')
        output = stdout.readlines()
        print('\n'.join(output))
        time.sleep(1)
        exit(0)

    def create_station_on_GUI(self,y1,y2):
        global var1
        self.y1 = y1
        self.y2 = y2
        cmd = "python3 sta_cx.py --mgr 192.168.200.13 --num_stations 1 --ssid TestAP95 --passwd lanforge --security wpa2 --radio wiphy0"
        print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/home/lanforge/lanforge-scripts/py-scripts')
        print("Current working directory: {0}".format(os.getcwd()))
        x = os.popen(cmd).read()
        print("station created")
        y1 ='station created'

        with open("data.txt", "w")as f:
            f.write(x)
        f.close()

        file = open("data.txt", "r")
        for i in file:
            if "channel associated is " in i:
                my_list = list(i.split(" "))
                print(my_list[3])
                print(type(my_list[3]))
                var1 = my_list[3]

        print(var1)
        var = var1.replace("\n", "")

        if var == "52" or var == "56" or var == "60" or var == "64" or  var == "100" or var == "104" or var == "108" or var == "112" or var == "116" or var == "120" or var == "124" or var == "128" or var == "132" or var == "136" or var == "140":
            print('Station is on DFS Channel')
            self.y2 = 'station is on DFS Channel'
        else:
            print('Station is on Non DFS channel')
            self.y2 = 'Station is on Non DFS channel'

        return (self.y1 , self.y2)




    ''' ########### HACKRF  ####################### '''


    def generate_radar_at_ch52(self, r):
        self.r = r
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5260000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        #print("Current working directory: {0}".format(os.getcwd()))
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

    def hackrf_status_off(self):
        
        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5220000"
        # print("Current working directory: {0}".format(os.getcwd()))
        os.chdir('/usr/lib64/python2.7/site-packages/')
        # print("Current working directory: {0}".format(os.getcwd()))
        os.system(cmd)
        

    def monitor_station_channel(self,m):
        self.m = m
        obj = IPv4Test(_host="192.168.200.13",
                       _port=8080,
                       _ssid="TestAP95",
                       _password="lanforge",
                       _security="wpa2",
                       _radio="wiphy0")
        obj.cleanup(obj.sta_list)
        obj.build()
        obj.station_profile.admin_up()
        obj.local_realm.wait_for_ip(obj.sta_list)
        time.sleep(30)
        var = obj.json_get("/port/1/1/sta0000?fields=channel")
        var_1 = var['interface']['channel']
        self.m = var_1
        return self.m


    def aps_radio_off(self):
        pass

    def aps_not_switch_automatically(self):
        pass

    def check_ap_channel_switching_time(self):
        pass



def main():




    dfs = DFS_TESTING()

    que = Queue()



    ''' algorithm and sequence to be followed '''

    print("Hackrf is ON")
    print("press s --> enter --> q to stop hackrf")
    dfs.hackrf_status_off()
    print("Now hackrf is OFF")

    #set channel on ap //netgear

    threads_list = []
    t1 = threading.Thread(target=lambda q, arg1, arg2: q.put(dfs.create_station_on_GUI(arg1, arg2)), args=(que, "", ""))
    t1.start()
    threads_list.append(t1)
    t1.join()

    # Check thread's return value
    global my_var

    result = que.get()
    print("hi i reached", result)
    my_var = result

    list_1 = list(my_var)
    print("my list", list_1)

    if any("station is on DFS Channel" in s for s in list_1):
        t2 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch52(arg1)), args=(que, ""))
        t2.start()
        threads_list.append(t2)
        t2.join()
        x = que.get()
        print("result", x)
    else:
        print("radar unreachable")

    t3=threading.Thread(target=lambda q, arg1: q.put(dfs.monitor_station_channel(arg1)), args=(que, ""))
    t3.start()
    threads_list.append(t3)
    t3.join()
    y = que.get()
    print("channel after radar is ", y)

    if y == "52":
        print("station is on DFS Channel")
        t4 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch52(arg1)), args=(que, ""))
        t4.start()
        t4.join()
    elif y == "56":
        print("station is on DFS Channel 56")
        t5 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch56(arg1)), args=(que, ""))
        t5.start()
        t5.join()
    elif y == "60":
        print("station is on DFS Channel 60")
        t6 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch60(arg1)), args=(que, ""))
        t6.start()
        t6.join()
    elif y == "64":
        print("station is on DFS Channel 64")
        t7 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch64(arg1)), args=(que, ""))
        t7.start()
        t7.join()
    elif y == "100":
        print("station is on DFS Channel 100")
        t8 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch100(arg1)), args=(que, ""))
        t8.start()
        t8.join()
    elif y == "104":
        print("station is on DFS Channel 104")
        t9 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch104(arg1)), args=(que, ""))
        t9.start()
        t9.join()
    elif y == "108":
        print("station is on DFS Channel 108")
        t10 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch108(arg1)), args=(que, ""))
        t10.start()
        t10.join()
    elif y == "112":
        print("station is on DFS Channel 112")
        t11 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch112(arg1)), args=(que, ""))
        t11.start()
        t11.join()
    elif y == "116":
        print("station is on DFS Channel 116")
        t12 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch116(arg1)), args=(que, ""))
        t12.start()
        t12.join()
    elif y == "120":
        print("station is on DFS Channel 120")
        t13 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch120(arg1)), args=(que, ""))
        t13.start()
        t13.join()
    elif y == "124":
        print("station is on DFS Channel 124")
        t14 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch124(arg1)), args=(que, ""))
        t14.start()
        t14.join()
    elif y == "128":
        print("station is on DFS Channel 128")
        t15 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch128(arg1)), args=(que, ""))
        t15.start()
        t15.join()
    elif y == "132":
        print("station is on DFS Channel 132")
        t16 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch132(arg1)), args=(que, ""))
        t16.start()
        t16.join()
    elif y == "136":
        print("station is on DFS Channel 136")
        t17 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch136(arg1)), args=(que, ""))
        t17.start()
        t17.join()
    elif y == "140":
        print("station is on DFS Channel 140")
        t18 =threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch140(arg1)), args=(que, ""))
        t18.start()
        t18.join()
    else:
        print("station is on NON DFS Channel")








    """t2 = threading.Thread(target=lambda q, arg1: q.put(dfs.generate_radar_at_ch52(arg1)), args=(que, ""))
    t2.start()
    threads_list.append(t2)
    t2.join()"""




    # Join all the threads
    """for t in threads_list:
        t.join()"""



    """print("my var", my_var)
    empty_list = []
    list = empty_list.append(my_var)
    print("list", list)"""


    '''t2 = threading.Thread(target=dfs.generate_radar_at_ch100())
    t2.start()
    t2.join()
    print("radar received")

    t3 = threading.Thread(target=dfs.create_station_on_GUI())
    t3.start()
    t3.join()
    print("station reassociated")'''




    '''dfs.hackrf_status_off()
    dfs.aps_radio_off()
    dfs.aps_not_switch_automatically()
    #generate radar and check for all dfs channels
    dfs.check_ap_channel_switching_time()
    #after testing turn off hackrf'''






if __name__ == '__main__':
    main()
