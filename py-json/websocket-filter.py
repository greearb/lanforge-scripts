#!/usr/bin/python3
'''
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                                                                             -
# Example of how to filter messages from the :8081 websocket                  -
#                                                                             -
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
You will need websocket-client:
apt install python3-websocket
'''

import sys
if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()
import argparse
import json
import logging
import time
from time import sleep
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import pprint
import LANforge
from LANforge import LFRequest
from LANforge import LFUtils
from LANforge.LFUtils import NA
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def main():
    host = "ct524-debbie.jbr.candelatech.com"
    base_url = "ws://%s:8081"%host
    websock = None

    ignore=(
        "scan finished",
        "scan started"
        "CTRL-EVENT-SCAN-STARTED",
        "CTRL-EVENT-SSID-TEMP-DISABLED",
        "new station",
        "delstation",
        "ping",
        )
    interesting=(
        "Trying to authenticate",
        "auth: timed out",
        'link DOWN',
        'link UP',
        'wifi-event'
        )

    # open websocket
    start_websocket(base_url, websock)
    if (websock is not None):
        print ("Started websocket")
    else:
        print ("Failed to start websocket, bye.")
        exit(1)

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
def sock_filter(wsock, text):
    debug = 1
    for test in ignore:
        print (".")
        if (test in text):
            if (debug):
                print ("ignoring ",text)
            return;

    try:
        message = json.loads(text)
        #if (("time" in message) and ("timestamp" in message)):
        #    return
        if ("wifi-event" in message):
            for test in ignore:
                if (test in message["wifi-event"]):
                    return;
            print (message["wifi-event"], "\n")
        else:
            print ("\nUnhandled: ")
            LFUtils.debug_printer.pprint(message)

    except Exception:
        print ("# ----- Not JSON: ----- ----- ----- ----- ----- ----- ----- ----- ----- -----\n")
        print (text)
        print ("# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----\n")
        return

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
def m_error(wsock, err):
    print ("# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----\n")
    LFUtils.debug_printer.pprint(err)
    print ("# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----\n")

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
def m_open(wsock):
    def run(*args):
        time.sleep(0.1)
        #ping = json.loads();
        wsock.send('{"text":"ping"}')
    thread.start_new_thread(run, ())

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
def m_close(wsock):
    LFUtils.debug_printer.pprint(wsock)

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
def start_websocket(uri, *websock):
    #websocket.enableTrace(True)
    websock = websocket.WebSocketApp(uri,
        on_message = sock_filter,
        on_error = m_error,
        on_close = m_close)
    websock.on_open = m_open
    websock.run_forever()


# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
if __name__ == '__main__':
    main()


####
####
####