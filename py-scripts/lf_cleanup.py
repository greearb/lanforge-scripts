#!/usr/bin/env python3
"""
NAME: lf_cleanup.py

PURPOSE:
    clean up stations, cross connects and endpoints

EXAMPLE:
    clear all stations:
        ./lf_cleanup.py --mgr localhost --resource 1 --sta

    This example will clean the Port Mgr, Layer-3, L3 Endps, and Layer 4-7 LF GUI tabs:
        ./lf_cleanup.py --mgr localhost --resource 1 --sanitize

    clear all cxs and enps:
        ./lf_cleanup.py --mgr localhost --resource 1 --cxs

    clear all endps:
        ./lf_cleanup.py --mgr localhost --resource 1 --endp

    clear all bridges:
        ./lf_cleanup.py --mgr localhost --resource 1 --br

    clear sta with names phy (not wiphy) and 1.1.eth stations:
        ./lf_cleanup.py --mgr localhost --resource 1 --misc

JSON EXAMPLE:
    clear all stations:
        "args": ["--mgr","192.168.30.12","--resource","1","--sta"]

    This example will clean the Port Mgr, Layer-3, L3 Endps, and Layer 4-7 LF GUI tabs:
        "args": ["--mgr","192.168.30.12","--resource","1","--sanitize"]

    clear all cxs and enps:
        "args": ["--mgr","192.168.30.12","--resource","1","--cxs"]

    clear all endps:
        "args": ["--mgr","192.168.30.12","--resource","1","--endp"]

    clear all bridges:
        "args": ["--mgr","192.168.30.12","--resource","1","--br"]

    clear sta with names phy (not wiphy) and 1.1.eth stations:
        "args": ["--mgr","192.168.30.12","--resource","1","--misc"]

SCRIPT_CLASSIFICATION:  Deletion

SCRIPT_CATEGORIES:  Functional

NOTES:

    The default port is 8080
    The script will only cleanup what is present in the GUI,
     so it will need to iterate multiple times with script

VERIFIED_ON:
    Tested on 03/17/2023:
        kernel version: 5.19.17+
        gui version: 5.4.6

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc
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
        super().__init__(lfclient_host=host,
                         lfclient_port=port),
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

    # removes the endps from the LF gui Layer 4-7 tab (--layer4):
    def layer4_endp_clean(self):
        still_looking_endp = True
        iterations_endp = 0

        while still_looking_endp and iterations_endp <= 10:
            iterations_endp += 1
            logger.info("layer4_endp_clean: iterations_endp: {iterations_endp}".format(iterations_endp=iterations_endp))
            layer4_endp_json = super().json_get("layer4")
            # logger.info(layer4_endp_json)
            if layer4_endp_json is not None and 'empty' not in layer4_endp_json:
                logger.info("Removing old Layer 4-7 endpoints")
                layer4_endp_json.pop("handler")
                layer4_endp_json.pop("uri")
                if 'warnings' in layer4_endp_json:
                    layer4_endp_json.pop("warnings")

                for name in list(layer4_endp_json):
                    # if name != 'handler' and name != 'uri' and name != 'empty':
                    if name == 'endpoint':
                        # if there is only a single endpoint:
                        if type(layer4_endp_json['endpoint']) is dict:
                            endp_name = layer4_endp_json['endpoint']['name']
                            # Remove Layer 4-7 cross connection:
                            req_url = "cli-json/rm_cx"
                            data = {
                                "test_mgr": "default_tm",
                                "cx_name": "CX_" + endp_name
                            }
                            logger.info("Removing {endp_name}...".format(endp_name="CX_" + endp_name))
                            super().json_post(req_url, data)

                            # Remove Layer 4-7 endpoint
                            req_url = "cli-json/rm_endp"
                            data = {
                                "endp_name": endp_name
                            }
                            logger.info("Removing {endp_name}...".format(endp_name=endp_name))
                            super().json_post(req_url, data)

                        # if there are > 1 endpoints:
                        else:
                            for endp_num in layer4_endp_json['endpoint']:
                                # get L4-Endp name:
                                for endp_values in endp_num.values():
                                    endp_name = endp_values['name']
                                    if endp_name != '':
                                        # Remove Layer 4-7 cross connections:
                                        req_url = "cli-json/rm_cx"
                                        data = {
                                            "test_mgr": "default_tm",
                                            "cx_name": "CX_" + endp_name
                                        }
                                        logger.info("Removing {endp_name}...".format(endp_name="CX_" + endp_name))
                                        super().json_post(req_url, data)

                                        # Remove Layer 4-7 endpoint
                                        req_url = "cli-json/rm_endp"
                                        data = {
                                            "endp_name": endp_name
                                        }
                                        logger.info("Removing {endp_name}...".format(endp_name=endp_name))
                                        super().json_post(req_url, data)
                time.sleep(1)
            else:
                logger.info("No endpoints found to cleanup")
                still_looking_endp = False
                logger.info("clean_endp still_looking_endp {ednp_looking}".format(ednp_looking=still_looking_endp))
            if not still_looking_endp:
                self.endp_done = True
            return still_looking_endp

    # removes cxs from the Layer-3 gui tab, and the related l3-endps from the L3 Endps gui tab.
    # you have to remove CX before removing endpoints belonging to that CX
    # Note the code changed to only remove CX and not endpoints
    def cxs_clean(self):
        still_looking_cxs = True
        iterations_cxs = 1

        while still_looking_cxs and iterations_cxs <= 10:
            iterations_cxs += 1
            logger.info("cxs_clean: iterations_cxs: {iterations_cxs}".format(iterations_cxs=iterations_cxs))
            cx_json = super().json_get("cx")
            # endp_json = super().json_get("endp")
            if cx_json is not None and 'empty' not in cx_json:
                logger.info(cx_json.keys())
                logger.info("Removing old cross connects")
                # delete L3-CX based upon the L3-Endp name & the resource value from
                # the e.i.d of the associated L3-Endps
                cx_json.pop("handler")
                cx_json.pop("uri")
                if 'warnings' in cx_json:
                    cx_json.pop("warnings")
                # if type(endp_json['endpoint']) is dict:

                for cx_name in list(cx_json):
                    cxs_eid = cx_json[cx_name]['entity id']
                    cxs_eid_split = cxs_eid.split('.')
                    # cxs_eid_split[1] == realm resource value:
                    resource_eid = str(cxs_eid_split[1])
                    # logger.info(resource_eid)
                    if resource_eid in self.resource or 'all' in self.resource:
                        # remove Layer-3 cx:
                        req_url = "cli-json/rm_cx"
                        data = {
                            "test_mgr": "default_tm",
                            "cx_name": cx_name
                        }
                        # logger.info(data)
                        logger.info("Removing {cx_name}...".format(cx_name=cx_name))
                        super().json_post(req_url, data)

                time.sleep(5)
            else:
                logger.info("No cross connects found to cleanup")
                still_looking_cxs = False
                logger.info("clean_cxs still_looking_cxs {cxs_looking}".format(cxs_looking=still_looking_cxs))
            if not still_looking_cxs:
                self.cxs_done = True
            return still_looking_cxs

    # removes endpoints that do not have a related Layer-3 cxs from the L3 Endps gui tab.
    def get_json1(self):
        response = self.json_get("port/all")
        return response

    def layer3_endp_clean(self):
        still_looking_endp = True
        iterations_endp = 0

        while still_looking_endp and iterations_endp <= 10:
            iterations_endp += 1
            logger.info("layer3_endp_clean: iterations_endp: {iterations_endp}".format(iterations_endp=iterations_endp))
            endp_json = super().json_get("endp")
            # logger.info(endp_json)
            if endp_json is not None:
                logger.info("Removing old Layer 3 endpoints")
                # if there is only a single endpoint:
                if type(endp_json['endpoint']) is dict:
                    endp_name = endp_json['endpoint']['name']
                    req_url = "cli-json/rm_endp"
                    data = {
                        "endp_name": endp_name
                    }
                    # logger.info(data)
                    logger.info("Removing {endp_name}...".format(endp_name=endp_name))
                    super().json_post(req_url, data)

                # if there are > 1 endpoints:
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
                        logger.info("Removing {endp_name}...".format(endp_name=endp_name))
                        super().json_post(req_url, data)
                time.sleep(1)
            else:
                logger.info("No endpoints found to cleanup")
                still_looking_endp = False
                logger.info("layer3_clean_endp still_looking_endp {ednp_looking}".format(ednp_looking=still_looking_endp))
            if not still_looking_endp:
                self.endp_done = True
            return still_looking_endp

    def sta_clean(self):
        still_looking_sta = True
        iterations_sta = 0

        while still_looking_sta and iterations_sta <= 10:
            iterations_sta += 1
            logger.info("sta_clean: iterations_sta: {iterations_sta}".format(iterations_sta=iterations_sta))
            try:
                sta_json = super().json_get("/port/?fields=alias")['interfaces']
                # logger.info(sta_json)
            except TypeError:
                sta_json = None
                logger.info("sta_json set to None")

            # get and remove current stations
            if sta_json is not None:
                logger.info("Removing old stations ")
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
                                logger.info("Removing {alias}...".format(alias=alias))
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
                                logger.info("Removing {alias}...".format(alias=alias))
                                super().json_post(req_url, data)
                            if 'moni' in alias:
                                info = self.name_to_eid(alias)
                                req_url = "cli-json/rm_vlan"
                                data = {
                                    "shelf": info[0],
                                    "resource": info[1],
                                    "port": info[2]
                                }
                                # logger.info(data)
                                logger.info("Removing {alias}...".format(alias=alias))
                                super().json_post(req_url, data)
                            if 'Unknown' in alias:
                                info = self.name_to_eid(alias)
                                req_url = "cli-json/rm_vlan"
                                data = {
                                    "shelf": info[0],
                                    "resource": info[1],
                                    "port": info[2]
                                }
                                # logger.info(data)
                                logger.info("Removing {alias}...".format(alias=alias))
                                super().json_post(req_url, data)
                time.sleep(1)
            else:
                logger.info("No stations found to cleanup")
                still_looking_sta = False
                logger.info("clean_sta still_looking_sta {sta_looking}".format(sta_looking=still_looking_sta))
            if not still_looking_sta:
                self.sta_done = True
            return still_looking_sta

    # cleans all gui or script created objects from Port Mgr tab
    def port_mgr_clean(self):
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
                logger.info("port_mgr_json set to None")

            # get and remove LF Port Mgr objects
            if port_mgr_json is not None:
                logger.info("Removing old stations ")
                '''
                NOTE: [LF system - APU2/CT521a]: if wiphy radios are deleted
                      run the following command and reboot to fix:
                      /root/lf_kinstall.pl --lfver 5.4.5 --do_sys_reconfig
                '''
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
                                logger.info("Removing {alias}...".format(alias=alias))
                                super().json_post(req_url, data)
                time.sleep(1)
            else:
                logger.info("No stations found to cleanup")
                still_looking_san = False
                logger.info("port_mgr_clean still_looking_san {still_looking_san}".format(still_looking_san=still_looking_san))
            if not still_looking_san:
                self.port_mgr_done = True
            return still_looking_san

    def bridge_clean(self):
        still_looking_br = True
        iterations_br = 0

        while still_looking_br and iterations_br <= 10:
            iterations_br += 1
            logger.info("bridge_clean: iterations_br: {iterations_br}".format(iterations_br=iterations_br))
            try:
                # br_json = super().json_get("port/1/1/list?field=alias")['interfaces']
                br_json = super().json_get("/port/?fields=port+type,alias")['interfaces']
            except TypeError:
                br_json = None

            # get and remove current stations
            if br_json is not None:
                # logger.info(br_json)
                logger.info("Removing old bridges ")
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
                                logger.info("Removing {alias}...".format(alias=alias))
                                super().json_post(req_url, data)
                time.sleep(1)
            else:
                logger.info("No bridges found to cleanup")
                still_looking_br = False
                logger.info("clean_bridge still_looking_br {br_looking}".format(br_looking=still_looking_br))
            if not still_looking_br:
                self.br_done = True
            return still_looking_br

    # Some test have various station names or a station named 1.1.eth2
    def misc_clean(self):
        still_looking_misc = True
        iterations_misc = 0

        while still_looking_misc and iterations_misc <= 10:
            iterations_misc += 1
            logger.info("misc_clean: iterations_misc: {iterations_misc}".format(iterations_misc=iterations_misc))
            try:
                # misc_json = super().json_get("port/1/1/list?field=alias")['interfaces']
                misc_json = super().json_get("/port/?fields=alias")['interfaces']
            except TypeError:
                misc_json = None

            # get and remove current stations
            if misc_json is not None:
                # logger.info(misc_json)
                logger.info("Removing misc station names phy, 1.1.eth (malformed station name) ")
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
                                logger.info("Removing {alias}...".format(alias=alias))
                                super().json_post(req_url, data)
                        if '1.1.1.1.eth' in alias:
                            logger.info('alias 1.1.1.1.eth {alias}'.format(alias=alias))
                            # need to hand construct for delete.
                            info = alias.split('.')
                            logger.info('info {info}'.format(info=info))
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
                                logger.info("Removing {alias}...".format(alias=alias))
                                super().json_post(req_url, data)
                time.sleep(1)
            else:
                logger.info("No misc found to cleanup")
                still_looking_misc = False
                logger.info("clean_misc still_looking_misc {misc_looking}".format(misc_looking=still_looking_misc))
            if not still_looking_misc:
                self.misc_done = True
            return still_looking_misc

    '''
        1: delete cx (Layer-3 tab objects)
        2: delete endp (L3 Endps tab objects)
        3: delete cx & endp (Layer 4-7 tab objects)
        4: delete Port Mgr tab objects
        when deleting sta first, you will end up with phantom CX
    '''
    def sanitize_all(self):
        # 1. clean Layer-3 tab:
        finished_clean_cxs = self.cxs_clean()
        logger.info("clean_cxs: finished_clean_cxs {looking_cxs}".format(looking_cxs=finished_clean_cxs))
        # 2. clean L3 Endps tab:
        finished_clean_endp = self.layer3_endp_clean()
        logger.info("layer3_clean_endp: finished_clean_endp {looking_endp}".format(looking_endp=finished_clean_endp))
        # 3. clean Layer 4-7 tab:
        finished_clean_l4 = self.layer4_endp_clean()
        logger.info("clean_l4_endp: finished_clean_l4 {looking_l4}".format(looking_l4=finished_clean_l4))
        # 4. clean Port Mgr tab:
        finished_clean_port_mgr = self.port_mgr_clean()
        logger.info("clean_sta: finished_clean_port_mgr {looking_port_mgr}".format(looking_port_mgr=finished_clean_port_mgr))


def main():
    help_summary = '''\
    This script is used for cleaning the cross-connections, layer-3-endpoints, stations and bridges in Lanforge.
    This script is also used to sanitize the lanforge unit, which means will clean the Port Mgr, Layer-3, L3 Endps,
    and Layer 4-7 tabs.
            '''
    parser = argparse.ArgumentParser(
        prog='lf_cleanup.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Clean up cxs and endpoints
            ''',
        description='''\
NAME: lf_cleanup.py

PURPOSE:
    clean up stations, cross connects and endpoints

EXAMPLE:
    clear all stations:
        ./lf_cleanup.py --mgr localhost --resource 1 --sta

    This example will clean the Port Mgr, Layer-3, L3 Endps, and Layer 4-7 LF GUI tabs:
        ./lf_cleanup.py --mgr localhost --resource 1 --sanitize

    clear all cxs and enps:
        ./lf_cleanup.py --mgr localhost --resource 1 --cxs

    clear all endps:
        ./lf_cleanup.py --mgr localhost --resource 1 --endp

    clear all bridges:
        ./lf_cleanup.py --mgr localhost --resource 1 --br

    clear sta with names phy (not wiphy) and 1.1.eth stations:
        ./lf_cleanup.py --mgr localhost --resource 1 --misc

JSON EXAMPLE:
    clear all stations:
        "args": ["--mgr","192.168.30.12","--resource","1","--sta"]

    This example will clean the Port Mgr, Layer-3, L3 Endps, and Layer 4-7 LF GUI tabs:
        "args": ["--mgr","192.168.30.12","--resource","1","--sanitize"]

    clear all cxs and enps:
        "args": ["--mgr","192.168.30.12","--resource","1","--cxs"]

    clear all endps:
        "args": ["--mgr","192.168.30.12","--resource","1","--endp"]

    clear all bridges:
        "args": ["--mgr","192.168.30.12","--resource","1","--br"]

    clear sta with names phy (not wiphy) and 1.1.eth stations:
        "args": ["--mgr","192.168.30.12","--resource","1","--misc"]

SCRIPT_CLASSIFICATION:  Deletion

SCRIPT_CATEGORIES:  Functional

NOTES:

    The default port is 8080
    The script will only cleanup what is present in the GUI,
     so it will need to iterate multiple times with script

VERIFIED_ON:
    Tested on 03/17/2023:
        kernel version: 5.19.17+
        gui version: 5.4.6

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright 2023 Candela Technologies Inc

            ''')
    parser.add_argument(
        '--mgr',
        '--lfmgr',
        help='--mgr <hostname for where LANforge GUI is running>',
        default='localhost')
    parser.add_argument(
        '--resource',
        '--res',
        help='--resource <realm resource> to clear a specific resource, or --resource <all> to cleanup all resources',
        default='all')
    parser.add_argument(
        '--cxs',
        help="--cxs, this will clear all the Layer-3 cxs and endps",
        action='store_true')
    parser.add_argument(
        '--l3_endp',
        help="--endp, this will clear all the Layer-3 endps",
        action='store_true')
    parser.add_argument(
        '--sta',
        help="--sta, this will clear all the stations generated by a script",
        action='store_true')
    parser.add_argument(
        '--port_mgr',
        help="--port_mgr, this will clear all the created ports on the Port Mgr tab (wifi-sta, mac-vlans, vap, br)",
        action='store_true')
    parser.add_argument(
        '--br',
        help="--br, this will clear all the bridges",
        action='store_true')
    parser.add_argument(
        '--misc',
        help="--misc, this will clear sta with names phy (not wiphy) and 1.1.eth stations",
        action='store_true')
    parser.add_argument(
        '--layer4',
        help="--layer4, this will clear all the created endpoints on the Layer 4-7 LF GUI tab",
        action='store_true')
    parser.add_argument(
        '--sanitize',
        help="--sanitize, this will clear all the created objects on the Layer-3, L3 Endps, Layer 4-7, and Port Mgr LF GUI tabs",
        action='store_true')
    parser.add_argument('--sleep', help="sleep at completion of cleanup in seconds --sleep 2")
    parser.add_argument(
        "--debug",
        help="enable debugging",
        action="store_true")
    parser.add_argument(
        "--lf_logger_config_json",
        help="--lf_logger_config_json <json file> , json configuration of logger")

    parser.add_argument('--log_level', default=None,
                        help='Set logging level: debug | info | warning | error | critical')

    parser.add_argument('--help_summary', help='Show summary of what this script does', default=None,
                        action="store_true")

    args = parser.parse_args()

    # Print help summary
    if args.help_summary:
        print(help_summary)
        exit(0)

    # Configure logging
    logger_config = lf_logger_config.lf_logger_config()
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)
    if args.debug:
        logger_config.set_level("debug")

    if args.cxs or args.l3_endp or args.sta or args.br or args.misc or args.port_mgr or args.layer4 or args.sanitize:
        clean = lf_clean(host=args.mgr,
                         resource=args.resource,
                         clean_cxs=args.cxs,
                         clean_endp=args.l3_endp,
                         clean_sta=args.sta,
                         clean_port_mgr=args.port_mgr,
                         clean_misc=args.misc)
        logger.info("cleaning cxs: {cxs} endpoints: {endp} stations: {sta} start".format(cxs=args.cxs, endp=args.l3_endp, sta=args.sta))

        response = clean.get_json1()
        logger.debug(response)
        logger.debug("The objects that are present in the port Manager")
        for i in range(len(response["interfaces"])):
            response2 = list(response["interfaces"][i].keys())
            logger.debug(response2)

        if args.cxs:
            logger.info("cleaning cxs will also clean endp")
            clean.cxs_clean()
        if args.l3_endp:
            clean.layer3_endp_clean()
        if args.sta:
            clean.sta_clean()
        if args.port_mgr:
            clean.port_mgr_clean()
        if args.br:
            clean.bridge_clean()
        if args.misc:
            clean.misc_clean()
        if args.layer4:
            clean.layer4_endp_clean()
        if args.sanitize:
            clean.sanitize_all()

        if args.sleep is not None:
            sleep = int(args.sleep)
            logger.info("sleep option selected sleep {sleep} seconds".format(sleep=sleep))
            time.sleep(sleep)

        logger.info("Clean done")
    else:
        logger.info("please add option of --cxs ,--endp, --sta , --br, --misc to clean")


if __name__ == "__main__":
    main()
