# LANforge Perl, Python, and Shell Scripts #
This is a collection of scripts and scripting libraries designed to work
with LANforge systems. On your LANforge system, these scripts are
typically installed into `/home/lanforge/scripts`. The `LANforge/` sub directory holds
the perl modules (`.pm` files) that are common to the perl scripts.

### Commonly Used ###
The `lf_*.pl` scripts are typically more complete and general purpose
scripts, though some are ancient and very specific.  In particular,
these scripts are more modern and may be a good place to start:

| Name             | Purpose   |
|------------------|-----------|
| `lf_portmod.pl`       | Query and update physical and virtual ports |
| `lf_firemod.pl`       | Query and update connections (Layer 3) |
| `lf_icemod.pl`        | Query and update WAN links and impairments |
| `lf_attenmod.pl`      | Query and update CT70X programmable attenuators |
| `lf_associate_ap.pl`  | Query and update wifi stations |
| `lf_tos_test.py`      | Python script to generate traffic at different QoS and report in spreadsheet |
| `lf_sniff.py`         | Python script to create packet capture files, especially OFDMA /AX captures |

The `lf_wifi_rest_example.pl` script shows how one might call the other scripts from
within a script.

### Examples and Documents ###
Read more examples in the [scripting LANforge](http://www.candelatech.com/lfcli_api_cookbook.php) cookbook.

### Python Scripts ###

When starting to use Python, please run the update_deps.py script located in py-scripts to install all necessary dependencies for this library.

| Name | Purpose |
|------|---------|
| `lf_tos_test.py`                   | Python script to generate traffic at different QoS and report performance in a spreadsheet |
| `lf_sniff.py`                      | Python script to create packet capture files, especially OFDMA /AX captures |
| `cicd_TipIntegration.py`           | Python script for Facebook TIP infrastructure|
| `cicd_testrail.py`                 | TestRail API binding for Python 3 |
| `cicd_testrailAndInfraSetup.py`    | Python script for Facebook TIP infrastructure |
| `lf_cisco_dfs.py`                  | Python scripts customized for cisco controllers |
| `lf_cisco_snp.py`                  | Python script customized for cisco controllers  |
| `lf_dut_sta_vap_test.py`           | Python script to load an existing scenario, start some layer 3 traffic, and test the Linux based DUT that has SSH server |
| `run_cv_scenario.py`               | Python script to set the LANforge to a BLANK database then it will load the specified database and start a graphical report |
| `sta_connect2.py`                  | Python script to create a station, run TCP and UDP traffic then verify traffic was received. Stations are cleaned up afterwards |
| `test_fileio.py`                   | Python script to test FileIO traffic |
| `test_generic.py`                  | Python script to test generic traffic using generic cross-connect and endpoint type |
| `test_ipv4_connection.py`          | Python script to test connections to a VAP of varying security types (WEP, WPA, WPA2, WPA3, Open) |
| `test_ipv4_l4.py`                  | Python script to test layer 4 traffic using layer 4 cross-connect and endpoint type |
| `test_ipv4_l4_ftp_upload.py`       | Python script to test ftp upload traffic |
| `test_ipv4_l4_ftp_urls_per_ten.py` | Python script to test the number of urls per ten minutes in ftp traffic |
| `test_ipv4_l4_ftp_wifi.py`         | Python script to test ftp upload traffic wifi-wifi |
| `test_ipv4_l4_urls_per_ten.py`     | Python script to test urls per ten minutes in layer 4 traffic |
| `test_ipv4_l4_wifi.py`             | Python script to test layer 4 upload traffic wifi-wifi|
| `test_ipv4_ttls.py`                | Python script to test connection to ttls system |
| `test_ipv4_variable_time.py`       | Python script to test connection and traffic on VAPs of varying security types (WEP, WPA, WPA2, WPA3, Open) |
| `test_ipv6_connection.py`          | Python script to test IPV6 connection to VAPs of varying security types (WEP, WPA, WPA2, WPA3, Open) |
| `test_ipv6_variable_time.py`       | Python script to test IPV6 connection and traffic on VAPs of varying security types (WEP, WPA, WPA2, WPA3, Open) |
| `test_l3_WAN_LAN.py`               | Python script to test traffic over a bridged NAT connection |
| `test_l3_longevity.py`             | Python script customized for cisco controllers |
| `test_l3_scenario_throughput.py`   | Python script to load an existing scenario and run the simultaneous throughput over time and generate report and P=plot the G=graph|
| `test_l3_unicast_traffic_gen.py`   | Python script to generate unicast traffic over a list of stations|
| `tip_station_powersave.py`         | Python script to generate and test for powersave packets within traffic run over multiple stations |


### Perl and Shell Scripts ###

| Name | Purpose |
|------|---------|
| `associate_loop.sh`              | Use this script to associate stations between SSIDs A and B |
| `attenuator_series_example.csv`  | Example of CSV input for a series of attenuator settings |
| `attenuator_series.pl`           | Reads a CSV of attenuator settings and replays them to CT70X programmble attenuator |
| `ftp-upload.pl`                  | Use this script to collect and upload station data to FTP site |
| `imix.pl`                        | packet loss survey tool |
| `lf_associate_ap.pl`             |  LANforge server script for associating virtual stations to an chosen SSID |
| `lf_attenmod.pl`                 | This program is used to modify the LANforge attenuator through the LANforge |
| `lf_auto_wifi_cap.pl`            | This program is used to automatically run LANforge-GUI WiFi Capacity tests |
| `lf_cmc_macvlan.pl`              | This program is used to stress test the LANforge system, and may be used as an example for others who wish to automate LANforge tests |
| `lf_create_bcast.pl`             | creates a L3 broadcast connection |
| `lf_cycle_wanlinks.pl`           | example of how to call lf_icemod.pl from a script |
| `lf_endp_script.pl`              | create a hunt script on a L3 connection endpoint |
| `lf_firemod.pl`                  | queries and modifies L3 connections |
| `lf_icemod.pl`                   | queries and modified WANLink connections |
| `lf_ice.pl`                      | adds and configures wanlinks |
| `lf_l4_auth.pl`                  | example of scripting L4 http script with basic auth |
| `lf_l4_reset.sh`                 | reset any layer 4 connection that reaches 0 Mbps over last minute |
| `lf_log_parse.pl`                | Convert the timestamp in LANforge logs (it is in unix-time, miliseconds) to readable date |
| `lf_loop_traffic.sh`             | Repeatedly start and stop a L3 connection |
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

### Compatibility ###
Scripts will be kept backwards and forwards compatible with LANforge
releases as much as possible.

### Installation ###
These scripts call each other and rely on the structure of this directory. To use these scripts in other locations,
such as your laptop, either copy the entire scripts directory or do a __git clone__ of this repository. Just copying
one script to a separate directory is going to break its requirements.

### Requirements ###
The perl scripts require the following perl packages to be installed. Most of these
perl packages are available through your repository as `.deb` or `.rpm` packages.

| Perl Package       | RPM              | Required       |
| -------------------|------------------|----------------|
| Net::Telnet        | perl-Net-Telnet |  Yes            |
| JSON               | perl-JSON       |  Yes, for JSON parsing |
| JSON::PrettyPrint  | perl-JSON-PP    |  No, useful for debugging |

| Python3 Package  |  RPM    | Required    |
|-------------------------|-----------|---------------|
| Pexpect                 | python3-pexpect | yes |
| XlsxWriter             | python3-xlsxwriter | yes, Xlsx output |


#### Pip v Pip3 ####
Please use pip3, we are targeting Python 3 with our scripts. If your pip/pip3 repositories have a difficult time connecting,
it's likely that you are trying to download from **pypi.python.org**. This is a deprecated location. Please update
using the **pypi.org** servers. Consider updating your ``~/.pypirc`` file:

````
[distutils]
index-servers =  
    pypi  

[pypi]  
repository: https://upload.pypi.org/legacy/
````


As [described on Python.org](https://packaging.python.org/guides/migrating-to-pypi-org/).

### License ###
Code in this repository is released under the BSD license (see license.txt).


### Support ###
Please contact support@candelatech.com if you have any questions.

_Thanks,
Ben_
