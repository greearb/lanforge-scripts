#!/usr/bin/python3
"""
NAME:       ssh_remote.py

PURPOSE:    Run command on a remote system over SSH

NOTES:      By default, the program runs with user 'root' and password 'lanforge'.

EXAMPLE:    # Run command with no arguments using test port over SSH
            ./ssh_remote.py \
                --ip    192.168.1.101 \
                --prog  ls

            # Run command 'ls --recursive'
            ./ssh_remote.py \
                --ip            192.168.1.101 \
                --prog          ls \
                --remote_args   'recursive'

            # Run command 'ls -r' (recursive but with shorter '-r' flag)
            ./ssh_remote.py \
                --ip            192.168.1.101 \
                --prog          "ls -r"

            # Run command with non-default user and password
            ./ssh_remote.py \
                --ip            192.168.1.101 \
                --username      lanforge \
                --password      egrofnal \
                --prog          ls
"""

import paramiko
# from paramiko import SSHClient
import socket
import argparse
# import logging

HELP_SUMMARY = "Runs a command on a remote system over SSH. Useful for DUT automation " \
               "in LANforge Chamber View tests"

global ip
global ssh_port
global user_name
global password
global timeout
global prog

ip = "192.168.100.157"
ssh_port = 22
username = "root"
password = "lanforge"
prog = "/home/lanforge/do_ap"
timeout = 5
remote_args = ""


def get_info(cmd):
    try:
        # logging.getLogger("paramiko").setLevel(logging.DEBUG)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # print("Connecting to Remote System...")
        client.connect(ip, username=username, password=password, port=ssh_port, timeout=timeout, allow_agent=False, look_for_keys=False)
        # print("Running cmd: %s" %(cmd))
        stdin, stdout, stderr = client.exec_command(cmd)

        output = str(stdout.read(), 'utf-8')

        # print("Output:\n")
        print(output)

    except paramiko.ssh_exception.AuthenticationException as e:
        print(e)
        print("Authentication Error, Check Credentials")
        return
    except paramiko.SSHException as e:
        print(e)
        print("Cannot SSH to the remote system: %s:%i user: %s  password: %s" % (ip, ssh_port, username, password))
        return
    except socket.timeout as e:
        print(e)
        print("AP Unreachable")
        return
    return


def parse_args():
    parser = argparse.ArgumentParser(
        prog='ssh_remote.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
 Run command against remote machine over ssh
            ''',

        description='''
 Run command against remote machine over ssh
        ''')

    parser.add_argument(
        '--prog',
        help='Remote command to execute',
        default=prog)

    parser.add_argument(
        '--remote_args',
        help='Arguments for remote command',
        default="")

    parser.add_argument(
        '--ip',
        help='IP address of remote system',
        default=ip)

    parser.add_argument(
        '--username',
        help='User-name for remote machine',
        default=username)

    parser.add_argument(
        '--password',
        help='Password for remote machine',
        default=password)

    parser.add_argument(
        '--help_summary',
        action="store_true",
        help='Show summary of what this script does')

    return parser.parse_args()


def main():
    global ip
    global prog
    global username
    global password

    args = parse_args()
    if args.help_summary:
        print(HELP_SUMMARY)
        exit(0)

    ip = args.ip
    username = args.username
    password = args.password
    prog = args.prog

    cmd = args.prog
    ra = args.remote_args.split()
    for a in ra:
        cmd += " --"
        cmd += a

    get_info(cmd)


if __name__ == '__main__':
    main()
