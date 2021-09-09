#! /bin/bash

rm -r 2021*
mv py-scripts py_scripts
mv py-json py_json
mv py-dashboard py_dashboard
rm *.pl
rm -r json
rm -r gui
rm -r LANforge

#fix files in root
sed -i -- 's/from LANforge/from py_json.LANforge/g' *.py
sed -i -- 's/from py_json/from .py_json/g' *.py

cd py_scripts
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

cd ../py_json
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

cd ../../py_dashboard
sed -i -- 's/from GrafanaRequest/from .GrafanaRequest/g' *.py
sed -i -- 's/from InfluxRequest/from .InfluxRequest/g' *.py
