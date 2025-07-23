"""Library code for automating LANforge Chamber View tests."""
import sys
import os
import importlib
import time
import json
import logging

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
cv_test_reports = importlib.import_module("py-json.cv_test_reports")
lf_rpt = cv_test_reports.lanforge_reports
logger = logging.getLogger(__name__)


def cv_base_adjust_parser(args):
    # TODO: Can we add these options to base parser?
    if args.test_rig != "":
        # TODO:  In future, can use TestRig once that GUI update has propagated
        args.set.append(["Test Rig ID:", args.test_rig])

    if args.test_tag != "":
        args.set.append(["TestTag", args.test_tag])


def cv_add_base_parser(parser):
    """Update provided argparse argument parser with Chamber View-specific arguments."""
    parser.add_argument("-m", "--mgr",
                        dest="mgr",
                        type=str,
                        default="localhost",
                        help="Hostname or IP address of the LANforge GUI machine (localhost is default)")
    parser.add_argument("-o", "--port",
                        dest="port",
                        type=int,
                        default=8080,
                        help="IP Port the LANforge GUI is listening on (8080 is default)")
    parser.add_argument("--lf_user",
                        type=str,
                        default="lanforge",
                        help="LANforge system username used to SSH and pull reports")
    parser.add_argument("--lf_password",
                        type=str,
                        default="lanforge",
                        help="LANforge system password used to SSH in and pull reports")
    parser.add_argument("--lf_ssh_port",
                        type=int,
                        default=22,
                        help="LANforge system SSH port used to SSH in and pull reports")

    parser.add_argument("-i", "--instance_name",
                        dest="instance_name",
                        type=str,
                        default="cv_dflt_inst",
                        help="Chamber View test instance name")
    parser.add_argument("-c", "--config_name",
                        dest="config_name",
                        type=str,
                        default="cv_dflt_cfg",
                        help="Config file name")

    parser.add_argument("-r", "--pull_report",
                        dest="pull_report",
                        action='store_true',
                        help="Pull reports from LANforge system. Off by default")
    parser.add_argument("--load_old_cfg",
                        action='store_true',
                        help="Load defaults from previous run of the test")

    parser.add_argument("--enable",
                        action='append',
                        nargs=1,
                        default=[],
                        help="Specify options to enable (set config option value to 1). "
                             "Often used to enable Chamber View test sub-tests, for example "
                             "the 'Stability' test in the AP-Auto Chamber View test. "
                             "See test config for possible options. May be specified multiple times")
    parser.add_argument("--disable",
                        action='append',
                        nargs=1,
                        default=[],
                        help="Specify options to disable (set config option value to 0). "
                             "See test config for possible options. May be specified multiple times.")
    parser.add_argument("--set",
                        action='append',
                        nargs=2,
                        default=[],
                        help="Specify options to set values based on their label in the GUI. "
                             "For example, '--set \"Basic Client Connectivity\" 1' "
                             "May be specified multiple times.")
    parser.add_argument("--raw_line",
                        action='append',
                        nargs=1,
                        default=[],
                        help="Specify lines of the raw config file. "
                             "For example, '--raw_line \"test_rig: Ferndale-01-Basic\"' "
                             "See test config for possible options. "
                             "This is catch-all for any options not available to be specified elsewhere. "
                             "May be specified multiple times.")
    # TODO: Clarify which takes precedent, --raw_line or --raw_lines_file
    parser.add_argument("--raw_lines_file",
                        type=str,
                        default="",
                        help="Specify a file of raw lines to apply. "
                             "See the '--raw_line' option for more information.")

    # Reporting info
    parser.add_argument("--test_rig",
                        default="",
                        help="Specify the test rig info for reporting purposes. "
                             "For example, '--test_rig testbed-01'")
    parser.add_argument("--test_tag",
                        default="",
                        help="Specify the test tag info for reporting purposes, for instance:  testbed-01")


class cv_test(Realm):
    """Utilities for configuring LANforge Chamber View tests and Scenarios."""
    def __init__(self,
                 lfclient_host: str = "localhost",
                 lfclient_port: int = 8080,
                 lf_report_dir: str = None,
                 debug_: bool = False):
        """Create new session for configuring LANforge Chamber View tests and Scenarios."""
        super().__init__(lfclient_host=lfclient_host,
                         lfclient_port=lfclient_port,
                         debug_=debug_)
        self.lf_report_dir = lf_report_dir
        self.report_name = None

    # ~~~ Chamber View test functions ~~~
    def create_test_config(self, config_name: str, blob_test_name: str, text: str):
        """Create a new or update an existing Chamber View test configuration.

        Recommended to use the `build_cfg()` wrapper function instead, as this function
        does not ensure the config is active before returning.

        The config name and blob test name are combined to create a unique test configuration,
        referred to as a 'text blob'.
        """
        req_url = "/cli-json/add_text_blob"
        data = {
            "type": "Plugin-Settings",
            "name": str(blob_test_name + config_name),
            "text": text
        }

        logger.info("adding -:%s:- to test config: %s  blob-name: %s" % (text, config_name, blob_test_name))

        self.json_post(req_url, data)

    def create_test(self, test_name: str, instance: str, load_old_cfg: int):
        """Launch test window for specified Chamber View test (does not start the test).

        Recommended to use the `create_and_run_test()` function if creating
        new test automation, as it manages process of configuring, invoking, and running
        a Chamber View test.
        """
        cmd = "cv create '{0}' '{1}' '{2}'".format(test_name, instance, load_old_cfg)
        return self.run_cv_cmd(str(cmd))

    def load_test_scenario(self, instance: str, scenario: str):
        """Load Chamber View test config for specified test instance (active test window).

        Recommended to use `load_test_config()` instead, as the term 'scenario' here
        is overloaded with Chamber View Scenario, which is separate.

        Recommended to use the `create_and_run_test()` function if creating
        new test automation, as it manages process of configuring, invoking, and running
        a Chamber View test.
        """
        cmd = "cv load '{0}' '{1}'".format(instance, scenario)
        self.run_cv_cmd(cmd)

    def load_test_config(self, test_config: str, instance: str):
        """Load Chamber View test config for specified test instance.

        Recommended to use the `create_and_run_test()` function if creating
        new test automation, as it manages process of configuring, invoking, and running
        a Chamber View test.
        """
        cmd = "cv load '{0}' '{1}'".format(instance, test_config)
        self.run_cv_cmd(cmd)

    def start_test(self, instance: str):
        """Start the Chamber View test for specified test instance (assumes instance is active).

        Recommended to use the `create_and_run_test()` function if creating
        new test automation, as it manages process of invoking and running
        a Chamber View test."""
        cmd = "cv click '%s' Start" % instance
        return self.run_cv_cmd(cmd)

    def close_test(self, instance: str):
        """Close the Chamber View test window for specified test instance."""  # TODO: Assume it also stops the test?
        cmd = "cv click '%s' 'Close'" % instance
        self.run_cv_cmd(cmd)

    def cancel_test(self, instance: str):
        """Cancel the Chamber View test for specified test instance."""
        cmd = "cv click '%s' Cancel" % instance
        self.run_cv_cmd(cmd)

    def auto_save_report(self, instance: str):
        """Toggle Chamber View test 'Auto Save' option for specified test instance.

        Recommended to use `set_auto_save_report()` instead to avoid unexpected errors.
        If the option is presently selected, this will un-select (disable) auto save functionality.
        """
        cmd = "cv click '%s' 'Auto Save Report'" % instance
        self.run_cv_cmd(cmd)

    def set_auto_save_report(self, instance: str, onoff: int):
        """Set Chamber View test 'Auto Save' option for specified test instance.

        Specify '1' to enable the 'Auto Save' option or '0' to disable the option.
        """
        cmd = "cv set '%s' 'Auto Save Report' %s" % (instance, onoff)
        self.run_cv_cmd(cmd)

    def get_report_location(self, instance: str):
        """Query the report location for the specified Chamber View test instance."""
        cmd = "cv get '%s' 'Report Location:'" % instance
        location = self.run_cv_cmd(cmd)
        return location

    def get_is_running(self, instance: str):
        """Query test status of the specified Chamber View test instance."""
        cmd = "cv get '%s' 'StartStop'" % instance
        val = self.run_cv_cmd(cmd)
        # pprint(val)
        return val[0]["LAST"]["response"] == 'StartStop::Stop'

    def save_html(self, instance: str):
        """Save the test results for the specified Chamber View test instance.

        This assumes that the test has completed.
        """
        cmd = "cv click %s 'Save HTML'" % instance
        self.run_cv_cmd(cmd)

    def get_exists(self, instance: str):
        """Query existence of specified Chamber View test instance."""
        cmd = "cv exists %s" % instance
        val = self.run_cv_cmd(cmd)
        # pprint(val)
        return val[0]["LAST"]["response"] == 'YES'

    def get_cv_is_built(self):
        """Query status of specified Chamber View Scenario (built or not)."""
        cmd = "cv is_built"
        val = self.run_cv_cmd(cmd)
        # pprint(val)
        rv = val[0]["LAST"]["response"] == 'YES'
        logger.info("is-built: {rv} ".format(rv=rv))
        return rv

    def delete_instance(self, instance: str):
        """Delete specified Chamber View test instance."""
        cmd = "cv delete '%s'" % instance
        self.run_cv_cmd(cmd)

        # It can take a while, some test rebuild the old scenario upon exit, for instance.
        tries = 0
        while True:
            if self.get_exists(instance):
                logger.info("Waiting %i/60 for test instance: %s to be deleted." % (tries, instance))
                tries += 1
                if tries > 60:
                    break
                time.sleep(1)
            else:
                break

        # And make sure chamber-view is properly re-built
        tries = 0
        while True:
            if not self.get_cv_is_built():
                logger.info("Waiting %i/60 for Chamber-View to be built." % tries)
                tries += 1
                if tries > 60:
                    break
                time.sleep(1)
            else:
                break

    def get_ports(self, url: str = "/ports/"):
        """Query manager for port information."""
        response = self.json_get(url)
        return response

    def show_text_blob(self, config_name: str, blob_test_name: str, brief: bool):
        """Query specified Chamber View config contents.

        The config name and blob test name are combined to create a unique test configuration
        referred to as a 'text blob'.
        """
        req_url = "/cli-json/show_text_blob"
        response_json = []
        data = {"type": "Plugin-Settings"}
        if config_name and blob_test_name:
            data["name"] = "%s%s" % (blob_test_name, config_name)  # config name
        else:
            data["name"] = "ALL"
        if brief:
            data["brief"] = "brief"
        self.json_post(req_url, data, response_json_list_=response_json)
        return response_json

    def rm_text_blob(self, config_name: str, blob_test_name: str):
        """Remove specified Chamber View config.

        The config name and blob test name are combined to create a unique test configuration
        referred to as a 'text blob'.
        """
        req_url = "/cli-json/rm_text_blob"
        data = {
            "type": "Plugin-Settings",
            "name": str(blob_test_name + config_name),  # config name
        }
        self.json_post(req_url, data)

    # TODO: What does 'Network-Connectivity' denote?
    def rm_cv_text_blob(self, cv_type: str = "Network-Connectivity", name: str = None):
        """Remove specified Chamber View config.

        The config name and blob test name are combined to create a unique test configuration
        referred to as a 'text blob'.
        """
        req_url = "/cli-json/rm_text_blob"
        data = {
            "type": cv_type,
            "name": name,  # config name
        }
        self.json_post(req_url, data)

    @staticmethod
    def apply_cfg_options(cfg_options: list, enables: list, disables: list, raw_lines: list, raw_lines_file: str):
        """Update specified config options list with provided configuration."""
        # Read in calibration data and whatever else.
        if raw_lines_file != "":
            # Check that file exists before attempting to open
            if not os.path.exists(raw_lines_file) or not os.path.isfile(raw_lines_file):
                logger.error(f"Could not open raw lines file \'{raw_lines_file}\'. Exiting")
                exit(1)

            with open(raw_lines_file) as fp:
                line = fp.readline()
                while line:
                    cfg_options.append(line)
                    line = fp.readline()
            fp.close()

        for en in enables:
            cfg_options.append("%s: 1" % (en[0]))

        for en in disables:
            cfg_options.append("%s: 0" % (en[0]))

        for r in raw_lines:
            cfg_options.append(r[0])

    def build_cfg(self, config_name: str, blob_test: str, cfg_options: list):
        """Apply and make active specified Chamber View test configuration.

        This function also ensures the config is active in the GUI.
        """
        for value in cfg_options:
            self.create_test_config(config_name, blob_test, value)

        # Request GUI update its text blob listing.
        self.show_text_blob(config_name, blob_test, False)

        # Hack, not certain if the above show returns before the action has been completed
        # or not, so we sleep here until we have better idea how to query if GUI knows about
        # the text blob.
        time.sleep(5)

    def create_and_run_test(self,
                            load_old_cfg: bool,
                            test_name: str,
                            instance_name: str,
                            config_name: str,
                            sets: list,
                            pull_report: bool,
                            lf_host: str,
                            lf_user: str,
                            lf_password: str,
                            cv_cmds: list,
                            local_lf_report_dir: str = None,
                            ssh_port: int = 22,
                            graph_groups_file: str = None):
        """Create and run Chamber View test with specified configuration.

            load_old_config is boolean
            test_name is specific to the type of test being launched (Dataplane, tr398, etc)
            ChamberViewFrame.java has list of supported test names.
            instance_name is per-test instance, it does not matter much, just use the same name
            throughout the entire run of the test.
            config_name what to call the text-blob that configures the test.  Does not matter much
            since we (re)create it during the run.
            sets:  Arrany of [key,value] pairs.  The key is the widget name, typically the label
            before the entry field.
            pull_report:  Boolean, should we download the report to current working directory.
            lf_host:  LANforge machine running the GUI.
            lf_password:  Password for LANforge machine running the GUI.
            cv_cmds:  Array of raw chamber-view commands, such as "cv click 'button-name'"
            These (and the sets) are applied after the test is created and before it is started.
        """
        load_old = "false"
        if load_old_cfg:
            load_old = "true"

        # 1. Attempt to create test as configured (does not start yet)
        #
        # This may fail for a number of reasons, including there
        # already being an active test instance with the same name
        #
        # Note that this logic only checks for test instance with same name.
        # It currently has no logic to detect any *other* active tests
        # with a different test instance name
        start_try = 0
        while True:
            response = self.create_test(test_name, instance_name, load_old)

            # Check response data to see if test creation was successful
            if response and len(response) > 0:
                response = response[0]
                if "LAST" in response and "response" in response["LAST"] \
                        and response["LAST"]["response"] == "OK":
                    # Successfully created test
                    break

                logger.warning(f"Create test response data not in expected format: {response}")

            # Failed to create test, try again until our try counter expires
            logger.warning(f"Could not create test, try: {start_try}/60:")

            start_try += 1
            if start_try > 60:
                logger.critical("Could not start within 60 tries, aborting.")
                exit(1)
            time.sleep(1)

        # 2. Configure test
        self.load_test_config(config_name, instance_name)
        self.set_auto_save_report(instance_name, "true")

        for kv in sets:
            cmd = "cv set '%s' '%s' '%s'" % (instance_name, kv[0], kv[1])
            self.run_cv_cmd(cmd)

        for cmd in cv_cmds:
            self.run_cv_cmd(cmd)

        # 3. Start test
        response = self.start_test(instance_name)
        if response[0]["LAST"]["response"].__contains__("Could not find instance:"):
            logger.error("ERROR:  start_test failed: ", response[0]["LAST"]["response"], "\n")
            exit(1)

        # 4. Poll test while it runs
        not_running = 0
        ok_status = 1
        while True:
            # Report and close any dialogs
            cmd = "cv get_and_close_dialog"
            dialog = self.run_cv_cmd(cmd)
            if dialog[0]["LAST"]["response"] != "NO-DIALOG":
                logger.warning(f"Popup Dialog: {dialog[0]["LAST"]["response"]}")

            # Query test status
            if ok_status:
                cmd = "cv get_status '%s'" % (instance_name)
                status = self.run_cv_cmd(cmd)
                if status[0]["LAST"]["response"] != "NO-STATUS" and status[0]["LAST"]["response"] != "NO-INSTANCE":
                    if "Unknown 1-argument cv command: cv get_status" in status[0]["LAST"]["response"]:
                        logger.info("Disabling status query, this LANforge GUI version does not support it.")
                        ok_status = 0
                    else:
                        logger.info("Status:\n")
                        logger.info(status[0]["LAST"]["response"])

            # TODO: Only need to check this once. Maybe moving this to the end of the function
            #       where we already set report location
            check = self.get_report_location(instance_name)
            location = json.dumps(check[0]["LAST"]["response"])
            if location != '\"Report Location:::\"':
                # Please Do not remove or comment out the next line of logger.info it is used
                # to find the location of the meta file used by LANforge Qualification
                logger.info(location)  # Do Not comment out or remove
                location = location.replace('\"Report Location:::', '')
                location = location.replace('\"', '')
                report = lf_rpt()
                logger.info(graph_groups_file)
                if graph_groups_file is not None:
                    filelocation = open(graph_groups_file, 'a')
                    if pull_report:
                        location2 = location.replace('/home/lanforge/html-reports/', '')
                        filelocation.write(location2 + '/kpi.csv\n')
                    else:
                        filelocation.write(location + '/kpi.csv\n')
                    filelocation.close()
                logger.info('Ready to pull report from location: %s' % (location))
                self.lf_report_dir = location
                if pull_report:
                    try:
                        logger.info("Pulling report to directory: %s from %s@%s/%s" %
                                    (local_lf_report_dir, lf_user, lf_host, location))
                        report.pull_reports(hostname=lf_host, username=lf_user, password=lf_password,
                                            port=ssh_port, report_dir=local_lf_report_dir,
                                            report_location=location)
                    except Exception as e:
                        logger.critical("SCP failed, user %s, password %s, dest %s" % (lf_user, lf_password, lf_host))
                        raise e  # Exception("Could not find Reports")
                    break
            else:
                logger.info('Waiting on test completion for kpi')

            # Stop polling CV test if it's not running after five tries
            # This includes both issues during test run (after successful creation)
            # as well as normal stop logic
            if not self.get_is_running(instance_name):
                logger.info("Detected test is not running %s / 5." % (not_running))
                not_running += 1
                if not_running > 5:
                    break

            time.sleep(1)

        # 5. Test complete, gather reports and cleanup
        #
        # This closes the test and any present pop-ups
        self.report_name = self.get_report_location(instance_name)
        self.delete_instance(instance_name)

        # Clean up any remaining popups
        while True:
            cmd = "cv get_and_close_dialog"
            dialog = self.run_cv_cmd(cmd)
            if dialog[0]["LAST"]["response"] != "NO-DIALOG":
                logger.info("Popup Dialog:\n")
                logger.info(dialog[0]["LAST"]["response"])
            else:
                break

    def kpi_results_present(self) -> bool:
        """Query whether Chamber View test KPI results are available in configured report directory."""
        kpi_csv_data_present = False
        kpi_csv = ''

        if self.local_lf_report_dir is None or self.local_lf_report_dir == "":
            logger.info("Local report directory not specified. No KPI results present.")
            return False
        else:
            kpi_location = self.local_lf_report_dir + "/" + os.path.basename(self.lf_report_dir)
            # the lf_report_dir is the parent directory,  need to get the directory name
            kpi_csv = "{kpi_location}/kpi.csv".format(kpi_location=kpi_location)

        if os.path.isfile(kpi_csv):
            kpi_size = os.path.getsize(kpi_csv)
            if kpi_size < 210:
                logger.error(f"kpi_csv file may only have column headers size: {kpi_size} file: {kpi_csv}")
            else:
                logger.info(f"kpi_csv file not empty size: {kpi_size} {kpi_csv}")
                kpi_csv_data_present = True

        return kpi_csv_data_present

    # ~~~ Chamber View Scenario functions ~~~
    def add_text_blob_line(self,
                           scenario_name: str = "Automation",
                           Resources: str = "1.1",
                           Profile: str = "STA-AC",
                           Amount: str = "1",
                           DUT: str = "DUT",
                           Dut_Radio: str = "Radio-1",
                           Uses1: str = "wiphy0",
                           Uses2: str = "AUTO",
                           Traffic: str = "http",
                           Freq: str = "-1",
                           VLAN: str = ""):
        """Create and/or add configuration to specified Chamber View config.

        See the more generalized `pass_raw_lines_to_cv()` function for more information.
        """
        req_url = "/cli-json/add_text_blob"

        text_blob = "profile_link" + " " + Resources + " " + Profile + " " + Amount + " " + "\'DUT:" + " " + DUT \
                    + " " + Dut_Radio + "\' " + Traffic + " " + Uses1 + "," + Uses2 + " " + Freq + " " + VLAN

        if self.debug:
            print("text-blob-line: %s" % (text_blob))

        data = {
            "type": "Network-Connectivity",
            "name": scenario_name,
            "text": text_blob
        }

        self.json_post(req_url, data)

    def pass_raw_lines_to_cv(self,
                             scenario_name: str = "Automation",
                             Rawline: str = ""):
        """Create and/or add configuration to specified Chamber View Test or Scenario config.

        Each configurable in a Chamber View test corresponds to a key-value pair.
        When saved to a config (text blob), each of these pairs is referred to as a 'rawline'.

        This function is generally utilized to set options for automated Chamber View tests
        but can be used to configure Chamber View Scenarios. It is recommended to start with
        a dedicated Chamber View test script if you're integrating this into your own automation.
        """
        req_url = "/cli-json/add_text_blob"
        data = {
            "type": "Network-Connectivity",
            "name": scenario_name,
            "text": Rawline
        }
        self.json_post(req_url, data)

    def apply_cv_scenario(self, cv_scenario: str):
        """Stage specified Chamber View Scenario for configuration in testbed.

        Assumes Chamber View Scenario already exists. After applying the scenario,
        one must build the scenario to make the configuration active on the system
        (see `build_cv_scenario()`).

        While Chamber View tests may rely on existing Chamber View Scenarios,
        they are unique and rely on separate configuration for use in LANforge.
        """
        cmd = "cv apply '%s'" % cv_scenario
        self.run_cv_cmd(cmd)
        logger.info("Applying %s scenario" % cv_scenario)

    def build_cv_scenario(self):
        """Make staged Chamber View Scenario active in testbed.

        Assumes scenario exists and is already staged (see `apply_cv_scenario()`).
        Status of scenario can be queried with `get_cv_build_status()`.

        While Chamber View tests may rely on existing Chamber View Scenarios,
        they are unique and rely on separate configuration for use in LANforge.
        """
        cmd = "cv build"
        self.run_cv_cmd(cmd)
        logger.info("Building scenario")

    def get_cv_build_status(self):
        """Query whether Chamber View Scenario is active (built) in testbed.

        While Chamber View tests may rely on existing Chamber View Scenarios,
        they are unique and rely on separate configuration for use in LANforge.
        """
        cmd = "cv is_built"
        response = self.run_cv_cmd(cmd)
        return self.check_reponse(response)

    def sync_cv(self):
        """Request GUI update Chamber View with configuration active in system.

        This is generally not necessary if building a new scenario in automation.

        While Chamber View tests may rely on existing Chamber View Scenarios,
        they are unique and rely on separate configuration for use in LANforge.
        """
        cmd = "cv sync"
        logger.info(self.run_cv_cmd(cmd))

    # ~~~ Chamber View command helpers ~~~
    @staticmethod
    def get_response_string(response: list):
        """Extract response string from specified message."""
        return response[0]["LAST"]["response"]

    def run_cv_cmd(self, command: str):
        """Send LANforge Chamber View command to GUI.

        Aside from special cases, this is generally not to be used directly.
        """
        logger.debug(f"Running CV command: {command}")

        response_json = []
        self.json_post("/gui-json/cmd",
                       {"cmd": command},
                       debug_=False,
                       response_json_list_=response_json)

        logger.debug(f"CV command response: {command}")
        return response_json

    def get_popup_info_and_close(self):
        """Grab info from and close any pop-up dialog box in Chamber View."""
        cmd = "cv get_and_close_dialog"
        dialog = self.run_cv_cmd(cmd)
        if dialog[0]["LAST"]["response"] != "NO-DIALOG":
            logger.info("Popup Dialog:\n")
            logger.info(dialog[0]["LAST"]["response"])
