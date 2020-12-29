#!/bin/bash
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#  Check for large files and purge many of the most inconsequencial       #
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
# set -x
# set -e
# these are default selections
selections=()
deletion_targets=()
show_menu=1
verbose=0
quiet=0
starting_dir="$PWD"

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
    if (( $quiet > 0 )); then return; fi
    echo "# $1"
}

function contains () {
    if [[ x$1 = x ]] || [[ x$2 = x ]]; then
        echo "contains wants ARRAY and ITEM arguments: if contains name joe; then...  }$"
        exit 1
    fi
    # these two lines below are important to not modify
    local tmp="${1}[@]"
    local array=( ${!tmp} )

    # if [[ x$verbose = x1 ]]; then
    #    printf "contains array %s\n" "${array[@]}"
    # fi
    if (( ${#array[@]} < 1 )); then
        return 1
    fi
    local item
    for item in "${array[@]}"; do
        # debug "contains testing $2 == $item"
        [[ "$2" = "$item" ]] && return 0
    done
    return 1
}

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
    [n]="DNF cache"
    [r]="/home/lanforge/report_data"
    [t]="/var/tmp"
)
declare -A surveyors_map=(
    [b]="survey_kernel_files"
    [c]="survey_core_files"
    [d]="survey_lf_downloads"
    [k]="survey_ath10_files"
    [l]="survey_var_log"
    [m]="survey_mnt_lf_files"
    [n]="survey_dnf_cache"
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
    [n]="clean_dnf_cache"
    [r]="compress_report_data"
    [t]="clean_var_tmp"
)

kernel_to_relnum() {
    local hunks=()
    #echo "KERNEL RELNUM:[$1]"
    IFS="." read -ra hunks <<< "$1"
    IFS=
    local tmpstr
    local max_width=8
    local last_len=0
    local diff_len=0
    local expandos=()
    for i in 0 1 2; do
        if (( $i < 2 )); then
            expandos+=( $(( 100 + ${hunks[$i]} )) )
        else
            tmpstr="0000000000000${hunks[i]}"
            last_len=$(( ${#tmpstr} - $max_width ))
            expandos+=( ${tmpstr:$last_len:${#tmpstr}} )
            #1>&2 echo "TRIMMED ${tmpstr:$last_len:${#tmpstr}}"
        fi
    done
    #local relnum="${expandos[0]}${expandos[1]}${expandos[2]}"
    echo "${expandos[0]}${expandos[1]}${expandos[2]}"
}

clean_old_kernels() {
    note "Cleaning old kernels..."
    local pkg
    local k_pkgs=()
    local selected_k=()
    local k_series=()
    # need to avoid most recent fedora kernel
    if [ ! -x /usr/bin/rpm ]; then
        note "Does not appear to be an rpm system."
        return 0
    fi
    local ur=$( uname -r )
    local current_relnum=$( kernel_to_relnum $ur )
    local kern_pkgs=( $( rpm -qa 'kernel*' | sort ) )
    local pkg
    for pkg in "${kern_pkgs[@]}"; do
        if [[ $pkg = kernel-tools-* ]] \
            || [[ $pkg = kernel-headers-* ]] \
            || [[ $pkg = kernel-devel-* ]] ; then
            continue
        fi
        k_pkgs+=( $pkg )
    done
    for pkg in "${k_pkgs[@]}"; do
        pkg=${pkg##kernel-modules-extra-}
        pkg=${pkg##kernel-modules-}
        pkg=${pkg##kernel-core-}
        pkg=${pkg%.fc??.x86_64}
        kernel_series=$( kernel_to_relnum ${pkg##kernel-} )

        #debug "K SER: $kernel_series"
        if contains k_series $kernel_series; then
            continue
        elif [[ x$current_relnum = x$kernel_series ]]; then
            debug "avoiding current kernel [$kernel_series]"
        else
            k_series+=($kernel_series)
        fi
    done

    IFS=$'\n' k_series=($(sort <<<"${k_series[*]}" | uniq)); unset IFS
    for pkg in "${k_series[@]}"; do
        debug "series $pkg"
    done
    if (( "${#k_series[@]}" > 1 )); then
        local i=0
        # lets try and avoid the last item assuming that is the most recent
        for i in $( seq 0 $(( ${#k_series[@]} - 2 )) ); do
            debug "item $i is ${k_series[$i]}"
        done
    fi

    set +x
    if (( ${#selected_k[@]} < 1 )); then
        note "No kernels selected for removal"
    fi
    if (( $quiet < 1 )); then
        printf "Would remove %s\n" "${selected_k[@]}"
    fi
}

clean_core_files() {
    note "Cleaning core files..."
    if (( ${#core_files[@]} < 1 )); then
        debug "No core files ?"
        return 0
    fi
    local counter=0
    for f in "${core_files[@]}"; do
        echo -n "-"
        rm -f "$f"
        counter=$(( counter + 1 ))
        if (( ($counter % 100) == 0 )); then
            sleep 0.2
        fi
    done
    echo ""
}

clean_lf_downloads() {
    if (( ${#lf_downloads[@]} < 1 )); then
        note "No /home/lanforge/downloads files to remove"
        return 0
    fi
    note "Clean LF downloads..."
    if (( $verbose > 0 )); then
        printf "Delete:[%s]\n" "${lf_downloads[@]}" | sort
    fi
    cd /home/lanforge/Downloads
    for f in "${lf_downloads[@]}"; do
        [[ "$f" = "/" ]] && echo "Whuuut? this is not good, bye." && exit 1
        echo "Next:[$f]"
        sleep 0.2
        rm -f "$f"
    done
    cd "$starting_dir"
}

clean_ath10_files() {
    note "clean_ath10_files WIP"
    if (( $verbose > 0 )); then
        printf "%s\n" "${ath10_files[@]}"
    fi
}

clean_var_log() {
    note "Vacuuming journal..."
    journalctl --vacuum-size 1M
    if (( ${#var_log_files[@]} < 1 )); then
        note "No notable files in /var/log to remove"
        return
    fi
    local vee=""
    if (( $verbose > 0 )); then
        printf "%s\n" "${var_log_files[@]}"
        vee="-v"
    fi
    cd /var/log
    while read file; do
        if [[ $file = /var/log/messages ]]; then
            echo "" > /var/log/messages
        else
            rm -f $vee "$file"
        fi
    done <<< "${var_log_files[@]}"
    cd "$starting_dir"
}

clean_dnf_cache() {
    local yum="dnf"
    which --skip-alias dnf &> /dev/null
    (( $? < 0 )) && yum="yum"
    debug "Purging $yum cache"
    $yum clean all
}

clean_mnt_lf_files() {
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
        printf "    %s\n" "${var_tmp_files[@]}"
        sleep 1
    fi
    for f in "${var_tmp_files[@]}"; do
        rf -f "$f"
        sleep 0.2
    done
}


kernel_files=()
survey_kernel_files() {
    debug "Surveying Kernel files"
    mapfile -t kernel_files < <(ls /boot/* /lib/modules/* 2>/dev/null)
    # totals[b]=$(du -hc "$kernel_files" | awk '/total/{print $1}')
    local boot_u=
}

# Find core files
core_files=()
survey_core_files() {
    debug "Surveying core files"
    cd /
    mapfile -t core_files < <(ls /core* /home/lanforge/core* 2>/dev/null) 2>/dev/null
    if [[ $verbose = 1 ]] && (( ${#core_files[@]} > 0 )); then
        printf "    %s\n" "${core_files[@]}" | head
    fi
    if (( ${#core_files[@]} > 0 )); then
        totals[c]=$(du -hc "${core_files[@]}" | awk '/total/{print $1}')
    fi
    #set +x
    [[ x${totals[c]} = x ]] && totals[c]=0
    cd "$starting_dir"
}

# downloads
lf_downloads=()
survey_lf_downloads() {
    debug "Surveying /home/lanforge downloads"
    [ ! -d "/home/lanforge/Downloads" ] && note "No downloads folder " && return 0
    cd /home/lanforge/Downloads
    mapfile -t lf_downloads < <(ls *gz *z2 *-Installer.exe *firmware* kinst_* *Docs* 2>/dev/null)
    totals[d]=$(du -hc "${lf_downloads[@]}" | awk '/total/{print $1}')
    [[ x${totals[d]} = x ]] && totals[d]=0
    cd "$starting_dir"
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
    mapfile -t var_log_files < <(find /var/log -type f -size +35M \
        -not \( -path '*/journal/*' -o -path '*/sa/*' -o -path '*/lastlog' \) 2>/dev/null)
    totals[l]=$(du -hc "${var_log_files}" 2>/dev/null | awk '/total/{print $1}' )
    [[ x${totals[l]} = x ]] && totals[l]=0
}

# stuff in var tmp
var_tmp_files=()
survey_var_tmp() {
    debug "Surveying var tmp"
    mapfile -t var_tmp_files < <(find /var/tmp -type f 2>/dev/null)
    totals[t]=$(du -sh "${var_tmp_files}" 2>/dev/null | awk '/total/{print $1}' )
    [[ x${totals[t]} = x ]] && totals[t]=0
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

survey_dnf_cache() {
    local yum="dnf"
    which --skip-alias dnf &> /dev/null
    (( $? < 0 )) && yum="yum"
    debug "Surveying $yum cache"
    totals[n]=$(du -hc '/var/cache/{dnf,yum}' 2>/dev/null | awk '/total/{print $1}')
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
    local fnum=$( find -type f -name '*.csv' 2>/dev/null | wc -l )
    local fsiz=$( find -type f -name '*.csv' 2>/dev/null | xargs du -hc | awk '/total/{print $1}')
    totals[r]="$fsiz"
    [[ x${totals[r]} = x ]] && totals[r]=0
    report_files=("CSV files: $fnum tt $fsiz")
    cd "$starting_dir"
}


# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
#       gather usage areas
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- #
survey_areas() {
    local area
    note "Surveying..."
    for area in "${!surveyors_map[@]}"; do
        if (( $quiet < 1 )) && (( $verbose < 1 )); then
            echo -n "#"
        fi
        ${surveyors_map[$area]}
    done
    if (( $quiet < 1 )) && (( $verbose < 1 )); then
        echo ""
    fi
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
    hr
    note "${#core_files[@]} Core Files detected:"
    filestr=""
    declare -A core_groups
    # set -e
    # note that the long pipe at the bottom of the loop is the best way to get
    # the system to operate with thousands of core files
    while read group7; do
        (( $verbose > 0 )) && echo -n '+'
        group7="${group7%, *}"
        group7="${group7//\'/}"
        [[ ${core_groups[$group7]+_} != _ ]] && core_groups[$group7]=0
        core_groups[$group7]=$(( ${core_groups[$group7]} + 1 ))
    done < <(echo "${core_files[@]}" | xargs file | awk -F": " '/execfn:/{print $7}')
    echo ""
    echo "These types of core files were found:"
    for group in "${!core_groups[@]}"; do
        echo "${core_groups[$group]} files of $group"
    done | sort -n
    hr
    (( ${#core_files[@]} > 0 )) && selections+=("c")
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
    debug "Doing selected cleanup: "
    printf "    %s\n" "${selections[@]}"
    sleep 1
    for z in "${selections[@]}"; do
        debug "Performing ${desc[$z]}"
        ${cleaners_map[$z]}
        selections=("${selections[@]/$z}")
    done
    survey_areas
    disk_usage_report
else
    debug "No selections present"
fi

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
    echo "  n) purge dnf/yum cache        ${totals[n]}"
    echo "  r) compress .csv report files ${totals[r]}"
    echo "  t) clean /var/tmp             ${totals[t]}"
    echo "  q) quit"
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
