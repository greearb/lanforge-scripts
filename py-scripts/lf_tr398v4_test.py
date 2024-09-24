#!/usr/bin/env python3
# flake8: noqa
"""
Note: To Run this script gui should be opened with

    path: cd LANforgeGUI_5.4.7 (5.4.7 can be changed with GUI version)
          pwd (Output : /home/lanforge/LANforgeGUI_5.4.7)
          ./lfclient.bash -cli-socket 3990

This script is used to automate running TR398v4 tests.  You
may need to view a TR398v4 test configured through the GUI to understand
the options and how best to input data.

    Example 1 :
    
    ./lf_tr398v4_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge \
      --instance_name tr398-instance --config_name test_con \
      --upstream 1.2.eth2 \
      --test_rig Testbed-01 --pull_report \
      --local_lf_report_dir=/tmp/my_report \
      --dut6 'TR398-DUT ruckus750-5 4c:b1:cd:18:e8:eb (3)' \
      --dut5 'TR398-DUT ruckus750-5 4c:b1:cd:18:e8:ec (1)' \
      --dut2 'TR398-DUT ruckus750-2 4c:b1:cd:18:e8:e8 (2)' \
      --raw_lines_file cv_examples/example_cfgs/tr398v4-ferndale-be-cfg.txt \
      --set 'Calibrate 802.11AX Attenuators' 0 \
      --set 'Calibrate Virt-Sta Attenuators' 0 \
      --set '6.1.1 Receiver Sensitivity' 0 \
      --set '6.2.1 Maximum Connection' 0 \
      --set '6.2.2 Maximum Throughput' 1 \
      --set '6.2.3 Airtime Fairness' 0 \
      --set '6.2.4 Dual-Band Throughput' 0 \
      --set '6.2.5 Bi-Directional Throughput' 0 \
      --set '6.3.1 Range Versus Rate' 0 \
      --set '6.3.2 Spatial Consistency' 0 \
      --set '6.3.3 AX Peak Performance' 0 \
      --set '6.4.1 Multiple STAs Performance' 0 \
      --set '6.4.2 Multiple Assoc Stability' 0 \
      --set '6.4.3 Downlink MU-MIMO' 0 \
      --set '6.5.2 AP Coexistence' 0 \
      --set '6.5.1 Long Term Stability' 0

    Example 2:

    ./lf_tr398v4_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge  \
     --instance_name tr398-max-throughput  --upstream 1.1.eth2  --local_lf_report_dir /home/lanforge/Desktop \
     --pull_report --config_name MAX_THROUGHPUT
    

Note:
    --raw_line 'line contents' will add any setting to the test config. It is not required. This is
        useful way to support any options not specifically enabled by the
        command options.
    --set modifications will be applied after the other config has happened,
        so it can be used to override any other config.  Above, we are disabling many
        of the subtests, and enabling just Maximum Connection and Maximum Throughput
        tests.

    The RSSI values are calibrated, so you will need to run the calibration step and
    call with appropriate values for your particular testbed.  This is loaded from
    cv_examples/example_cfgs/tr398v4-ferndale-be-cfg.txt in this example.
    Contents of that file is a list of raw lines, for instance:

rssi_0_2-0: -26
rssi_0_2-1: -26
rssi_0_2-2: -26
....

The preferred way to get the raw text config file is to manually configure the TR398v4 test,
then use the 'Show Configuration' button on the Advanced Configuration tab and paste that text
into the raw text config file.

"""
import sys
import os
import importlib
import argparse
import time
import json
from os import path

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

cv_test_manager = importlib.import_module("py-json.cv_test_manager")
cvtest = cv_test_manager.cv_test
cv_add_base_parser = cv_test_manager.cv_add_base_parser
cv_base_adjust_parser = cv_test_manager.cv_base_adjust_parser


class TR398v4Test(cvtest):
    def __init__(self,
                 lf_host="localhost",
                 lf_port=8080,
                 lf_user="lanforge",
                 lf_password="lanforge",
                 instance_name="tr398_instance",
                 config_name="tr398_config",
                 upstream="1.2.eth2",
                 test_rig="",
                 local_lf_report_dir="",
                 pull_report=False,
                 load_old_cfg=False,
                 raw_lines_file="",
                 dut6="",
                 dut5="",
                 dut2="",
                 enables=None,
                 disables=None,
                 raw_lines=None,
                 sets=None,
                 ):
        super().__init__(lfclient_host=lf_host, lfclient_port=lf_port)

        if enables is None:
            enables = []
        if disables is None:
            disables = []
        if raw_lines is None:
            raw_lines = []
        if sets is None:
            sets = []

        self.lf_host                = lf_host
        self.lf_port                = lf_port
        self.lf_user                = lf_user
        self.lf_password            = lf_password
        self.instance_name          = instance_name
        self.config_name            = config_name
        self.dut6                   = dut6
        self.dut5                   = dut5
        self.dut2                   = dut2
        self.raw_lines_file         = raw_lines_file
        self.upstream               = upstream
        self.pull_report            = pull_report
        self.load_old_cfg           = load_old_cfg
        self.test_name              = "TR-398 Issue 4"
        self.enables                = enables
        self.disables               = disables
        self.raw_lines              = raw_lines
        self.sets                   = sets
        self.local_lf_report_dir    = local_lf_report_dir
        self.test_rig               = test_rig

    def setup(self):
        # Nothing to do at this time.
        return

    def run(self):
        self.sync_cv()
        time.sleep(2)
        self.sync_cv()

        blob_test = "TR-398v4-"

        # To delete old config with same name
        self.rm_text_blob(config_name=self.config_name,
                          blob_test_name=blob_test)
        self.show_text_blob(config_name=None,
                            blob_test_name=None,
                            brief=False)

        # Test related settings

        # These options are so that the config is 3rd priority, the built-in method is first, and any raw-line is 2nd. 
        # all cfgs are added to the cfg options and the array will be read top to bottom. so last cfg option will override the old c
        cfg_options = []

        self.apply_cfg_options(cfg_options=cfg_options,
                               enables=self.enables,
                               disables=self.disables,
                               raw_lines=self.raw_lines,
                               raw_lines_file=self.raw_lines_file)

        # cmd line args take precedence
        if self.upstream != "":
            cfg_options.append("upstream_port: " + self.upstream)
        if self.dut6 != "":
            cfg_options.append("selected_dut6: " + self.dut6)
        if self.dut5 != "":
            cfg_options.append("selected_dut5: " + self.dut5)
        if self.dut2 != "":
            cfg_options.append("selected_dut2: " + self.dut2)
        if self.test_rig != "":
            cfg_options.append("test_rig: " + self.test_rig)

        # We deleted the scenario earlier, now re-build new one line at a time.
        # print("here are the cfg options: ", cfg_options)
        self.build_cfg(config_name=self.config_name,
                       blob_test=blob_test,
                       cfg_options=cfg_options)

        cv_cmds = []
        self.create_and_run_test(load_old_cfg=self.load_old_cfg,
                                 test_name=self.test_name,
                                 instance_name=self.instance_name,
                                 config_name=self.config_name,
                                 sets=self.sets,
                                 pull_report=self.pull_report,
                                 lf_host=self.lf_host,
                                 lf_user=self.lf_user,
                                 lf_password=self.lf_password,
                                 cv_cmds=cv_cmds,
                                 local_lf_report_dir=self.local_lf_report_dir)

        # To delete old config with same name
        self.rm_text_blob(config_name=self.config_name,
                          blob_test_name=blob_test)


def main():
    help_summary = '''\
    Automate running TR398 issue 4 tests.  See cv_examples/run_tr398_71.bash
    for example of how to use this in a larger context.
    '''

    parser = argparse.ArgumentParser("""
    Open this file in an editor and read the top notes for more details.

    Example:

  ./lf_tr398v4_test.py --mgr localhost --port 8080 --lf_user lanforge --lf_password lanforge \\
      --instance_name tr398-instance --config_name test_con \\
      --upstream 1.2.eth2 \\
      --test_rig Testbed-01 --pull_report \\
      --local_lf_report_dir /tmp/my-report \\
      --dut6 'TR398-DUT-r750 ruckus-r750-5g 4c:b1:cd:18:e8:eb (3)' \\
      --dut5 'TR398-DUT-r750 ruckus-r750-5g 4c:b1:cd:18:e8:ec (1)' \\
      --dut2 'TR398-DUT-r750 ruckus-r750-2g 4c:b1:cd:18:e8:e8 (2)' \\
      --raw_lines_file cv_examples/example_cfgs/tr398v4-ferndale-be-cfg.txt \\
      --set 'Calibrate 802.11AX Attenuators' 0 \\
      --set 'Calibrate 802.11AC Attenuators' 0 \\
      --set '6.1.1 Receiver Sensitivity' 0 \\
      --set '6.2.1 Maximum Connection' 0 \\
      --set '6.2.2 Maximum Throughput' 1 \\
      --set '6.2.3 Airtime Fairness' 0 \\
      --set '6.2.4 Dual-Band Throughput' 0 \\
      --set '6.2.5 Bi-Directional Throughput' 0 \\
      --set '6.3.1 Range Versus Rate' 0 \\
      --set '6.3.2 Spatial Consistency' 0 \\
      --set '6.3.3 AX Peak Performance' 0 \\
      --set '6.4.1 Multiple STAs Performance' 0 \\
      --set '6.4.2 Multiple Assoc Stability' 0 \\
      --set '6.4.3 Downlink MU-MIMO' 0 \\
      --set '6.5.2 AP Coexistence' 0 \\
      --set '6.5.1 Long Term Stability' 0

  ./lf_tr398v4_test.py --mgr 192.168.100.105 --port 8080 --lf_user lanforge\\
    --lf_password lanforge --instance_name x \\
    --config_name testing --pull_report \\
    --local_lf_report_dir /tmp --dut5 'ASUS_70 ASUS_70 f0:2f:74:7c:a5:70 (1)' \\ 
    --dut2 'ASUS_70 ASUS_70 f0:2f:74:7c:a5:70 (1)' --raw_line "upstream_port: 1.1.eth2"
    

   The contents of the 'raw_lines_file' argument can be obtained by manually configuring the
   TR398 issue 2 test in the LANforge GUI, then selecting 'Show Config' in the Advanced configuration tab, then
   highlighting and pasting that text into file.  That file is the argument to the --raw_lines_file parameter.

   Each TR398 test's setting values can be specified by the python script in multiple ways.
   For example, each test needs an upstream port. The python script can specify upstream port in several ways
   and below is the hierarchy of which upstream port will be the final one in the settings.
    1. --upstream_port argument
    2. --raw_lines argument in the command line
    3. upstream port specified in the --raw_lines_file file.txt
    4. upsteam port loaded from the --config argument



      """
                                     )

    cv_add_base_parser(parser)  # see cv_test_manager.py

    parser.add_argument("-u", "--upstream", type=str, default="",
                        help="Upstream port for wifi capacity test ex. 1.1.eth2")

    parser.add_argument("--dut2", default="",
                        help="Specify 2Ghz DUT used by this test, example: 'TR398-DUT-r750 ruckus-r750-2g 4c:b1:cd:18:e8:e8 (2)'")
    parser.add_argument("--dut5", default="",
                        help="Specify 5Ghz DUT used by this test, example: 'TR398-DUT-r750 ruckus-r750-5g 4c:b1:cd:18:e8:ec (1)'")
    parser.add_argument("--dut6", default="",
                        help="Specify 6Ghz DUT used by this test, example: 'TR398-DUT-r750 ruckus-r750-6g 4c:b1:cd:18:e8:eb (3)'")
    parser.add_argument("--local_lf_report_dir",
                        help="--local_lf_report_dir <where to pull reports to>  default '' means put in current working directory",
                        default="")
    parser.add_argument('--help_summary', help='Show summary of what this script does', default=None,
                        action="store_true")

    args = parser.parse_args()

    # help_summary
    if args.help_summary:
        print(help_summary)
        exit(0)

    cv_base_adjust_parser(args)

    CV_Test = TR398v4Test(lf_host=args.mgr,
                          lf_port=args.port,
                          lf_user=args.lf_user,
                          lf_password=args.lf_password,
                          instance_name=args.instance_name,
                          config_name=args.config_name,
                          upstream=args.upstream,
                          pull_report=args.pull_report,
                          local_lf_report_dir=args.local_lf_report_dir,
                          load_old_cfg=args.load_old_cfg,
                          dut2=args.dut2,
                          dut5=args.dut5,
                          dut6=args.dut6,
                          raw_lines_file=args.raw_lines_file,
                          enables=args.enable,
                          disables=args.disable,
                          raw_lines=args.raw_line,
                          sets=args.set,
                          test_rig=args.test_rig
                          )
    CV_Test.setup()
    CV_Test.run()


if __name__ == "__main__":
    main()
