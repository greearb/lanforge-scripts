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

| Name | Purpose |
|------|---------|
| `lf_tos_test.py`      | Python script to generate traffic at different QoS and report performance in a spreadsheet |
| `lf_sniff.py`         | Python script to create packet capture files, especially OFDMA /AX captures |


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


