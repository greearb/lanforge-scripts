#!/usr/bin/env python3
"""
NAME: monitor_cx.py

PURPOSE: The Monitor CX script is for collecting CSV data from running Layer 3 connections. It reports data for each
        endpoint. Start this script after beginning traffic in the GUI or other means. When all connections have
        stopped, this script will exit. If this script is run before connections are started, it will immediately
        exit.

EXAMPLE:
#########################################
# Examples
#########################################

Begin by starting traffic in the GUI or other means.

Example monitoring one connection:
$ ./monitor_cx.py --host ct521a-jana --cx_names cx1 --csv_file connections.csv

Example monitoring all connections:
$ ./monitor_cx.py --host ct521a-jana --cx_names all --csv_file connections.csv


SCRIPT_CLASSIFICATION:  Monitors Traffic

SCRIPT_CATEGORIES:  CSV Generation

NOTES:
        This script is purposely simple. It should serve as a reasonable basis for querying connections
        in general. Please make a copy of this script and edit it to customize which columns you wish to collect.

STATUS: functional

VERIFIED_ON: Oct 2, 2023 jed@candelatech

LICENSE
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

INCLUDE_IN_README: True


"""
import os
import sys
import time

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

import importlib
import argparse
import pprint
import logging
import io
import csv
from enum import Enum

sys.path.insert(1, "../")
sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
from lanforge_client.lanforge_api import LFSession
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFJsonQuery

LFUtils = importlib.import_module("py-json.LANforge.LFUtils")

logger = logging.getLogger(__name__)


class QuitWhen(Enum):
    """
    QuitWhen is a utility Enum placed here to define a quit time policy.
    Right now we only define when all connections stop.
    """
    # NEVER = "never"
    ALL_CX_STOPPED = "all_cx_stopped"

    # TIME_ELAPSED = "time_elapsed" # not implemented

    @staticmethod
    def parse(criteria: str = None) -> str:
        # print(f"word <{word}>")
        if not criteria:
            raise ValueError(f"empty <{criteria}> will not parse")
        lc_word = str(criteria).lower()

        # if lc_word.endswith("never"):
        #    return QuitWhen.NEVER
        if lc_word.endswith("all_cx_stopped"):
            return QuitWhen.ALL_CX_STOPPED
        # if lc_word.endswith("time_elapsed"):
        #    return QuitWhen.TIME_ELAPSED
        else:
            raise ValueError(f"Unknown value: {criteria}")


class CxMonitor:
    def __init__(self,
                 session: LFSession = None,
                 cxnames: list = None,
                 filename: str = None,
                 quit_when: str = None):
        self.command: LFJsonCommand = session.get_command()
        self.command.debug_on = True
        self.query: LFJsonQuery = session.get_query()
        self.query.debug_on = True
        self.cxnames: list = []
        self.endp_names: dict = {}
        self.lines_written: int = 0;

        if not filename:
            raise ValueError("Please specify a filename")
        if not cxnames:
            raise ValueError("Please specify connection names, or ALL")
        self.csvfile = filename
        self.csv_fh: io.TextIOWrapper = None

        if isinstance(cxnames, str):
            if cxnames.lower() == "all":
                # print(f"ALL:{cxnames}")
                self.cxnames = ["all"]
            elif cxnames.find(",") > 0:
                # print("COMMA")
                self.cxnames = ",".split(cxnames)
            else:
                self.cxnames = cxnames
        elif isinstance(cxnames, list):
            # print("LIST ")
            self.cxnames.extend(cxnames)

        # turn cxnames into endpoint unique names:
        if len(self.cxnames) == 1 and self.cxnames[0] == "all":
            items = self.query.get_cx(eid_list=['all'], requested_col_names=["name"])
            for cxname in items.keys():
                self.endp_names[f"{cxname}-A"] = 1
                self.endp_names[f"{cxname}-B"] = 1

        else:
            # pprint.pprint(["cxnames", self.cxnames])
            for name in self.cxnames:
                self.endp_names[f"{name}-A"] = 1
                self.endp_names[f"{name}-B"] = 1

        self.quit_when: str = quit_when
        if not quit_when:
            self.quit_when = QuitWhen.ALL_CX_STOPPED

    def open_save_file(self):
        if not self.csvfile:
            raise ValueError("CxMonitor: open_save_file lacks filename")
        self.csv_fh = open(self.csvfile, "w")
        if not self.csv_fh:
            raise ValueError(f"unable to open file for writing: [{self.csvfile}]")
        self.lines_written += 1

    def monitor(self):
        quitting_time: bool = False

        # The column names below are commented out on purpose. Not all data columns are useful for the majority
        # of test cases, and some columns are not data but URLs pointing to more specific queries. If you copy
        # modify this script, this is the area we expect you to customize first.
        default_col_names = (
            # 'name',
            'type',
            'run',
            # "1st rx",
            # "_links",
            "a/b",  # A-side or B-size
            # "bursty",
            # "crc fail",
            # "cwnd",
            "cx active",
            "cx estab",
            "cx estab/s",
            "cx to",
            "delay",
            # "destination addr",
            # "drop-count-5m", # this is a URL
            "dropped",
            "dup pkts",
            # "eid", # eid is ephemeral, not useful to save
            "elapsed",
            # "entity id", # eid is ephemeral, not useful to save
            "jitter",
            # "latency-5m", # this is a URL
            "max pdu",
            "max rate",
            # "mcast rx",
            "min pdu",
            "min rate",
            # "mng",
            # "name", # listed above
            "ooo pkts",
            "pattern",
            "pdu/s rx",
            "pdu/s tx",
            "pps rx ll",
            "pps tx ll",
            "rcv buf",
            # "replays",
            # "rt-latency-5m", # this is a URL
            # "run", # listed above
            "rx ber",
            "rx bytes",
            "rx drop %",
            "rx dup %",
            "rx ooo %",
            "rx pdus",
            "rx pkts ll",
            "rx rate",
            "rx rate (1m)",
            "rx rate (last)",
            "rx rate ll",
            "rx wrong dev",
            # "rx-silence-3s", # this is a URL
            # "script",
            # "send buf",
            # "source addr",
            "tcp mss",
            "tcp rtx",
            "tos",
            "tx bytes",
            "tx pdus",
            "tx pkts ll",
            "tx rate",
            "tx rate (1&nbsp;min)",
            "tx rate (last)",
            "tx rate ll"
        )
        # output header of csv file
        column_title: list = ["Time", "Endpoint", "Port"]
        column_title.extend(default_col_names)
        self.csv_fh.write(",".join(column_title) + "\n")
        self.csv_fh.close()

        # determine port alias for each endpoint
        endp_eid_list: list = list(self.endp_names.keys())
        endp_eid_items = self.query.get_endp(eid_list=endp_eid_list,
                                             requested_col_names=["name", "eid"])

        endp_name_to_alias: dict = {}
        for endp in endp_eid_items:
            endp_vals: dict = list(endp.values())[0]
            # eid_to_str() introduced recently, it is functionally:
            #       f"{port_eid_slice[0]}.{int(port_eid_slice[1])}.{int(port_eid_slice[2])}"
            port_eid: str = LFUtils.eid_to_str(LFUtils.name_to_eid(endp_vals["eid"]))
            endp_name_to_alias[port_eid] = "-"

        port_list = self.query.get_port(eid_list=list(endp_name_to_alias.keys()),
                                        requested_col_names=["port", "alias"])
        for port in port_list:
            port_eidn = list(port.keys())[0]
            port_eid = LFUtils.eid_to_str(LFUtils.name_to_eid(list(port.values())[0]["port"]))
            endp_name_to_alias[port_eid] = port_eidn

        print("Starting to monitor:")
        while not quitting_time:
            try:
                time.sleep(1)
                endp_eid_items = self.query.get_endp(eid_list=endp_eid_list,
                                                     requested_col_names=default_col_names)
                rows: list = []
                possibly_running: int = len(endp_eid_items)
                for endp in endp_eid_items:
                    endp_vals: dict = list(endp.values())[0]
                    row: list = []
                    row.extend([
                        int(time.time()),
                        list(endp.keys())[0],
                        endp_name_to_alias[LFUtils.eid_to_str(LFUtils.name_to_eid(endp_vals["eid"]))]
                    ])
                    endp_vals: dict = list(endp.values())[0]
                    if not "run" in endp_vals:
                        pprint.pprint(list(endp_vals))
                        quitting_time = True
                        raise ValueError("cannot find run column for endpoint, please include the *run* column")
                    if not bool(endp_vals["run"]):
                        possibly_running -= 1
                    for col in default_col_names:
                        row.append(endp_vals[col])
                    rows.append(row)

                with open(self.csvfile, "a") as csv_fh:
                    writer = csv.writer(csv_fh)
                    writer.writerows(rows)
                    # this is status output so that we don't think the script is dead
                    print(".", end="", flush=True)
                    self.lines_written += len(rows)

                if possibly_running < 1:
                    quitting_time = True
            except KeyboardInterrupt as k:
                quitting_time = True

    def close(self):
        if self.csv_fh and not self.csv_fh.closed:
            try:
                self.csv_fh.flush()
                self.csv_fh.close()
            finally:
                pass


def main():
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description="monitors connections and prints data to a csv file",
    )
    parser.add_argument(
        "--host", "--mgr", help="specify the GUI to connect to, assumes port 8080"
    )
    parser.add_argument("--cx_names",
                        nargs="+",
                        help="spsace or comma separated list of cx names, or ALL")
    parser.add_argument("--csv_file", help="csv filename to save data to")
    parser.add_argument(
        "--quit",
        default=QuitWhen.ALL_CX_STOPPED,
        help="when to exit the script: all_cx_stopped: when all connections stop",
    )
    parser.add_argument(
        "--debug", action="store_true", default=False, help="turn on debugging"
    )
    parser.add_argument("--log_level")

    args = parser.parse_args()
    if not args.csv_file:
        print("No csv file name provided")
        exit(1)
    if not args.cx_names:
        print("No connection names provided, did you mean ALL?")
        exit(1)
    if args.log_level:
        logger.setLevel(args.log_level)

    session = lanforge_api.LFSession(
        lfclient_url="http://%s:8080" % args.host,
        debug=args.debug,
        connection_timeout_sec=2.0,
        stream_errors=True,
        stream_warnings=True,
        require_session=True,
        exit_on_error=True,
    )
    # pprint.pprint(["CX NAMES", args.cx_names])
    cx_monitor = CxMonitor(
        session,
        cxnames=args.cx_names,
        filename=args.csv_file,
        quit_when=QuitWhen.parse(criteria=args.quit),
    )
    try:
        cx_monitor.open_save_file()
        cx_monitor.monitor()
    except Exception as e:
        print(e)
    finally:
        cx_monitor.close()
        print(f"Wrote {cx_monitor.lines_written} lines to {cx_monitor.csvfile}")
    exit(0)


if __name__ == "__main__":
    main()
