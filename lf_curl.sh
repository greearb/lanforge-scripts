#!/bin/bash
[ -f /home/lanforge/lanforge.profile ] && . /home/lanforge/lanforge.profile
CURL=`which curl`;
#echo $CURL;

SOURCE_IP=""
SOURCE_PORT=""
DEST_HOST=""
OUT_FILE=/dev/null
NUM_LOOPS=1

help="$0 options:
      -d {destination_url}
      -h this help
      -i {source ip}
      -n {number of times, 0 = infinite}
      -o {output file prefix, /dev/null is default}
      -p {source port}
E.G.:      
   $0 -i 10.0.0.1 -p eth1 -o /tmp/output -d http://example.com/
becomes
   curl -sqLk --interface 10.0.0.1 -o /tmp/output_eth1 http://example.com/
   
Best if used from lf_generic_ping.pl to construct commands referencing this script:
   ./lf_generic_ping.pl --mgr cholla-f19 -r 2 -n curl_ex_ --match 'eth2#' --cmd 'lf_curl.sh -o /tmp/curl_%p.out -i %i -d %d -p %p' --dest http://localhost/
"

while getopts ":d:hi:n:o:p:" OPT ; do
   #echo "OPT[$OPT] OPTARG[$OPTARG]"
   case $OPT in
   h)
      echo $help
      exit 0
      ;;
   d)
      DEST_HOST="$OPTARG"
      ;;
   i)
      if [[ $CURL = ~/local/bin/curl ]]; then
         SOURCE_IP="--dns-ipv4-addr $OPTARG --interface $OPTARG"
      else
         SOURCE_IP="--interface $OPTARG"
      fi
      ;;
   n)
      NUM_LOOPS=$OPTARG
      ;;
   o)
      OUT_FILE="$OPTARG"
      ;;
   p)
      SOURCE_PORT="--interface $OPTARG"
      ;;
   *)
      echo "Unknown option [$OPT] [$OPTARG]"
      ;;
   esac
done

if [[ -z "$DEST_HOST" ]]; then
   echo "$help"
   exit 1
fi

if [[ x$OUT_FILE != x/dev/null ]] && [[ x$SOURCE_PORT != x ]] ; then
   OUT_FILE="-o ${OUT_FILE}_${SOURCE_PORT}"
fi

NUM_GOOD=0

for N in `seq 1 $NUM_LOOPS`; do
   $CURL -sqLk --connect-timeout 1 \
      --max-time 10 \
      -D /tmp/lf_curl_h.$$ \
      $OUT_FILE \
      $SOURCE_IP \
      $DEST_HOST \
      > /tmp/lf_curl_so.$$ \
      2> /tmp/lf_curl_se.$$

   if [[ $? > 0 ]]; then
      echo "Failed $DEST_HOST"
      head -1 /tmp/lf_curl_se.$$
   else
      NUM_GOOD=$(( $NUM_GOOD +1))
      head -1 /tmp/lf_curl_so.$$
      head -1 /tmp/lf_curl_h.$$
   fi
   sleep 1
done
echo "Finished $NUM_LOOPS, $NUM_GOOD successful"
#
