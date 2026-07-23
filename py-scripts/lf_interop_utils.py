#!/usr/bin/env python3
"""
NAME: lf_interop_utils.py

PURPOSE:
lf_interop_utils.py provides shared helpers for interop test scripts (lf_webpage.py, lf_ftp.py,
lf_interop_*.py, ...). It resolves LANforge layer4 API field names that vary
across server versions -- for example, 'rx rate (1m)' and 'rx-rate-1m' on different LANforge server builds. Requesting a name a given
server doesn't recognize fails the whole layer4 query and it utils prevents it.

Run standalone to inspect what a given LANforge server actually calls each of these fields,
without needing to start a full test first (an existing layer4 CX must already be running on
the server, e.g. started by another script, for there to be anything to probe).

EXAMPLE-1:
Command Line Interface to detect a LANforge server's layer4 field names
python3 lf_interop_utils.py --mgr 192.168.200.165 --get_l4_fields

EXAMPLE-2:
Command Line Interface to probe a specific CX instead of auto-picking the first one found
python3 lf_interop_utils.py --mgr 192.168.200.165 --get_l4_fields --cx_name wlan0_http30_l4
"""
import argparse
import importlib
import logging
import os
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm

logger = logging.getLogger(__name__)

# Known alternate spellings LANforge servers have used for the same layer4 column, newest known
# name first. Every field read from a layer4 record should have an entry here (even a
# single-alias one) so a future rename only needs a new alias added in one place.
LAYER4_FIELD_ALIASES = {
    'uc_avg': ['uc-avg'],
    'uc_max': ['uc-max'],
    'uc_min': ['uc-min'],
    'total_urls': ['total-urls'],
    'rx_rate_1m': ['rx-rate-1m', 'rx rate (1m)'],
    'tx_rate_1m': ['tx-rate-1m'],
    'bytes_rd': ['bytes-rd'],
    'total_err': ['total-err'],
    'status': ['status'],
}


def resolve_layer4_fields(local_realm, cx_name, field_keys, defaults=None):
    """Probe one CX to find which known alias each field_key uses on this server, returning
    {field_key: resolved_name}."""
    defaults = defaults or {}
    candidates_by_key = {key: LAYER4_FIELD_ALIASES.get(key, [key]) for key in field_keys}
    resolved = {key: defaults.get(key, candidates[0]) for key, candidates in candidates_by_key.items()}
    if not cx_name:
        return resolved
    try:
        # No 'fields' filter: the server returns every column it supports for this CX, so we
        # can check which alias is present without risking an invalid-field-name error.
        probe = local_realm.json_get('layer4/{}/list'.format(cx_name))
        endpoint = probe.get('endpoint') if probe else None
        if isinstance(endpoint, list) and endpoint:
            endpoint = list(endpoint[0].values())[0]
        if isinstance(endpoint, dict):
            for key, candidates in candidates_by_key.items():
                for candidate in candidates:
                    if candidate in endpoint:
                        resolved[key] = candidate
                        break
    except Exception:
        logger.warning("Could not probe layer4 columns, using default field names: %s", resolved)
    return resolved


def layer4_fields_query(resolved_fields, field_keys):
    """Build the comma-separated 'fields=' value for a layer4 list request, in order, from a
    resolve_layer4_fields() result."""
    return ','.join(resolved_fields[key] for key in field_keys)


def find_any_cx_name(local_realm):
    """Return the name of any one layer4 CX currently on the server, or None if there aren't any."""
    try:
        response = local_realm.json_get('layer4/list')
        endpoint = response.get('endpoint') if response else None
    except Exception:
        return None
    if isinstance(endpoint, dict):
        return endpoint.get('name')
    if isinstance(endpoint, list) and endpoint:
        return list(endpoint[0].keys())[0]
    return None


def main():
    parser = argparse.ArgumentParser(
        prog='lf_interop_utils.py',
        formatter_class=argparse.RawTextHelpFormatter,
        description=__doc__)
    parser.add_argument('--mgr', help='hostname for where LANforge GUI is running [default = localhost]', default='localhost')
    parser.add_argument('--mgr_port', help='port LANforge GUI HTTP service is running on [default = 8080]', type=int, default=8080)
    parser.add_argument('--cx_name', help='name of an existing layer4 CX to probe; if omitted, the first CX found on the server is used', default=None)
    parser.add_argument('--get_l4_fields', help='resolve and print this LANforge server\'s layer4 field names (e.g. rx-rate-1m vs rx rate (1m))', action='store_true')
    parser.add_argument('--help_summary', action='store_true', help='Show summary of what this script does')
    args = parser.parse_args()

    help_summary = '''\
lf_interop_utils.py provides shared helpers for interop test scripts, most notably resolving
LANforge layer4 API field names (e.g. 'rx rate (1m)' vs 'rx-rate-1m') that vary across server
versions. Run with --get_l4_fields to detect what a given LANforge server calls these fields.
'''
    if args.help_summary:
        print(help_summary)
        exit(0)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    if not args.get_l4_fields:
        parser.print_help()
        return

    local_realm = Realm(lfclient_host=args.mgr, lfclient_port=args.mgr_port)
    cx_name = args.cx_name or find_any_cx_name(local_realm)
    if not cx_name:
        logger.error("No layer4 CXs found on %s:%s; start a test that creates one first, "
                     "or pass --cx_name explicitly.", args.mgr, args.mgr_port)
        exit(1)

    fields = resolve_layer4_fields(local_realm, cx_name, LAYER4_FIELD_ALIASES.keys())
    print("Resolved layer4 field names on {}:{} (probed CX '{}'):".format(args.mgr, args.mgr_port, cx_name))
    for key, value in fields.items():
        print("  {:15s} -> {}".format(key, value))


if __name__ == '__main__':
    main()
