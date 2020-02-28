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
import traceback
import time
from time import sleep
import websocket
import re
try:
    import thread
except ImportError:
    import _thread as thread
import pprint
import LANforge
from LANforge import LFRequest
from LANforge import LFUtils
from LANforge.LFUtils import NA

ignore=[
    ": scan finished",
    ": scan started",
    "CTRL-EVENT-SCAN-STARTED",
    "SCAN-STARTED",
    "SSID-TEMP-DISABLED",
    "CTRL-EVENT-REGDOM-CHANGE",
    "CTRL-EVENT-SUBNET-STATUS-UPDATE",
    "new station",
    "del station",
    "ping",
    "deleted-alert",
    "regulatory domain change",
]
interesting=[
    "Trying to authenticate",
    "auth: timed out",
    "link DOWN",
    "link UP",
    'wifi-event'
]

rebank = {
    "ifname" : re.compile("IFNAME=(\S+)")
}
websock = None

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def main():
    global websock
    host = "localhost"
    base_url = "ws://%s:8081"%host
    resource_id = 1     # typically you're using resource 1 in stand alone realm

    parser = argparse.ArgumentParser(description="test creating a station")
    parser.add_argument("-m", "--host", type=str, help="json host to connect to")

    args = None
    try:
      args = parser.parse_args()
      if (args.host is not None):
         host = args.host,
         baseurl = base_url = "ws://%s:8081"%host
    except Exception as e:
      logging.exception(e)
      usage()
      exit(2)

    # open websocket
    websock = start_websocket(base_url, websock)


# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
def sock_filter(wsock, text):
    global ignore
    global interesting
    global rebank
    debug = 0
    station_name = None
    resource = None

    for test in ignore:
        if (test in text):
            if (debug):
                print ("                ignoring ",text)
            return;

    try:
        message = json.loads(text)
    except Exception as ex:
        print ("Json Exception: ", repr(ex))
        traceback.print_exc()

    try:
        # big generic filter for wifi-message or details keys
        try:
            if ("details" in message.keys()):
                for test in ignore:
                    if (test in message["details"]):
                        return;
        except KeyError:
            print ("Message lacks key 'details'")
        try:
            if ("wifi-event" in message.keys()):
                for test in ignore:
                    #print ("      is ",test, " in ", message["wifi-event"])
                    if (test in message["wifi-event"]):
                        return;
        except KeyError:
            print("Message lacks key 'wifi-event'" )

        if (("time" in message.keys()) and ("timestamp" in message.keys())):
            return

        if ("name" in message.keys()):
            station_name = message["name"]
        if ("resource" in message.keys()):
            resource = "1.", message["resource"]

        if ("event_type" in message.keys()):
            match_result = re.match(r'Port (\S+)', message["details"])
            if (match_result is not None):
                station_name = match_result.group(1)

            if (message["is_alert"]):
                print ("alert: ", message["details"])
                LFUtils.debug_printer.pprint(message)
                return
            else:
                print ("event: ", message["details"])
                LFUtils.debug_printer.pprint(message)
                if (" IP change from " in message["details"]):
                    if (" to 0.0.0.0" in messsage["details"]):
                        print ("e: %s.%s lost IP address",[resource,station_name])
                    else:
                        print ("e: %s.%s gained IP address",[resource,station_name])
                if ("Link DOWN" in message["details"]):
                    return # duplicates alert
                return

        if ("wifi-event" in message.keys()):
            if ((station_name is None) or (resource is None)):
                try:
                    print ("Searching for station name:")
                    match_result = re.match(r'^(1\.\d+):\s+(\S+)\s+\(phy', message["wifi-event"])
                    if (match_result is not None):
                        LFUtils.debug_printer.pprint(match_result)
                        LFUtils.debug_printer.pprint(match_result.group)
                        resource = match_result.group(1)
                        station_name = match_result.group(2)
                        print ("good!")
                    else:
                        match_result = re.match(r'(1\.\d+):\s+IFNAME=(\S+)\s+', message["wifi-event"])
                        LFUtils.debug_printer.pprint(match_result)
                        LFUtils.debug_printer.pprint(match_result.group)
                        if (match_result is not None):
                            resource = match_result.group(1)
                            station_name = match_result.group(2)
                            print ("ok!")
                        else:
                            station_name = 'no-sta'
                            resource_name = 'no-resource'
                            print ("bleh!")
                except Exception as ex2:
                    print ("No regex match:")
                    print(repr(ex2))
                    traceback.print_exc()
                    sleep(1)

            print ("Determined station name: as %s/%s"%[resource, station_name])

            if ("disconnected" in message["wifi-event"]):
                print ("Station %s.%s down"%[resource,station_name])
                return
            if ("Trying to authenticate" in message["wifi-event"]):
                print ("station %s.%s authenticating"%[resource,station_name])
                return
            print ("w: ", message["wifi-event"])
        else:
            print ("\nUnhandled: ")
            LFUtils.debug_printer.pprint(message)

    except KeyError as kerr:
        print ("# ----- Bad Key: ----- ----- ----- ----- ----- ----- ----- ----- ----- -----")
        print ("input: ",text)
        print (repr(kerr))
        traceback.print_exc()
        print ("# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----")
        sleep(1)
        return
    except json.JSONDecodeError as derr:
        print ("# ----- Decode err: ----- ----- ----- ----- ----- ----- ----- ----- ----- -----")
        print ("input: ",text)
        print (repr(derr))
        traceback.print_exc()
        print ("# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----")
        sleep(1)
        return
    except Exception as ex:
        print ("# ----- Exception: ----- ----- ----- ----- ----- ----- ----- ----- ----- -----")
        print(repr(ex))
        print ("input: ",text)
        LFUtils.debug_printer.pprint(message)
        traceback.print_exc()
        print ("# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----")
        sleep(1)
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
    print ("started websocket client")

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
def m_close(wsock):
    LFUtils.debug_printer.pprint(wsock)

# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
def start_websocket(uri, websock):
    #websocket.enableTrace(True)
    websock = websocket.WebSocketApp(uri,
        on_message = sock_filter,
        on_error = m_error,
        on_close = m_close)
    websock.on_open = m_open
    websock.run_forever()
    return websock


# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
if __name__ == '__main__':
    main()


####
####
####