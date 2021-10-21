#!/bin/bash
Q='"'
A="'"
function set_background() {
   gsettings set "org.mate.background" "$1" "$2"
}

SourceFile="/usr/share/backgrounds/mate/desktop/Ubuntu-Mate-Cold-no-logo.png"
DesktopFile="/home/lanforge/desktop.png"
my_version=`cat /var/www/html/installed-ver.txt`
my_hostname=`hostname`
my_dev=`ip ro sho | awk '/default via/{print $5}'`
my_ip=`ip ro sho | awk '/default via/{print$3}'`
my_mac=`ip a sho | grep -B1 "$my_dev" | awk '/ether /{print $2}'`

X=220
Y=150
convert -pointsize 80 -fill cyan \
  -draw "text $X,$Y \"$my_hostname\"" \
  -draw "text $X,$(( Y + 75 )) \"$my_dev $my_ip\"" \
  -draw "text $X,$(( Y + 150 )) \"$my_mac\"" \
  $SourceFile \
  -scale 1600x900 \
  $DesktopFile

set_background picture-filename ${A}${DesktopFile}${A}
set_background picture-options  'stretched'
#
