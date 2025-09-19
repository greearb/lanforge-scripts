#!/usr/bin/python3

r"""
NAME:       lf_update.py

PURPOSE:    Update a lanforge system via kinstall, reboot, and run check_large_files.

NOTES:      This script is used to help to automate lanforge update

EXAMPLE:    # Updating a LANforge cli
            ./lf_update.py \
            --mgr 192.168.50.103 \
            --root_user root \
            --root_password lanforge \
            --user lanforge \
            --user_password lanforge \
            --mgr_ssh_port 22\
            --lfver 5.5.1\
            --kver 6.15.6+\
            --log_level info

            # Updating a LANforge Vscode json
            // ./lf_update.py
            "args":[
            "--mgr", "192.168.50.103",
            "--root_user", "root",
            "--root_password", "lanforge",
            "--user", "lanforge",
            "--user_password", "lanforge",
            "--mgr_ssh_port", "22",
            "--log_level","info",
            "--lfver","5.5.1",
            "--kver","6.15.6+"
            "--log_level","info"
            ]

SCRIPT_CLASSIFICATION : Tool

SCRIPT_CATEGORIES:   installation

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2025 Candela Technologies Inc


INCLUDE_IN_README

"""
from contextlib import contextmanager

import scrapli
from scrapli.driver import GenericDriver, Driver
import paramiko
import time

import argparse
import os
import importlib
import logging
import sys

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("lf_logger_config")


if sys.version_info[0] != 3:
    logger.critical("This script requires Python 3")
    exit(1)


# from time import sleep


if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()


def get_jump_function(params: dict):
    def jump_through_vrf(conn: Driver):
        # ./vrf_exec.bash eth1 ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa root@192.168.215.113

        # jump_cmd = f'./vrf_exec.bash eth1 ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa root@192.168.215.113'
        jump_cmd = './vrf_exec.bash eth1 ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa root@192.168.215.113'

        # This happens after login completes
        conn.channel.send_input(jump_cmd, eager=True, strip_prompt=False)
        conn.channel._read_until_explicit_prompt(prompts=["password:"])
        conn.channel.send_inputs_interact(
            interact_events=[
                (params['auth_password'], "Password:", True)
            ],
            interaction_complete_patterns=[
                "#"
            ]
        )
        # At this point we should be logged into the dut and need to change the prompt pattern
        conn.comms_prompt_pattern = params['comms_prompt_pattern']

    return jump_through_vrf


class create_lanforge_object:
    def __init__(self,
                 **kwargs
                 ):

        if "mgr" in kwargs:
            self.mgr = kwargs["mgr"]

        if "user" in kwargs:
            self.user = kwargs["user"]

        if "user_password" in kwargs:
            self.user_password = kwargs["user_password"]

        if "root_user" in kwargs:
            self.root_user = kwargs["root_user"]

        if "root_password" in kwargs:
            self.root_password = kwargs["root_password"]

        if "mgr_ssh_port" in kwargs:
            self.mgr_ssh_port = kwargs["mgr_ssh_port"]

        if "lfver" in kwargs:
            self.lfver = kwargs["lfver"]

        if "kver" in kwargs:
            self.kver = kwargs["kver"]

        if "user_timeout" in kwargs:
            self.user_timeout = kwargs["user_timeout"]

        if "root_timeout" in kwargs:
            self.root_timeout = kwargs["root_timeout"]

        self.gui_resourse = kwargs["gui_resourse"]

        self.lanforge_system_node_version = None
        self.lanforge_system_reboot = None
        self.timeout = 2
        self.interval = 5
        self.max_iterations = 24

    def __del__(self) -> None:
        self.tear_down_mgmt()

    def tear_down_mgmt(self) -> None:
        pass
        if getattr(self, "conn", None) is not None:
            self.conn.close()
            self.conn = None

    # not used left in for reference
    def reboot_lf_with_paramiko(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.mgr, port=self.mgr_ssh_port, username=self.root_user, password=self.root_password,
                    allow_agent=False, look_for_keys=False, banner_timeout=600)
        stdin, stdout, stderr = ssh.exec_command('reboot')
        self.lanforge_system_node_version = stdout.readlines()
        self.lanforge_system_node_version = [line.replace(
            '\n', '') for line in self.lanforge_system_node_version]
        ssh.close()
        time.sleep(1)
        return self.lanforge_system_reboot

    def get_lanforge_kernel_version(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.mgr, port=self.mgr_ssh_port, username=self.user, password=self.user_password,
                    allow_agent=False, look_for_keys=False, banner_timeout=600)
        stdin, stdout, stderr = ssh.exec_command('uname -a')
        self.lanforge_kernel_version = stdout.readlines()
        self.lanforge_kernel_version = [line.replace(
            '\n', '') for line in self.lanforge_kernel_version]
        ssh.close()
        time.sleep(1)
        return self.lanforge_kernel_version

    def get_lanforge_server_version(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.mgr, port=self.mgr_ssh_port, username=self.user, password=self.user_password,
                    allow_agent=False, look_for_keys=False, banner_timeout=600)
        stdin, stdout, stderr = ssh.exec_command(
            './btserver --version | grep  Version')
        self.lanforge_server_version_full = stdout.readlines()
        self.lanforge_server_version_full = [line.replace(
            '\n', '') for line in self.lanforge_server_version_full]
        logger.info("lanforge_server_version_full: {lanforge_server_version_full}".format(
            lanforge_server_version_full=self.lanforge_server_version_full))
        self.lanforge_server_version = self.lanforge_server_version_full[0].split(
            'Version:', maxsplit=1)[-1].split(maxsplit=1)[0]
        self.lanforge_server_version = self.lanforge_server_version.strip()
        logger.info("lanforge_server_version: {lanforge_server_version}".format(
            lanforge_server_version=self.lanforge_server_version))
        ssh.close()
        time.sleep(1)
        return self.lanforge_server_version_full

    def get_lanforge_gui_version(self):
        if self.gui_resourse:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.mgr, port=self.mgr_ssh_port, username=self.user, password=self.user_password,
                        allow_agent=False, look_for_keys=False, banner_timeout=600)
            stdin, stdout, stderr = ssh.exec_command(
                'curl -H "Accept: application/json" http://{lanforge_ip}:8080 | json_pp  | grep -A 7 "VersionInfo"'.format(lanforge_ip=self.mgr))
            self.lanforge_gui_version_full = stdout.readlines()
            logger.info("lanforge_gui_version_full pre: {lanforge_gui_version_full}".format(lanforge_gui_version_full=self.lanforge_gui_version_full))
            self.lanforge_gui_version_full = [line.replace(
                '\n', '') for line in self.lanforge_gui_version_full]
            # logger.info("lanforge_gui_version_full: {lanforge_gui_version_full}".format(lanforge_gui_version_full=self.lanforge_gui_version_full))
            for element in self.lanforge_gui_version_full:
                if "BuildVersion" in element:
                    ver_str = str(element)
                    self.lanforge_gui_version = ver_str.split(
                        ':', maxsplit=1)[-1].replace(',', '')
                    self.lanforge_gui_version = self.lanforge_gui_version.strip().replace('"', '')
                    logger.info("BuildVersion {}".format(
                        self.lanforge_gui_version))
                if "BuildDate" in element:
                    gui_str = str(element)
                    self.lanforge_gui_build_date = gui_str.split(
                        ':', maxsplit=1)[-1].replace(',', '')
                    logger.info("BuildDate {}".format(
                        self.lanforge_gui_build_date))
                if "GitVersion" in element:
                    git_sha_str = str(element)
                    self.lanforge_gui_git_sha = git_sha_str.split(
                        ':', maxsplit=1)[-1].replace(',', '')
                    logger.info("GitVersion {}".format(
                        self.lanforge_gui_git_sha))
            else:
                self.lanforge_gui_version = "NA"
                self.lanforge_gui_build_data = "NA"
                self.lanforge_gui_get_shaw = "NA"

    def check_system_status(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Attempt to connect to the server
        # try for a minute
        interations = 0
        while interations < 10:
            try:
                ssh.connect(hostname=self.mgr, port=self.mgr_ssh_port, username=self.root_user, password=self.root_password)
                print("System is up!")
                break
            except (paramiko.ssh_exception.NoValidConnectionsError, paramiko.ssh_exception.AuthenticationException):
                print("System is down, retrying in 5 seconds...")
                time.sleep(5)  # Wait before retrying
                interations += 1

        # Execute a command to confirm the system is operational
        stdin, stdout, stderr = ssh.exec_command("uptime")
        print(stdout.read().decode())

        ssh.close()

    # TODO move to using scrapli and check for prompt
    def check_large_files(self):
        command = "'/home/lanforge/scripts/check_large_files.bash -d -t -a'"
        r = self.send_lf_command(command)
        if r.failed:
            raise Exception(r.result)

        print(f"command: {command}: {r.result}")

    def remove_DB_gz(self):

        command = "rm DB*.gz"
        r = self.send_lf_command(command)
        if r.failed:
            raise Exception(r.result)

        print(f"command: {command}: {r.result}")

    def start_gui(self):
        # creating shh client object we use this object to connect to router
        command = 'nohup /home/lanforge/LANforgeGUI_5.1.1/lfclient.bash -s localhost &'
        r = self.send_lf_command(command)
        if r.failed:
            raise Exception(r.result)
        print(f"command: {command}: {r.result}")

    def check_system_up(self):
        iterations = 0
        while True:
            iterations = iterations + 1
            if iterations > self.max_iterations:
                print(f"Connection failed: iterations {iterations} > max_iterations {self.max_iterations}")
                break

            try:
                # Create a new SSH client
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                # Set the timeout for the connection
                ssh.connect(hostname=self.mgr, port=self.mgr_ssh_port, username=self.root_user, password=self.root_password, timeout=self.timeout)

                # client.connect(hostname, port=port, username=username, password=password, timeout=timeout)
                print(f"System {self.mgr} is up!")
                # Execute a command to confirm the system is operational
                stdin, stdout, stderr = ssh.exec_command("uptime")
                print(stdout.read().decode())

                ssh.close()
                break  # Exit the loop if the connection is successful
            except (paramiko.ssh_exception.NoValidConnectionsError, paramiko.ssh_exception.SSHException) as e:
                print(f"Connection failed system  down: {e}. Retrying in {self.interval} seconds...")
                time.sleep(self.interval)  # Wait before retrying
            except Exception as e:
                print(f"An error occurred system down: {e}. Retrying in {self.interval} seconds...")
                time.sleep(self.interval)  # Wait before retrying

    def cmd_pwd(self):
        command = "pwd"
        print(f"command: {command}")
        r = self.send_lf_command(command)
        if r.failed:
            raise Exception(r.result)
        print(f"result {command}: {r.result}")

    def cmd_uptime(self):
        command = "uptime"
        print(f"command: {command}")
        r = self.send_lf_command(command)
        if r.failed:
            raise Exception(r.result)
        print(f"result {command}: {r.result}")

    def cmd_ls(self):
        command = "ls"
        r = self.send_lf_command(command)
        if r.failed:
            raise Exception(r.result)
        print(f"command: {command}: {r.result}")

    def killall_lfclient(self):
        command = "killall lfclient.bash"
        r = self.send_lf_command(command)
        if r.failed:
            raise Exception(r.result)
        print(f"command: {command}: {r.result}")

    def killall_java(self):
        command = "killall java"
        r = self.send_lf_command(command)
        if r.failed:
            raise Exception(r.result)
        print(f"command: {command}: {r.result}")

    def lf_kinstall(self):

        # send the reboot command
        # check for done
        # [F30] Command: ./lf_kinstall.pl ./lf_kinstall.pl --lfver 5.5.1 --kver 6.15.6+ --do_noaer 1 --do_upgrade
        # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
        # Done.

        # command = "curl -o lf_kinstall.pl www.candelatech.com/lf_kinstall.txt" # leave in for testing
        # command = "curl -o lf_kinstall.pl www.candelatech.com/lf_kinstall.txt; ./lf_kinstall.pl --lfver 5.5.1 --kver 6.15.6+ --do_noaer 1 --do_upgrade"
        command = f"curl -o lf_kinstall.pl www.candelatech.com/lf_kinstall.txt; chmod +x lf_kinstall.pl; ./lf_kinstall.pl --lfver {self.lfver} --kver {self.kver} --do_noaer 1 --do_upgrade"
        r = self.send_lf_command(command)
        if r.failed:
            raise Exception(r.result)

        print(f"{command}: {r.result}")

    def reboot_lanforge(self):
        command = "/sbin/reboot -f > /dev/null 2>&1 &"
        print(f"command: {command}")
        r = self.send_lf_command(command)
        if r.failed:
            raise Exception(r.result)

        print(f"{command}: {r.result}")

    def update_lanforge(self):

        # this should reconnect
        self.check_system_up()

        self.cmd_pwd()

        self.cmd_ls()

        self.killall_lfclient()

        self.killall_java()

        self.lf_kinstall()

        # self.reboot_lanforge()

        self.reboot_lf_with_paramiko()  # leave in if paramiko needs to be in reboot

        # take down connection so as to reconnect
        self.tear_down_mgmt()

        # this should reconnect
        self.check_system_up()

        # check large files
        self.check_large_files()

    # LANforge user manager
    @contextmanager
    def get_mgmt_user(self) -> "Generator[GenericDriver]":  # noqa:
        if getattr(self, "conn_user", None) == None:  # noqa:

            #  ./vrf_exec.bash eth1 ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa root@192.168.215.113
            # jumphost config
            # c = {
            #     "host":self.dest,  # noqa:
            #     "auth_username":self.root_user,  # noqa:
            #     "auth_password":self.root_password,  # noqa:
            #     "ssh_config_file": True,
            #     "comms_prompt_pattern":"^\S+\s\S+\s[#>$]\s*$", # noqa: 231
            #     "timeout_ops": 120,
            #     "timeout_transport": 240
            # }

            # if not getattr(self, "jump_host", None) == None:
            # jump_function = get_jump_function(c)

            # LANforge root config
            user = { # noqa
                "host": self.mgr,  # noqa:
                "auth_username": self.user,  # noqa:
                "auth_password": self.user_password,  # noqa:
                "auth_strict_key": False,
                # "comms_prompt_pattern": "^\\S[a-z]*\\@[a-zA-Z0-9]+[-][a-zA-Z0-9]+[\\s\\S]\\S\\S[\\#\\$\\>]",
                "comms_prompt_pattern": r"^(?:\([a-z]+[-][0-9]+\.[0-9]+\)|)(?:\s|\S)(?:\[|)[a-z]*\@[a-zA-Z0-9]+(?:[-][a-zA-Z0-9]+|)[-][a-zA-Z0-9]+[\s\S]\S(?:\:|\s)(?:\S|\S\S)[\\#\\$\\>]",
                # "on_open": jump_function, # on logging into LANforge will run the jump_function
                # "auth_password_pattern": "Password:",
                "timeout_ops": int(self.user_timeout),
                "timeout_transport": int(self.user_timeout),
                "timeout_socket": int(self.user_timeout),
                "ssh_config_file": True,
            }

            self.conn_user = GenericDriver(**root) # noqa
            try:
                self.conn_user.open()
            except scrapli.exceptions.ScrapliAuthenticationFailed as e:
                raise Exception(
                    f"Failed to open connection to {self.mgr} ({e.message})"
                ) from e
        yield self.conn_user

    # LANforge root manager
    @contextmanager
    def get_mgmt(self) -> "Generator[GenericDriver]":  # noqa:
        if getattr(self, "conn", None) == None:  # noqa:

            # jumphost config left in for reference eventually may need to reboot AP's
            #  ./vrf_exec.bash eth1 ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa root@192.168.215.113
            # jumphost config
            # c = {
            #     "host":self.dest,  # noqa:
            #     "auth_username":self.root_user,  # noqa:
            #     "auth_password":self.root_password,  # noqa:
            #     "ssh_config_file": True,
            #     "comms_prompt_pattern":"^\S+\s\S+\s[#>$]\s*$", # noqa: 231
            #     "timeout_ops": 120,
            #     "timeout_transport": 240
            # }

            # if not getattr(self, "jump_host", None) == None:
            # jump_function = get_jump_function(c)

            # LANforge root config
            root = {
                "host": self.mgr,  # noqa:
                "auth_username": self.root_user,  # noqa:
                "auth_password": self.root_password,  # noqa:
                "auth_strict_key": False,
                # "comms_prompt_pattern": "^\\S[a-z]*\\@[a-zA-Z0-9]+[-][a-zA-Z0-9]+[\\s\\S]\\S\\S[\\#\\$\\>]",
                "comms_prompt_pattern": r"^(?:\([a-z]+[-][0-9]+\.[0-9]+\)|)(?:\s|\S)(?:\[|)[a-z]*\@[a-zA-Z0-9]+(?:[-][a-zA-Z0-9]+|)[-][a-zA-Z0-9]+[\s\S]\S(?:\:|\s)(?:\S|\S\S)[\\#\\$\\>]",
                # "on_open": jump_function, # on logging into LANforge will run the jump_function
                # "auth_password_pattern": "Password:",
                "timeout_ops": int(self.root_timeout),
                "timeout_transport": int(self.root_timeout),
                "timeout_socket": int(self.root_timeout),
                "ssh_config_file": True,
            }

            self.conn = GenericDriver(**root)
            try:
                self.conn.open()
            except scrapli.exceptions.ScrapliAuthenticationFailed as e:
                raise Exception(
                    f"Failed to open connection to {self.mgr} ({e.message})"
                ) from e
        yield self.conn

    def send_lf_command(self, command: "str"):
        print(f"command : {command}")
        with self.get_mgmt() as console:

            r = console.send_command(command, failed_when_contains=["ERROR: .*"])

        return r

    def send_lf_command_user(self, command: "str"):
        print(f"command : {command}")
        with self.get_mgmt_user() as console:

            r = console.send_command(command, failed_when_contains=["ERROR: .*"])

        return r

    # left in for reference
    def send_multiple_lf_commands(self, command: "list"):
        print(f"command : {command}")
        with self.get_mgmt() as console:

            r = console.send_commands(command, failed_when_contains=["ERROR: .*"])

        return r

    def send_ap_command(self, command: "str"):

        print(f"command sent: {command}")
        with self.get_mgmt() as console:

            r = console.send_command(command, failed_when_contains=["ERROR: .*"])

        return r


def validate_args(args):
    """Validate CLI arguments."""
    if args.mgr is None:
        logger.error("--mgr required")
        exit(1)

    if args.user is None:
        logger.error("--user required")
        exit(1)

    if args.user_password is None:
        logger.error("--user_password required")
        exit(1)

    if args.root_user is None:
        logger.error("--root_user required")
        exit(1)

    if args.root_password is None:
        logger.error("--root_password required")
        exit(1)

    if args.lfver is None:
        logger.error("--lfver required")
        exit(1)

    if args.kver is None:
        logger.error("--kver required")
        exit(1)

    if "+" not in args.kver:
        logger.error("kver needs to have a '+'")

    if args.user_timeout is None:
        logger.error("--user_timeout required")
        exit(1)

    if args.root_timeout is None:
        logger.error("--root_timeout required")
        exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        prog='lf_update.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
 Update lanforge
            ''',

        description=r'''
 NAME:       lf_update.py

PURPOSE:    Update a lanforge system via kinstall, reboot, and run check_large_files.

NOTES:      This script is used to help to automate lanforge update

EXAMPLE:    # Updating a LANforge cli
            ./lf_update.py \
            --mgr 192.168.50.103 \
            --root_user root \
            --root_password lanforge \
            --user lanforge \
            --user_password lanforge \
            --mgr_ssh_port 22\
            --lfver 5.5.1\
            --kver 6.15.6+\
            --log_level info

            # Updating a LANforge Vscode json
            // ./lf_update.py
            "args":[
            "--mgr", "192.168.50.103",
            "--root_user", "root",
            "--root_password", "lanforge",
            "--user", "lanforge",
            "--user_password", "lanforge",
            "--mgr_ssh_port", "22",
            "--log_level","info",
            "--lfver","5.5.1",
            "--kver","6.15.6+"
            "--log_level","info"
            ]


SCRIPT_CLASSIFICATION : Tool

SCRIPT_CATEGORIES:   installation

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2025 Candela Technologies Inc


INCLUDE_IN_README
       ''')

    # leave in for possible remote commands to execute
    # parser.add_argument(
    #     '--prog',
    #     help='Remote command to execute',
    #     default=prog)

    parser.add_argument(
        '--remote_args',
        help='Arguments for remote command',
        default="")

    parser.add_argument(
        '--mgr', '--lf_mgr',
        help='IP address of remote system',
        dest='mgr')

    parser.add_argument(
        '--user', '--lf_user',
        help='User-name for remote machine',
        dest='user')

    parser.add_argument(
        '--user_password', '--lf_user_passwd',
        help='User Password for remote machine',
        dest='user_password')

    parser.add_argument(
        '--root_user', '--lf_root_user',
        help='User-name for remote machine',
        dest='root_user')

    parser.add_argument(
        '--root_password', '--lf_root_passwd',
        help='Root Password for remote machine',
        dest='root_password')

    parser.add_argument(
        '--mgr_ssh_port', '--lf_mgr_ssh_port', '--lf_port',
        help='ssh port to use',
        dest='mgr_ssh_port')

    parser.add_argument(
        '--gui_resourse',
        help='The lanforge has the resourse GUI running on it',
        action='store_true')

    parser.add_argument(
        '--kver',
        help='kernel version  example: 6.15.6+',
        dest='kver')

    parser.add_argument(
        '--lfver',
        help='lanforge version --lfver 5.5.1',
        dest='lfver')

    parser.add_argument(
        '--user_timeout',
        help=''' lanforge update timeout for user login seconds, suggested time:
        523c  =  10 sec
        AT7   =  10 sec
        Noah2 = 20 sec
        APU2  = 25 sec
        example: --user_timeout 1320
        ''',
        dest='user_timeout')

    parser.add_argument(
        '--root_timeout',
        help=''' lanforge update timeout for root login seconds, suggested time:
        523c  =  300 sec
        AT7   =  300 sec
        Noah2 = 720 sec
        APU2  = 1320 sec
        example: --timeout 1320
        ''',
        dest='root_timeout')

    parser.add_argument(
        '--action',
        help='action for remote machine')

    parser.add_argument('--log_level',
                        default=None,
                        help='Set logging level: debug | info | warning | error | critical')

    parser.add_argument(
        '--help_summary',
        action="store_true",
        help='Show summary of what this script does')

    parser.add_argument(
        '--help_example',
        action="store_true",
        help='Show simple example for lf_update.py')

    parser.add_argument(
        '--help_vscode',
        action="store_true",
        help='Print out simple vscode example for lf_update.py')

    return parser.parse_args()


def help_commands(args):
    help_summary = '''\
This script will perform an update on lanforge GUI version, Kernel version, reboot, run check_large_files.bash
'''

    if args.help_summary:
        print(help_summary)
        exit(0)

    help_example = r'''\
This example may be directly modified and executed from the command line
    ./lf_update.py \
    --mgr 192.168.50.103 \
    --root_user root \
    --root_password lanforge \
    --user lanforge \
    --user_password lanforge \
    --mgr_ssh_port 22\
    --lfver 5.5.1\
    --kver 6.15.6+\
    --user_timeout 10\
    --root_timeout 300\
    --log_level info
'''

    if args.help_example:
        print(help_example)
        exit(0)

    help_vscode = r'''
            // ./lf_update.py
            "args":[
            "--mgr", "192.168.50.103",
            "--root_user", "root",
            "--root_password", "lanforge",
            "--user", "lanforge",
            "--user_password", "lanforge",
            "--mgr_ssh_port", "22",
            "--log_level","info",
            "--lfver","5.5.1",
            "--kver","6.15.6+",
            "--user_timeout","10",
            "--root_timeout","300",
            "--log_level","info"
            ]
'''

    if args.help_vscode:
        print(help_vscode)
        exit(0)


def main():

    args = parse_args()

    help_commands(args)

    validate_args(args)

    logger_config = lf_logger_config.lf_logger_config()

    if args.log_level:
        logger_config.set_level(level=args.log_level)

    lf = create_lanforge_object(**vars(args))

    lf.check_system_up()

    lf.update_lanforge()

    lf.check_system_up()

    kernel_version = lf.get_lanforge_kernel_version()
    logger.info(f"kernel_version = {kernel_version}")

    server_version = lf.get_lanforge_server_version()
    logger.info(f"server_version: {server_version}")

    gui_version = lf.get_lanforge_gui_version()

    # Work in progress , the process closes when starting the GUI
    # if gui_version is None and gui_version != "NA":
    #     logger.info(f"gui_version = {gui_version}")
    #     lf.start_gui()
    #     time.sleep(10)
    #     gui_version = lf.get_lanforge_gui_version()

    logger.info(f"gui_version = {gui_version}")


if __name__ == '__main__':
    main()
