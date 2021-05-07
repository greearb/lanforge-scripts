#!/bin/bash
##########################
# Help
##########################
Help()
{
  echo "This bash script creates a DUT, loads a scenario, runs a WiFi Capacity test, and saves it to Influx"
}
MGR=192.168.1.7
INFLUXTOKEN=Tdxwq5KRbj1oNbZ_ErPL5tw_HUH2wJ1VR4dwZNugJ-APz__mEFIwnqHZdoobmQpt2fa1VdWMlHQClR8XNotwbg==
GRAFANATOKEN=eyJrIjoiZTJwZkZlemhLQVNpY3hiemRjUkNBZ3k2RWc3bWpQWEkiLCJuIjoibWFzdGVyIiwiaWQiOjF9
TESTBED=Stidmatt-01
GROUPS=/tmp/lf_cv_rpt_filelocation.txt
#Replace my arguments with your setup.  Separate your ssid arguments with spaces and ensure the names are lowercase
echo "Make new DUT"
./create_chamberview_dut.py --lfmgr ${MGR} --dut_name DUT_TO_GRAFANA_DUT --ssid "ssid_idx=0 ssid=lanforge security=WPA2 password=password bssid=04:f0:21:2c:41:84 traffic=wiphy1"

echo "Build Chamber View Scenario" #change the lfmgr to your system, set the radio to a working radio on your LANforge system, same with the ethernet port.
./create_chamberview.py --lfmgr ${MGR} --create_scenario DUT_TO_GRAFANA_SCENARIO \
--line "Resource=1.1 Profile=default Amount=32 Uses-1=wiphy1 DUT=DUT_TO_GRAFANA_DUT Traffic=wiphy1 Freq=-1" \
--line "Resource=1.1 Profile=upstream Amount=1 Uses-1=eth1 DUT=DUT_TO_GRAFANA_DUT Traffic=eth1 Freq=-1"

#config_name doesn't matter, change the influx_host to your LANforge device,
echo "run Dataplane test"
./lf_dataplane_test.py --mgr ${MGR} --instance_name dataplane-instance --config_name test_config --upstream 1.1.eth1 \
--station 1.1.14 --dut linksys-8450 --influx_host ${MGR} --influx_port 8086 --influx_org Candela --influx_token ${INFLUXTOKEN} \
--influx_bucket lanforge --influx_tag testbed ${TESTBED} --graphgroups ${GROUPS}

./grafana_profile.py --create_custom --title ${TESTBED} --influx_bucket lanforge --mgr 192.168.1.7 --grafana_token ${GRAFANATOKEN} \
--grafana_host 192.168.1.7 --testbed ${TESTBED} --graph-groups ${GROUPS} \
--scripts Dataplane --scripts 'WiFi Capacity'
