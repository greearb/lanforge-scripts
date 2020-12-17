#!/bin/bash
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#  Check for large files and purge many of the most inconsequencial       #
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
set -x
set -e
HR=" ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----"
function hr() {
  echo "$HR"
}

eyedee=`id -u`
if (( eyedee != 0 )); then
    echo "$0: Please become root to use this script, bye"
    exit 1
fi

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
usage_libmod=`du -sh *`

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

if (( ${#boot_kernels[@]} > 4 )); then
    echo "Boot ramdisks:"
    hr
    printf '     %s\n' "${boot_kernels[@]}"
    hr
fi

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#   delete extra things now                                               #
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#   ask to remove if we are interactive                                   #
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #

