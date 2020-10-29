#!/usr/bin/env python3
import pprint
import sys
import os

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

import argparse
from LANforge.lfcli_base import LFCliBase
from LANforge import LFUtils
import realm

parser = LFCliBase.create_bare_argparse(
    prog='scenario.py',
    formatter_class=argparse.RawTextHelpFormatter,
    epilog='''Load a database file and control test groups\n''',
    description='''scenario.py
--------------------
Generic command example:
python3 scenario.py --load db1 --action overwrite --clean_dut --clean_chambers

python3 scenario.py --start test_group1

python3 scenario.py --quiesce test_group1

python3 scenario.py --stop test_group1
''')

parser.add_argument('--load', help='name of database to load', default="DFLT")

parser.add_argument('--action', help='action to take with database {overwrite | append}', default="overwrite")

parser.add_argument('--clean_dut',
                    help='use to cleanup DUT will be when overwrite is selected, otherwise they will be kept',
                    action="store_true")

parser.add_argument('--clean_chambers',
                    help='use to cleanup Chambers will be when overwrite is selected, otherwise they will be kept',
                    action="store_true")

group = parser.add_mutually_exclusive_group()
group.add_argument('--start', help='name of test group to start', default=None)
group.add_argument('--quiesce', help='name of test group to quiesce', default=None)
group.add_argument('--stop', help='name of test group to stop', default=None)
args = parser.parse_args()

local_realm = realm.Realm(lfclient_host=args.mgr, lfclient_port=args.mgr_port, debug_=args.debug)

if args.load is not None:
    data = {
        "name": args.load,
        "action": args.action,
        "clean_dut": "no",
        "clean_chambers": "no"
    }
    if args.clean_dut:
        data['clean_dut'] = "yes"
    if args.clean_chambers:
        data['clean_chambers'] = "yes"
    local_realm.json_post("/cli-json/load", data)

elif args.start is not None:
    local_realm.json_post("/cli-json/start_group", {"name": args.start})
elif args.stop is not None:
    local_realm.json_post("/cli-json/stop_group", {"name": args.stop})
elif args.quiesce is not None:
    local_realm.json_post("/cli-json/quiesce_group", {"name": args.quiesce})