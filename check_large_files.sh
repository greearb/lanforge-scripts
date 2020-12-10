#!/bin/bash
set -x
set -e
eyedee=`id -u`
if (( eyedee != 0 )); then
    echo "Please become root to use this script"
    exit 1
fi

# Find core files
core_files=()
cd /
while read F; do
    core_files+=("$F")
done < <(ls /core* /home/lanforge/core* 2>/dev/null)


# Find ath10k crash residue
ath10_files=()
while read F; do
    ath10_files+=("$F")
done < <(ls /home/lanforge/ath10* 2>/dev/null)

# Find size of /mnt/lf that is not mounted
cd /mnt
usage_mnt=`du -shxc .`

# Find size of /lib/modules
cd /lib/modules
usage_libmod=`du -sh *`

# Find how many kernels are installed
cd /boot
boot_kernels=(`ls init*`)
boot_usage=`du -sh .`

HR="---------------------------------------"
#                               #
#       report sizes here       #
#                               #
if (( ${#core_files[@]} > 0 )); then
    echo "Core Files:"
    echo "$HR"
    printf '%s\n' "${core_files[@]}"
    echo "$HR"
fi

echo "Usage of /mnt: $usage_mnt"
echo "Usage of /lib/modules: $usage_libmod"
echo "Boot usage: $boot_usage"

if (( ${#boot_kernels[@]} > 4 )); then
    echo "Boot ramdisks:"
    echo "$HR"
    printf '%s\n' "${boot_kernels[@]}"
    echo "$HR"
fi

# delete extra things now #

# remove
