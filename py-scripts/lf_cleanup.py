#!/usr/bin/env python3
r"""
NAME:       lf_cleanup.py

PURPOSE:    Remove present test configuration, resetting system(s) to a reproducible base state.

EXAMPLE:
            # Remove all stations with CLI
            ./lf_cleanup.py --sta

            # Remove all stations with CLI for a specific resource
            ./lf_cleanup.py --sta --resource 2

            # Full cleanup (ports, L3 CXs/endpoints, L4-7 endpoints with CLI
            ./lf_cleanup.py --sanitize

            # Remove all CXs and endpoints with CLI
            ./lf_cleanup.py --cxs

            # Remove all endpoints with CLI
            ./lf_cleanup.py --endp

            # Remove all bridge with CLI
            ./lf_cleanup.py --br

            # Remove all STAs with unexpected names with CLI (often from misuse of or bugs in automation)
            # This includes names 'phy' (not 'wiphy') and '1.1.eth'
            ./lf_cleanup.py --misc

            # Remove all stations with JSON
            "args": ["--mgr", "192.168.30.12", "--resource", "1", "--sta"]

            # Full cleanup (ports, L3 CXs/endpoints, L4-7 endpoints with JSON
            "args": ["--mgr", "192.168.30.12", "--resource", "1", "--sanitize"]

            # Remove all CXs and endpoints with JSON
            "args": ["--mgr", "192.168.30.12", "--resource", "1", "--cxs"]

            # Remove all endpoints with JSON
            "args": ["--mgr", "192.168.30.12", "--resource", "1", "--endp"]

            # Remove all bridge with JSON
            "args": ["--mgr", "192.168.30.12", "--resource", "1", "--br"]

            # Remove all STAs with unexpected names with CLI (often from misuse of or bugs in automation)
            # This includes names 'phy' (not 'wiphy') and '1.1.eth'
            "args": ["--mgr", "192.168.30.12", "--resource", "1", "--misc"]

SCRIPT_CLASSIFICATION:
            Deletion

SCRIPT_CATEGORIES:
            Functional

NOTES:      The script will only cleanup what is present in the GUI. If object creation (e.g. port or CX)
            is in process but the object is not yet present in the GUI, then this script may need to be run
            multiple times for deletion to take effect.

VERIFIED_ON:
            Working date:   03/17/2023
            Build version:  5.4.6
            Kernel version: 5.19.17+

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2025 Candela Technologies Inc
"""
import sys
import os
import importlib
import argparse
import time
import logging

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")


class lf_clean(Realm):
    def __init__(self,
                 host="localhost",
                 port=8080,
                 resource=None,
                 clean_cxs=None,
                 clean_endp=None,
                 clean_sta=None,
                 clean_port_mgr=None,
                 clean_misc=None):
        super().__init__(lfclient_host=host, lfclient_port=port)

        self.host = host
        self.port = port
        self.resource = resource
        self.clean_cxs = clean_cxs
        self.clean_endp = clean_endp
        self.clean_sta = clean_sta
        self.clean_port_mgr = clean_port_mgr
        self.clean_misc = clean_misc
        self.cxs_done = False
        self.endp_done = False
        self.sta_done = False
        self.port_mgr_done = False
        self.br_done = False
        self.misc_done = False

    def layer4_endp_clean(self):
        """Delete L4-7 endpoints (see the Layer 4-7 tab of the LANforge GUI)."""
        still_looking_endp = True
        iterations_endp = 0

        while still_looking_endp and iterations_endp <= 10:
            iterations_endp += 1
            logger.debug(f"layer4_endp_clean: iterations_endp: {iterations_endp}")
            layer4_endp_json = super().json_get("layer4")
            # logger.info(layer4_endp_json)
            if layer4_endp_json is not None and 'empty' not in layer4_endp_json:
                logger.info("Removing old Layer 4-7 endpoints")
                layer4_endp_json.pop("handler")
                layer4_endp_json.pop("uri")
                if 'warnings' in layer4_endp_json:
                    layer4_endp_json.pop("warnings")

                for name in list(layer4_endp_json):
                    if name == 'endpoint':
                        # Single endpoint
                        if type(layer4_endp_json['endpoint']) is dict:
                            endp_name = layer4_endp_json['endpoint']['name']

                            # Delete Layer 4-7 cross connection:
                            req_url = "cli-json/rm_cx"
                            data = {
                                "test_mgr": "default_tm",
                                "cx_name": "CX_" + endp_name
                            }
                            logger.info("Removing {endp_name}...".format(endp_name="CX_" + endp_name))
                            super().json_post(req_url, data)

                            # Delete Layer 4-7 endpoint
                            req_url = "cli-json/rm_endp"
                            data = {
                                "endp_name": endp_name
                            }
                            logger.info("Removing {endp_name}...".format(endp_name=endp_name))
                            super().json_post(req_url, data)

                        # More than one endpoint
                        else:
                            for endp_num in layer4_endp_json['endpoint']:
                                # get L4-Endp name:
                                for endp_values in endp_num.values():
                                    endp_name = endp_values['name']
                                    if endp_name != '':
                                        # Delete Layer 4-7 cross connections:
                                        req_url = "cli-json/rm_cx"
                                        data = {
                                            "test_mgr": "default_tm",
                                            "cx_name": "CX_" + endp_name
                                        }
                                        logger.info("Removing {endp_name}...".format(endp_name="CX_" + endp_name))
                                        super().json_post(req_url, data)

                                        # Delete Layer 4-7 endpoint
                                        req_url = "cli-json/rm_endp"
                                        data = {
                                            "endp_name": endp_name
                                        }
                                        logger.info("Removing {endp_name}...".format(endp_name=endp_name))
                                        super().json_post(req_url, data)
                time.sleep(1)
            else:
                logger.info("No further endpoints found")
                still_looking_endp = False
                logger.debug(f"clean_endp still_looking_endp {still_looking_endp}")

            if not still_looking_endp:
                self.endp_done = True

            return still_looking_endp

    def cxs_clean(self):
        """
        Deletes Layer-3 CXs. Does not remove Layer-3 endpoints.

        See the 'Layer-3' and 'L3 Endps' tabs in the LANforge GUI.
        NOTE: Previously this function removed Layer-3 endpoints as well.
        """
        still_looking_cxs = True
        iterations_cxs = 1

        while still_looking_cxs and iterations_cxs <= 10:
            iterations_cxs += 1
            logger.debug("cxs_clean: iterations_cxs: {iterations_cxs}".format(iterations_cxs=iterations_cxs))
            cx_json = super().json_get("cx")
            # endp_json = super().json_get("endp")
            if cx_json is not None and 'empty' not in cx_json:
                logger.debug(cx_json.keys())
                logger.debug("Removing old cross connects")

                # delete L3-CX based upon the L3-Endp name & the resource value from
                # the e.i.d of the associated L3-Endps
                cx_json.pop("handler")
                cx_json.pop("uri")
                if 'warnings' in cx_json:
                    cx_json.pop("warnings")

                for cx_name in list(cx_json):
                    cxs_eid = cx_json[cx_name]['entity id']
                    cxs_eid_split = cxs_eid.split('.')
                    resource_eid = str(cxs_eid_split[1])
                    # logger.info(resource_eid)

                    if resource_eid in self.resource or 'all' in self.resource:
                        # remove Layer-3 cx:
                        req_url = "cli-json/rm_cx"
                        data = {
                            "test_mgr": "default_tm",
                            "cx_name": cx_name
                        }
                        logger.debug(f"Removing {cx_name}")
                        super().json_post(req_url, data)

                time.sleep(5)
            else:
                logger.info("No further Layer-3 CXs found")
                still_looking_cxs = False
                logger.debug(f"clean_cxs still_looking_cxs {still_looking_cxs}")

            if not still_looking_cxs:
                self.cxs_done = True

            return still_looking_cxs

    def get_json1(self):
        response = self.json_get("port/all")
        return response

    def layer3_endp_clean(self):
        """
        Delete Layer-3 endpoints with no associated Layer-3 CX.

        To delete a Layer-3 traffic pair in full with this function,
        first cleanup the CX then cleanup its associated Layer-3 endpoints.
        See the 'Layer-3' and 'L3 Endps' tabs in the LANforge GUI.
        """
        still_looking_endp = True
        iterations_endp = 0

        while still_looking_endp and iterations_endp <= 10:
            iterations_endp += 1
            logger.debug("layer3_endp_clean: iterations_endp: {iterations_endp}".format(iterations_endp=iterations_endp))
            endp_json = super().json_get("endp")
            # logger.info(endp_json)
            if endp_json is not None:
                logger.debug("Removing old Layer 3 endpoints")

                # Single endpoint
                if type(endp_json['endpoint']) is dict:
                    endp_name = endp_json['endpoint']['name']
                    req_url = "cli-json/rm_endp"
                    data = {
                        "endp_name": endp_name
                    }
                    # logger.info(data)
                    logger.debug(f"Removing {endp_name}")
                    super().json_post(req_url, data)

                # More than one endpoint
                else:
                    for name in list(endp_json['endpoint']):
                        endp_name = list(name)[0]
                        if name[list(name)[0]]["name"] == '':
                            continue
                        req_url = "cli-json/rm_endp"
                        data = {
                            "endp_name": endp_name
                        }
                        # logger.info(data)
                        logger.debug(f"Removing {endp_name}")
                        super().json_post(req_url, data)
                time.sleep(1)
            else:
                logger.info("No further Layer-3 endpoints found")
                still_looking_endp = False
                logger.debug(f"layer3_clean_endp still_looking_endp {still_looking_endp}")

            if not still_looking_endp:
                self.endp_done = True

            return still_looking_endp

    def sta_clean(self):
        still_looking_sta = True
        iterations_sta = 0

        while still_looking_sta and iterations_sta <= 10:
            iterations_sta += 1
            logger.debug(f"sta_clean: iterations_sta: {iterations_sta}")
            try:
                sta_json = super().json_get("/port/?fields=alias")['interfaces']
                # logger.info(sta_json)
            except TypeError:
                # TODO: When would this be the case
                sta_json = None
                logger.warning("sta_json set to None")

            # TODO: Refactor this to make common w/ port removal
            #       And delete on type not on alias
            # get and remove current stations
            if sta_json is not None:
                logger.debug("Removing old stations")
                for name in list(sta_json):
                    for alias in list(name):
                        info = self.name_to_eid(alias)
                        sta_resource = str(info[1])
                        if sta_resource in self.resource or 'all' in self.resource:
                            # logger.info("alias {alias}".format(alias=alias))
                            if 'sta' in alias:
                                info = self.name_to_eid(alias)
                                req_url = "cli-json/rm_vlan"
                                data = {
                                    "shelf": info[0],
                                    "resource": info[1],
                                    "port": info[2]
                                }
                                # logger.info(data)
                                logger.debug(f"Removing {alias}")
                                super().json_post(req_url, data)
                            if 'wlan' in alias:
                                info = self.name_to_eid(alias)
                                req_url = "cli-json/rm_vlan"
                                data = {
                                    "shelf": info[0],
                                    "resource": info[1],
                                    "port": info[2]
                                }
                                # logger.info(data)
                                logger.debug(f"Removing {alias}")
                                super().json_post(req_url, data)

                            # TODO: This isn't a station type port
                            if 'moni' in alias:
                                info = self.name_to_eid(alias)
                                req_url = "cli-json/rm_vlan"
                                data = {
                                    "shelf": info[0],
                                    "resource": info[1],
                                    "port": info[2]
                                }
                                # logger.info(data)
                                logger.debug(f"Removing {alias}")
                                super().json_post(req_url, data)

                            # TODO: Move this to misc cleanup logic
                            if 'Unknown' in alias:
                                info = self.name_to_eid(alias)
                                req_url = "cli-json/rm_vlan"
                                data = {
                                    "shelf": info[0],
                                    "resource": info[1],
                                    "port": info[2]
                                }
                                # logger.info(data)
                                logger.debug(f"Removing {alias}")
                                super().json_post(req_url, data)
                time.sleep(1)
            else:
                logger.info("No further stations found")
                still_looking_sta = False
                logger.debug(f"clean_sta still_looking_sta {still_looking_sta}")

            if not still_looking_sta:
                self.sta_done = True

            return still_looking_sta

    # cleans all gui or script created objects from Port Mgr tab
    def port_mgr_clean(self):
        """
        Delete all virtual interfaces.

        Read differently, this function attempts to delete anything
        that isn't a physical port on the system.
        """
        still_looking_san = True
        iterations_san = 0

        while still_looking_san and iterations_san <= 10:
            iterations_san += 1
            try:
                port_mgr_json = super().json_get("/port/?fields=port+type,alias")['interfaces']
                # logger.info(port_mgr_json)
                # logger.info(len(port_mgr_json))
            except TypeError:
                port_mgr_json = None
                logger.warning("port_mgr_json set to None")

            # get and remove LF Port Mgr objects
            if port_mgr_json is not None:
                logger.debug("Removing old stations ")
                for name in list(port_mgr_json):
                    # logger.info(name)
                    # alias is the eid (ex: 1.1.eth0)
                    for alias in list(name):
                        # logger.info(alias)
                        port_type = name[alias]['port type']
                        # logger.info(port_type)
                        if port_type != 'Ethernet' and port_type != 'WIFI-Radio' and port_type != 'NA':
                            info = self.name_to_eid(alias)
                            port_mgr_resource = str(info[1])
                            if port_mgr_resource in self.resource or 'all' in self.resource:
                                req_url = "cli-json/rm_vlan"
                                data = {
                                    "shelf": info[0],
                                    "resource": info[1],
                                    "port": info[2]
                                }
                                # logger.info(data)
                                logger.debug(f"Removing {alias}")
                                super().json_post(req_url, data)
                time.sleep(1)
            else:
                logger.info("No further ports found")
                still_looking_san = False
                logger.debug(f"port_mgr_clean still_looking_san {still_looking_san}")

            if not still_looking_san:
                self.port_mgr_done = True

            return still_looking_san

    def bridge_clean(self):
        still_looking_br = True
        iterations_br = 0

        # TODO: Merge this w/ prot deletion logic
        while still_looking_br and iterations_br <= 10:
            iterations_br += 1
            logger.debug(f"bridge_clean: iterations_br: {iterations_br}")
            try:
                # br_json = super().json_get("port/1/1/list?field=alias")['interfaces']
                br_json = super().json_get("/port/?fields=port+type,alias")['interfaces']
            except TypeError:
                br_json = None

            # get and remove current stations
            if br_json is not None:
                # logger.info(br_json)
                logger.debug("Removing old bridges")
                for name in list(br_json):
                    for alias in list(name):
                        port_type = name[alias]['port type']
                        # if 'br' in alias:
                        if 'Bridge' in port_type:
                            # logger.info(alias)
                            info = self.name_to_eid(alias)
                            bridge_resource = str(info[1])
                            if bridge_resource in self.resource or 'all' in self.resource:
                                req_url = "cli-json/rm_vlan"
                                data = {
                                    "shelf": info[0],
                                    "resource": info[1],
                                    "port": info[2]
                                }
                                # logger.info(data)
                                logger.debug(f"Removing {alias}")
                                super().json_post(req_url, data)
                time.sleep(1)
            else:
                logger.info("No further bridge ports found")
                still_looking_br = False
                logger.debug(f"clean_bridge still_looking_br {still_looking_br}")

            if not still_looking_br:
                self.br_done = True

            return still_looking_br

    # Some test have various station names or a station named 1.1.eth2
    def misc_clean(self):
        still_looking_misc = True
        iterations_misc = 0

        while still_looking_misc and iterations_misc <= 10:
            iterations_misc += 1
            logger.debug(f"misc_clean: iterations_misc: {iterations_misc}")
            try:
                # misc_json = super().json_get("port/1/1/list?field=alias")['interfaces']
                misc_json = super().json_get("/port/?fields=alias")['interfaces']
            except TypeError:
                misc_json = None

            # get and remove current stations
            if misc_json is not None:
                # logger.info(misc_json)
                logger.debug("Removing misc station names phy, 1.1.eth (malformed station name) ")
                for name in list(misc_json):
                    for alias in list(name):
                        if 'phy' in alias and 'wiphy' not in alias:
                            # logger.info(alias)
                            info = self.name_to_eid(alias)
                            misc_resource = str(info[1])
                            if misc_resource in self.resource or 'all' in self.resource:
                                req_url = "cli-json/rm_vlan"
                                data = {
                                    "shelf": info[0],
                                    "resource": info[1],
                                    "port": info[2]
                                }
                                # logger.info(data)
                                logger.debug(f"Removing {alias}")
                                super().json_post(req_url, data)

                        if '1.1.1.1.eth' in alias:
                            logger.debug(f"alias 1.1.1.1.eth {alias}")
                            # need to hand construct for delete.
                            info = alias.split('.')
                            logger.debug(f'info {info}')
                            req_url = "cli-json/rm_vlan"
                            # info_2 = "{info2}.{info3}.{info4}".format(info2=info[2], info3=info[3], info4=info[4])
                            misc_resource = str(info[3])
                            if misc_resource in self.resource or 'all' in self.resource:
                                data = {
                                    "shelf": info[2],
                                    "resource": info[3],
                                    "port": info[4]
                                }
                                # logger.info(data)
                                logger.debug(f"Removing {alias}")
                                super().json_post(req_url, data)
                time.sleep(1)
            else:
                logger.info("No further miscellaneous ports found")
                still_looking_misc = False
                logger.debug(f"clean_misc still_looking_misc {still_looking_misc}")

            if not still_looking_misc:
                self.misc_done = True

            return still_looking_misc

    def sanitize_all(self):
        """Run comprehensive, multi-step cleanup

            1: Delete Layer-3 CXs
            2: Delete Layer-3 endpoints
            3: Delete Layer-4 endpoints
            4: Delete ports

            NOTE: When deleting ports before Layer-3 CXs, any CXs
                  which use the deleted ports will then appear as phantom
        """
        # 1. clean Layer-3 tab:
        finished_clean_cxs = self.cxs_clean()
        logger.debug(f"clean_cxs: finished_clean_cxs {finished_clean_cxs}")

        # 2. clean L3 Endps tab:
        finished_clean_endp = self.layer3_endp_clean()
        logger.debug(f"layer3_clean_endp: finished_clean_endp {finished_clean_endp}")

        # 3. clean Layer 4-7 tab:
        finished_clean_l4 = self.layer4_endp_clean()
        logger.debug(f"clean_l4_endp: finished_clean_l4 {finished_clean_l4}")

        # 4. clean Port Mgr tab:
        finished_clean_port_mgr = self.port_mgr_clean()
        logger.debug(f"clean_sta: finished_clean_port_mgr {finished_clean_port_mgr}")


def parse_args():
    parser = argparse.ArgumentParser(
        prog='lf_cleanup.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Clean up cxs and endpoints
            ''',
        description=r'''
NAME:       lf_cleanup.py

PURPOSE:    Remove present test configuration, resetting system(s) to
            a reproducible base state.

EXAMPLE:
            # Remove all stations with CLI
            ./lf_cleanup.py --sta

            # Remove all stations with CLI for a specific resource
            ./lf_cleanup.py --sta --resource 2

            # Full cleanup (ports, L3 CXs/endpoints, L4-7 endpoints with CLI
            ./lf_cleanup.py --sanitize

            # Remove all CXs and endpoints with CLI
            ./lf_cleanup.py --cxs

            # Remove all endpoints with CLI
            ./lf_cleanup.py --endp

            # Remove all bridge with CLI
            ./lf_cleanup.py --br

            # Remove all STAs with unexpected names with CLI (often from misuse of or bugs in automation)
            # This includes names 'phy' (not 'wiphy') and '1.1.eth'
            ./lf_cleanup.py --misc

            # Remove all stations with JSON
            "args": ["--mgr", "192.168.30.12", "--resource", "1", "--sta"]

            # Full cleanup (ports, L3 CXs/endpoints, L4-7 endpoints with JSON
            "args": ["--mgr", "192.168.30.12", "--resource", "1", "--sanitize"]

            # Remove all CXs and endpoints with JSON
            "args": ["--mgr", "192.168.30.12", "--resource", "1", "--cxs"]

            # Remove all endpoints with JSON
            "args": ["--mgr", "192.168.30.12", "--resource", "1", "--endp"]

            # Remove all bridge with JSON
            "args": ["--mgr", "192.168.30.12", "--resource", "1", "--br"]

            # Remove all STAs with unexpected names with CLI (often from misuse of or bugs in automation)
            # This includes names 'phy' (not 'wiphy') and '1.1.eth'
            "args": ["--mgr", "192.168.30.12", "--resource", "1", "--misc"]

SCRIPT_CLASSIFICATION:
            Deletion

SCRIPT_CATEGORIES:
            Functional

NOTES:      The script will only cleanup what is present in the GUI. If object creation (e.g. port or CX)
            is in process but the object is not yet present in the GUI, then this script may need to be run
            multiple times for deletion to take effect.

VERIFIED_ON:
            Working date:   03/17/2023
            Build version:  5.4.6
            Kernel version: 5.19.17+

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2025 Candela Technologies Inc
            ''')
    # Base options
    parser.add_argument('--mgr',
                        '--lfmgr',
                        dest='mgr',
                        help='--mgr <hostname for where LANforge GUI is running>',
                        default='localhost')

    # Cleanup configuration options
    parser.add_argument('--res',
                        '--resource',
                        dest='resource',
                        help='--resource <realm resource> to clear a specific resource, or --resource <all> to cleanup all resources',
                        default='all')
    parser.add_argument('--cx',
                        '--cxs',
                        dest='cxs',
                        help="Delete all Layer-3 CXs and Layer-3 endpoints",
                        action='store_true')
    parser.add_argument('--l3_endp',
                        help="Delete all Layer-3 endpoints with no associated L3 CX",
                        action='store_true')
    parser.add_argument('--sta',
                        '--station',
                        '--stations',
                        dest='sta',
                        help="Delete all WiFi stations",
                        action='store_true')
    parser.add_argument('--port',
                        '--ports',
                        '--port_mgr',
                        dest='port_mgr',
                        help="Delete all virtual ports (e.g. WiFi station, MAC-VLAN, virtual AP, bridge). "
                             "Does not delete physical ports (e.g. Ethernet, WiFi radio)",
                        action='store_true')
    parser.add_argument('--br',
                        '--bridge',
                        '--bridges',
                        dest='br',
                        help="Delete all bridge ports",
                        action='store_true')
    parser.add_argument('--misc',
                        help="Attempts to delete stations w/ misconfigured names",
                        action='store_true')
    parser.add_argument('--layer4',
                        help="Delete all created L4-7 endpoints ",
                        action='store_true')
    parser.add_argument('--sanitize',
                        help="Equivalent to '--port_mgr', '--cxs', and '--layer4'",
                        action='store_true')
    parser.add_argument('--sleep',
                        help="Time in seconds to sleep after cleanup",
                        default=0)

    # Logging configuration options
    parser.add_argument("--debug",
                        help="Enable debug logging",
                        action="store_true")
    parser.add_argument("--lf_logger_config_json",
                        help="Logger JSON configuration file")
    parser.add_argument('--log_level', default=None,
                        help='Set logging level: debug | info | warning | error | critical')

    # Misc options
    parser.add_argument('--help_summary',
                        help='Show summary of what this script does',
                        default=None,
                        action="store_true")

    return parser.parse_args()


def validate_args(args):
    """Ensure arguments specified for program are valid."""
    if not (args.cxs
            or args.l3_endp
            or args.sta
            or args.br
            or args.misc
            or args.port_mgr
            or args.layer4
            or args.sanitize):
        logger.error("No required clean option specified. Re-run with '--help' for more information.")
        exit(1)


def main():
    help_summary = '''\
    This script is used for cleaning the cross-connections, layer-3-endpoints, stations and bridges in Lanforge.
    This script is also used to sanitize the lanforge unit, which means will clean the Port Mgr, Layer-3, L3 Endps,
    and Layer 4-7 tabs.
            '''

    args = parse_args()

    # Print help summary
    if args.help_summary:
        print(help_summary)
        exit(0)

    validate_args(args)

    # Configure logging
    logger_config = lf_logger_config.lf_logger_config()
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)
    if args.debug:
        logger_config.set_level("debug")

    clean = lf_clean(host=args.mgr,
                     resource=args.resource,
                     clean_cxs=args.cxs,
                     clean_endp=args.l3_endp,
                     clean_sta=args.sta,
                     clean_port_mgr=args.port_mgr,
                     clean_misc=args.misc)
    logger.debug("cleaning cxs: {cxs} endpoints: {endp} stations: {sta} start".format(cxs=args.cxs, endp=args.l3_endp, sta=args.sta))

    response = clean.get_json1()
    logger.debug(response)
    logger.debug("The objects that are present in the port Manager")
    for i in range(len(response["interfaces"])):
        response2 = list(response["interfaces"][i].keys())
        logger.debug(response2)

    if args.cxs:
        logger.info("Deleting Layer-3 CXs")
        logger.info("Requesting CX cleanup will also cleanup endpoints")
        clean.cxs_clean()
        clean.layer3_endp_clean()
    if args.l3_endp:
        logger.info("Deleting Layer-3 endpoints")
        clean.layer3_endp_clean()
    if args.sta:
        logger.info("Deleting stations")
        clean.sta_clean()
    if args.port_mgr:
        logger.info("Deleting ports")
        clean.port_mgr_clean()
    if args.br:
        logger.info("Deleting bridges")
        clean.bridge_clean()
    if args.misc:
        logger.info("Deleting miscellaneous ports")
        clean.misc_clean()
    if args.layer4:
        logger.info("Deleting Layer-4 endpoints")
        clean.layer4_endp_clean()
    if args.sanitize:
        logger.info("Deleting ports, Layer-3 CXs and endpoints, and Layer-4 endpoints")
        clean.sanitize_all()

    # Optional sleep after performing requested cleanup
    if args.sleep > 0:
        logger.info(f"Sleeping for {args.sleep} seconds post cleanup")
        time.sleep(args.sleep)

    logger.info("Requested cleanup complete")


if __name__ == "__main__":
    main()
