#!/usr/bin/env python3
import subprocess
def main():
    command = "pip3 install pandas plotly numpy paramiko bokeh websocket-client pyarrow xlsxwriter pyshark influxdb influxdb_client --upgrade"
    res = subprocess.call(command, shell = True)

    print("Returned Value: ", res)

if __name__ == "__main__":
    main()
