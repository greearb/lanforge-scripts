import paramiko
import time
import argparse


class Netgear:
    def __init__(self, ip, user, pswd, port=22):
        self.ip = ip
        self.user = user
        self.pswd = pswd
        self.port = port

    def set_channel_in_ap_at_(self, channel, model):
        if model == "dual":
            channel = str(channel)

            ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
            ssh.connect(self.ip, port=self.port, username=self.user, password=self.pswd, banner_timeout=600)
            command = "conf_set system:wlanSettings:wlanSettingTable:wlan1:channel " + channel
            stdin, stdout, stderr = ssh.exec_command(str(command))
            stdout.readlines()
            ssh.close()
            # print('\n'.join(output))
            time.sleep(10)
        elif model == "triband":
            channel = str(channel)
            if channel == "52" or channel == "56" or channel == "60" or channel == "64":
                ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
                ssh.connect(self.ip, port=self.port, username=self.user, password=self.pswd, banner_timeout=600)
                command = "conf_set system:wlanSettings:wlanSettingTable:wlan1:channel " + channel
                stdin, stdout, stderr = ssh.exec_command(str(command))
                stdout.readlines()
                ssh.close()
                # print('\n'.join(output))
                time.sleep(10)

            elif channel == "100" or channel == "104" or channel == "108" or channel == "112" or channel == "116" or channel == "120" or channel == "124" or channel == "128" or channel == "132" or channel == "136" or channel == "140":
                ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
                ssh.connect(self.ip, port=self.port, username=self.user, password=self.pswd, banner_timeout=600)
                command = "conf_set system:wlanSettings:wlanSettingTable:wlan2:channel " + channel
                stdin, stdout, stderr = ssh.exec_command(str(command))
                stdout.readlines()
                ssh.close()
                # print('\n'.join(output))
                time.sleep(10)

    def check_radar_time(self):
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(self.ip, port=self.port, username=self.user, password=self.pswd, banner_timeout=600)
        stdin, stdout, stderr = ssh.exec_command('cat /tmp/log/messages | grep Radar')
        output = stdout.readlines()
        # print('\n'.join(output))
        ssh.close()
        time.sleep(1)
        return output

    def ap_reboot(self):
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(self.ip, port=self.port, username=self.user, password=self.pswd, banner_timeout=600)
        stdin, stdout, stderr = ssh.exec_command('reboot')
        stdout.readlines()
        ssh.close()
        time.sleep(10)

    def monitor_channel_available_time(self):
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(self.ip, port=self.port, username=self.user, password=self.pswd, banner_timeout=600)
        stdin, stdout, stderr = ssh.exec_command('iwlist channel ')
        output = stdout.readlines()
        # print('\n'.join(output))
        ssh.close()
        time.sleep(1)
        return output

    def get_ap_model(self):
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(self.ip, port=self.port, username=self.user, password=self.pswd)
        stdin, stdout, stderr = ssh.exec_command('printmd')
        output = stdout.readlines()
        ssh.close()
        return output

    def fiveg_low_on_off(self, status):
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(self.ip, port=self.port, username=self.user, password=self.pswd)
        cmd = 'ifconfig wifi1 ' + str(status)
        stdin, stdout, stderr = ssh.exec_command(str(cmd))
        output = stdout.readlines()
        ssh.close()
        return output

    def fiveg_high_on_off(self, status):
        ssh = paramiko.SSHClient()  # creating shh client object we use this object to connect to router
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # automatically adds the missing host key
        ssh.connect(self.ip, port=self.port, username=self.user, password=self.pswd)
        cmd = 'ifconfig wifi2 ' + str(status)
        stdin, stdout, stderr = ssh.exec_command(str(cmd))
        output = stdout.readlines()
        ssh.close()
        return output


def main():
    parser = argparse.ArgumentParser(description="Netgear AP DFS Test Script")
    parser.add_argument('--ip', type=str, help='AP ip')
    parser.add_argument('--user', type=str, help='credentials login/username')
    parser.add_argument('--pswd', type=str, help='credential password')
    parser.add_argument('--ssh_port', type=int, help="ssh port eg 22", default=22)
    args = parser.parse_args()

    netgear = Netgear(ip=args.ip, user=args.user, pswd=args.pswd, port=args.ssh_port)
    netgear.set_channel_in_ap_at_(channel=52, model="dual")
    netgear.check_radar_time()
    netgear.ap_reboot()
    netgear.monitor_channel_available_time()
    netgear.get_ap_model()
    netgear.fiveg_low_on_off(status="up")
    netgear.fiveg_high_on_off(status="down")


if __name__ == '__main__':
    main()
