#!/usr/bin/env python3
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
import argparse
import logging
import paramiko
import socket

HELP_SUMMARY = "Runs a command on a remote system over SSH. Useful for DUT automation " \
               "in LANforge Chamber View tests"

# Default values
ip = "192.168.100.157"
ssh_port = 22
username = "root"
password = "lanforge"
prog = "/home/lanforge/do_ap"
timeout = 5
remote_args = ""

# Grab logger for this module for easy usage
logger = logging.getLogger(__name__)


def get_info(cmd: str, ip: str, ssh_port: int, username: str, password: str, timeout: int, **kwargs):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to remote system
        logger.debug(f"Connecting to remote system '{ip}:{ssh_port}' with username '{username}' and password '{password}'")
        client.connect(ip, username=username, password=password, port=ssh_port, timeout=timeout, allow_agent=False, look_for_keys=False)

        # Run command on remote system
        logger.debug(f"Running command on remote system: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)

        # Print output from command (both in debug and non-debug mode. This is grabbed by automation)
        output = str(stdout.read(), 'utf-8')
        logger.debug("Command output:\n")
        print(output)  # Using 'logger.info()' here will result in timeout for large command output

    except paramiko.ssh_exception.AuthenticationException as e:
        logger.error(e)
        logger.error("Authentication error, check credentials")
        return
    except paramiko.SSHException as e:
        logger.error(e)
        logger.error(f"Failed to connect to remote system '{ip}:{ssh_port}' with username '{username}' and password '{password}'")
        return
    except socket.timeout as e:
        logger.error(e)
        logger.error("AP Unreachable")
        return
    return


def parse_args():
    parser = argparse.ArgumentParser(
        prog="ssh_remote.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="Run command on remote system over SSH")

    # Command and command argument options
    parser.add_argument("--prog",
                        help="Remote command to execute",
                        default=prog)
    parser.add_argument("--remote_args",
                        help="Arguments for remote command",
                        default="")

    # SSH options
    parser.add_argument("--ip",
                        help="IP address of remote system",
                        default=ip)
    parser.add_argument("-p", "--port", "--ssh_port",
                        dest="ssh_port",
                        help="SSH port for remote system",
                        default=ssh_port)
    parser.add_argument("--user", "--username",
                        dest="username",
                        help="Username for remote machine",
                        default=username)

    parser.add_argument("--passwd", "--password",
                        dest="password",
                        help="Password for remote machine",
                        default=password)
    parser.add_argument("--timeout",
                        help="SSH timeout for connection failures",
                        default=timeout)

    parser.add_argument("--help_summary",
                        action="store_true",
                        help="Show summary of what this script does")
    parser.add_argument("--debug",
                        action="store_true",
                        help="Run in debugging mode with logging enabled and in verbose mode.")

    return parser.parse_args()


def configure_logging(debug: bool):
    """Configure logging based on user configuration.

    Since the output of this script is parsed in other automation, configure default
    logging to output with no timestamp. When debug mode is enabled, add back the timestamp
    and output more verbose logs.
    """
    # Configure SSH client library logging
    paramiko_logger = logging.getLogger("paramiko")
    paramiko_logger.setLevel(logging.ERROR)

    if not debug:
        # Configure logging with no timestamp format. Only permit this module to log at INFO level.
        # Set all others to ERROR level to ensure other automation, which output of this script,
        # does not break unnecessarily
        logging.basicConfig(level=logging.ERROR, format="")
        logging.getLogger(__name__).setLevel(logging.INFO)

    else:
        # Configure logging with timestamp format. Permit this module and SSH client module to
        # log at DEBUG level. Set all other modules to INFO level
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).setLevel(logging.DEBUG)
        logging.getLogger("paramiko").setLevel(logging.DEBUG)


def main():
    args = parse_args()
    if args.help_summary:
        print(HELP_SUMMARY)
        exit(0)

    configure_logging(args.debug)

    cmd = args.prog
    ra = args.remote_args.split()
    for a in ra:
        cmd += " --"
        cmd += a

    # **vars(args) unpacks the arguments dict into arguments to function
    # with all non-argument key-value pairs set in the '**kwargs' variable
    get_info(cmd=cmd, **vars(args))


if __name__ == '__main__':
    main()
