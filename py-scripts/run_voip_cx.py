#!/usr/bin/env python3
# This script will start a named set of voip connections and report their data to a csv file
import argparse
import csv
import importlib
import logging
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
        self.last_written_row = 0
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
            "name",
            "state",
            "reg state",
            "mos-lqo#",
            "mos-lqo",
            "attenuation (agc)",
            "avg delay",
            "snr ref",
            "snr deg",
            "scoring bklg",
            "tx pkts",
            "rx pkts",
            "tx bytes",
            "rx bytes",
            "dropped",
            "ooo pkts",
            "dup pkts",
            "jb silence",
            "jb under",
            "jb over",
            "jb cur",
            "delay",
            "rtp rtt",
            "jitter",
            "vad pkts",
            "calls attempted",
            "calls completed",
            "calls failed",
            "cf 404",
            "cf 408",
            "cf busy",
            "cf canceled",
            "calls answered",
            "destination addr",
            "source addr",
            "elapsed",
            "rst",
            "run",
            "mng",
            "eid",
            # "entity id"
        )
        self.csv_data: list = []
        try:
            if not self.csv_filename:
                raise ValueError("no filename provided")
                exit(1)
            self.csv_fileh = open(self.csv_filename, "w")
            self.csv_writer = csv.writer(self.csv_fileh)
            self.csv_writer.writerow(self.ep_col_names)
        except Exception as e:
            e.print_exc()
            traceback.print_exc()
            exit(1)

    def start(self):
        # query list of voip connections, warn on any not found
        lf_query: LFJsonQuery = self.lfsession.get_query()
        lf_cmd: LFJsonCommand = self.lfsession.get_command()
        e_w_list: list = []

        response = lf_query.get_voip(eid_list=self.cx_list,
                                     requested_col_names=("name"),
                                     errors_warnings=e_w_list,
                                     debug=True)
        # print(" - - - - - - -  - - - - - - -  - - - - - - -  - - - - - - - ")
        # pprint(response)
        # print(" - - - - - - -  - - - - - - -  - - - - - - -  - - - - - - - ")

        if not response:
            raise ValueError("unable to find voip connections")

        if isinstance(response, dict):
            response = [response]

        for entry in response:
            for (key, value) in entry.items():
                if key == "name":
                    key = value
                if str(self.cx_list[0]).lower() == "all":
                    print(f"adding endpoints for {key}")
                elif key not in self.cx_list:
                    print(f"cx [{key}] not found in {self.cx_list}")
                    continue
                self.voip_endp_list.append(f"{key}-A")
                self.voip_endp_list.append(f"{key}-B")
                # start cx
                try:
                    # print(f"Starting cx {key}")
                    lf_cmd.post_set_cx_state(cx_name=key,
                                             test_mgr='ALL',
                                             suppress_related_commands=True,
                                             cx_state=lf_cmd.SetCxStateCxState.RUNNING.value,
                                             errors_warnings=e_w_list)
                except Exception as e:
                    pprint(['exception:', e, "cx:", key, e_w_list])

    def write_rows(self):
        if self.last_written_row >= (len(self.csv_data) - 1):
            print(f"write_row: row[{self.last_written_row}] already written, rows: {len(self.csv_data)} rows")
            return
        for i in range(self.last_written_row, len(self.csv_data)):
            # pprint(["i:", i, "csv:", self.csv_data[i]])
            row_strs: list = map(str, self.csv_data[i])
            self.csv_writer.writerow(row_strs)
            self.last_written_row = i
        self.csv_fileh.flush()

    def append_to_csv(self, ep_name: str = None, ep_record: dict = None):
        if not ep_name:
            raise ValueError("append_to_csv needs endpoint name")
        if not ep_record:
            raise ValueError("append_to_csv needs endpoint record")
        # pprint(["ep_record:", ep_record])
        new_row: list[str] = []
        # ep_col_names defines the sorted order to retrieve the column values
        for key in self.ep_col_names:
            if "epoch_time" == key:
                new_row.extend([int(time.time())])
                continue
            new_row.append(ep_record[key])
        # pprint(["csv_row:", new_row])
        self.csv_data.append(new_row)

    def monitor(self):
        if not self.ep_col_names:
            raise ValueError("no endpoint names")
        num_running_ep = 1
        lf_query: LFJsonQuery = self.lfsession.get_query()
        # lf_cmd: LFJsonCommand = self.lfsession.get_command()
        e_w_list: list = []
        response: list
        old_mos_value_A = 0
        old_mos_value_B = 0
        append_row_zero_endp_A_flag = True
        append_row_zero_endp_B_flag = True
        wait_flag_A = True
        wait_flag_B = True

        # stop until endpoints actually starts the test else script terminates early.
        while wait_flag_A or wait_flag_B:
            response = lf_query.get_voip_endp(eid_list=self.voip_endp_list,
                                                  debug=False,
                                                  errors_warnings=e_w_list)

            if not response:
                    # pprint(e_w_list)
                    raise ValueError("unable to find endpoint data")

            for entry in response:
                name = list(entry.keys())[0]
                record = entry[name]

                if "-A" in name: # endp A
                    if "Stopped" != record['state']:
                        wait_flag_A = False

                if "-A" in name: # endp B
                    if "Stopped" != record['state']:
                        wait_flag_B = False

                time.sleep(1)

        print("Script is now running....")

        while num_running_ep > 0:
            time.sleep(1)
            try:
                # pprint(["self.voip.endp_list:", self.voip_endp_list])
                num_running_ep = len(self.voip_endp_list)
                response = lf_query.get_voip_endp(eid_list=self.voip_endp_list,
                                                  debug=False,
                                                  errors_warnings=e_w_list)
                if not response:
                    # pprint(e_w_list)
                    raise ValueError("unable to find endpoint data")

                for entry in response:
                    name = list(entry.keys())[0]
                    record = entry[name]
                    # print(f"checking {name}, ", end=None)

                    if "-A" in name: # endp A

                        if (int(record['mos-lqo#']) == 0) and (float(record['mos-lqo']) != 0):
                            if (append_row_zero_endp_A_flag):
                                self.append_to_csv(ep_name=name, ep_record=record) # check record
                                append_row_zero_endp_A_flag = False

                        if int(record['mos-lqo#']) != old_mos_value_A:
                            self.append_to_csv(ep_name=name, ep_record=record)
                            old_mos_value_A = int(record['mos-lqo#'])

                    if "-B" in name: # endp B

                        if (int(record['mos-lqo#']) == 0) and (float(record['mos-lqo']) != 0):
                            if append_row_zero_endp_B_flag:
                                self.append_to_csv(ep_name=name, ep_record=record)
                                append_row_zero_endp_B_flag = False

                        if int(record['mos-lqo#']) != old_mos_value_B:
                            self.append_to_csv(ep_name=name, ep_record=record)
                            old_mos_value_B = int(record['mos-lqo#'])

                    # print("Debug: int(record['calls completed']) " + str(record['calls completed']))
                    # print("Debug: int(record['calls failed']) " + str(record['calls failed']))
                    # print("Debug: int(record['mos-lqo#']) " + str(record['mos-lqo#']))
                    # print("Debug: record['state'] " + str(record['state']))
                    # print()

                    # exit if endp is scoring polqa/pesq and test is stopped.
                    # wait until last call data is fetched
                    # both endp needs to stop separately as we are in a for loop.
                    if int(record['calls completed']) + int(record['calls failed']) == int(record['mos-lqo#']) + 1:
                        if "Stopped" == record['state']:
                            num_running_ep -= 1

                    # exit if other endp is not scoring polqa/pesq and test is stopped.
                    if int(record['mos-lqo#']) == 0:
                        if "Stopped" == record['state']:
                            num_running_ep -= 1

            except Exception as e:
                # self.write_rows()
                traceback.print_exc()
                pprint(['exception:', e, 'e_w_list:', e_w_list])
                self.write_rows()
                exit(1)
            # self.write_rows()

    def report(self):
        self.write_rows()
        print(f"saved {self.csv_filename}")
        print("Script is done....")
        self.csv_fileh.close()


def parse_args():
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--host", "--mgr",
                        dest="host",
                        help="URL of the LANforge GUI machine (localhost is default, http://localhost:8080)",
                        type=str,
                        default="localhost")
    parser.add_argument("--csv_file",
                        help="name of the csv output file",
                        type=str)
    parser.add_argument("--cx_list", "--cx_names",
                        dest="cx_list",
                        help="comma separated list of voip connection names, or 'ALL'",
                        type=str)
    parser.add_argument("--debug",
                        help='Enable debugging',
                        action="store_true",
                        default=False)
    parser.add_argument("--log_level",
                        help='debug message verbosity',
                        type=str)

    return parser.parse_args()


def main():
    lfjson_host = "localhost"
    args = parse_args()

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
