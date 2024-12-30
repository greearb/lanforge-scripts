#!/usr/bin/env python3
# flake8: noqa
import argparse

help_summary='''\
This file contains a helper module standardize_json_results.
standardize_json_results takes a dict of information retrieved from json_get and standardizes
it to use the plural version of the data requested.
The data is returned starting with the "endpoints"
The script will read column data from lanforge GUI using request
'''


def standardize_json_results(results):
    f'''{help_summary}
    TODO: Add functionality to handle other plural vs singular data representations
    '''
    if 'endpoints' not in results: 
        tmp_results = {}
        print(results)
        results = results['endpoint']
        name = results['name']
        tmp_results['endpoints'] = []
        tmp_results['endpoints'].append({results['name']: results})
        results = tmp_results

    return results['endpoints']

# used so help summary may work
def main():
    parser = argparse.ArgumentParser(
        prog="lf_json_api.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description=f"""{help_summary}""")
    parser.add_argument('--help_summary', action="store_true", help='Show summary of what this script does')
    args = parser.parse_args()
    
    if args.help_summary:
        print(help_summary)
        exit(0)


if __name__ == "__main__":
    main()

