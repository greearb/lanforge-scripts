#!/usr/bin/env python3
"""
NAME: lf_wifi_msgs.py

PURPOSE:
    Fetch LANforge Wi-Fi messages from the GUI REST API (/wifi-msgs): the last or
    first N messages, every buffered message, everything since a time-stamp,
    everything from the last <duration>, everything between two stamps, or keep
    printing new messages as they arrive.

EXAMPLE:
    python3 lf_wifi_msgs.py --mgr 192.168.1.31 --last 50
    python3 lf_wifi_msgs.py --mgr 192.168.1.31 --all
    python3 lf_wifi_msgs.py --mgr 192.168.1.31 --duration 5m --output json --outfile msgs.json
    python3 lf_wifi_msgs.py --mgr 192.168.1.31 --since 1699999999999 --output json
    python3 lf_wifi_msgs.py --mgr 192.168.1.31 --between 1788159332090 1788161286054
    python3 lf_wifi_msgs.py --mgr 192.168.1.31 --poll --interval 2s

    # check connection stats for given device_list for real clients:
    python3 lf_wifi_msgs.py --mgr 192.168.245.117 --analyze_clients --device_list 1.10,1.13 \
        --start_time 1699999999999

    # check connection stats by querying the device_list from LANforge of real clients:
    python3 lf_wifi_msgs.py --mgr 192.168.245.117 --analyze_clients --start_time 1699999999999

    # check connection stats for selected device_list for real clients, between two timestamps:
    python3 lf_wifi_msgs.py --mgr 192.168.245.117 --analyze_clients --start_time 1699999999999 --end_time 1700000000000

    # check connection stats for the last 5 minutes, instead of giving --start_time:
    python3 lf_wifi_msgs.py --mgr 192.168.245.117 --analyze_clients --duration 5m --device_list 1.10,1.13


    # importable
    from lf_wifi_msgs import WifiMessages
    wifi_msgs = WifiMessages(host="192.168.1.31")
    for entry in wifi_msgs.last(50):
        print(entry["time-stamp"], entry["resource"], entry["text"])
    for entry in wifi_msgs.poll(interval=2):   # stop with break / wifi_msgs.stop_polling()
        handle(entry)

NOTES:
    LANforge time-stamps are epoch milliseconds. --since / --between values are
    sent through unchanged; --duration is computed off the newest message.
    Raw output is '<time-stamp> <resource>  <text>' per line; --output json keeps the full entry dicts.

SCRIPT_CLASSIFICATION: Reporting, Wi-Fi Messages

SCRIPT_CATEGORIES: Functional

STATUS: Functional

COPYRIGHT:
Copyright (C) 2020-2026 Candela Technologies Inc
License: Free to distribute and modify. LANforge systems must be licensed.

INCLUDE_IN_README: False
"""
import sys
import os
import importlib
import argparse
import json
import re
import time
import datetime
import threading
import logging
from typing import Callable, Iterator, List, Optional
import pandas as pd
from DeviceConfig import DeviceConfig

logger = logging.getLogger(__name__)
if sys.version_info[0] != 3:
    logger.critical("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

RETRY_TIMEOUT = 40      # seconds to keep retrying a /wifi-msgs GET that returns nothing
RETRY_INTERVAL = 5      # seconds between those retries
POLL_INTERVAL = 5       # default seconds between polls in poll()


class WifiMessages(Realm):
    """Query the LANforge '/wifi-msgs' REST endpoints."""

    def __init__(self, host: Optional[str] = None, port: int = 8080, debug: bool = False,
                 retry_timeout: int = RETRY_TIMEOUT, retry_interval: int = RETRY_INTERVAL) -> None:
        """Build a /wifi-msgs client.

        Args:
            host: LANforge manager IP or hostname.
            port: LANforge GUI REST port (default 8080).
            debug: pass through to the REST layer for verbose logging.
            retry_timeout: seconds to keep retrying a GET that returns nothing.
            retry_interval: seconds between those retries.
        """
        super().__init__(host, port, debug_=debug)
        self.debug = debug
        self.retry_timeout = retry_timeout
        self.retry_interval = retry_interval
        self._poll_stop = threading.Event()   # set by stop_polling(), watched by poll()

    @staticmethod
    def normalize_messages(response: Optional[dict]) -> List[dict]:
        """Normalize a '/wifi-msgs' response body into a flat list of entry dicts.

        Args:
            response: the decoded JSON body of a /wifi-msgs GET, or None.

        LANforge returns wifi-messages as a bare entry, a '{<key>: {entry}}'
        wrapper, or a list of either; this returns a plain list of the entry dicts
        (each has 'resource', 'text', 'time-stamp'). Missing or empty gives [].
        """
        messages = (response or {}).get("wifi-messages")
        if messages is None:
            return []
        items = messages if isinstance(messages, list) else [messages]
        out = []
        for item in items:
            if not isinstance(item, dict):
                continue
            if "text" in item or "time-stamp" in item:
                out.append(item)
            else:
                out.extend(v for v in item.values() if isinstance(v, dict))
        return out

    @staticmethod
    def timestamp_ms(entry: dict) -> Optional[int]:
        """The entry's 'time-stamp' as an int, or None if missing/non-numeric.

        Args:
            entry: one normalized wifi-msg dict.
        """
        raw = entry.get("time-stamp") or entry.get("timestamp")
        try:
            return int(str(raw).strip())
        except (TypeError, ValueError):
            logger.error("wifi-msg entry has a missing/non-numeric time-stamp: %r", raw)
            return None

    @staticmethod
    def to_seconds(text: str) -> float:
        """Parse a duration into float seconds.

        Accepts a bare number (seconds) or a number with a unit suffix - ms, s, m, h or d - e.g. 30s, 5m, 2h, 500ms, or just 30.

        Args:
            text: the duration string to parse.
        """
        match = re.match(r"^\s*(\d+(?:\.\d+)?)\s*(ms|s|m|h|d)?\s*$", str(text), re.IGNORECASE)
        if not match:
            raise ValueError("invalid duration {!r}; use e.g. 30s, 5m, 2h, 500ms".format(text))
        units = {"ms": 0.001, "s": 1, "m": 60, "h": 3600, "d": 86400}
        return float(match.group(1)) * units[(match.group(2) or "s").lower()]

    def get_wifi_messages(self, uri: str) -> List[dict]:
        """GET wifi messages (retrying while the response is empty), return the normalized entries.

        Args:
            uri: the /wifi-msgs REST path to GET.
        """
        start = time.time()
        response = self.json_get(uri, debug_=self.debug)
        while response is None and (time.time() - start) < self.retry_timeout:
            logger.warning("GET %s returned nothing from LANforge; retrying", uri)
            time.sleep(self.retry_interval)
            response = self.json_get(uri, debug_=self.debug)
        if response is None:
            logger.error("GET %s returned nothing after %ss", uri, self.retry_timeout)
        return self.normalize_messages(response)

    def all_messages(self) -> List[dict]:
        """Every message currently buffered by LANforge - using first message as reference."""
        oldest = self.first(1)
        base_ms = self.timestamp_ms(oldest[0]) if oldest else None
        if base_ms is None:
            return oldest
        return self.since(base_ms)

    def last(self, count: int = 1) -> List[dict]:
        """The most recent buffered messages.

        Args:
            count: number of messages to fetch (default 1).
        """
        return self.get_wifi_messages("/wifi-msgs/last/{}".format(int(count)))

    def first(self, count: int = 1) -> List[dict]:
        """The oldest buffered messages.

        Args:
            count: number of messages to fetch (default 1).
        """
        return self.get_wifi_messages("/wifi-msgs/first/{}".format(int(count)))

    def since(self, timestamp: int) -> List[dict]:
        """Every buffered message at or after a time-stamp.

        Args:
            timestamp: LANforge epoch-ms time-stamp.
        """
        return self.get_wifi_messages("/wifi-msgs/since=time/{}".format(timestamp))

    def between(self, start: int, end: int) -> List[dict]:
        """Every buffered message within a time window.

        Args:
            start: window start, LANforge epoch-ms time-stamp.
            end: window end, LANforge epoch-ms time-stamp.
        """
        return self.get_wifi_messages("/wifi-msgs/between=time/{}/{}".format(start, end))

    def fetch_keyed_messages(self, start: int, end: Optional[int] = None) -> List[dict]:
        """Fetches messages for a time window, each wrapped as '{"<resource>.<time-stamp>": entry}'.

        Args:
            start: window start, LANforge epoch-ms time-stamp.
            end: window end, LANforge epoch-ms time-stamp, or None to go since 'start'.
        """
        entries = self.between(start, end) if end is not None else self.since(start)
        keyed_entries = []
        for entry in entries:
            resource = entry.get("resource", "")
            ts = entry.get("time-stamp", entry.get("timestamp", ""))
            keyed_entries.append({"{}.{}".format(resource, ts): entry})
        return keyed_entries

    def duration(self, seconds: float) -> List[dict]:
        """Messages from the last 'seconds': the newest message's stamp minus the window, via since=time.
           Falls back to last=time with no baseline.

        Args:
            seconds: window length in seconds.
        """
        window_ms = int(float(seconds) * 1000)
        latest = self.last(1)
        base_ms = self.timestamp_ms(latest[-1]) if latest else None
        if base_ms is None:
            logger.warning("No epoch-ms wifi-msg baseline available; using /wifi-msgs/last=time")
            return self.get_wifi_messages("/wifi-msgs/last=time/{}".format(window_ms))
        return self.since(base_ms - window_ms)

    def stop_polling(self) -> None:
        """Ask a running 'poll()' to stop. Cleared on the next 'poll()' entry."""
        self._poll_stop.set()

    def poll(self, interval: float = POLL_INTERVAL, since_ts: Optional[int] = None,
             stop: Optional[Callable[[], bool]] = None) -> Iterator[dict]:
        """Yield each new /wifi-msgs entry once, as it appears.

        Open-ended generator; never prints. Stop it with 'break', 'stop_polling()', or a 'stop' predicate.

        Args:
            interval: seconds to wait between polls (default POLL_INTERVAL).
            since_ts: epoch-ms start point; default is the newest message at entry, so only new traffic is yielded.
            stop: optional predicate; polling ends when it returns True.
        """
        self._poll_stop.clear()
        if since_ts is None:
            deadline = time.time() + self.retry_timeout
            while since_ts is None:
                latest = self.last(1)
                since_ts = self.timestamp_ms(latest[-1]) if latest else None
                if since_ts is not None or time.time() >= deadline:
                    break
                # timestamp_ms() is None on a missing/non-numeric stamp; retry a few times for a real one before giving up.
                logger.warning("wifi-msg has no usable time-stamp; retrying for a poll baseline")
                if self._poll_stop.wait(self.retry_interval):
                    return
            if since_ts is None:
                # Still nothing usable, end the generator so the caller stops.
                logger.error("no usable wifi-msg time-stamp for a poll baseline after %ss; giving up", self.retry_timeout)
                return
        since_ts = int(since_ts)
        seen = {(e.get("resource"), e.get("time-stamp"), str(e.get("text")))
                for e in self.since(since_ts) if self.timestamp_ms(e) == since_ts}

        while not self._poll_stop.is_set() and not (stop and stop()):
            batch = self.since(since_ts)
            newest = since_ts
            for entry in batch:
                marker = (entry.get("resource"), entry.get("time-stamp"), str(entry.get("text")))
                if marker not in seen:
                    yield entry
                ts = self.timestamp_ms(entry)
                if ts is not None and ts > newest:
                    newest = ts
            # Advance the cursor; the batch was fetched from the old (<= newest) cursor.
            since_ts = newest
            seen = {(e.get("resource"), e.get("time-stamp"), str(e.get("text")))
                    for e in batch if self.timestamp_ms(e) == newest}
            if self._poll_stop.wait(interval):
                return

    @staticmethod
    def render(entries: List[dict], output: str, stream, line_delimited: bool = False) -> None:
        """Write entries to stream.

        Args:
            entries: normalized wifi-msg dicts to write.
            output: 'raw' or 'json'.
            stream: a writable text stream (file object or sys.stdout).
            line_delimited: json only - emit one object per line instead of an array.

        output='raw'  -> '<time-stamp> <resource>  <text>', one line of text at a time.
        output='json' -> a pretty JSON array; or, with line_delimited=True (used by --poll), one compact JSON object
                         per line so the growing stream stays parseable line by line.

        """
        if output == "json":
            if line_delimited:
                for entry in entries:
                    stream.write(json.dumps(entry, separators=(",", ":")) + "\n")
            else:
                json.dump(entries, stream, indent=2)
                stream.write("\n")
            return
        for entry in entries:
            ts = entry.get("time-stamp", "")
            resource = entry.get("resource", "")
            text = entry.get("text", [])
            for line in (text if isinstance(text, list) else [text]):
                stream.write("{} {}  {}\n".format(ts, resource, line))


class ClientAnalysis(Realm):
    """Tracks each real client device's Wi-Fi connection stats: disconnects, scans,
    connect attempts, rejections, and successful connections from wifi messages.
    """

    def __init__(self, host: Optional[str] = None, port: int = 8080,
                 device_list: Optional[List[str]] = None, debug: bool = False) -> None:
        """Sets up a new analyzer for checking real client devices' Wi-Fi connections.

        Args:
            host (str): LANforge manager IP.
            port (int): LANforge GUI REST port (default 8080).
            device_list (list): resource IDs (e.g. '1.10') to analyze.
            debug (bool): turn on verbose logging.

        Returns:
            None

        Example:
            ClientAnalysis(host="192.168.1.31", device_list=["1.10", "1.13"])
        """
        super().__init__(host, port, debug_=debug)
        self.host = host
        self.port = port
        self.device_list = list(device_list) if device_list else []
        self.wifi_msgs = WifiMessages(host=host, port=port, debug=debug)
        self.device_config_obj = DeviceConfig(lanforge_ip=host, port=port)
        self.resource_id_to_abs = {}
        self.windows_list = []
        self.resource_id_list = []
        self.device_messages = {}
        self.android_device_names = set()

    FILTER_SPECS = {
        "android": {
            "Disconnected": ["Terminating..."],
            "Scanning": ["SCAN-STARTED"],
            "ConnectAttempt": ["Trying to associate with"],
            "Association Rejection": ["ASSOC_REJECT"],
            "Connected": ["CTRL-EVENT-CONNECTED"],
        },
        "windows": {
            "Disconnected": ["Wireless security stopped.",
                             "WLAN AutoConfig service has successfully disconnected from a wireless network"],
            "Scanning": ["service started"],
            "ConnectAttempt": ["association started."],
            "Association Rejection": ["failed to connect"],
            "Connected": ["connected"],
        },
        "other": {  # linux, mac
            "Disconnected": ["disconnected", "<3>CTRL-EVENT-DSCP-POLICY clear_all"],
            "Scanning": ["<3>CTRL-EVENT-SCAN-STARTED"],
            "ConnectAttempt": ["<3>Trying to associate with"],
            "Association Rejection": ["NoneValue"],
            # macOS reports connects as "en0: STA is connected to a wireless network."
            "Connected": ["<3>CTRL-EVENT-CONNECTED", "STA is connected"],
        },
    }

    def setup_device_entries(self) -> dict:
        """Builds an empty counters entry for each device to analyze.

        Returns:
            dict: one empty counters entry per device to analyze.

        Example:
            analysis.setup_device_entries()
            # {"1.10.wlan0": {"ConnectAttempt": None, "Disconnected": None, "Scanning": None,
            #                 "Association Rejection": None, "Connected": None, "port_name": "1.10.wlan0"}}
        """
        if not self.resource_id_list and not self.resource_id_to_abs:
            self.discover_devices()
        adb_resources = self.json_get("/adb/")
        android_devices = adb_resources["devices"]
        local_dict = {}
        port_name_list = []

        single_device = isinstance(android_devices, dict)
        if single_device:
            android_devices = [android_devices]

        for device in android_devices:
            actual_device = device if single_device else list(device.values())[0]
            res = actual_device.get("resource-id")
            name = actual_device.get("name")
            if name:
                self.android_device_names.add(name)
            for i in self.device_list:
                if res in i and res != "":
                    local_dict[name] = None
                    port_name_list.append(res + ".wlan0")

        for dev in self.resource_id_to_abs.values():
            res_id = "{}.{}".format(dev.split('.')[0], dev.split('.')[1])
            for i in self.device_list:
                if res_id in i:
                    local_dict[dev] = None
                    port_name_list.append(dev)

        keys_list = ["ConnectAttempt", "Disconnected", "Scanning", "Association Rejection", "Connected", "port_name"]
        sec_dict = dict.fromkeys(keys_list)
        for i, key in enumerate(local_dict.keys()):
            local_dict[key] = sec_dict.copy()
            local_dict[key]["port_name"] = port_name_list[i]
        logger.debug("local dict: %s", local_dict)
        return local_dict

    def build_devices_dataframe(self, all_devices: List[dict]):
        """Builds a table of devices, with each one's resource ID, name, and OS.

        Args:
            all_devices (list): the discovered device dicts to show (each with 'shelf',
                'resource', 'type', and either 'hostname' or 'serial').

        Returns:
            DataFrame: one row per device, with 'Resource ID', 'Name', and 'OS' columns.

        Example:
            analysis.build_devices_dataframe([{"shelf": "1", "resource": "10", "type": "laptop",
                                           "hostname": "my-laptop", "os": "Win"}])
            #   Resource ID        Name   OS
            #   1.10        my-laptop  Win
        """
        rows = []
        for device in all_devices:
            res_id = device["shelf"] + '.' + device["resource"]
            os_type = device.get("os", "Unknown")
            if device["type"] == 'laptop':
                dev_name = device.get("hostname", "Unknown")
            else:  # adb
                dev_name = device.get("serial", "Unknown")
            rows.append({
                "Resource ID": res_id,
                "Name": dev_name,
                "OS": os_type,
            })
        return pd.DataFrame(rows)

    @staticmethod
    def save_json_log(json_list, file_name: str = "empty.json") -> None:
        """Saves json_list as a JSON log file under Wifi_Messages/.

        Args:
            json_list: the data to save -- anything json.dumps() can serialize.
            file_name (str): the file name to save it under, inside Wifi_Messages/.

        Returns:
            None

        Example:
            ClientAnalysis.save_json_log({"1.10.wlan0": {"Connected": []}}, "2026-10-23.json")
            # writes Wifi_Messages/2026-10-23.json
        """
        json_string = json.dumps(json_list)
        new_folder = "Wifi_Messages"
        if not (os.path.exists(new_folder) and os.path.isdir(new_folder)):
            os.makedirs(new_folder)
        with open(os.path.join(new_folder, file_name), 'w') as file:
            file.write(json_string)

    def find_messages_for_device_and_filter(self, value=None, keys_list=None, device=None, filter=None) -> List[dict]:
        """Goes through one device's wifi messages and pulls out the ones that both
        mention that device and match the given keyword (e.g. 'disconnected').

        Args:
            value (list): the wifi messages to search, e.g. from WifiMessages.fetch_keyed_messages().
            keys_list (list): the keys of 'value', in the same order (one per message).
            device (str): the LANforge port name (e.g. '1.10.wlan0') to look for messages about.
            filter (str): the keyword (or phrase) that marks the event being searched for.

        Returns:
            list: each match as a {'timestamp', 'text'} dict, in the order they were found.

        Example:
            analysis.find_messages_for_device_and_filter(
                value=values, keys_list=keys_list, device="1.10.wlan0", filter="CTRL-EVENT-CONNECTED")
            # [{"timestamp": "1699999999999", "text": "wlan0: CTRL-EVENT-CONNECTED - ..."}]
        """
        matches = []
        device_split = device.split(".")
        device_name = device_split[2]
        resource_id = "{}.{}".format(device_split[0], device_split[1])
        ifname_marker = "IFNAME={}".format(device_name)
        filter_words = filter.split(" ")

        for i, y in zip(keys_list, range(len(keys_list))):
            entry = value[y][i]
            if entry['resource'] != resource_id:
                continue
            time_stamp = entry['time-stamp']
            wifi_msg_text = entry['text']
            is_android_message = isinstance(wifi_msg_text, list)
            for text in (wifi_msg_text if is_android_message else [wifi_msg_text]):
                words = text.split(" ")
                message_mentions_device = (device_name in words) if is_android_message \
                    else any(device_name in word for word in words)
                message_mentions_device = message_mentions_device or ifname_marker in words
                if message_mentions_device and (filter in words or all(word in words for word in filter_words)):
                    matches.append({"timestamp": time_stamp, "text": text})
        return matches

    def count_wifi_events_for_device(self, local_dict, phn_name, values, keys_list) -> dict:
        """Counts one device's connect/disconnect/scan/rejection events from wifi messages.

        Args:
            local_dict (dict): counters for every device, from setup_device_entries(). We only
                update this device's entry.
            phn_name (str): the device's LANforge port name, e.g. '1.10.wlan0'.
            values (list): wifi messages already fetched, from WifiMessages.fetch_keyed_messages().
            keys_list (list): the keys of 'values', in the same order (one per message).

        Returns:
            dict: the same local_dict, with this device's counts filled in.

        Example:
            analysis.count_wifi_events_for_device(local_dict, "1.10.wlan0", values, keys_list)
            # {"1.10.wlan0": {"Disconnected": 1, "Scanning": 1, "ConnectAttempt": 1,
            #                 "Association Rejection": 0, "Connected": 1, "Remarks": "NA"}}
        """
        logger.debug("Counting DISCONNECTIONS/SCANNING/ASSOC ATTEMPTS/ASSOC REJECTIONS/CONNECTS for device %s", phn_name)

        android = any(phn_name in name for name in self.android_device_names)
        os_key = "android" if android else ("windows" if phn_name in self.windows_list else "other")

        device_messages = {}
        for category, filters in self.FILTER_SPECS[os_key].items():
            matches = []
            for text_filter in filters:
                matches = self.find_messages_for_device_and_filter(value=values, keys_list=keys_list, device=phn_name, filter=text_filter)
                if matches:
                    break
            device_messages[category] = matches
        counts = {category: len(msgs) for category, msgs in device_messages.items()}
        disconnected = counts["Disconnected"]
        scanning = counts["Scanning"]
        attempt = counts["ConnectAttempt"]
        rejection = counts["Association Rejection"]
        connected = counts["Connected"]

        if android:
            if attempt > connected:
                rejection = attempt - connected
            remarks = "NA"
        else:
            if rejection:
                actual_connects = attempt - rejection
                connected = connected if actual_connects == connected else actual_connects
            if attempt > connected:
                rejection = attempt - connected
            if disconnected == 0 and connected == 1:
                remarks = "No Disconnections are seen but Client is UP and connected to SSID."
            elif disconnected >= 1 and connected == 0:
                remarks = "The Disconnections are seen but Client did not connected to SSID."
            else:
                remarks = "NA"

        local_dict[phn_name].update({
            "Disconnected": disconnected, "Scanning": scanning, "ConnectAttempt": attempt,
            "Association Rejection": rejection, "Connected": connected,
            "Remarks": remarks,
        })

        self.device_messages[phn_name] = device_messages
        return local_dict

    def get_connectivity_analysis(self, start_time, end_time, local_dict: dict) -> dict:
        """Gets connectivity stats for every device in local_dict, and logs the evidence.

        Args:
            start_time (int): epoch-ms timestamp to start counting from.
            end_time (int): epoch-ms timestamp to stop counting at. Leave as None to count
                all the way up to now.
            local_dict (dict): counters for every device, from setup_device_entries().

        Returns:
            dict: the same local_dict, with every device's counts filled in.

        Example:
            analysis.get_connectivity_analysis(1699999999999, None, local_dict)
            # {"1.10.wlan0": {"Disconnected": 1, "Scanning": 1, "ConnectAttempt": 1,
            #                 "Association Rejection": 0, "Connected": 1, "Remarks": "NA"}}
        """
        values = self.wifi_msgs.fetch_keyed_messages(start_time, end_time)
        keys_list = [list(v.keys())[0] for v in values]
        for phn_name in local_dict.keys():
            local_dict = self.count_wifi_events_for_device(local_dict=local_dict, phn_name=phn_name,
                                                           values=values, keys_list=keys_list)
        file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
        self.save_json_log(json_list=self.device_messages, file_name=file_name)
        logger.info("Saved wifi message evidence for %d device(s) to %s",
                    len(self.device_messages), os.path.join("Wifi_Messages", file_name))

        totals = {"Disconnected": 0, "Scanning": 0, "ConnectAttempt": 0,
                  "Association Rejection": 0, "Connected": 0}
        for messages in self.device_messages.values():
            for category in totals:
                totals[category] += len(messages[category])
        logger.info("Totals across all devices: Disconnected=%d Scanning=%d ConnectAttempt=%d "
                    "Association Rejection=%d Connected=%d",
                    totals["Disconnected"], totals["Scanning"], totals["ConnectAttempt"],
                    totals["Association Rejection"], totals["Connected"])
        return local_dict

    def discover_devices(self) -> None:
        """Discovers the devices LANforge knows about and fills the lookup lists.
        If no device list was given, prompts the user to pick one.

        Returns:
            None

        Example:
            analysis.discover_devices()
            # fills self.resource_id_list, self.windows_list, self.resource_id_to_abs,
            # and self.device_list (e.g. ["1.10", "1.13"])
        """
        filtered_all_devices = []
        all_devices = self.device_config_obj.get_all_devices()
        dev_list_all = []
        for data in all_devices:
            res_id = "{}.{}".format(data["shelf"], data["resource"])
            if data["shelf"] != "" and data["resource"] != "":
                dev_list_all.append(res_id)
            if data["type"].lower() == "laptop":
                res_id_abs = "{}.{}.{}".format(data["shelf"], data["resource"], data["sta_name"])
                self.resource_id_to_abs[res_id] = res_id_abs
                if data["os"].lower() == "win":
                    self.windows_list.append(res_id_abs)

        response_port = self.json_get("/port/all")
        if "interfaces" not in response_port.keys():
            logger.error("'interfaces' key not found in /port/all response")
            exit(1)
        for interface in response_port['interfaces']:
            for port, port_data in interface.items():
                if not port_data['phantom'] and not port_data['down'] \
                        and port_data['parent dev'] == "wiphy0" and port_data['alias'] != 'p2p0':
                    for data in all_devices:
                        res_id = "{}.{}".format(data["shelf"], data["resource"])
                        if res_id + "." in port:
                            self.resource_id_list.append(res_id)
                            filtered_all_devices.append(data)

        if self.device_list:
            return

        available_df = self.build_devices_dataframe(filtered_all_devices)
        print("\nAvailable devices:")
        print(available_df.to_string(index=False))
        print()

        dev_list = input("Enter the desired resource IDs to run the test (e.g. '1.10'): ").split(',')
        if "all" in dev_list:
            dev_list = dev_list_all.copy()

        res_to_name = {}
        name_to_res = {}
        for device in filtered_all_devices:
            if device["type"] == 'laptop':
                res_to_name[device["shelf"] + '.' + device["resource"]] = device["hostname"]
                name_to_res[device["hostname"]] = device["shelf"] + '.' + device["resource"]
            else:  # adb
                res_to_name[device["eid"]] = device["serial"]
                name_to_res[device["serial"]] = device["eid"]

        self.device_list = self.device_config_obj.filter_device_list(dev_list, name_to_res, res_to_name)


def main() -> None:
    help_summary = ("Fetch LANforge Wi-Fi messages from the /wifi-msgs REST API: last/first N, all buffered, "
                    "since a time-stamp, from the last <duration>, between two stamps, or poll for new ones. "
                    "Importable as WifiMessages.")

    parser = LFCliBase.create_basic_argparse(
        prog='lf_wifi_msgs.py',
        formatter_class=argparse.RawTextHelpFormatter,
        description=__doc__)

    wifi_msgs_args = parser.add_argument_group('wifi-msgs arguments')
    mode = wifi_msgs_args.add_mutually_exclusive_group()
    mode.add_argument('--last', type=int, metavar='N', help='the most recent N messages (default: 25)')
    mode.add_argument('--first', type=int, metavar='N', help='the oldest N messages still buffered')
    mode.add_argument('--all', action='store_true', help='every message currently buffered')
    mode.add_argument('--since', metavar='TIMESTAMP', help='every message since a LANforge epoch-ms time-stamp')
    mode.add_argument('--duration', metavar='WINDOW', help='every message from the last WINDOW (e.g. 30s, 5m, 2h)')
    mode.add_argument('--between', nargs=2, type=int, metavar=('START', 'END'),
                      help='every message between two epoch-ms stamps')
    mode.add_argument('--poll', '-p', action='store_true',
                      help='print new messages as they arrive (Ctrl-C to stop)')
    wifi_msgs_args.add_argument('--analyze_clients', action='store_true',
                                help='show connect/disconnect/scan/rejection counts per '
                                     'device instead of raw wifi messages')
    wifi_msgs_args.add_argument('--interval', default='5s', metavar='WINDOW',
                                help='--poll interval (e.g. 2s, 500ms; default: 5s)')
    wifi_msgs_args.add_argument('--output', choices=['raw', 'json'], default='raw',
                                help='raw message text lines or json (default: raw)')
    wifi_msgs_args.add_argument('--outfile', metavar='PATH', help='write output to PATH instead of stdout')

    analysis_args = parser.add_argument_group('--analyze_clients arguments')
    analysis_args.add_argument('--device_list', default="", metavar='IDS',
                               help="comma-separated resource IDs (e.g. '1.10') to analyze; "
                                    "leave empty to be prompted interactively")
    analysis_args.add_argument('--start_time', metavar='TIMESTAMP',
                               help='epoch-ms time-stamp to start counting wifi messages from; '
                                    'not needed if you give --duration instead')
    analysis_args.add_argument('--end_time', metavar='TIMESTAMP',
                               help='epoch-ms time-stamp to stop counting at (default: now)')

    args = parser.parse_args()
    if args.help_summary:
        print(help_summary)
        exit(0)

    if args.analyze_clients and not args.start_time and args.duration is None:
        parser.error('give either --start_time or --duration with --analyze_clients')

    try:
        interval = WifiMessages.to_seconds(args.interval)
        duration = WifiMessages.to_seconds(args.duration) if args.duration is not None else None
    except Exception as error:
        parser.error(f"Failed to parse the CLI arguments: {str(error)}")

    logger_config = lf_logger_config.lf_logger_config()
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    if args.analyze_clients:
        start_time = args.start_time if args.start_time else str(int(time.time() * 1000) - int(duration * 1000))
        analysis = ClientAnalysis(
            host=args.mgr, port=args.mgr_port,
            device_list=args.device_list.split(',') if args.device_list else [],
            debug=args.debug)
        local_dict = analysis.setup_device_entries()
        if not local_dict:
            print("None of the given devices resolved to a device LANforge knows about.")
            exit(1)
        analysis.get_connectivity_analysis(start_time, args.end_time, local_dict)
        exit(0)

    wifi_msgs = WifiMessages(host=args.mgr, port=args.mgr_port, debug=args.debug)
    out_stream = open(args.outfile, 'w') if args.outfile else sys.stdout
    try:
        if args.poll:
            print("Polling /wifi-msgs (Ctrl-C to stop)", file=sys.stderr)
            try:
                for entry in wifi_msgs.poll(interval=interval):
                    wifi_msgs.render([entry], args.output, out_stream, line_delimited=True)
                    out_stream.flush()
            except KeyboardInterrupt:
                wifi_msgs.stop_polling()
                print("Polling stopped", file=sys.stderr)
        else:
            if args.all:
                entries = wifi_msgs.all_messages()
            elif args.since is not None:
                entries = wifi_msgs.since(args.since)
            elif duration is not None:
                entries = wifi_msgs.duration(duration)
            elif args.between is not None:
                entries = wifi_msgs.between(*sorted(args.between))
            elif args.first is not None:
                entries = wifi_msgs.first(args.first)
            else:
                entries = wifi_msgs.last(args.last if args.last is not None else 25)
            logger.debug("Fetched %d wifi message(s)", len(entries))
            if not entries:
                print("wifi messages are empty or cleared", file=sys.stderr)
            wifi_msgs.render(entries, args.output, out_stream)
    finally:
        if out_stream is not sys.stdout:
            out_stream.close()
    exit(0)


if __name__ == "__main__":
    main()
