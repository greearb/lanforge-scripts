# LANForge Python Scripts 
This directory contains python scripts useful for unit-tests.  It uses
libraries in ../py-json.

#### Scripts included are: 

* `cicd_TipIntegration.py`:

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



