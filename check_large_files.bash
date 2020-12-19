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

function contains () {
    if [[ x$1 = x ]] || [[ x$2 = x ]]; then
        echo "contains wants ARRAY and ITEM arguments: if contains name joe; then...  }$"
        exit 1
    fi
    local zarray="${1}[@]"
    for item in "${zarray[@]}"; do
        echo $item
        [[ "$2" = "$item" ]] && return 0
    done
    return 1
}

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
      ;;
    t)
      selections+=($opt)
      ;;
    v)
      quiet=0
      verbose=1
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

declare -A totals=(
    [b]=0
    [c]=0
    [d]=0
    [k]=0
    [l]=0
    [m]=0
    [r]=0
    [t]=0
)
declare -A desc=(
    [b]="kernel files"
    [c]="core files"
    [d]="lf downloads"
    [k]="lf/ath10 files"
    [l]="/var/log"
    [m]="/mnt/lf files"
    [r]="lf/report_data"
    [t]="/var/tmp"
)
declare -A surveyors_map=(
    [b]="survey_kernel_files"
    [c]="survey_core_files"
    [d]="survey_lf_downloads"
    [k]="survey_ath10_files"
    [l]="survey_var_log"
    [m]="survey_mnt_lf_files"
    [r]="survey_report_data"
    [t]="survey_var_tmp"
)

declare -A cleaners_map=(
    [b]="clean_old_kernels"
    [c]="clean_core_files"
    [d]="clean_lf_downloads"
    [k]="clean_ath10_files"
    [l]="clean_var_log"
    [m]="clean_mnt_lf_files"
    [r]="compress_report_data"
    [t]="clean_var_tmp"
)

kernel_files=()
survey_kernel_files() {
    mapfile -t kernel_files < <(ls /boot/* /lib/modules/* 2>/dev/null)
    totals[b]=$(du -hc "$kernel_files" | awk '/total/{print $1}')
}

# Find core files
core_files=()
survey_core_files() {
    cd /
    mapfile -t core_files < <(ls /core* /home/lanforge/core* 2>/dev/null)
    totals[c]=$(du -hc "${core_files[@]}" | awk '/total/{print $1}')
    [[ x${totals[c]} = x ]] && totals[c]=0
}

# downloads
downloads=()
survey_lf_downloads() {
    cd /home/lanforge/Downloads || return 1
    mapfile -t downloads < <(ls *gz *z2 *-Installer.exe *firmware* kinst_* *Docs* 2>/dev/null)
    totals[d]=$(du -hc "${downloads[@]}" | awk '/total/{print $1}')
    [[ x${totals[d]} = x ]] && totals[d]=0
}

# Find ath10k crash residue
ath10_files=()
survey_ath10_files() {
    mapfile -t ath10_files < <(ls /home/lanforge/ath10* 2>/dev/null)
    totals[k]=$(du -hc "${ath10_files}" 2>/dev/null | awk '/total/{print $1}')
    [[ x${totals[k]} = x ]] && totals[k]=0
}

# stuff in var log
var_log_files=()
survey_var_log() {
    mapfile -t var_log_files < <(find /var/log -type f -size +10M 2>/dev/null)
    totals[l]=$(du -hc "${var_log_files}" 2>/dev/null | awk '/total/{print $1}' )
    [[ x${totals[l]} = x ]] && totals[l]=0
}

# stuff in var tmp
var_tmp_files=()
survey_var_tmp() {
    mapfile -t var_tmp_files < <(find /var/tmp -type f 2>/dev/null)
    totals[t]=$(du -sh "${var_tmp_files}" 2>/dev/null | awk '/total/{print $1}' )
    [[ x${totals[t]} = x ]] && totals[t]=0
}

# Find size of /mnt/lf that is not mounted
mnt_lf_files=()
survey_mnt_lf_files() {
    [ ! -d /mnt/lf ] && return 0
    mapfile -t mnt_lf_files < <(find /mnt/lf -type f --one_filesystem)
    totals[m]=$(du -xhc "${mnt_lf_files[@]}" 2>/dev/null | awk '/total/{print $1}')
    [[ x${totals[m]} = x ]] && totals[m]=0
}

## Find size of /lib/modules
# cd /lib/modules
# mapfile -t usage_libmod < <(du -sh *)

# Find how many kernels are installed
# cd /boot
# mapfile -t boot_kernels < <(ls init*)
# boot_usage=`du -sh .`

report_files=()
survey_report_data() {
    cd /home/lanforge
    totals=that
}


# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#       gather usage areas
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
survey_areas() {
    local area
    echo -n "surveying..."
    for area in "${!surveyors_map[@]}"; do
        echo -n "#"
        ${surveyors_map[$area]}
    done
    echo ""
}

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#       report sizes here                                                 #
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
disk_usage_report() {
    for k in "${!totals[@]}"; do
        echo -e "\t${desc[$k]}:\t${totals[$k]}"
    done
}
survey_areas
disk_usage_report
exit
#if (( ${#core_files[@]} > 0 )); then
#    echo "Core Files:"
#    hr
#    printf '     %s\n' "${core_files[@]}"
#    hr
#fi

#echo "Usage of /mnt: $usage_mnt"
#echo "Usage of /lib/modules: $usage_libmod"
#echo "Boot usage: $boot_usage"

#if (( ${#boot_kernels[@]} > 1 )); then
#    echo "Boot ramdisks:"
#    hr
#    printf '     %s\n' "${boot_kernels[@]}"
#    hr
#fi

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#   delete extra things now                                               #
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
echo "Automatic deletion will include: "
echo " journalctl space"
sleep 1
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#   ask to remove if we are interactive                                   #
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #

if contains "selections" "a" ; then
    for z in "${selections[@]}"; do
        echo "will execute $z"
    done
    exit 0
fi

choice=""
while [[ $choice != q ]]; do
  hr
  #abcdhklmqrtv
  echo "Would you like to delete? "
  echo "  b) old kernels"
  echo "  c) core crash files"
  echo "  d) old LANforge downloads"
  echo "  k) ath10k crash files"
  echo "  l) old /var/log files"
  echo "  m) orphaned /mnt/lf files"
  echo "  r) compress .csv report files"
  echo "  t) clean /var/tmp"
  read -p "[1-5] or q ? " choice

  case "$choice" in
    b )
        printf "%s\n" "${kernels[@]}"
        clean_old_kernels
        ;;
    c )
        printf "%s\n" "${core_files[@]}"
        clean_core_files
        ;;
    d )
        printf "%s\n" "${lf_downloads[@]}"
        clean_lf_downloads
        ;;
    k )
        printf "%s\n" "${ath10_files[@]}"
        clean_ath10_files
        ;;
    l )
        printf "%s\n" "${var_log_files[@]}"
        clean_var_log
        ;;
    m )
        printf "%s\n" "${mnt_lf_files[@]}"
        clean_mnt_lf_files
        ;;
    r )
        printf "%s\n" "${report_data_dirs[@]}"
        compress_report_data
        ;;
    t )
        printf "%s\n" "${var_tmp_files[@]}"
        clean_var_tmp
        ;;
    q )
        break
        ;;
    * )
        echo "not an option [$choice]"
        ;;
  esac
done


echo bye