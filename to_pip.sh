#! /bin/bash
Help()
{
  echo "This script modifies lanforge scripts so that it can be imported into python as a library"
  echo "store this repository in your python path, and then import lanforge_scripts from anywhere on your machine"
  echo "An example of how to run this in python is like so:"
  echo "import lanforge_scripts"
  echo "ip_var=lanforge_scripts.IPVariableTime(host='192.168.1.239',port='8080',radio='wiphy0',sta_list=['1.1.sta0000','1.1.sta0001'],ssid='lanforge',password='password',security='wpa2',upstream='eth1',name_prefix='VT',traffic_type='lf_udp',_debug_on=True)"
  echo "ip_var.build()"
  echo "ip_var.start(False,False)"
}

while getopts ":h:a:t:" option; do
  case "${option}" in
    h) #display help
      Help
      exit 1
      ;;
    a) #Archive
      ARCHIVE=1
      ;;
    t) #target dir
      TARGET_DIR=${OPTARG}
      ;;
    *)
      ;;
  esac
done
#Rename repository so it can be imported as a package
cd ..
mv lanforge-scripts lanforge_scripts
cd lanforge_scripts

ln -s py-scripts/ py_scripts
ln -s py-json/ py_json
ln -s py-dashboard/ py_dashboard


echo "#Automate LANforge devices with lanforge-scripts

from .py_scripts import *
from .py_dashboard import *
from .py_json import *
from .py_json import LANforge
from .py_json.LANforge import *
from . import ap_ctl
from . import emailHelper
from . import lf_mail
from . import lf_tos_plus_test
from . import lf_tx_power
from . import tos_plus_auto
#from . import auto_install_gui
from . import cpu_stats
from . import lf_sniff
from . import lf_tos_test
from . import openwrt_ctl
#from . import stationStressTest
from . import wifi_ctl_9800_3504

__all__ = ['LFRequest', 'LFUtils', 'LANforge','LFCliBase']

__title__ = 'lanforge_scripts'
__version__ = '0.0.1'
__author__ = 'Candela Technologies <www.candelatechnologies.com>'
__license__ = ''" > __init__.py

#fix files in root
sed -i -- 's/from LANforge/from py_json.LANforge/g' *.py
sed -i -- 's/from py_json/from .py_json/g' *.py

cd py_scripts

echo "#from .connection_test import ConnectionTest
from .create_bond import CreateBond
from .create_bridge import CreateBridge
from .create_chamberview import CreateChamberview
from .create_l3 import CreateL3
from .create_l4 import CreateL4
from .create_macvlan import CreateMacVlan
from .create_qvlan import CreateQVlan
from .create_station import CreateStation
from .create_vap import CreateVAP
from .csv_convert import CSVParcer
from .csv_processor import L3CSVParcer
from .csv_to_influx import CSVtoInflux
from .csv_to_grafana import UseGrafana
from .download_test import DownloadTest
from .event_breaker import EventBreaker
from .event_flood import EventBreaker as EventFlood
from .example_security_connection import IPv4Test
from .ghost_profile import UseGhost
from .grafana_profile import UseGrafana
from .influx import RecordInflux
from .layer3_test import Layer3Test
from .layer4_test import HTTPTest
from .lf_ap_auto_test import ApAutoTest
from .lf_atten_mod_test import CreateAttenuator
from .lf_csv import lf_csv, lf_kpi_csv
from .lf_dataplane_test import DataplaneTest
from .lf_dfs_test import FileAdapter, CreateCtlr, L3VariableTime
from .lf_dut_sta_vap_test import Login_DUT, LoadScenario, CreateSTA_CX
from .lf_ftp_test import ftp_test
from .lf_ftp import FtpTest
from .lf_graph import lf_bar_graph, lf_stacked_graph, lf_horizontal_stacked_graph, lf_scatter_graph, lf_line_graph
from .lf_mesh_test import MeshTest
from .lf_multipsk import MultiPsk
from .lf_report import lf_report
from .lf_rvr_test import RvrTest
from .lf_rx_sensitivity_test import RxSensitivityTest
from .lf_sniff_radio import SniffRadio
#from .lf_snp_test import  SAME CLASS NAMES AS LF_DFS_TEST
#from .lf_tr398_test import DataPlaneTest
from .lf_webpage import HttpDownload
from .lf_wifi_capacity_test import WiFiCapacityTest
from .measure_station_time_up import MeasureTimeUp
from .modify_station import ModifyStation
from .modify_vap import ModifyVAP
from .run_cv_scenario import RunCvScenario
from .sta_connect import StaConnect
from .sta_connect2 import StaConnect2
from .sta_connect_bssid_mac import client_connect
from .station_layer3 import STATION
from .stations_connected import StationsConnected
from .test_1k_clients_jedtest import Test1KClients
from .test_client_admission import LoadLayer3
from .test_fileio import FileIOTest
from .test_generic import GenTest
from .test_ip_connection import ConnectTest
from .test_ip_variable_time import IPVariableTime
from .test_ipv4_ttls import TTLSTest
from .test_ipv4_ps import IPV4VariableTime
#from .test_l3_longevity import L3VariableTime ALSO IN LF_DFS_TEST
from .test_l3_powersave_traffic import L3PowersaveTraffic
#from .test_l3_scenario_throughput import
from .test_l3_unicast_traffic_gen import L3VariableTimeLongevity
from .test_l3_WAN_LAN import VRTest
from .test_l4 import IPV4L4
from .test_status_msg import TestStatusMessage
#from .test_wanlink import LANtoWAN
#from .test_wpa_passphrases import WPAPassphrases
from .testgroup import TestGroup
from .testgroup2 import TestGroup2
from .tip_station_powersave import TIPStationPowersave
from .vap_stations_example import VapStations
from .video_rates import VideoRates
from .wlan_capacity_calculator import main as WlanCapacityCalculator
from .ws_generic_monitor_test import WS_Listener" > __init__.py

# Fix files in py_scripts
sed -i -- 's/import realm/ /g' create_vap.py lf_dut_sta_vap_test.py lf_sniff_radio.py run_cv_scenario.py sta_connect.py station_layer3.py test_client_admission.py
sed -i -- 's/import realm/from realm import Realm/g' layer4_test.py lf_atten_mod_test.py lf_multipsk.py test_fileio.py test_ip_connection.py test_ipv4_ttls.py test_l3_WAN_LAN.py test_l3_unicast_traffic_gen.py test_l4.py testgroup.py
sed -i -- 's/realm.Realm/Realm/g' layer4_test.py lf_atten_mod_test.py lf_multipsk.py lf_sniff_radio.py station_layer3.py test_client_admission.py test_fileio.py test_ip_connection.py
sed -i -- 's/import realm/from realm import Realm, PortUtils/g' lf_ftp.py lf_ftp_test.py lf_webpage.py
sed -i -- 's/import realm/from realm import Realm, WifiMonitor/g' test_ipv4_ps.py
sed -i -- 's/import l3_cxprofile/from l3_cxprofile import L3CXProfile/g' test_l3_powersave_traffic.py
sed -i -- 's/import realm/from realm import Realm, StationProfile, WifiMonitor/g' test_l3_powersave_traffic.py
sed -i -- 's/import realm/from realm import Realm, PacketFilter/g' tip_station_powersave.py
sed -i -- 's/from generic_cx import GenericCx/ /g' *.py
sed -i -- 's/import wlan_theoretical_sta/from wlan_theoretical_sta import abg11_calculator, n11_calculator, ac11_calculator/g' wlan_capacity_calculator.py


sed -i -- 's/from influxdb/from .influxdb/g' *.py
sed -i -- 's/py-scripts/py_scripts/g' *.py
sed -i -- 's/py-json/py_json/g' *.py
sed -i -- 's/py-dashboard/py_dashboard/g' *.py

# fix py_dashboard files
sed -i -- 's/from GrafanaRequest/from ..py_dashboard.GrafanaRequest/g' *.py
sed -i -- 's/from InfluxRequest/from ..py_dashboard.InfluxRequest/g' *.py
sed -i -- 's/from GhostRequest/from ..py_dashboard.GhostRequest/g' *.py

#fix py_json files
sed -i -- 's/from LANforge/from ..py_json.LANforge/g' *.py
sed -i -- 's/from realm/from ..py_json.realm/g' *.py
sed -i -- 's/from cv_test_manager/from ..py_json.cv_test_manager/g' *.py
sed -i -- 's/import LANforge/import ..py_json.LANforge/g' *.py

#fix py_scripts files
sed -i -- 's/from lf_report/from .lf_report/g' *.py
sed -i -- 's/from lf_graph/from .lf_graph/g' *.py
sed -i -- 's/from csv_to_influx/from .csv_to_influx/g' *.py
sed -i -- 's/from csv_to_grafana/from .csv_to_grafana/g' *.py
sed -i -- 's/from grafana_profile/from .grafana_profile/g' *.py
sed -i -- 's/from influx import/from .influx import/g' *.py
sed -i -- 's/import ..py_json.LANforge/ /g' *.py
sed -i -- 's/import realm/from ..py_json import realm /g' example_security_connection.py
sed -i -- 's/import realm/from ..py_json import realm /g' layer3_test.py
sed -i -- 's/from .influxdb/from influxdb/g' *.py
sed -i -- 's/from test_utility/from ..py_json.test_utility/g' *.py
sed -i -- 's/from ftp_html/from .ftp_html/g' *.py
sed -i -- 's/from lf_csv/from .lf_csv/g' *.py
sed -i -- 's/from test_ip_variable_time/from .test_ip_variable_time/g' *.py
sed -i -- 's/from l3_cxprofile/from ..py_json.l3_cxprofile/g' *.py
sed -i -- 's/from create_wanlink/from ..py_json.create_wanlink/g' *.py
sed -i -- 's/from wlan_theoretical_sta/from ..py_json.wlan_theoretical_sta/g' *.py
sed -i -- 's/from ws_generic_monitor/from ..py_json.ws_generic_monitor/g' *.py
sed -i -- 's/from port_utils/from ..py_json.port_utils/g' *.py

cd ../py_json
#Fix files in py_json
sed -i -- 's/import port_utils/from port_utils import PortUtils/g' http_profile.py
sed -i -- 's/import realm/from realm import PortUtils/g' test_utility.py

# fix py_dashboard files
sed -i -- 's/from GrafanaRequest/from ..py_dashboard.GrafanaRequest/g' *.py
sed -i -- 's/from InfluxRequest/from ..py_dashboard.InfluxRequest/g' *.py
sed -i -- 's/from GhostRequest/from ..py_dashboard.GhostRequest/g' *.py

#fix py_json files
sed -i -- 's/from LANforge/from .LANforge/g' *.py
sed -i -- 's/from realm/from .realm/g' *.py
sed -i -- 's/from cv_test_manager/from .cv_test_manager/g' *.py
sed -i -- 's/from lf_cv_base/from .lf_cv_base/g' *.py
sed -i -- 's/from lfdata/from .lfdata/g' *.py
sed -i -- 's/from base_profile/from .base_profile/g' *.py
sed -i -- 's/from test_utility/from .test_utility/g' *.py
sed -i -- 's/import l3_cxprofile2/ /g' *.py
sed -i -- 's/import l3_cxprofile/ /g' *.py
sed -i -- 's/l3_cxprofile2./ /g' *.py
sed -i -- 's/l3_cxprofile./ /g' *.py


# shellcheck disable=SC2039
realmfiles=("l3_cxprofile"
            "l4_cxprofile"
            "lf_attenmod"
            "multicast_profile"
            "http_profile"
            "station_profile"
            "fio_endp_profile"
            "test_group_profile"
            "dut_profile"
            "vap_profile"
            "mac_vlan_profile"
            "wifi_monitor_profile"
            "gen_cxprofile"
            "qvlan_profile"
            "lfdata")
# shellcheck disable=SC2039
for i in "${realmfiles[@]}"; do
str="s/from ${i}/from .${i}/g"
sed -i -- "${str}" realm.py
done
sed -i -- 's/from ..LANforge/from .LANforge/g' realm.py
sed -i -- 's/from port_utils/from .port_utils/g' *.py

#fix py_scripts files
sed -i -- 's/from lf_report/from ..py_scripts.lf_report/g' *.py
sed -i -- 's/from lf_graph/from ..py_scripts.lf_graph/g' *.py
sed -i -- 's/from create_station/from ..py_scripts.create_station/g' *.py
sed -i -- 's/from cv_test_reports/from .cv_test_reports/g' *.py

cd LANforge
sed -i -- 's/from LFRequest import LFRequest/from .LFRequest import LFRequest/g' *.py
sed -i -- 's/from LFRequest/from .LFRequest/g' *.py
sed -i -- 's/from LANforge import LFRequest/import .LFRequest/g' LFUtils.py
sed -i -- 's/from LFUtils/from .LFUtils/g' *.py
sed -i -- 's/from LANforge.LFUtils/from .LFUtils/g' *.py
sed -i -- 's/from LANforge import LFRequest/from . import LFRequest/g' *.py
sed -i -- 's/import LANforge/import /g' *.py
sed -i -- 's/import LANforge.LFUtils/from . import LFUtils/g' *.py
sed -i -- 's/import LANforge.LFRequest/ /g' lfcli_base.py
sed -i -- 's/import .LFRequest/from . import LFRequest/g' *.py
sed -i -- 's/import .LFUtils/from . import LFUtils/g' *.py
sed -i -- 's/LANforge.LFUtils./LFUtils./g' *.py


cd ../../py_dashboard
sed -i -- 's/from GrafanaRequest/from .GrafanaRequest/g' *.py
sed -i -- 's/from InfluxRequest/from .InfluxRequest/g' *.py

if [[ ${ARCHIVE} -eq 0 ]]; then
  Archive()
  {
    cd ../..
    tar cvzf lanforge_scripts.tar.gz ${TARGET_DIR}
    zip lanforge_scripts.zip ${TARGET_DIR}
  }
fi