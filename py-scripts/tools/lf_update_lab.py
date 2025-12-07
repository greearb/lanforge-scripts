#!/usr/bin/python3

r"""
NAME:       lf_lab_update.py

PURPOSE:    Update either single or multiple lanforge systems

NOTES:      This script is used to help to automate lanforge updates in a lab

EXAMPLE:    # Updating a LANforge cli
            ./lf_update.py \
            --mgr 192.168.50.103 \
            --root_user root \
            --root_password lanforge \
            --user lanforge \
            --user_password lanforge \
            --mgr_ssh_port 22 \
            --lfver 5.5.1 \
            --kver 6.15.6+ \
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

SCRIPT_CATEGORIES:   Lanforge Installation

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2025 Candela Technologies Inc


INCLUDE_IN_README

"""
# import threading
import multiprocessing
# import time

import argparse
import os
import importlib
import logging
import logging.config
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("lf_logger_config")


if sys.version_info[0] != 3:
    print("This script requires Python 3")
    logger.critical("This script requires Python 3")
    exit(1)


if sys.version_info[0] != 3:
    exit()


class ProcessLogFilter(logging.Filter):
    """
    This filter only show log entries for specified process name
    """

    def __init__(self, process_name, *args, **kwargs):
        logging.Filter.__init__(self, *args, **kwargs)
        self.process_name = process_name

    def filter(self, record):
        return record.processName == self.process_name


class create_update_lab_object:
    def __init__(self,
                 **kwargs
                 ):

        if "update_module" in kwargs:
            self.update_module = importlib.import_module(kwargs["update_module"])
            removed_module = kwargs.pop('update_module', None)
            logger.info(f"remove_module : {removed_module}")

        # if "json_lf_lab_mgrs" in kwargs:
        #     self.json_lf_lab_mgrs = kwargs["json_lf_lab_mgrs"]

        self.lf_update_obj = []
        self.lab_tb = {}
        if "tb_name" in kwargs:
            self.tb_name = kwargs["tb_name"]
            for tb_name in self.tb_name:
                key, value = str(tb_name).replace("'", "").replace("[", "").replace("]", "").split('=')
                self.lab_tb[key] = value

        self.kwargs = kwargs
        # if "mgr" in kwargs:
        #     self.mgr = kwargs["mgr"]

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

    def start_process_logging(self):
        """
        Add a log handler to separate file for current process
        """
        process_name = multiprocessing.current_process().name
        log_file = '/tmp/{}.log'.format(process_name)
        log_handler = logging.FileHandler(log_file)

        log_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)-15s"
            "| %(processName)-11s"
            "| %(levelname)-5s"
            "| %(message)s")
        log_handler.setFormatter(formatter)

        log_filter = ProcessLogFilter(process_name)
        log_handler.addFilter(log_filter)

        logger = logging.getLogger()
        logger.addHandler(log_handler)

        return log_handler

    def stop_process_logging(self, log_handler):
        # Remove process log handler from root logger
        logging.getLogger().removeHandler(log_handler)

        # Close the process log handler so that the lock on log file can be released
        log_handler.close()

    def worker(self):
        process_log_handler = self.start_process_logging()
        self.lf_update_obj[self.obj_index].update_lanforge()
        self.stop_process_logging(process_log_handler)

    def config_root_logger(self, log_level):

        time_now = datetime.now()
        formatted_datetime = time_now.strftime("%Y-%m-%d-%H-%M-%S")

        log_file = f'/tmp/Process_Logging_All_{formatted_datetime}.log'

        formatter = "%(asctime)-15s" \
                    "| %(processName)-11s" \
                    "| %(levelname)-5s" \
                    "| %(message)s"

        logging.config.dictConfig({
            'version': 1,
            'formatters': {
                'root_formatter': {
                    'format': formatter
                }
            },
            'handlers': {
                'console': {
                    'level': log_level,
                    'class': 'logging.StreamHandler',
                    'formatter': 'root_formatter'
                },
                'log_file': {
                    'class': 'logging.FileHandler',
                    'level': log_level,
                    'filename': log_file,
                    'formatter': 'root_formatter',
                }
            },
            'loggers': {
                '': {
                    'handlers': [
                        'console',
                        'log_file',
                    ],
                    'level': log_level,
                    'propagate': True
                }
            }
        })

    def update_lab(self):

        processes = []

        # create the update objects
        self.obj_index = 0
        for key in self.lab_tb:
            self.kwargs["tb_name"] = key
            self.kwargs["mgr"] = self.lab_tb[key]
            self.lf_update_obj.append(self.update_module.create_lanforge_object(**self.kwargs))
            time_now = datetime.now()
            formatted_datetime = time_now.strftime("%Y-%m-%d-%H-%M-%S")
            process = multiprocessing.Process(target=self.worker, name=f'Process_{self.kwargs["tb_name"]}_{self.kwargs["mgr"]}_{formatted_datetime}')
            processes.append(process)
            process.start()
            self.obj_index = self.obj_index + 1

        # Wait for all processes to finish
        for process in processes:
            process.join()


def validate_args(args):
    """Validate CLI arguments."""
    if args.update_module is None:
        logger.error("--update_module required")
        exit(1)

    if args.tb_name is None:
        logger.error("--tb_name required")
        exit(1)

    # if args.mgr is None:
    #     logger.error("--json_lf_lab_mgrs required")
    #     exit(1)

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

    if args.log_level is None:
        logger.error("--log_level required Set logging level: debug | info | warning | error | critical")
        exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        prog='lf_lab_update.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
 Update lanforge
            ''',

        description=r'''
 NAME:       lf_lab_update.py

PURPOSE:    Update a lanforge system via kinstall, reboot, and run check_large_files.

NOTES:      This script is used to help to automate lanforge update

EXAMPLE:    # Updating a LANforge cli
            ./lf_lab_update.py \
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
            // ./lf_lab_update.py
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
        '--update_module',
        help="--update_module <module used for updates> most likely  lf_update.py ",
        dest="update_module")

    # parser.add_argument(
    #     '--json_lf_lab_mgrs',
    #     help="--json_rig <rig json config> ",
    #     dest="json_lf_lab_mgrs")

    parser.add_argument(
        '--remote_args',
        help='Arguments for remote command',
        default="")

    parser.add_argument(
        '--tb_name', '--test_bed_name',
        action='append',
        nargs=1,
        help='name of the test_bed followed by ip , CT-US-001=192.168.100.116 is used in reporting complete loading',
        dest='tb_name')

    # parser.add_argument(
    #     '--mgr', '--lf_mgr',
    #     help='IP address of remote system',
    #     dest='mgr')

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
        example: --user_timeout 25
        ''',
        dest='user_timeout')

    parser.add_argument(
        '--root_timeout',
        help=''' lanforge update timeout for root login seconds, suggested time:
        523c  =  300 sec
        AT7   =  300 sec
        Noah2 = 720 sec
        APU2  = 1800 sec
        example: --timeout 1800
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

    # logger_config = lf_logger_config.lf_logger_config()

    # if args.log_level:
    #     logger_config.set_level(level=args.log_level)

    lf = create_update_lab_object(**vars(args))
    log_level = str.upper(args.log_level)
    lf.config_root_logger(log_level)

    lf.update_lab()


if __name__ == '__main__':
    main()
