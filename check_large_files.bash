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

debug() {
    if [[ x$verbose = x ]] || (( $verbose < 1 )); then return; fi

    echo ": $1"
}

note() {
    #set -x
    if (( $quiet > 0 )); then return; fi

    echo "# $1"
    #set +x
}

function contains () {
    if [[ x$1 = x ]] || [[ x$2 = x ]]; then
        echo "contains wants ARRAY and ITEM arguments: if contains name joe; then...  }$"
        exit 1
    fi
    local tmp=$1[@]
    local array=( "${!tmp[@]}" )
    if (( ${#array[@]} < 1 )); then
        return 1
    fi
    for item in "${array[@]}"; do
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

#if (( ${#selections} < 1 )); then
#  echo "$USAGE"
#  exit 0
#fi

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

clean_old_kernels() {
    note "Cleaning old kernels WIP"
    kernels=()
    # need to avoid most recent fedora kernel
    if [ -x /usr/sbin/rpm ]; then
        local kern_pkgs=( $( rpm -qa 'kernel*' | sort ) )
        local pkg
        for pkg in "${kern_pkgs[@]}"; do
            if [[ $pkg = kernel-tools* ]] \
                || [[ $pkg = kernel-headers* ]] \
                || [[ $pkg = kernel-devel* ]] ; then
                continue
            fi
            kernels+=( $pkg )
            kernel_series=${pkg##kernel*5}
            echo "K SER: $kernel_series"
        done
    fi
    if (( $verbose > 0 )); then
        printf "Would remove %s\n" "${kernels[@]}"
    fi
}

clean_core_files() {
    note "Cleaning core files WIP"
    if (( $verbose > 0 )); then
        printf "%s\n" "${core_files[@]}"
    fi
}

clean_lf_downloads() {
    note "Clean LF downloads WIP"
    if (( $verbose > 0 )); then
        printf "%s\n" "${lf_downloads[@]}"
    fi
}

clean_ath10_files() {
    note "clean_ath10_files WIP"
    if (( $verbose > 0 )); then
        printf "%s\n" "${ath10_files[@]}"
    fi
}

clean_var_log() {
    note "Clean var log WIP"
    if (( $verbose > 0 )); then
        printf "%s\n" "${var_log_files[@]}"
    fi
}

clean_mnt_fl_files() {
    note "clean mnt lf files WIP"
    if (( $verbose > 0 )); then
        printf "%s\n" "${mnt_lf_files[@]}"
    fi

}

compress_report_data() {
    note "compress report data WIP"
    if (( $verbose > 0 )); then
        printf "%s\n" "${report_data_dirs[@]}"
    fi
}

clean_var_tmp() {
    note "clean var tmp"
    if (( $verbose > 0 )); then
        printf "%s\n" "${var_tmp_files[@]}"
    fi
    rf -f "${var_tmp_files[@]}"
}


kernel_files=()
survey_kernel_files() {
    debug "Surveying Kernel files"
    mapfile -t kernel_files < <(ls /boot/* /lib/modules/* 2>/dev/null)
    totals[b]=$(du -hc "$kernel_files" | awk '/total/{print $1}')
}

# Find core files
core_files=()
survey_core_files() {
    debug "Surveying core files"
    cd /
    #set -x
    mapfile -t core_files < <(ls /core* /home/lanforge/core* 2>/dev/null) 2>/dev/null
    if [[ $verbose = 1 ]]; then
        printf "%s\n" "${core_files[@]}"
    fi
    if (( ${#core_files[@]} > 0 )); then
        totals[c]=$(du -hc "${core_files[@]}" | awk '/total/{print $1}')
    fi
    #set +x
    [[ x${totals[c]} = x ]] && totals[c]=0
}

# downloads
downloads=()
survey_lf_downloads() {
    debug "Surveying /home/lanforge downloads"
    cd /home/lanforge/Downloads || return 1
    mapfile -t downloads < <(ls *gz *z2 *-Installer.exe *firmware* kinst_* *Docs* 2>/dev/null)
    totals[d]=$(du -hc "${downloads[@]}" | awk '/total/{print $1}')
    [[ x${totals[d]} = x ]] && totals[d]=0
}

# Find ath10k crash residue
ath10_files=()
survey_ath10_files() {
    debug "Sureyinig ath10 crash files"
    mapfile -t ath10_files < <(ls /home/lanforge/ath10* 2>/dev/null)
    totals[k]=$(du -hc "${ath10_files}" 2>/dev/null | awk '/total/{print $1}')
    [[ x${totals[k]} = x ]] && totals[k]=0
}

# stuff in var log
var_log_files=()
survey_var_log() {
    debug "Surveying var log"
    mapfile -t var_log_files < <(find /var/log -type f -size +10M 2>/dev/null)
    totals[l]=$(du -hc "${var_log_files}" 2>/dev/null | awk '/total/{print $1}' )
    [[ x${totals[l]} = x ]] && totals[l]=0
}

# stuff in var tmp
var_tmp_files=()
survey_var_tmp() {
    #set -x
    debug "Surveying var tmp"
    mapfile -t var_tmp_files < <(find /var/tmp -type f 2>/dev/null)
    totals[t]=$(du -sh "${var_tmp_files}" 2>/dev/null | awk '/total/{print $1}' )
    [[ x${totals[t]} = x ]] && totals[t]=0
    #set +x
}

# Find size of /mnt/lf that is not mounted
mnt_lf_files=()
survey_mnt_lf_files() {
    [ ! -d /mnt/lf ] && return 0
    debug "Surveying mnt lf"
    mapfile -t mnt_lf_files < <(find /mnt/lf -type f --one_filesystem 2>/dev/null)
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
    debug "Surveying for lanforge report data"
    cd /home/lanforge
    #set -x
    local fnum=$( find -type f -name '*.csv' 2>/dev/null | wc -l )
    local fsiz=$( find -type f -name '*.csv' 2>/dev/null | xargs du -hc | awk '/total/{print $1}')
    totals[r]="$fsiz"
    [[ x${totals[r]} = x ]] && totals[r]=0
    report_files=("CSV files: $fnum tt $fsiz")
    #set +x
}


# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#       gather usage areas
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
survey_areas() {
    local area
    if [[ x$quiet = x ]] || (( $quiet < 1 )); then
        echo -n "Surveying..."
    fi
    for area in "${!surveyors_map[@]}"; do
        if [[ x$quiet = x ]] || (( $quiet < 1 )); then
            echo -n "#"
        fi
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

if (( ${#core_files[@]} > 0 )); then
    note "Core Files detected, will remove:"
    hr
    printf '     %s\n' "${core_files[@]}"
    hr
    selections+=("c")
fi

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
#set -x
if contains "selections" "a" ; then
    note "Automatic deletion will include: "
    printf "%s\n" "${selections[@]}"
    debug "Doing automatic cleanup"
    for z in "${selections[@]}"; do
        debug "Will perform ${desc[$z]}"
        ${cleaners_map[$z]}
    done
   
    survey_areas
    disk_usage_report

    exit 0
fi

if (( ${#selections[@]} > 0 )) ; then
    debug "Doing selected cleanup"
    for z in "${selections[@]}"; do
        debug "Will perform ${desc[$z]}"
        ${cleaners_map[$z]}
        selections=("${selections[@]/$z}")
    done
   
    survey_areas
    disk_usage_report
fi
set +x

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#   ask for things to remove if we are interactive                        #
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #


choice=""
while [[ $choice != q ]]; do
    hr
    #abcdhklmqrtv
    echo "Would you like to delete? "
    echo "  b) old kernels                ${totals[b]}"
    echo "  c) core crash files           ${totals[c]}"
    echo "  d) old LANforge downloads     ${totals[d]}"
    echo "  k) ath10k crash files         ${totals[k]}"
    echo "  l) old /var/log files         ${totals[l]}"
    echo "  m) orphaned /mnt/lf files     ${totals[m]}"
    echo "  r) compress .csv report files ${totals[r]}"
    echo "  t) clean /var/tmp             ${totals[t]}"
    read -p "[1-5] or q ? " choice

    case "$choice" in
    b )
        clean_old_kernels
        ;;
    c )
        clean_core_files
        ;;
    d )
        clean_lf_downloads
        ;;
    k )
        clean_ath10_files
        ;;
    l )
        clean_var_log
        ;;
    m )
        clean_mnt_lf_files
        ;;
    r )
        compress_report_data
        ;;
    t )
        clean_var_tmp
        ;;
    q )
        break
        ;;
    * )
        echo "not an option [$choice]"
        ;;
    esac
    survey_areas
    disk_usage_report
done


echo bye
