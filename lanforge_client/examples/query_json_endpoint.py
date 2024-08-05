#!/usr/bin/env python3
import argparse
import importlib
import pprint
import sys
import os


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
from lanforge_client import lanforge_api  # noqa


def main(mgr: str,
         mgr_port: int,
         json_endpoint: str,
         fields: str,
         **kwargs):
    # Parse out fields into list, if specified.
    if fields != "":
        fields = fields.split(",")
    else:
        fields = []

    # Instantiate a LANforge API session with the specified LANforge system.
    #
    # The JSON API port is almost always 8080. The LANforge server port,
    # which isn't relevant here, are in the 4001+ range
    session = lanforge_api.LFSession(
        lfclient_url=f"http://{mgr}:{mgr_port}",
    )

    # Returns LFJsonQuery instance which is used to invoke GET requests
    query = session.get_query()

    # Attempt to find the method which queries the JSON endpoint
    query_method = session.find_method(json_endpoint)
    if not query_method:
        print(
            f"ERROR: Failed to find LANforge API JSON GET method for JSON endpoint {json_endpoint}")
        exit(1)

    # Query the ports on the system by sending a JSON GET to the endpoint
    #
    # NOTE: Currently specifying an empty 'eid_list' will not return data for all EIDs
    #       as one might expect, given that a GET to '/port' will return all ports, for example.
    #       To work around this, specify the eid_list using only the '/list' string
    #
    query_results = query_method(eid_list=["/list"],
                                 requested_col_names=fields)
    if not query_results:
        print(
            f"ERROR: Failed to query JSON endpoint {json_endpoint} for fields: {fields}")
        exit(1)

    pprint.pprint(query_results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="query_json_endpoint.py",
        description="Example script to demonstrate using LANforge API to query and print out data from "
                    "the specified LANforge JSON API endpoint using the required \'--json_endpoint\' argument. "
                    "By default, no specific fields are queried, but a user can specify specific fields to "
                    "query from the provided endpoint using the \'--fields\' argument. Run with \'--help\' "
                    "for more details.")
    parser.add_argument("--mgr",
                        default="localhost",
                        help="Hostname for where LANforge GUI is running")
    parser.add_argument("--mgr_port",
                        default=8080,
                        help="Port LANforge GUI HTTP service is running on")
    parser.add_argument("--json_endpoint",
                        required=True,
                        help="Name of LANforge JSON endpoint to query (e.g. \'--json_endpoint \"/ports\"')")
    parser.add_argument("--fields",
                        default="",
                        help="Comma separated list of fields to query. Available fields generally "
                             "correspond to columns in GUI tables. If unspecified, no fields are "
                             "specified in the JSON GET request and default data is returned. "
                             "For example, \'--fields alias,ip\' when querying the \'/ports\' endpoint")
    args = parser.parse_args()

    # The '**vars()' unpacks the 'args' variable's contents
    # into the arguments specified in the function.
    #
    # Argument names must match the 'args' variable's.
    # Any non-existent arguments are unpacked into the functions
    # 'kwargs' argument. Should it not exist, an exception is thrown.
    main(**vars(args))
