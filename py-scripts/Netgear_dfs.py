""" file under progress not ffor testing

"""





import time

import threading

import os

import paramiko

from queue import Queue

from cx_time import IPv4Test







class DFS_TESTING:





    def __init__(self):

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



    def generate_radar_at_ch56(self):

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5280000"

        # print("Current working directory: {0}".format(os.getcwd()))

        os.chdir('/usr/lib64/python2.7/site-packages/')

        # print("Current working directory: {0}".format(os.getcwd()))

        os.system(cmd)



    def generate_radar_at_ch60(self):

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5300000"

        # print("Current working directory: {0}".format(os.getcwd()))

        os.chdir('/usr/lib64/python2.7/site-packages/')

        # print("Current working directory: {0}".format(os.getcwd()))

        os.system(cmd)



    def generate_radar_at_ch64(self):

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5320000"

        # print("Current working directory: {0}".format(os.getcwd()))

        os.chdir('/usr/lib64/python2.7/site-packages/')

        # print("Current working directory: {0}".format(os.getcwd()))

        os.system(cmd)



    def generate_radar_at_ch100(self,r):

        self.r = r

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5500000"

        # print("Current working directory: {0}".format(os.getcwd()))

        os.chdir('/usr/lib64/python2.7/site-packages/')

        # print("Current working directory: {0}".format(os.getcwd()))

        os.system(cmd)

        self.r = "Radar received"

        return self.r



    def generate_radar_at_ch104(self):

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5520000"

        # print("Current working directory: {0}".format(os.getcwd()))

        os.chdir('/usr/lib64/python2.7/site-packages/')

        # print("Current working directory: {0}".format(os.getcwd()))

        os.system(cmd)



    def generate_radar_at_ch108(self):

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5540000"

        # print("Current working directory: {0}".format(os.getcwd()))

        os.chdir('/usr/lib64/python2.7/site-packages/')

        # print("Current working directory: {0}".format(os.getcwd()))

        os.system(cmd)



    def generate_radar_at_ch112(self):

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5560000"

        # print("Current working directory: {0}".format(os.getcwd()))

        os.chdir('/usr/lib64/python2.7/site-packages/')

        # print("Current working directory: {0}".format(os.getcwd()))

        os.system(cmd)



    def generate_radar_at_ch116(self):

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5280000"

        # print("Current working directory: {0}".format(os.getcwd()))

        os.chdir('/usr/lib64/python2.7/site-packages/')

        # print("Current working directory: {0}".format(os.getcwd()))

        os.system(cmd)



    def generate_radar_at_ch120(self):

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5600000"

        #print("Current working directory: {0}".format(os.getcwd()))

        os.chdir('/usr/lib64/python2.7/site-packages/')

        # print("Current working directory: {0}".format(os.getcwd()))

        os.system(cmd)



    def generate_radar_at_ch124(self):

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5620000"

        # print("Current working directory: {0}".format(os.getcwd()))

        os.chdir('/usr/lib64/python2.7/site-packages/')

        # print("Current working directory: {0}".format(os.getcwd()))

        os.system(cmd)



    def generate_radar_at_ch128(self):

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5640000"

        # print("Current working directory: {0}".format(os.getcwd()))

        os.chdir('/usr/lib64/python2.7/site-packages/')

        # print("Current working directory: {0}".format(os.getcwd()))

        os.system(cmd)



    def generate_radar_at_ch132(self):

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5660000"

        # print("Current working directory: {0}".format(os.getcwd()))

        os.chdir('/usr/lib64/python2.7/site-packages/')

        # print("Current working directory: {0}".format(os.getcwd()))

        os.system(cmd)



    def generate_radar_at_ch136(self):

        cmd = "sudo python lf_hackrf.py --pulse_width 1 --pulse_interval 1428 --pulse_count 18 --sweep_time 1000 --freq 5680000"

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



    if (y != "52"):

        print("station is on Non DFS Channel")

    else:

        print("station is on DFS Channel")

















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


