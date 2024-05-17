#!/bin/bash
#
#   Build and/or install a version of python and create the virtual environment it wants.
#   Start by building the updated python version. Then package it. Then do a "make install"
#
# this is the comcast python upgrade steps:
#
set -veux
cd /home/lanforge/Downloads
# wget https://yumrepo.sys.comcast.net/cats/candela/Python-3.10.11.tar.xz
PYVER=3.10.14
if [[ ! -f Python-$PYVER.tar.xz ]]; then
    wget https://www.python.org/ftp/python/$PYVER/Python-$PYVER.tar.xz
fi
sudo dnf install libffi-devel \
  tcl tcl-devel \
  readline readline-devel \
  zlib zlib-devel \
  openssl-devel openssl-libs

if [[ ! -d Python-$PYVER ]]; then
  tar xf Python-$PYVER.tar.xz
fi
cd Python-$PYVER
sudo chown -R $LOGNAME: .
make clean ||:
make distclean ||:
./configure \
  --with-ensurepip \
  --enable-optimizations \
  --prefix=/usr/local

make -j12 || {
  echo "Build error"
  exit 1
}
echo "About to install...."
sleep 5
sudo make install
sudo update-alternatives --install /usr/bin/python python /usr/local/bin/python3.10 20
sudo update-alternatives --config python

cd
if [[ -d venv-3.10 ]]; then
  rm -rf venv-3.10
fi
mkdir venv-3.10
/usr/local/bin/python3 -m venv venv-3.10
. venv-3.10/bin/activate
/usr/local/bin/pip3.10 install pandas
# 
