#!/usr/bin/env python3
import subprocess
def main():
    command = "pip3 install pandas plotly numpy paramiko bokeh websocket-client pyarrow xlsxwriter pyshark influxdb influxdb-client matplotlib pdfkit pip-search --upgrade"
    res = subprocess.call(command, shell = True)

    print("Returned Value: ", res)

if __name__ == "__main__":
    main()
