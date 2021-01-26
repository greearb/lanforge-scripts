# LANforge Python JSON Scripts #

Similar to the JSON sibling directory that provides Perl JSON adapters
with the LANforge client, this directory provides Python adapters to
the LANforge client. The LANforge client is the LANforge Java GUI
package running with the `-http` switch (by default) and possibly in the *headless*
mode using the `-daemon` switch.

Follow our [getting started cookbook](http://www.candelatech.com/cookbook.php?vol=cli&book=Querying+the+LANforge+GUI+for+JSON+Data)
to learn more about how to operate your LANforge client.

## Getting Started ##
The first step is to run update_deps.py which is located in py-scripts. This command will install all dependencies necessary for lanforge-scripts on your system.

New automation tests and JSON client scripts should go in `../py-scripts`. This directory
is intended for utility and library scripts. To use this module, make sure your include path
captures this module by adding it to your `sys.path`. We recommend your scripts in `../py-scripts`
begin with these imports:

    if 'py-json' not in sys.path:
        sys.path.append('../py-json')
    from LANforge import LFUtils
    from LANforge import lfcli_base
    from LANforge.lfcli_base import LFCliBase
    from LANforge.LFUtils import *
    import realm
    from realm import Realm


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

    * `__init__`: our constructor
    * `load()`: load a test scenario database, as you would find in the GUI Status tab
    * `cx_list()`: request json list of cross connects
    * `station_map()`: request a map of stations via `/port/list` and alter the list to name based map of only stations
    * `station_list()`: request a list of stations
    * `vap_list()`: request a list of virtual APs
    * `remove_vlan_by_eid()`: a way of deleting a port/station/vAP
    * `find_ports_like()`: returns a list of ports matching a string prefix, like:
      * `sta\*` matches names starting with `sta`
      * `sta10+` matches names with port numbers 10 or greater
      * `sta[10..20]` matches a range of stations including the range sta10 -- sta20
    * `name_to_eid()`: takes a name like `1.1.eth1` and returns it split into an array `[1, 1, "eth1"]`
    * `parse_time()`: returns numeric seconds when given strings like `1d`, `2h`, or `3m` or `4s`
    * `parse_link()`:
    * `new_station_profile()`: creates a blank station profile, configure station properties in this profile
                               and then use its `create()` method to create a series of stations
    * `new_l3_cx_profile()`: creates a blank Layer-3 profile, configure this connection profile and
                             then use its `create()` method to create a series of endpoints and cross connects
    * `new_l4_cx_profile()`: creates a blank Layer-4 (http/ftp) profile, configure it then call `create()`
    * `new_generic_cx_profile()`: creates a blank Generic connection profile (for lfping/iperf3/curl-post/speedtest.net)
                                  then configure and call `create()`
    * class `L3CXProfile`: this class is the Layer-3 connection profile **unfinished**
      * `__init__`: should be called by `Realm::new_l3_cx_profile()`
      * `create()`: pass endpoint-type, side-a list, side-b list, and sleep_time between creating endpoints and connections
      * Parameters for this profile include:
        * prefix
        * txbps
    * class `L4CXProfile`: this class is the Layer-4 connection profile **unfinished**
      * `__init__`: should be called by `Realm::new_l4_cx_profile()`
      * `create()`: pass a list of ports to create endpoints on, note that resulting cross connects are prefixed with `CX_`
      * Parameters for this profile include:
        * url
        * requests_per_ten: number of requests to make in ten minutes
    * class `GenCXProfile`: this class is the Generic connection profile **unfinished**
      * `__init__`: should be called by `Realm::new_gen_cx_profile()`
      * `create()`: pass a list of ports to create connections on
      * Parameters for this profile include:
        * type: includes lfping, iperf3, speedtest, lfcurl or cmd
        * dest: IP address of destination for command
    * class `StationProfile`: configure instances of this class for creating series of ports
      * `__init__`: should be called by `Realm::new_station_profile()`
      * `use_wpa2()`: pass on=True,ssid=a,passwd,b to set station_command_param add_sta/ssid, add_sta_key
                      pass on=False,ssid=a to turn off command_flag add_sta/flags/wpa2_enable
      * `set_command_param()`
      * `set_command_flag()`
      * `set_prefix()`
      * `add_named_flags()`
      * `create()`: you can use either an integer number of stations or a list of station names, if you want to create a
                    specific range of ports, create the names first and do not specify `num_stations`
        * resource: the resource number for the radio
        * radio: name of the radio, like 'wiphy0'
        * num_stations: `value > 0` indicates creating station series `sta0000..sta$value`
        * sta_names_: a list of station names to create, please use `LFUtils.port_name_series()`
        * dry_run: True avoids posting commands
        * debug:
    * class `PacketFilter` : This class provides filters that can be used with tshark
        * `get_filter_wlan_assoc_packets()` : This packet filter will look for wlan.fc.type_subtype<=3. It takes
                                             two arguments: `ap_mac` and `sta_mac`
        * `get_filter_wlan_null_packets()` : This packet filter will look for wlan.fc.type_subtype==44. It takes
                                             two arguments: `ap_mac` and `sta_mac`
        * `run_filter()` : This function will run the filter specified by the `filter` argument on the pcap
                          file specified by the `pcap_file` argument. It redirects this output into a txt file in /tmp
                          and returns the lines in that file as an array.
## realm_test.py ##
Exercises realm.py
## show_ports.py ##
This simple example shows how to gather a digest of ports
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
            super().__init__(host, port, _debug=debug_, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)

   Those parameters provide base functionality:
     * host: lfclient host running the LANforge GUI or headless LANforgeGUI -daemon
     * port: lfclient HTTP port, typically 8080
     * _debug: provides verbose mode behavior
     * _halt_on_error: if a HTTP 400 or HTTP 500 occurs or some execeptions are raised, exit
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


Have fun coding!
support@candelatech.com
