#!/usr/bin/env python3
"""
This script will start a named set of voip connections and report their data to a csv file

Example usage:
- Configure two VoIP CXs, TEST1 and TEST2.
    + TEST1:
        * 3 looped phone calls
        * Endpoint A: 1234 phone number, 11:11:11:11:11:11 Bluetooth MAC
        * Endpoint B: 5678 phone number, 22:22:22:22:22:22 Bluetooth MAC
    + TEST2:
        * 2 looped phone calls
        * Endpoint A: 8765 phone number, 33:33:33:33:33:33 Bluetooth MAC
        * Endpoint B: 4321 phone number, 44:44:44:44:44:44 Bluetooth MAC

    ./run_voip_cx.py \
        --mgr                       192.168.100.110 \
        --csv_file                  out.csv \
        --cx_names                  TEST1,TEST2 \
        --num_calls                 3                 2 \
        --side_a_phone_nums         1234              5678 \
        --side_b_phone_nums         8765              4321 \
        --side_a_mobile_bt_macs     11:11:11:11:11:11 22:22:22:22:22:22 \
        --side_b_mobile_bt_macs     33:33:33:33:33:33 44:44:44:44:44:44
"""


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


class VoipEndp:
    def __init__(self,
                 name: str,
                 num_calls: int = 0,
                 **kwargs):
        self._name: str = name

        self._phone_num: str = None
        self._mobile_bt_mac: str = None

        self._num_calls = num_calls

    @property
    def name(self):
        """Endpoint name."""
        return self._name

    @property
    def num_calls(self):
        """Number of calls for endpoint when in loop mode."""
        return self._num_calls

    @num_calls.setter
    def num_calls(self, num_calls: str):
        """Set number of calls for endpoint when in loop mode."""
        self._num_calls= num_calls

    @property
    def phone_num(self):
        """Endpoint phone number."""
        return self._phone_num

    @phone_num.setter
    def phone_num(self, phone_num: str):
        """Set endpoint phone number."""
        self._phone_num = phone_num

    @property
    def mobile_bt_mac(self):
        """Endpoint Bluetooth MAC, if resource is a phone."""
        return self._mobile_bt_mac

    @mobile_bt_mac.setter
    def mobile_bt_mac(self, mobile_bt_mac: str):
        """Set endpoint Bluetooth MAC, if resource is a phone."""
        self._mobile_bt_mac = mobile_bt_mac


class VoipCx:
    def __init__(self,
                 name: str,
                 endp_a: VoipEndp = None,
                 endp_b: VoipEndp = None,
                 **kwargs):
        self._name = name

        self._endp_a = endp_a
        self._endp_b = endp_b

    @property
    def name(self):
        """VoIP CX name."""
        return self._name

    @property
    def endp_a(self):
        """VoIP CX endpoint A."""
        return self._endp_a

    @property
    def endp_b(self):
        """VoIP CX endpoint B."""
        return self._endp_b


class VoipReport():
    def __init__(self,
                 lfsession: LFSession,
                 csv_file: str,
                 cx_names_str: str,
                 debug: bool,
                 **kwargs):
        """Initialize VoIP test."""
        self.lfsession = lfsession
        self.debug = debug

        self.__init_csv_output(csv_file=csv_file)
        self.__initialize_voip_cxs(cx_names_str=cx_names_str,
                                   **kwargs)

    def __init_csv_output(self, csv_file: str):
        """Initialize CSV output file."""

        # Parse CSV file, if specified. Otherwise, use generate default in `/home/lanforge/report-data/`
        csv_file_name = f"/home/lanforge/report-data/voip-{time.time()}.csv"
        if csv_file:
            self.csv_filename = csv_file
        else:
            self.csv_filename = csv_file_name
        logger.info(f"Test CSV output file is \'{csv_file_name}\'")

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

        # Attempt to open CSV file
        try:
            self.csv_fileh = open(self.csv_filename, "w")
            self.csv_writer = csv.writer(self.csv_fileh)
            self.csv_writer.writerow(self.ep_col_names)
            self.last_written_row = 0
        except Exception as e:
            e.print_exc()
            traceback.print_exc()
            exit(1)

    def __initialize_voip_cxs(self, cx_names_str: str, **kwargs):
        """
        Given user-specified list, initialize data structures
        used to store, configure, and query VoIP CXs.
        """
        logger.info("Initializing local CX data structures")

        self.cxs = []
        self.endps_a = []
        self.endps_b = []

        # Parse out CX list string into actual list of CX names
        cx_list = []
        if cx_names_str.find(',') < 0:
            # Only one cx name specified
            cx_list.append(cx_names_str)
        else:
            # Multiple cx names specified
            cx_list.extend(cx_names_str.split(','))

        # If only one CX and is 'all' or 'ALL', user specified to use all VoIP CXs.
        # Check for equality, as want to make sure user can specify
        # a cx name with string 'all' or 'ALL' in it.
        if len(cx_list) == 1 and (cx_list[0] == "all") or (cx_list[0]== "ALL"):
            logger.debug(f"Querying all VoIP CXs")
        else:
            logger.debug(f"Querying parsed VoIP CXs: {cx_list}")

        # TODO: Don't hardcode endpoint names
        #queried_endps = self.__query_voip_endps(endp_list=["all"])

        queried_cxs = self.__query_voip_cxs(cx_list=cx_list)
        for queried_cx in queried_cxs:
            # Queried Cx data is a list of dicts, where each dict
            # has a single key which is the CX name. For example:
            # [
            #   {'TEST1': {'name': 'TEST1'}},
            # ]
            cx_name = list(queried_cx.keys())[0]

            # CX endpoint A
            endp_a = VoipEndp(name=cx_name + "-A")
            self.endps_a.append(endp_a)

            # CX endpoint B
            endp_b = VoipEndp(name=cx_name + "-B")
            self.endps_b.append(endp_b)

            cx = VoipCx(name=cx_name,
                        endp_a=endp_a,
                        endp_b=endp_b,
                        **kwargs)
            self.cxs.append(cx)

        # Allow for user to specify VoIP endpoints settings,
        # regardless of whether specified individually or as all
        self.num_cxs = len(self.cxs)
        self.__configure_voip_endps(**kwargs)

    def __configure_voip_endps(self, **kwargs):
        """Configure settings on remote VoIP endpoints."""
        logger.info("Configuring remote VoIP endpoints")

        # Set endpoint number of phone calls (also referred to as loop call count)
        #
        # Since number of calls on both endpoints of a VoIP CX must match,
        # apply configured number of calls to both endpoints per CX
        if "num_calls" in kwargs:
            num_calls = kwargs["num_calls"]

            if num_calls:
                if len(num_calls) == 1:
                    # Apply same number of calls to all CXs' endpoints
                    for endp in (self.endps_a + self.endps_b):
                        endp.num_calls = num_calls[0]
                elif len(num_calls) == self.num_cxs:
                    for ix, cx_num_calls in enumerate(num_calls):
                        self.endps_a[ix].num_calls = cx_num_calls
                        self.endps_b[ix].num_calls = cx_num_calls
                else:
                    logger.error("Number of phone numbers does not match number of VoIP CXs.")
                    exit(1)

        # Set endpoint phone numbers
        if "side_a_phone_nums" in kwargs:
            side_a_phone_nums = kwargs["side_a_phone_nums"]

            if side_a_phone_nums:
                if len(side_a_phone_nums) != self.num_cxs:
                    logger.error("Number of endpoint A phone numbers does not match number of VoIP CXs.")
                    exit(1)

                for ix, phone_num in enumerate(side_a_phone_nums):
                    self.endps_a[ix].phone_num = phone_num

        if "side_b_phone_nums" in kwargs:
            side_b_phone_nums = kwargs["side_b_phone_nums"]

            if side_b_phone_nums:
                if len(side_b_phone_nums) != self.num_cxs:
                    logger.error("Number of endpoint B phone numbers does not match number of VoIP CXs.")
                    exit(1)

                for ix, phone_num in enumerate(side_b_phone_nums):
                    self.endps_b[ix].phone_num = phone_num

        # Set endpoint Bluetooth MAC addresses
        if "side_a_mobile_bt_macs" in kwargs:
            side_a_mobile_bt_macs = kwargs["side_a_mobile_bt_macs"]

            if side_a_mobile_bt_macs:
                if len(side_a_mobile_bt_macs) != self.num_cxs:
                    logger.error("Number of endpoint A mobile Bluetooth MACs does not match number of VoIP CXs.")
                    exit(1)

                for ix, bt_mac in enumerate(side_a_mobile_bt_macs):
                    self.endps_a[ix].mobile_bt_mac = bt_mac

        if "side_b_mobile_bt_macs" in kwargs:
            side_b_mobile_bt_macs = kwargs["side_b_mobile_bt_macs"]

            if side_b_mobile_bt_macs:
                if len(side_b_mobile_bt_macs) != self.num_cxs:
                    logger.error("Number of endpoint B mobile Bluetooth MACs does not match number of VoIP CXs.")
                    exit(1)

                for ix, bt_mac in enumerate(side_b_mobile_bt_macs):
                    self.endps_b[ix].mobile_bt_mac = bt_mac

        e_w_list: list = []
        lf_cmd: LFJsonCommand = self.lfsession.get_command()
        for endp in (self.endps_a + self.endps_b):
            e_w_list.clear()
            logger.debug(f"Configuring endpoint \'{endp.name}\'")
            try:
                lf_cmd.post_add_voip_endp(alias=endp.name,
                                          phone_num=endp.phone_num,
                                          mobile_bt_mac=endp.mobile_bt_mac)
                lf_cmd.post_set_voip_info(name=endp.name,
                                          loop_call_count=endp.num_calls)
            except Exception as e:
                logger.error(f"Error configuring endpoint \'{endp.name}\'")
                logger.error(pprint(['exception:', e, e_w_list]))


    def __query_voip_cxs(self, cx_list: list[str], columns: list[str] = ["name"]):
        """Query and return all VoIP CXs."""
        e_w_list: list = []
        lf_query: LFJsonQuery = self.lfsession.get_query()
        response = lf_query.get_voip(eid_list=cx_list,
                                     requested_col_names=columns,
                                     errors_warnings=e_w_list,
                                     debug=True)
        if not response:
            logger.error(f"Unable to query \'{columns}\' data for VoIP CXs \'{cx_list}\'")
            exit(1)

        # When multiple to return, returned as list of dicts.
        # When one to return, returned as just dict.
        # Package into list of dict (with single element) to simplify processing.
        if isinstance(response, dict):
            response = [response]

        return response


    def __query_voip_endps(self, endp_list: list[str], columns: list[str] = ["name"]):
        """Query and return all VoIP endpoints."""
        e_w_list: list = []
        lf_query: LFJsonQuery = self.lfsession.get_query()
        response = lf_query.get_voip_endp(eid_list=endp_list,
                                          requested_col_names=columns,
                                          errors_warnings=e_w_list,
                                          debug=True)
        if not response:
            logger.error(f"Unable to query \'{columns}\' data for VoIP endpoints \'{endp_list}\'")
            exit(1)

        # When multiple to return, returned as list of dicts.
        # When one to return, returned as just dict.
        # Package into list of dict (with single element) to simplify processing.
        if isinstance(response, dict):
            response = [response]

        return response

    def start(self):
        """Start specified VoIP CXs."""
        logger.debug(f"Starting CXs")

        e_w_list: list = []
        lf_cmd: LFJsonCommand = self.lfsession.get_command()

        for cx in self.cxs:
            e_w_list.clear()
            cx_name = cx.name

            try:
                logger.debug(f"Starting CX \'{cx_name}\'")
                lf_cmd.post_set_cx_state(cx_name=cx_name,
                                        test_mgr='ALL',
                                        suppress_related_commands=True,
                                        cx_state=lf_cmd.SetCxStateCxState.RUNNING.value,
                                        errors_warnings=e_w_list)
            except Exception as e:
                pprint(['exception:', e, "cx:", cx_name, e_w_list])

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

        all_endps = [cx.endp_a.name for cx in self.cxs] + [cx.endp_b.name for cx in self.cxs]
        num_running_ep = len(all_endps)

        # stop until endpoints actually starts the test else script terminates early.
        while wait_flag_A or wait_flag_B:
            response = lf_query.get_voip_endp(eid_list=all_endps,
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
                response = lf_query.get_voip_endp(eid_list=all_endps,
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
                        required=True,
                        type=str)
    parser.add_argument("--cx_list", "--cx_names",
                        dest="cx_names_str",
                        help="comma separated list of voip connection names, or 'ALL'",
                        required=True,
                        type=str)
    parser.add_argument("--debug",
                        help='Enable debugging',
                        action="store_true",
                        default=False)
    parser.add_argument("--log_level",
                        help='debug message verbosity',
                        type=str)

    # Could make this endpoint specific (like phone nums), but stick w/ simple for now
    parser.add_argument("--num_calls", "--loop_call_count",
                        dest="num_calls",
                        help="Number of calls to make in looped mode. "
                             "If one number specified, applies to all CXs specified. "
                             "If more than one number specified, each number matches the CX specified "
                             "\'--cx_list\' argument (order and length must match).",
                        nargs="*")

    # Configuration to apply to CXs/endpoints
    parser.add_argument("--side_a_phone_nums", "--side_a_phone_numbers",
                        dest="side_a_phone_nums",
                        help="List of phone numbers to configure on side A VoIP endpoints. "
                             "Order and length must match the order of connections passed in the "
                             "\'--cx_list\' argument.",
                        nargs="*")
    parser.add_argument("--side_b_phone_nums", "--side_b_phone_numbers",
                        dest="side_b_phone_nums",
                        help="List of phone numbers to configure on side A VoIP endpoints. "
                             "Order and length must match the order of connections passed in the "
                             "\'--cx_list\' argument.",
                        nargs="*")
    parser.add_argument("--side_a_mobile_bt_macs",
                        help="List of Bluetooth MAC addresses to configure on side A VoIP endpoints. "
                             "Order and length must match the order of connections passed in the "
                             "\'--cx_list\' argument.",
                        nargs="*")
    parser.add_argument("--side_b_mobile_bt_macs",
                        help="List of Bluetooth MAC addresses to configure on side A VoIP endpoints. "
                             "Order and length must match the order of connections passed in the "
                             "\'--cx_list\' argument.",
                        nargs="*")

    return parser.parse_args()


def main():
    args = parse_args()
    lfapi_session = LFSession(lfclient_url=args.host,
                              debug=args.debug)

    # The '**vars(args)' unpacks arguments into named parameters
    # of the VoipReport initializer.
    voip_report = VoipReport(lfsession=lfapi_session,
                             **vars(args))
    voip_report.start()
    voip_report.monitor()
    voip_report.report()


if __name__ == "__main__":
    main()
