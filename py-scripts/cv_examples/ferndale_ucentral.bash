#!/bin/bash

# This bash script creates/updates a DUT, creates/updates a chamberview scenario,
# loads and builds that scenario, runs wifi capacity test, and saves the kpi.csv info
# into influxdb.  As final step, it builds a grafana dashboard for the KPI information.

# Define some common variables.  This will need to be changed to match your own testbed.
# LANforge GUI machine
#MGR=192.168.100.209
MGR=localhost
INFLUXTOKEN=-u_Wd-L8o992701QF0c5UmqEp7w7Z7YOMaWLxOMgmHfATJGnQbbmYyNxHBR9PgD6taM_tcxqJl6U8DjU1xINFQ==
TESTBED=Ferndale-01
GRAFANATOKEN=eyJrIjoiVXVyZ0dQSXlNdGlQNGQ1R282S2p6SE1PZXJVOVpvM1UiLCJuIjoiYmVuLWdyYWZhbmEiLCJpZCI6MX0=
GROUPS=/tmp/lf_cv_rpt_filelocation.txt
DUT=linksys-8450

# Create/update new DUT.
#Replace my arguments with your setup.  Separate your ssid arguments with spaces and ensure the names are lowercase
echo "Make new DUT"
./create_chamberview_dut.py --lfmgr ${MGR} --dut_name ${DUT} \
  --ssid "ssid_idx=0 ssid=Default-SSID-2g security=WPA2 password=12345678 bssid=c4:41:1e:f5:3f:24" \
  --ssid "ssid_idx=1 ssid=Default-SSID-5gl security=WPA2 password=12345678 bssid=c4:41:1e:f5:3f:25" \
  --sw_version "ucentral-01" --hw_version ea8450 --serial_num 1001 --model_num 8450

exit 0

# Create/update chamber view scenario and apply and build it.
echo "Build Chamber View Scenario"
#change the lfmgr to your system, set the radio to a working radio on your LANforge system, same with the ethernet port.
./create_chamberview.py --lfmgr ${MGR} --create_scenario DUT_TO_GRAFANA_SCENARIO \
--line "Resource=1.1 Profile=default Amount=32 Uses-1=wiphy1 DUT=DUT_TO_GRAFANA_DUT Traffic=wiphy1 Freq=-1" \
--line "Resource=1.1 Profile=upstream Amount=1 Uses-1=eth1 DUT=DUT_TO_GRAFANA_DUT Traffic=eth1 Freq=-1"

# Run capacity test on the stations created by the chamber view scenario.
# Submit the KPI data into the influxdb.
#config_name doesn't matter, change the influx_host to your LANforge device,
echo "run wifi capacity test"
./lf_wifi_capacity_test.py --config_name Custom --create_stations --radio wiphy1 --pull_report --influx_host ${MGR} \
--influx_port 8086 --influx_org Candela --influx_token  ${INFLUXTOKEN} --influx_bucket lanforge --mgr ${MGR} \
--instance_name testing --upstream eth1 --test_rig ${TESTBED} --graphgroups ${GROUPS}

# Build grafana dashboard and graphs view for the KPI in the capacity test.
./grafana_profile.py --create_custom --title ${TESTBED} --influx_bucket lanforge --mgr 192.168.1.7 --grafana_token ${GRAFANATOKEN} \
--grafana_host 192.168.1.7 --testbed ${TESTBED} --graph-groups  ${GROUPS} --scripts Dataplane --scripts 'WiFi Capacity'

rm ${GROUPS}
