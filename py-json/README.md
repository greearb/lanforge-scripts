# LANforge Python JSON Scripts #

Similar to the JSON sibling directory that provides Perl JSON adapters
with the LANforge client, this directory provides Python adapters to
the LANforge client. The LANforge client is the LANforge Java GUI 
package running with the `-http` switch (by default) and possibly in the *headless*
mode using the `-daemon` switch.

Follow our [getting started cookbook](http://www.candelatech.com/cookbook.php?vol=cli&book=Querying+the+LANforge+GUI+for+JSON+Data) 
to learn more about how to operate your LANforge client.

## These Scripts ##

  * `show_ports.py`: this simple example shows how to gather a digest of ports
  * `create_sta.py`: Please follow though `create_sta.py` to see how you can
                     utilize the JSON API provided by the LANforge client. It
                     is possible to use similar commands to create virtual Access points.

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

