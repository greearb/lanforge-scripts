#!/usr/bin/env python3
"""
This example is to demonstrate ws_generic_monitor to monitor events triggered by scripts,
This script when running, will monitor the events triggered by test_ipv4_connection.py

"""


import sys
import json
if 'py-json' not in sys.path:
    sys.path.append('../py-json')
from ws_generic_monitor import WS_Listener

reference = "test_ipv4_connection.py"
def main():
    WS_Listener(lfclient_host="localhost", _scriptname=reference, _callback=TestRun)


def TestRun(ws, message):
    if (str(message).__contains__(reference)):
        #print(message)
        temp = json.loads(message)
        event_message = str(temp['name']) + "/" + str(temp['details']) + "/" + str(temp['timestamp'])
        print(event_message)

if __name__ == "__main__":
    main()

