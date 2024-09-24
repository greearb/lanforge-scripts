#!/usr/bin/env python3
# flake8: noqa
"""
NAME: port_probe.py

PURPOSE:
    This script serves both as an example for automating LANforge using the REST API
    and as a minimal port probe example.

    It is designed to find and show details about a specific port. If the port is related to WiFi,
    the gathered details will include the port's radio information and regulatory information,
    among other items.

EXAMPLE:
    ./port_probe.py --mgr 192.168.30.12 --port_eid 1.1.wiphy0
"""
import argparse
from http import HTTPStatus
import logging
import requests
import sys
from time import sleep

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

# Make logging output a bit more legible
logger = logging.getLogger("port_probe")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def probe_port(port: str, mgr: str = "localhost", mgr_port: int = 8080):
    """
    Using the LANforge REST API, submit and gather the results of a port probe for the specied port.
    Generally the LANforge IP address is that of the manager system for the testbed.

    :param port: Port EID to probe, e.g. '1.1.wiphy0'
    :param mgr: LANforge manager IP address
    :param mgr_port: LANforge manager REST API port (almost always '8080')
    """
    # First query LANforge system for radio info (returned as JSON)
    base_url = f"http://{mgr}:{mgr_port}"   # Manager system to query (GUI must be running)

    # Verify that port EID is in format SHELF.RESOURCE.PORT, e.g. '1.2.eth0'
    hunks = port.split(".")
    if len(hunks) != 3:
        logger.error("Port EID \'{args.port}\' is incorrect")
        exit(1)

    # REST endpoint used for both submitting and gathering port probe results
    endpoint = f"/probe/1/{hunks[-2]}/{hunks[-1]}"
    url = base_url + endpoint

    # Submit port probe as HTTP POST with no data
    logger.info(f"Submitting port probe for LANforge port using URL \'{url}\'")
    response = requests.post(url=url)
    if response.status_code != HTTPStatus.OK:
        logger.error(f"Failed to submit port probe for LANforge port using URL \'{url}\' with status code {response.status_code}")
        exit(1)

    # Delay slightly to allow port probe to complete
    sleep(0.5)

    # Gather port probe results as HTTP GET. Data returned is JSON
    logger.info(f"Gathering port probe results for LANforge port using URL \'{url}\'")
    response = requests.post(url=url)
    if response.status_code != HTTPStatus.OK:
        logger.error(f"Failed to gather port probe results for LANforge port using URL \'{url}\' with status code {response.status_code}")
        exit(1)

    # Unpack and print out data
    data = response.json()
    if "probe-results" not in data:
        logger.error("Error probing port \'{self.port}\'")
        exit(1)

    # Print out port probe results
    probe_results = data["probe-results"][0]
    for (key, value) in probe_results.items():
        print("port " + key)
        xlated_results = str(value['probe results']).replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
        print(xlated_results)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="port_probe.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
Summary:
    This script serves both as an example for automating LANforge using the 'py-json' library
    and as a minimal port probe example.

    It is designed to find and show details about a specific port. If the port is related to WiFi,
    the gathered details will include the port's radio information and regulatory information,
    among other items.

Example:
    ./port_probe.py --mgr 192.168.30.12 --port 1.1.wiphy0
""")

    parser.add_argument("--mgr",
                        help="Manager LANforge GUI IP address",
                        type=str,
                        default='localhost')
    parser.add_argument("--mgr_port",
                        help="Manager LANforge GUI port (almost always 8080)",
                        type=int,
                        default=8080)
    parser.add_argument("--port", "--port_eid",
                        dest="port",
                        help='EID of station to be used',
                        default="1.1.eth0")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # The '**vars()' unpacks the 'args' into arguments to function.
    probe_port(**vars(args))
