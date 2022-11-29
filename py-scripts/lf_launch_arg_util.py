#!/usr/bin/env python3
'''
This module is meant to serve as a utility for converting command line arguments to VSCode launch.json formatted launch
parameters. Importing the script offers functions command_to_json, which takes a command string and returns a dict structure, and 
prettify_json, which creates and returns a pretty print string grouping parameters by the parameter and its input. 
If run as a script, the --command option should be used to provide a string containing the full command used for running the script.
The prettified output will be printed to the console.

See --help for options and examples
'''
import re
import argparse

def command_to_json(command: str) -> dict:
    '''
    command_to_json takes a command with arguments in a string and looks for command line parameters starting with '--' and
    assumes parameters without '--' is input for those parameters.
    Returns a json formatted data set similar in structure to what is found in VScode's launch.json
    '''
    regex_string = r"(\./\S+\s?|--\S+)\s?([^-]\S*)?"
    m = re.findall(regex_string, command)
    json_results = {}
    json_results['args'] = []
    json_results['command'] = ""
    for match in m:
        for i in match:
            if not i.startswith('./'):
                if i != '':
                    json_results['args'].append(i)
            else:
                json_results['command'] = i.strip()
    
    return json_results

def prettify_output(json_results: dict) -> str:
    '''
    prettify_output takes a dict created by the command_to_json function and returns an easy to read formatted string
    '''
    print(json_results)
    arg = 0
    prettified_output = f"\\\\ {json_results['command']}\n"
    prettified_output += '\\\\ "args": [\n'
    while arg <= len(json_results['args']) - 1:
        if arg+1 != len(json_results['args']) and not json_results['args'][arg+1].startswith('--'):
            prettified_output += f"\\\\ \t\"{json_results['args'][arg]}\", "
            arg += 1
        else:
            prettified_output += "\\\\ \t"

        if arg == len(json_results['args']) - 1:
            prettified_output += f"\"{json_results['args'][arg]}\"\n"
        else:
            prettified_output += f"\"{json_results['args'][arg]}\",\n"
        arg += 1

    prettified_output += "\\\\ ]"
    return prettified_output

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description='''Utility for creating launch.json params from command
    Command Example:
    ./lf_launch_arg_util.py --command "./test_ip_connection.py  --mgr 192.168.100.194 --num_stations 4 --upstream_port 1.1.eth2  --radio wiphy1 --ssid asus11ax-5 --passwd hello123 --security wpa2 --debug"

    \\\\ ./test_ip_connection.py 
    \\\\ "args": [
    \\\\    "--mgr", "192.168.100.194",
    \\\\    "--num_stations", "4",
    \\\\    "--upstream_port", "1.1.eth2",
    \\\\    "--radio", "wiphy1",
    \\\\    "--ssid", "asus11ax-5",
    \\\\     "--passwd", "hello123",
    \\\\    "--security", "wpa2"
    \\\\ ]
    ''')
    parser.add_argument('--command', help='Full command to be parsed surrounded by single or double quotes')

    args = parser.parse_args()
    print(prettify_output(command_to_json(args.command)))


if __name__ == '__main__':
    main()
