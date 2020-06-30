# LANForge Python Scripts 
This directory contains python scripts useful for unit-tests.  It uses libraries in ../py-json. Please place new tests in this directory. Unless they are libraries, please avoid adding python scripts to ../py-json.

# Getting Started
Please consider using the `LFCliBase` class as your script superclass. It will help you with a consistent set of JSON handling methods and pass and fail methods for recording test results. Below is a sample snippet that includes LFCliBase:

    if 'py-json' not in sys.path:
        sys.path.append('../py-json')
    from LANforge import LFUtils
    from LANforge import lfcli_base
    from LANforge.lfcli_base import LFCliBase
    from LANforge.LFUtils import *
    import realm
    from realm import Realm
    
    class Eggzample(LFCliBase):
        def __init__(self, lfclient_host, lfclient_port):
            super().__init__(lfclient_host, lfclient_port, debug=True)
    
    def main():
        eggz = Eggzample("http://localhost", 8080)
        frontpage_json = eggz.json_get("/")
        pprint.pprint(frontpage_json)
        data = {
            "message": "hello world"
        }
        eggz.json_post("/cli-json/gossip", data, debug_=True)
        
    if __name__ == "__main__":
        main()

The above example will stimulate output on the LANforge client websocket `ws://localhost:8081`. You can monitor system activity over that channel.

## Useful URIs:
* /: provides version information and a list of supported URIs
* /DUT/: Device Under Test records
* /alerts/: port or connection alerts
* /cli-form: post multi-part form data to this URI
* /cli-json: post JSON data to this URI
* /help: list of CLI commands and refence links
* /help/set_port: each CLI command has a command composer
* /cx: connections
* /endp: endpoints that make up connections
* /gui-cli: post multi-part form data for GUI automation
* /gui-json: post JSON data to this URI for GUI automation
* /port: list ports and stations, oriented by shelf, resource and name: `/port/1/1/eth0` is typically your management port
* /stations: entities that are associated to your virtual access points (vAP)
There are more URIs you can explore, these are the more useful ones.

#### Scripts included are: 

* `cicd_TipIntegration.py`: battery of TIP tests that include upgrading DUT and executing sta_connect script

* `cicd_testrail.py`: 
  * `function send_get`: Issues a GET request (read) against the API.
  * `function send_post`: Issues a write against the API.
  * `function __send_request`: 
  * `function get_project_id`: Gets the project ID using the project name
  * `function get_run_id`: Gets the run ID using test name and project name
  * `function update_testrail`: Update TestRail for a given run_id and case_id

* `cicd_testrailAndInfraSetup.py`:
  * class `GetBuild`:
     * function `get_latest_image`: extract a tar file from the latest file name from a URL
     * function run_`opensyncgw_in_docker`:
     * function `run_opensyncgw_in_aws`:
  * class `openwrt_linksys`:
    * function `ap_upgrade`: transfers file from local host to remote host. Upgrade access point with new information (?)
  * class `RunTest`:
    * function `TestCase_938`: checks single client connectivity
    * function `TestCase_941`: checks for multi-client connectivity
    * function `TestCase_939`: checks for client count in MQTT log and runs the clients (?)

* `run_cv_scenario.py`:
   * class `RunCvScenario`: imports the LFCliBase class.
    * function `get_report_file_name`: returns report name
    * function `build`: loads and sends the ports available? 
    * function `start`: /gui_cli takes commands keyed on 'cmd' and this function create an array of commands
* `sta_connect.py`:  This function creates a station, create TCP and UDP traffic, run it a short amount of time,
  and verify whether traffic was sent and received.  It also verifies the station connected
  to the requested BSSID if bssid is specified as an argument.
  The script will clean up the station and connections at the end of the test.
    * class `StaConnect(LFCliBase)`:
        * function `get_realm`: returns the local realm
        * function `get_station_url`:
        * function `get_upstream_url`:
        * function `compare_vals`: compares pre-test values to post-test values
        * function `remove_stations`: removes all stations
        * function `num_associated`:
        * function `clear_test_results`:
        * function `run`: 
        * function `setup`:
        * function `start`:
        * function `stop`:
        * function `finish`:
        * function `cleanup`:
        * function `main`:
* `sta_connect2.py`: This will create a station, create TCP and UDP traffic, run it a short amount of time,
  and verify whether traffic was sent and received.  It also verifies the station connected
  to the requested BSSID if bssid is specified as an argument. The script will clean up the station and connections at the end of the test.
    * function `get_realm`: returns local realm
    * function `get_station_url`:
    * function `get_upstream_url`:
    * function `compare_vals`: compares pre-test values to post-test values
    * function `remove_stations`: removes all ports
    * function `num_associated`: 
    * function `clear_test_results`
    * function `setup`: verifies upstream url, creates stations and turns dhcp on, creates endpoints,
    UDP endpoints,  
    * function `start`: 
    * function `stop`:
    * function `cleanup`:
    * function `main`: 

* `sta_connect_example.py`: example of how to instantiate StaConnect and run the test

* `sta_connect_multi_example.py`: example of how to instantiate StaConnect and run the test and create multiple OPEN stations,have 
some stations using WPA2 

* `stations_connected.py`: Contains examples of using realm to query stations and get specific information from them

* `test_ipv4_connection.py`:
  * class `IPv4Test`
        * function `run_test_full`:
        * function `run test_custom`:
        * function `_run_test`:
        * function `cleanup`: 
        * function `run`:

* `test_ipv6_connection.py`:
     * class `IPv6Test`
        * function `run_test_full`:
        * function `run test_custom`:
        * function `_run_test`:
        * function `cleanup`: 
        * function `run`:

* `test_ipv4_variable_time.py`:
     * class `IPv4VariableTime`
        * function `__set_all_cx_state`:
        * function `run_test`:
        * function `cleanup`:
        * function `run`:

* `test_wanlink.py`:
   * class `LANtoWAN`
      * function `run_test`:
      * function `create_wanlinks`:
      * function `run`:
      * function `cleanup`:

* `vap_stations_example.py`:
    * class `VapStations`
      * function `run`:
      * function `main`:



