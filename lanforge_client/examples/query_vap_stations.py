import argparse
import importlib
import sys
import os


# Get LANforge scripts path from environment variable 'LF_PYSCRIPTS'
if 'LF_SCRIPTS' not in os.environ:
    print("ERROR: Environment variable \'LF_SCRIPTS\' not defined")
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
from lanforge_client import lanforge_api  # noqa


def main(mgr: str,
         mgr_port: int,
         column_names: str,
         **kwargs):
    # Parse out column names into list, if specified.
    # Otherwise, default to handful of standard columns
    if column_names != "":
        column_names = column_names.split(",")
    else:
        column_names = [
            "station+ssid",
            "station+bssid",
            "ip",
            "signal+avg",
            "tx+rate",
            "rx+rate"]

    # Always query for vAP EID
    if "ap" not in column_names:
        column_names.append("ap")

    # Instantiate a LANforge API session with the specified LANforge system.
    #
    # The JSON API port is almost always 8080. The LANforge server port,
    # which isn't relevant here, are in the 4001+ range
    session = lanforge_api.LFSession(
        lfclient_url=f"http://{mgr}:{mgr_port}",
    )

    # Returns LFJsonQuery instance which is used to invoke GET requests
    query = session.get_query()

    # Query for any stations associated to LANforge vAP(s)
    #
    # NOTE: Currently specifying an empty 'eid_list' will not return all JSON endpoint data
    #       as one might expect, given that an arbitrary GET to the same JSON endpoint will.
    # To work around this, specify the eid_list using only the '/list' string
    query_results = query.get_stations(eid_list=["/list"],
                                       requested_col_names=column_names)
    if not query_results:
        print(f"ERROR: No stations associated to vAP")
        exit(1)

    # If one result is returned, it's returned as a dict. When more than
    # one result is returned, it's returned as a list of dicts.
    # Make single result into same format to simplify processing
    if isinstance(query_results, dict):
        sta_bssid = query_results.get("station bssid")
        if not sta_bssid:
            print("ERROR: station BSSID not found in queried results")
            exit(1)
        else:
            query_results = [{sta_bssid: query_results}]

    col_name_str = "COLUMN NAME"
    col_data_str = "COLUMN DATA"
    blank_str = ""
    for ix, query_result in enumerate(query_results, 1):
        sta_ix_str = f"STA {ix}"
        print(f"{sta_ix_str:<10}{col_name_str:<20}{col_data_str}")

        sta_bssid = list(query_result.keys())[0]
        associated_sta_data = query_result[sta_bssid]

        # Always print vAP EID first
        queried_vap_eid = associated_sta_data.get("ap")
        if not queried_vap_eid:
            print("ERROR: vAP EID not found in queried results")
            exit(1)
        else:
            associated_sta_data.pop("ap")
            column_name = "ap"
            column_data = queried_vap_eid
            print(f"{blank_str:<10}{column_name:<20}{column_data:<20}")

        for column_name in associated_sta_data:
            column_data = associated_sta_data[column_name]
            print(f"{blank_str:<10}{column_name:<20}{column_data:<20}")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="query_vap_stations.py",
        description="Example script to demonstrate using LANforge API to query and print out vAP station information",
    )
    parser.add_argument("--mgr",
                        default="localhost",
                        help="Hostname for where LANforge GUI is running")
    parser.add_argument("--mgr_port",
                        default=8080,
                        help="Port LANforge GUI HTTP service is running on")
    parser.add_argument("--column_names",
                        default="",
                        help="Comma separated list of vAP data to query (columns in 'vAP Stations' table). "
                             "The value strings are parsed directly into the URL, so whitespace should "
                             "be URL encoded. For example, \'tx rate\' and \'rx rate\' would be "
                             "specified by passing \'--column_names \"tx+rate\",\"rx+rate\"\'")
    args = parser.parse_args()

    # The '**vars()' unpacks the 'args' variable's contents
    # into the arguments specified in the function.
    #
    # Argument names must match the 'args' variable's.
    # Any non-existent arguments are unpacked into the functions
    # 'kwargs' argument. Should it not exist, an exception is thrown.
    main(**vars(args))
