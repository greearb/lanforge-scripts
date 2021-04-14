#!/usr/bin/env python3
"""
This file is intended to expose concurrency
problems in the /events/ URL handler
"""
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append('../py-json')

import argparse
from LANforge.lfcli_base import LFCliBase
from realm import Realm
import datetime
from datetime import datetime
import time
import pprint

class EventBreaker(Realm):
    def __init__(self,  host, port,
                 duration=None,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port)
        self.counter = 0
        self.test_duration=duration
        if (self.test_duration is None):
            raise ValueError("run wants numeric run_duration_sec")

    def create(self):
        pass

    def run(self):

        now = datetime.now()
        end_time = self.parse_time(self.test_duration) + now
        while datetime.now() < end_time:
            print ('.', end='')
            response = self.json_get("/events/all")
            if "events" not in response:
                # pprint.pprint(response)
                raise AssertionError("no events in response")
            events = response["events"]
            self.counter += 1
            for record in events:
                # pprint.pprint(record)

                for k in record.keys():
                    if record[k] is None:
                        print ('.', end='')
                        continue
                    # pprint.pprint( record[k])
                    if "NA" == record[k]["event"] \
                            or "NA" == record[k]["name"] \
                            or "NA" == record[k]["type"] \
                            or "NA" == record[k]["priority"]:
                        print( "id[%s]"%k, end='')
            print("counter %s"%self.counter)


    def cleanup(self):
        pass


def main():
    parser = LFCliBase.create_bare_argparse(
        prog='event_breaker.py',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--test_duration", help='test duration', default="30s" )
    # if optional_args is not None:
    args = parser.parse_args()

    event_breaker = EventBreaker(host=args.mgr,
                                 port=args.mgr_port,
                                 duration=args.test_duration,
                                 _debug_on=True,
                                 _exit_on_error=True,
                                 _exit_on_fail=True)
    event_breaker.create()
    event_breaker.run()
    event_breaker.cleanup()

if __name__ == "__main__":
    main()
