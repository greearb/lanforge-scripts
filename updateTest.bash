#!/bin/bash
# check for log file
LOCKFILE="/tmp/update-test.lock"
[ -f $LOCKFILE ] && echo "lockfile $LOCKFILE found, bye" && exit 0

export DISPLAY=:1
[ ! -z "$DEBUG" ] && set -x
IP="192.168.95.239"
HL="/home/lanforge"
HLD="${HL}/Documents"
scripts="${HLD}/lanforge-scripts"
verNum="5.4.3"
GUILog="/home/lanforge/Documents/GUILog.txt"
GUIUpdate="/home/lanforge/Documents/GUIUpdateLog.txt"
CTLGUI="/home/lanforge/Documents/connectTestGUILog.txt"
CTLH="/home/lanforge/Documents/connectTestHLog.txt"
GUIDIR="${HL}/LANforgeGUI_${verNum}"
ST="/tmp/summary.txt"
DM_FLAG="${HL}/LANforgeGUI_${verNum}/DAEMON_MODE"
output=/tmp/gui_update_test

trap do_sigint ABRT
trap do_sigint INT 
trap do_sigint KILL
trap do_sigint PIPE
trap do_sigint QUIT
trap do_sigint SEGV
trap do_sigint TERM

function do_sigint() {
   [ -f $LOCKFILE ] && echo "removing lockfile" && rm -f $LOCKFILE
   for f in $GUILog $GUIUpdate $CTLGUI $CTLH /tmp/\+.*; do
      rm -f "$f"
   done
}
function start_gui() {
   daemon_mode=""
   [ -f $GUIDIR/DAEMON_MODE ] && daemon_mode="-daemon"
   ( cd $GUIDIR; nohup env RESTARTS=999999 ./lfclient.bash $daemon_mode -s localhost &> $GUILog & )
   connect_fail=0
   wait_8080 || connect_fail=1

   if [[ $connect_fail = 1 ]]; then
     echo "" > $output
     [ -s $GUIUpdate ] && cat $GUIUpdate >> $output
     cat $GUILog >> $output
     mail -s 'GUI connect failure' "test.notice@candelatech.com" -q $output
     exit 1
   fi
}

function wait_8080() {
   set +x
   local connected=0
   local limit_sec=30
   echo "Testing for 8080 connection "
   while (( connected == 0 )); do
      (( limit_sec <= 0)) && break
      curl -so /dev/null http://localhost:8080/ && connected=1
      (( connected >= 1 )) && break;
      limit_sec=$(( limit_sec - 1 ))
      echo -n "."
      sleep 1
   done
   if [[ $connected = 0 ]]; then
      echo "Unable to connect, bye"
      return 1
   fi
   [ ! -z "$DEBUG" ] && set -x
}

touch $LOCKFILE

if [ -f ${GUIDIR}/down-check ]; then 
   numFound=`find ${GUIDIR} -name down-check -mmin +59 | grep -c down-check`

   if (( numFound >= 1 )); then
     ping -c2 -i1 -nq -w4 -W8 ${IP}
     if (( 0 == $? )); then
       rm "${GUIDIR}/down-check"
     else
       touch "${GUIDIR}/down-check"
       echo "Could not connect to ${IP}"
       exit 1
     fi
   else
     ping -c2 -i1 -nq -w4 -W4 ${IP}
     if (( 0 != $? )); then
       touch "${GUIDIR}/down-check"
       echo "Could not connect to ${IP}"
       exit 1
     fi
   fi
fi

sudo rm -f /tmp/*.txt
sudo rm -f $GUILog $GUIUpdate $CTLGUI $CTLH $ST

touch "${HL}/LANforgeGUI_${verNum}/NO_AUTOSTART"
pgrep java &>/dev/null && killall -9 java
touch $GUIUpdate
touch $ST
if [ ! -z "SKIP_INSTALL" ] && [ x$SKIP_INSTALL = x1 ]; then
   echo "skipping installation"
   sleep 4
else
   echo "doing installation"
   sleep 4
   python3 ${scripts}/auto-install-gui.py --versionNumber $verNum &> $GUIUpdate
   [ -s $GUIUpdate ] && grep -q "Current GUI version up to date" $GUIUpdate && exit
   [ -s $GUIUpdate ] && head $GUIUpdate >> $ST
   if grep -q -i "fail" $GUIUpdate; then
     cat $ST | mail -s 'GUI Update Test Failure' -a $GUILog -a $GUIUpdate "test.notice@candelatech.com"
     exit 1
   fi
fi
sleep 1
rm -f "${HL}/LANforgeGUI_${verNum}/NO_AUTOSTART"

start_gui
python3 ${scripts}/connectTest.py &> $CTLGUI
echo "== GUI =============================================" >> $ST
head $CTLGUI >> $ST
echo "===============================================" >> $ST
pgrep java &>/dev/null && killall -9 java
sleep 1

#-daemon
touch "${HL}/LANforgeGUI_${verNum}/DAEMON_MODE"
start_gui
python3 ${scripts}/connectTest.py &> $CTLH

echo "== HEADLESS =============================================" >> $ST
head $CTLH >> $ST
echo "===============================================" >> $ST
rm -f "${HL}/LANforgeGUI_${verNum}/DAEMON_MODE"
pgrep java &>/dev/null && killall -9 java
start_gui
connect_fail=0
wait_8080 || connect_fail=1

cat $ST > $output
echo "=== FULL LOGS ============================================" >> $output
[ -s $GUILog ] && cat $GUILog >> $output
echo "===============================================" >> $output
[ -s $GUIUpdate ] && cat $GUIUpdate >> $output
echo "===============================================" >> $output
[ -s $CTLGUI ] && cat $CTLGUI >> $output
echo "===============================================" >> $output
[ -s $CTLH ] && cat $CTLH >> $output
echo "===============================================" >> $output
echo -e "--\n.\n" >> $output

mail -s 'GUI Update Test' "test.notice@candelatech.com" -q $output

#cat $ST | mail -s 'GUI Update Test' -a $GUILog -a $GUIUpdate -a $CTLGUI -a $CTLH  "test.notice@candelatech.com"
#eof
