# LANforge Perl, Python, and Shell Scripts

## Overview

**This repository contains a collection of scripts and Python and Perl-based scripting libraries designed to automate LANforge systems.**

These scripts span a variety of use cases, including automating Chamber View tests, configuring LANforge ports and traffic pairs, and much more.
Scripts will be kept backwards and forwards compatible with LANforge releases as much as possible.

**No additional setup is required to run these scripts on a system with LANforge pre-installed**. On your LANforge system, you can find this repository in the
`/home/lanforge/scripts/` directory. The contents of the directory match the version of LANforge installed on your system (see the
[tagged releases](https://github.com/greearb/lanforge-scripts/tags) for tagged versions of scripts/automation).

As currently implemented, scripts in this repository require the directory structure as present. Many scripts import from and call into each other (primarily Python),
so modifying script location will likely break script assumptions. Things that may break assumptions and prevent script usage include moving the script to another directory.

Please contact [`support@candelatech.com`](mailto:support@candelatech.com) if you have any questions or encounter issues.

## Contents

- [Overview](#overview)
- [Contents](#contents)
- [Setup and Installation](#setup-and-installation)
  - [Installing from Source Prerequisites](#installing-from-source-prerequisites)
  - [Installing from Source Setup](#installing-from-source-setup)
  - [Installing from Source Perl Scripts/Automation Setup](#installing-from-source-perl-scriptsautomation-setup)
- [Advanced Usage/Library-style Code](#advanced-usage-library-style-code)
- [Quick Tips](#quick-tips)
  - [Documentation Links](#documentation-links)
  - [Basic Terminology](#basic-terminology)
- [Scripts/Automation by Type](#scriptsautomation-by-type)
  - [Creation/Configuration Scripts](#creationconfiguration-scripts)
  - [Chamber View Scripts](#chamber-view-scripts)
  - [Test Scripts](#test-scripts)
  - [Utility Scripts](#utility-scripts)
  - [Library Code Scripts](#library-code-scripts) (Not suggested)
  - [Unsorted or Older Scripts](#unsorted-or-older-scripts)
- [Exploring LANforge HTTP API/Crafting CLI Commands](#exploring-lanforge-http-apicrafting-cli-commands)
- [Configure Non-Root Serial Access](#configure-non-root-serial-access)
- [License](#license)

## Setup and Installation

There are two primary methods to use LANforge scripts:

1. Using the version available on your pre-installed LANforge system (**no setup required**)

   On pre-installed LANforge systems, LANforge scripts are installed in `/home/lanforge/scripts/py-scripts/`. No setup is required
   (dependencies come pre-installed), as this is done for you during install/upgrades.

   Pre-installed scripts in `/home/lanforge/scripts/py-scripts/` match the LANforge software version already installed on the system.

2. By installing from the Git repository (repository [here](https://github.com/greearb/lanforge-scripts))

   Installation from source is generally required for users looking to configure LANforge automation on a system where LANforge isn't pre-installed,
   install a specific version, or more advanced use cases, installation/setup is required.

   Instructions for this are detailed in [this section](#installing-from-source).

### Installing from Source

#### Installing from Source Prerequisites

For users who clone or download these scripts from the Git repo, some setup is required. This process is generally for more advanced users or developers.
However, if you have questions, please email [`support@candelatech.com`](mailto:support@candelatech.com), and we can guide you through.

Please ensure the following criteria are met before installing LANforge scripts (installation steps [here](#installing-from-source-setup)):

1. Familiarity with the command line (e.g. `bash`)

   - Installation will require running commands, most likely on a Linux system

2. Python 3.7+ and Git installed on system

   - **LANforge Python automation requires Python 3.7+**. Most systems and Linux distributions should have a newer version available for install.
     However, Python 3.7 continues to be our minimum supported version to ensure backwards compatibility with older LANforge systems.

   - How this is completed will depend on the system used. Generally, we encourage installing Python and Git through the
     system (e.g. `apt` on Ubuntu) and installing Python libraries/dependencies in a virtual environment (detailed in instructions)

3. Known target LANforge software version

   - **We strongly encourage matching the version of LANforge scripts to the version installed on your LANforge**, unless there is a specific need
   (e.g. new feature or bug fix). While not recommended, it is possible to use the latest version as well.

#### Installing from Source Setup

**NOTE:** Developers and anyone looking to contribute to LANforge scripts should also familiarize themselves with the information outlined
in the [`CONBTRIBUTING.md` document](../CONTRIBUTING.md).

**NOTE:** **For usage directly on a LANforge system, these steps are not necessary**, as the scripts/automation are already fully installed in
`/home/lanforge/scripts/` and match the version of LANforge already installed on the system.

This section details how to setup LANforge scripts/automation using a specific version (e.g. 5.4.9). To use Perl-based scripts/automation,
please complete the below instructions then proceed to [this section](#installing-from-source-perl-scriptsautomation-setup).

1. Open a shell and clone LANforge scripts

   ```Bash
   git clone https://github.com/greearb/lanforge-scripts
   ```

2. Get the version-tagged commits of the repository

   ```Bash
   git fetch --tags
   ```

3. List the version-tagged commits available

   ```Bash
   git tag
   ```

4. Select the matching tag for your LANforge system's version

   ```Bash
   # Checkout LANforge 5.4.9 version of LANforge scripts.
   git checkout lf-5.4.9
   ```

5. Create and source a Python virtual environment (optional but **strongly suggested**)

   We suggest Python's [builtin virtual environment tool](https://docs.python.org/3/tutorial/venv.html) for simplicity, although other
   tools requiring more configuration like [Anaconda](https://anaconda.org/) will work as well.

   ```Bash
   # Create Python virtual environment named 'venv'
   virtualenv venv

   # Enter the Python virtual environment (Linux)
   source venv/bin/activate
   ```

6. Enter the `lanforge-scripts/py-scripts/` directory

7. Run the dependency installation script

   ```Bash
   # This step may take a moment to complete
   ./update_dependencies.py
   ```

Once you have successfully completed these steps, you can now use the LANforge Python scripts.
To use Perl scripts/automation, please proceed to [this section](#installing-from-source-perl-scriptsautomation-setup)

#### Installing from Source Perl Scripts/Automation Setup

To use LANforge Perl automation, the system which will run the scripts must have the following packages installed. On Linux systems, most of these packages are available through your system's package manager as `.deb` or `.rpm` packages.

| Package           | RPM                | Required                     |
| ----------------- | ------------------ | ---------------------------- |
| Net::Telnet       | perl-Net-Telnet    | Yes                          |
| JSON              | perl-JSON          | Yes, for JSON parsing        |
| JSON::PrettyPrint | perl-JSON-PP       | No, but useful for debugging |
| Pexpect           | python3-pexpect    | Yes                          |
| XlsxWriter        | python3-xlsxwriter | Yes, for Xlsx output         |

## Advanced Usage, Library-style Code

For more advanced users wanting to develop their own automation, we offer the following:

- Auto-generated Python library in [`lanforge_client/`](./lanforge_client/)
  - **NOTE: This library is under development and subject to change as it progresses.**
  - Designed to make LANforge CLI commands and LANforge JSON API endpoints available in Python.
  - See the [`README`](./lanforge_client/README.md) for more details.
- Perl modules in [`LANforge/`](./LANforge/)
  - See the [`README`](./LANforge/README.md) for more details.

If you would like to contribute to LANforge scripts, please read the [`CONTRIBUTING.md`](./CONTRIBUTING.md) document for more information.

## Quick Tips

### Documentation Links

- [Python Automation Setup](./py-scripts/README.md) (requires Python 3.7+, which is backwards compatible to Fedora 27 systems)
- [LANforge CLI Users Guide](https://www.candelatech.com/lfcli_ug.php)
- [LANforge Scripting Cookbook](http://www.candelatech.com/scripting_cookbook.php)
- [Querying the LANforge JSON API using Python Cookbook](https://www.candelatech.com/cookbook/cli/json-python)

### Basic Terminology

| Name                 | Definition                                                                                                                                                              |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Port                 | Network interface (station, 802.1Q VLAN, Ethernet), WiFi radio, etc.                                                                                                    |
| Resource             | LANforge system ID. For example, a two LANforge system testbed would have two LANforge resources.                                                                       |
| Shelf                | Now unused identifier for a set of LANforge resources. Generally can be omitted for automation purposes (e.g. '1.1.wlan0' same as '1.wlan0')                            |
| EID                  | Entity identifier. Uniquely identifies LANforge object with meaning depending on context (e.g. in 'Port Mgr' tab, EID identifies a port)                                |
| Port EID             | Comes in format shelf, resource, port number/name, e.g. '1.1.wiphy0'. For automation pourposes, shelf and even resource may be omitted. Assumed to be '1' in that case. |
| STA, Station, Client | Interchangable terms used to refer to a WiFi device (emulated or real)                                                                                                  |

## Scripts/Automation by Type

LANforge scripts and automation offerings vary widely, including test scripts, "toolbox" scripts (i.e. perform one task like creating stations), library code which may be imported by other scripts, and utility scripts. Given the large number of available scripts and automation, the following sections aim to guide a user to their desired script/automation based on their needs.

For Python scripts in `py-scripts/`, run the script with the `--help_summary` option to list a summary of script functionality and purpose.
Generally, Python scripts support a `--help` option which prints all arguments supported by a given script.

Should a script or automation not exist for your needs, please reach out to [`support@candelatech.com`](mailto:support@candelatech.com) detailing general requirements for your desired use case.

### Creation/Configuration Scripts

These are generally single-use scripts aimed at creating and configuring LANforge items like stations, traffic pairs, and more.

| Name                                                  | Purpose                                                                                                              |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| [`lf_attenmod.pl`](./lf_attenmod.pl)                  | This program is used to modify the LANforge attenuator through the LANforge                                          |
| [`create_bond.py`](./py-scripts/create_bond.py)       | Create and configure a single Bond port using a variable number of child ports                                       |
| [`create_bridge.py`](./py-scripts/create_bridge.py)   | Create and configure a single Bridge port using a variable number of child ports                                     |
| [`create_l3.py`](./py-scripts/create_l3.py)           | Create and configure a variable number of LANforge L3 CX traffic pairs using existing ports                          |
| [`create_l4.py`](./py-scripts/create_l4.py)           | Create and configure a variable number of LANforge L4 traffic endpoints using existing ports                         |
| [`create_macvlan.py`](./py-scripts/create_macvlan.py) | Create and configure a variable number of MACVLAN ports (different from 802.1Q VLAN) using a single parent interface |
| [`create_qvlan.py`](./py-scripts/create_qvlan.py)     | Create and configure a variable number of 802.1Q VLAN ports using a single parent interface                          |
| [`create_station.py`](./py-scripts/create_station.py) | Create and configure a variable number of WiFi stations using a single parent radio                                  |
| [`create_vap.py`](./py-scripts/create_vap.py)         | Create and configure a variable number of WiFi virtual APs (vAPs) using a single parent radio                        |
| [`lf_firemod.pl`](./lf_firemod.pl)                    | Queries and modifies L3 connections                                                                                  |
| [`lf_icemod.pl`](./lf_icemod.pl)                      | Queries and modifies WANLink connections                                                                             |
| [`lf_ice.pl`](./lf_ice.pl)                            | Creates and configures wanlinks                                                                                      |
| [`lf_portmod.pl`](./lf_portmod.pl)                    | Queries and changes LANforge physical and virtual ports                                                              |

### Chamber View Scripts

Automation for LANforge GUI test automation available in the 'Chamber View' window.

See the documentation [here](./py-scripts/cv_examples/) for more information on Chamber View test overview, configuration, and automation examples.

| Name                                                                                | Purpose                                                                                                                                    |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| [`create_chamberview_dut.py`](./py-scripts/create_chamberview_dut.py)               | Create a single LANforge Chamber View DUT object, primarily useful in Chamber View tests                                                   |
| [`create_chamberview.py`](./py-scripts/create_chamberview.py)                       | Create a single LANforge Chamber View Scenario, useful for larger-scale test configuration where manual configuration would become tedious |
| [`lf_ap_auto_test.py`](./py-scripts/lf_ap_auto_test.py)                             | Automate the AP-Auto Chamber View test                                                                                                     |
| [`lf_continuous_throughput_test.py`](./py-scripts/lf_continuous_throughput_test.py) | Automate the Continuous Throughput Chamber View test                                                                                       |
| [`lf_dataplane_test.py`](./py-scripts/lf_dataplane_test.py)                         | Automate the Dataplane Chamber View test                                                                                                   |
| [`lf_mesh_test.py`](./py-scripts/lf_mesh_test.py)                                   | Automate the Mesh Chamber View test                                                                                                        |
| [`lf_rvr_test.py`](./py-scripts/lf_rvr_test.py)                                     | Automate the Rate-vs-Range Chamber View test                                                                                               |
| [`lf_tr398_test.py`](./py-scripts/lf_tr398_test.py)                                 | Automate the TR398 Issue 1 Chamber View test                                                                                               |
| [`lf_tr398v2_test.py`](./py-scripts/lf_tr398v2_test.py)                             | Automate the TR398 Issue 2 Chamber View test                                                                                               |
| [`lf_tr398v4_test.py`](./py-scripts/lf_tr398v4_test.py)                             | Automate the TR398 Issue 4 Chamber View test                                                                                               |
| [`lf_wifi_capacity_test.py`](./py-scripts/lf_wifi_capacity_test.py)                 | Automate the WiFi Capacity Chamber View test                                                                                               |
| [`run_cv_scenario.py`](./py-scripts/run_cv_scenario.py)                             | Configure a LANforge                                                                                                                       |

### Test Scripts

General test scripts for automating LANforge tests (see [this section](#chamber-view-scripts) for scripts which automate Chamber View tests).

| Name                                                                            | Purpose                                                                                                                             |
| ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| [`lf_ftp_test.py`](./py-scripts/lf_ftp.py)                                      | Python script will create stations and endpoints to generate and verify layer-4 traffic over an ftp connection                      |
| [`lf_snp_test.py`](./py-scripts/lf_snp_test.py)                                 | Test scaling and performance (snp) run various configurations and measures data rates                                               |
| [`sta_connect.py`](./py-scripts/sta_connect.py)                                 | Create a station, run TCP and UDP traffic then verify traffic was received. Stations are cleaned up afterwards                      |
| [`sta_connect2.py`](./py-scripts/sta_connect2.py)                               | Create a station, run TCP and UDP traffic then verify traffic was received. Stations are cleaned up afterwards                      |
| [`test_fileio.py`](./py-scripts/test_fileio.py)                                 | Test FileIO traffic                                                                                                                 |
| [`test_generic.py`](./py-scripts/test_generic.py)                               | Test generic traffic using generic cross-connect and endpoint type                                                                  |
| [`test_l3_WAN_LAN.py`](./py-scripts/test_l3_WAN_LAN.py)                         | Test traffic over a bridged NAT connection                                                                                          |
| [`test_l3_longevity.py`](./py-scripts/test_l3_longevity.py)                     | Create variable stations on multiple radios, configurable rates, PDU, ToS, TCP and/or UDP traffic, upload and download, attenuation |
| [`test_l3_powersave_traffic.py`](./py-scripts/test_l3_powersave_traffic.py)     | Python script to test for layer 3 powersave traffic                                                                                 |
| [`test_l3_unicast_traffic_gen.py`](./py-scripts/test_l3_unicast_traffic_gen.py) | Generate unicast traffic over a list of stations                                                                                    |
| [`tip_station_powersave.py`](./py-scripts/tip_station_powersave.py)             | Generate and test for powersave packets within traffic run over multiple stations                                                   |
| [`wlan_capacity_calculator.py`](./py-scripts/wlan_capacity_calculator.py)       | Standard Script for WLAN Capacity Calculator                                                                                        |

### Utility Scripts

Scripts/automation to perform small tasks on the system but not run tests or configure ports for test usage.

| Name                                                            | Purpose                                                                                                                                                 |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`check_large_files.sh`](./check_large_files.bash)              | Utility script to increase available disk space by removing old kernels, logs, etc. as prompted                                                         |
| [`csv_convert.py`](./py-scripts/csv_convert.py)                 | Python script to read in a LANforge Dataplane CSV file and output a csv file that works with a customer's RvRvO visualization tool.                     |
| [`csv_processor.py`](./py-scripts/csv_processor.py)             | Python script to assist processing csv files                                                                                                            |
| [`lf_log_parse.pl`](./lf_log_parse.pl)                          | Convert the timestamp in LANforge logs (it is in unix-time, miliseconds) to readable date                                                               |
| [`lf_monitor.pl`](./lf_monitor.pl)                              | Monitor L4 connections                                                                                                                                  |
| [`lf_parse_tshark_log.pl`](./lf_parse_tshark_log.pl)            | Basic parsing of tshark logs                                                                                                                            |
| [`print_udev.sh`](./print_udev.sh)                              | Prints out Linux `udev` rules describing how to name ports by MAC address                                                                               |
| [`sensorz.pl`](./sensorz.pl)                                    | Displays temperature readings for CPU, mt7915 radios, ath10k radios                                                                                     |
| [`sysmon.sh`](./sysmon.sh)                                      | grabs netdev stats and timestamp every second or so, saves to logfile.                                                                                  |
| [`topmon.sh`](./topmon.sh)                                      | LANforge system monitor that can be used from cron                                                                                                      |
| [`update_dependencies.py`](./py-scripts/update_dependencies.py) | Installs Python dependencies required to run LANforge Python scripts. See the [`py-scripts/README`](./py-scripts/README.md#setup) for more information. |

### Library Code Scripts

These scripts/automation are presently used via relative importing from other scripts, including some scripts which also run tests when invoked directly.
This method is discouraged for new automation but available when absolutely necessary. The list is non-comprehensive.

| Name                                              | Purpose                                                                                                        |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| [`lf_graph.py`](./py-scripts/lf_graph.py)         | Classes for creating images from graphs using data sets                                                        |
| [`lf_report.py`](./py-scripts/lf_report.py)       | This program is a helper class for reporting results for a lanforge python script                              |
| [`sta_connect.py`](./py-scripts/sta_connect.py)   | Create a station, run TCP and UDP traffic then verify traffic was received. Stations are cleaned up afterwards |
| [`sta_connect2.py`](./py-scripts/sta_connect2.py) | Create a station, run TCP and UDP traffic then verify traffic was received. Stations are cleaned up afterwards |

### Unsorted or Older Scripts

Unsorted and generally older scripts. These are generally not regularly used and may sometimes show errors. This list is non-comprehensive.

| Name                            | Purpose                                                                                                                                                              |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `associate_loop.sh`             | Use this script to associate stations between SSIDs A and B                                                                                                          |
| `attenuator_series_example.csv` | Example of CSV input for a series of attenuator settings                                                                                                             |
| `attenuator_series.pl`          | Reads a CSV of attenuator settings and replays them to CT70X programmble attenuator                                                                                  |
| `ftp-upload.pl`                 | Use this script to collect and upload station data to FTP site                                                                                                       |
| `imix.pl`                       | packet loss survey tool                                                                                                                                              |
| `lf_associate_ap.pl`            | LANforge server script for associating virtual stations to an chosen SSID                                                                                            |
| `lf_auto_wifi_cap.pl`           | This program is used to automatically run LANforge-GUI WiFi Capacity tests                                                                                           |
| `lf_cmc_macvlan.pl`             | Stress test sets up traffic types of udp , tcp , continuously starts and stops the connections                                                                       |
| `lf_create_bcast.pl`            | creates a L3 broadcast connection                                                                                                                                    |
| `lf_cycle_wanlinks.pl`          | example of how to call lf_icemod.pl from a script                                                                                                                    |
| `lf_endp_script.pl`             | create a hunt script on a L3 connection endpoint                                                                                                                     |
| `lf_generic_ping.pl`            | Generate a batch of Generic lfping endpoints                                                                                                                         |
| `lf_gui_cmd.pl`                 | Initiate a stress test                                                                                                                                               |
| `lf_l4_auth.pl`                 | example of scripting L4 http script with basic auth                                                                                                                  |
| `lf_l4_reset.sh`                | reset any layer 4 connection that reaches 0 Mbps over last minute                                                                                                    |
| `lf_loop_traffic.sh`            | Repeatedly start and stop a L3 connection                                                                                                                            |
| `lf_macvlan_l4.pl`              | Set up connection types: lf_udp, lf_tcp across 1 real port and many macvlan ports on 2 machines. Then continously starts and stops the connections.                  |
| `lf_mcast.bash`                 | Create a multicast L3 connection endpoint                                                                                                                            |
| `lf_nfs_io.pl`                  | Creates and runs NFS connections                                                                                                                                     |
| `lf_port_walk.pl`               | Creates a series of connections, useful for basic firewall testing                                                                                                   |
| `lf_show_events.pl`             | Displays and clears LANforge event log                                                                                                                               |
| `lf_staggered_dl.sh`            | his script starts a series of Layer-3 connections across a series of stations each station will wait $nap seconds, download $quantity KB and then remove its old CX. |
| `lf_sta_name.pl`                | Use this script to alter a virtual station names                                                                                                                     |
| `lf_verify.pl`                  | Creates a basic L3 connection to verify that two ethernet ports are physically connected                                                                             |
| `lf_voip.pl`                    | Creates series of VOIP connections between two LANforge machines                                                                                                     |
| `lf_voip_test.pl`               | Creates series of VOIP connections and runs them                                                                                                                     |
| `lf_vue_mod.sh`                 | Bash script that wraps common operations for Virtual User Endpoint operations done by `lf_associate_ap`                                                              |
| `lf_wifi_rest_example.pl`       | Example script that queries a LF GUI for JSON data and displays a slice of it                                                                                        |
| `lf_zlt_binary.pl`              | Configures a Zero Loss Throughput test                                                                                                                               |
| `list_phy_sta.sh`               | Lists virtual stations backed by specified physical radio                                                                                                            |
| `min_max_ave_station.pl`        | This script looks for min-max-average bps for rx-rate in a station csv data file                                                                                     |
| `multi_routers.pl`              | Routing cleanup script that can be used with virtual routers                                                                                                         |
| `show-port-from-json.pl`        | Example script showing how to display a slice from a JSON GUI response                                                                                               |
| `station-toggle.sh`             | Use this script to toggle a set of stations on or off                                                                                                                |
| `test_refcnt.pl`                | creates MAC-VLANs and curl requests for each                                                                                                                         |
| `wait_on_ports.pl`              | waits on ports to have IP addresses, can up/down port to stimulate new DHCP lease                                                                                    |
| `wifi-roaming-times.pl`         | parses `wpa_supplicant_log.wiphyX` file to determine roaming times                                                                                                   |

## Exploring LANforge HTTP API/Crafting CLI Commands

**NOTE:** The term endpoint may be confusing, as you may also see the term 'endpoint' refer to traffic generation endpoints. In this section, all reference to 'endpoint' refers
to the HTTP version unless indicated otherwise.

### HTTP API/CLI Commands Overview

When the LANforge GUI is running, a user can query and configure their LANforge system using the LANforge HTTP API. This service runs on port 8080 _wherever the LANforge GUI runs_
and exposes HTTP API endpoints for various uses. Additionally, the manager exposes the direct CLI via a telnet-like interface on port 4001. However, for all but the most advanced
users, we recommend the HTTP API.

Most HTTP endpoints exist to query the system and generally match 1:1 with tabs in the LANforge GUI. The data available from query HTTP endpoints is returned as JSON and matches the data
available in the respective GUI tab (in the table). By default, though, only a limited set of data is returned for each endpoint. However, more specific fields may be queried as needed.
HTTP endpoints for configuration include `/cli-json/` and `/cli-form/`, both of which accept CLI commands in JSON and URL-encoded formats, respectively.

Information on available HTTP API endpoints is available at the main/root HTTP endpoint `http://GUI_SYSTEM_IP_HERE:8080/`, accessible via browser or by querying it
through `curl` (very verbose, e.g. `curl http://GUI_SYSTEM_IP_HERE:8080 | jq`). Additional information is available in our online documentation as well as in the HTTP
API help page `http://GUI_SYSTEM_IP_HERE:8080/help`.

### System Configuration with Command Composer

In order to better understand and use the HTTP API and CLI commands for system _configuration_, LANforge offers the web-based LANforge Command Composer. With this tool, a user can
dynamically generate CLI commands, either for use via the HTTP API via the `/cli-json/` and `/cli-form/` endpoints or directly through the telnet interface (port 4001).

To access and use this tool, perform the following steps:

1. Navigate to the 'Help' page (either from the LANforge or remotely)

   - Note that the IP or hostname should be the system where the _GUI_ is running
   - From the LANforge system (e.g. through VNC): `http://localhost:8080/help`
   - Remotely:
     - Directly by IP address: `http://192.168.1.101:8080/help`
     - Via DNS resolution, if supported by your network: `http://ct523c-cafe:8080/help`

2. Click on the link on the _left_ for your desired command, e.g. `add_sta`

   - Each CLI command will display two links. The link _on the left side_ takes you to the Command Composer tool.
     The right link takes you to the command in our CLI reference documentation.

3. Set the desired fields for the command

4. Click the `Parse Command` at the top
   - This generates CLI output for the fields you configured at the top of the webpage
   - Generated output includes:
     - CLI command for use in the telnet interface
     - Commands to manually send data to the `/cli-json/` and `/cli-form/` LANforge HTTP API endpoints

## Configure Non-Root Serial Access

Some automation requires accessing a DUT over a USB serial port (e.g. `/dev/ttyUSB0`). By default, you must explicitly allow users to access serial devices
on Linux. Otherwise, using a USB serial device requires root permissions (e.g. have to use `sudo`). For automation, we generally suggest _not_ running with
root permissions where possible.

There are several methods to configure this, each depending on the distribution (all require root access to the system). Often the easiest is to perform
the following:

1. Add your user to the `dialout` and `tty` groups

   ```Bash
   sudo usermod -a -G dialout,tty $USER
   ```

2. Log out and log back in (full logout required, not just closing the terminal)

   - Can also run the `newgrp` command, but this will only affect the currently running login session (i.e. that shell)

## License

Code in this repository is released under the BSD license (see [license.txt](./license.txt)).
