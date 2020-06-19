#!/bin/bash
export DISPLAY=:1

HL="/home/lanforge"
HLD="${HL}/Documents"
scripts="${HLD}/lanforge-scripts"
GUILog="/home/lanforge/Documents/GUILog.txt"
GUIUpdate="/home/lanforge/Documents/GUIUpdateLog.txt"
CTLGUI="/home/lanforge/Documents/connectTestGUILog.txt"
CTLH="/home/lanforge/Documents/connectTestHLog.txt"
verNum="5.4.2"
GUIDIR="${HL}/LANforgeGUI_${verNum}"
ST="/tmp/summary.txt"
IP="192.168.95.239"

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

rm -f /tmp/*.txt
rm -f $GUILog $GUIUpdate $CTLGUI $CTLH $ST

touch "${HL}/LANforgeGUI_${verNum}/NO_AUTOSTART"
pgrep java &>/dev/null && killall -9 java
python3 ${scripts}/auto-install-gui.py --versionNumber $verNum &> $GUIUpdate
sleep 1
rm -f "${HL}/LANforgeGUI_${verNum}/NO_AUTOSTART"
( cd $GUIDIR; nohup env RESTARTS=999999 ./lfclient.bash -s localhost &> $GUILog & )
sleep 10
grep -q "Current GUI version up to date" $GUIUpdate && exit
echo "===============================================" > $ST
head $GUILog >> $ST
echo "===============================================" >> $ST
head $GUIUpdate >> $ST
if grep -q -i "fail" $GUIUpdate; then
  cat $ST | mail -s 'GUI Update Test Failure' -a $GUILog -a $GUIUpdate "test.notice@candelatech.com"
fi

#pgrep java &>/dev/null && killall -9 java
#( cd $GUIDIR; nohup env RESTARTS=999999 ./lfclient.bash -s localhost &> $GUILog & )
python3 ${scripts}/connectTest.py &> $CTLGUI

touch "${HL}/LANforgeGUI_${verNum}/DAEMON_MODE"

pgrep java &>/dev/null && killall -9 java
sleep 10

python3 ${scripts}/connectTest.py &> $CTLH

rm "${HL}/LANforgeGUI_${verNum}/DAEMON_MODE"
pgrep java &>/dev/null && killall -9 java

echo "===============================================" >> $ST
head $CTLGUI >> $ST
echo "===============================================" >> $ST
head $CTLH >> $ST
echo "===============================================" >> $ST

cat $ST | mail -s 'GUI Update Test' -a $GUILog -a $GUIUpdate -a $CTLGUI -a $CTLH  "test.notice@candelatech.com"

