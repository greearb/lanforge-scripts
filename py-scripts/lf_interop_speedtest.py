
import sys
import os
import csv
import time
import shutil
import importlib
import logging
from click import Path
import paramiko
import argparse
import pandas as pd
from datetime import datetime
import threading
from typing import Dict

# Flask is optional; only import when used
try:
    from tabulate import tabulate
except:
    pass


logger = logging.getLogger(__name__)

if sys.version_info[0] != 3:
    print("This script requires Python3")
    exit()

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
from lf_report import lf_report
from lf_graph import lf_bar_graph

interop_connectivity = importlib.import_module("py-json.interop_connectivity")


class SpeedTest(Realm):
    def __init__(self,
                manager_ip=None,
                port=8080,
                device_list=None,
                instance="Speed_Test_Report",
                iteration=1,
                do_interopability=False,
                dowebgui=False,
                type='ookla',
                result_dir='local',
                _debug_on=False):
        super().__init__(lfclient_host=manager_ip,
                        debug_=_debug_on)
        self.manager_ip = manager_ip
        self.manager_port = port
        self.device_list = device_list
        self.instance = instance
        self.iteration = iteration
        self.do_interopability = do_interopability
        self.dowebgui = dowebgui
        self.result_dir = result_dir
        self.type=type
        self.devices_data = {}
        self.android_data = {}
        self.laptop_data = {}
        self.generic_endps_profile = self.new_generic_endp_profile()
        self.generic_endps_profile.type = 'generic'
        self.generic_endps_profile.cmd = ' '
        self.result_json = {}
        self.stop_time = None
        self.start_time = None
        self.device_info = {}

        self._ingest_lock = threading.Lock()
        self._flask_thread = None
        self._post_url = None

        if self.dowebgui:
            print('Initiating Server for WebGUI Ingest')
            self.change_port_to_ip()
            self._post_url = f"http://{self.manager_ip}:5050/api/speedtest"
            self._start_ingest_server() 
        #reporting variable
        self.selected_device_type = set()
        self.selected_resources = None
        self.ip_hostname = {}
        self.result_dict = {
                            'ip':[],
                            'hostname':[],
                            'download_speed':[],
                            'upload_speed':[],
                            'download_lat':[],
                            'upload_lat':[]
                        }
        self.iteration_dict = {}


    def change_port_to_ip(self):
            if self.manager_ip.count('.') != 3:
                target_port_list = self.name_to_eid(self.manager_ip)
                shelf, resource, port, _ = target_port_list
                try:
                    target_port_ip = self.json_get(f'/port/{shelf}/{resource}/{port}?fields=ip')['interface']['ip']
                    self.manager_ip = target_port_ip
                except BaseException:
                    logging.warning(f'The Server port is not an ethernet port. Proceeding with the given {self.manager_ip}.')
                logging.info(f"Server port IP {self.manager_ip}")
            else:
                logging.info(f"Server port IP {self.manager_ip}")

            self.manager_ip = self.manager_ip

    def _start_ingest_server(self):
        try:
            from flask import Flask, request, jsonify
        except Exception:
            print("[WARN] Flask not installed; --dowebgui ingest disabled.")
            return

        app = Flask(__name__)
        parent = self

        @app.get("/api/health")
        def health():
            return jsonify({"ok": True, "ts": time.time()}), 200

        @app.route("/api/speedtest", methods=["POST"])
        def _ingest():
            try:
                payload = request.get_json(force=True) or {}
                ip  = (payload.get("ip") or "").strip()
                host = payload.get("hostname")
                key = ip.replace('.', '_') if ip else (payload.get("device_id") or payload.get("serial"))
                rec = {
                    "download":               f"{payload.get('download_mbps','0')} Mbps",
                    "upload":                 f"{payload.get('upload_mbps','0')} Mbps",
                    "Idle Latency":           f"{payload.get('idle_ms','0')} ms",
                    "Download Latency":       f"{payload.get('download_latency_ms','0')} ms",
                    "Upload Latency":         f"{payload.get('upload_latency_ms','0')} ms",
                    "source":                 "ingest"
                }

                print('[POST] got payload for key:', key, rec)
                with parent._ingest_lock:
                    parent.result_json[key] = rec
                    if ip and host:
                        parent.ip_hostname[ip] = host
                print("[INGEST] stored under key:", key)
                return jsonify({"stored": True}), 200
            except Exception as e:
                return jsonify({"stored": False, "error": str(e)}), 400

        @app.get("/api/data")
        def data():
            return jsonify(parent.result_json), 200

        def run():
            # IMPORTANT: bind to all interfaces so other machines clear
            #  POST
            app.run(host=self.manager_ip, port=5050, debug=True, use_reloader=False)

        import threading
        self._flask_thread = threading.Thread(target=run, daemon=True)
        self._flask_thread.start()

    def _ssh_connect(self, host, username, password):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        return ssh

    # def get_device_data(self, resource_data):
    #     # Get ports
    #     resource_id = list(resource_data.keys())
    #     ports = self.json_get('/ports/all')['interfaces']
    #     interop =  self.json_get('/adb/all')['devices']

    #     for port_data_dict in ports:
    #         port_id = list(port_data_dict.keys())[0]
    #         port_id_parts = port_id.split('.')
    #         resource = port_id_parts[0] + '.' + port_id_parts[1]

    #         # Skip any non-real devices we have decided to not track
    #         if resource not in resource_id:
    #             continue

    #         # Need to unpack resource data dict of encapsulating dict that contains it
    #         port_data_dict = port_data_dict[port_id]

    #         try: 
    #             if 'phantom' not in port_data_dict or 'down' not in port_data_dict or 'parent dev' not in port_data_dict:
    #                 logging.error('Malformed json response for endpoint /ports/all')
    #                 raise ValueError('Malformed json response for endpoint /ports/all')

    #             # Skip phantom or down ports
    #             if port_data_dict['phantom'] or port_data_dict['down']:
    #                 continue

    #             # TODO: Support more than one station per real device
    #             # print(port_data_dict['parent dev'])
    #             if port_data_dict['parent dev'] != 'wiphy0':
    #                 continue
    #         except:
    #             pass

    #         if resource in resource_data:
    #             self.devices_data[port_id] = {'device type': None, 'cmd': None, 'ip': None, 'serial': None}
    #             self.devices_data[port_id]['device type'] = resource_data[resource]['device type']
    #             self.devices_data[port_id]['ip'] = resource_data[resource]['ctrl-ip']
    #             self.devices_data[port_id]['hostname'] = resource_data[resource]['hostname']
    #             self.devices_data[port_id]['ssid'] = port_data_dict.get('ssid', None)
    #             self.devices_data[port_id]['channel'] = port_data_dict.get('channel', None)
    #             self.devices_data[port_id]['mac'] = port_data_dict.get('mac', None)

    #             # Reporting purpose
    #             self.ip_hostname[resource_data[resource]['ctrl-ip']] = resource_data[resource]['hostname']

    #     # Only to know serial of an ADB device
    #     for res_id in resource_id:
    #         if resource_data[res_id]['device type'] == 'Android':
    #             for interop_data_dict in interop:
    #                 if interop_data_dict[list(interop_data_dict.keys())[0]]['resource-id'] in list(resource_data.keys()):
    #                     serial = (next((v['name'] for d in interop for k, v in d.items() if v.get('resource-id') == res_id), None))
    #                     temp = f'{serial}' # {res_id}.
    #                     self.devices_data[temp] = {'device type': None, 'serial': None, 'ip': None}
    #                     self.devices_data[temp]['device type'] = resource_data[res_id]['device type']
    #                     self.devices_data[temp]['ip'] = resource_data[res_id]['ctrl-ip']
    #                     self.devices_data[temp]['hostname'] = resource_data[res_id]['user']
    #                     self.devices_data[temp]['serial'] = serial.split(".")[2]
    #                     self.devices_data[temp]['mac'] = resource_data[res_id].get('wifi mac', None) #TODO need to take this from /adb/all which is interop
    #                     self.ip_hostname[resource_data[res_id]['ctrl-ip']] = resource_data[res_id]['user']

    #                     # self.devices_data[res_id]['serial'] += f'.{self.devices_data[res_id]['serial']}'

    #     ip_to_key = {}
    #     final_devices_data = {}

    #     for key, info in self.devices_data.items():
    #         ip = info.get('ip')
    #         if not ip:
    #             continue

    #         if ip not in ip_to_key:
    #             ip_to_key[ip] = key
    #             final_devices_data[key] = info.copy()
    #         else:
    #             existing_key = ip_to_key[ip]

    #             if 'wlan' in key and 'wlan' not in existing_key:
    #                 final_devices_data[key] = final_devices_data.pop(existing_key)
    #                 ip_to_key[ip] = key
    #                 existing_key = key

    #             for k, v in info.items():
    #                 if v is not None:
    #                     final_devices_data[existing_key][k] = v

    #     self.devices_data = final_devices_data

    #     print(self.devices_data)

    # def get_device_data(self, resource_data):
    #     """
    #     get_devices_data:
    #     - /ports/all  ? ssid/channel/mac and the WLAN port key (e.g. '1.11.wlan0')
    #     - selected resource_data ? ctrl-ip, device type, box hostname
    #     - /adb/all    ? Android serial (name), user-name (friendly host), wifi mac
    #     """
    #     resource_ids = set(resource_data.keys())

    #     ports = self.json_get('/ports/all').get('interfaces', [])
    #     adb_devices_list = self.json_get('/adb/all').get('devices', [])

    #     adb_by_resource = {}
    #     for dev_dict in adb_devices_list:
    #         key = next(iter(dev_dict))
    #         info = dev_dict[key]
    #         rid = info.get('resource-id')
    #         if rid:
    #             adb_by_resource[rid] = {
    #                 'name': info.get('name'),
    #                 'serial': (info.get('name') or ''),  
    #                 'shelf_resource': info.get('name').rsplit('.', 1)[0],
    #                 'user_name': info.get('user-name'),
    #                 'wifi_mac': info.get('wifi mac'),
    #                 'device_type': info.get('device-type', 'Android')
    #             }

    #     devices_data = {}

    #     # From /ports/all: capture WLAN ports only, skip phantom/down
    #     for pd in ports:
    #         port_id = next(iter(pd))
    #         pdata = pd[port_id]

    #         # resource id like "1.11" from "1.11.wlan0"
    #         parts = port_id.split('.')
    #         if len(parts) < 3:
    #             continue
    #         resource = '.'.join(parts[:2])

    #         if resource not in resource_ids:
    #             continue

    #         try:
    #             if pdata.get('phantom', True) or pdata.get('down', True):
    #                 continue
    #             # keep only real client radios (adjust if you support more)
    #             if pdata.get('parent dev') != 'wiphy0':
    #                 continue
    #         except Exception:
    #             # best effort: if structure is odd, skip it
    #             continue

    #         res = resource_data[resource]
    #         dev_type = res.get('device type')
    #         ctrl_ip = res.get('ctrl-ip')
    #         box_hostname = res.get('hostname')

    #         if not ctrl_ip:
    #             continue

    #         devices_data[port_id] = {
    #             'device type': dev_type,
    #             'cmd': None,
    #             'ip': ctrl_ip,
    #             'serial': None,
    #             'hostname': box_hostname,
    #             'ssid': pdata.get('ssid'),
    #             'channel': pdata.get('channel'),
    #             'mac': pdata.get('mac')
    #         }

    #         # For reporting lookups
    #         self.ip_hostname[ctrl_ip] = box_hostname

    #     # ---- From /adb/all: add/augment Android rows using serial key 
    #     for rid in resource_ids:
    #         res = resource_data[rid]
    #         if (res.get('device type') or '').lower() != 'android':
    #             continue

    #         ctrl_ip = res.get('ctrl-ip')
    #         adb = adb_by_resource.get(rid)
    #         if not adb:
    #             continue  # no ADB info for this resource
    #         print(adb.get('shelf_resource'), adb.get('serial'), adb.get('user_name'))

    #         serial_key = f"{adb.get('shelf_resource')}.wlan0"
    #         # seed or update a dedicated Android row keyed by serial-key
    #         row = devices_data.get(serial_key, {})
    #         row.update({
    #             'device type': 'Android',
    #             'ip': ctrl_ip,
    #             'port': adb.get('shelf_resource'),
    #             'serial': adb.get('serial').split('.')[-1],
    #             'hostname': adb.get('user_name') or res.get('hostname') or res.get('user'),  # prefer user-name
    #             'ssid': row.get('ssid'),      # keep if we already had from wlan0
    #             'channel': row.get('channel'),
    #             'mac': adb.get('wifi_mac') or row.get('mac')  # prefer adb wifi mac
    #         })
    #         devices_data[serial_key] = row
    #         print(devices_data)

    #         # Prefer the friendlier hostname for reporting
    #         if ctrl_ip and adb.get('user_name'):
    #             self.ip_hostname[ctrl_ip] = adb['user_name']
    #     exit(0)

    #     # ---- Deduplicate by IP: prefer WLAN key as canonical
    #     ip_to_key = {}
    #     final_devices = {}

    #     for key, info in devices_data.items():
    #         ip = info.get('ip')
    #         if not ip:
    #             continue

    #         if ip not in ip_to_key:
    #             ip_to_key[ip] = key
    #             final_devices[key] = info.copy()
    #             continue

    #         # merge into existing canonical
    #         existing_key = ip_to_key[ip]

    #         # If new key looks like a WLAN port and the existing one does not, swap canonical
    #         if ('wlan' in key) and ('wlan' not in existing_key):
    #             # move data over to WLAN key as the canonical
    #             merged = final_devices.pop(existing_key)
    #             ip_to_key[ip] = key
    #             final_devices[key] = merged
    #             existing_key = key  # new canonical

    #         # Merge non-None (and non-empty) fields into canonical
    #         for k, v in info.items():
    #             if v not in (None, ''):
    #                 final_devices[existing_key][k] = v

    #     # Save back
    #     self.devices_data = final_devices

    #     # Debug print (optional)
    #     print(self.devices_data)
    #     exit(0)

    def get_device_data(self, resource_data):
        """
        get_devices_data:
        - /ports/all  ? ssid/channel/mac and the WLAN port key (e.g. '1.11.wlan0')
        - selected resource_data ? ctrl-ip, device type, box hostname
        - /adb/all    ? Android serial (name), user-name (friendly host), wifi mac
        """
        resource_ids = set(resource_data.keys())

        ports = self.json_get('/ports/all').get('interfaces', [])
        adb_devices_list = self.json_get('/adb/all').get('devices', [])

        adb_by_resource = {}
        for dev_dict in adb_devices_list:
            key = next(iter(dev_dict))
            info = dev_dict[key]
            rid = info.get('resource-id')
            if rid:
                adb_by_resource[rid] = {
                    'name': info.get('name'),
                    'serial': (info.get('name') or ''),
                    'shelf_resource': (info.get('name') or '').rsplit('.', 1)[0],
                    'user_name': info.get('user-name'),
                    'wifi_mac': info.get('wifi mac'),
                    'device_type': info.get('device-type', 'Android')
                }

        def merge_preferring_non_empty(dst: dict, src: dict) -> dict:
            for k, v in (src or {}).items():
                if v not in (None, ''):
                    if dst.get(k) in (None, ''):
                        dst[k] = v
            return dst

        devices_data = {}

        # From /ports/all: capture WLAN ports only, skip phantom/down
        for pd in ports:
            port_id = next(iter(pd))
            pdata = pd[port_id]

            parts = port_id.split('.')
            if len(parts) < 3:
                continue
            resource = '.'.join(parts[:2])

            if resource not in resource_ids:
                continue

            try:
                if pdata.get('phantom', True) or pdata.get('down', True):
                    continue
                if pdata.get('parent dev') != 'wiphy0':
                    continue
            except Exception:
                continue

            res = resource_data[resource]
            dev_type = res.get('device type')
            ctrl_ip = res.get('ctrl-ip')
            box_hostname = res.get('hostname')

            if not ctrl_ip:
                continue

            devices_data[port_id] = {
                'device type': dev_type,
                'cmd': None,
                'ip': ctrl_ip,
                'serial': None,
                'hostname': box_hostname,
                'ssid': pdata.get('ssid'),
                'channel': pdata.get('channel'),
                'mac': pdata.get('mac')
            }

            # For reporting lookups
            if ctrl_ip and box_hostname:
                self.ip_hostname[ctrl_ip] = box_hostname

        # ---- From /adb/all: move Android rows to a single row keyed by SERIAL
        for rid in resource_ids:
            res = resource_data[rid]
            if (res.get('device type') or '').lower() != 'android':
                continue

            ctrl_ip = res.get('ctrl-ip')
            adb = adb_by_resource.get(rid)
            if not adb:
                continue

            serial_key = adb.get('serial').split('.')[-1]  # e.g. R9ZW9098RMZ
            port_key = f"{rid}.wlan0"                      # e.g. 1.11.wlan0

            wlan_row = devices_data.pop(port_key, {})  # <? deletes 1.xx.wlan0 if present

            # Start the serial row with sane defaults
            serial_row = {
                'device type': 'Android',
                'cmd': None,
                'ip': ctrl_ip or wlan_row.get('ip'),
                'port': adb.get('shelf_resource'),
                'serial': serial_key,
                'hostname': adb.get('user_name') or res.get('hostname') or wlan_row.get('hostname') or res.get('user'),
                'ssid': wlan_row.get('ssid'),
                'channel': wlan_row.get('channel'),
                'mac': adb.get('wifi_mac') or wlan_row.get('mac'),
            }

            # If we had already created a serial row, merge non-empty fields into it
            if serial_key in devices_data:
                serial_row = merge_preferring_non_empty(devices_data[serial_key], serial_row)

            devices_data[serial_key] = serial_row

            # Prefer hostname for reporting
            if ctrl_ip and adb.get('user_name'):
                self.ip_hostname[ctrl_ip] = adb['user_name']

        self.devices_data = devices_data
        print(self.devices_data)

    def filter_devices(self, resources_list):
        resource_data = {}
        for resource_data_dict in resources_list:
            resource_id = list(resource_data_dict.keys())[0]
            resource_data_dict = resource_data_dict[resource_id]
            devices = ['Linux/Interop', 'Windows', 'Mac OS', 'Android']
            if resource_data_dict['device type'] in devices:
                resource_data[resource_id] = resource_data_dict
        return resource_data

    def get_resource_data(self):

        resources_list = self.json_get("/resource/all")["resources"]
        resource_data = self.filter_devices(resources_list)

        headers = ["Index", "Resource ID", "Hostname", "IP", "Device Type"]
        rows = []
        resource_keys = list(resource_data.keys())

        for i, res_id in enumerate(resource_keys):
            res = resource_data[res_id]
            self.device_info[res.get("ctrl-ip", "N/A")] = res.get("device type", "N/A")
            rows.append([
                i,
                res_id,
                res.get("hostname", "N/A"),
                res.get("ctrl-ip", "N/A"),
                res.get("device type", "N/A"),
            ])

        if self.device_list:
            selected_ids = [x.strip() for x in self.device_list.split(',') if x.strip()]
        else:
            print("\n Available Devices:")
            try:
                print(tabulate(rows, headers=headers, tablefmt="fancy_grid"), disable_numparse=True)
            except:
                # Print table without using tabulate
                print("\t".join(headers))
                for row in rows:
                    print("\t".join(str(item) for item in row))

            selection = input("\n> Enter ports of devices to run speedtest on (comma-separated): ")
            selected_ids = [str(i.strip()) for i in selection.split(',')]

        print(resource_data)
        self.selected_resources = {res_id: resource_data[res_id] for res_id in selected_ids}
        print(f"\n Selected Devices:\n{self.selected_resources}")
        self.get_device_data(self.selected_resources)

        if self.devices_data:

            for device in self.devices_data:
                dev_type = self.devices_data[device]['device type']
                
                # For regular devices (Linux, Windows, Mac)
                if dev_type == 'Linux/Interop':
                    self.devices_data[device]['cmd'] = f"DISPLAY=:1 ./vrf_exec.bash {device.split('.')[2]} python3 ookla.py --type {self.type}{' --post_url ' + self._post_url if self.dowebgui and self._post_url else ''} --ip {self.devices_data[device]['ip']}"
                elif dev_type == 'Windows':
                    self.devices_data[device]['cmd'] = f"py ookla.py --type {self.type}{' --post_url ' + self._post_url if self.dowebgui and self._post_url else ''} --ip {self.devices_data[device]['ip']}"
                elif dev_type == 'Mac OS':
                    self.devices_data[device]['cmd'] = f"python3 ookla.py --type {self.type}{' --post_url ' + self._post_url if self.dowebgui and self._post_url else ''} --ip {self.devices_data[device]['ip']}"
                
                # For ADB devices (override previous command if serial exists)
                if self.devices_data[device].get("serial"):
                    self.devices_data[device]['cmd'] = f"python3 ookla.py --type adb --adb_devices {self.devices_data[device]['serial']}{' --post_url ' + self._post_url if self.dowebgui and self._post_url else ''} --ip {self.devices_data[device]['ip']}"
                
                # REMOVE THIS DUPLICATE SECTION:
                # if self.dowebgui and self._post_url:
                #     self.devices_data[device]['cmd'] += f' --post_url {self._post_url}'
        else:
            print(" No compatible devices found.")

        print("\n Final Device Commands for Speedtest")
        self.android_data = { #.split('.', 2)[-1]
            k: v
            for k, v in self.devices_data.items()
            if v.get('device type', '').lower() == 'android'
        }

        self.laptop_data = {
            k: v
            for k, v in self.devices_data.items()
            if v.get('device type', '').lower() != 'android'
        }

        print('android_data :=', self.android_data)
        print('laptop_data :=', self.laptop_data)

        if self.laptop_data:
            for device in self.laptop_data:
                print(f"{device}   ?  {self.laptop_data[device]['ip']} ({self.laptop_data[device]['device type']}): {self.laptop_data[device]['cmd']}")
        if self.android_data:
            for android in self.android_data:
                print(f"{android}   ?  {self.android_data[android]['ip']} ({self.android_data[android]['device type']}): {self.android_data[android]['cmd']}")

    def start_generic(self):
        self.generic_endps_profile.start_cx()
        self.start_time = datetime.now()

    def stop_generic(self):
        self.generic_endps_profile.stop_cx()
        self.stop_time = datetime.now()

    def get_results(self):
        logging.debug(self.generic_endps_profile.created_endp)
        results = self.json_get(
            "/generic/{}".format(','.join(self.generic_endps_profile.created_endp)))
        if (len(self.generic_endps_profile.created_endp) > 1):
            results = results['endpoints']
        else:
            results = results['endpoint']
        return (results)

    def create_cx_do_interop(self, csv_file):
        for iter in range(1, self.iteration + 1):
            print(f"\n Starting Interop Iteration {iter} of {self.iteration}")
            for cx_name in self.generic_endps_profile.created_cx:
                self.start_specific([cx_name])
                time.sleep(60)
                self.stop_specific([cx_name])

                for device in self.devices_data:
                    os_type = self.devices_data[device]['device type']
                    remote_path = self.get_remote_file_path_by_os(os_type)
                    result = self.fetch_remote_speedtest_file(
                        ip=self.devices_data[device]['ip'],
                        username="lanforge" if os_type.lower() != 'windows' else "Administrator",
                        password="lanforge",
                        remote_path=remote_path
                    )
                    print(result)

                self.write_results_to_csv(iter, csv_file)
                self.result_json = {}

    # def create_cx_incremental(self, increment_values):
    #     for values in increment_values:
    #         for cx_name in self.generic_endps_profile.created_cx:
    #             self.start_specific()
    #             time.sleep(60)
    #             self.stop_specific()

    def start_specific(self, cx_list):
        logging.info("Test started at : {0} ".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        if len(cx_list) > 0:
            for cx in cx_list:
                req_url = "cli-json/set_cx_report_timer"
                data = {
                    "test_mgr": "all",
                    "cx_name": cx,
                    "milliseconds": 1000
                }
                self.json_post(req_url, data)
        for cx_name in cx_list:
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
                "cx_state": "RUNNING"
            }, debug_=True)

    def stop_specific(self, cx_list):
        logging.info("Stopping specific CXs...")
        for cx_name in cx_list:
            if self.debug:
                logging.debug("cx-name: {cx_name}".format(cx_name=cx_name))
            self.json_post("/cli-json/set_cx_state", {
                "test_mgr": "default_tm",
                "cx_name": cx_name,
                "cx_state": "STOPPED"
            }, debug_=self.debug)

    def create(self):
        device_types = [device['device type'] for device in self.laptop_data.values()]

        if self.laptop_data:
            self.generic_endps_profile.create(ports=list(self.laptop_data.keys()), real_client_os_types=device_types)
            
        for endp_name in self.generic_endps_profile.created_endp:
            self.generic_endps_profile.set_cmd(endp_name, cmd=self.laptop_data[endp_name.split('-')[1]]['cmd'])

        if self.android_data:
            self.android_data = {
                f"{v['port']}.{k}": v
                for k, v in self.android_data.items()
            }
            status, created_cx, created_endp = self.create_android(ports=list(self.android_data.keys()), real_client_os_types=device_types)
            self.generic_endps_profile.created_endp.extend(created_endp)
            self.generic_endps_profile.created_cx.extend(created_cx)

            for endp_name in created_endp:
                self.generic_endps_profile.set_cmd(endp_name, cmd=self.android_data[(endp_name.split('-')[1]).replace('_', '.')]['cmd'])
        
        print(self.generic_endps_profile.created_endp)
        print(self.generic_endps_profile.created_cx)


    def create_android(self, ports=None, sleep_time=.5, debug_=False, suppress_related_commands_=None, real_client_os_types=None):
        if ports and real_client_os_types and len(real_client_os_types) == 0:
            logging.error('Real client operating systems types is empty list')
            raise ValueError('Real client operating systems types is empty list')
        created_cx = []
        created_endp = []

        if not ports:
            ports = []

        if self.debug:
            debug_ = True

        post_data = []
        endp_tpls = []
        for port_name in ports:
            port_info = self.name_to_eid(port_name)
            resource = port_info[1]
            shelf = port_info[0]
            if real_client_os_types:
                name = port_name
            else:
                name = port_info[2]

            gen_name_a = "%s-%s" % ('generic', '_'.join(port_name.split('.')))
            endp_tpls.append((shelf, resource, name, gen_name_a))

        print('endp_tpls', endp_tpls)
        for endp_tpl in endp_tpls:
            shelf = endp_tpl[0]
            resource = endp_tpl[1]
            if real_client_os_types:
                name = endp_tpl[2].split('.')[2]
            else:
                name = endp_tpl[2]
            gen_name_a = endp_tpl[3]

            data = {
                "alias": gen_name_a,
                "shelf": shelf,
                "resource": resource,
                "port": 'eth0',
                "type": "gen_generic"
            }
            # print('Adding endpoint ', data)
            self.json_post("cli-json/add_gen_endp", data, debug_=self.debug)

        self.json_post("/cli-json/nc_show_endpoints", {"endpoint": "all"})
        if sleep_time:
            time.sleep(sleep_time)

        for endp_tpl in endp_tpls:
            gen_name_a = endp_tpl[3]
            self.generic_endps_profile.set_flags(gen_name_a, "ClearPortOnStart", 1)

        for endp_tpl in endp_tpls:
            name = endp_tpl[2]
            gen_name_a = endp_tpl[3]
            cx_name = "CX_%s-%s" % ("generic", gen_name_a)
            data = {
                "alias": cx_name,
                "test_mgr": "default_tm",
                "tx_endp": gen_name_a
            }
            post_data.append(data)
            created_cx.append(cx_name)
            created_endp.append(gen_name_a)

        for data in post_data:
            url = "/cli-json/add_cx"
            # print('Adding cx', data)
            self.json_post(url, data, debug_=debug_, suppress_related_commands_=suppress_related_commands_)
            # time.sleep(2)
        if sleep_time:
            time.sleep(sleep_time)

        for data in post_data:
            self.json_post("/cli-json/show_cx", {
                "test_mgr": "default_tm",
                "cross_connect": data["alias"]
            })
        return True, created_cx, created_endp

    def save_results(self):
        results = self.get_results()
        print(results, 'RESULTS')
        for device in self.generic_endps_profile.created_endp:
            if(device in list(results[0].keys())):
                self.result_json[device] = results[0][device]['last results']

    def fetch_remote_speedtest_file(self, ip, username, password, remote_path="/home/lanforge/speedtest.txt"):
        try:
            print(f"Connecting to {ip} to fetch speedtest.txt")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password)

            sftp = ssh.open_sftp()
            local_path = f"./{ip.replace('.', '_')}_speedtest.txt"
            sftp.get(remote_path, local_path)
            sftp.close()
            ssh.close()

            with open(local_path, "r") as f:
                content = f.read()

            # Parse download and upload
            download = upload = idle_latency = down_latency = up_latency = "N/A"
            for line in content.splitlines():
                if "Download speed" in line:
                    download = line.split(":")[1].strip()
                elif "Upload speed" in line:
                    upload = line.split(":")[1].strip()
                elif "Idle Latency" in line:
                    idle_latency = line.split(":")[1].strip()
                elif "Download Latency" in line:
                    down_latency = line.split(":")[1].strip()
                elif "Upload Latency" in line:
                    up_latency = line.split(":")[1].strip()

            # Store in result_json
            self.result_json[ip] = {"upload": upload,
                                    "download": download,
                                    "Idle Latency": idle_latency,
                                    "Download Latency": down_latency,
                                    "Upload Latency": up_latency
                                    }

            print(f"{ip} - Download: {download}, Upload: {upload}, Idle Latency: {idle_latency}, Download Latency: {down_latency}, Upload Latency: {up_latency}")
            return content

        except Exception as e:
            print(f" Failed to fetch file from {ip}: {e}")
            self.result_json[ip] = {"download": "Error", "upload": "Error"}
            return None

    def fetch_android_speedtest_from_lanforge(self, ip, username='lanforge', password='lanforge',
                                            remote_dir="/home/lanforge"):
        """
        Fetches <ip>_speedtest.txt from LANforge to local machine and parses it.
        If the file does not exist, sets all values to 0 for that IP.
        """
        print(ip, 'fetching speedtest file')
        remote_file = f"{remote_dir.rstrip('/')}/{ip}_speedtest.txt"
        local_path = f"./{ip}_speedtest.txt"

        try:
            print(f"Connecting to {self.manager_ip} to fetch {remote_file} and local path {local_path}")
            ssh = self._ssh_connect(self.manager_ip, username, password)
            sftp = ssh.open_sftp()
            sftp.get(remote_file, local_path)
            sftp.close()
            ssh.close()

            with open(local_path, "r") as f:
                content = f.read()

            download = upload = idle_latency = down_latency = up_latency = "N/A"
            for line in content.splitlines():
                if "Download speed" in line:
                    download = line.split(":", 1)[1].strip()
                elif "Upload speed" in line:
                    upload = line.split(":", 1)[1].strip()
                elif "Idle Latency" in line:
                    idle_latency = line.split(":", 1)[1].strip()
                elif "Download Latency" in line:
                    down_latency = line.split(":", 1)[1].strip()
                elif "Upload Latency" in line:
                    up_latency = line.split(":", 1)[1].strip()

            self.result_json[ip] = {
                "download": download,
                "upload": upload,
                "Idle Latency": idle_latency,
                "Download Latency": down_latency,
                "Upload Latency": up_latency,
                "local_file": local_path,
            }
            print(f"{ip} - D:{download} U:{upload} Idle:{idle_latency} DLat:{down_latency} ULat:{up_latency}")
            return self.result_json[ip]
        except Exception as e:
            print(f"Failed to fetch or parse Android speedtest result for {ip}: {e}")
            self.result_json[ip] = {
                "download": "0",
                "upload": "0",
                "Idle Latency": "0",
                "Download Latency": "0",
                "Upload Latency": "0",
                "local_file": None,
            }

            return self.result_json[ip]

    # def write_results_to_csv(self, current_iter, csv_file):
    #     csv_exists = os.path.isfile(csv_file)

    #     csv_data = []
    #     table_data = []

    #     for ip, data in self.result_json.items():
    #         ip = ip.replace('_', '.')
    #         download = data.get("download", "N/A")
    #         upload = data.get("upload", "N/A")
    #         idle_latency = data.get("Idle Latency", "N/A")
    #         down_latency = data.get("Download Latency", "N/A")
    #         up_latency = data.get("Upload Latency", "N/A")
    #         csv_data.append([current_iter, self.iteration, ip, self.device_info[ip],
    #                         download, upload, idle_latency, down_latency, up_latency])
    #         table_data.append([current_iter, self.iteration, ip, self.device_info[ip],
    #                             download, upload, idle_latency, down_latency, up_latency])

    #         print('--------------------------')
    #         print(table_data)
    #         print(csv_data)
    #         print(self.ip_hostname)
    #         print('--------------------------')

    #         self.result_dict['ip'].append(ip)
    #         self.result_dict['hostname'].append(self.ip_hostname[ip])
    #         try:
    #             self.result_dict['download_speed'].append(float(download.split(' ')[0]))
    #         except Exception:
    #             self.result_dict['download_speed'].append(0.0)
    #         try:
    #             self.result_dict['upload_speed'].append(float(upload.split(' ')[0]))
    #         except Exception:
    #             self.result_dict['upload_speed'].append(0.0)
    #         try:
    #             self.result_dict['download_lat'].append(float(down_latency.split(' ')[0]))
    #         except Exception:
    #             self.result_dict['download_lat'].append(0.0)
    #         try:
    #             self.result_dict['upload_lat'].append(float(up_latency.split(' ')[0]))
    #         except Exception:
    #             self.result_dict['upload_lat'].append(0.0)

    #     self.iteration_dict[current_iter] = self.result_dict
    #     self.result_dict = {
    #                         'ip':[],
    #                         'hostname':[],
    #                         'download_speed':[],
    #                         'upload_speed':[],
    #                         'download_lat':[],
    #                         'upload_lat':[]
    #                     }
                        

    #     with open(csv_file, "a", newline="") as csvfile:
    #         writer = csv.writer(csvfile)
    #         # Write header only once
    #         if not csv_exists:
    #             writer.writerow(["Iteration", "Total Iterations", "IP", "Device Type",
    #                             "Download", "Upload", "Idle Latency", "Download Latency", "Upload Latency"])
    #         writer.writerows(csv_data)

    #     print("\n Speedtest Results for Iteration", current_iter)
    #     try:
    #         print(tabulate(
    #             table_data,
    #             headers=["Iteration", "Total Iterations", "IP", "Device Type",
    #                     "Download", "Upload", "Idle Latency", "Download Latency", "Upload Latency"],
    #             tablefmt="fancy_grid",
    #             disable_numparse=True
    #         ))
    #     except:
    #         headers = ["Iteration", "Total Iterations", "IP", "Device Type",
    #                     "Download", "Upload", "Idle Latency", "Download Latency", "Upload Latency"]
    #         print("\t".join(headers))
    #         for row in table_data:
    #             print("\t".join(str(item) for item in row))
    #     print("==============================================================================================================================================")
    #     print(self.iteration_dict)

    
    def write_results_to_csv(self, current_iter, csv_file,  per_iter_wait_seconds=120):

        # expected_ips = list(self.ip_hostname.keys()) or list(self.device_info.keys())
        # end = time.time() + per_iter_wait_seconds
        # while time.time() < end:
        #     got = 0
        #     for ip in expected_ips:
        #         k = ip.replace('.', '_')
        #         if (k in self.result_json) or (ip in self.result_json):
        #             got += 1
        #     if got >= len(expected_ips): break
        #     time.sleep(2)


        csv_exists = os.path.isfile(csv_file)

        csv_data   = []
        table_data = []

        # 1) Normalize keys we received this iteration
        received = {}
        for raw_ip, data in self.result_json.items():
            ip = raw_ip.replace('_', '.')
            received[ip] = {
                "download":          data.get("download", "N/A"),
                "upload":            data.get("upload", "N/A"),
                "Idle Latency":      data.get("Idle Latency", "N/A"),
                "Download Latency":  data.get("Download Latency", "N/A"),
                "Upload Latency":    data.get("Upload Latency", "N/A"),
            }

        # 2) Figure out expected devices (from what you selected earlier)
        # Prefer the IPs you learned during device discovery; fall back to device_info keys.
        expected_ips = list(self.ip_hostname.keys()) or list(self.device_info.keys())

        # 3) Emit rows for devices that DID report
        for ip, data in received.items():
            dev_type      = self.device_info.get(ip, "N/A")
            hostname_safe = self.ip_hostname.get(ip, ip)

            download      = data["download"]
            upload        = data["upload"]
            idle_latency  = data["Idle Latency"]
            down_latency  = data["Download Latency"]
            up_latency    = data["Upload Latency"]

            csv_data.append([current_iter, self.iteration, ip, dev_type,
                            download, upload, idle_latency, down_latency, up_latency])
            table_data.append([current_iter, self.iteration, ip, dev_type,
                            download, upload, idle_latency, down_latency, up_latency])

            # Accumulate into per-iter dicts for graphs/tables
            self.result_dict['ip'].append(ip)
            self.result_dict['hostname'].append(hostname_safe)

            def _num(x):
                try:
                    # Handles values like "24.2 Mbps" or "114 ms" or "N/A"
                    return float(str(x).split()[0])
                except Exception:
                    return 0.0

            self.result_dict['download_speed'].append(_num(download))
            self.result_dict['upload_speed'].append(_num(upload))
            self.result_dict['download_lat'].append(_num(down_latency))
            self.result_dict['upload_lat'].append(_num(up_latency))

        # 4) Emit rows for devices that did NOT report in this iteration (N/A)
        missing_ips = [ip for ip in expected_ips if ip not in received]
        for ip in missing_ips:
            dev_type      = self.device_info.get(ip, "N/A")
            hostname_safe = self.ip_hostname.get(ip, ip)

            csv_data.append([current_iter, self.iteration, ip, dev_type,
                            "N/A", "N/A", "N/A", "N/A", "N/A"])
            table_data.append([current_iter, self.iteration, ip, dev_type,
                            "N/A", "N/A", "N/A", "N/A", "N/A"])

            # For graphs: use zeros so categories & lengths stay aligned
            self.result_dict['ip'].append(ip)
            self.result_dict['hostname'].append(hostname_safe)
            self.result_dict['download_speed'].append(0.0)
            self.result_dict['upload_speed'].append(0.0)
            self.result_dict['download_lat'].append(0.0)
            self.result_dict['upload_lat'].append(0.0)

        # 5) Freeze per-iteration snapshot, then reset the accumulator for the next iter
        self.iteration_dict[current_iter] = self.result_dict
        self.result_dict = {
            'ip': [],
            'hostname': [],
            'download_speed': [],
            'upload_speed': [],
            'download_lat': [],
            'upload_lat': []
        }

        # 6) Append to CSV
        with open(csv_file, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if not csv_exists:
                writer.writerow([
                    "Iteration", "Total Iterations", "IP", "Device Type",
                    "Download", "Upload", "Idle Latency", "Download Latency", "Upload Latency"
                ])
            writer.writerows(csv_data)

        # 7) Pretty print table for the console
        print(f"\n Speedtest Results for Iteration {current_iter}")
        try:
            from tabulate import tabulate
            print(tabulate(
                table_data,
                headers=["Iteration", "Total Iterations", "IP", "Device Type",
                        "Download", "Upload", "Idle Latency", "Download Latency", "Upload Latency"],
                tablefmt="fancy_grid",
                disable_numparse=True
            ))
        except Exception:
            headers = ["Iteration", "Total Iterations", "IP", "Device Type",
                    "Download", "Upload", "Idle Latency", "Download Latency", "Upload Latency"]
            print("\t".join(headers))
            for row in table_data:
                print("\t".join(str(item) for item in row))

        if missing_ips:
            print(f"[NOTE] No data received for iteration {current_iter} from: {', '.join(missing_ips)} (filled with N/A)")
        print("=" * 158)
        print(self.iteration_dict)

    def cleanup(self):
        self.generic_endps_profile.cleanup()
        self.generic_endps_profile.created_cx = []
        self.generic_endps_profile.created_endp = []

    @staticmethod
    def get_remote_file_path_by_os(os_type):
        if os_type.lower() == 'windows':
            return r"C:\Program Files (x86)\LANforge-Server\speedtest.txt"
        elif os_type.lower() == 'mac os':
            return "/Users/lanforge/speedtest.txt"
        else:
            return "/home/lanforge/speedtest.txt"


    # def generate_report(self, result_dir_name):
    #     import pandas as pd
    #     import shutil
    #     import time

    #     print('===============================')
    #     print('Devices DATA:', self.devices_data)
    #     print('===============================')

    #     # ---- helper: which devices are expected to POST? ----
    #     def expected_post_ips():
    #         want = []
    #         for k, v in (self.devices_data or {}).items():
    #             cmd = (v.get('cmd') or '')
    #             ip  = (v.get('ip')  or '')
    #             # If this endpoint is launched with --post_url, we expect a POST for this IP.
    #             if ip and '--post_url' in cmd:
    #                 want.append(ip)
    #         # de-dup and keep order
    #         seen, ans = set(), []
    #         for ip in want:
    #             if ip not in seen:
    #                 seen.add(ip)
    #                 ans.append(ip)
    #         return ans

    #     # ---- helper: wait until all expected posts land (or timeout) ----
    #     def wait_for_posts(expected_ips, timeout_sec=90, poll_sec=1, iter_idx=None):
    #         deadline = time.time() + timeout_sec
    #         # We store by key like '192_168_204_54' or occasionally by serial; normalize both.
    #         def has_post_for(ip):
    #             k = ip.replace('.', '_')
    #             return (k in self.result_json) or (ip in self.result_json)

    #         while time.time() < deadline:
    #             got = [ip for ip in expected_ips if has_post_for(ip)]
    #             if len(got) >= len(expected_ips):
    #                 print(f"[INGEST] iteration {iter_idx}: received {len(got)}/{len(expected_ips)} posts.")
    #                 return True, []
    #             time.sleep(poll_sec)
    #         missing = [ip for ip in expected_ips if not has_post_for(ip)]
    #         print(f"[WARN] iteration {iter_idx}: timed out waiting for posts. "
    #             f"Got {len(expected_ips) - len(missing)}/{len(expected_ips)}. Missing: {missing}")
    #         return False, missing

    #     # if you?re running WebGUI mode, enforce n*m posts across n loops (m per loop)
    #     POST_TIMEOUT_SECS   = 120
    #     POLL_INTERVAL_SECS  = 1
    #     will_wait_for_posts = bool(self.dowebgui)
    #     expected_ips_once   = expected_post_ips()
    #     expected_m          = len(expected_ips_once)
    #     if will_wait_for_posts:
    #         print(f"[INGEST] expecting {expected_m} POST(s) per iteration from: {expected_ips_once}")

    #     if not self.do_interopability:
    #         report = lf_report(
    #             _output_pdf="speedtest.pdf",
    #             _output_html="speedtest.html",
    #             _results_dir_name=result_dir_name,
    #             _path=self.result_dir if self.dowebgui else "/home/lanforge/html-reports"
    #         )

    #         report_path = report.get_path()
    #         report_path_date_time = report.get_path_date_time()

    #         os.makedirs(report_path_date_time, exist_ok=True)
    #         if os.path.exists('speedtest_results.csv'):
    #             try:
    #                 shutil.move('speedtest_results.csv', report_path_date_time)
    #             except Exception as e:
    #                 print(f"[WARN] could not move CSV: {e}")

    #         logger.info("path: {}".format(report_path))
    #         logger.info("path_date_time: {}".format(report_path_date_time))

    #         report.set_title("Speed Test")
    #         report.build_banner()

    #         report.set_obj_html(
    #             _obj_title="Objective",
    #             _obj=("The Candela Speed Test evaluates AP performance under real-world conditions "
    #                 "by measuring latency, download speed, and upload speed to reflect end-user experience.")
    #         )
    #         report.build_objective()

    #         report.set_obj_html(_obj_title="Input Parameters",
    #                             _obj="The tables below provide the input parameters for the test.")
    #         report.build_objective()

    #         # Device counts
    #         android_devices = windows_devices = linux_devices = mac_devices = 0
    #         for i in self.devices_data:
    #             self.selected_device_type.add(self.devices_data[i]['device type'])
    #             dev_type = self.devices_data[i]['device type']
    #             if dev_type == 'Android':
    #                 android_devices += 1
    #             elif dev_type == 'Windows':
    #                 windows_devices += 1
    #             elif dev_type == 'Mac OS' or dev_type == 'Mac':
    #                 mac_devices += 1
    #             elif dev_type == 'Linux/Interop':
    #                 linux_devices += 1

    #         total_devices = ""
    #         if android_devices > 0: total_devices += f" Android({android_devices})"
    #         if windows_devices > 0: total_devices += f" Windows({windows_devices})"
    #         if linux_devices > 0:   total_devices += f" Linux({linux_devices})"
    #         if mac_devices > 0:     total_devices += f" Mac({mac_devices})"

    #         input_params = {
    #             "Test name": "Speed Test",
    #             "Number of Iterations": self.iteration,
    #             "Number of Selected Devices": f"{len(self.selected_resources)} {total_devices}"
    #         }
    #         report.test_setup_table(test_setup_data=input_params, value="Test Configuration")

    #         print('Iteration DATA:', self.iteration_dict)

    #         # --- For each iteration, (optionally) enforce ingest barrier, then graph & table ---
    #         for iter_idx in sorted(self.iteration_dict.keys()):
    #             # If ingest mode, wait for m posts for this iteration
    #             if will_wait_for_posts and expected_m:
    #                 ok, missing = wait_for_posts(
    #                     expected_ips_once,
    #                     timeout_sec=POST_TIMEOUT_SECS,
    #                     poll_sec=POLL_INTERVAL_SECS,
    #                     iter_idx=iter_idx
    #                 )
    #                 # Continue even if some are missing; we?ll still render what we have

    #             # Graphs
    #             hostnames = self.iteration_dict[iter_idx].get('hostname', [])
    #             dl_list   = self.iteration_dict[iter_idx].get('download_speed', [])
    #             ul_list   = self.iteration_dict[iter_idx].get('upload_speed', [])
    #             dlat_list = self.iteration_dict[iter_idx].get('download_lat', [])
    #             ulat_list = self.iteration_dict[iter_idx].get('upload_lat', [])

    #             # Guard: if no data, skip iteration block cleanly
    #             if not hostnames:
    #                 print(f"[WARN] iteration {iter_idx}: no hostnames; skipping graphs/tables.")
    #                 continue

    #             # Per-client speed
    #             report.set_table_title('Per-Client Speed (Download & Upload)')
    #             report.build_table_title()
    #             graph = lf_bar_graph(
    #                 _data_set=[dl_list, ul_list],
    #                 _xaxis_name="Device Name",
    #                 _yaxis_name="Speed (in Mbps)",
    #                 _xaxis_categories=hostnames,
    #                 _graph_image_name=f"Download_upload_speed_iter_{iter_idx}",
    #                 _label=["Download", "Upload"],
    #                 _color=None,
    #                 _color_edge='red',
    #                 _show_bar_value=True,
    #                 _text_font=7,
    #                 _text_rotation=None,
    #                 _enable_csv=True
    #             )
    #             report.set_graph_image(graph.build_bar_graph())
    #             report.move_graph_image()
    #             report.build_graph()

    #             # Per-client latency
    #             report.set_table_title('Per-Client Latency (Download & Upload)')
    #             report.build_table_title()
    #             graph2 = lf_bar_graph(
    #                 _data_set=[dlat_list, ulat_list],
    #                 _xaxis_name="Device Name",
    #                 _yaxis_name="Latency (in ms)",
    #                 _xaxis_categories=hostnames,
    #                 _graph_image_name=f"Download_upload_Latency_iter_{iter_idx}",
    #                 _label=["Download", "Upload"],
    #                 _color=None,
    #                 _color_edge='red',
    #                 _show_bar_value=True,
    #                 _text_font=7,
    #                 _text_rotation=None,
    #                 _enable_csv=True
    #             )
    #             report.set_graph_image(graph2.build_bar_graph())
    #             report.move_graph_image()
    #             report.build_graph()

    #             # ---------- Per-Iteration ?Device Data? table (safe alignment) ----------
    #             # Fast lookups for device metadata
    #             by_key      = self.devices_data
    #             by_hostname = {v.get('hostname'): v for v in self.devices_data.values() if v.get('hostname')}
    #             by_ip       = {v.get('ip'): v for v in self.devices_data.values() if v.get('ip')}

    #             def find_device(host_like=None, ip_like=None):
    #                 return (
    #                     (host_like and by_key.get(host_like)) or
    #                     (host_like and by_hostname.get(host_like)) or
    #                     (ip_like   and by_ip.get(ip_like)) or
    #                     {}
    #                 )

    #             valid_hosts = list(hostnames)
    #             valid_ips   = self.iteration_dict[iter_idx].get('ip', [])
    #             # Row count is the larger of hosts or ips; we?ll pad missing with ''
    #             N = max(len(valid_hosts), len(valid_ips), len(dl_list), len(ul_list), len(dlat_list), len(ulat_list))
    #             def get_or_blank(a, i): return a[i] if i < len(a) else ''

    #             ip_list, mac_list, ssid_list, device_name_list, channel_list = [], [], [], [], []
    #             for i in range(N):
    #                 h = get_or_blank(valid_hosts, i)
    #                 ip = get_or_blank(valid_ips,   i)
    #                 info = find_device(host_like=h, ip_like=ip)

    #                 ip_list.append(ip or info.get('ip', ''))
    #                 mac_list.append(info.get('mac', ''))
    #                 ssid_list.append(info.get('ssid', ''))
    #                 device_name_list.append(info.get('hostname', h or ''))
    #                 channel_list.append(info.get('channel', ''))

    #             # Equalize metric arrays to N so pandas is happy
    #             def pad_to(lst, n, fill=''):
    #                 out = list(lst)
    #                 while len(out) < n: out.append(fill)
    #                 if len(out) > n: out = out[:n]
    #                 return out

    #             dl_list   = pad_to(dl_list,   N, '')
    #             ul_list   = pad_to(ul_list,   N, '')
    #             dlat_list = pad_to(dlat_list, N, '')
    #             ulat_list = pad_to(ulat_list, N, '')

    #             test_input_info = {
    #                 "hostname": device_name_list,
    #                 "MAC": mac_list,
    #                 "SSID": ssid_list,
    #                 "Channel": channel_list,
    #                 "Download Speed (Mbps)": dl_list,
    #                 "Upload Speed (Mbps)": ul_list,
    #                 "Download Latency (ms)": dlat_list,
    #                 "Upload Latency (ms)": ulat_list,
    #             }

    #             report.set_table_title(f'<b>Device Data (Iteration {iter_idx})</b>')
    #             report.build_table_title()
    #             for k, v in test_input_info.items():
    #                 print(f" {k}  : {v} ")

    #             report.set_table_dataframe(pd.DataFrame(test_input_info))
    #             report.build_table()

    #         report.build_footer()
    #         report.write_html()
    #         report.write_pdf(_orientation="Landscape")


    def generate_report(self, result_dir_name, per_post_timeout=120, poll_interval=2):
        """
        Build report, guaranteeing per-iteration completeness:
        - Waits until (#posts seen for iteration i) == (#devices) or timeout.
        - For devices that never posted in iteration i, inserts NA rows.
        """
        import os, time, shutil
        import pandas as pd

        print('===============================')
        print('Devices DATA:', self.devices_data)
        print('===============================')

        # --- Build the canonical device roster (stable order) ---
        # Roster is list of dicts with hostname/ip/mac/ssid/channel
        roster = []
        for key, info in self.devices_data.items():
            roster.append({
                "key": key,
                "hostname": info.get("hostname", "") or "",
                "ip": info.get("ip", "") or "",
                "mac": info.get("mac", "") or "",
                "ssid": info.get("ssid", "") or "",
                "channel": info.get("channel", "") or "",
                "device_type": info.get("device type", "") or ""
            })
        # sort by hostname, then ip for stable graphs/tables
        roster.sort(key=lambda r: (str(r["hostname"]), str(r["ip"])))
        device_count = len(roster)

        # --- Helper: ensure we received m posts for iteration i, otherwise wait (up to timeout) ---
        def wait_for_iteration_posts(iter_idx, expected, timeout_s=per_post_timeout, sleep_s=poll_interval):
            start = time.time()
            while True:
                # how many rows do we have recorded for this iteration?
                iter_block = self.iteration_dict.get(iter_idx, None)
                have = len(iter_block["ip"]) if iter_block and "ip" in iter_block else 0
                if have >= expected:
                    print(f"[WAIT] Iteration {iter_idx}: received {have}/{expected} posts ? continuing.")
                    return True
                if time.time() - start >= timeout_s:
                    print(f"[WAIT] Iteration {iter_idx}: timed out at {have}/{expected} posts after {timeout_s}s.")
                    return False
                time.sleep(sleep_s)

        # --- Reporting only if not interop mode (keeps your original behavior) ---
        if not self.do_interopability:
            # Create report and make sure destination dirs exist
            report = lf_report(
                _output_pdf="speedtest.pdf",
                _output_html="speedtest.html",
                _results_dir_name=result_dir_name,
                _path=self.result_dir if self.dowebgui else "/home/lanforge/html-reports"
            )
            report_path = report.get_path()
            report_path_date_time = report.get_path_date_time()
            os.makedirs(report_path, exist_ok=True)
            os.makedirs(report_path_date_time, exist_ok=True)

            # Move CSV (if created earlier) into timestamp dir, ignore if absent
            try:
                if os.path.exists(f'speedtest_results_{self.instance}.csv'):
                    shutil.move(f'speedtest_results_{self.instance}.csv', report_path_date_time)
            except Exception as e:
                print(f"[WARN] could not move CSV: {e}")

            logger.info("path: {}".format(report_path))
            logger.info("path_date_time: {}".format(report_path_date_time))

            # --- Title & objective ---
            report.set_title("Speed Test")
            report.build_banner()

            report.set_obj_html(
                _obj_title="Objective",
                _obj=("The Candela Speed Test evaluates AP performance under real-world conditions by measuring latency, "
                    "download speed, and upload speed. The goal is to reflect true end-user experience in typical deployments.")
            )
            report.build_objective()

            # --- Test configuration summary ---
            android_devices = windows_devices = linux_devices = mac_devices = 0
            for r in roster:
                dt = r["device_type"]
                if dt == 'Android':
                    android_devices += 1
                elif dt == 'Windows':
                    windows_devices += 1
                elif dt == 'Mac OS':
                    mac_devices += 1
                elif dt == 'Linux/Interop':
                    linux_devices += 1
            total_devices = ""
            if android_devices: total_devices += f" Android({android_devices})"
            if windows_devices: total_devices += f" Windows({windows_devices})"
            if linux_devices:   total_devices += f" Linux({linux_devices})"
            if mac_devices:     total_devices += f" Mac({mac_devices})"

            report.test_setup_table(
                test_setup_data={
                    "Test name": "Speed Test",
                    "Number of Iterations": self.iteration,
                    "Number of Selected Devices": f"{device_count} {total_devices}".strip()
                },
                value="Test Configuration"
            )

            # --- Per-iteration graphs and tables, with NA backfill ---
            missing_notes_all = []

            for iter_idx in range(1, self.iteration + 1):
                print('Iteration DATA:', self.iteration_dict)

                # Wait until we have m rows or timing out
                wait_for_iteration_posts(iter_idx, expected=device_count)

                iter_block = self.iteration_dict.get(iter_idx, {
                    'ip': [], 'hostname': [], 'download_speed': [], 'upload_speed': [], 'download_lat': [], 'upload_lat': []
                })

                # Map from IP -> index in lists (iteration_dict keeps parallel arrays)
                ip_to_idx = {ip: i for i, ip in enumerate(iter_block.get('ip', []))}

                hostnames = []
                dls = []
                uls = []
                dlat = []
                ulat = []

                t_hostname = []
                t_mac = []
                t_ssid = []
                t_channel = []
                t_type = []

                for dev in roster:
                    ip = dev["ip"]
                    host = dev["hostname"]
                    t_hostname.append(host)
                    t_mac.append(dev["mac"])
                    t_ssid.append(dev["ssid"])
                    t_channel.append(dev["channel"])
                    t_type.append(dev["device_type"])

                    if ip in ip_to_idx:
                        j = ip_to_idx[ip]
                        hostnames.append(host or ip)
                        dls.append(iter_block['download_speed'][j])
                        uls.append(iter_block['upload_speed'][j])
                        dlat.append(iter_block['download_lat'][j])
                        ulat.append(iter_block['upload_lat'][j])
                    else:
                        host_label = host or ip or "(unknown)"
                        hostnames.append(host_label)
                        dls.append(0.0)
                        uls.append(0.0)
                        dlat.append(0.0)
                        ulat.append(0.0)
                        missing_notes_all.append(
                            f"Iteration {iter_idx}: no POST received for device {host_label} (IP {ip or 'N/A'}); row filled with NA/0."
                        )

                # ---- Graphs ----
                report.set_table_title('Per-Client Speed (Download & Upload)')
                report.build_table_title()
                graph = lf_bar_graph(
                    _data_set=[dls, uls],
                    _xaxis_name="Device Name",
                    _yaxis_name="Speed (in Mbps)",
                    _xaxis_categories=hostnames,
                    _graph_image_name=f"Download_upload_speed_iter_{iter_idx}",
                    _label=["Download", "Upload"],
                    _color=None,
                    _color_edge='red',
                    _show_bar_value=True,
                    _text_font=7,
                    _text_rotation=None,
                    _enable_csv=True
                )
                report.set_graph_image(graph.build_bar_graph())
                report.move_graph_image()
                report.build_graph()

                report.set_table_title('Per-Client Latency (Download & Upload)')
                report.build_table_title()
                graph2 = lf_bar_graph(
                    _data_set=[dlat, ulat],
                    _xaxis_name="Device Name",
                    _yaxis_name="Latency (in ms)",
                    _xaxis_categories=hostnames,
                    _graph_image_name=f"Download_upload_Latency_iter_{iter_idx}",
                    _label=["Download", "Upload"],
                    _color=None,
                    _color_edge='red',
                    _show_bar_value=True,
                    _text_font=7,
                    _text_rotation=None,
                    _enable_csv=True
                )
                report.set_graph_image(graph2.build_bar_graph())
                report.move_graph_image()
                report.build_graph()

                # ---- Per-iteration device table (aligned, always length m) ----
                test_input_info = {
                    # "IP": [dev["ip"] for dev in roster],   # uncomment if you want the IP column
                    "hostname": t_hostname,
                    "MAC": t_mac,
                    "Device Type": t_type,
                    "SSID": t_ssid,
                    "Channel": t_channel,
                    "Download Speed (Mbps)": dls,
                    "Upload Speed (Mbps)": uls,
                    "Download Latency (ms)": dlat,
                    "Upload Latency (ms)": ulat,
                }

                report.set_table_title(f'<b>Device Data (Iteration {iter_idx})</b>')
                report.build_table_title()
                for k, v in test_input_info.items():
                    print(f" {k}  : {v} ")

                report.set_table_dataframe(pd.DataFrame(test_input_info))
                report.build_table()

            # If anything was missing, add a ?Notes? block at the end
            if missing_notes_all:
                notes_html = "<br>".join(missing_notes_all)
                report.set_obj_html(_obj_title="Notes", _obj=notes_html)
                report.build_objective()

            # Footer + files
            report.build_footer()
            report.write_html()
            report.write_pdf(_orientation="Landscape")
        print(f"[REPORT] done, files in: {report_path_date_time}")



def main():
    help_summary = '''\
The Candela's Speed Test is designed to evaluate the Access Point (AP) performance under real-world conditions by measuring key network metrics such as latency, download speed, upload speed.
This test aims to reflect the true end-user experience in typical deployment environments.

This test is currently supported only on laptop-based clients, including Linux, Windows, and Mac OS devices.

Key metrics collected include:
- Download Speed
- Upload Speed
- Idle Latency
- Download Latency
- Upload Latency
    '''

    parser = argparse.ArgumentParser(
        prog="lf_interop_speedtest.py",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
            Provides the list of available client devices and allows the user to perform speed testing
            on selected devices.
        ''',
        description='''\
            NAME: lf_interop_speedtest.py

            PURPOSE:
                The lf_interop_speedtest.py script enables users to perform real-world WiFi speed tests using laptop-based clients
                such as Linux, Windows, and macOS. This test does not support mobile platforms (e.g., Android, iOS).

                Instead, it focuses on measuring actual end-user experience by capturing metrics such as download/upload speed,
                latency (ping). The script uses the Speedtest.net service (via browser automation) to run the tests.

                TO PERFORM SPEED TEST:

                EXAMPLE-1:
                Run a default speed test using browser-based automation (Selenium)

                python3 lf_interop_speedtest.py --mgr 192.168.204.74

                EXAMPLE-2:
                Run a speed and interoperability test using browser automation

                python3 lf_interop_speedtest.py --mgr 192.168.204.74 --do_interopability
            '''
        )

    parser = argparse.ArgumentParser(
        prog='interop_speedtest.py',
        formatter_class=argparse.RawTextHelpFormatter)
    optional = parser.add_argument_group('Optional arguments')

    # optional arguments
    optional.add_argument('--mgr',
                        type=str,
                        help='hostname where LANforge GUI is running',
                        default='localhost')

    optional.add_argument('--device_list',
                        type=str,
                        help='Mention device list (comma seperated)',
                        )

    optional.add_argument('--instance_name',
                        type=str,
                        default='Speed_Test_report',
                        help='Mention Test Instance name (report folder name)',
                        )
    optional.add_argument('--iteration',
                        type=int,
                        default=1,
                        help='Mention number of iterations for the test.',
                        )

    optional.add_argument('--do_interopability',
                        action='store_true',
                        help='Ensures test on devices run sequentially')
    
    optional.add_argument('--result_dir',
                        type=str,
                        default='results',
                        help='Directory to store test results')
    
    optional.add_argument('--dowebgui',
                        action='store_true',
                        help='Generates a web GUI report for the test results')

    optional.add_argument('--type',
                        choices=['cli', 'ookla'],
                        default='ookla',
                        help='Type of speed test to perform (cli, ookla)')

    optional.add_argument('--cleanup',
                        action='store_true',
                        help='cleans up generic cx after completion of the test')


    #TODO Commented lines are for implementation of incremental testing.
    # optional.add_argument('--do_increment',
    #                       help='Specify the incremental values for speedtesting as a comma-separated list (e.g., 10,20,30).',
    #                       default=[])

    parser.add_argument('--help_summary', default=None, action="store_true", help='Show summary of what this script does')

    args = parser.parse_args()

    if args.help_summary:
        print(help_summary)
        exit(0)

    #TODO for folder creation purpose only 
    # folder_name = f"{args.instance_name or 'SpeedTest'}"
    # os.makedirs(folder_name, exist_ok=True)
    # csv_file = os.path.join(folder_name, "speedtest_results.csv")
    
    csv_file = f"speedtest_results_{args.instance_name}.csv"
    # if not args.dowebgui else f"{args.result_dir}/speedtest_results_{args.instance_name}.csv"

    speedtest_obj = SpeedTest(manager_ip=args.mgr,
                            device_list=args.device_list,
                            instance=args.instance_name,
                            iteration=args.iteration,
                            do_interopability=args.do_interopability,
                            result_dir=args.result_dir,
                            type=args.type,
                            dowebgui=args.dowebgui)
    speedtest_obj.get_resource_data()
    speedtest_obj.create()

    if args.do_interopability:
        speedtest_obj.create_cx_do_interop(csv_file)

    else:
        for iter in range(1, args.iteration + 1):
            print(f"\n Starting Iteration {iter} of {args.iteration}")

            speedtest_obj.start_generic()
            print(f"Test started at {speedtest_obj.start_time}")
            time.sleep(50) # Speedtest duration wait time.
            speedtest_obj.stop_generic()
            time.sleep(20)

            # Wait until we have received posts from all expected devices (or timeout)
            def expected_post_ips(devices):
                want = []
                for info in devices.values():
                    cmd = (info.get('cmd') or '')
                    ip  = (info.get('ip')  or '')
                    if ip and '--post_url' in cmd:
                        want.append(ip)
                # de-dup (stable)
                seen, out = set(), []
                for ip in want:
                    if ip not in seen:
                        seen.add(ip)
                        out.append(ip)
                return out

            def has_post_for(ip):
                k = ip.replace('.', '_')
                # ookla.py posts using this exact key format
                return (k in speedtest_obj.result_json) or (ip in speedtest_obj.result_json)

            expected_ips = expected_post_ips(speedtest_obj.devices_data)
            deadline = time.time() + 120
            while time.time() < deadline:
                got = [ip for ip in expected_ips if has_post_for(ip)]
                if len(got) >= len(expected_ips):
                    break
                time.sleep(1)

            # Finally, write results for this iteration
            speedtest_obj.write_results_to_csv(iter, csv_file)
            # time.sleep() #TODO Hardcoded wait time to allow all devices to be ready for next iteration.
            speedtest_obj.result_json = {}

    if args.cleanup:
        speedtest_obj.cleanup()

    speedtest_obj.generate_report(result_dir_name=args.instance_name)

if __name__ == "__main__":
    main()
