#!/bin/bash
unset proxy
unset http_proxy
set -x
set -e
ajson_h="Accept: application/json"
cjson_h="Content-type: application/json"

R=8
W=wiphy0
M=8000
N=8050
SSID="idtest-1100-wpa2"
KEY="idtest-1100-wpa2"

for n in `seq $M $N`; do
   echo "shelf=1&resource=$R&port=sta$n" > /tmp/curl_data
   curl -sqv -H "$ajson_h" -X POST -d '@/tmp/curl_data' http://localhost:8080/cli-form/rm_vlan ||:
done
sleep 2
for n in `seq $M $N`; do
   echo "shelf=1&resource=$R&radio=$W&sta_name=sta$n&flags=0x400&ssid=$SSID&key=$KEY&mac=xx:xx:xx:xx:*:*" > /tmp/curl_data
   curl -sqv -H 'Accept: application/json' -X POST -d '@/tmp/curl_data' http://localhost:8080/cli-form/add_sta ||:
done
sleep 3
for n in `seq $M $N`; do
   curl -sqv -H "$ajson_h" -X GET -o /tmp/response "http://localhost:8080/port/1/$R/sta$n"
   #if [ -s /tmp/response ]; then
   #   json_pp < /tmp/response
   #fi
done
exit

echo 'shelf=1&resource=3&port=sta3100' > /tmp/curl_data
curl -sqv -H "$ajson_h" -X POST -d '@/tmp/curl_data' http://localhost:8080/cli-form/rm_vlan

sleep 1
echo 'shelf=1&resource=3&radio=wiphy1&sta_name=sta3100&flags=1024&ssid=idtest-1100-wpa2&nickname=sta3100&key=idtest-1100-wpa2&mac=XX:XX:XX:XX:*:*&flags_mask=1024' > /tmp/curl_data
curl -sqv -H "$ajson_h" -X POST -d '@/tmp/curl_data' http://localhost:8080/cli-form/add_sta


sleep 1
rm -f /tmp/response
curl -sqv -H "$ajson_h" -X GET -o /tmp/response http://localhost:8080/port/1/3/sta3100
if [ -s /tmp/response ]; then
   json_pp < /tmp/response
fi

sleep 2
echo '{"shelf":1,"resource":3,"port":"sta3100"}' > /tmp/curl_data
curl -sqv -H "$ajson_h" -H "$cjson_h" -X POST -d '@/tmp/curl_data' http://localhost:8080/cli-json/rm_vlan

sleep 2
echo '{"shelf":1,"resource":3,"radio":"wiphy1","sta_name":"sta3100","flags":1024,"ssid":idtest-1100-wpa2","nickname":"sta3100","key":"idtest-1100-wpa2","mac":"XX:XX:XX:XX:*:XX","flags_mask":1024}' > /tmp/curl_data
curl -sqv -H "$ajson_h" -H "$cjson_h" -X POST -d '@/tmp/curl_data' http://localhost:8080/cli-json/add_sta

sleep 1
rm -f /tmp/response
curl -sqv -H "$ajson_h" -X GET -o /tmp/response http://localhost:8080/port/1/3/sta3100
if [ -s /tmp/response ]; then
   json_pp < /tmp/response
fi


#
