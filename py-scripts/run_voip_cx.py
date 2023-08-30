#!/usr/bin/env python3
# This script will start a named set of voip connections and report their data to a csv file
import logging
import argparse
import importlib
import os
import pprint
import sys
import time
import traceback
# from time import sleep
from pprint import pprint

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)
sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
from lanforge_client.lanforge_api import LFSession
from lanforge_client.lanforge_api import LFJsonCommand
from lanforge_client.lanforge_api import LFJsonQuery

logger = logging.getLogger(__name__)


# lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
# LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
# lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
# LFCliBase = lfcli_base.LFCliBase
# realm = importlib.import_module("py-json.realm")
# Realm = realm.Realm


class VoipReport():
    def __init__(self, lfsession: LFSession = None, args=None):

        self.lfsession = lfsession
        self.csv_filename = args.csv_file
        self.cx_list: list = []
        self.voip_endp_list: list = []
        if not args.cx_list:
            raise ValueError("no cx names")
        if isinstance(args.cx_list, list):
            self.cx_list.extend(args.cx_list)
        elif isinstance(args.cx_list, str):
            if args.cx_list.find(',') < 0:
                self.cx_list.append(args.cx_list)
            else:
                self.cx_list.extend(args.cx_list.split(','))
        # pprint(["self.cx_list:", self.cx_list])
        csv_file_name = f"/home/lanforge/report-data/voip-{time.time()}.csv"
        if args.csv_file:
            self.csv_filename = args.csv_file
        else:
            self.csv_filename = csv_file_name
        self.ep_col_names: list = (
            "epoch_time",
            "attenuation (agc)",
            "avg delay",
            "calls answered",
            "calls attempted",
            "calls completed",
            "calls failed",
            "cf 404",
            "cf 408",
            "cf busy",
            "cf canceled",
            "delay",
            "destination addr",
            "dropped",
            "dup pkts",
            "eid",
            "elapsed",
            "entity id",
            "jb cur",
            "jb over",
            "jb silence",
            "jb under",
            "jitter",
            "mng",
            "mos-lqo",
            "mos-lqo#",
            "name",
            "ooo pkts",
            "reg state",
            "rst",
            "rtp rtt",
            "run",
            "rx bytes",
            "rx pkts",
            "scoring bklg",
            "snr deg",
            "snr ref",
            "source addr",
            "state",
            "tx bytes",
            "tx pkts",
            "vad pkts"
        )
        self.csv_data : list = []

    def start(self):
        # query list of voip connections, warn on any not found

        lf_query: LFJsonQuery = self.lfsession.get_query()
        lf_cmd: LFJsonCommand = self.lfsession.get_command()
        e_w_list: list = []

        response: list = lf_query.get_voip(eid_list=self.cx_list,
                                           requested_col_names=("name"),
                                           errors_warnings=e_w_list,
                                           debug=True)
        if len(e_w_list):
            pprint(['ewlist:', e_w_list])
        if not response:
            raise ValueError("unable to find voip connections")
        for (key, _) in response[0].items():
            if key not in self.cx_list:
                print(f"cx {key} not found")
                continue
            self.voip_endp_list.append(f"{key}-A")
            self.voip_endp_list.append(f"{key}-B")
            # start cx
            try:
                lf_cmd.post_set_cx_state(cx_name=key,
                                         test_mgr='ALL',
                                         suppress_related_commands=True,
                                         cx_state=lf_cmd.SetCxStateCxState.RUNNING.value,
                                         errors_warnings=e_w_list)
            except Exception as e:
                pprint(['exception:', e, "cx:", key, e_w_list])

        # csv header row:
        self.csv_data.append(','.join(self.ep_col_names))
        #pprint(["self.csv_data:", self.csv_data])
        #exit(1)
        #print("----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ")

    def append_to_csv(self, ep_name: str = None, ep_record: dict = None):
        if not ep_name:
            raise ValueError("append_to_csv needs endpoint name")
        if not ep_record:
            raise ValueError("append_to_csv needs endpoint record")
        #pprint(["ep_record:", ep_record])
        csv_row : list = []
        # ep_col_names defines the sorted order to retrieve the column values
        for key in self.ep_col_names:
            if "epoch_time" == key:
                csv_row.extend([int(time.time()), ep_name])
                continue
            csv_row.append(str(ep_record[key]))
        self.csv_data.append(csv_row)
        pprint(["   csv_row> ", csv_row])
        exit(1)

    def monitor(self):
        if not self.ep_col_names:
            raise ValueError("no endpoint names")
        num_running_ep = 1

        #column_names: str = ','.join(self.ep_col_names)
        lf_query: LFJsonQuery = self.lfsession.get_query()
        lf_cmd: LFJsonCommand = self.lfsession.get_command()
        e_w_list: list = []
        response: list
        #pprint(['column_names:', column_names])
        while num_running_ep > 0:
            time.sleep(1)
            try:
                pprint(["self.voip.endp_list:", self.voip_endp_list])
                num_running_ep = len(self.voip_endp_list)
                response = lf_query.get_voip_endp(eid_list=self.voip_endp_list,
                                                  debug=False,
                                                  errors_warnings=e_w_list)
                if not response:
                    #pprint(e_w_list)
                    raise ValueError("unable to find endpoint data")

                for entry in response:
                    name = list(entry.keys())[0]
                    record = entry[name]
                    self.append_to_csv(ep_name=name, ep_record=entry[name])

                    print(f"    state: {record['state']}")
                    if "Stopped" == record['state']:
                        num_running_ep -= 1
                        continue

            except Exception as e:
                traceback.print_exc()
                pprint(['exception:', e, 'e_w_list:', e_w_list])
                exit(1)

    def report(self):
        pprint(self.csv_data)
        pass


def main():
    lfjson_host = "localhost"
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--host", type=str, default="localhost",
                        help="URL of the LANforge GUI machine (localhost is default, http://localhost:8080)")
    parser.add_argument("--csv_file", help="name of the csv output file", type=str)
    parser.add_argument("--cx_list", "--cx_names", help="comma separated list of voip connection names, or 'ALL'",
                        type=str)
    parser.add_argument("--debug", help='Enable debugging', default=False, action="store_true")
    parser.add_argument("--log_level", help='debug message verbosity', type=str)

    args = parser.parse_args()
    if args.host is not None:
        lfjson_host = args.host
    if args.debug is not None:
        debug = args.debug
    if not args.cx_list:
        print("Please list voip connection names (ex: cx1,cx2,cx3) or ALL")

    lfapi_session = LFSession(lfclient_url=lfjson_host,
                                debug=debug,
                                )
    voip_report = VoipReport(lfsession=lfapi_session, args=args)
    voip_report.start()
    voip_report.monitor()
    voip_report.report()


if __name__ == "__main__":
    main()
