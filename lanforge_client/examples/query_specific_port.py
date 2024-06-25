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
         port_eid: str,
         column_names: str,
         **kwargs):
    # Parse out column names into list, if specified.
    # Otherwise, use default to handful of standard columns
    if column_names != "":
        column_names = column_names.split(",")
    else:
        column_names = ["down", "phantom", "ip"]

    # Always query for port alias
    if "alias" not in column_names:
        column_names.append("alias")

    # Instantiate a LANforge API session with the specified LANforge system.
    #
    # The JSON API port is almost always 8080. The LANforge server port,
    # which isn't relevant here, are in the 4001+ range
    session = lanforge_api.LFSession(
        lfclient_url=f"http://{mgr}:{mgr_port}",
    )

    # Returns LFJsonQuery instance which is used to invoke GET requests
    query = session.get_query()

    # Query the ports on the system by sending a JSON GET to the '/port' endpoint
    #
    # NOTE: Currently specifying an empty 'eid_list' will not return all ports
    #       as one might expect, given that a GET to '/port' will return all ports.
    #       To work around this, specify the eid_list using only the '/list' string
    #
    query_results = query.get_port(eid_list=[port_eid],
                                   requested_col_names=column_names)
    if not query_results:
        print(
            f"ERROR: Failed to query port \'{port_eid}\' for columns: {column_names}")
        exit(1)

    for field in ["COLUMN NAME", "COLUMN DATA"]:
        print(f"{field:<20}", end="")
    print()

    # Always print port EID first
    queried_port_alias = query_results.get("alias")
    if not queried_port_alias:
        print("ERROR: Port alias not found in queried results")
        exit(1)
    else:
        query_results.pop("alias")
        column_name = "alias"
        column_data = queried_port_alias
        print(f"{column_name:<20}{column_data:<20}")

    for column_name in query_results:
        column_data = query_results[column_name]
        print(f"{column_name:<20}{column_data:<20}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="query_specific_port.py",
        description="Example script to demonstrate using LANforge API to print out port status information "
                    "for a specific port. This example supports specifying specific column names to query "
                    "via the \'--column_names\' argument. Run with \'--help\' for more details.",
    )
    parser.add_argument("--mgr",
                        default="localhost",
                        help="Hostname for where LANforge GUI is running")
    parser.add_argument("--mgr_port",
                        default=8080,
                        help="Port LANforge GUI HTTP service is running on")
    parser.add_argument("--port_eid",
                        required=True,
                        help="Name of port to query")
    parser.add_argument("--column_names",
                        default="",
                        help="Comma separated list of port data to query (columns in 'Port Mgr' table). "
                             "The value strings are parsed directly into the URL, so whitespace should "
                             "be URL encoded. For example, \'port type\' and \'parent dev\' would be "
                             "specified by passing \'--column_names \"port+type\",\"parent+dev\"\'")
    args = parser.parse_args()

    # The '**vars()' unpacks the 'args' variable's contents
    # into the arguments specified in the function.
    #
    # Argument names must match the 'args' variable's.
    # Any non-existent arguments are unpacked into the functions
    # 'kwargs' argument. Should it not exist, an exception is thrown.
    main(**vars(args))
