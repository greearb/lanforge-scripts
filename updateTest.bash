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

rm -f $GUILog $GUIUpdate $CTLGUI $CTLH $ST

touch "${HL}/LANforgeGUI_${verNum}/NO_AUTOSTART"
python3 ${scripts}/auto-install-gui.py --versionNumber $verNum &> $GUIUpdate
sleep 5
grep -q "Current GUI version up to date" $GUIUpdate && exit
grep -q -i "fail" $GUIUpdate && exit

pgrep java &>/dev/null && killall -9 java
rm "${HL}/LANforgeGUI_${verNum}/NO_AUTOSTART"

( cd $GUIDIR; nohup env RESTARTS=999999 ./lfclient.bash -s localhost &> $GUILog & )
sleep 10
python3 ${scripts}/connectTest.py &> $CTLGUI

touch "${HL}/LANforgeGUI_${verNum}/DAEMON_MODE"
pgrep java &>/dev/null && killall -9 java
sleep 10
python3 ${scripts}/connectTest.py &> $CTLH
rm "${HL}/LANforgeGUI_${verNum}/DAEMON_MODE"

pgrep java &>/dev/null && killall -9 java

echo "===============================================" > $ST
head $GUILog >> $ST
echo "===============================================" >> $ST
head $GUIUpdate >> $ST
echo "===============================================" >> $ST
head $CTLGUI >> $ST
echo "===============================================" >> $ST
head $CTLH >> $ST
echo "===============================================" >> $ST

cat $ST | mail -s 'GUI Update Test' -a $GUILog -a $GUIUpdate -a $CTLGUI -a $CTLH  "test.notice@candelatech.com"

