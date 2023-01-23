#!/usr/bin/env python3

"""
NAME: lf_interop_windows_installer.py


PURPOSE:
    This program is used Installing the Lanforge InterOp Server Windows app in Windows Laptop that are connected to Lanforge using ethernet.

EXAMPLE: ./python3 lf_interop_windows_installer.py  --host 192.168.200.253 192.168.212.65 --manager_ip 192.168.200.238
--realm=85 --resource=4 --version=5.4.6 --action=configure --machine_user Test2 candela --machine_pass 9090 candela

Note: To Run this script
    The Windows machine should have ssh installed on the machine before running this script
    The Windows machine should also have jdk and VLC pre installed on it

LICENSE:
    Copyright 2023 Candela Technologies Inc
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
                 location=None,
                 realm=2,
                 resource=2,
                 machine_user='test1',
                 machine_password='password',
                 host=None,
                 version="5.4.6",
                 action="install",
                 _exit_on_fail=False):
        self.client = None
        self.mgt_dev = None
        self.version = version
        self.location = location
        self.manager_ip = manager_ip
        self.resource = resource
        self.realm = realm
        self.host = host
        self.machine_user = machine_user
        self.machine_password = machine_password
        self.action = action

    def start(self):
        if len(self.machine_user) == 1 and len(self.host) > 1:
            self.machine_password = self.machine_password*(len(self.host))
            print(self.machine_user)
            print(self.machine_password)
            self.machine_user = self.machine_user*(len(self.host))
        for i in range(len(self.host)):
            print("Currently Working for machine having ip address as ", self.host[i])
            self.connect(self.host[i], self.machine_user[i], self.machine_password[i])
            if self.action == "install":
                self.install_apk()
                self.configure()
            if self.action == "uninstall":
                self.uninstall()
            if self.action == "upgrade":
                self.upgrade(self.version)
            if self.action == "configure":
                self.configure()
            if self.action == "start_app":
                self.start_app()
            self.close_session()

    def connect(self, host, machine_user, machine_password):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(host, username=machine_user, password=machine_password)

    def install_apk(self):
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
            "powershell.exe wget http://candelatech.com/private/downloads/r" + version + "/LANforge-Server-" + version + "-Installer.exe -O C:\\LANforge-Server-" + version + "-Installer.exe")
        output = stdout.readline().strip()
        print("[UP-GRADATION] ", output)

        stdin, stdout, stderr = self.client.exec_command(
            "powershell.exe Start-Process -Wait -FilePath C:\\LANforge-Server-" + version + "-Installer.exe -ArgumentList '/S','/v','/qn' -passthru ")
        output = stdout.readline().strip()

        stdin, stdout, stderr = self.client.exec_command("del C:\\LANforge-Server-" + version + "-Installer.exe")
        output = stdout.readline().strip()
        print("[UP-GRADATION] ", output)

        print("[UPGRADE] Upgraded Successfully to version " + version + "\n")

    def start_app(self):
        # Start - Process C:\Users\Test2\AppData\Roaming\start_both.bat - Verb runAs
        # TODO: Runas Administrator is being stuck for now find some other method.
        stdin, stdout, stderr = self.client.exec_command(
            "Start-Process C:\\Users\\Test2\\AppData\\Roaming\\start_both.bat - Verb runAs")
        output = (stdout.readline()).strip()
        print(output)

    def configure(self):
        stdin, stdout, stderr = self.client.exec_command("echo %USERPROFILE%")
        userprofile = (stdout.readline()).strip()
        configure_file = userprofile + "\\AppData\\Roaming\\config.values"
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
        print("[CONFIG] Configuring host id as " + str(self.manager_ip))
        stdin, stdout, stderr = self.client.exec_command(
            "echo " + "connect_mgr " + str(self.manager_ip) + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "dev_ignore" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "first_cli_port 4001" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "gps_dev none" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "keepalive 30000" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command(
            "echo " + "log_dir " + userprofile.lower() + "\\appdata\\local\\temp" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "log_file_len 0" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "log_level 7" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "max_tx 5" + " >> " + configure_file)
        print("[CONFIG] Adding management device as " + self.mgt_dev)
        stdin, stdout, stderr = self.client.exec_command("echo " + "mgt_dev " + self.mgt_dev + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "mode resource" + " >> " + configure_file)
        print("[CONFIG] Configuring realm id as " + str(self.realm))
        stdin, stdout, stderr = self.client.exec_command("echo " + "realm " + str(self.realm) + " >> " + configure_file)
        print("[CONFIG] Configuring resource id as " + str(self.resource))
        stdin, stdout, stderr = self.client.exec_command(
            "echo " + "resource " + str(self.resource) + " >> " + configure_file)
        print("[CONFIG] Configuring shelf id as 1")
        stdin, stdout, stderr = self.client.exec_command("echo " + "shelf 1" + " >> " + configure_file)
        stdin, stdout, stderr = self.client.exec_command("echo " + "wl_probe_timer 50" + " >> " + configure_file)
        print("[SUCCESS] Successfully configured")

    def copy(self):
        sftp = self.client.open_sftp()
        if self.location is None:
            sftp.put("/home/lanforge/LANforge-Server-" + self.version + "-Installer.exe", 'C:\\')
        else:
            sftp.put(self.location + "/LANforge-Server-" + self.version + "-Installer.exe", 'C:\\')
        sftp.close()

    def uninstall(self):
        print("[UNINSTALLING] Trying to Uninstall the LANforge Server")
        try:
            stdin, stdout, stderr = self.client.exec_command(
                "powershell.exe Start-Process -Wait -FilePath 'C:\\Program Files (x86)\\LANforge-Server\\Uninstall.exe'"
                " -ArgumentList '/S','/v','/qn' -passthru")
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
    parser = argparse.ArgumentParser(description="""This program is used for Installing, Uninstalling, Upgrading, 
             Copying and to Configure the LANforge Server on Windows Machine/Laptop that are connected to  
             LANforge using ethernet and have a static IP address. 
             NOTE: The Windows machine should have ssh installed on the machine before running this 
             script and the Windows machine should also have jdk and VLC pre installed on it""")

    parser.add_argument('--host', help='Static IP address on which all the phones are connected', required=True,
                        nargs='+', default='localhost')
    parser.add_argument('--manager_ip', help='Manager IP address for clustering Eg. 192.168.200.14', required=True,
                        default='localhost')
    parser.add_argument('--version', help='Version of the LANforge address for clustering Eg. 5.4.6', required=True,
                        default='2')
    parser.add_argument('--action', help='What action you want to perform Eg. install, uninstall, upgrade ',
                        required=True, default='2')
    parser.add_argument('--machine_pass', help='Windows machine Password Eg. password', required=True, nargs='+',
                        default='password')
    parser.add_argument('--location', help='Location of the executable file without file name Eg. '
                                           '/home/lanforge/ ', default=None)
    parser.add_argument('--machine_user', help='Windows machine username Eg. user1', required=True, nargs='+', default='user')
    parser.add_argument('--realm', help='Realm address for clustering Eg. 75', default='25')
    parser.add_argument('--resource', help='Resource address for clustering Eg. 4', default='2')

    args = parser.parse_args()
    app_installer = WinAppInstaller(host=args.host,
                                    manager_ip=args.manager_ip,
                                    location=args.location,
                                    realm=args.realm,
                                    resource=args.resource,
                                    machine_user=args.machine_user,
                                    machine_password=args.machine_pass,
                                    version=args.version,
                                    action=args.action)
    app_installer.start()


if __name__ == "__main__":
    main()
