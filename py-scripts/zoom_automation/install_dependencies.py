#!/usr/bin/env python3

import subprocess
import argparse
import os
import platform

def main():
    parser = argparse.ArgumentParser(
        prog="update_dependencies.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description='''
        NAME: update_dependencies.py

        PURPOSE: Installs Python3 script package dependencies

        OUTPUT: List of successful and unsuccessful installs

        NOTES: Run this as lanforge user (not root)
        '''
    )

    args = parser.parse_args()

    print("Installing Script Python3 Dependencies")
    packages = ['selenium','requests','flask','pyperclip','paramiko','pytz']
    packages_installed = []
    packages_failed = []
    
    

    for package in packages:
        if platform.system() == 'Windows':
            command = f"py -m pip install {package}"
        else:
            command = f"python3 -m pip install {package} >/tmp/pip3-stdout 2>/tmp/pip3-stderr"
        
        try:
            res = subprocess.run(command, shell=True, check=True)
            print(f"Package {package} install SUCCESS Returned Value: {res.returncode}")
            packages_installed.append(package)
        except subprocess.CalledProcessError as e:
            print(f"Package {package} install FAILED Returned Value: {e.returncode}")
            print(f"To see errors try: {command}")
            packages_failed.append(package)

    print("Install Complete")
    print(f"Packages Installed Success: {packages_installed}\n")
    
    if packages_failed:
        print(f"Packages Failed  {packages_failed}")

if __name__ == "__main__":
    main()

