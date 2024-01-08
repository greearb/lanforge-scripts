#!/bin/bash
Q='"'
A="'"
function set_background() {
   gsettings set "org.mate.background" "$1" "$2"
}
. /etc/os-release
SourceFile="/usr/share/backgrounds/mate/desktop/Ubuntu-Mate-Cold-no-logo.png"
# desktop.svg is cached as a png I think and does not change notably.
# randomizing the name would force a change
_R="${RANDOM}dt${RANDOM}"
DesktopFile="/home/lanforge/Pictures/desktop-${_R}.svg"
my_version=`cat /var/www/html/installed-ver.txt`
my_hostname=`hostname`
my_dev=`ip ro sho | awk '/default via/{print $5}'`
my_ip=`ip a sho $my_dev | awk '/inet /{print $2}'`
my_mac=`ip a sho | grep -A1 "$my_dev" | awk '/ether /{print $2}'`
my_os="$PRETTY_NAME"
my_realm=`awk '/^realm / {print $2}' /home/lanforge/config.values`
my_resource=`awk '/^first_client / {print $2}' /home/lanforge/config.values`
my_mode=`awk '/^mode / {print $2}' /home/lanforge/config.values`
my_lfver=`cat /var/www/html/installed-ver.txt`
my_greeting_f="/tmp/greeting.txt"

my_build="-"
if [[ -f $my_greeting_f ]]; then
    my_build=`grep 'Compiled on: ' $my_greeting_f`
    my_build="${my_build#*Compiled on: }"
fi
#echo "BUILD: $my_build"

fill_color=${my_mac//:/}
fill_color=${fill_color:6:12}
X=220
Y=150

if (( $my_realm == 255 )); then
    my_realm="Stand Alone"
else
    my_realm="Realm $my_realm"
fi
#convert -pointsize 80 -fill "#$fill_color" -stroke black -strokewidth 1 \
#  -draw "text $X,$Y \"$my_hostname\"" \
#  -draw "text $X,$(( Y + 75 )) \"$my_dev $my_ip\"" \
#  -draw "text $X,$(( Y + 150 )) \"$my_mac\"" \
#  $SourceFile \
#  -scale 1600x900 \
#  $DesktopFile

#    font-family: 'Source Code Pro', 'FreeMono', 'Liberation Mono', 'DejaVu Sans Mono', 'Lucida Sans Typewriter', 'Consolas',  mono, sans-serif;

imgtag=""
ANV="/home/lanforge/Pictures/anvil-right.svg"
if [ -r "$ANV" ] ; then
    imgtag="<image x='400' y='200' width='800' height='450' href='$ANV' />"
fi

cat > $DesktopFile <<_EOF_
<svg viewBox='0 0 1601 901' width='1600' height='900' xmlns='http://www.w3.org/2000/svg'>
<style>
text {
    fill: #$fill_color;
    stroke: rgba(4, 64, 4, 64);
    stroke-width: 1px;
    text-anchor: left;
    font-size: 34px;
    font-family: 'Consolas, DejaVu Sans Mono, Liberation Mono, Nimbus Mono, fixed';
    font-weight: bold;
    opacity: 0.8;
}
#bgrec {
    fill: gray;
    opacity: 0.5;
    stroke-width: 6px;
    stroke: rgba(50, 50, 50, 255);
}
</style>
<g>
    <rect id='bgrec' x='260' y='80' rx='10' ry='10' width='901px' height='351px'>
    </rect>
    <g>
        <text x='270' y='120'>LANforge $my_lfver $my_hostname</text>
        <text x='270' y='160'>Build: $my_build</text>
        <text x='270' y='200'>$my_realm Resource 1.$my_resource</text>
        <text x='270' y='240'>$my_dev $my_ip</text>
        <text x='270' y='280'>$my_os</text>
        <text x='270' y='320'>$my_mac</text>
    </g>
</g>
</svg>
_EOF_
touch "$DesktopFile"
set_background picture-filename ${A}${DesktopFile}${A}
set_background picture-options  'stretched'
#
