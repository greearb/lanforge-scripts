#!/usr/bin/env python3

"""
Note: To Run this script gui should be opened with

    path: cd LANforgeGUI_5.4.3 (5.4.3 can be changed with GUI version)
          pwd (Output : /home/lanforge/LANforgeGUI_5.4.3)
          ./lfclient.bash -cli-socket 3990

This script is used to automate running Rate-vs-Range tests.  You
may need to view a Rate-vs-Range test configured through the GUI to understand
the options and how best to input data.
    
    ./lf_rvr_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge \
      --instance_name rvr-instance --config_name test_con --upstream 1.2.eth2 \
      --dut linksys-8450 --duration 15s --station 1.1.sta01500 \
      --download_speed 85% --upload_speed 0 \
      --raw_line 'pkts: MTU' \
      --raw_line 'directions: DUT Transmit;DUT Receive' \
      --raw_line 'traffic_types: UDP;TCP' \
      --test_rig Testbed-01 --pull_report \
      --influx_host c7-graphana --influx_port 8086 --influx_org Candela \
      --influx_token=-u_Wd-L8o992701QF0c5UmqEp7w7Z7YOMaWLxOMgmHfATJGnQbbmYyNxHBR9PgD6taM_tcxqJl6U8DjU1xINFQ== \
      --influx_bucket ben \
      --influx_tag testbed Ferndale-Advanced

Note:
    --raw_line 'line contents' will add any setting to the test config.  This is
        useful way to support any options not specifically enabled by the
        command options.
    --set modifications will be applied after the other config has happened,
        so it can be used to override any other config.

Example of raw text config for Dataplane, to show other possible options:


"""

import sys
import os
import argparse
import time
import json
from os import path

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

from cv_test_manager import cv_test as cvtest
from cv_test_manager import *
from cv_commands import chamberview as cv


class RvrTest(cvtest):
    def __init__(self,
                 lf_host="localhost",
                 lf_port=8080,
                 lf_user="lanforge",
                 lf_password="lanforge",
                 instance_name="rvr_instance",
                 config_name="rvr_config",
                 upstream="1.1.eth2",
                 pull_report=False,
                 load_old_cfg=False,
                 upload_speed="0",
                 download_speed="85%",
                 duration="15s",
                 station="1.1.sta01500",
                 dut="NA",
                 enables=[],
                 disables=[],
                 raw_lines=[],
                 raw_lines_file="",
                 sets=[],
                 ):
        super().__init__(lfclient_host=lf_host, lfclient_port=lf_port)

        self.lf_host = lf_host
        self.lf_port = lf_port
        self.lf_user = lf_user
        self.lf_password =lf_password
        self.createCV = cv(lf_host, lf_port);
        self.instance_name = instance_name
        self.config_name = config_name
        self.dut = dut
        self.duration = duration
        self.upstream = upstream
        self.station = station
        self.pull_report = pull_report
        self.load_old_cfg = load_old_cfg
        self.test_name = "Rate vs Range"
        self.upload_speed = upload_speed
        self.download_speed = download_speed
        self.enables = enables
        self.disables = disables
        self.raw_lines = raw_lines
        self.raw_lines_file = raw_lines_file
        self.sets = sets

    def setup(self):
        # Nothing to do at this time.
        return


    def run(self):
        self.createCV.sync_cv()
        time.sleep(2)
        self.createCV.sync_cv()

        blob_test = "rvr-test-latest-"

        self.rm_text_blob(self.config_name, blob_test)  # To delete old config with same name
        self.show_text_blob(None, None, False)

        # Test related settings
        cfg_options = []

        ### HERE###
        self.apply_cfg_options(cfg_options, self.enables, self.disables, self.raw_lines, self.raw_lines_file)

        # cmd line args take precedence and so come last in the cfg array.
        if self.upstream != "":
            cfg_options.append("upstream_port: " + self.upstream)
        if self.station != "":
            cfg_options.append("traffic_port: " + self.station)
        if self.download_speed != "":
            cfg_options.append("speed: " + self.download_speed)
        if self.upload_speed != "":
            cfg_options.append("speed2: " + self.upload_speed)
        if self.duration != "":
            cfg_options.append("duration: " + self.duration)
        if self.dut != "":
            cfg_options.append("selected_dut: " + self.dut)

        # We deleted the scenario earlier, now re-build new one line at a time.

        self.build_cfg(self.config_name, blob_test, cfg_options)

        cv_cmds = []
        self.create_and_run_test(self.load_old_cfg, self.test_name, self.instance_name,
                                 self.config_name, self.sets,
                                 self.pull_report, self.lf_host, self.lf_user, self.lf_password,
                                 cv_cmds)
        self.rm_text_blob(self.config_name, blob_test)  # To delete old config with same name


def main():

    parser = argparse.ArgumentParser("""
    Open this file in an editor and read the top notes for more details.

    Example:

    
      """
                                     )

    cv_add_base_parser(parser)  # see cv_test_manager.py

    parser.add_argument("-u", "--upstream", type=str, default="1.1.eth2",
                        help="Upstream port for wifi capacity test ex. 1.1.eth2")
    parser.add_argument("--station", type=str, default="1.1.sta01500",
                        help="Station to be used in this test, example: 1.1.sta01500")

    parser.add_argument("--dut", default="",
                        help="Specify DUT used by this test, example: linksys-8450")
    parser.add_argument("--download_speed", default="",
                        help="Specify requested download speed.  Percentage of theoretical is also supported.  Default: 85%")
    parser.add_argument("--upload_speed", default="",
                        help="Specify requested upload speed.  Percentage of theoretical is also supported.  Default: 0")
    parser.add_argument("--duration", default="",
                        help="Specify duration of each traffic run")

    args = parser.parse_args()

    cv_base_adjust_parser(args)

    CV_Test = RvrTest(lf_host = args.mgr,
                      lf_port = args.port,
                      lf_user = args.lf_user,
                      lf_password = args.lf_password,
                      instance_name = args.instance_name,
                      config_name = args.config_name,
                      upstream = args.upstream,
                      pull_report = args.pull_report,
                      load_old_cfg = args.load_old_cfg,
                      download_speed = args.download_speed,
                      upload_speed = args.upload_speed,
                      duration = args.duration,
                      dut = args.dut,
                      station = args.station,
                      enables = args.enable,
                      disables = args.disable,
                      raw_lines = args.raw_line,
                      raw_lines_file = args.raw_lines_file,
                      sets = args.set
                      )
    CV_Test.setup()
    CV_Test.run()

    CV_Test.check_influx_kpi(args)

if __name__ == "__main__":
    main()
