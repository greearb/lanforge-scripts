#!/usr/bin/env python3
# flake8: noqa
'''
NAME: radio_info.py

PURPOSE:
    This script queries and displays general information for all radios in a LANforge testbed.
    Information queried includes WiFi generation, number of stations and vAPs supported,
    driver, and firmware version for all resources in the testbed.

EXAMPLE:
    ./radio_info.py --mgr 192.168.30.22
'''

import argparse
import logging
import requests
import pandas
from http import HTTPStatus

# Make logging output a bit more legible
logger = logging.getLogger("radio_info")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def query_radio_information(mgr: str = "localhost", mgr_port: int = 8080) -> pandas.DataFrame:
    """
    Queries specified LANforge manager for general information on all radios in testbed.

    :param mgr: LANforge manager IP address
    :param mgr_port: LANforge manager REST API port (almost always '8080')
    :returns: Radio information
    :rtype: pandas.DataFrame
    """
    # First query LANforge system for radio info (returned as JSON)
    base_url = f"http://{mgr}:{mgr_port}"   # Manager system to query (GUI must be running)
    endpoint = "/radiostatus/all"           # REST endpoint to query for radio information
    url = base_url + endpoint

    logger.info(f"Querying LANforge radio information using URL \'{url}\'")
    response = requests.get(url=url)
    if response.status_code != HTTPStatus.OK:
        logger.error(f"Failed to query radio information at URL \'{url}\' with status code {response.status_code}")
        exit(1)

    # Unpack JSON data from response
    json_data = response.json()

    # Temporary data structure to store all radio info until ready to build dataframe
    tmp_radio_data = {
        'Radio': [],
        'Driver': [],
        'Radio Capa.': [],
        'Firmware Ver.': [],
        'Max STA': [],
        'Max vAPs': [],
        'Max Virt. Interfaces': [],
    }

    # Now convert JSON into a pandas DataFrame to pretty print to the terminal
    for key in json_data:
        # Ignore other standard keys in JSON return are 'handler', 'uri', and 'warnings'
        # Radio info stored with EID keys like '1.1.wiphy0'
        if 'wiphy' not in key:
            continue

        logger.debug(f"Found data for radio \'{key}\'")
        radio_data = json_data[key]

        # Filter out unnecessary information like PCI(e) bus
        driver = radio_data['driver'].split('Driver:', maxsplit=1)[-1].split(maxsplit=1)[0]

        tmp_radio_data['Radio'].append(radio_data['entity id'])
        tmp_radio_data['Driver'].append(driver)
        tmp_radio_data['Radio Capa.'].append(radio_data['capabilities'])
        tmp_radio_data['Firmware Ver.'].append(radio_data['firmware version'])
        tmp_radio_data['Max STA'].append(radio_data['max_sta'])
        tmp_radio_data['Max vAPs'].append(radio_data['max_vap'])
        tmp_radio_data['Max Virt. Interfaces'].append(radio_data['max_vifs'])

    return pandas.DataFrame(tmp_radio_data)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="radio_info.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
Summary:
    This script queries and displays general information for all radios in a LANforge testbed.
    Information queried includes WiFi generation, number of stations and vAPs supported,
    driver, and firmware version for all resources in the testbed.

Example:
    ./lf_radio_info.py --mgr 192.168.30.12
""")

    parser.add_argument("--mgr",
                        help="Manager LANforge GUI IP address",
                        type=str,
                        default='localhost')
    parser.add_argument("--mgr_port",
                        help="Manager LANforge GUI port (almost always 8080)",
                        type=int,
                        default=8080)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # The '**vars()' unpacks the 'args' into arguments to function.
    radio_df = query_radio_information(**vars(args))
    print(radio_df)
