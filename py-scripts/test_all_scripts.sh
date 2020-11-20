#!/bin/bash
#Security connection examples#########################################
echo "Beginning example_wpa_connection.py test..."
chmod +x example_wpa2_connection.py
./example_wpa2_connection.py --num_stations 3 --ssid jedway-r8000-36 --passwd jedway-r8000-36 --radio wiphy0
chmod +x scenario.py
./scenario.py --load BLANK
chmod +x example_wep_connection.py
./example_wep_connection.py --ssid jedway-wep-48 --passwd jedway-wep-48 --radio wiphy1 
./scenario.py --load BLANK
chmod +x example_wpa3_connection.py
./example_wpa3_connection.py 
./scenario.py --load BLANK
chmod +x example_wpa_connection.py
./example_wpa_connection.py --radio wiphy1
./scenario.py --load BLANK
#test generic and test fileio######################################################
#chmod +x test_fileio.py
#./test_fileio.py
chmod +x test_generic.py
#lfping
./test_generic.py --num_stations 3 --ssid jedway-r8000-36 --passwd jedway-r8000-36 --radio wiphy0
#lfcurl
./test_generic.py --num_stations 3 --ssid jedway-r8000-36 --passwd jedway-r8000-36 --radio wiphy0
#generic
./test_generic.py --num_stations 3 --ssid jedway-r8000-36 --passwd jedway-r8000-36 --radio wiphy0
#speedtest
./test_generic.py --num_stations 3 --ssid jedway-r8000-36 --passwd jedway-r8000-36 --radio wiphy0
#iperf3
./test_generic.py --num_stations 3 --ssid jedway-r8000-36 --passwd jedway-r8000-36 --radio wiphy0
#Ipv4 connection tests##########################################
chmod +x test_ipv4_connection.py
./test_ipv4_connection.py  
chmod +x test_ipv4_l4_ftp_upload.py
./test_ipv4_l4_ftp_upload.py
chmod +x test_ipv4_l4_ftp_urls_per_ten.py
./test_ipv4_l4_ftp_urls_per_ten.py
chmod +x test_ipv4_l4_ftp_wifi.py
./test_ipv4_l4_ftp_wifi.py
chmod +x test_ipv4_l4_urls_per_ten.py
./test_ipv4_l4_urls_per_ten.py  
chmod +x test_ipv4_l4_wifi.py
./test_ipv4_l4_wifi.py 
chmod +x test_ipv4_l4
./test_ipv4_l4.py
chmod +x test_ipv4_ps.py
./test_ipv4_l4_ps.py  
chmod +x test_ipv4_ttls.py
./test_ipv4_l4_ttls.py 
chmod +x test_ipv4_variable_time.py
./test_ipv4_variable_time.py
#Layer 3 tests################################################
chmod +x test_l3_longevity.py
./test_l3_longevity.py 
chmod +x test_l3_powersave_traffic
./test_l3_powersave_traffic.py
chmod +x test_l3_scenario_traffic.py
./test_l3_scenario_traffic.py  
chmod +x test_l3_unicast_traffic_gen.py
./test_l3_unicast_traffic_gen.py
chmod +x test_l3_WAN_LAN.py
./test_l3_WAN_LAN.py
#WANlink######################################################
chmod +x test_wanlink.py
./test_wanlink.py
#IPv6 connection tests########################################
chmod +x test_ipv6_connection.py
./test_ipv6_variable_connection.py
chmod +x test_ipv6_variable_time.py
./test_ipv6_variable_time.py
#STA Connect examples#########################################
chmod +x sta_connect_example.py
./sta_connect_example.py  
chmod +x sta_connect_multi_example.py
./sta_connect_multi_example.py 
chmod +x sta_connect.py
./sta_connect.py
chmod +x sta_connect2.py
./sta_connect2.py 
