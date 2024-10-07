#!/usr/bin/env python3
"""
NAME:       show_ports.py

PURPOSE:    This script serves both as an example for automating LANforge using the REST API
            and as a minimal example to show general port information.

            While the script will always show basic information like the port name, port EID,
            phantom status, down status. Other fields visible in the 'Port Mgr' GUI tab are
            supported when passed via the `--addtl_fields` argument.

EXAMPLE:    # Query testbed managed by '192.168.30.12' LANforge for all ports
            # for data in 'hardware', 'mode', 'channel', and 'signal' columns of
            # the 'Port Mgr' tab
            ./show_ports.py --mgr 192.168.30.12 --addtl_fields "hardware,mode,channel,signal"

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2024 Candela Technologies Inc.
"""
import argparse
from http import HTTPStatus
import logging
import pandas
import requests
import sys

if sys.version_info[0] != 3:
    print("The script required python3")
    exit()

# Make logging output a bit more legible
logger = logging.getLogger("port_probe")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

DEFAULT_FIELDS = ["_links", "port", "alias", "down", "phantom"]
DEFAULT_FIELDS_CSV = ",".join(DEFAULT_FIELDS)


def show_ports(mgr: str = "localhost", mgr_port: int = 8080, resource: str = "all", addtl_fields: str = "") -> pandas.DataFrame:
    """Gather and print specified information on all ports using the LANforge API.

    Generally the LANforge IP address is that of the manager system for the testbed.

    Args:
        mgr: LANforge manager IP address
        mgr_port: LANforge manager REST API port (almost always '8080')
        resource: LANforge resource ID. When specified and not -1, limit port information
            to that resource. By default, port information is shown for all resources.
        addtl_fields: Comma separated list of additional fields to print. Permitted
            fields are those visible in the 'Port Mgr' GUI tab.

    Returns:
        Pandas DataFrame containing the desired ports data
    """
    # Query LANforge system for port info (returned as JSON)
    base_url = f"http://{mgr}:{mgr_port}"   # Manager system to query (GUI must be running)

    # If don't pass "?fields=..." portion, will return lots of data (which may be desired, but not here)
    if addtl_fields == "":
        all_fields = DEFAULT_FIELDS
        endpoint = f"/port/1/{resource}/list?fields={DEFAULT_FIELDS_CSV}"
    else:
        all_fields = DEFAULT_FIELDS + addtl_fields.split(",")
        endpoint = f"/port/1/{resource}/list?fields={DEFAULT_FIELDS_CSV},{addtl_fields}"

    url = base_url + endpoint

    # Query port information using HTTP GET. Data returned is JSON
    logger.info(f"Querying LANforge port information using URL \'{url}\'")
    response = requests.get(url=url)
    if response.status_code != HTTPStatus.OK:
        logger.error(f"Failed to query LANforge port information using URL \'{url}\' with status code {response.status_code}")
        exit(1)

    json_data = response.json()

    ports_data = json_data.get("interfaces")
    if not ports_data:
        logger.error("Key \'interfaces\' not in JSON data")
        exit(1)

    # Unpack ports data into temporary data structure
    # Assume that request would have failed for any non-existent fields
    ports_data_dict = {key: [] for key in all_fields}
    for port_data_dict in ports_data:
        # 'port_data_dict' should be a dict with a single key value pair, the port EID and port data
        keys = list(port_data_dict.keys())
        if len(keys) != 1:
            logger.error(f"Malformatted port data: {port_data_dict}")
            exit(1)

        # Transfer from JSON returned to temporary data structure
        port_data = port_data_dict[keys[0]]
        for key in port_data:
            ports_data_dict[key].append(port_data[key])

    return pandas.DataFrame(ports_data_dict)


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="show_ports.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
Summary:
    This script serves both as an example for automating LANforge using the REST API
    and as a minimal example to show general port information.

    While the script will always show basic information like the port name, phantom status, down status,
    IP and parent device, other fields visible in the 'Port Mgr' GUI tab are supported when passed via
    the `--additional_fields` argument.

Example:
    ./show_ports.py --mgr 192.168.30.12 --additional_fields "alias,channel,mode,signal"
""")

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
                             "fields are those visible in the \'Port Mgr\' GUI tab. ",
                        default="",
                        type=str)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # The '**vars()' unpacks the 'args' into arguments to function.
    ports_data = show_ports(**vars(args))
    print(ports_data)
