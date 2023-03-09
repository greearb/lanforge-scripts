#!/usr/bin/env python3
"""
NAME: chamber_ctl.py

PURPOSE:
    Examine or control a turntable associated with a Chamber View chamber.

EXAMPLES:
    Examine a chamber with a turntable using --info:
        ./chamber_ctl.py --host 127.0.0.1 --chamber TR-398 --info

    Rotate a turntable to a specific position using --position:
        ./chamber_ctl.py --host 127.0.0.1 --chamber TR-398 --speed 4 --position 90
        Positions should be positive values between 0.0 and 359.9.
        Speed is RPM between 0.1 - 7.0
    Rotate a turntable relative to its present position using --adjust:
        ./chamber_ctl.py --host 127.0.0.1 --chamber TR-398 --speed 4 --adjust -90
        Adjustments can be positive or negative.

    By default, this script will poll the position of the turntable once an position
    has been submitted. Option --no_settle sends the rotation command to the LANforge host
    without waiting for the turntable to reach its destination position.

Copyright 2023 Candela Technologies Inc
License: Free to distribute and modify. LANforge systems must be licensed.
"""
import sys
if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()
import os
import importlib
import argparse
import pprint
import logging
import time

sys.path.insert(1, "../")
sys.path.insert(1, "../../")

if "SHELL" in os.environ.keys():
    lanforge_api = importlib.import_module("lanforge_client.lanforge_api")
    from lanforge_client.lanforge_api import LFSession
    from lanforge_client.lanforge_api import LFJsonCommand
    from lanforge_client.lanforge_api import LFJsonQuery
    realm = importlib.import_module("py-json.realm")
    Realm = realm.Realm
else:
    import lanforge_api
    from lanforge_api import LFJsonCommand
    from lanforge_api import LFJsonQuery
    import realm
    from realm import Realm

lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
logger = logging.getLogger(__name__)


class Turntable(Realm):
    UNKNOWN_POSITION : int = -999
    CURRENT_POSITION : str = "reported rotation (deg)"

    def __init__(self,
                 api_session: lanforge_api.LFSession = None,
                 debug=False):
        super().__init__(lfclient_host=api_session.get_lfclient_host(),
                         lfclient_port=api_session.get_lfclient_port(),
                         debug_=debug,
                         _exit_on_error=True,
                         _exit_on_fail=False)

        self.api_session = api_session
        self.api_command = api_session.get_command()
        self.api_query = api_session.get_query()
        self.chamber_name: str = None
        self.turntable_position: float = Turntable.UNKNOWN_POSITION
        self.errors_warnings = []
        self.located_chamber: dict = None
        self.speed: float = self.UNKNOWN_POSITION
        self.position: float = self.UNKNOWN_POSITION
        self.adjust: float = self.UNKNOWN_POSITION
        self.found_chamber: bool = None
        self.no_settle: bool = False

    def build(self):
        pass

    def start(self, no_settle=None):
        logger.info("Locating chamber [%s]" % self.chamber_name)
        if not self.locate_chamber(chamber_name=self.chamber_name):
            logger.error("Unable to locate chamber, bye")
            sys.exit(1)
        # pprint.pprint(self.found_chamber)
        if not self.speed or self.speed == Turntable.UNKNOWN_POSITION:
            self.speed = float(self.found_chamber["rpm"])

        if self.adjust is None or self.adjust == Turntable.UNKNOWN_POSITION:
            self.adjust = 0

        if self.position is None or self.position == Turntable.UNKNOWN_POSITION:
            print("self.position[%s] assigning position to [%s][%s]" %
                (self.position,
                 self.found_chamber[Turntable.CURRENT_POSITION],
                 float(self.found_chamber[Turntable.CURRENT_POSITION])))
            self.position = float(self.found_chamber[Turntable.CURRENT_POSITION])

        if self.adjust != 0:
            if (self.position + self.adjust) < 0:
                self.position = 360 + (self.position + self.adjust)
            elif (self.position + self.adjust) > 359.9:
                if (self.position + self.adjust) == 360:
                    self.position = 0
                else:
                    self.position = (self.position + self.adjust) - 360
            else:
                self.position += self.adjust
        else:
            if self.position < 0:
                self.position = 360 + self.position
            elif self.position > 359.9:
                if self.position == 360:
                    self.position = 0
                else:
                    self.position = self.position - 360
        logger.info("Setting new chamber position")
        self.api_command.post_set_chamber(chamber=self.chamber_name,
                                          speed_rpm=self.speed,
                                          position=self.position)
        time.sleep(0.125)
        if no_settle is False:
            logging.warning("not waiting for chamber settings to take effect")
            return
        if float(self.found_chamber[Turntable.CURRENT_POSITION]) == float(self.position):
            logging.warning("requested position %s, current reported position is %s" % (self.position, self.found_chamber[Turntable.CURRENT_POSITION]))
            return

        max_wait_ms: int = 20000
        check_ms: int = 250
        last_position: float = float(self.found_chamber[Turntable.CURRENT_POSITION])
        start_ms: int = lanforge_api._now_ms()
        until_ms: int = start_ms + max_wait_ms
        now_ms: int = start_ms
        while now_ms <= until_ms:
            if not self.locate_chamber(self.chamber_name):
                print("chamber %s disappeared" % self.chamber_name)
                sys.exit(1)
            logger.info("Position %s dT %s" %
                         (float(self.found_chamber[Turntable.CURRENT_POSITION]),
                          until_ms - now_ms))
            if last_position != float(self.found_chamber[Turntable.CURRENT_POSITION]):
                last_position = float(self.found_chamber[Turntable.CURRENT_POSITION])
            if last_position == self.position:
                self.api_session.logger.warning("target position %s reached in %s ms" %
                                (self.position, (now_ms - start_ms)))
                break
            time.sleep(check_ms / 1000)
            now_ms = lanforge_api._now_ms()

        logger.warning("done")

    def set_speed(self, speed:float=None):
        """
        Set speed in RPM
        """
        self.speed = speed
    def set_position(self, position:float=None):
        """
        Sets the absolute rotation position of the table
        """
        logger.warning("setting position to %s" % position)
        self.position = position

    def adjust_position(self, position:float=None):
        """
        Add or subtract from the current position of the table
        """
        self.adjust = position

    def locate_chamber(self, chamber_name: str = None) -> bool:
        """
        Sets self.found_chamber with named chamber
        :param chamber_name: name/eid of chamber
        :return: False if unable to identify chamber and determine it has a turntable,
        True if able to identify chamber with a turntable

        """
        if not chamber_name:
            logger.error("No chamber name")
            return False
        result = self.api_query.get_chamber(eid_list=[chamber_name],
                                            errors_warnings=self.errors_warnings,
                                            debug=self.api_session.debug_on)
        if not result:
            logger.error("No chambers found")
            return False

        if self.debug:
            pprint.pprint(["located chamber might be this:", result])
        self.chamber_name = result["chamber"]
        self.found_chamber = result
        return True


def main():
    """
    Control or monitor a turntable
    """
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
        description='operate a turntable')
    parser.add_argument("--host", "--mgr", help='specify the GUI to connect to, assumes port 8080')
    parser.add_argument("--debug", action="store_true",
                        help='turn on debugging')
    parser.add_argument("--chamber", type=str,
                        help="""Chamber name (e.g. Chamber-0). Turntables are features of ChamberView chambers.
    There can be multiple resources per chamber, just like there can be multiple virtual routers per resource.
    Do NOT use the short name of the chamber or turntable you see in ChamberView (C0), use the FULL NAME
    of the turntable or chamber from the Modify Chamber window (Chamber-0).""")
    parser.add_argument("--info", default=False, action="store_true",
                        help="Display chamber turntable information")
    parser.add_argument("--position", type=float,
                        help="""Set the turn table position to an absolute position (between 0.0 and 359.9).
     Position resolution is 1/10th of a degree.""")
    parser.add_argument("--adjust", type=float,
                        help="""Adjust the turn table position a few degrees relative to current position.
    Negative degrees turn the table clockwise. Positive degrees turn the table anti-clockwise.
    If the table is at 270deg, '--adjust -5' will set the position of the table to 265deg.
     Position resolution is 1/10th of a degree.""")
    parser.add_argument("--speed", "--rpm", type=float,
                        help="Turn table rotation speed, in RPM. Minimum is 0.1 RPM, maximum is 7 RPM")
    parser.add_argument("--log_level", help="Set log level")
    parser.add_argument("--no_settle", default=False, action="store_true",
                        help="Exit script before turntable reports no movement for more than two pollings.")

    args = parser.parse_args()

    session = lanforge_api.LFSession(lfclient_url="http://%s:8080" % args.host,
                                     debug=args.debug,
                                     connection_timeout_sec=2.0,
                                     stream_errors=True,
                                     stream_warnings=True,
                                     require_session=True,
                                     exit_on_error=True)
    session.logger.enable(reserved_tag="json_get")
    session.logger.enable(reserved_tag="json_post")

    if not args.chamber:
        session.logger.error("No chamber name provided")
        sys.exit(1)
    if args.log_level is not None:
        logger.setLevel(args.log_level)
    this_turntable = Turntable(api_session=session, debug=args.debug)
    if not this_turntable.locate_chamber(chamber_name=args.chamber):
        print("Unable to find chamber [%s]" % args.chamber)
        sys.exit(1)
    if args.info and args.info is True:
        pprint.pprint(this_turntable.found_chamber)
        sys.exit(0)

    wait_to_settle: bool = True
    if args.no_settle and args.no_settle is False:
        wait_to_settle = args.no_settle

    if args.speed is not None:
        this_turntable.set_speed(args.speed)
    if args.position is not None:
        this_turntable.set_position(args.position)
    elif args.adjust is not None:
        this_turntable.adjust_position(args.adjust)
    this_turntable.start(no_settle=wait_to_settle)


if __name__ == "__main__":
    main()



