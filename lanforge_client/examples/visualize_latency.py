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
         endp: str,
         width: int,
         **kwargs):

    # Instantiate a LANforge API session with the specified LANforge system.
    #
    # The JSON API port is almost always 8080. The LANforge server port,
    # which isn't relevant here, are in the 4001+ range
    session = lanforge_api.LFSession(
        lfclient_url=f"http://{mgr}:{mgr_port}",
    )

    # Returns LFJsonQuery instance which is used to invoke GET requests
    query = session.get_query()

    # Query for the given endpoint
    query_results = query.get_endp(eid_list=[endp],
                                   requested_col_names="adv-rt-latency-5m")
    if not query_results:
        print(f"Endpoint '{endp}' could not be found.")
        exit(1)

    latency_results = query_results["adv-rt-latency-5m"]

    # If the above entry is not populated, then the 'Advanced Latency' feature may not be enabled,
    # or may not be supported by that endpoint. In that event, we will fall back to the older
    # latency histogram.
    if not latency_results:
        query_results = query.get_endp(eid_list=[endp],
                                       requested_col_names="rt-latency-5m")
        latency_results = query_results["rt-latency-5m"]

    # The counts for each column of the histogram are given as a list by the 'histogram' entry.
    # Each count represents the frequency that a particular latency was recorded between an upper
    # and lower limit, given by the 'item_bounds' entry (described below).
    counts = latency_results["histogram"]

    # The histogram item bounds are given by the 'item_bounds' entry. This data is a list.
    # These represent, in milliseconds, the upper and lower times counted by each bucket in the
    # histogram data. The indices for this list will line up with the count data from the
    # 'histogram' entry.
    bounds = latency_results["item_bounds"]

    # Find the minimum and maximum indices where the counts are populated
    lowest_counted_index = -1
    highest_counted_index = -1
    for i, count in enumerate(counts):
        if count > 0:
            if lowest_counted_index == -1:
                lowest_counted_index = i

            highest_counted_index = i

    # Exit early if we don't have any data to show
    if lowest_counted_index == highest_counted_index:
        print("No data to show")
        exit(0)

    # Restrict our bounds and counts lists to be within the populated indices
    bounds = bounds[lowest_counted_index:highest_counted_index + 1]
    counts = counts[lowest_counted_index:highest_counted_index + 1]

    # Account for bounds labels
    width -= 15

    # Show table header
    print("Latency (ms)  | Frequency")
    print("--------------+" + ('-' * width))

    # Find a count divisor that will make the visualization fit within within
    # the desired width
    highest_count = max(counts)
    divisor = highest_count // width

    # In case width > highest_count, we'll make sure that we aren't dividing
    # by zero
    divisor = max(divisor, 1)

    for bound, count in zip(bounds, counts):
        # Each bound is a list, where the first entry is the low end of the bound and the second
        # entry is the high end of the bound
        hi = bound[1]
        lo = bound[0]

        # We will normalize the count so that it fits *just* within the desired
        # width
        normalized_count = (count + divisor - 1) // divisor

        # Show the visualization
        prefix = f"{lo} to {hi}"
        print(f"{prefix: <13} |" + ('X' * normalized_count))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="visualize_latency.py",
        description="Example script to demonstrate using LANforge API to query and visualize endpoint latency distributions",
    )
    parser.add_argument("--mgr",
                        default="localhost",
                        help="Hostname for where LANforge GUI is running")
    parser.add_argument("--mgr_port",
                        default=8080,
                        help="Port LANforge GUI HTTP service is running on")
    parser.add_argument("--endp", "--endpoint",
                        dest="endp",
                        type=str,
                        help="Endpoint name or EID whose latency should be visualized")
    parser.add_argument("--width",
                        type=int,
                        default=80,
                        help="Text width for the latency visualization")
    args = parser.parse_args()

    # The '**vars()' unpacks the 'args' variable's contents
    # into the arguments specified in the function.
    #
    # Argument names must match the 'args' variable's.
    # Any non-existent arguments are unpacked into the functions
    # 'kwargs' argument. Should it not exist, an exception is thrown.
    main(**vars(args))
