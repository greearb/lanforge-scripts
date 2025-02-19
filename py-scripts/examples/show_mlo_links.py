#!/usr/bin/env python3
'''
NAME:  show_mlo_links.py

PURPOSE:
    This script serves as an example for automating LANforge using the REST API
    and as a minimal example to show general mlo links information.

EXAMPLE:
    # Query testbed mananged by '192.168.xxx.xxx' LANforge for all mlo links.
    # Default fields are 'eid', 'parent dev', 'active', 'rx rate', 'tx rate', 'channel', 'chain rssi', 'avg chain rssi', 'time-stamp'
    ./show_mlo_links.py --mgr 192.168.xxx.xxx

    # Query testbed managed by '192.168.xxx.xxx' LANforge for all mlo links
    # with additional fields 'noise', 'activity'
    ./show_mlo_links.py --mgr 192.168.xxx.xxx --addtl_fields "noise,activity"

NOTES:
    Any column visible in the 'MLO' tab of the LANforge GUI can be added as an additional field

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2024 Candela Technologies Inc.
'''

import argparse
import logging
import requests
import pandas
import sys
from http import HTTPStatus

if sys.version_info[0] != 3:
    print("The script requires python3")

logger = logging.getLogger("mlo_links")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

DEFAULT_FIELDS = ["eid", "parent dev", "active", "rx rate", "tx rate", "channel", "chain rssi", "avg chain rssi", "time-stamp"]
DEFAULT_FIELDS_CSV = ",".join(DEFAULT_FIELDS)


def show_links(mgr: str = "localhost", mgr_port: int = 8080, resource: str = "all", addtl_fields: str = "") -> pandas.DataFrame:

    base_url = f"http://{mgr}:{mgr_port}"

    if addtl_fields == "":
        all_fields = DEFAULT_FIELDS
        endpoint = f"/mlo/1/{resource}/list?fields={DEFAULT_FIELDS_CSV}"
    else:
        all_fields = DEFAULT_FIELDS + addtl_fields.split(",")
        endpoint = f"/mlo/1/{resource}/list?fields={DEFAULT_FIELDS_CSV},{addtl_fields}"

    url = base_url + endpoint

    logger.info(f"Querying LANforge mlo links information using URL \'{url}\'")
    response = requests.get(url=url)

    if response.status_code != HTTPStatus.OK:
        logger.error(f"Failed to query mlo links information at URL \'{url}\' with status code {response.status_code}")
        exit(1)

    json_data = response.json()
    mlo_data = json_data.get("mlo_links")

    if not mlo_data:
        logger.error("Key \'mlo_links\' not in JSON data")
        exit(1)

    links_data_dict = {key: [] for key in all_fields}
    for mlo_data_dict in mlo_data:

        keys = list(mlo_data_dict.keys())
        if len(keys) != 1:
            logger.error(f"Malformatted mlo data: {mlo_data_dict}")
            exit(1)

        mlo_data = mlo_data_dict[keys[0]]
        for key in mlo_data:
            links_data_dict[key].append(mlo_data[key])

    return pandas.DataFrame(links_data_dict)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="show_mlo_links.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description='''
        Summary:
            This script serves as an example for automating LANforge using the REST API
            and as a minimal example to show general mlo links information.

        Example:
            # Query testbed mananged by '192.168.xxx.xxx' LANforge for all mlo links.
            # Default fields are 'eid', 'parent dev', 'active', 'rx rate', 'tx rate', 'channel', 'chain rssi', 'avg chain rssi', 'time-stamp'
            ./show_mlo_links.py --mgr 192.168.xxx.xxx

            # Query testbed managed by '192.168.xxx.xxx' LANforge for all mlo links
            # with additional fields 'noise', 'activity'
            ./show_mlo_links.py --mgr 192.168.xxx.xxx --addtl_fields "noise,activity"

        Notes:
            Any column visible in the 'MLO' tab of the LANforge GUI can be added as an additional field with '--addtl_fields argument'
        '''
    )

    parser.add_argument("--mgr",
                        help="Manager LANforge GUI IP address",
                        type=str,
                        default='localhost')
    parser.add_argument("--mgr_port",
                        help="Manager LANforge GUI port (almost always 8080)",
                        type=int,
                        default=8080)
    parser.add_argument("--resource",
                        help="LANforge resource to query ports information. Default is all resources.",
                        type=str,
                        default="all")
    parser.add_argument("--addtl_fields",
                        help="Comma separated list of additional fields to print. Permitted "
                             "fields are those visible in the \'MLO Links\' GUI tab. ",
                        default="",
                        type=str)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # The '**vars()' unpacks the 'args' into arguments to function.
    mlo_data = show_links(**vars(args))
    print(mlo_data)
