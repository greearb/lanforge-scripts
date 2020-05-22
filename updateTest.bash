#!/bin/bash
export DISPLAY=:1

GUILog="/home/lanforge/Documents/GUILog.txt"
GUIUpdate="/home/lanforge/Documents/GUIUpdateLog.txt"
CTLGUI="/home/lanforge/Documents/connectTestGUILog.txt"
CTLH="/home/lanforge/Documents/connectTestHLog.txt"
verNum="5.4.2"

python3 /home/lanforge/Documents/lanforge-scripts/auto-install-gui.py --versionNumber $verNum &> $GUIUpdate

grep -q "Current GUI version up to date" $GUIUpdate && exit

python3 /home/lanforge/Documents/lanforge-scripts/connectTest.py &> $CTLGUI

pgrep java | xargs kill

/home/lanforge/LANforgeGUI_5.4.2/lfclient.bash -daemon -s localhost &> $GUILog &
python3 /home/lanforge/Documents/lanforge-scripts/connectTest.py &> $CTLH

echo "Logs Attached" | mail -s 'GUI Update Logs' -a $GUILog -a $GUIUpdate -a $CTLGUI -a $CTLH  test.notice@candelatech.com
