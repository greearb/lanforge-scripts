#!/usr/bin/env python3
import pathlib
import subprocess
import argparse
import os
import os.path
import sys
import sysconfig


def main():
    parser = argparse.ArgumentParser(
        prog="update_dependencies.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description='''
        NAME: update_dependencies.py

        PURPOSE:  Installs python3 script package dependencies

        OUTPUT: List of successful and unsuccessful installs

        NOTES: Run this as lanforge user (not root)
        '''
    )
    # TODO: add --create_venv option (with PEP 668 in mind).
    sysconfig_dir = sysconfig.get_path("stdlib", sysconfig.get_default_scheme())
    external_marker = pathlib.Path(f"{sysconfig_dir}/EXTERNALLY-MANAGED")
    if external_marker.is_file():
        print(f"PEP 668 EXTERNALLY-MANAGED detected. Testing for virtual environment...")
        if sys.prefix == sys.base_prefix:
            print("Cannot continue, pip3 commands are not in a virtual environment.")
            exit(1)
        else:
            print("Virtual environment detected, proceeding...")
    else:
        print("PEP 668 not detected.")

    args = parser.parse_args()

    print("Installing Script Python3 Dependencies")

    packages = [
        'cryptography',
        'kaleido',
        'matplotlib',
        'numpy',
        'pandas',
        'paramiko',
        'pdfkit',
        'pexpect-serial',
        'pip-search',
        'plotly',
        'psutil',
        'pyserial',
        'pyshark',
        'scipy',
        'scp',
        'simple-geometry',
        'websocket-client',
        'xlsxwriter',
    ]
    packages_installed = []
    packages_failed = []
    subprocess.call('pip3 install --upgrade pip', shell=True)
    for package in packages:
        if os.name == 'nt':
            command = "pip3 install {} ".format(package)
        else:
            command = "pip3 install {} >/tmp/pip3-stdout 2>/tmp/pip3-stderr".format(package)
        res = subprocess.call(command, shell=True)
        if res == 0:
            print("Package {} install SUCCESS Returned Value: {} ".format(package, res))
            packages_installed.append(package)
        else:
            print("Package {} install FAILED Returned Value: {} ".format(package, res))
            print("To see errors try: pip3 install {}".format(package))
            packages_failed.append(package)

    print("Install Complete")
    print("Packages Installed Success: {}\n".format(packages_installed))
    if not packages_failed:
        return
    print("Packages Failed (Some scripts may not need these packages): {}".format(packages_failed))


if __name__ == "__main__":
    main()
