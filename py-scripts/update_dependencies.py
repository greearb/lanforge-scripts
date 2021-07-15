#!/usr/bin/env python3
# INCLUDE_IN_README
'''
NAME: update_dependencies.py 

PURPOSE:  Installs python3 script package dependencies

OUTPUT: List of successful and unsuccessful installs

NOTES: Install as root
'''

import subprocess
def main():
    print("Installing Script Python3 Dependencies")
    packages = ['pandas', 'plotly', 'numpy', 'cryptography', 'paramiko', 'bokeh','pyarrow', 'websocket-client', 'xlsxwriter',\
         'pyshark', 'influxdb', 'influxdb-client', 'matplotlib', 'pdfkit', 'pip-search', 'pyserial', 'pexpect-serial' ,'scp', 'pyjwt']
    packages_installed = []
    packages_failed =[]
    subprocess.call("pip3 uninstall jwt", shell=True)
    for package in packages:
<<<<<<< HEAD
        command = "pip3 install {} ".format(package)
        res = subprocess.call(command, shell = True)
=======
        command = "pip3 install {} >/tmp/pip3-stdout 2>/tmp/pip3-stderr".format(package)
        res = subprocess.call(command, shell=True)
>>>>>>> 0ef021e1165cbaa612e5128bc48d6abfbb7b887b
        if res == 0:
            print("Package {} install SUCCESS Returned Value: {} ".format(package, res))
            packages_installed.append(package)
        else:
            print("Package {} install FAILED Returned Value: {} ".format(package, res))
            print("To see errors try: pip3 install {}".format(package))
            packages_failed.append(package)

    print("Install Complete")
    print("Packages Installed Success: {}\n".format(packages_installed))
    print("Packages Failed (Some scripts may not need these packages): {}".format(packages_failed))

if __name__ == "__main__":
    main()
