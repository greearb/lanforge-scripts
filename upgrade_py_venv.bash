#!/bin/bash
#
#   Build and/or install a version of python and create the virtual environment it wants.
#   Start by building the updated python version. Then package it. Then do a "make install"
#
# this is the comcast python upgrade steps:
#
set -eu

# wget https://yumrepo.sys.comcast.net/cats/candela/Python-3.10.11.tar.xz
PYVER="" #3.10.14"
SHORTVER=""
VENVD="" #venv-3.10"
BUILD_DEST=""
PORTAPYD="$HOME/python"
DEST_TYPE=""
OSSL_DOM="https://www.openssl.org/source/"
OSSL_SRC="openssl-3.0.13.tar.gz"
OSSL_DIR="${OSSL_SRC%.tar.gz}"
OSSL_URL="${OSSL_DOM}/$OSSL_SRC"
OSSL_DEST="${HOME}/python/$OSSL_DIR"

declare -A source_urls=(
    ["3.8.19"]="https://www.python.org/ftp/python/3.8.19/Python-3.8.19.tar.xz"
    ["3.9.17"]="https://www.python.org/ftp/python/3.9.17/Python-3.9.17.tar.xz"
    ["3.10.14"]="https://www.python.org/ftp/python/3.10.14/Python-3.10.14.tar.xz"
)
declare -A dest_dirs=(
  ["local-3.8.19"]="/usr/local/lib/python3.8"
  ["local-3.9.17"]="/usr/local/lib/python3.9"
  ["local-3.10.14"]="/usr/local/lib/python3.10"
  ["portable-3.8.19"]="$PORTAPYD/python3.8.19"
  ["portable-3.9.17"]="$PORTAPYD/python3.9.17"
  ["portable-3.10.14"]="$PORTAPYD//python3.10"
)

declare -A build_choices=(
  ["local"]="/usr/local"
  ["portable"]="$PORTAPYD"
)

declare -A dirs_to_clean=(
  ["/usr/local-3.8.19"]="${dest_dirs['local-3.8.19']}"
  ["$PORTAPYD-3.8.19"]="${dest_dirs['portable-3.8.19']}"
  ["/usr/local-3.9.17"]="${dest_dirs['local-3.9.17']}"
  ["$PORTAPYD-3.9.17"]="${dest_dirs['portable-3.9.17']}"
  ["/usr/local-3.10.14"]="${dest_dirs['local-3.10.14']}"
  ["$PORTAPYD-3.10.14"]="${dest_dirs['portable-3.10.14']}"
)

function help() {
        cat <<EOF
$0 options:
    -a pyver            # python version: 3.8.19, 3.9.17, 3.10.14
    -b local|portable   # local: install to /usr/local
                        # portable: install to $PORTAPYD/<pyver>
    -c                  # remove $PORTAPYD/<pyver>

    Example of cleaning the /usr/local install of python library files
    $0 -a3.9.17 -blocal -c

    Example of buildng $PORTAPYD for python 3.10.11:
    $0 -a3.10.14 -bportable
EOF
}
show_help=0
opts="a:b:ch"
do_clean=0
while getopts $opts opt; do
    case "$opt" in
    a)
        # found is to test for the python version number
        found="${dest_dirs[local-$OPTARG]+1}"
        if [[ -z $found ]]; then
          show_help=1
          echo "Versions available: "
          printf "    %s\n" "${!source_urls[@]}"
          exit 1
        else
          PYVER="$OPTARG"
          VENVD="venv-$OPTARG"
          SHORTVER="${PYVER%.*}"
        fi
        ;;
    b)
        if [[ -z ${OPTARG:-} ]]; then
          show_help=1
          1>&2 echo "-b requires argument"
        fi
        found="${build_choices[$OPTARG]+1}"
        if [[ -z $found ]]; then
          1>&2  echo "No matching -b action [${OPTARG:-}], choose local or portable "
          show_help=1
        else
          BUILD_DEST="${OPTARG}-${PYVER}"
          BUILD_DEST="${dest_dirs[$BUILD_DEST]}"
          DEST_TYPE="$OPTARG"
          echo "Directories: BUILD_DEST[$BUILD_DEST] DEST_TYPE[$DEST_TYPE]"
        fi
        ;;
    c)
        # echo "C $opt $OPTARG"
        if [[ -z ${PYVER:-} ]] || [[ -z $DEST_TYPE ]]; then
          1>&2 echo "-c requires -a<pyver> to be set and dest_type[$DEST_TYPE]"
          show_help=1
        else
          found="${dest_dirs[${DEST_TYPE}-$PYVER]+1}"
          if [[ -z $found ]]; then
            1>&2 echo "Clean: did not see version [${PYVER:-}] or dest_type[$DEST_TYPE]"
            show_help=1
          elif [[ -z ${BUILD_DEST:-} ]]; then
            1>&2 echo "-c requires -a<pyver> and -b<target>"
            show_help=1
          else
            do_clean=1
          fi
        fi
        ;;
    h)
        show_help=1
        ;;
    esac
done

if [[ -z ${PYVER:-} ]] || [[ -z ${VENVD} ]] || [[ -z ${BUILD_DEST:-} ]]; then
    1>&2 echo "Incomplete build options: PYVER[${PYVER:-}] VENVD[${VENVD:-}] BUILD_DEST[${BUILD_DEST:-}]"
    show_help=1
fi

if (( show_help == 1 )); then
    help
    exit 0
fi

if (( do_clean == 1 )); then
  echo "Cleaning $BUILD_DEST $PYVER "
  if [[ ! -d "$BUILD_DEST" ]]; then
    1>&2 echo "Unable to find $BUILD_DEST"
  else
    echo "Build dest: $BUILD_DEST"
  fi
  # set -veux
  dir_key="${DEST_TYPE}-$PYVER"
  if [[ ! -d "${dest_dirs[$dir_key]}" ]]; then
    1>&2 echo "Unable to find ${dest_dirs[$dir_key]}/ dir_key[$dir_key]"
  else
    echo "Cleaning! will remove:"
    echo "$HOME/Downloads/Python-$PYVER"
    echo "$BUILD_DEST/lib/python$SHORTVER"
    echo "$BUILD_DEST/"
  fi
fi


## ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
##    Clean things
## ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
if (( do_clean == 1 )); then

    read -p "Will remove these files...[enter]"
    rm -f /tmp/clean-list.txt
    dirlist=(
      "$HOME/$VENVD"
      "$HOME/Downloads/Python-$PYVER"
      "$BUILD_DEST/lib/python$SHORTVER"
      "$BUILD_DEST/bin/python3"
      "$BUILD_DEST/bin/python$SHORTVER"
      "$BUILD_DEST/bin/python${SHORTVER}-config"
      "$BUILD_DEST/bin/python3-config"
      "$BUILD_DEST/bin/pydoc3"
      "$BUILD_DEST/bin/pydoc${SHORTVER}"
      "$BUILD_DEST/bin/2to3-${SHORTVER}"
      "$BUILD_DEST/bin/2to3"
    )
    for dirnaam in "${dirlist[@]}"; do
      if [[ -e "$dirnaam" ]]; then
        find "$dirnaam" -depth >> /tmp/clean-list.txt
      else
        1>&2 echo "Unable to find $dirnaam"
      fi
    done
    if [[ -s /tmp/clean-list.txt ]]; then
      echo "You are about to see the files to be removed: "
      sleep 3
      less /tmp/clean-list.txt
      read -p "\nProceed to remove files? [enter|ctrl-c] "
      sleep 1
      cat /tmp/clean-list.txt | sudo xargs -n100 rm -rf
    else
      echo "No files found to clean up! This is unexpected"
      exit 1
    fi
    echo "Cleaning finished."
    exit 0
fi



# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
#   Download source
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
set -v
mkdir -p $PORTAPYD ||:
sudo chown -R lanforge: $PORTAPYD
set +v
cd $HOME/Downloads
if [[ ! -f Python-$PYVER.tar.xz ]]; then
    echo "Downloading python $PYVER source..."
    wget https://www.python.org/ftp/python/$PYVER/Python-$PYVER.tar.xz
fi
if [[ ! -f $OSSL_SRC ]]; then
  echo "Downloading openssl..."
  wget -O $OSSL_SRC $OSSL_URL
  tar xf $OSSL_SRC
  PKI=$(sudo find /etc/ -name openssl.cnf -printf "%h\n")
  echo "Configuring openssl..."
  cd $OSSL_DIR
  ./config \
    --prefix=$OSSL_DEST \
    --libdir=lib \
    --openssldir=$PKI
  sleep 1
  echo "Building openssl..."
  make -j1 depend
  make -j$(nproc)
  make install_sw
  cd -
fi


## ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
##    Build things
## ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----

echo "Checking build requirements..."
sudo dnf install libffi-devel \
  tcl tcl-devel \
  readline readline-devel \
  zlib zlib-devel \
  openssl-devel openssl-libs

if [[ -x Python-$PYVER/python ]]; then
    echo "Python already compiled. Remove $PWD/python to recompile"
    sleep 5
else
    if [[ ! -d Python-$PYVER ]]; then
      tar xf Python-$PYVER.tar.xz
    fi
    echo "Compiling python $PYVER..."
    sleep 5
    cd Python-$PYVER
    sudo chown -R $LOGNAME: .
    make clean ||:
    make distclean ||:
    set -v
    ./configure \
      --with-openssl=$HOME/Downloads/$OSSL_DIR \
      --with-openssl-rpath=auto \
      --with-ensurepip \
      --enable-optimizations \
      --prefix=$BUILD_DEST

    make -j$(nproc) || {
      echo "Build error"
      exit 1
    }
    set +v
    echo "About to install...."
    # sleep 5
    sudo make install
    if [[ -x $BUILD_DEST/bin/python$SHORTVER ]]; then
      echo "Updating etc alternatives..."
      sudo update-alternatives --install /usr/bin/python python $BUILD_DEST/bin/python$SHORTVER 20
      sudo update-alternatives --config python
    else
      1>&2 echo "Unable to find $BUILD_DEST/bin/python$SHORTVER, alternatives not updated"
      read -p "Continue? [enter|ctrl-c] "
    fi
fi
cd
if [[ -f $VENVD/pyenv.cfg ]]; then
    echo "Not removing old $VENVD. If you want to rebuild it, remove $VENVD/pyenv.cfg"
else
    echo "Rebuilding $VENVD..."
    rm -rf $VENVD
    mkdir $VENVD
    $BUILD_DEST/bin/python3 -m venv $VENVD
    . $VENVD/bin/activate
    # /usr/local/bin/pip3.10 install pandasS
    $HOME/scripts/py-scripts/update_dependencies.py
fi
# check if lanforge/.bashrc is updated to source venv
if grep -q "$VENVD" $HOME/.bashrc; then
    echo "Found $VENVD alias"
else
    echo "Creating $VENVD alias..."
    (
        echo "alias $VENVD='. \$HOME/$VENVD/bin/activate'"
        echo "if [[ -r \$HOME/USE_$VENVD ]]; then . \$HOME/$VENVD/bin/activate; fi"
    ) >> "$HOME/.bashrc"
fi
# uncomment this you want new shells to automatically source venv
# touch $HOME/USE_VENV3-10
#
