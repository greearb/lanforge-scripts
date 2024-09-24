# LANforge Perl, Python, and Shell Scripts

**This repository contains a collection of scripts and Python and Perl-based scripting libraries designed to automate LANforge systems.**

## Overview
These scripts span a variety of use cases, including automating Chamber View tests, configuring LANforge ports and traffic pairs, and much more.

**No additional setup is required to run these scripts on a system with LANforge pre-installed**. On your LANforge system, you can find this repository in the `/home/lanforge/scripts/` directory. (e.g. CT523c, CT521b). The contents of the directory match the version of LANforge installed on your system (see the [tagged releases](https://github.com/greearb/lanforge-scripts/tags) to clone specific version.)

To setup and use these scripts on a non-LANforge system or to use a specific version (e.g. specific LANforge release), please follow the instructions outlined in the [LANforge Python Scripts README](./py-scripts/README.md).

For more advanced users wanting to develop their own automation, we offer the following:
- Auto-generated Python library in [`lanforge_client/`](./lanforge_client/)
  - **NOTE: This library is under development and subject to change as it progresses.**
  - Designed to make LANforge CLI commands and LANforge JSON API endpoints available in Python.
  - See the [`README`](./lanforge_client/README.md) for more details.
- Perl modules in [`LANforge/`](./LANforge/)
  - See the [`README`](./LANforge/README.md) for more details.

## Quick Tips

### Documentation Links

- [LANforge CLI Users Guide](https://www.candelatech.com/lfcli_ug.php)
- [LANforge Scripting Cookbook](http://www.candelatech.com/scripting_cookbook.php)
- [Querying the LANforge JSON API using Python Cookbook](https://www.candelatech.com/cookbook/cli/json-python)

### Commonly Used Scripts
The `lf_*.pl` scripts are typically more complete and general purpose
scripts, though some are ancient and very specific.

In particular, these scripts are more modern and may be a good place to start:

| Name             | Purpose   |
|------------------|-----------|
| `lf_associate_ap.pl`    | LANforge server script for associating virtual stations to an arbitrary SSID |
| `lf_attenmod.pl`        | Query and update CT70X programmable attenuators |
| `lf_firemod.pl`         | Query and update connections (Layer 3) |
| `lf_icemod.pl`          | Query and update WAN links and impairments |
| `lf_portmod.pl`         | Query and update physical and virtual ports |
| `lf_tos_test.py`        | Generate traffic at different QoS and report in spreadsheet |
| `lf_sniff.py`           | Create packet capture files, especially OFDMA /AX captures |

The `lf_wifi_rest_example.pl` script shows how one might call the other scripts from
within a script.

### Exploring LANforge JSON API/Crafting CLI Commands

When the LANforge GUI is running, a user can use the web-based LANforge Command Composer tool to generate CLI commands, either for use directly through the telnet interface (port 4001) or indirectly through the `cli-json/` LANFORGE JSON API endpoint.

To access this tool, perform the following steps:
1. Navigate to the Help page (either from the LANforge or remotely)
    - From the LANforge system (e.g. through VNC): [`http://localhost:8080/help`](http://localhost:8080/help)
    - Remotely:
      - Directly by IP address: `http://192.168.1.101:8080/help`
      - If your network supports DNS resolution: `http://ct523c-cafe:8080/help`

2. Click on the link for your desired command, e.g. `add_sta`
    - Each CLI command will display two links. The link *on the left side* takes you to the Command Composer tool

3. Set the desired fields for the command

4. Click the `Parse Command` at the top
   - This generates CLI output for the fields you configured at the top of the webpage
   - Generated output includes:
     - CLI command for use in the telnet interface
     - Commands to manually send data to the `cli-json/` LANFORGE JSON API endpoint

More information on other LANforge JSON API endpoints can be by navigating to the main (root) endpoint `http://localhost:8080/` or querying it through `curl` (very verbose, e.g. `curl http://localhost:8080 | jq`).

## Python Scripts

**NOTE: LANforge Python scripts require Python 3.7+** (which is backwards compatible to Fedora 27 systems).

See the [LANforge Python Scripts README](./py-scripts/README.md) for more information, including setup for use on non-LANforge systems.


### Python Scripts in `py-scripts/`

Test scripts and helper scripts written in Python.

Helper scripts, especially creation and modification scripts, are designed in a "toolbox" approach. Each "toolbox" script performs a single task, like a tool in the toolbox. For example, the [`create_station.py`](./py-scripts/create_station.py) is designed to create and configure LANforge station ports, with many options for that specific use case.

| Name | Purpose |
|------|---------|
| `create_bond.py`                   | This script can be used to create a bond |
| `create_bridge.py`                 | Script for creating a variable number of bridges |
| `create_chamberview.py`            | Script for creating a chamberview scenario |
| `create_l3.py`                     | This script will create a variable number of layer3 stations each with their own set of cross-connects and endpoints |
| `create_l4.py`                     | This script will create a variable number of layer4 stations each with their own set of cross-connects and endpoints |
| `create_macvlan.py`                | Script for creating a variable number of macvlans |
| `create_qvlan.py`                  | Script for creating a variable number of qvlans |
| `create_station.py`                | Script for creating a variable number of stations |
| `create_station_from_df.py`        | Script for creating a variable number of stations from a file |
| `create_vap.py`                    | Script for creating a variable number of VAPs |
| `create_vr.py`                     | Script for creating a variable number of bridges |
| `csv_convert.py`                   | Python script to read in a LANforge Dataplane CSV file and output a csv file that works with a customer's RvRvO visualization tool.|
| `csv_processor.py`                 | Python script to assist processing csv files|
| `download_test.py`                 | download_test.py will do lf_report::add_kpi(tags, 'throughput-download-bps', $my_value);|
| `event_breaker.py`                 | This file is intended to expose concurrency problems in the /events/ URL handler by querying events rapidly. Please use concurrently with event_flood.py. |
| `event_flood.py`                   | This file is intended to expose concurrency problems in the /events/ URL handler by inserting events rapidly. Please concurrently use with event_breaker.py.|
| `lf_ap_auto_test.py`               | This script is used to automate running AP-Auto tests |
| `lf_dataplane_test.py`             | This script is used to automate running Dataplane tests |
| `lf_ftp_test.py`                   | Python script will create stations and endpoints to generate and verify layer-4 traffic over an ftp connection |
| `lf_graph.py`                      | Classes for creating images from graphs using data sets |
| `lf_mesh_test.py`                  | This script is used to automate running Mesh tests |
| `lf_report.py`                     | This program is a helper  class for reporting results for a lanforge python script |
| `lf_report_test.py`                | Python script to test reporting |
| `lf_rvr_test.py`                   | This script is used to automate running Rate-vs-Range tests |
| `lf_snp_test.py`                   | Test scaling and performance (snp) run various configurations and measures data rates |
| `lf_tr398_test.py`                 | This script is used to automate running TR398 tests |
| `lf_wifi_capacity_test.py`         | This is a test file which will run a wifi capacity test |
| `run_cv_scenario.py`               | Set the LANforge to a BLANK database then it will load the specified database and start a graphical report |
| `rvr_scenario.py`                  | This script will set the LANforge to a BLANK database then it will load the specified database and start a graphical report |
| `scenario.py`                      | Python script to load a database file and control test groups |
| `sta_connect.py`                   | Create a station, run TCP and UDP traffic then verify traffic was received. Stations are cleaned up afterwards |
| `sta_connect2.py`                  | Create a station, run TCP and UDP traffic then verify traffic was received. Stations are cleaned up afterwards |
| `sta_connect_example.py`           | Example of how to instantiate StaConnect and run the test |
| `sta_connect_multi_example.py`     | Example of how to instantiate StaConnect and run the test |
| `station_layer3.py`                | this script creates one station with given arguments |
| `stations_connected.py`            | Contains examples of using realm to query stations and get specific information from them |
| `test_client_admission.py`         | This script will create one station at a time and generate downstream traffic |
| `test_fileio.py`                   | Test FileIO traffic |
| `test_generic.py`                  | Test generic traffic using generic cross-connect and endpoint type |
| `test_ipv4_connection.py`          | Test connections to a VAP of varying security types (WEP, WPA, WPA2, WPA3, Open) |
| `test_ipv4_l4.py`                  | Test layer 4 traffic using layer 4 cross-connect and endpoint type |
| `test_ipv4_l4_ftp_upload.py`       | Test ftp upload traffic |
| `test_ipv4_l4_ftp_urls_per_ten.py` | Test the number of urls per ten minutes in ftp traffic |
| `test_ipv4_l4_ftp_wifi.py`         | Test ftp upload traffic wifi-wifi |
| `test_ipv4_l4_urls_per_ten.py`     | Test urls per ten minutes in layer 4 traffic |
| `test_ipv4_l4_wifi.py`             | Test layer 4 upload traffic wifi-wifi|
| `test_ipv4_ttls.py`                | Test connection to ttls system |
| `test_ipv4_variable_time.py`       | Test connection and traffic on VAPs of varying security types (WEP, WPA, WPA2, WPA3, Open) |
| `test_ipv6_connection.py`          | Test IPV6 connection to VAPs of varying security types (WEP, WPA, WPA2, WPA3, Open) |
| `test_ipv6_variable_time.py`       | Test IPV6 connection and traffic on VAPs of varying security types (WEP, WPA, WPA2, WPA3, Open) |
| `test_l3_WAN_LAN.py`               | Test traffic over a bridged NAT connection |
| `test_l3_longevity.py`             | Create variable stations on multiple radios, configurable rates, PDU, ToS, TCP and/or UDP traffic, upload and download, attenuation |
| `test_l3_powersave_traffic.py`     | Python script to test for layer 3 powersave traffic |
| `test_l3_scenario_throughput.py`   | Load an existing scenario and run the simultaneous throughput over time and generate report and P=plot the G=graph|
| `test_l3_unicast_traffic_gen.py`   | Generate unicast traffic over a list of stations|
| `test_status_msg.py`               | Test the status message passing functions of /status-msg |
| `test_wanlink.py`                  | Python script to test wanlink creation |
| `test_wpa_passphrases.py`          | Python script to test challenging wpa psk passphrases |
| `testgroup.py`                     | Python script to test creation and control of test groups |
| `testgroup2.py`                    | Python script to test creation and control of test groups |
| `tip_station_powersave.py`         | Generate and test for powersave packets within traffic run over multiple stations |
| `update_dependencies.py`           | Python script to update dependencies for various Candelatech python scripts |
| `wlan_capacity_calculator.py`      | Standard Script for WLAN Capacity Calculator |
| `ws_generic_monitor_test.py`       | This example is to demonstrate ws_generic_monitor to monitor events triggered by scripts, This script when running, will monitor the events triggered by test_ipv4_connection.py |

## Perl and Shell Scripts ##

| Name | Purpose |
|------|---------|
| `associate_loop.sh`              | Use this script to associate stations between SSIDs A and B |
| `attenuator_series_example.csv`  | Example of CSV input for a series of attenuator settings |
| `attenuator_series.pl`           | Reads a CSV of attenuator settings and replays them to CT70X programmble attenuator |
| `ftp-upload.pl`                  | Use this script to collect and upload station data to FTP site |
| `imix.pl`                        | packet loss survey tool |
| `lf_associate_ap.pl`             | LANforge server script for associating virtual stations to an chosen SSID |
| `lf_attenmod.pl`                 | This program is used to modify the LANforge attenuator through the LANforge |
| `lf_auto_wifi_cap.pl`            | This program is used to automatically run LANforge-GUI WiFi Capacity tests |
| `lf_cmc_macvlan.pl`              | Stress test sets up traffic types of udp , tcp , continuously starts and stops the connections  |
| `lf_create_bcast.pl`             | creates a L3 broadcast connection |
| `lf_cycle_wanlinks.pl`           | example of how to call lf_icemod.pl from a script |
| `lf_endp_script.pl`              | create a hunt script on a L3 connection endpoint |
| `lf_firemod.pl`                  | queries and modifies L3 connections |
| `lf_generic_ping.pl`             | Generate a batch of Generic lfping endpoints |
| `lf_gui_cmd.pl`                  | Initiate a stress test  |
| `lf_icemod.pl`                   | queries and modified WANLink connections |
| `lf_ice.pl`                      | adds and configures wanlinks |
| `lf_l4_auth.pl`                  | example of scripting L4 http script with basic auth |
| `lf_l4_reset.sh`                 | reset any layer 4 connection that reaches 0 Mbps over last minute |
| `lf_log_parse.pl`                | Convert the timestamp in LANforge logs (it is in unix-time, miliseconds) to readable date |
| `lf_loop_traffic.sh`             | Repeatedly start and stop a L3 connection |
| `lf_macvlan_l4.pl`               | Set up connection types: lf_udp, lf_tcp across 1 real port and many macvlan ports on 2 machines. Then continously starts and stops the connections. |
| `lf_mcast.bash`                  | Create a multicast L3 connection endpoint |
| `lf_monitor.pl`                  | Monitor L4 connections |
| `lf_nfs_io.pl`                   | Creates and runs NFS connections |
| `lf_parse_tshark_log.pl`         | Basic parsing of tshark logs |
| `lf_portmod.pl`                  | Queries and changes LANforge physical and virtual ports |
| `lf_port_walk.pl`                | Creates a series of connections, useful for basic firewall testing |
| `lf_show_events.pl`              | Displays and clears LANforge event log |
| `lf_staggered_dl.sh`             | his script starts a series of Layer-3 connections across a series of stations each station will wait $nap seconds, download $quantity KB and then remove its old CX. |
| `lf_sta_name.pl`                 | Use this script to alter a virtual station names |
| `lf_verify.pl`                   | Creates a basic L3 connection to verify that two ethernet ports are physically connected |
| `lf_voip.pl`                     | Creates series of VOIP connections between two LANforge machines |
| `lf_voip_test.pl`                | Creates series of VOIP connections and runs them |
| `lf_vue_mod.sh`                  | Bash script that wraps common operations for Virtual User Endpoint operations done by `lf_associate_ap` |
| `lf_wifi_rest_example.pl`        | Example script that queries a LF GUI for JSON data and displays a slice of it |
| `lf_zlt_binary.pl`               | Configures a Zero Loss Throughput test |
| `list_phy_sta.sh`                | Lists virtual stations backed by specified physical radio |
| `min_max_ave_station.pl`         | This script looks for min-max-average bps for rx-rate in a station csv data file |
| `multi_routers.pl`               | Routing cleanup script that can be used with virtual routers |
| `print_udev.sh`                  | Prints out Linux Udev rules describing how to name ports by MAC address |
| `sensorz.pl`                     | Displays temperature readings for CPU and ATH10K radios |
| `show-port-from-json.pl`         | Example script showing how to display a slice from a JSON GUI response |
| `station-toggle.sh`              | Use this script to toggle a set of stations on or off |
| `sysmon.sh`                      | grabs netdev stats and timestamp every second or so, saves to logfile.  |
| `test_refcnt.pl`                 | creates MAC-VLANs and curl requests for each |
| `topmon.sh`                      | LANforge system monitor that can be used from cron |
| `wait_on_ports.pl`               | waits on ports to have IP addresses, can up/down port to stimulate new DHCP lease |
| `wifi-roaming-times.pl`          | parses `wpa_supplicant_log.wiphyX` file to determine roaming times |

## Compatibility

Scripts will be kept backwards and forwards compatible with LANforge
releases as much as possible.

## Installation

These scripts call each other and rely on the structure of this directory. To use these scripts in other locations,
such as your laptop, either copy the entire scripts directory or do a `git clone` of this repository. Just copying
one script to a separate directory will likely break its requirements.

See the setup steps outlined in the `py-scripts/` README [here](./py-scripts/README.md) for more information, including configuring a specific version of LANforge scripts.

## Requirements

**NOTE:** Pre-installed LANforge systems generally do not require additional setup, save for specific advanced use cases.

LANforge Perl automation requirements are outlined below. See the `py-scripts/` README [here](./py-scripts/README.md) for information on LANforge Python automation requirements.

To use LANforge Perl automation, the system which will run the scripts must have the following packages installed. On Linux systems, most of these packages are available through your system's package manager as `.deb` or `.rpm` packages.

Please contact support@candelatech.com if you have any questions.

| Package            | RPM                | Required       |
| -------------------|--------------------|----------------|
| Net::Telnet        | perl-Net-Telnet    | Yes            |
| JSON               | perl-JSON          | Yes, for JSON parsing |
| JSON::PrettyPrint  | perl-JSON-PP       | No, but useful for debugging |
| Pexpect            | python3-pexpect    | Yes |
| XlsxWriter         | python3-xlsxwriter | Yes, for Xlsx output |

## License

Code in this repository is released under the BSD license (see license.txt).

## Support/Contact Info

Please contact support@candelatech.com if you have any questions.

_Thanks,
Ben_
