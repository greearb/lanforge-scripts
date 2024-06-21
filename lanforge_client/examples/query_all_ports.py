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
         **kwargs):
    # Instantiate a LANforge API session with the specified LANforge system.
    #
    # The JSON API port is almost always 8080. The LANforge server port,
    # # which isn't relevant here, are in the 4001+ range
    session = lanforge_api.LFSession(
        lfclient_url=f"http://{mgr}:{mgr_port}",
    )

    # Returns LFJsonQuery instance which is used to invoke GET requests
    query = session.get_query()

    # Query the ports on the system by sending a JSON GET to the '/port' endpoint
    #
    # NOTE: Currently specifying an empty 'eid_list' will not return all ports
    #       as one might expect, given that a GET to '/port' will return all ports.
    # To work around this, specify the eid_list using only the '/list' string
    query_results = query.get_port(eid_list=["/list"], debug=True)

    # Print table header
    for field in ["PORT EID", "PHANTOM", "DOWN"]:
        print(f"{field:<20}", end="")
    print()

    # Print port data in table
    for port_data in query_results:
        # Port data is returned as a list of dicts where each dict
        # contains one key-value pair. The key is the port EID
        # and the value is a dict that contains the queried port data
        #
        # NOTE: When only one port is returned, the data is returned as just a dict
        #       not a list of dicts.
        port_eid = list(port_data.keys())[0]
        phantom = "yes" if port_data[port_eid]["phantom"] == 1 else "no"
        down = "yes" if port_data[port_eid]["down"] == 1 else "no"

        print(f"{port_eid:<20}{phantom:<20}{down:<20}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="show_all_ports.py",
        description="Example script to demonstrate using LANforge API to print out port status information",
    )
    parser.add_argument("--mgr",
                        default="localhost",
                        help="Hostname for where LANforge GUI is running")
    parser.add_argument("--mgr_port",
                        default=8080,
                        help="Port LANforge GUI HTTP service is running on")
    args = parser.parse_args()

    # The '**vars()' unpacks the 'args' variable's contents
    # into the arguments specified in the function.
    #
    # Argument names must match the 'args' variable's.
    # Any non-existent arguments are unpacked into the functions
    # 'kwargs' argument. Should it not exist, an exception is thrown.
    main(**vars(args))
