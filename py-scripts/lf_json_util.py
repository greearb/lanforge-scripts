#!/usr/bin/env python3
import argparse

help_summary = '''\
This file contains a helper module standardize_json_results.
standardize_json_results takes a dict of information retrieved from json_get and standardizes
it to use the plural version of the data requested.
The data is returned starting with the "endpoints"
The script will read column data from lanforge GUI using request
'''


def standardize_json_results(results):
    # TODO: Add functionality to handle other plural vs singular data representations
    if 'endpoints' not in results:
        tmp_results = {}
        print(results)
        results = results['endpoint']
        name = results['name']  # noqa: F841
        tmp_results['endpoints'] = []
        tmp_results['endpoints'].append({results['name']: results})
        results = tmp_results

    return results['endpoints']


def main():
    # Only print help summary when invoked from command line
    parser = argparse.ArgumentParser(
        prog="lf_json_util.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description=f"""{help_summary}""")
    parser.add_argument('--help_summary', action="store_true", help='Show summary of what this script does')
    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)


if __name__ == "__main__":
    main()
