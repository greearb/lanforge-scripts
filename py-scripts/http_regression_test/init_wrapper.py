#!/usr/bin/env python3

"""
NAME:       http_regression_test/init_wrapper.py

PURPOSE:    Establish the preconditions for a the regression test by invoking a given initialization
            script before invoking http_regression_test/main.py with the supplied arguments.

EXAMPLE:    $ python http_regression_test/init_wrapper.py \
                --init_script_args python http_regression_ports_init_ct_us_008.py \
                --regression_test_args baseline 5.5.2 192.168.101.137 --save 5.5.2-baseline.json --get /port/1/all
"""

import sys
import subprocess
import logging

# Some shenannigans to import the logger config from a cousin file
import importlib
from os import path
file_dir = path.dirname(path.realpath(__file__))
sys.path.insert(0, path.abspath(path.join(file_dir, "..")))

lf_logger_config = importlib.import_module("lf_logger_config")
logger = logging.getLogger(__name__)

# Get the path to the main test script
dir_path = path.dirname(path.realpath(__file__))
main_path = path.join(dir_path, "main.py")


def usage(help=False):
    if help:
        print("Establish the preconditions for a the regression test by invoking a given initialization\n"
              "script before invoking http_regression_test/main.py with the supplied arguments.\n")

    print("usage:\n"
          "    init_wrapper.py --init_script_args exe args... --regression_test_args args...")

    if help:
        exit(0)
    else:
        exit(1)


def main():
    args = sys.argv

    # Find argument indices
    try:
        init_index = args.index("--init_script_args")
    except ValueError:
        init_index = None

    try:
        test_index = args.index("--regression_test_args")
    except ValueError:
        test_index = None

    # Check for help
    if any((h in sys.argv) for h in ("-h", "--help", "--help_summary")):
        if init_index is None:
            usage(help=True)
        elif any((h in sys.argv[:init_index]) for h in ("-h", "--help", "--help_summary")):
            usage(help=True)

    # Check for invalid argument arrangements
    if init_index is None:
        print("Missing required argument '--init_script_args'\n")
        usage()

    elif test_index is None:
        print("Missing required argument '--regression_test_args'\n")
        usage()

    elif test_index <= init_index:
        print("'--init_script_args' must come before '--regression_test_args'\n")
        usage()

    # Slice arguments out of sys.argv based on the found indices
    init_args = sys.argv[init_index+1:test_index]
    test_args = ["python", main_path] + sys.argv[test_index+1:]

    # Execute both scripts with the given arguments
    subprocess.run(init_args)
    subprocess.run(test_args)


if __name__ == "__main__":
    main()
