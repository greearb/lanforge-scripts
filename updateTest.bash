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

for f in $GUILog $GUIUpdate $CTLGUI $CTLH; do rm -f $f; done

python3 ${scripts}/auto-install-gui.py --versionNumber $verNum &> $GUIUpdate
sleep 5
grep -q "Current GUI version up to date" $GUIUpdate && exit

python3 ${scripts}/connectTest.py &> $CTLGUI
sleep 1
pgrep java | xargs kill
sleep 1

${HL}/LANforgeGUI_5.4.2/lfclient.bash -daemon -s localhost &> $GUILog &
sleep 5
python3 ${scripts}/connectTest.py &> $CTLH
sleep 1

echo "Logs Attached" | mail -s 'GUI Update Logs' -a $GUILog -a $GUIUpdate -a $CTLGUI -a $CTLH  "test.notice@candelatech.com"
