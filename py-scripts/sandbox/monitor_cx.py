#!/usr/bin/env python3
"""
NAME: monitor_cx.py

PURPOSE: polls connections and saves data to a csv file

EXAMPLE:
$ ./monitor_cx.py --host ct521a-jana --cx_names cx1,cx2,... --csv_file connections.csv --quit=cx_stop

NOTES:


TO DO NOTES:

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

sys.path.insert(1, "../../")

if "SHELL" in os.environ.keys():
    lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
    from lanforge_client.lanforge_api import LFSession
    from lanforge_client.lanforge_api import LFJsonCommand
    from lanforge_client.lanforge_api import LFJsonQuery
else:
    import lanforge_api
    from lanforge_api import LFJsonCommand
    from lanforge_api import LFJsonQuery

from enum import Enum

logger = logging.getLogger(__name__)


# lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class QuitWhen(Enum):
    NEVER = "never"
    ALL_CX_STOPPED = "all_cx_stopped"
    TIME_ELAPSED = "time_elapsed"

    @staticmethod
    def parse(word: str = None) -> str:
        # print(f"word <{word}>")
        if not word:
            raise ValueError(f"empty <{word}> will not parse")
        lc_word = word.lower()

        if lc_word.endswith("never"):
            return QuitWhen.NEVER
        if lc_word.endswith("all_cx_stopped"):
            return QuitWhen.ALL_CX_STOPPED
        if lc_word.endswith("time_elapsed"):
            return QuitWhen.TIME_ELAPSED
        else:
            raise ValueError(f"Unknown value: {word}")


class CxMonitor:
    def __init__(self,
                 session: LFSession = None,
                 cxnames: list = None,
                 filename: str = None,
                 quit_when: str = None):
        self.command: LFJsonCommand
        self.command = session.get_command()
        self.command.debug_on = True
        self.query: LFJsonQuery
        self.query = session.get_query()

        if not filename:
            raise ValueError("Please specify a filename")
        if not cxnames:
            raise ValueError("Please specify connection names, or ALL")
        self.csvfile = filename

        if isinstance(cxnames, str):
            if cxnames == "ALL" or "all":
                self.cxnames = ("all")
            elif cxnames.find(",") > 0:
                self.cxnames = ",".split(cxnames)
            else:
                self.cxnames = (cxnames)
        if isinstance(cxnames, list):
            self.cxnames = cxnames

        self.quit_when: QuitWhen = quit_when
        if not quit_when:
            self.quit_when = QuitWhen.ALL_CX_STOPPED

    def monitor(self):
        quitting_time: bool = False
        default_col_names = (
            "name",
            "state",
            "bps rx b",
            "pkt rx a",
            "pkt rx b",
            "rx drop % a",
            "rx drop % b",
            "drop pkts a",
            "drop pkts b",
        )
        while not quitting_time:
            time.sleep(1)
            items = self.query.get_cx(eid_list=self.cxnames,
                                      requested_col_names=default_col_names,
                                      debug=True)
            pprint.pprint(["items", items])
            for cx in items:
                pprint.pprint(cx)

    def save(self):
        pass


def main():
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='monitors connections and prints data to a csv file')
    parser.add_argument("--host", "--mgr", help='specify the GUI to connect to, assumes port 8080')
    parser.add_argument("--cx_names", help='comma separated list of cx names, or ALL')
    parser.add_argument("--csv_file", help='csv filename to save data to')
    parser.add_argument("--quit", default=QuitWhen.ALL_CX_STOPPED,
                        help='when to exit the script: never, a number of minutes, or when all connections stop')
    parser.add_argument("--debug", action="store_true", default=False,
                        help='turn on debugging')
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
        # lf_logger_config.set_level(level=args.log_level)

    session = lanforge_api.LFSession(lfclient_url="http://%s:8080" % args.host,
                                     debug=args.debug,
                                     connection_timeout_sec=2.0,
                                     stream_errors=True,
                                     stream_warnings=True,
                                     require_session=True,
                                     exit_on_error=True)
    #print(f"quit: {args.quit}")
    cx_monitor = CxMonitor(session,
                           cxnames=args.cx_names,
                           filename=args.csv_file,
                           quit_when=QuitWhen.parse(word=args.quit))
    cx_monitor.monitor()
    cx_monitor.save()


if __name__ == "__main__":
    main()
