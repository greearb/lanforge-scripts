# LANforge Python JSON Scripts #

Similar to the JSON sibling directory that provides Perl JSON adapters
with the LANforge client, this directory provides Python adapters to
the LANforge client. The LANforge client is the LANforge Java GUI
package running with the `-http` switch (by default) and possibly in the *headless*
mode using the `-daemon` switch.

Follow our [getting started cookbook](http://www.candelatech.com/cookbook.php?vol=cli&book=Querying+the+LANforge+GUI+for+JSON+Data)
to learn more about how to operate your LANforge client.

## Getting Started ##
New automation tests and JSON client scripts should go in `../py-scripts`. This directory
is intended for utility and library scripts. To use this module, make sure your include path
captures this module by adding it to your `sys.path`. We recommend your scripts in `../py-scripts`
begin with these imports:

    `if 'py-json' not in sys.path:
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
  * `create_sta.py`: Please follow though `create_sta.py` to see how you can
                     utilize the JSON API provided by the LANforge client. It
                     is possible to use similar commands to create virtual Access points.
  * `create_wanlink.py`: example that creates a WANlink
  * `generic_cx.py`: example that creates a cross connect
  * `realm.py`: module defining the Realm class. `Realm` is a toolbox class that also serves as a facade
                for finer-grained methods in LFUtils and LFRequest:
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
    * `class L3CXProfile`: this class is the Layer-3 connection profile
      * `__init__`: should be called by `Realm::new_l3_cx_profile()`
      * `create()`: pass endpoint-type, side-a list, side-b list, and sleep_time between creating endpoints and connections
      * Parameters for this profile include:
        * prefix
        * txbps
    * `class L4CXProfile`: this class is the Layer-4 connection profile
      * `__init__`: should be called by `Realm::new_l4_cx_profile()`
      * `create()`: pass a list of ports to create endpoints on, note that resulting cross connects are prefixed with `CX_`
      * Parameters for this profile include:
        * url
        * requests_per_ten: number of requests to make in ten minutes
        *
  * `show_ports.py`: this simple example shows how to gather a digest of ports



## LANforge ##
This directory defines the LANforge module holding:

  * LFRequest: provides default mechanism to make API queries, use this
      to create most of your API requests, but you may also use the normal
      `urllib.request` library on simple GET requests if you wish.
     * formPost(): post data in url-encoded format
     * jsonPost(): post data in JSON format
     * get(): GET method returns text (which could be JSON)
     * getAsJson(): converts get() JSON results into python objects
     * addPostData(): provide a dictionary to this method before calling formPost() or jsonPost()

  * LFUtils: defines constants and utility methods
    * class PortEID: convenient handle for port objects
    * newStationDownRequest(): create POST data object for station down
    * portSetDhcpDownRequest(): create POST data object for station down, apply `use_dhcp` flags
    * portDhcpUpRequest(): apply `use_dhcp`, ask for station to come up
    * portUpRequest(): ask for station to come up
    * portDownRequest(): ask for station to go down
    * generateMac(): generate mac addresses
    * portNameSeries(): produce a padded-number series of port names
    * generateRandomHex(): series of random octets
    * portAliasesInList(): returns station aliases from `/port` listing
    * findPortEids(): returns EIDs of ports
    * waitUntilPortsAdminDown(): watch ports until they report admin down
    * waitUntilPortsAdminUp(): watch ports until they report admin up
    * waitUntilPortsDisappear(): use this after deleting ports
    * waitUntilPortsAppear(): use this after `add_sta` or `set_port`


Have fun coding!
support@candelatech.com

