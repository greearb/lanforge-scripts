#!/usr/bin/env python3
import logging
import os
import sys
import time
"""
Script is a demonstration of how to operate a turn-table using the CLI admin command.
"""
if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

import importlib
import argparse
import pprint
sys.path.insert(1, "../../")

if "SHELL" in os.environ.keys():
    lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
    from lanforge_client.lanforge_api import LFSession
    from lanforge_client.lanforge_api import LFJsonCommand
    from lanforge_client.lanforge_api import LFJsonQuery
else:
    import lanforge_api
    from lanforge_api import LFJsonCommand
    from lanforge_api import LFJsonQuery



class turntable:
    UNKNOWN_POSITION : int = -999

    def __init__(self,
                 api_session : lanforge_api.LFSession = None,
                 debug=False):
        self.api_session = api_session
        self.api_command = api_session.get_command()
        self.api_query = api_session.get_query()
        self.chamber_name = None
        self.turntable_position = turntable.UNKNOWN_POSITION
        self.errors_warnings = []
        self.located_chamber = None

    def locate_chamber(self, chamber_name : str = None) -> bool:
        """

        :param chamber_name: name/eid of chamber
        :return: False if unable to identify chamber and determine it has a turntable,
        True if able to identify chamber with a turntable
        """
        if not chamber_name:
            self.api_session.logger.error("No chamber name")
            return False
        result = self.api_query.get_chamber(eid_list=[chamber_name],
                                            errors_warnings=self.errors_warnings,
                                            debug=self.api_session.debug_on)
        if not result:
            self.api_session.logger.error("No chambers found")
            return False

        pprint(["located chamber might be this:", result])

        return True

def main():
    """
    This is really just a simple loop

    :return: void
    """
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='tests creating wanlink')
    parser.add_argument("--host", "--mgr", help='specify the GUI to connect to, assumes port 8080')
    parser.add_argument("--debug", help='turn on debugging', action="store_true")
    parser.add_argument("--chamber",
                        help="""Chamber EID (1.1.1 or 1.1.Chamber-0). Turntables are features of ChamberView chambers.
    There can be multiple chambers per resource, just like there can be multiple virtual routers per resource.
    Do NOT use the name of the turntable you see in ChamberView (C0), use the full name
    of the chamber from the Modify Chamber window (Chamber-0).""")
    parser.add_argument("--info", help="Display chamber turntable information")
    parser.add_argument("--angle", help="Turn table angle. Angle resolution is 1/10th of a degree.")
    parser.add_argument("--speed", help="Turn table rotation speed, in RPM. Minimum is 0.1 RPM, maximum is 7 RPM")

    args = parser.parse_args()

    session = lanforge_api.LFSession(lfclient_url="http://%s:8080" % args.host,
                                     debug=args.debug,
                                     connection_timeout_sec=2.0,
                                     stream_errors=True,
                                     stream_warnings=True,
                                     require_session=True,
                                     exit_on_error=True)
    this_turntable = turntable(api_session=session, debug=args.debug)

    if not this_turntable.locate_chamber(chamber_name=args.chamber):
        print("Unable to find chamber [%s]" % args.chamber)
        sys.exit(1)



if __name__ == "__main__":
    main()
