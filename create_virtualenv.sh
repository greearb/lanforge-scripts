#!/bin/bash
sudo dnf install virtualenv -y
su -l lanforge -c "python3 -m venv lanforge_env"
su -l lanforge -c "echo 'source ~/lanforge_env/bin/actcivate' >> ~/.bashrc"
