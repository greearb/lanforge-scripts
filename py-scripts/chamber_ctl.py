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
    CHAMBER_NAME     : str = "chamber"
    CURRENT_POSITION : str = "reported rotation (deg)"
    CURRENT_TILT     : str = "reported tilt (deg)"
    TURNTABLE_TYPE   : str = "turntable type"

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
        self._adjust_position: float = self.UNKNOWN_POSITION
        self.tilt: float = self.UNKNOWN_POSITION
        self._adjust_tilt: float = self.UNKNOWN_POSITION
        self.found_chamber: bool = None
        self.no_settle: bool = False

    def build(self):
        pass

    def start(self, no_settle=None):
        # Get current chamber values
        logger.info("Locating chamber [%s]" % self.chamber_name)
        if not self.locate_chamber(chamber_name=self.chamber_name):
            logger.error("Unable to locate chamber, bye")
            sys.exit(1)
        # pprint.pprint(self.found_chamber)

        # Set speed to current if not specified
        if not self.speed or self.speed == Turntable.UNKNOWN_POSITION:
            self.speed = float(self.found_chamber["rpm"])

        # Check if using adjust position function
        if self._adjust_position is None or self._adjust_position == Turntable.UNKNOWN_POSITION:
            self._adjust_position = 0

        # Check if using adjust tilt function
        if self._adjust_tilt is None or self._adjust_tilt == Turntable.UNKNOWN_POSITION:
            self._adjust_tilt = 0

        # User didn't pass a position angle, so use what turntable is currently at
        if self.position is None or self.position == Turntable.UNKNOWN_POSITION:
            print("self.position[%s] assigning position to [%s][%s]" %
                (self.position,
                 self.found_chamber[Turntable.CURRENT_POSITION],
                 float(self.found_chamber[Turntable.CURRENT_POSITION])))
            self.position = float(self.found_chamber[Turntable.CURRENT_POSITION])

        # User didn't pass a tilt angle, so use what turntable is currently at
        if self.tilt is None or self.tilt == Turntable.UNKNOWN_POSITION:
            print("self.tilt[%s] assigning tilt to [%s][%s]" %
                (self.tilt,
                 self.found_chamber[Turntable.CURRENT_TILT],
                 float(self.found_chamber[Turntable.CURRENT_TILT])))
            self.tilt = float(self.found_chamber[Turntable.CURRENT_TILT])

        self.position = Turntable.__validate_angle(self.position, self._adjust_position)
        self.tilt = Turntable.__validate_angle(self.tilt, self._adjust_tilt)

        # Warn if setting tilt for non 3D turntable
        if self.tilt is not None and self.tilt != 0 and self.found_chamber[Turntable.TURNTABLE_TYPE] != 4:
            logging.warning("attempting to set tilt for chamber %s with non 3D turntable type"
                            % self.found_chamber[Turntable.CHAMBER_NAME])


        logger.info("Setting new chamber position")
        self.api_command.post_set_chamber(chamber=self.chamber_name,
                                          speed_rpm=self.speed,
                                          position=self.position,
                                          tilt=self.tilt)
        time.sleep(0.125)
        if no_settle is False:
            logging.warning("not waiting for chamber settings to take effect")
            return

        if float(self.found_chamber[Turntable.CURRENT_POSITION]) == float(self.position) \
                and float(self.found_chamber[Turntable.CURRENT_TILT]) == float(self.tilt):
            logging.warning("requested position %s, current reported position is %s" % (self.position, self.found_chamber[Turntable.CURRENT_POSITION]))
            logging.warning("requested tilt %s, current reported position is %s" % (self.tilt, self.found_chamber[Turntable.CURRENT_TILT]))
            return

        self.__wait_for_settle()
        logger.warning("done")

    def __validate_angle(angle:float, adjust_angle:float):
        """
        Make sure whatever new angle the turntable will be at (position or tilt)
        does not result in turntable spinning more than a full rotation.

        Simulate wrap around if so (e.g. at 20 deg and request 390, just move to 30 [30=390-360])
        """
        if adjust_angle != 0:
            # Deal with potential wrap-arounds (don't want turntable to spin more than a full rotation)
            if (angle + adjust_angle) < 0:
                angle = 360 + (angle + adjust_angle)
            elif (angle + adjust_angle) > 359.9:
                if (angle + adjust_angle) == 360:
                    angle = 0
                else:
                    angle = (angle + adjust_angle) - 360
            else:
                angle += adjust_angle
        else:
            # Setting angle to specific point, make sure what's written is w/in [0,360)
            if angle < 0:
                angle = 360 + angle
            elif angle > 359.9:
                if angle == 360:
                    angle = 0
                else:
                    angle = angle - 360 # Simulate full rotation

        return angle

    def __wait_for_settle(self):
        """
        Wait for turntable to settle at requested position and/or tilt
        """
        max_wait_ms: int     = 20000
        check_ms: int        = 250
        last_position: float = float(self.found_chamber[Turntable.CURRENT_POSITION])
        last_tilt: float     = float(self.found_chamber[Turntable.CURRENT_TILT])
        start_ms: int        = lanforge_api._now_ms()
        until_ms: int        = start_ms + max_wait_ms
        now_ms: int          = start_ms

        while now_ms <= until_ms:
            if not self.locate_chamber(self.chamber_name):
                print("chamber %s disappeared" % self.chamber_name)
                sys.exit(1)
            logger.info("Position %s, Tilt %s, dT %s" %
                         (float(self.found_chamber[Turntable.CURRENT_POSITION]),
                          float(self.found_chamber[Turntable.CURRENT_TILT]),
                          until_ms - now_ms))

            if last_position != float(self.found_chamber[Turntable.CURRENT_POSITION]):
                last_position = float(self.found_chamber[Turntable.CURRENT_POSITION])

            if last_tilt != float(self.found_chamber[Turntable.CURRENT_TILT]):
                last_tilt = float(self.found_chamber[Turntable.CURRENT_TILT])

            if last_position == self.position and last_tilt == self.tilt:
                self.api_session.logger.warning("target position %s and tilt %s reached in %s ms" %
                                (self.position, self.tilt, (now_ms - start_ms)))
                break
            time.sleep(check_ms / 1000)
            now_ms = lanforge_api._now_ms()

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
        self._adjust_position = position

    def set_tilt(self, tilt:float=None):
        """
        Sets the absolute rotation tilt of the table
        """
        logger.warning("setting tilt to %s" % tilt)
        self.tilt = tilt

    def adjust_tilt(self, tilt:float=None):
        """
        Add or subtract from the current tilt of the table
        """
        self._adjust_tilt = tilt

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
        description='operate a LANForge-connected turntable.' \
                    'NOTE: \"--position\" and \"--tilt\" will override their adjust argument counterparts')
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
    parser.add_argument("--adjust_position", type=float,
                        help="""Adjust the turn table position a few degrees relative to current position.
    Negative degrees turn the table clockwise. Positive degrees turn the table anti-clockwise.
    If the table is at 270deg, '--adjust -5' will set the position of the table to 265deg.
     Position resolution is 1/10th of a degree.""")
    parser.add_argument("--tilt", type=float,
                        help="""Set the turn table tilt to an absolute position (between 0.0 and 359.9).
     Position resolution is 1/10th of a degree.""")
    parser.add_argument("--adjust_tilt", type=float,
                        help="""Adjust the turn table tilt a few degrees relative to current position.
                        Requires 845D turntable. See \"--adjust_position\" for more details""")
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

    # Validate arguments
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

    # Set request parameters
    if args.speed is not None:
        this_turntable.set_speed(args.speed)

    if args.position is not None:
        this_turntable.set_position(args.position)
    elif args.adjust_position is not None:
        this_turntable.adjust_position(args.adjust_position)

    if args.tilt is not None:
        this_turntable.set_tilt(args.tilt)
    elif args.adjust_tilt is not None:
        this_turntable.adjust_tilt(args.adjust_tilt)

    # Tell the turntable where to go and how quickly
    this_turntable.start(no_settle=wait_to_settle)


if __name__ == "__main__":
    main()



