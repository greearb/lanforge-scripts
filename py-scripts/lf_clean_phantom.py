import re
import sys
import os
import importlib
import argparse
import time
import logging

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
logger = logging.getLogger(__name__)
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

class clean_phantom(Realm):
    def __init__(self,host="localhost",port=8080,resource=None,clean_phantom_port=None):
        super().__init__(lfclient_host=host,lfclient_port=port)
        self.host=host
        self.port=port
        self.resource=resource
        self.clean_phantom_port=clean_phantom_port
        self.lf_query_ports = super().json_get("/port/all")
        self.lf_query_cx = super().json_get("/cx/all")
        self.lf_query_endps=super().json_get("/endp")
        self.lf_query_resource=super().json_get("/resource/all")
        self.lf_query_layer4=super().json_get("/layer4/all")


    def clean_phantom_cx(self):
        print("\n Ok...now validating Layer-3 CX \n")
        lf_query_cx = super().json_get("/cx/all")
        lf_query_endps=super().json_get("/endp")
        print(list(lf_query_cx)[2])
        if 'empty' in list(lf_query_cx)[2]:
            print('cx connects do not exist')
        else:
            print('cx connects exist')
            for j in range(len(list(lf_query_cx))):
                for i in [lf_query_cx]:
                    if 'handler'!=list(i)[j] and 'uri' != list(i)[j]:
                        cx_name=list(i)[j]  
                        temp=i.get(list(i)[j])
                        print(cx_name+' is in PHANTOM state:-','PHANTOM' in temp.get('state'))

                        if 'PHANTOM' in temp.get('state'):
                            req_url = "cli-json/rm_cx"
                            data = {
                                "test_mgr": "default_tm",
                                "cx_name": cx_name
                            }
                            print('Cleaning ',cx_name,' cross connect')
                            logger.info("Removing {cx_name}...".format(cx_name=cx_name))
                            super().json_post(req_url, data)
                            #time.sleep(1)
                            #clearing associated endps
                            endp=lf_query_endps["endpoint"]
                            for id in range(len(endp)):
                                endp=lf_query_endps["endpoint"][id]
                                if [cx_name+'-A']==list(endp) or [cx_name+'-B']==list(endp):
                                    req_url = "cli-json/rm_endp"
                                    data = {
                                    "endp_name": list(endp)[0]
                                    }
                                    logger.info(data)
                                    logger.info("Removing {endp_name}...".format(endp_name=list(endp)[0]))
                                    super().json_post(req_url, data)
                                    print('Delete ',list(endp)[0])
                        
                        
        
    def clean_phantom_ports(self):
        print("\n Now validating Port manager ports \n")
        #print('helo your IP='+self.host)
        temp=-1
        for i in [self.lf_query_ports['interfaces']]:
            for j in i:
                temp+=1
                for k in j:
                    print("The "+k+' is in phantom: ',i[temp][k]["phantom"])    
                if i[temp][k]["phantom"] is True:
                    info=self.name_to_eid(k)
                    req_url = "cli-json/rm_vlan"
                    data = {
                        "shelf": info[0],
                        "resource": info[1],
                        "port": info[2]
                    }
                    logger.info("Removing {alias}...".format(alias=k))
                    super().json_post(req_url, data)
                    #time.sleep(1)

    def clean_phantom_resources(self):
        print("\n Now validating Resource manager ports \n")
        if 'resources' in list(self.lf_query_resource):
            #print(list(self.lf_query_resource['resources']))
            for i in range(len(list(self.lf_query_resource['resources']))):
                id=(list(list(self.lf_query_resource['resources'])[i])[0])
                resource=list(self.lf_query_resource['resources'])[i].get(id)["phantom"]
                print('The',id,'port is in PHANTOM:-',resource)
                while resource:
                    print('Deleting the resource',id)
                    info=id.split('.')
                    req_url = "cli-json/rm_resource"
                    data = {
                        "shelf": int(info[0]),
                        "resource": int(info[1])
                    }
                    super().json_post(req_url, data)
                    break
                
        else:
            print("No phantom resources")
        #time.sleep(1)

    # def clean_phantom_l4(self):
        

    def clean_phantom_l4(self):
        print("\nNow analysing layer 4-7 tab..!\n")
        still_looking_endp = True
        iterations_endp = 0

        while still_looking_endp and iterations_endp <= 10:
            iterations_endp += 1
            logger.info("layer4_endp_clean: iterations_endp: {iterations_endp}".format(iterations_endp=iterations_endp))
            layer4_endp_json = super().json_get("layer4")
            logger.info(layer4_endp_json)
            if layer4_endp_json is not None:
                logger.info("Removing old Layer 4-7 endpoints")
                for name in list(layer4_endp_json):
                    # if name != 'handler' and name != 'uri' and name != 'empty':
                    if name == 'endpoint':
                        for i in range(len(list(self.lf_query_layer4['endpoint']))):
                            endp_name=list(self.lf_query_layer4['endpoint'][i])[0]
                            while self.lf_query_layer4['endpoint'][i][endp_name]['status']:                                
                                #Remove Layer 4-7 cross connections:
                                req_url = "cli-json/rm_cx"
                                data = {
                                    "test_mgr": "default_tm",
                                    "cx_name": "CX_" + endp_name
                                }
                                logger.info("Removing {endp_name}...".format(endp_name="CX_" + endp_name))
                                super().json_post(req_url, data)

                                # Remove Layer 4-7 endpoint
                                req_url = "cli-json/rm_endp"
                                data = {
                                    "endp_name": endp_name
                                }
                                logger.info("Removing {endp_name}...".format(endp_name=endp_name))
                                super().json_post(req_url, data)
                                break
                time.sleep(1)
            else:
                logger.info("No endpoints found to cleanup")
                print("No endpoints found to cleanup")
                still_looking_endp = False
                logger.info("clean_endp still_looking_endp {ednp_looking}".format(ednp_looking=still_looking_endp))
            if not still_looking_endp:
                self.endp_done = True
            return still_looking_endp

        
def main():
    parser = argparse.ArgumentParser(
        prog='lf_clean_phantom.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Clean Phantom hosts and connects
            ''',
        description='''\
lf_clean_phantom.py:
--------------------
Generic command layout:

Example:
This example will clean the Phantom ports and resources from LF GUI tabs:
./lf_clean_phantom.py --mgr MGR --phantom_____

    default port is 8080

    NOTE: will only cleanup what is present in the GUI
            So will need to iterate multiple times with script
            ''')
    parser.add_argument(
        '--mgr',
        '--lfmgr',
        help='--mgr <hostname for where LANforge GUI is running>',
        default='localhost')
    
    parser.add_argument(
        "--phantom_port",
        help="to delete phantom ports from port mgr",
        action="store_true")
    parser.add_argument(
        "--phantom_cx",
        help="to delete phantom cx connects",
        action="store_true")
    parser.add_argument(
        "--phantom_resource",
        help="to delete phantom resources",
        action="store_true")
    parser.add_argument(
        "--phantom_l4",
        help="to delete phantom cx connects layer4-7 tab",
        action="store_true")
    parser.add_argument(
        "--sanitize_phantom",
        help="to delete phantoms from layer3 tab, layer4-7 tab, resources all in one shot",
        action="store_true")


    args = parser.parse_args()
    x=clean_phantom(host=args.mgr,port=8080,resource=None,clean_phantom_port=None)
    if args.phantom_port:
      x.clean_phantom_ports()
      time.sleep(4)
    if args.phantom_cx:
      x.clean_phantom_cx()
      time.sleep(1)
    if args.phantom_resource:
      x.clean_phantom_resources()
    if args.phantom_l4:
      x.clean_phantom_l4()
    if args.sanitize_phantom:
        x.clean_phantom_cx()
        x.clean_phantom_resources()
        x.clean_phantom_l4()

      

  
# if __name__ == "__main__":
main()



