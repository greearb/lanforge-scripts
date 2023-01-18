#!/usr/bin/env python3

"""
NAME: lf_interop_windows_installer.py


PURPOSE:
    This program is used Installing the Lanforge InterOp Server Windows app in Windows Laptop that are connected to Lanforge using ethernet.

EXAMPLE: ./ python3 lf_interop_windows_installer.py  --host 192.168.200.253 --manager_ip 192.168.200.232 --realm=75
            --resource=4 --version=5.4.6 --action=install --machine_user Test2 --machine_pass 90900

Note: To Run this script
    The Windows machine should have ssh installed on the machine before running this script
    The Windows machine should also have jdk and VLC pre installed on it

LICENSE:
    Copyright 2021 Candela Technologies Inc
"""
import sys
import paramiko
import argparse
import socket

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)


class WinAppInstaller:
    def __init__(self,
                 manager_ip="localhost",
                 realm=2,
                 resource=2,
                 machine_user='test1',
                 machine_password='password',
                 host="localhost",
                 version="5.4.6",
                 action="install",
                 _exit_on_fail=False):
        self.mgt_dev = None
        self.version = version
        self.manager_ip = manager_ip
        self.resource = resource
        self.realm = realm
        self.host = host
        self.machine_user = machine_user
        self.machine_password = machine_password
        self.action = action

        if self.host == "localhost":
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            self.host = ip
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.host, username=self.machine_user, password=self.machine_password)

    def start(self):
        if self.action == "install":
            self.install_apk()
            self.configure()
        if self.action == "uninstall":
            self.uninstall()
        if self.action == "upgrade":
            self.upgrade(self.version)
        if self.action == "configure":
            self.configure()

    def install_apk(self):
        # Removed Installing JDK as default As of now
        # stdin, stdout, stderr = self.client.exec_command(
        #     "powershell.exe wget https://download.oracle.com/java/19/latest/jdk-19_windows-x64_bin.exe -O 'C:\jdk.exe'")
        # output = stdout.readline().strip()
        # print("[INSTALLATION] ", output)
        #
        # stdin, stdout, stderr = self.client.exec_command(
        #     "powershell.exe Start-Process -Wait -FilePath 'C:\jdk.exe' -ArgumentList '/S','/v','/qn' -passthru")
        # output = stdout.readline().strip()
        # print("[INSTALLATION] ", output)
        #
        # stdin, stdout, stderr = self.client.exec_command("del  'C:\jdk.exe'")
        # output = stdout.readline().strip()
        # print("[INSTALLATION] ", output)

        stdin, stdout, stderr = self.client.exec_command(
            "powershell.exe wget http://candelatech.com/private/downloads/r5.4.6/LANforge-Server-" + self.version + "-Installer.exe -O 'C:\Lanforge.exe'")
        output = stdout.readline().strip()
        print("[INSTALLATION] ", output)

        stdin, stdout, stderr = self.client.exec_command(
            "powershell.exe Start-Process -Wait -FilePath 'C:\\Lanforge.exe' -ArgumentList '/S','/v','/qn' -passthru ")
        output = stdout.readline().strip()
        print("[INSTALLATION] ", output)

        stdin, stdout, stderr = self.client.exec_command("del 'C:\\Lanforge.exe'")
        output = stdout.readline().strip()
        # print("[DELETION] Removing the exe file form the machine", output)

        print("[SUCCESS] Installation Success\n")

    def upgrade(self, version):
        print("[UPGRADE] Uninstalling the LANForge server")
        self.uninstall()
        stdin, stdout, stderr = self.client.exec_command(
            "powershell.exe wget http://candelatech.com/private/downloads/r5.4.6/LANforge-Server-" + version + "-Installer.exe -O 'C:\Lanforge.exe'")
        output = stdout.readline().strip()
        print("[UP-GRADATION] ", output)

        stdin, stdout, stderr = self.client.exec_command(
            "powershell.exe Start-Process -Wait -FilePath 'C:\\Lanforge.exe' -ArgumentList '/S','/v','/qn' -passthru ")
        output = stdout.readline().strip()
        # print("[UP-GRADATION] ", output)

        stdin, stdout, stderr = self.client.exec_command("del 'C:\\Lanforge.exe'")
        output = stdout.readline().strip()
        print("[UP-GRADATION] ", output)

        print("[UPGRADE] Upgraded Successfully to version " + version + "\n")

    def configure(self):
        stdin, stdout, stderr = self.client.exec_command("echo %USERNAME%")
        user = (stdout.readline()).strip()
        configure_file = "C:\\Users\\" + user + "\\AppData\\Roaming\\config.values"
        # C:\Users\test2\AppData\Roaming\config.values
        # Getting management devices
        self.mgt_dev = ""
        stdin, stdout, stderr = self.client.exec_command("more " + configure_file)
        pre_config_text = (stdout.readlines())
        for i in pre_config_text:
            if "mgt_dev" in i.strip():
                self.mgt_dev = i.strip().split(" ")[1]

        stdin, stdout, stderr = self.client.exec_command("echo " + "add_resource_addr" + " > " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "bind_mgt 1" + " >> " + configure_file)
        print("[CONFIG] Configuring host id")
        stdin, stdout, stderr = self.client.exec_command(
            "echo " + "connect_mgr " + str(self.manager_ip) + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "dev_ignore" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "first_cli_port 4001" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "gps_dev none" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "keepalive 30000" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command(
            "echo " + "log_dir c:\\users\\" + user + "\\appdata\\local\\temp" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "log_file_len 0" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "log_level 7" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "max_tx 5" + " >> " + configure_file)
        print("[CONFIG] Adding management device")
        stdin, stdout, stderr = self.client.exec_command("echo " + "mgt_dev " + self.mgt_dev + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "mode resource" + " >> " + configure_file)
        print("[CONFIG] Configuring realm id")
        stdin, stdout, stderr = self.client.exec_command("echo " + "realm " + str(self.realm) + " >> " + configure_file)
        print("[CONFIG] Configuring resource id")
        stdin, stdout, stderr = self.client.exec_command(
            "echo " + "resource " + str(self.resource) + " >> " + configure_file)
        print("[CONFIG] Configuring shelf id")
        stdin, stdout, stderr = self.client.exec_command("echo " + "shelf 1" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "wl_probe_timer 50" + " >> " + configure_file)
        print("[SUCCESS] Successfully configured")

    def copy(self):
        sftp = self.client.open_sftp()
        sftp.put('/home/lanforge/Desktop/MonkeyRemote-0.5.jar', 'C:\\Users\\Test2\\Desktop')
        sftp.close()

    def uninstall(self):
        print("[UNINSTALLING] Trying to Uninstall the LANforge Server from machine with ip " + self.host)
        try:
            stdin, stdout, stderr = self.client.exec_command(
                "powershell.exe Start-Process -Wait -FilePath 'C:\\Program Files (x86)\\LANforge-Server\\Uninstall.exe' -ArgumentList '/S','/v','/qn' -passthru")
            output = (stderr.readline()).strip()
            # Start-Process : This command cannot be run due to the error: The system cannot find the file specified.
            print(output)
            print("[UNINSTALLED] Success fully Uninstalled")
        except:
            print("App Not installed")


    def get_all_windows_ip(self):
        pass

    def close_session(self):
        print("[END] Closing the ssh Session")
        self.client.close()


def main():
    parser = argparse.ArgumentParser(description="Lanforge Interop App Installer (Please enable developers mode for "
                                                 "all the phones before using this script)")
    parser.add_argument('--host', help='Lanforge IP address on which all the phones are connected', required=True,
                        default='localhost')
    parser.add_argument('--manager_ip', help='Manager IP address for clustering Eg. 192.168.200.14', required=True,
                        default='localhost')
    parser.add_argument('--version', help='Version of the LANforge address for clustering Eg. 5.4.6', required=True,
                        default='2')
    parser.add_argument('--action', help='What action you want to perform Eg. install, uninstall, upgrade ',
                        required=True, default='2')
    parser.add_argument('--machine_pass', help='Windows machine Password Eg. password', required=True,
                        default='password')
    parser.add_argument('--machine_user', help='Windows machine username Eg. user1', required=True, default='user')
    parser.add_argument('--realm', help='Realm address for clustering Eg. 75', default='25')
    parser.add_argument('--resource', help='Resource address for clustering Eg. 4', default='2')

    args = parser.parse_args()
    app_installer = WinAppInstaller(host=args.host,
                                    manager_ip=args.manager_ip,
                                    realm=args.realm,
                                    resource=args.resource,
                                    machine_user=args.machine_user,
                                    machine_password=args.machine_pass,
                                    version=args.version,
                                    action=args.action)
    app_installer.start()
    app_installer.close_session()


if __name__ == "__main__":
    main()
