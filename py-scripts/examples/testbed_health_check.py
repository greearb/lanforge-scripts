#!/usr/bin/env python3
"""
NAME:       health_check_info.py

PURPOSE:    This script demonstrates automating the LANforge JSON API
            to query basic system information.

            This includes the following (per resource in a testbed):
            - System reachability (through JSON API)
            - Hostname
            - LANforge version
            - OS version
            - System kernel version
            - Number of stations (active and total)
            - Number of L3 endpoints (active and total)

EXAMPLE:    # Perform health check for LANforge testbed w/ manager '192.168.30.12'
            ./health_check_info.py --mgr 192.168.30.12

            # Perform health check for LANforge testbed w/ manager '192.168.30.12'
            # Output JSON API endpoint queries and returned JSON data
            ./health_check_info.py \
                --mgr 192.168.30.12 \
                --verbose

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2024 Candela Technologies Inc.
"""  # noqa: D212,D415
import argparse
from http import HTTPStatus
import logging
import pandas
import requests
import sys
import traceback

if sys.version_info[0] != 3:
    print("The script requires Python 3")
    exit()


class ResourceInfo:
    """LANforge resource data."""
    def __init__(self,
                 resource_id: str,
                 hostname: str = "",
                 ctrl_ip: str = "",
                 sw_version: str = "",
                 build_date: str = ""):
        self.resource_id = resource_id
        self.hostname = hostname
        self.ctrl_ip = ctrl_ip
        self.sw_version = sw_version
        self.build_date = build_date

        # Everything we build is 64bit at this point.
        # Simplify printout by removing from LANforge version
        self.sw_version = self.sw_version.replace("64bit", "").strip()

        self.stations = []
        self.active_stations = []
        self.endps = []
        self.active_endps = []


class PortInfo:
    """LANforge port data."""
    def __init__(self,
                 port_id: str,
                 port_type: str = "",
                 alias: str = "",
                 phantom: bool = True,
                 down: bool = True):
        self.port_id = port_id
        self.port_type = port_type
        self.alias = alias
        self.phantom = phantom
        self.down = down

        # Derive resource ID for this port from port ID
        rsrc_id = ".".join(port_id.split(".")[:2])
        self.resource_id = rsrc_id


class EndpInfo:
    """LANforge L3 endpoint data."""
    def __init__(self,
                 endp_name: str,
                 eid: str = "",
                 endp_type: str = "",
                 run: bool = False):
        self.endp_name = endp_name
        self.eid = eid
        self.endp_type = endp_type
        self.run = run

        # Derive resource ID for this port from port ID
        rsrc_id = ".".join(eid.split(".")[:2])
        self.resource_id = rsrc_id


def health_check_info(mgr: str = "localhost", mgr_port: int = 8080, **kwargs):
    """Perform system help check as detailed in docstring.

    Leverages LANforge JSON API running on port 8080 when GUI is active.

    Args:
        mgr: LANforge manager IP address
        mgr_port: LANforge manager REST API port (almost always '8080')
    """
    # 0. Initialize data to print later
    json_api_up = False

    # LANforge JSON API base URL (other URLs constructed from this)
    base_url = f"http://{mgr}:{mgr_port}"

    # 1. Query base endpoint ('/', e.g. '192.168.1.101:8080/')
    #
    # Successful GET request indicates JSON API is up and running as expected
    ret, (status_code, _) = query_lanforge(base_url=base_url, endpoint="/")
    if ret != 0:
        return ret
    elif status_code == HTTPStatus.OK:
        json_api_up = True

    if not json_api_up:
        logger.error("Cannot connect to JSON API")
        return -1

    # 2. Query '/resource' endpoint data
    #
    # Query resource JSON API endpoint to get relevant resource data
    # Will filter additional queried data to these resource data
    # structures, coalescing everything based on resource
    ret, rsrc_data_list = query_resource_data(base_url)
    if ret != 0:
        return ret

    # 3. Query '/port' endpoint data
    #
    # Query port JSON API endpoint to get relevant port data
    # Need to post-process to determine desired station counts
    ret, port_data_list = query_port_data(base_url)
    if ret != 0:
        return ret

    # 4. Query '/endp' endpoint data (L3 connection endpoint)
    #
    # Query the layer-3 endpoint endpoint to get relevant layer-3 endpoint data
    ret, endp_data_list = query_endp_data(base_url)
    if ret != 0:
        return ret

    # 5. Filter port and endpoint data to respective resources
    #
    # Filter out stations and active stations into corresponding resources
    # Active stations here are defined as stations which are not down and not phantom
    filter_stations_to_resource(rsrc_data_list, port_data_list)
    filter_endps_to_resource(rsrc_data_list, endp_data_list)

    # 6. Merge data into single dict and print system health check info
    #
    # Assume processing up to this point ensures all fields present
    # in all resource info ojbects. Otherwise, would have to worry about
    # missing data effect on results display.
    all_data = {}
    for rsrc_data in rsrc_data_list:
        for field, data in vars(rsrc_data).items():
            if field not in all_data:
                all_data[field] = []

            # We don't care about all station data for display purposes, just count
            if field in ['stations', 'active_stations', 'endps', 'active_endps']:
                data = len(data)

            all_data[field].append(data)

    # Make into a Pandas DataFrame for easy printing
    health_data_df = pandas.DataFrame(all_data)

    # Print data to console
    print(f"LANforge testbed status (manager \'{mgr}\'):")
    print(health_data_df)

    return 0


def query_lanforge(base_url: str, endpoint: str, fields: list = None) -> tuple:
    """Query LANforge system for desired data from JSON API endpoint.

    Args:
        base_url: URL of LANforge JSON API (e.g. 'http://192.168.1.101:8080')
        endpoint: JSON API endpoint to query
        fields: Optional fields to query the specified JSON API endpoint with

    Returns:
        Two element tuple containing return code and return data.
        Return code is 0 on success, non-zero on error. Return data
        is a two element tuple containing the HTTP GET response code
        and the response JSON data.
    """
    # Begin constructing URL to query LANforge
    url = base_url + endpoint

    # Prepare and append to URL any specific fields desired
    #
    # Fields must be properly URL encoded (e.g. ' ' must be '+')
    # and separated by comma
    if fields:
        encoded_fields = ",".join([field.replace(" ", "+") for field in fields])
        url += "?fields=" + encoded_fields

    response = None
    try:
        logger.debug(f"Querying LANforge JSON endpoint with URL: \'{url}\'")
        response = requests.get(url=url)
    except requests.exceptions.ConnectionError:
        # Given we need to check if system is up, handle this
        # differently than other exceptions
        logger.error(f"Failed to connect to LANforge JSON HTTP using URL \'{url}\'")
        return 0, (None, None)
    except Exception:
        logging.error(traceback.format_exc())
        logger.error("Unhandled exception in HTTP GET request")
        return -1, (None, None)

    if response is None:
        logger.error(f"No response when querying LANforge JSON HTTP using URL "
                     f"\'{url}\'. All example URLs should return data. "
                     "This is a bug.")
        return -1, (None, None)
    elif response.status_code != HTTPStatus.OK and endpoint != "/endp":
        # TODO: Fix hack to workaround API issue (see 'query_endp_data()')
        logger.error(f"Failed to query LANforge JSON HTTP API URL \'{url}\' "
                     f"with status code {response.status_code}")
        return 0, (response.status_code, None)

    response_data = response.json()
    logger.debug(f"Returned JSON data: {response_data}")

    return 0, (response.status_code, response_data)


def query_resource_data(base_url: str) -> tuple:
    """Query LANforge for desired resource data.

    Args:
        base_url: Base LANforge JSON API URL to query using JSON HTTP GET

    Returns:
        Two element tuple containing return code and return data.
        Return code is 0 on success, non-zero on error. Return data
        is a list of 'ResourceInfo' objects queried from specified system.
    """
    # TODO: OS-version once implemented.
    #       Need to consider backwards compatibility. Can't directly query
    #       for something not supported. Need to query all and filter.
    RESOURCE_ENDP_FIELDS = [
        "eid",
        "hostname",
        "ctrl-ip",
        "sw version",
        "build date",
    ]

    ret, (status_code, queried_rsrc_data) = query_lanforge(base_url=base_url,
                                                           endpoint="/resource",
                                                           fields=RESOURCE_ENDP_FIELDS)
    if ret != 0:
        return ret, None
    elif status_code != HTTPStatus.OK:
        return -1, None

    # Unpack desired data from data returned querying the endpoint above
    if "resource" not in queried_rsrc_data and "resources" not in queried_rsrc_data:
        logger.error("Neither required field \'resource\' or \'resources\' "
                     "present in returned data")
        return -1, None

    all_rsrc_data = queried_rsrc_data.get("resource")
    if all_rsrc_data is None:
        all_rsrc_data = queried_rsrc_data.get("resources")

        if all_rsrc_data is None:
            logger.error("Previous check should've ensured either required field present")
            return -1, None

    # If one result is returned, it's returned as a dict. When more than
    # one result is returned, it's returned as a list of dicts.
    # Make single result into same format to simplify processing
    if isinstance(all_rsrc_data, dict):
        rsrc_id = all_rsrc_data.get("eid")
        if not rsrc_id:
            logger.error("Resource ID (field: \'eid\') not present")
            return -1, None
        else:
            all_rsrc_data = [{rsrc_id: all_rsrc_data}]

    # Initialize 'ResourceInfo' objects per resource detected
    #
    # Should a required field not be present, still initialize
    # but only with the ID, which is always present. This ensures
    # still visible even with missing data.
    rsrc_info_objs = []
    for rsrc_data in all_rsrc_data:
        rsrc_id = list(rsrc_data.keys())[0]
        rsrc_data = rsrc_data[rsrc_id]

        any_not_present = False
        for field in RESOURCE_ENDP_FIELDS:
            if field not in rsrc_data:
                logger.error(f"Expected field \'{field}\' not present in "
                             f"resource data for resource \'{rsrc_id}\'")
                any_not_present = True
                break

        if any_not_present:
            rsrc_obj = ResourceInfo(resource_id=rsrc_id)
        else:
            rsrc_obj = ResourceInfo(resource_id=rsrc_id,
                                    hostname=rsrc_data['hostname'],
                                    ctrl_ip=rsrc_data['ctrl-ip'],
                                    sw_version=rsrc_data['sw version'],
                                    build_date=rsrc_data['build date'])

        rsrc_info_objs.append(rsrc_obj)

    return 0, rsrc_info_objs


def query_port_data(base_url: str) -> tuple:
    """Query LANforge for desired port data.

    Args:
        base_url: Base LANforge JSON API URL to query using JSON HTTP GET

    Returns:
        Two element tuple containing return code and return data.
        Return code is 0 on success, non-zero on error. Return data
        is a list of 'PortInfo' objects queried from specified system.
    """
    PORT_ENDP_FIELDS = [
        "port",
        "port type",
        "alias",
        "down",
        "phantom",
    ]

    ret, (status_code, queried_port_data) = query_lanforge(base_url=base_url,
                                                           endpoint="/port",
                                                           fields=PORT_ENDP_FIELDS)
    if ret != 0:
        return ret, None
    elif status_code != HTTPStatus.OK:
        return -1, None

    # Unpack desired data from data returned from querying the endpoint above
    if "interfaces" not in queried_port_data:
        logger.error("Required data key-value pair \'interfaces\' not "
                     "present in returned data")
        return -1, None

    all_port_data = queried_port_data.get("interfaces")
    if all_port_data is None:
        all_port_data = queried_port_data.get("interfaces")

        if all_port_data is None:
            logger.error("Previous check should've ensured required key present")
            return -1, None

    # If one result is returned, it's returned as a dict. When more than
    # one result is returned, it's returned as a list of dicts.
    # Make single result into same format to simplify processing
    if isinstance(all_port_data, dict):
        port_id = all_port_data.get("port")
        if not port_id:
            logger.error("Port ID (field: \'port\') not present")
            return -1, None
        else:
            all_port_data = [{port_id: all_port_data}]

    # Initialize 'PortInfo' objects per port detected
    #
    # Should a required field not be present, still initialize
    # but only with the ID, which is always present. This ensures
    # still visible even with missing data.
    port_info_objs = []
    for port_data in all_port_data:
        port_id = list(port_data.keys())[0]
        port_data = port_data[port_id]

        any_not_present = False
        for field in PORT_ENDP_FIELDS:
            if field not in port_data:
                logger.error(f"Expected field \'{field}\' not present in "
                             f"port data for port \'{port_id}\'")
                any_not_present = True
                break

        if any_not_present:
            port_obj = PortInfo(port_id=port_id)
        else:
            port_obj = PortInfo(port_id=port_id,
                                alias=port_data['alias'],
                                port_type=port_data['port type'],
                                down=port_data['down'],
                                phantom=port_data['phantom'])

        port_info_objs.append(port_obj)

    return 0, port_info_objs


def query_endp_data(base_url: str) -> tuple:
    """Query LANforge for desired Layer 3 endpoint data.

    Args:
        base_url: Base LANforge JSON API URL to query using JSON HTTP GET

    Returns:
        Two element tuple containing return code and return data.
        Return code is 0 on success, non-zero on error. Return data
        is a list of 'EndpInfo' objects queried from specified system.
    """
    ENDP_ENDP_FIELDS = [
        "name",
        "eid",
        "type",
        "run",
    ]

    # URL enconded fields must be properly encoded (e.g. ' ' must be '+')
    ret, (status_code, queried_endp_data) = query_lanforge(base_url=base_url,
                                                           endpoint="/endp",
                                                           fields=ENDP_ENDP_FIELDS)
    if ret != 0:
        return ret, None
    elif status_code == HTTPStatus.NOT_FOUND:
        # TODO: When no layer-3 connections present, API currently 404s
        #       even when layer-3 tab is active. This is an API issue
        return 0, []
    elif status_code != HTTPStatus.OK:
        return -1, None

    # Unpack desired data from data returned from querying the endpoint above
    if "endpoint" not in queried_endp_data:
        logger.error("Required data key-value pair \'endpoint\' not "
                     "present in returned data")
        return -1, None

    all_endp_data = queried_endp_data.get("endpoint")
    if all_endp_data is None:
        logger.error("Previous check should've ensured required key present")
        return -1, None

    # If one result is returned, it's returned as a dict. When more than
    # one result is returned, it's returned as a list of dicts.
    # Make single result into same format to simplify processing
    if isinstance(all_endp_data, dict):
        # TODO: Test this w/ multicast endpoints.
        endp_name = all_endp_data.get("name")
        if not endp_name:
            logger.error("Endpoint name (field: \'name\') not present")
            return -1, None
        else:
            all_endp_data = [{endp_name: all_endp_data}]

    # Initialize 'EndpInfo' objects per port detected
    #
    # Should a required field not be present, still initialize
    # but only with the name, which is always present. This ensures
    # still visible even with missing data.
    endp_info_objs = []
    for endp_data in all_endp_data:
        endp_name = list(endp_data.keys())[0]
        endp_data = endp_data[endp_name]

        any_not_present = False
        for field in ENDP_ENDP_FIELDS:
            if field not in endp_data:
                logger.error(f"Expected field \'{field}\' not present in "
                             f"endpoint data for endpoint \'{endp_name}\'")
                any_not_present = True
                break

        if any_not_present:
            endp_obj = EndpInfo(endp_name=endp_name)
        else:
            endp_obj = EndpInfo(endp_name=endp_name,
                                eid=endp_data['eid'],
                                endp_type=endp_data['type'],
                                run=endp_data['run'])

        endp_info_objs.append(endp_obj)

    return 0, endp_info_objs


def filter_stations_to_resource(resource_data_list: list, port_data_list: list) -> None:
    """Filter provided station port data to provided resources.

    Given a list of 'ResourceInfo' objects, filter out any provided 'PortInfo'
    station objects into the respective 'ResourceInfo' objects.

    Args:
        resource_data_list: List of queried 'ResourceInfo' objects
        port_data_list: List of queried 'PortInfo' objects
    """
    sta_ports_list = [port for port in port_data_list if port.port_type == "WIFI-STA"]

    for rsrc in resource_data_list:
        this_rsrc_stations = [sta for sta in sta_ports_list if sta.resource_id == rsrc.resource_id]
        this_rsrc_active_stations = [
            sta for sta in this_rsrc_stations
            if sta.phantom is False and sta.down is False
        ]

        rsrc.stations = this_rsrc_stations
        rsrc.active_stations = this_rsrc_active_stations


def filter_endps_to_resource(resource_data_list: list, endp_data_list: list) -> None:
    """Filter provided endpoint data to provided resources.

    Given a list of 'ResourceInfo' objects, filter out any provided 'EndpInfo'
    objects into the respective 'ResourceInfo' objects.

    Args:
        resource_data_list: List of queried 'ResourceInfo' objects
        endp_data_list: List of queried 'EndpInfo' objects
    """
    for rsrc in resource_data_list:
        this_rsrc_endps = [endp for endp in endp_data_list if endp.resource_id == rsrc.resource_id]
        this_rsrc_active_endps = [endp for endp in this_rsrc_endps if endp.run]

        rsrc.endps = this_rsrc_endps
        rsrc.active_endps = this_rsrc_active_endps


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="health_check_info.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
NAME:       health_check_info.py

PURPOSE:    This script demonstrates automating the LANforge JSON API
            to query basic system information. This includes the following:

            - Hostname
            - LANforge version
            - OS version
            - System kernel
            - System reachability (through JSON API)

EXAMPLE:    # Perform health check for LANforge testbed w/ manager '192.168.30.12'
            ./health_check_info.py --mgr 192.168.30.12

LICENSE:    Free to distribute and modify. LANforge systems must be licensed.
            Copyright 2024 Candela Technologies Inc.
""")

    parser.add_argument("--mgr",
                        help="Manager LANforge GUI IP address",
                        type=str,
                        default='localhost')
    parser.add_argument("--mgr_port",
                        help="Manager LANforge GUI port (almost always 8080)",
                        type=int,
                        default=8080)
    parser.add_argument("--debug",
                        help="Output debugging level log information, including "
                             "JSON API endpoint queries and returned JSON data",
                        action="store_true")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Make logging output a bit more legible
    logger = logging.getLogger("health_check")
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    if args.debug:
        logger.setLevel(logging.DEBUG)

    # The '**vars()' unpacks the 'args' into arguments to function.
    ret = health_check_info(**vars(args))
    exit(ret)
