#!/bin/bash
##########################
# Help
##########################
Help()
{
  echo "This bash script creates a DUT, loads a scenario, runs a WiFi Capacity test, and saves it to Influx"
}

#Replace my arguments with your setup.  Separate your ssid arguments with spaces and ensure the names are lowercase
echo "Make new DUT"
./create_chamberview_dut.py --lfmgr 192.168.1.7 --dut_name DUT_TO_GRAFANA_DUT --ssid "ssid_idx=0 ssid=lanforge security=WPA2 password=password bssid=04:f0:21:2c:41:84 traffic=wiphy1"

echo "Build Chamber View Scenario" #change the lfmgr to your system, set the radio to a working radio on your LANforge system, same with the ethernet port.
./create_chamberview.py --lfmgr 192.168.1.7 --create_scenario DUT_TO_GRAFANA_SCENARIO --line "Resource=1.1 Profile=default Amount=32 Uses-1=wiphy1 DUT=DUT_TO_GRAFANA_DUT Traffic=wiphy1 Freq=-1" --line "Resource=1.1 Profile=upstream Amount=1 Uses-1=eth1 DUT=DUT_TO_GRAFANA_DUT Traffic=eth1 Freq=-1"

#config_name doesn't matter, change the influx_host to your LANforge device,
echo "run wifi capacity test"
./lf_wifi_capacity_test.py --config_name Custom --create_stations --radio wiphy1 --pull_report --influx_host 192.168.1.7 --influx_port 8086 --influx_org Candela --influx_token Tdxwq5KRbj1oNbZ_ErPL5tw_HUH2wJ1VR4dwZNugJ-APz__mEFIwnqHZdoobmQpt2fa1VdWMlHQClR8XNotwbg== --influx_bucket lanforge --mgr 192.168.1.7 --instance_name testing --upstream eth1
