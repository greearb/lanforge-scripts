#!/usr/bin/env python3
import subprocess
def main():
    command = "pip3 install pandas seaborn plotly numpy dash paramiko bokeh websocket-client pyarrow xlsxwriter datatable --upgrade"
    res = subprocess.call(command, shell = True)

    print("Returned Value: ", res)

if __name__ == "__main__":
    main()
