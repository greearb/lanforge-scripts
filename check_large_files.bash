#!/bin/bash
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#  Check for large files and purge many of the most inconsequencial       #
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
# set -x
# set -e

USAGE="$0 # Check for large files and purge many of the most inconsequencial
 -a   # automatic: disable menu and clean automatically
 -b   # remove extra kernels and modules
 -c   # remove all core files
 -d   # remove old LANforge downloads
 -h   # help
 -k   # remove ath10k crash files
 -l   # remove old files from /var/log, truncate /var/log/messages
 -m   # remove orphaned fileio items in /mnt/lf
 -q   # quiet
 -r   # compress .csv data in /home/lanforge
 -t   # remove /var/tmp files
 -v   # verbose

"

eyedee=`id -u`
if (( eyedee != 0 )); then
    echo "$0: Please become root to use this script, bye"
    exit 1
fi

# these are default selections
selections=()
deletion_targets=()
show_menu=1
verbose=0
quiet=0
#opts=""
opts="abcdhklmqrtv"
while getopts $opts opt; do
  case "$opt" in
    a)
      verbose=0
      quiet=1
      selections+=($opt)
      show_menu=0
      ;;
    b)
      selections+=($opt)
      ;;
    c)
      selections+=($opt)
      ;;
    d)
      selections+=($opt)
      ;;
    h)
      echo "$USAGE"
      exit 0
      ;;
    k)
      selections+=($opt)
      ;;
    l)
      selections+=($opt)
      ;;
    m)
      selections+=($opt)
      ;;
    r)
      selections+=($opt)
      ;;
    q)
      quiet=1
      verbose=0
      selections+=($opt)
      ;;
    t)
      selections+=($opt)
      ;;
    v)
      quiet=0
      verbose=1
      selections+=($opt)
      ;;
    *)
      echo "unknown option: $opt"
      echo "$USAGE"
      exit 1
      ;;
  esac
done

if (( ${#selections} < 1 )); then
  echo "$USAGE"
  exit 0
fi

HR=" ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----"
function hr() {
  echo "$HR"
}

# Find core files
core_files=()
cd /
mapfile -t core_files < <(ls /core* /home/lanforge/core* 2>/dev/null)

# Find ath10k crash residue
ath10_files=()
mapfile -t ath10_files < <(ls /home/lanforge/ath10* 2>/dev/null)

# Find size of /mnt/lf that is not mounted
cd /mnt
usage_mnt=`du -shxc .`

# Find size of /lib/modules
cd /lib/modules
mapfile -t usage_libmod < <(du -sh *)

# Find how many kernels are installed
cd /boot
mapfile -t boot_kernels < <(ls init*)
boot_usage=`du -sh .`


# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#       report sizes here                                                 #
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
if (( ${#core_files[@]} > 0 )); then
    echo "Core Files:"
    hr
    printf '     %s\n' "${core_files[@]}"
    hr
fi

echo "Usage of /mnt: $usage_mnt"
echo "Usage of /lib/modules: $usage_libmod"
echo "Boot usage: $boot_usage"

if (( ${#boot_kernels[@]} > 1 )); then
    echo "Boot ramdisks:"
    hr
    printf '     %s\n' "${boot_kernels[@]}"
    hr
fi

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#   delete extra things now                                               #
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
echo "Automatic deletion will include: "
echo " journalctl space"
sleep 1
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#   ask to remove if we are interactive                                   #
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
if
item=""
while [[ $item != q ]]; do
  hr
  echo "Would you like to delete? "
  echo "  1) core crash files"
  echo "  2) ath10k crash files"
  echo "  3) old var/www downloads"
  echo "  4) old lanforge downloads"
  echo "  5) orphaned /mnt/lf files"
  read -p "[1-5] or q ? " item
done
