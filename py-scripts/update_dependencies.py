#!/usr/bin/env python3
import subprocess
def main():
    print("Installing Script Python3 Dependencies")
    packages = ['pandas', 'plotly', 'numpy', 'cryptography', 'paramiko', 'bokeh','pyarrow', 'websocket-client', 'xlsxwriter',\
         'pyshark', 'influxdb', 'influxdb-client', 'matplotlib', 'pdfkit', 'pip-search', 'pyserial', 'pexpect-serial' ]
    packages_installed = []
    packages_failed =[]
    for package in packages:
        command = "pip3 install {} ".format(package)#pandas plotly numpy paramiko bokeh websocket-client pyarrow xlsxwriter pyshark influxdb influxdb-client matplotlib pdfkit pip-search --upgrade"
        res = subprocess.call(command, shell = True)
        if res == 0:
            print("Package {} install SUCCESS Returned Value: {} ".format(package, res))
            packages_installed.append(package)
        else:
            print("Package {} install FAILED Returned Value: {} ".format(package, res))
            print("To see errors try: pip3 install {}".format(package))
            packages_failed.append(package)


    print("Install Complete")
    print("Packages Installed Success: {}".format(packages_installed))
    print("Packages Failed (Some scripts may not need these packages): {}".format(packages_failed))

if __name__ == "__main__":
    main()
