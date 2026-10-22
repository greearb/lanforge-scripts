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
    python3 lf_wifi_msgs.py --mgr 192.168.245.117 --analyze_real_clients --device_list 1.10,1.13 \
        --start_time 1699999999999

    # check connection stats by querying the device_list from LANforge of real clients:
    python3 lf_wifi_msgs.py --mgr 192.168.245.117 --analyze_real_clients --start_time 1699999999999

    # check connection stats for selected device_list for real clients, between two timestamps:
    python3 lf_wifi_msgs.py --mgr 192.168.245.117 --analyze_clients --start_time 1699999999999 --end_time 1700000000000


    # importable
    from lf_wifi_msgs import WifiMessages
    wifi_msgs = WifiMessages(host="192.168.245.117")
    for entry in wifi_msgs.last(50):
        print(entry["time-stamp"], entry["resource"], entry["text"])
    for entry in wifi_msgs.poll(interval=2):   # stop with break / wifi_msgs.stop_polling()
        handle(entry)

    # importable, per-real-client connectivity stats (see lf_interop_throughput.py's
    # start_wifi_analysis()/stop_wifi_analysis() for this same pattern in real use)
    from lf_wifi_msgs import RealClientAnalysis
    import time
    analysis = RealClientAnalysis(host="192.168.245.117", device_list=["1.10", "1.13"])
    start_time = int(time.time() * 1000)
    # ... run your test here ...
    analysis.populate_device_lookups()
    local_dict = analysis.create_local_dict()
    stats = analysis.get_client_connectivity_stats_from_timestamp(start_time, None, local_dict)

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

    @staticmethod
    def keyed(entries: List[dict]) -> List[dict]:
        """Re-wrap normalized entries as '[{"<resource>.<time-stamp>": entry}, ...]'.

        Args:
            entries: normalized wifi-msg dicts (as returned by last()/since()/between()/etc.).

        Some callers (e.g. per-device connectivity analysis) index a batch of messages by a
        '<resource>.<time-stamp>' key rather than working off the flat entry list normalize_messages()
        returns. This produces that shape from the same normalized entries, so callers needing it
        don't have to re-implement their own '/wifi-msgs' fetching/retry logic to get it.
        """
        keyed_entries = []
        for entry in entries:
            resource = entry.get("resource", "")
            ts = entry.get("time-stamp", entry.get("timestamp", ""))
            keyed_entries.append({"{}.{}".format(resource, ts): entry})
        return keyed_entries

    def since_keyed(self, timestamp: int) -> List[dict]:
        """Like since(), but each entry is wrapped '{"<resource>.<time-stamp>": entry}'.

        Args:
            timestamp: LANforge epoch-ms time-stamp.
        """
        return self.keyed(self.since(timestamp))

    def between_keyed(self, start: int, end: int) -> List[dict]:
        """Like between(), but each entry is wrapped '{"<resource>.<time-stamp>": entry}'.

        Args:
            start: window start, LANforge epoch-ms time-stamp.
            end: window end, LANforge epoch-ms time-stamp.
        """
        return self.keyed(self.between(start, end))

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


class RealClientAnalysis(Realm):
    """Checks how well each real client device connected to Wi-Fi: how many times it
    disconnected, scanned, tried to connect, got rejected, or connected successfully.

    It works out these counts by reading LANforge's wifi message log (via WifiMessages)
    and figuring out which devices exist (via DeviceConfig).
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

    def create_local_dict(self) -> dict:
        """Creates an empty counters entry for each device to analyze, ready for
        get_time_from_wifi_msgs() to fill in.

        Looks for devices in two places: Android phones from /adb/, and laptops already
        found by populate_device_lookups(). Each entry is keyed by its LANforge port name.

        Returns:
            dict: one empty counters entry per device to analyze.
        """
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

    def display_available_devices(self, all_devices: List[dict]):
        """Builds a simple table of the devices found, showing each one's resource ID,
        name, and operating system, so it can be shown to the user.

        Args:
            all_devices (list): the discovered device dicts to show (each with 'shelf',
                'resource', 'type', and either 'hostname' or 'serial').

        Returns:
            DataFrame: one row per device, with 'Res_Id/serial' and 'OS' columns.
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
                "Res_Id/serial": "{} / {}".format(res_id, dev_name),
                "OS": os_type,
            })
        return pd.DataFrame(rows)

    def filter_device_list(self, dev_list: List[str], res_to_name: dict):
        """Checks each resource ID the user asked for against the devices LANforge actually has.

        Args:
            dev_list (list): the resource IDs the user asked for (e.g. ['1.10', '1.13']).
            res_to_name (dict): lookup of known resource ID -> device name, from populate_device_lookups().

        Returns:
            tuple: (final_dev_list, remarks_df) -- the list of valid, unique devices, and a
                table explaining what happened to each one (found, not found, or a duplicate).
        """
        final_dev_list = []
        final_df = pd.DataFrame(columns=['Res_Id/serial', 'remarks'])

        for dev in dev_list:
            dev_str = "{} / {}".format(dev, res_to_name.get(dev, None))

            if dev not in res_to_name.keys():
                logger.warning("The device %s is not found in LANforge.", dev)
                final_df = pd.concat([
                    final_df,
                    pd.DataFrame([[dev_str, 'Not found in LANforge']], columns=['Res_Id/serial', 'remarks'])
                ], ignore_index=True)
            elif dev in final_dev_list:
                msg = "The device {} is duplicated in the provided device list".format(dev)
                logger.warning(msg)
                final_df = pd.concat([
                    final_df,
                    pd.DataFrame([[dev_str, msg]], columns=['Res_Id/serial', 'remarks'])
                ], ignore_index=True)
            else:
                final_dev_list.append(dev)
                final_df = pd.concat([
                    final_df,
                    pd.DataFrame([[dev_str, 'Found in LANforge']], columns=['Res_Id/serial', 'remarks'])
                ], ignore_index=True)

        return final_dev_list, final_df

    @staticmethod
    def create_log_file(json_list, file_name: str = "empty.json") -> None:
        """Saves json_list as a JSON file inside the Wifi_Messages folder, creating that
        folder first if it doesn't already exist.

        Args:
            json_list: the data to save -- anything json.dumps() can serialize.
            file_name (str): the file name to save it under, inside Wifi_Messages/.

        Returns:
            None
        """
        json_string = json.dumps(json_list)
        new_folder = "Wifi_Messages"
        if not (os.path.exists(new_folder) and os.path.isdir(new_folder)):
            os.makedirs(new_folder)
        with open(os.path.join(new_folder, file_name), 'w') as file:
            file.write(json_string)

    def collect_matches(self, value=None, keys_list=None, device=None, filter=None) -> List[dict]:
        """Looks through one device's wifi messages and finds every one matching a given
        keyword, like 'disconnected' or 'connected'.

        Args:
            value (list): the wifi messages to search, e.g. from WifiMessages.since_keyed()/between_keyed().
            keys_list (list): the keys of 'value', in the same order (one per message).
            device (str): the LANforge port name (e.g. '1.10.wlan0') to look for messages about.
            filter (str): the keyword (or phrase) that marks the event being searched for.

        Returns:
            list: each match as a {'timestamp', 'text'} dict, in the order they were found.
        """
        matches = []
        device_split = device.split(".")
        device = device_split[2]
        resource_id = device_split[0] + "." + device_split[1]
        for i, y in zip(keys_list, range(len(keys_list))):
            wifi_msg_text = value[y][i]['text']
            resource = value[y][i]['resource']
            time_stamp = value[y][i]['time-stamp']
            if type(wifi_msg_text) is str:
                wifi_msg_text_keyword_list = value[y][i]['text'].split(" ")
                if device is None:
                    continue
                if resource != resource_id:
                    continue
                flag = any(device in msg for msg in wifi_msg_text_keyword_list)
                if flag:
                    if filter in wifi_msg_text_keyword_list:
                        matches.append({"timestamp": time_stamp, "text": wifi_msg_text})
                    else:
                        with_empty_filter = filter.split(" ")
                        if all(item in wifi_msg_text_keyword_list for item in with_empty_filter):
                            matches.append({"timestamp": time_stamp, "text": wifi_msg_text})
                else:
                    if "IFNAME={}".format(device) in wifi_msg_text_keyword_list:  # for linux
                        if filter in wifi_msg_text_keyword_list:
                            matches.append({"timestamp": time_stamp, "text": wifi_msg_text})
                        else:
                            with_empty_filter = filter.split(" ")
                            if all(item in wifi_msg_text_keyword_list for item in with_empty_filter):
                                matches.append({"timestamp": time_stamp, "text": wifi_msg_text})
            else:  # wifi_msg_text is a list
                for item in wifi_msg_text:
                    wifi_msg_text_keyword_list = item.split(" ")
                    if device is None or resource != resource_id:
                        continue
                    if device in wifi_msg_text_keyword_list:  # for android
                        if filter in wifi_msg_text_keyword_list:
                            matches.append({"timestamp": time_stamp, "text": item})
                        else:
                            with_empty_filter = filter.split(" ")
                            if all(item_ in wifi_msg_text_keyword_list for item_ in with_empty_filter):
                                matches.append({"timestamp": time_stamp, "text": item})
                    else:
                        if "IFNAME={}".format(device) in wifi_msg_text_keyword_list:  # for linux
                            if filter in wifi_msg_text_keyword_list:
                                matches.append({"timestamp": time_stamp, "text": item})
                            else:
                                with_empty_filter = filter.split(" ")
                                if all(item_ in wifi_msg_text_keyword_list for item_ in with_empty_filter):
                                    matches.append({"timestamp": time_stamp, "text": item})
        return matches

    def get_count(self, value=None, keys_list=None, device=None, filter=None) -> int:
        """Returns how many wifi messages matched -- see collect_matches() for the rules;
        this just counts them instead of returning them.

        Args:
            value (list): the wifi messages to search.
            keys_list (list): the keys of 'value', in the same order (one per message).
            device (str): the LANforge port name (e.g. '1.10.wlan0') to look for messages about.
            filter (str): the keyword (or phrase) that marks the event being counted.

        Returns:
            int: how many messages matched.
        """
        return len(self.collect_matches(value=value, keys_list=keys_list, device=device, filter=filter))

    def get_time_from_wifi_msgs(self, local_dict=None, phn_name=None, start_time=None,
                                end_time=None, reset_cnt=None) -> dict:
        """Works out one device's connect/disconnect/scan/rejection counts from its wifi
        messages, and saves the matching messages into self.device_messages[phn_name] as proof.

        Args:
            local_dict (dict): the per-device counter dict to fill in, from create_local_dict().
            phn_name (str): the LANforge port name of the device to analyze (e.g. '1.10.wlan0').
            start_time (int): epoch-ms time-stamp to start counting wifi messages from.
            end_time (int): epoch-ms time-stamp to stop counting at, or None to count up to now.
            reset_cnt: unused.

        Returns:
            dict: local_dict, with phn_name's counters filled in.
        """
        if start_time and end_time:
            values = self.wifi_msgs.between_keyed(start_time, end_time)
        else:
            values = self.wifi_msgs.since_keyed(start_time)
        logger.debug("Counting DISCONNECTIONS/SCANNING/ASSOC ATTEMPTS/ASSOC REJECTIONS/CONNECTS for device %s", phn_name)
        keys_list = [list(v.keys())[0] for v in values]
        device_messages = {"Disconnected": [], "Scanning": [], "ConnectAttempt": [],
                           "Association Rejection": [], "Connected": []}

        android = False
        adb_devices = self.json_get('/adb/')['devices']
        single_device = isinstance(adb_devices, dict)
        if single_device:
            adb_devices = [adb_devices]
        for device_data in adb_devices:
            device_name = device_data.get("name") if single_device else list(device_data.keys())[0]
            if phn_name in device_name:
                android = True
                break

        if android:
            device_messages["Disconnected"] = self.collect_matches(value=values, keys_list=keys_list, device=phn_name,
                                                                   filter="Terminating...")
            adb_disconnect_count = len(device_messages["Disconnected"])
            local_dict[phn_name]["Disconnected"] = adb_disconnect_count
            device_messages["Scanning"] = self.collect_matches(value=values, keys_list=keys_list, device=phn_name,
                                                               filter="SCAN-STARTED")
            local_dict[str(phn_name)]["Scanning"] = len(device_messages["Scanning"])
            device_messages["ConnectAttempt"] = self.collect_matches(value=values, keys_list=keys_list, device=phn_name,
                                                                     filter="Trying to associate with")
            adb_association_attempt = len(device_messages["ConnectAttempt"])
            local_dict[str(phn_name)]["ConnectAttempt"] = adb_association_attempt
            device_messages["Association Rejection"] = self.collect_matches(value=values, keys_list=keys_list,
                                                                            device=phn_name, filter="ASSOC_REJECT")
            adb_association_rejection = len(device_messages["Association Rejection"])
            local_dict[str(phn_name)]["Association Rejection"] = adb_association_rejection
            device_messages["Connected"] = self.collect_matches(value=values, keys_list=keys_list, device=phn_name,
                                                                filter="CTRL-EVENT-CONNECTED")
            adb_connected_count = len(device_messages["Connected"])
            local_dict[str(phn_name)]["Connected"] = adb_connected_count
            local_dict[str(phn_name)]["Remarks"] = "NA"
            if adb_association_attempt > adb_connected_count:
                adb_association_rejection = adb_association_attempt - adb_connected_count
            local_dict[str(phn_name)]["Association Rejection"] = adb_association_rejection
            if adb_connected_count > 0:
                _, shelf, serial = phn_name.split('.')
                resource_id = self.json_get('/adb/1/{}/{}?fields=resource-id'.format(shelf, serial))
                resource_id = resource_id['devices']['resource-id']
                port_ssid_query = self.json_get('port/1/{}/wlan0?fields=cx time (us)'.format(resource_id.split('.')[1]))
                local_dict[str(phn_name)]['cx time (us)'] = port_ssid_query['interface']['cx time (us)']
            else:
                local_dict[str(phn_name)]['cx time (us)'] = 'NA'
        else:
            if phn_name in self.windows_list:  # for windows
                device_messages["Disconnected"] = self.collect_matches(value=values, keys_list=keys_list, device=phn_name,
                                                                       filter="Wireless security stopped.")
                if not device_messages["Disconnected"]:
                    device_messages["Disconnected"] = self.collect_matches(
                        value=values, keys_list=keys_list, device=phn_name,
                        filter="WLAN AutoConfig service has successfully disconnected from a wireless network")
                win_disconnect_count = len(device_messages["Disconnected"])
                local_dict[phn_name]["Disconnected"] = win_disconnect_count
                device_messages["Scanning"] = self.collect_matches(value=values, keys_list=keys_list, device=phn_name,
                                                                   filter="service started")
                win_scan_count = len(device_messages["Scanning"])
                local_dict[str(phn_name)]["Scanning"] = win_scan_count
                device_messages["ConnectAttempt"] = self.collect_matches(value=values, keys_list=keys_list, device=phn_name,
                                                                         filter="association started.")
                win_association_attempt = len(device_messages["ConnectAttempt"])
                local_dict[str(phn_name)]["ConnectAttempt"] = win_association_attempt
                device_messages["Association Rejection"] = self.collect_matches(value=values, keys_list=keys_list,
                                                                                device=phn_name, filter="failed to connect")
                win_association_rejection = len(device_messages["Association Rejection"])
                local_dict[str(phn_name)]["Association Rejection"] = win_association_rejection
                device_messages["Connected"] = self.collect_matches(value=values, keys_list=keys_list, device=phn_name,
                                                                    filter="connected")
                win_connected_count = len(device_messages["Connected"])
                if win_association_rejection:
                    actual_connects = win_association_attempt - win_association_rejection
                    win_connected_count = win_connected_count if actual_connects == win_connected_count else actual_connects
                local_dict[str(phn_name)]["Connected"] = win_connected_count
                if win_association_attempt > win_connected_count:
                    win_association_rejection = win_association_attempt - win_connected_count
                local_dict[str(phn_name)]["Association Rejection"] = win_association_rejection
                remarks = "NA"
                if win_disconnect_count == 0 and win_connected_count == 1:
                    remarks = "No Disconnections are seen but Client is UP and connected to user given SSID."
                elif win_disconnect_count >= 1 and win_connected_count == 0:
                    remarks = "The Disconnections are seen but Client did not connected to user given SSID."
                local_dict[str(phn_name)]["Remarks"] = remarks
                if win_connected_count > 0:
                    port_name = phn_name.split(".")
                    port_ssid_query = self.json_get(
                        "port/{}/{}/{}?fields=cx time (us)".format(port_name[0], port_name[1], port_name[2]))
                    local_dict[str(phn_name)]['cx time (us)'] = port_ssid_query['interface']['cx time (us)']
                else:
                    local_dict[str(phn_name)]['cx time (us)'] = 'NA'
            else:  # linux, mac
                device_messages["Disconnected"] = self.collect_matches(value=values, keys_list=keys_list, device=phn_name,
                                                                       filter="disconnected")
                if not device_messages["Disconnected"]:
                    device_messages["Disconnected"] = self.collect_matches(value=values, keys_list=keys_list, device=phn_name,
                                                                           filter="<3>CTRL-EVENT-DSCP-POLICY clear_all")
                other_disconnect_count = len(device_messages["Disconnected"])
                local_dict[phn_name]["Disconnected"] = other_disconnect_count
                device_messages["Scanning"] = self.collect_matches(value=values, keys_list=keys_list, device=phn_name,
                                                                   filter="<3>CTRL-EVENT-SCAN-STARTED")
                other_scan_count = len(device_messages["Scanning"])
                local_dict[str(phn_name)]["Scanning"] = other_scan_count
                device_messages["ConnectAttempt"] = self.collect_matches(value=values, keys_list=keys_list, device=phn_name,
                                                                         filter="<3>Trying to associate with")
                other_association_attempt = len(device_messages["ConnectAttempt"])
                local_dict[str(phn_name)]["ConnectAttempt"] = other_association_attempt
                device_messages["Association Rejection"] = self.collect_matches(value=values, keys_list=keys_list,
                                                                                device=phn_name, filter="NoneValue")
                other_association_rejection = len(device_messages["Association Rejection"])
                local_dict[str(phn_name)]["Association Rejection"] = other_association_rejection
                device_messages["Connected"] = self.collect_matches(value=values, keys_list=keys_list, device=phn_name,
                                                                    filter="<3>CTRL-EVENT-CONNECTED")
                if not device_messages["Connected"]:
                    # macOS reports connects as "en0: STA is connected to a wireless network."
                    device_messages["Connected"] = self.collect_matches(value=values, keys_list=keys_list, device=phn_name,
                                                                        filter="STA is connected")
                other_connected_count = len(device_messages["Connected"])
                if other_association_rejection:
                    actual_connects = other_association_attempt - other_association_rejection
                    other_connected_count = other_connected_count if actual_connects == other_connected_count else actual_connects
                local_dict[str(phn_name)]["Connected"] = other_connected_count
                if other_association_attempt > other_connected_count:
                    other_association_rejection = other_association_attempt - other_connected_count
                local_dict[str(phn_name)]["Association Rejection"] = other_association_rejection
                remarks = "NA"
                if other_disconnect_count == 0 and other_connected_count == 1:
                    remarks = "No Disconnections are seen but Client is UP and connected to user given SSID."
                elif other_disconnect_count >= 1 and other_connected_count == 0:
                    remarks = "The Disconnections are seen but Client did not connected to user given SSID."
                local_dict[str(phn_name)]["Remarks"] = remarks
                if other_connected_count > 0:
                    port_name = phn_name.split(".")
                    port_ssid_query = self.json_get(
                        "port/{}/{}/{}?fields=cx time (us)".format(port_name[0], port_name[1], port_name[2]))
                    local_dict[str(phn_name)]['cx time (us)'] = port_ssid_query['interface']['cx time (us)']
                else:
                    local_dict[str(phn_name)]['cx time (us)'] = 'NA'

        self.device_messages[phn_name] = device_messages
        return local_dict

    def get_client_connectivity_stats_from_timestamp(self, start_time, end_time, local_dict: dict) -> dict:
        """Works out the connectivity counts for every device in local_dict, then saves all
        of their matched messages in one file (Wifi_Messages/<date>_<time>.json), keyed by
        device name, as proof of how the counts were worked out.

        Args:
            start_time (int): epoch-ms time-stamp to start counting wifi messages from.
            end_time (int): epoch-ms time-stamp to stop counting at, or None to count up to now.
            local_dict (dict): the per-device counter dict to fill in, from create_local_dict().

        Returns:
            dict: local_dict, with every device's counters filled in.
        """
        for phn_name in local_dict.keys():
            local_dict = self.get_time_from_wifi_msgs(local_dict=local_dict, phn_name=phn_name,
                                                      start_time=start_time, end_time=end_time)
        file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
        self.create_log_file(json_list=self.device_messages, file_name=file_name)
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

    def populate_device_lookups(self) -> None:
        """Finds every device LANforge knows about and sorts them into lookup lists
        (self.resource_id_list, self.windows_list, self.resource_id_to_abs).

        If self.device_list was already given, this just checks it against those lookups.
        If it was left empty, it shows the user what devices are available and asks them to
        pick which ones (or 'all') to analyze -- the answer is saved into self.device_list so
        create_local_dict() can use it as usual.

        Returns:
            None
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

        available_df = self.display_available_devices(filtered_all_devices)
        logger.info("%s", available_df.to_string(index=False))

        dev_list = input("Enter the desired resource IDs to run the test (e.g. '1.10'): ").split(',')
        if "all" in dev_list:
            dev_list = dev_list_all.copy()

        res_to_name = {}
        for device in filtered_all_devices:
            if device["type"] == 'laptop':
                res_to_name[device["shelf"] + '.' + device["resource"]] = device["hostname"]
            else:  # adb
                res_to_name[device["eid"]] = device["serial"]

        self.device_list, remarks_df = self.filter_device_list(dev_list, res_to_name)
        logger.info("%s", remarks_df.to_string(index=False))

    @staticmethod
    def dicttolist(client_connectivity_stats: dict):
        """Turns the per-device stats dict into separate lists (one per column: devices,
        ConnectAttempt, Disconnected, Scanning, Association Rejection, Connected, Remarks,
        cx_time), so they're easy to print as a table.

        Args:
            client_connectivity_stats (dict): the per-device stats dict, from
                get_client_connectivity_stats_from_timestamp().

        Returns:
            tuple: (devices, connect_attempt, disconnected, scanning, association_rejection,
                connected, remarks, cx_time) -- one parallel list per column.
        """
        devices, connect_attempt, disconnected, scanning = [], [], [], []
        association_rejection, connected, remarks, cx_time = [], [], [], []
        for i in client_connectivity_stats.keys():
            connect_attempt.append(client_connectivity_stats[i]["ConnectAttempt"])
            disconnected.append(client_connectivity_stats[i]["Disconnected"])
            scanning.append(client_connectivity_stats[i]["Scanning"])
            association_rejection.append(client_connectivity_stats[i]["Association Rejection"])
            connected.append(client_connectivity_stats[i]["Connected"])
            remarks.append(client_connectivity_stats[i]["Remarks"])
            cx_time.append(client_connectivity_stats[i]["cx time (us)"])
            devices.append(client_connectivity_stats[i]["port_name"])
        return devices, connect_attempt, disconnected, scanning, association_rejection, connected, remarks, cx_time


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
    mode.add_argument('--analyze_real_clients', action='store_true',
                      help='per-real-client connect/disconnect/scan/rejection stats '
                           '(RealClientAnalysis) instead of raw wifi-msgs')
    wifi_msgs_args.add_argument('--interval', default='5s', metavar='WINDOW',
                                help='--poll interval (e.g. 2s, 500ms; default: 5s)')
    wifi_msgs_args.add_argument('--output', choices=['raw', 'json'], default='raw',
                                help='raw message text lines or json (default: raw)')
    wifi_msgs_args.add_argument('--outfile', metavar='PATH', help='write output to PATH instead of stdout')

    analysis_args = parser.add_argument_group('--analyze_real_clients arguments')
    analysis_args.add_argument('--device_list', default="", metavar='IDS',
                               help="comma-separated resource IDs (e.g. '1.10') to analyze; "
                                    "leave empty to be prompted interactively")
    analysis_args.add_argument('--start_time', metavar='TIMESTAMP',
                               help='epoch-ms time-stamp to start counting wifi-msgs from (required)')
    analysis_args.add_argument('--end_time', metavar='TIMESTAMP',
                               help='epoch-ms time-stamp to stop counting at (default: now)')

    args = parser.parse_args()
    if args.help_summary:
        print(help_summary)
        exit(0)

    if args.analyze_real_clients and not args.start_time:
        parser.error('--start_time is required with --analyze_real_clients')

    try:
        interval = WifiMessages.to_seconds(args.interval)
        duration = WifiMessages.to_seconds(args.duration) if args.duration is not None else None
    except Exception as error:
        parser.error(f"Failed to parse the CLI arguments: {str(error)}")

    logger_config = lf_logger_config.lf_logger_config()
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

    if args.analyze_real_clients:
        analysis = RealClientAnalysis(
            host=args.mgr, port=args.mgr_port,
            device_list=args.device_list.split(',') if args.device_list else [],
            debug=args.debug)
        analysis.populate_device_lookups()  # prompts interactively if --device_list was left empty
        local_dict = analysis.create_local_dict()
        if not local_dict:
            print("None of the given devices resolved to a device LANforge knows about.")
            exit(1)
        stats = analysis.get_client_connectivity_stats_from_timestamp(args.start_time, args.end_time, local_dict)
        (devices, connect_attempt, disconnected, scanning,
         association_rejection, connected, remarks, cx_time) = analysis.dicttolist(stats)
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
