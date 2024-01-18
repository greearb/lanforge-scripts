"""
    This script will give the port manger fields data

    Example :  python3 lf_show_ports.py --add_fields True --fields "port,phantom,down,ip,alias,parent dev,..."etc

"""

import pprint
import sys
import os
import importlib
from argparse import ArgumentParser, RawTextHelpFormatter

if sys.version_info[0] != 3:
    print("The script required python3")
    exit()

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
LFRequest = importlib.import_module("py-json.LANforge.LFRequest")

class show_ports:
    def __init__(self,
                 url="http://localhost:8080/port/1/1/list",
                 fields="",
                 add_fields=False):
        self.url = url
        self.fields = fields.lower()
        self.add_fields = add_fields

    def show_ports(self):
        if self.add_fields:
            url= "http://localhost:8080/port?fields=_links,alias,down,phantom,port,%s" % (self.fields)
            print("Added Fields:", self.fields)
        else:
            url = self.url
        lf_r = LFRequest.LFRequest(url=url)
        json_response = lf_r.getAsJson()
        printer = pprint.PrettyPrinter(indent=2)
        printer.pprint(json_response)
        return json_response

def main():
    help_summary = '''\
    This script provides information about various fields in the port manager. By default details such as port numbers, 
    alias,down,phantom state and port will be shown. Also allows you to specify which fields you want to see 
    using the script arguments. Additionally it wil offer a comprehensive overview of the status and configuration of 
    different ports in a straightforward manner.
        '''
    parser  = ArgumentParser(prog=__file__,
                             formatter_class=RawTextHelpFormatter,
                             description="""
 lf_show_ports.py    
-----------------------------------------------
PORTS DESCRIPTION   
port            ---     To get the Port numbers
phantom         ---     To get the Phantom state info
down            ---     To get the Down state info
ip              ---     To get the IP address for all ports
alias           ---     To get Alias info
parent dev      ---     To get Parent Dev info
channel         ---     To get Channel info
mode            ---     To get Mode info 
status          ---     To get Status info 
signal          ---     To get Signal info 
rx-rate         ---     To get Rx-Rate info 
tx-rate         ---     To get Tx-Rate info  
chain rssi      ---     To get Chain RSSI           
avg chain rssi  ---     To get Avg Chain RSSI 
ssid            ---     To get SSID info 
gateway ip      ---     To get Gateway IP 
mac             ---     To get MAC info  
                                            """)
    parser.add_argument("--add_fields", default=False,
                        help='''To add extra fields data (True or False)
                            --add_fields True''')
    parser.add_argument("--fields", default='_links,alias,down,phantom,port',
                       help='''Specify to print the fields data in console & Need to specify the fields names 
                               separated with comas(,)
                            --fields "port,ip,mode,phantom,alias,parent dev,channel,...."etc
                            ''')
    parser.add_argument('--help_summary', help='Show summary of what this script does', default=None,
                        action="store_true")

    args = parser.parse_args()

    # help summary
    if args.help_summary:
        print(help_summary)
        exit(0)
    obj = show_ports(fields=args.fields,add_fields=args.add_fields)
    obj.show_ports()

if __name__ == "__main__":
    main()
