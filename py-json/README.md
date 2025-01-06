# LANforge Python JSON Scripts

**NOTE:** While we still support the `py-json` components listed here, new LANforge automation will leverage the auto-generated [LANforge API](../lanforge_client/) Python JSON components.

Similar to the sibling directory [`LANforge/`](../LANforge/) that provides Perl JSON adapters for Perl-based LANforge automation, the `py-json` directory provides Python adapters for Python-based LANforge automation. Existing LANforge automation-based test and helper scripts exist mostly in [`py-scripts/`](../py-scripts/). This directory (`py-json`) is largely intended for utility and library Python code for use in external scripts.

To leverage this automation, the LANforge GUI must be active and running with the `-http` switch (active by default). It is possible to run the LANforge GUI in *headless* mode using the `-daemon` switch, as well.

Follow our [getting started cookbook](http://www.candelatech.com/cookbook.php?vol=cli&book=Querying+the+LANforge+GUI+for+JSON+Data) to learn more about how to leverage the LANforge JSON API or email [`support@candelatech.com`](mailto:support@candelatech.com) with questions.


## Getting Started

To get started, please first follow the setup instructions outlined in the `py-scripts` README [here](../py-scripts/README.md).

To use this module, make sure your include path captures this module by adding it to your `sys.path`. We recommend your scripts in `../py-scripts`
begin with these imports:

    if 'py-json' not in sys.path:
        sys.path.append('../py-json')
    from LANforge import LFUtils
    from LANforge import lfcli_base
    from LANforge.lfcli_base import LFCliBase
    from LANforge.LFUtils import *
    import realm
    from realm import Realm

### Python Scripts `py-json/LANforge/`

Core communication files to LANforge

| Name | Purpose |
|------|---------|
| `add_dut.py`            | defined list of DUT keys, cli equivalent: https://www.candelatech.com/lfcli_ug.php#add_dut  |
| `add_file_endp.py`      | Add a File endpoint to the LANforge Manager.  cli equivalent: add_file_endp https://www.candelatech.com/lfcli_ug.php#add_file_endp |
| `add_l4_endp.py`        |  Add a Layer 4-7 (HTTP, FTP, TELNET, ..) endpoint to the LANforge Manager. cli equivalent: add_l4_endp https://www.candelatech.com/lfcli_ug.php#add_l4_endp |
| `add_monitor.py`        | Add a WIFI Monitor interface. These are useful for doing low-level wifi packet capturing.  cli equivalent: add_monitor https://www.candelatech.com/lfcli_ug.php#add_monitor |
| `add_sta.py`            | Add a WIFI Virtual Station (Virtual STA) interface. cli equivalent: add_sta https://www.candelatech.com/lfcli_ug.php#add_sta |
| `add_vap.py`            | Add a WIFI Virtual Access Point (VAP) interface.  cli equivalent: add_vap https://www.candelatech.com/lfcli_ug.php#add_vap |
| `set_port.py`           | This command allows you to modify attributes on an Ethernet port.  cli equivalent: set_port https://www.candelatech.com/lfcli_ug.php#set_port |
| `lfcli_base.py`          | json communication to LANforge |
| `LFRequest.py`          | Class holds default settings for json requests to LANforge, see: https://gist.github.com/aleiphoenix/4159510|
| `LFUtils.py`            | Defines useful common methods |
| `set_port.py`           | This command allows you to modify attributes on an Ethernet port. These options includes the IP address, netmask, gateway address, MAC, MTU, and TX Queue Length. cli equivalent: set_port https://www.candelatech.com/lfcli_ug.php#set_port |


### Python Scripts `py-json/`
| Name | Purpose |
|------|---------|
| `base_profile.py`                 | Class: BaseProfile  Use example: py-json/l3_cxprofile2.py used to define generic utility methods to be inherited by other classes |
| `create_wanlink.py`               | Create and modify WAN Links Using LANforge JSON AP : http://www.candelatech.com/cookbook.php?vol=cli&book=JSON:+Managing+WANlinks+using+JSON+and+Python |
| `cv_commands.py`                  | This is a library file used to create a chamber view scenario.  import this file as showed in create_chamberview.py to create a scenario |
| `cv_test_manager.py`              | This script is working as library for chamberview tests.  It holds different commands to automate test. |
| `cv_test_reports.py`              | Class: lanforge_reports  Pulls reports from LANforge |
| `dut_profile.py`                  | Class: DUTProfile (new_dut_profile) Use example:  py-scripts/update_dut.py used to updates a Device Under Test (DUT) entry in the LANforge test scenario A common reason to use this would be to update MAC addresses in a DUT when you switch between different items of the same make/model of a DUT |
| `fio_endp_profile.py`             | Class: FIOEndpProfile (new_fio_endp_profile) Use example: py-scripts/test_fileio.py will create stations or macvlans with matching fileio endpoints to generate and verify  fileio related traffic |
| `gen_cxprofile.py`                | Class: GenCXProfile (new_generic_endp_profile) Use example: test_generic.py  will create stations and endpoints to generate traffic based on a command-line specified command type |
| `http_profile.py`                 | Class: HTTPProfile (new_http_profile) Use example: test_ipv4_l4_wifi.py  will create stations and endpoints to generate and verify layer-4 upload traffic |
| `l3_cxprofile.py`                 | Class: L3CXProfile (new_l3_cx_profile)  Use example: test_ipv4_variable_time.py will create stations and endpoints to generate and verify layer-3 traffic |
| `l3_cxprofile2.py`                | Class: L3CXProfile2 (new_l3_cx_profile, ver=2) No current use example, inherits utility functions from BaseProfile, maintains functionality of L3CXProfile |
| `l4_cxprofile.py`                 | Class: L4CXProfile (new_l4_cx_profile) Use example: test_ipv4_l4.py will create stations and endpoints to generate and verify layer-4 traffic |
| `lf_cv_base.py`                   | Class: ChamberViewBase, Base Class to be used for Chamber View Tests, inherited by DataPlaneTest in dataplane_test_profile.py |
| `lfdata.py`                       | Class: LFDataCollection, class used for data collection utility methods |
| `mac_vlan_profile.py`             | Class: MACVLANProfile (new_mvlan_profile) Use example: test_fileio.py will create stations or macvlans with matching fileio endpoints to generate and verify  fileio related traffic. |
| `multicast_profile.py`            | Class: MULTICASTProfile (new_multicast_profile) Use example: test_l3_longevity.py multi cast profiles are created in this test |
| `port_utils.py`                   | Class: PortUtils used to set the ftp or http port |
| `qvlan_profile.py`                | Class: QVLANProfile (new_qvlan_profile) Use example: create_qvlan.py (802.1Q VLAN) |
| `realm.py`                        | Class: The Realm Class is inherited by most python tests.  Realm Class inherites from LFCliBase. The Realm Class contains the configurable components for LANforge,  For example L3 / L4 cross connects, stations.  http://www.candelatech.com/cookbook.php?vol=cli&book=Python_Create_Test_Scripts_With_the_Realm_Class |
| `realm_test.py`                   | Python script meant to test functionality of realm methods |
| `station_profile.py`              | Class: StationProfile (new_station_profile) Use example: most scripts create and use station profiles |
| `test_base.py`                    | Class: TestBase, basic class for creating tests, uses basic functions for cleanup, starting/stopping, and passing of tests |
| `test_group_profile.py`           | Class: TestGroupProfile (new_test_group_profile) Use example: test_fileio.py will create stations or macvlans with matching fileio endpoints to generate and verify  fileio related traffic |
| `test_utility.py`                 | Standard Script for Webconsole Test Utility |
| `vap_profile.py`                  | Class: VAPProfile (new_vap_profile) profile for creating Virtual AP's Use example: create_vap.py |
| `vr_profile2.py`                  | Class: VRProfile (new_vap_profile, ver=2) No current use example, inherits utility functions from BaseProfile |
| `wifi_monitor_profile.py`         | Class: WifiMonitor (new_wifi_monitor_profile) Use example: tip_station_powersave.py This script uses filters from realm's PacketFilter class to filter pcap output for specific packets. |
| `wlan_theoretical_sta.py`         | Class: abg11_calculator Standard Script for WLAN Capaity Calculator  Use example: wlan_capacitycalculator.py |
| `ws-sta-monitor.py`               | Example of how to filter messages from the :8081 websocket |
| `ws_generic_monitor.py`           | Class: WS_Listener web socket listener Use example: ws_generic_monitor_test.py, ws_generic_monitor to monitor events triggered by scripts, This script when running, will monitor the events triggered by test_ipv4_connection.py |


## These Scripts ##

  * `__init__.py`: this is a module header and it defines its relationship to sub-module LANforge,
                   requiring LFRequest.
  * `LANforge`: this module is for our json library. Use gain access to these by using:
                `import LANforge`
                `from LANforge import LFUtils`
                `from LANforge import LFRequest`
## create_sta.py ##
Please follow though `create_sta.py` to see how you can
utilize the JSON API provided by the LANforge client. It
is possible to use similar commands to create virtual Access points.
## create_wanlink.py ##
Example that creates a WANlink
## generic_cx.py ##
Example that creates a cross connect
## realm.py ##
Module defining the Realm class. `Realm` is a toolbox class that also serves as a facade for finer-grained methods in LFUtils and LFRequest:

     *`def __init__()`: our constructor
     *`def wait_until_ports_appear()`: takes a list of ports and waits until they all appear in the list of existing stations
     *`def wait_until_ports_disappear()`: takes a list of ports and waits until they all disappear from the list of existing stations
     *`def rm_port()`: takes a string in eid format and attempts to remove it
     *`def port_exists()`: takes a string in eid format and returns a boolean depending on if the port exists
     *`def admin_up()`: takes a string in eid format attempts to set it to admin up
     *`def admin_down()`: takes a string in eid format attempts to set it to admin down
     *`def reset_port()`: takes a string in eid format requests a port reset
     *`def rm_cx()`: takes a cross connect name as a string and attempts to remove it from LANforge
     *`def rm_endp()`: takes an endpoint name as a string and attempts to remove it from LANforge
     *`def set_endp_tos()`: attempts to set tos of a specified endpoint name
     *`def stop_cx()`: attempts to stop a cross connect with the given name
     *`def cleanup_cxe_prefix()`: attempts to remove all existing cross connects and endpoints
     *`def channel_freq()`: takes a channel and returns its corresponding frequency
     *`def freq_channel()`: takes a frequency and returns its corresponding channel
     *`def wait_while_building()`: checks for OK or BUSY when querying cli-json/cv+is_built
     *`def load()`: loads a database from the GUI
     *`def cx_list()`: request json list of cross connects
     *`def waitUntilEndpsAppear()`: takes a list of endpoints and waits until they all disappear from the list of existing endpoints
        *deprecated method use def wait_until_endps_appear() instead*
     *`def wait_until_endps_appear()`: takes a list of endpoints and waits until they all appear in the list of existing endpoints
     *`def waitUntilCxsAppear()`: takes a list of cross connects and waits until they all disappear from the list of existing cross connects
        *deprecated method use def wait_until_cxs_appear() instead*
     *`def wait_until_cxs_appear()`: takes a list of cross connects and waits until they all disappear from the list of existing cross connects
     *`def station_map()`: request a map of stations via `/port/list` and alter the list to name based map of only stations
     *`def station_list()`: request a list of stations
     *`def vap_list()`: request a list of virtual APs
     *`def remove_vlan_by_eid()`: a way of deleting a port/station/vAP
     *`def find_ports_like()`: returns a list of ports matching a string prefix, like:
      * `sta\*` matches names starting with `sta`
      * `sta10+` matches names with port numbers 10 or greater
      * `sta[10..20]` matches a range of stations including the range sta10 -- sta20
     *`def name_to_eid()`: takes a name like `1.1.eth1` and returns it split into an array `[1, 1, "eth1"]`
     *`def wait_for_ip()`: takes a list of stations and waits until they all have an ip address. Default wait time is 360 seconds,
                           can take -1 as timeout argument to determine timeout based on mean ip acquisition time
     *`def get_curr_num_ips()`: returns the number of stations with an ip address
     *`def duration_time_to_seconds()`: returns an integer for a time string converted to seconds
     *`def remove_all_stations()`: attempts to remove all currently existing stations
     *`def remove_all_endps()`: attempts to remove all currently existing endpoints
     *`def remove_all_cxs()`: attempts to remove all currently existing cross connects
     *`def new_station_profile()`: creates a blank station profile, configure station properties in this profile
                               and then use its `create()` method to create a series of stations
     *`def new_multicast_profile()`: creates a blank multicast profile, configure it then call `create()`
     *`def new_wifi_monitor_profile()`: creates a blank wifi monitor profile, configure it then call `create()`
     *`def new_l3_cx_profile()`: creates a blank Layer-3 profile, configure this connection profile and
                             then use its `create()` method to create a series of endpoints and cross connects
     *`def new_l4_cx_profile()`: creates a blank Layer-4 (http/ftp) profile, configure it then call `create()`
     *`def new_generic_endp_profile()`: creates a blank Generic endpoint profile, configure it then call `create()`
     *`def new_generic_cx_profile()`: creates a blank Generic connection profile (for lfping/iperf3/curl-post/speedtest.net)
                                  then configure and call `create()`
     *`def new_vap_profile()`: creates a blank VAP profile, configure it then call `create()`
     *`def new_vr_profile()`: creates a blank VR profile, configure it then call `create()`
     *`def new_http_profile()`: creates a blank HTTP profile, configure it then call `create()`
     *`def new_fio_endp_profile()`: creates a blank FileIO profile, configure it then call `create()`
     *`def new_dut_profile()`: creates a blank DUT profile, configure it then call `create()`
     *`def new_mvlan_profile()`: creates a blank MACVLAN profile, configure it then call `create()`
     *`def new_qvlan_profile()`: creates a blank QVLAN profile, configure it then call `create()`
     *`def new_test_group_profile()`: creates a blank Test Group profile, configure it then call `create()`
    *`class PacketFilter()`: This class provides filters that can be used with tshark
     *`def get_filter_wlan_assoc_packets()`: This packet filter will look for wlan.fc.type_subtype<=3. It takes
                                             two arguments: `ap_mac` and `sta_mac`
     *`def get_filter_wlan_null_packets()`: This packet filter will look for wlan.fc.type_subtype==44. It takes
                                             two arguments: `ap_mac` and `sta_mac`
     *`def run_filter()`: This function will run the filter specified by the `filter` argument on the pcap
                          file specified by the `pcap_file` argument. It redirects this output into a txt file in /tmp
                          and returns the lines in that file as an array.



## realm_test.py ##
Exercises realm.py
## test_l4.py ##
Example of how to use LFRequest to create a L4 endpoint
## wct-example.py ##
Example of using expect on port 3990 to operate a WiFi Capacity Test
## ws-sta-monitor.py ##
Websocket 8081 client that filters interesting station events from the lfclient websocket



## LANforge ##
This directory defines the LANforge module holding the following classes:
  * lfcli_base.py / class **LFCliBase**: This is a base class we encourage using for creating tests and
  other automation scripts. It provides a centralized manner for making uniform JSON GET and POST
  calls.
    * `__init__`: call this from your classes __init__ method as super().__init__(...) like below:

        class MyScript(LFCliBase):
        def __init__(self, host, port, debug_=False, _exit_on_error=False, _exit_on_fail=False):
            super().__init__(host, port, _debug=debug_, _exit_on_fail=_exit_on_fail)

   Those parameters provide base functionality:
     * host: lfclient host running the LANforge GUI or headless LANforgeGUI -daemon
     * port: lfclient HTTP port, typically 8080
     * _debug: provides verbose mode behavior
     * _exit_on_fail: if a test calls _fail(), exit

  * LFRequest.py / class **LFRequest**: provides default mechanism to make API queries, use this
      to create most of your API requests, but you may also use the normal
      `urllib.request` library on simple GET requests if you wish.
     * form_post(): post data in url-encoded format
     * json_post(): post data in JSON format
     * get(): GET method returns text (which could be JSON)
     * get_as_json(): converts get() JSON results into python objects
     * add_post_data(): provide a dictionary to this method before calling formPost() or jsonPost()

  * LFUtils.py / class **LFUtils**: defines constants and utility methods
    * class PortEID: convenient handle for port objects
    * sta_new_down_sta_request(): create POST data object for station down
    * port_set_dhcp_down_request(): create POST data object for station down, apply `use_dhcp` flags
    * port_dhcp_up_request(): apply `use_dhcp`, ask for station to come up
    * port_up_request(): ask for station to come up
    * port_down_request(): ask for station to go down
    * generate_mac(): generate mac addresses
    * port_name_series(): produce a padded-number series of port names
    * generate_random_hex(): series of random octets
    * portAliasesInList(): returns station aliases from `/port` listing
    * find_port_eids(): returns EIDs of ports
    * wait_until_ports_admin_down(): watch ports until they report admin down
    * wait_until_ports_admin_up(): watch ports until they report admin up
    * wait_until_ports_disappear(): use this after deleting ports
    * ~~waitUntilPortsDisappear()~~: use this after deleting ports, **deprecated**
    * wait_until_ports_appear(): use this after `add_sta` or `set_port`
    * remove_port(): remove a port using rm_vlan command
    * remove_cx(): request a list of CX names be removed
    * remove_endps(): request a list of endpoint names be removed
    * exec_wrap(): hair trigger method that exits when a command fails when called by os.system()
