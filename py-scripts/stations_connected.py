#!/usr/bin/env python3

# Contains examples of using realm to query stations and get specific information from them

import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append('../py-json')

from LANforge.lfcli_base import LFCliBase


class QueryStationsExample(LFCliBase):
    def __init__(self, lfjson_host, lfjson_port):
        super().__init__(_lfjson_host=lfjson_host, _lfjson_port=lfjson_port, _halt_on_error=True, _debug=True)

    def run(self):
        pass


def main():
    qstationsx = QueryStationsExample("localhost", 8080)
    qstationsx.run()


if __name__ == "__main__":
    main()
