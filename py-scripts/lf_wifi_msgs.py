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
import threading
import logging
from typing import Callable, Iterator, List, Optional

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
    wifi_msgs_args.add_argument('--interval', default='5s', metavar='WINDOW',
                                help='--poll interval (e.g. 2s, 500ms; default: 5s)')
    wifi_msgs_args.add_argument('--output', choices=['raw', 'json'], default='raw',
                                help='raw message text lines or json (default: raw)')
    wifi_msgs_args.add_argument('--outfile', metavar='PATH', help='write output to PATH instead of stdout')

    args = parser.parse_args()
    if args.help_summary:
        print(help_summary)
        exit(0)

    try:
        interval = WifiMessages.to_seconds(args.interval)
        duration = WifiMessages.to_seconds(args.duration) if args.duration is not None else None
    except Exception as error:
        parser.error(f"Failed to parse the CLI arguments: {str(error)}")

    logger_config = lf_logger_config.lf_logger_config()
    logger_config.set_level(level=args.log_level)
    logger_config.set_json(json_file=args.lf_logger_config_json)

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
            wifi_msgs.render(entries, args.output, out_stream)
    finally:
        if out_stream is not sys.stdout:
            out_stream.close()
    exit(0)


if __name__ == "__main__":
    main()
