#!/bin/bash
set -e
unset proxy
unset http_proxy
Q='"'
q="'"
S='*'
application_json="application/json"
accept_json="Accept: $application_json"
accept_html='Accept: text/html'
accept_text='Accept: text/plain'
#accept_any="'Accept: */*'" # just dont use
content_plain='Content-Type: text/plain'
content_json="Content-Type: $application_json"
switches='-sqv'
#switches='-sq'
data_file=/var/tmp/data.$$

function Kurl() {
   echo "======================================================================================="
   echo "curl $switches $@"
   echo "======================================================================================="
   curl $switches "$@" | json_pp
   echo ""
   echo "======================================================================================="
}

function Jurl() {
   echo "=J====================================================================================="
   echo "curl $switches -H $accept_json -H $content_json $@"
   echo "=J====================================================================================="
   curl $switches -H "$accept_json" -H "$content_json" -X POST "$@"
   echo ""
   echo "=J====================================================================================="
}

#url="http://jed-f24m64-9119:8080"
url="http://127.0.0.1:8080"

function PortDown() {
   echo "{\"shelf\":1,\"resource\":3,\"port\":\"$1\",\"current_flags\":1, \"interest\":8388610}" > $data_file
   curl $switches -H "$accept_json" -H "$content_json" -X POST  -d"@$data_file" "$url/cli-json/set_port" || :
   sleep 0.3
   for f in `seq 1 10`; do
      echo "{\"shelf\":1,\"resource\":3,\"port\":\"$1\"}" > $data_file
      curl $switches -H "$accept_json" -H "$content_json" -X POST -d"@$data_file" "$url/cli-json/nc_show_ports" || :
      sleep 0.5 
      curl $switches "$url/port/1/3/$1?fields=alias,ip,down" | json_pp > /var/tmp/result
      grep '"down" : true' /var/tmp/result && break || :
   done
}

function PortUp() {
   #set_port 1 3 sta3101 NA NA NA NA 0 NA NA NA NA 8388610
   echo "{\"shelf\":1,\"resource\":3,\"port\":\"$1\",\"current_flags\":0, \"interest\":8388610}" > $data_file
   curl $switches -H "$accept_json" -H "$content_json" -X POST  -d"@$data_file" "$url/cli-json/set_port"
   sleep 1 
   for f in `seq 1 100`; do
      echo "{\"shelf\":1,\"resource\":3,\"port\":\"$1\"}" > $data_file
      #Jurl -d"@$data_file" "$url/cli-json/nc_show_ports"
      curl $switches -H "$accept_json" -H "$content_json" -X POST -d"@$data_file" "$url/cli-json/nc_show_ports"
      sleep 0.5 
      curl $switches "$url/port/1/3/$1?fields=alias,ip,down" | json_pp > /var/tmp/result || :
      #cat /tmp/result
      grep '"down" : false' /var/tmp/result && break || :
   done
}

function CxToggle() {
   echo "{\"test_mgr\":\"all\",\"cx_name\":\"$1\",\"cx_state\":\"$2\"}" > $data_file
   curl $switches -H "$accept_json" -H "$content_json" -X POST  -d"@$data_file" "$url/cli-json/set_cx_state" || :
}

while true; do
   for eidcx in `seq 40 61` ; do
      CxToggle "$eidcx" "STOPPED"
      curl $switches  -H "$accept_json" "$url/endp/$eidcx?fields=name,run"
   done
   for sta in `seq 100 121`; do
      stb=$(( $sta + 3000))
      PortDown "sta$stb"
   done
   for sta in `seq 100 121`; do
      stb=$(( $sta + 3000))
      PortUp "sta$stb"
   done
   sleep 4
   for eidcx in 34 35 36 37 38 39 ; do
      CxToggle "$eidcx" "RUNNING"
      curl $switches  -H "$accept_json" "$url/endp/$eidcx?fields=name,run" || :
   done
   sleep 14
done

#
