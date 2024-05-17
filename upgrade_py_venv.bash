#!/bin/bash
#
#   Build and/or install a version of python and create the virtual environment it wants.
#   Start by building the updated python version. Then package it. Then do a "make install"
#
# this is the comcast python upgrade steps:
#
cd /home/lanforge/Downloads
wget https://yumrepo.sys.comcast.net/cats/candela/Python-3.10.11.tar.xz
tar xJf Python-3.10.11.tar.xz
cd Python-3.10.11
./configure --with-ensurepip --enable-optimizations --prefix=/usr/local
make -j
sudo make install
sudo update-alternatives --install /usr/bin/python python /usr/local/bin/python3.10 20
sudo update-alternatives --config python

# 
