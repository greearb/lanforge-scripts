#!/usr/bin/env python3
import argparse
from http import HTTPStatus
import importlib
import logging
import os
import pandas as pd
import sys
import time


# Get LANforge scripts path from environment variable 'LF_PYSCRIPTS'
if 'LF_SCRIPTS' not in os.environ:
    print("ERROR: Environment variable \'LF_SCRIPTS\' not defined. See README for more information")
    exit(1)
LF_SCRIPTS = os.environ['LF_SCRIPTS']

if LF_SCRIPTS == "":
    print("ERROR: Environment variable \'LF_SCRIPTS\' is empty")
    exit(1)
elif not os.path.exists(LF_SCRIPTS):
    print(
        f"ERROR: LANforge Python scripts directory \'{LF_SCRIPTS}\' does not exist")
    exit(1)
elif not os.path.isdir(LF_SCRIPTS):
    print(
        f"ERROR: Provided LANforge Python scripts directory \'{LF_SCRIPTS}\' is not a directory")
    exit(1)


# Import LANforge API
sys.path.append(os.path.join(os.path.abspath(LF_SCRIPTS)))  # noqa
lanforge_client = importlib.import_module("lanforge_client")  # noqa
from lanforge_client.lanforge_api import LFSession  # noqa


def main(mgr: str,
         mgr_port: int,
         duration: int,
         vap_eids: list[str],
         port_eids: list[str],
         cx_names: list[str],
         port_fields: str,
         cx_fields: str,
         vap_fields: str,
         vap_metrics_csv: str,
         port_metrics_csv: str,
         cx_metrics_csv: str,
         no_clear_port_counters: bool,
         no_clear_cx_counters: bool,
         **kwargs):
    # If specified, parse out user-provided fields to query into
    # format expected by LANforge API
    port_fields: list[str] = parse_port_fields(args.port_fields)
    cx_fields: list[str] = parse_cx_fields(args.cx_fields)
    vap_fields: list[str] = parse_vap_fields(args.vap_fields)

    # Instantiate a LANforge API session with the specified LANforge system.
    #
    # The JSON API port is almost always 8080. The LANforge server port,
    # which isn't relevant here, are in the 4001+ range
    logger.info(f"Initiating LANforge API session with LANforge {mgr}:{mgr_port}")
    session = LFSession(
        lfclient_url=f"http://{mgr}:{mgr_port}",
    )

    # Only query the '/stations' endpoint for provided vAP EIDs,
    # but query port information for both the provided Port EIDs
    # as well as the vAP EIDs.
    vaps_to_query = vap_eids
    ports_to_query = list(set(vap_eids + port_eids))  # Removes duplicates, if specified

    if not no_clear_port_counters and len(port_eids) != 0:
        ret = clear_port_counters(session=session, port_eids=ports_to_query)
        if ret != 0:
            return ret

    if not no_clear_cx_counters and len(cx_names) != 0:
        ret = clear_cx_counters(session=session, cx_names=cx_names)
        if ret != 0:
            return ret

    # Track data in dicts of key value pairs, where the key is the EID or name
    # and the value is a list of queried data
    vap_metrics = []
    port_metrics = []
    cx_metrics = []

    logger.info(f"Beginning to query metrics for port(s) {ports_to_query}, "
                f"stations associated to vAP(s) {vaps_to_query}, and "
                f"CX(s) {cx_names}")
    for _ in range(duration):
        start_time_ms = time.time() * 1_000
        end_time_ms = start_time_ms + 1_000

        # To ensure consistent data presented in the CSV, use the current time
        # as the timestamp (converted to milliseconds).
        #
        # This ensures a user gets a consistent view of associated stations
        # and port metrics across vAP and port data.
        #
        timestamp = start_time_ms * 1_000

        # NOTE: These functions return a value indicating success (0) or error (not 0).
        #       Ignore these for now to let the test continue running.
        #
        if len(vaps_to_query) > 0:
            query_vap_metrics(session=session,
                              timestamp=timestamp,
                              vap_list=vaps_to_query,
                              vap_fields=vap_fields,
                              vap_metrics=vap_metrics)

        if len(ports_to_query) > 0:
            query_port_metrics(session=session,
                               timestamp=timestamp,
                               eid_list=ports_to_query,
                               port_fields=port_fields,
                               port_metrics=port_metrics)

        if len(cx_names) > 0:
            query_cx_metrics(session=session,
                             timestamp=timestamp,
                             cx_names=cx_names,
                             cx_fields=cx_fields,
                             cx_metrics=cx_metrics)

        # Calculated time to start next loop earlier
        # Sleep difference between current time after querying and start of
        # next loop time to ensure data is queries as close to every second as possible
        cur_time_ms = (time.time() * 1_000)
        time_to_sleep_ms = end_time_ms - cur_time_ms
        logger.debug(f"Sleeping for {time_to_sleep_ms} ms")
        logger.debug(f"Start time: {start_time_ms}, End time: {end_time_ms}, Current time:  {cur_time_ms}")

        # Need to make sure calculation wasn't negative. If it was, that means the queries
        # above took longer than a second for whatever reason
        if time_to_sleep_ms < 0:
            logger.error("Sleep time is negative, continuing without sleeping.")
        else:
            time.sleep(time_to_sleep_ms / 1_000)

    # Convert metrics to Pandas DataFrame for convenience
    # then save to CSV output files specified
    logger.info("Completed querying metrics")
    vap_metrics_df = pd.DataFrame(vap_metrics)
    port_metrics_df = pd.DataFrame(port_metrics)
    cx_metrics_df = pd.DataFrame(cx_metrics)

    if len(port_eids) != 0:
        logger.info(f"Writing port metrics to \'{port_metrics_csv}\'")
        port_metrics_df.to_csv(port_metrics_csv, index=False)

    if len(cx_names) != 0:
        logger.info(f"Writing CX metrics to \'{cx_metrics_csv}\'")
        cx_metrics_df.to_csv(cx_metrics_csv, index=False)

    if len(vap_eids) != 0:
        logger.info(f"Writing vAP metrics to \'{vap_metrics_csv}\'")
        vap_metrics_df.to_csv(vap_metrics_csv, index=False)


def parse_port_fields(port_fields: str) -> list[str]:
    """
    Parse out field names into list, if any specified.
    Otherwise, return None
    """
    if port_fields:
        port_fields = port_fields.split(",")

        # Always query for these fields, as it will be useful regardless
        # The 'alias' and 'port' fields are mandatory for filtering data
        # later on in this script
        port_fields.extend(["alias", "port", "down", "phantom", "ip",])
        port_fields = list(set(port_fields))

    return port_fields


def parse_cx_fields(cx_fields: str) -> list[str]:
    """
    Parse out field names into list, if any specified.
    Otherwise, return None
    """
    if cx_fields:
        cx_fields = cx_fields.split(",")

        # Always query for these fields, as they will be useful regardless.
        cx_fields.extend(["name", "type", "state", "bps+rx+a", "bps+rx+b"])
        cx_fields = list(set(cx_fields))

    return cx_fields


def parse_vap_fields(vap_fields: str) -> list[str]:
    """
    Parse out field names into list, if any specified.
    Otherwise, return None
    """
    if vap_fields:
        vap_fields = vap_fields.split(",")

        # Always query for these fields, as they will be useful regardless.
        # The 'station bssid' and 'ap' fields are mandatory for filtering data
        # later on in this script
        vap_fields.extend(["ap", "station+bssid", "station+ssid"])
        vap_fields = list(set(vap_fields))

    return vap_fields


def clear_port_counters(session: LFSession, port_eids: list[str]) -> int:
    logger.info(f"Clearing port counters for port(s): {port_eids}")

    post = session.get_command()
    for port_eid in port_eids:
        ret, (_, resource, port) = parse_eid(port_eid=port_eid)
        if ret != 0:
            return ret

        try:
            response = post.post_clear_port_counters(resource=resource,
                                                     port=port)
            if response and response.status != HTTPStatus.OK:
                logger.error(f"Failed to clear port counters for port \'{port_eid}\', "
                             f"returned status code {response.status}")
                return -1
            elif not response:
                logger.error(f"Failed to clear port counters for port \'{port_eid}\', timed out")
                return -1
        except BaseException:
            logger.error(
                f"Failed to clear port counters for port \'{port_eid}\', exception encountered")
            return -1

    return 0


def clear_cx_counters(session: LFSession, cx_names: list[str]) -> int:
    logger.info(f"Clearing CX counters for CX(s): {cx_names}")

    post = session.get_command()
    for cx_name in cx_names:
        try:
            response = post.post_clear_cx_counters(cx_name=cx_name)
            if response and response.status != HTTPStatus.OK:
                logger.error(f"Failed to clear CX counters for CX \'{cx_name}\', "
                             f"returned status code {response.status}")
                return -1
            elif not response:
                logger.error(f"Failed to clear CX counters for CX \'{cx_name}\', timed out")
                return -1
        except BaseException:
            logger.error(f"Failed to clear CX counters for CX \'{cx_name}\', exception encountered")
            return -1

    return 0


def query_vap_metrics(session: LFSession,
                      timestamp: int,
                      vap_list: list[str],
                      vap_fields: list[str],
                      vap_metrics: list) -> None:
    logger.debug(f"Querying vAP metrics for vAPs {vap_list}")
    query = session.get_query()

    # Since the EIDs for associated stations do not contain the LANforge vAP
    # the station is associated to, we have to query for all associated stations
    # (using a bit of a workaround) and filter out stations that are associated
    # to vAPs we care about
    query_results = query.get_stations(eid_list=["/all"],
                                       requested_col_names=vap_fields)
    if not query_results:
        logger.warning("No stations associated to vAP")
        return 1

    # If one result is returned, it's returned as a dict. When more than
    # one result is returned, it's returned as a list of dicts.
    # Make single result into same format to simplify processing
    if isinstance(query_results, dict):
        sta_bssid = query_results.get("station bssid")
        if not sta_bssid:
            logger.error("key \'station bssid\' not found in queried results")
            return 1
        else:
            query_results = [{sta_bssid: query_results}]

    # Iterate through stations returned, searching for stations
    # which are associated to vAPs we care about
    for query_result in query_results:
        sta_bssid = list(query_result.keys())[0]
        associated_sta_data = query_result[sta_bssid]

        vap_eid = associated_sta_data["ap"]
        if vap_eid not in vap_list:
            # This is possible since we can't easily filter '/stations' endpoint data
            # for a specific vAP. The EIDs for it are only meaningful internally
            continue

        # This is a station associated to a vAP we care about.
        # Track it for post processing at the end of the script
        associated_sta_data["timestamp"] = timestamp
        vap_metrics.append(associated_sta_data)

    return 0


def query_port_metrics(session: LFSession,
                       timestamp: int,
                       eid_list: list[str],
                       port_fields: list[str],
                       port_metrics: list) -> None:
    logger.debug(f"Querying port metrics for ports {eid_list}")
    query = session.get_query()

    # Query LANforge for port data
    query_results = query.get_port(eid_list=eid_list,
                                   requested_col_names=port_fields)
    if not query_results:
        logger.warning("No port data returned")
        return 1

    # If one result is returned, it's returned as a dict. When more than
    # one result is returned, it's returned as a list of dicts.
    # Make single result into same format to simplify processing
    if isinstance(query_results, dict):
        alias = query_results.get("alias")
        numeric_eid = query_results.get("port")

        if not numeric_eid:
            logger.error("\'port\' key not found in queried results")
            return 1
        elif not alias:
            logger.error("\'alias\' key not found in queried results")
            return 1

        ret, named_port_eid = numeric_to_named_eid(numeric_eid=numeric_eid, alias=alias)
        if ret != 0:
            return ret

        query_results = [{named_port_eid: query_results}]

    # Iterate through ports returned, searching for ports we care about
    for query_result in query_results:
        port_eid = list(query_result.keys())[0]

        if port_eid not in eid_list:
            logger.warning(f"Unexpected port {port_eid} found in queried port data")
            continue

        # This is a port we care about.
        # Track it for post processing at the end of the script
        queried_port_metrics = query_result[port_eid]
        queried_port_metrics["timestamp"] = timestamp
        queried_port_metrics["eid"] = port_eid
        port_metrics.append(queried_port_metrics)

    return 0


def query_cx_metrics(session: LFSession,
                     timestamp: int,
                     cx_names: list[str],
                     cx_fields: list[str],
                     cx_metrics: list) -> None:
    logger.debug(f"Querying CX metrics for CX(s) {cx_names}")
    query = session.get_query()

    query_results = query.get_cx(eid_list=["/all"],
                                 requested_col_names=cx_fields)
    if not query_results:
        logger.warning("No CXs exist")
        return 1

    # Iterate through CXs returned, searching for CXs specified by user
    for cx_name, queried_cx_metrics in query_results.items():
        if cx_name not in cx_names:
            logger.warning(f"Unexpected CX {cx_name} found in queried CX data")
            continue

        # Desired CX match. Track it for post processing at the end of the script
        queried_cx_metrics["timestamp"] = timestamp
        cx_metrics.append(queried_cx_metrics)

    return 0


def parse_eid(port_eid: str) -> tuple[int, tuple[str, str, str]]:
    """
    Parse a port EID of the format 'shelf.resource.port'
    into its requisite components. For example, '1.1.vap0000'.
    """
    components = port_eid.split(".")

    if len(components) != 3:
        logger.error(f"Invalid port EID \'{port_eid}\'")
        return 1, None

    return 0, (components[0], components[1], components[2])


def numeric_to_named_eid(numeric_eid: str, alias: str) -> tuple[int, str]:
    """
    Convert from a numeric to named Port EID.
    """
    ret, (shelf, resource, _) = parse_eid(port_eid=numeric_eid)
    if ret != 0:
        return ret, None

    return 0, f"{shelf}.{resource}.{alias}"


def configure_logging(debug: bool = False):
    """
    Configure logging for script, including color-coded output when running on Linux.
    """
    # Configuration for all loggers, including this module
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s (%(name)s): %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")

    # Only log errors in imported module loggers to improve output readability
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.ERROR)

    # Configure this modules' logger
    global logger
    logger = logging.getLogger("AP Validation")
    logger.setLevel(logging.INFO)

    # If debugging specified, then increase logging verbosity
    if debug:
        root_logger.setLevel(logging.INFO)
        logger.setLevel(logging.DEBUG)

    if sys.platform.startswith('linux'):
        logging.addLevelName(
            logging.ERROR,
            "\033[1;31m%s\033[1;0m" %
            logging.getLevelName(
                logging.ERROR))
        logging.addLevelName(
            logging.WARNING,
            "\033[1;33m%s\033[1;0m" %
            logging.getLevelName(
                logging.WARNING))
        logging.addLevelName(
            logging.INFO,
            "\033[1;32m%s\033[1;0m" %
            logging.getLevelName(
                logging.INFO))


def parse_args():
    parser = argparse.ArgumentParser(
        prog="query_metrics.py",
        description="Script designed to gather metrics from one or more LANforge "
                    "virtual access points (vAPs) as another test runs once per "
                    "second for the specified duration. This test assumes all vAPs "
                    "and other ports to query already exist.")

    parser.add_argument("--mgr",
                        type=str,
                        default="localhost",
                        help="Hostname for where LANforge GUI is running")
    parser.add_argument("--mgr_port",
                        type=int,
                        default=8080,
                        help="Port LANforge GUI HTTP service is running on")
    parser.add_argument("--debug",
                        default=False,
                        action="store_true",
                        help="Enable verbose debug logging")

    parser.add_argument("--duration",
                        type=int,
                        default=120,
                        help="Time duration to query metrics from LANforge.")

    parser.add_argument("--port_eid",
                        dest="port_eids",
                        action="append",
                        default=[],
                        help="Entity ID(s) of the desired LANforge port(s) to query")
    parser.add_argument("--cx_name",
                        dest="cx_names",
                        action="append",
                        default=[],
                        help="Name(s) of the desired LANforge CX(s) to query")
    parser.add_argument("--vap_eid",
                        dest="vap_eids",
                        action="append",
                        default=[],
                        help="Entity ID(s) of the desired LANforge vAP(s) to query.")

    parser.add_argument("--port_fields", "--port_columns",
                        dest="port_fields",
                        default=None,
                        help="Comma separated list of port data to query (columns in 'Port Mgr' table). "
                             "The value strings are parsed directly into the URL, so whitespace should "
                             "be URL encoded. For example, \'port type\' and \'parent dev\' would be "
                             "specified by passing \'--column_names \"port+type\",\"parent+dev\"\'")
    parser.add_argument("--cx_fields", "--cx_columns",
                        dest="cx_fields",
                        default=None,
                        help="Comma separated list of CX data to query (columns in 'Layer-3' table). "
                             "The value strings are parsed directly into the URL, so whitespace should "
                             "be URL encoded. See \'--port_fields\' for more info.")
    parser.add_argument("--vap_fields", "--vap_columns",
                        dest="vap_fields",
                        default=None,
                        help="Comma separated list of vAP data to query (columns in 'vAP Stations' table). "
                             "The value strings are parsed directly into the URL, so whitespace should "
                             "be URL encoded. See \'--port_fields\' for more info.")

    parser.add_argument("--port_metrics_csv",
                        type=str,
                        default="port_metrics.csv",
                        help="Path to file where port metrics will be written to as CSV.")
    parser.add_argument("--cx_metrics_csv",
                        type=str,
                        default="cx_metrics.csv",
                        help="Path to file where Layer-3 CX metrics will be written to as CSV.")
    parser.add_argument("--vap_metrics_csv",
                        type=str,
                        default="vap_metrics.csv",
                        help="Path to file where vAP metrics will be written to as CSV.")

    parser.add_argument("--no_clear_port_counters",
                        action="store_true",
                        help="Don't clear port counters before querying.")
    parser.add_argument("--no_clear_cx_counters",
                        action="store_true",
                        help="Don't clear Layer-3 CX counters before querying.")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    configure_logging(debug=args.debug)

    if len(args.port_eids) == 0 and len(args.vap_eids) == 0 and len(args.cx_names) == 0:
        logger.error("No ports, vAPs, or CXs specified to query")
        exit(1)

    # The '**vars()' unpacks the 'args' variable's contents
    # into the arguments specified in the function.
    #
    # Argument names must match the 'args' variable's.
    # Any non-existent arguments are unpacked into the functions
    # 'kwargs' argument. Should it not exist, an exception is thrown.
    ret = main(**vars(args))
    exit(ret)
