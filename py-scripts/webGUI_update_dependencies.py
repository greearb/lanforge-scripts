#!/usr/bin/env python3

import subprocess
import argparse
import os


def main():
    parser = argparse.ArgumentParser(
        prog="update_dependencies.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description='''
        NAME: webGUI_update_dependencies.py

        PURPOSE:  Installs python3 webGUI package dependencies

        OUTPUT: List of successful and unsuccessful installs

        NOTES: Install as root
        '''
    )
    parser.add_argument('--pyjwt', help='Install PyJWT which is necessary for GhostRequest', action="store_true")

    args = parser.parse_args()

    print("Installing webGUI Python3 Dependencies")

    # These don't work on my F36 LANforge system
    # Possibly they are not required?
    # 'celery' (conflicts with OS's 'click'.  But I installed rpm celery pkg, maybe this is good enough?)
    # 'python-contrab':  pip doesn't know anything about it evidently.
    # 'django-celery-results':  Version 2.4.0 will install on F36
    
    packages = ['pandas', 'plotly', 'numpy', 'cryptography', 'paramiko', 'websocket-client',
                'xlsxwriter', 'pyshark', 'influxdb', 'influxdb-client', 'matplotlib', 'pdfkit', 'pip-search',
                'pyserial','pexpect-serial', 'scp','scipy','simple-geometry','kaleido','psutil','aiohttp','bs4',
                'django','django-celery-beat','django-enum-choices','django-timezone-field',
                'flower','jsonfield','matplotlib','psycopg2-binary','wheel','pytest','pytest-html','pytest-json',
                'django-celery-results==2.4.0',
                'pytest-json-report','pytest-metadata','python-dateutil','requests','pillow','tabulate','selenium']
    if args.pyjwt:
        packages.append('pyjwt')
    else:
        print('Not installing PyJWT')
    packages_installed = []
    packages_failed = []
    subprocess.call("pip3 uninstall jwt", shell=True)
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
