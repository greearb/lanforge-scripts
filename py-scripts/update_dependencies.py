#!/usr/bin/env python3
import subprocess
def main():
    command = "pip install pandas seaborn plotly numpy dash --upgrade"
    res = subprocess.call(command, shell = True)

    print("Returned Value: ", res)

if __name__ == "__main__":
    main()
