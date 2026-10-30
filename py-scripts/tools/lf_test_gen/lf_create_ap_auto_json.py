#!/usr/bin/env python3

'''
NAME: lf_create_ap_auto_json.py

PURPOSE:
     This script will create a lf_wc.json file that is used as a input --json_test to the lf_check.py script
     This script helps to store the of the information on LANforge
EXAMPLE:
    # For creating wifi capacity test json file according to the Tests present:



SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:   Functional

NOTES:

STATUS: Development

VERIFIED_ON:

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2024 Candela Technologies Inc


'''

import argparse
import json
import re
import shlex
import logging
import importlib
import os
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)


# sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../../../")))


logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("lf_logger_config")


class lf_create_ap_auto_json():
    def __init__(self,
                 _file_2g,
                 _file_5g,
                 _file_6g,
                 _dir_2g,
                 _dir_5g,
                 _dir_6g,
                 _ap_auto_duration,
                 _use_radio_dict,
                 _radio_dict,
                 _radio_type_dict,
                 _radio_max_sta_dict,
                 _use_radio_var_dict,
                 _use_radio_2g_var_dict,
                 _use_radio_5g_var_dict,
                 _use_radio_6g_var_dict,
                 _suite_radios_2g,
                 _suite_radios_5g,
                 _suite_radios_6g,
                 _suite_test_name_2g_dict,
                 _suite_test_name_5g_dict,
                 _suite_test_name_6g_dict,
                 _radio_count,
                 _radio_batch_dict,
                 _lf_ap_auto_use_qa_var,
                 _lf_ap_auto_use_inspect_var,
                 _lf_radio_2g,
                 _lf_radio_5g,
                 _lf_radio_6g,
                 _lf_ap_auto_number_dut_indexes_combobox,
                 _lf_ap_auto_basic_client_connectivity,  # basic_cx
                 _lf_ap_auto_band_steering,  # band_steering
                 _lf_ap_auto_capacity,  # capacity
                 _lf_ap_auto_channel_switching_test,  # channel_switch
                 _lf_ap_auto_long_term,  # long_term
                 _lf_ap_auto_stability,  # mix_stability
                 _lf_ap_auto_throughput_vs_pkt_size,  # tput_single_sta
                 _lf_ap_auto_multi_station_throughput_vs_pkt_size,  # tput_multi_sta
                 _lf_ap_auto_use_combined_var=None,
                 _use_idx_entry_var_dict=None,
                 _upstream_port="1.1.eth2",
                 ):
        self.upstream_port = _upstream_port.strip()
        self.lf_radios = {"2g": _lf_radio_2g, "5g": _lf_radio_5g, "6g": _lf_radio_6g}
        self.combined = (_lf_ap_auto_use_combined_var is not None
                         and _lf_ap_auto_use_combined_var.get() == "Use")
        self.number_dut_indexes = int(_lf_ap_auto_number_dut_indexes_combobox.get())
        if not 1 <= self.number_dut_indexes <= 4:
            raise ValueError("Number DUT Indexes must be between 1 and 4.")
        self.use_idx_entry_var_dict = _use_idx_entry_var_dict
        self.test_suite_band = ""
        self.use_radio_dict = _use_radio_dict
        self.radio_dict = _radio_dict
        self.radio_dict_size = len(self.radio_dict)
        self.radio_type_dict = _radio_type_dict
        self.radio_max_sta_dict = _radio_max_sta_dict
        self.use_radio_var_dict = _use_radio_var_dict
        self.radio_count = _radio_count
        self.radio_batch_dict = _radio_batch_dict

        self.lf_ap_auto_basic_client_connectivity = _lf_ap_auto_basic_client_connectivity
        self.lf_ap_auto_band_steering = _lf_ap_auto_band_steering
        self.lf_ap_auto_multi_station_throughput_vs_pkt_size = _lf_ap_auto_multi_station_throughput_vs_pkt_size
        self.lf_ap_auto_stability = _lf_ap_auto_stability
        self.lf_ap_auto_channel_switching_test = _lf_ap_auto_channel_switching_test
        self.lf_ap_auto_throughput_vs_pkt_size = _lf_ap_auto_throughput_vs_pkt_size
        self.lf_ap_auto_capacity = _lf_ap_auto_capacity
        # self.lf_ap_auto_band_steering = _lf_ap_auto_band_steering
        self.lf_ap_auto_long_term = _lf_ap_auto_long_term

        self.lf_ap_auto_use_qa_var = _lf_ap_auto_use_qa_var
        self.lf_ap_auto_use_inspect_var = _lf_ap_auto_use_inspect_var
        self.radio_index = ""

        # TODO Future copy generated file to alternate file (low priority until requeste)
        self.dir_2g = _dir_2g
        self.dir_5g = _dir_5g
        self.dir_6g = _dir_6g

        self.file_2g = _file_2g
        self.file_5g = _file_5g
        self.file_6g = _file_6g

        if self.file_2g == "":
            self.file_2g = "ct_perf_ap_auto_2g" + _suite_radios_2g + ".json"
        if self.file_5g == "":
            self.file_5g = "ct_perf_ap_auto_5g" + _suite_radios_5g + ".json"
        if self.file_6g == "":
            self.file_6g = "ct_perf_ap_auto_6g" + _suite_radios_6g + ".json"

        self.dir_file_2g = ""
        self.dir_file_5g = ""
        self.dir_file_6g = ""

        if self.dir_2g != "":
            self.dir_file_2g = os.path.join(self.dir_2g, self.file_2g)
        else:
            self.dir_file_2g = self.file_2g

        if self.dir_5g != "":
            self.dir_file_5g = os.path.join(self.dir_5g, self.file_5g)
        else:
            self.dir_file_5g = self.file_5g

        if self.dir_6g != "":
            self.dir_file_6g = os.path.join(self.dir_6g, self.file_6g)
        else:
            self.dir_file_6g = self.file_6g

        if _ap_auto_duration == "":
            self.ap_auto_duration = '20000'
        else:
            self.ap_auto_duration = _ap_auto_duration.split()[0]
        if not self.ap_auto_duration.isdigit() or int(self.ap_auto_duration) <= 0:
            raise ValueError("AP Auto duration must be a positive number of milliseconds.")

        self.use_radio_2g_var_dict = _use_radio_2g_var_dict
        self.use_radio_5g_var_dict = _use_radio_5g_var_dict
        self.use_radio_6g_var_dict = _use_radio_6g_var_dict

        self.suite_radios_2g = "ct_perf_ap_auto_2g" + _suite_radios_2g
        self.suite_radios_5g = "ct_perf_ap_auto_5g" + _suite_radios_5g
        self.suite_radios_6g = "ct_perf_ap_auto_6g" + _suite_radios_6g

        self.suite_test_name_2g_dict = _suite_test_name_2g_dict
        self.suite_test_name_5g_dict = _suite_test_name_5g_dict
        self.suite_test_name_6g_dict = _suite_test_name_6g_dict

        self.ap_auto_2g_json = ""
        self.ap_auto_5g_json = ""
        self.ap_auto_6g_json = ""

        self.last_2g_radio = 0

    def get_file_2g(self):
        return self.file_2g

    def get_file_5g(self):
        return self.file_5g

    def get_file_6g(self):
        return self.file_6g

    def get_dir_2g(self):
        return os.path.dirname(os.path.abspath(self.dir_file_2g))

    def get_dir_5g(self):
        return os.path.dirname(os.path.abspath(self.dir_file_5g))

    def get_dir_6g(self):
        return os.path.dirname(os.path.abspath(self.dir_file_6g))

    # Helper methods

    def validate_settings(self):
        """Check all active bands before creating any output files."""
        if not re.fullmatch(r"[1-9][0-9]*\.[1-9][0-9]*\.[^\s.]+", self.upstream_port):
            raise ValueError("Enter a DUT upstream port such as 1.1.eth2.")
        if not any(var.get() == "Use" for var in self._test_options().values()):
            raise ValueError("Select at least one AP Auto test.")
        for band in ("2g", "5g", "6g"):
            if self._selected_radios(band):
                self._dut_index(band)

    def _test_options(self):
        return {
            "basic_cx": self.lf_ap_auto_basic_client_connectivity,
            "band_steering": self.lf_ap_auto_band_steering,
            "capacity": self.lf_ap_auto_capacity,
            "channel_switch": self.lf_ap_auto_channel_switching_test,
            "long_term": self.lf_ap_auto_long_term,
            "mix_stability": self.lf_ap_auto_stability,
            "tput_single_sta": self.lf_ap_auto_throughput_vs_pkt_size,
            "tput_multi_sta": self.lf_ap_auto_multi_station_throughput_vs_pkt_size,
        }

    def _selected_radios(self, band):
        selected = getattr(self, f"use_radio_{band}_var_dict")
        return [radio for radio in self.radio_dict
                if self.use_radio_var_dict[radio].get() == "Use" and selected[radio].get() == "Use"]

    def _dut_index(self, band):
        match = re.fullmatch(r"Radio-([1-4])", self.lf_radios[band])
        if match is None:
            raise ValueError(f"Select a DUT radio (Radio-1 through Radio-4) for {band}.")
        index = int(match.group(1)) - 1
        if index >= self.number_dut_indexes:
            raise ValueError(f"{band} uses Radio-{index + 1}; increase Number DUT Indexes or change its DUT radio.")
        if self.use_idx_entry_var_dict is not None:
            for idx in range(self.number_dut_indexes):
                if self.use_idx_entry_var_dict[idx].get() != "Use":
                    raise ValueError(f"Enable DUT index {idx} or reduce Number DUT Indexes.")
        return index

    @staticmethod
    def _entry(command, args, **options):
        return {"enabled": "TRUE", "load_db": "skip", "command": command,
                "args": "", "args_list": args, **options}

    def create_suite(self):
        self.validate_settings()
        band = self.test_suite_band
        if band not in ("2g", "5g", "6g"):
            raise ValueError(f"Unknown AP Auto band: {band}")
        selected = self._selected_radios(band)
        if not selected:
            raise ValueError(f"No radios selected for {band}.")
        index = self._dut_index(band)
        groups = [selected] if self.combined else [[radio] for radio in selected]
        suite = {}
        for radios in groups:
            names = getattr(self, f"suite_test_name_{band}_dict")
            suffix = "_".join(self.radio_dict[r].get().strip().replace(".", "_") for r in radios)
            model = "combined" if self.combined else names[radios[0]].get()
            name = f"{model}_{band.upper()}_{suffix}"
            dut_args = [" --lfmgr LF_MGR_IP --port LF_MGR_PORT --dut_name USE_DUT_NAME"]
            dut_args.extend(
                f" --ssid 'ssid_idx={idx} ssid=SSID_USED security=SECURITY_USED password=SSID_PW_USED bssid=BSSID_TO_USE'"
                for idx in range(self.number_dut_indexes))
            dut_args.extend([
                " --sw_version DUT_SW --hw_version DUT_HW --serial_num DUT_SERIAL --model_num DUT_MODEL",
                " --dut_flag DHCPD-LAN",
            ])
            suite[f"CC_DUT_{name}"] = self._entry("create_chamberview_dut.py", dut_args)
            scenario_args = [" --lfmgr LF_MGR_IP --port LF_MGR_PORT --delete_scenario",
                             f" --create_scenario {shlex.quote(name)}"]
            station_count = 0
            for radio in radios:
                shelf, resource, phy = self.radio_dict[radio].get().strip().split(".")
                count = max(int(n) for n in self.radio_batch_dict[radio].get().split(","))
                station_count += count
                line = (f"profile_link {shelf}.{resource} STA-AUTO {count} "
                        f"'DUT: USE_DUT_NAME {self.lf_radios[band]}' NA {phy},AUTO -1 NA")
                scenario_args.append(f" --raw_line {shlex.quote(line)}")
            # The upstream may live on a different resource from the station radios.
            scenario_args.append(
                f" --raw_line \"profile_link {self.upstream_port.rsplit('.', 1)[0]} upstream 1 'DUT: USE_DUT_NAME LAN' NA UPSTREAM_ALIAS,AUTO -1 NA\"")
            suite[f"CC_{name}"] = self._entry("create_chamberview.py", scenario_args)
            args = [
                f" --mgr LF_MGR_IP --port LF_MGR_PORT --lf_user LF_MGR_USER --lf_password LF_MGR_PASS --instance_name {shlex.quote(name)}",
                " --upstream UPSTREAM_PORT",
                f" use_ssid_idx={index} --dut{band[0]}_0 'USE_DUT_NAME SSID_USED BSSID_TO_USE ({index + 1})'",
                f" --max_stations_{band[0]} {station_count}",
            ]
            args.extend(f" --radio{band[0]} {self.radio_dict[r].get().strip()}" for r in radios)
            args.extend(f" --set '{key}' {int(var.get() == 'Use')}" for key, var in self._test_options().items())
            args.append(" --set 'tput_multi_band' 0")
            for other in ("2", "5", "5b", "6", "dual", "tri", "tri_5b"):
                args.append(f" --set 'skip_{other}' {int(other != band[0])}")
            seconds = format(int(self.ap_auto_duration) / 1000, "g")
            for key, value in (("dur20", seconds), ("reset_duration_min", self.ap_auto_duration),
                               ("reset_duration_max", self.ap_auto_duration), ("loop_iter", "1"),
                               ("cx_psk_thresh", "500")):
                args.append(f" --raw_line '{key}: {value}'")
            args.extend([
                " --test_rig TEST_RIG", " --set DUT_SET_NAME", " --verbosity 11",
                f" --pull_report --local_lf_report_dir REPORT_PATH --test_tag {shlex.quote(name)}",
            ])
            suite[f"ap_auto_{name}"] = self._entry("lf_ap_auto_test.py", args, timeout="600", iterations="1")
        if self.lf_ap_auto_use_qa_var.get() == "Use":
            suite["lf_qa"] = self._entry("./tools/lf_qa.py", [
                " --server TEST_SERVER --path REPORT_PATH --store --png --database DATABASE_SQLITE --test_suite TEST_SUITE"
            ], timeout="600")
        if self.lf_ap_auto_use_inspect_var.get() == "Use":
            suite["lf_inspect"] = self._entry("./tools/lf_inspect.py", [
                " --path REPORT_PATH --database DATABASE_SQLITE --test_suite TEST_SUITE --db_index 1,0"
            ], timeout="600")
        data = {"ct_ap_auto_tests_scripts": {"Notes": ["AP Auto tests generated for lf_check.py"]},
                "test_suites": {getattr(self, f"suite_radios_{band}"): suite}}
        self.ap_auto_band_json = json.dumps(data, indent=4) + "\n"
        path = getattr(self, f"dir_file_{band}")
        with open(path, "w") as output:
            output.write(self.ap_auto_band_json)


def main():

    parser = argparse.ArgumentParser(
        prog='lf_create_ap_auto_json.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        lf_create_ap_auto_json.py creates
        NOTE: cannot have extra blank lines at the end of the json to work properly

            ''',
        description='''\
NAME: lf_create_ap_auto_json.py

PURPOSE:
EXAMPLE:


SCRIPT_CLASSIFICATION:  Creation

SCRIPT_CATEGORIES:   Functional

NOTES:
        This will create a file with the name specified in the CLI  [ --json_rig example_name.json ]
        * Helps to store the data related to the LANforge

STATUS: BETA RELEASE

VERIFIED_ON: December 20 2024,
             Build Version:  5.4.9
             Kernel Version: 6.11.11+

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2024 Candela Technologies Inc

INCLUDE_IN_README: False
''')

    parser.add_argument('--log_level',
                        default=None,
                        help='Set logging level: debug | info | warning | error | critical')

    # logging configuration
    parser.add_argument(
        "--lf_logger_config_json",
        help="--lf_logger_config_json <json file> , json configuration of logger")

    args = parser.parse_args()

    # set up logger
    logger_config = lf_logger_config.lf_logger_config()

    # set the logger level to debug
    if args.log_level:
        logger_config.set_level(level=args.log_level)

    # lf_logger_config_json will take presidence to changing debug levels
    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()


if __name__ == '__main__':
    main()
