#!/usr/bin/env python3
"""
NAME: lf_wifi_msgs.py

PURPOSE:
        Pull LANforge Wi-Fi messages from the GUI REST API (``/wifi-msgs``).

        Two entry points:

          1. Importable API -- ``WifiMsgClient``. Construct it from a Realm-derived
             object (pass ``self`` from a test) or a host/port via ``from_host()``.
             Query methods return ``list[WifiMessage]`` (``.text``, ``.timestamp_ms``,
             ``.resource``, ``.raw``).

          2. CLI query modes:
               --last N            most recent N messages
               --first N           oldest N messages still buffered
               --since TS          everything since a LANforge epoch-ms stamp
               --duration 30s|5m   everything from the last <window>
               --between A B        everything between two epoch-ms stamps
               --poll [--interval] keep printing new messages as they arrive

EXAMPLE (CLI):
        python3 lf_wifi_msgs.py --mgr 192.168.1.31 --last 50
        python3 lf_wifi_msgs.py --mgr 192.168.1.31 --duration 5m --output json --outfile msgs.json
        python3 lf_wifi_msgs.py --mgr 192.168.1.31 --since 1699999999999 --output json
        python3 lf_wifi_msgs.py --mgr 192.168.1.31 --between 1788159332090 1788161286054
        python3 lf_wifi_msgs.py --mgr 192.168.1.31 --poll --interval 2s

EXAMPLE (module):
        from lf_wifi_msgs import WifiMsgClient

        client = WifiMsgClient.from_host("192.168.1.31")   # or WifiMsgClient(self) in a test
        for msg in client.last(50):
            print(msg.timestamp_ms, msg.resource, msg.text)

        client.since_duration(300)          # last 5 minutes
        client.between(start_ms, end_ms)

        for msg in client.poll(interval=2): # tail; stop with break / client.stop_polling()
            handle(msg)

SCRIPT_CLASSIFICATION: Wi-Fi Messages

SCRIPT_CATEGORIES: Functional

NOTES:
        LANforge time-stamps are epoch milliseconds. --since / --between values are
        sent through unchanged; --duration is computed off the newest message.

STATUS: Functional

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright (C) 2020-2026 Candela Technologies Inc

INCLUDE_IN_README: False
"""

import argparse
import importlib
import json
import logging
import os
import re
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    sys.exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

realm = importlib.import_module("py-json.realm")
Realm = realm.Realm
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")

HELP_SUMMARY = (
    "Fetch LANforge Wi-Fi messages from the /wifi-msgs REST API: last/first N, since a "
    "time-stamp, from the last <duration>, between two stamps, or poll for new ones. "
    "Importable as WifiMsgClient."
)

# Retry when a single /wifi-msgs GET comes back empty.
DEFAULT_WIFI_MSGS_RETRY_TIMEOUT = 40    # give up after this many seconds
DEFAULT_WIFI_MSGS_RETRY_INTERVAL = 5    # wait this long between tries

# Gap between polls in WifiMsgClient.poll().
DEFAULT_WIFI_MSGS_POLL_INTERVAL = 5

_DURATION_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(ms|s|m|h|d)?\s*$", re.IGNORECASE)
_DURATION_UNIT_SECONDS = {"ms": 0.001, "s": 1, "m": 60, "h": 3600, "d": 86400}


def parse_duration(text: str) -> float:
    """'30s' / '5m' / '2h' / '500ms' / bare number (seconds) -> float seconds."""
    match = _DURATION_RE.match(str(text))
    if not match:
        raise argparse.ArgumentTypeError(
            f"invalid duration {text!r}; use e.g. 30s, 5m, 2h, 500ms or a bare number of seconds"
        )
    value, unit = match.group(1), (match.group(2) or "s").lower()
    return float(value) * _DURATION_UNIT_SECONDS[unit]


def parse_between(tokens) -> Tuple[int, int]:
    """Two epoch-ms stamps ('A B', 'A,B', or 'A, B') -> ordered (start, end) ints.

    Reversed input is swapped (with a warning). Raises argparse.ArgumentTypeError
    if there are not exactly two integer parts.
    """
    if isinstance(tokens, str):
        tokens = [tokens]
    parts = [p for p in re.split(r"[,\s]+", " ".join(tokens).strip()) if p]
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(
            f"--between needs exactly two epoch-ms time-stamps (got {len(parts)}: {parts}); "
            "e.g. --between 1788157373678 1788157422997  or  --between 1788157373678,1788157422997"
        )
    try:
        start, end = int(parts[0]), int(parts[1])
    except ValueError:
        raise argparse.ArgumentTypeError(f"--between time-stamps must be integers (epoch-ms); got {parts}")
    if start > end:
        logger.warning("--between start %d is after end %d; swapping", start, end)
        start, end = end, start
    return start, end


@dataclass
class WifiMessage:
    """One /wifi-msgs entry, normalised into a stable shape."""

    timestamp: Optional[str]                # epoch-ms string as reported by LANforge, or None
    resource: Optional[str]                 # 'shelf.resource', e.g. '1.1'
    text: List[str] = field(default_factory=list)   # always a list of lines
    key: Optional[str] = None               # '<resource>.<timestamp>' wrapper key, if the response had one
    raw: dict = field(default_factory=dict)  # untouched original entry

    @classmethod
    def from_entry(cls, key: Optional[str], entry: dict) -> "WifiMessage":
        """Build a WifiMessage from one raw entry dict. ``text`` is converted to a list; missing fields
        become ``[]`` / ``None``. ``key`` is the wrapper string (``None`` for a bare entry)."""
        text = entry.get("text", [])
        if isinstance(text, str):
            text = [text]
        elif isinstance(text, (list, tuple)):
            text = [str(line) for line in text]
        else:
            text = [str(text)]
        return cls(
            timestamp=entry.get("time-stamp", entry.get("timestamp")),
            resource=entry.get("resource"),
            text=list(text),
            key=key,
            raw=entry,
        )

    @property
    def timestamp_ms(self) -> Optional[int]:
        """``timestamp`` as an int, or ``None`` if it is missing/non-numeric."""
        try:
            return int(str(self.timestamp).strip())
        except (TypeError, ValueError):
            return None


def normalize(raw: Optional[dict]) -> List[WifiMessage]:
    """Flatten a raw /wifi-msgs response into a list of WifiMessage.

    Handles the shapes LANforge returns:
      * None / no 'wifi-messages' key              -> []
      * {'wifi-messages': {<entry>}}               -> 1   (last/1)
      * {'wifi-messages': {'<key>': {<entry>}}}    -> 1
      * {'wifi-messages': [ {'<key>': {<entry>}} ]} -> N   (last/N, since=time, ...)
      * {'wifi-messages': [ {<entry>} ]}           -> N   (defensive)

    '<key>' is the '<resource>.<time-stamp>' wrapper; a bare entry gets key=None.
    """
    if not raw:
        return []
    messages = raw.get("wifi-messages")
    if messages is None:
        return []

    def is_valid_entry(obj) -> bool:
        # An entry has text/stamp of its own; a wrapper is just {'<key>': {<entry>}}.
        return isinstance(obj, dict) and ("text" in obj or "time-stamp" in obj or "timestamp" in obj)

    out: List[WifiMessage] = []
    if isinstance(messages, dict):
        if is_valid_entry(messages):
            out.append(WifiMessage.from_entry(None, messages))
        else:
            for key, entry in messages.items():
                if isinstance(entry, dict):
                    out.append(WifiMessage.from_entry(key, entry))
        return out

    for item in messages:
        if not isinstance(item, dict):
            continue
        if is_valid_entry(item):
            out.append(WifiMessage.from_entry(None, item))
        else:
            for key, entry in item.items():
                if isinstance(entry, dict):
                    out.append(WifiMessage.from_entry(key, entry))
    return out


class WifiMsgClient:
    """Thin client over the LANforge ``/wifi-msgs`` REST endpoints.

        client = WifiMsgClient(self)                  # inside a Realm-derived test
        client = WifiMsgClient.from_host("host")      # standalone

    The session only needs a ``json_get(uri, debug_=...)`` method.
    """

    def __init__(self, session,
                 retry_timeout: float = DEFAULT_WIFI_MSGS_RETRY_TIMEOUT,
                 retry_interval: float = DEFAULT_WIFI_MSGS_RETRY_INTERVAL,
                 debug: bool = False):
        if not hasattr(session, "json_get"):
            raise TypeError("session must provide a json_get(uri, debug_=...) method")
        self.session = session
        self.retry_timeout = retry_timeout
        self.retry_interval = retry_interval
        self.debug = debug
        self._poll_stop = threading.Event()   # set by stop_polling(), watched by poll()

    @classmethod
    def from_host(cls, host: str, port: int = 8080, debug: bool = False, **kwargs) -> "WifiMsgClient":
        session = Realm(lfclient_host=host, lfclient_port=int(port), debug_=debug)
        return cls(session, debug=debug, **kwargs)

    def _query(self, uri: str) -> Optional[dict]:
        """GET ``uri``, retrying while the response is None up to ``retry_timeout``."""
        start = time.time()
        response = self.session.json_get(uri, debug_=self.debug)
        while response is None and (time.time() - start) < self.retry_timeout:
            logger.warning("GET %s returned no response from LANforge; retrying...", uri)
            time.sleep(self.retry_interval)
            response = self.session.json_get(uri, debug_=self.debug)
        if response is None:
            logger.error("GET %s returned no response after %ss", uri, self.retry_timeout)
        return response

    def query(self, uri: str) -> List[WifiMessage]:
        return normalize(self._query(uri))

    def last(self, count: int = 1) -> List[WifiMessage]:
        return self.query(f"/wifi-msgs/last/{int(count)}")

    def first(self, count: int = 1) -> List[WifiMessage]:
        return self.query(f"/wifi-msgs/first/{int(count)}")

    def latest(self) -> Optional[WifiMessage]:
        msgs = self.last(1)
        return msgs[-1] if msgs else None

    def since(self, timestamp) -> List[WifiMessage]:
        return self.query(f"/wifi-msgs/since=time/{timestamp}")

    def between(self, start, end) -> List[WifiMessage]:
        return self.query(f"/wifi-msgs/between=time/{start}/{end}")

    def since_duration(self, seconds: float) -> List[WifiMessage]:
        """Messages from the last ``seconds``: newest message's stamp minus the
        window, via ``since=time``. Falls back to ``last=time`` with no baseline."""
        window_ms = int(float(seconds) * 1000)
        newest = self.latest()
        base_ms = newest.timestamp_ms if newest else None
        if base_ms is None:
            logger.warning("No epoch-ms wifi-msg baseline available; using /wifi-msgs/last=time")
            return self.query(f"/wifi-msgs/last=time/{window_ms}")
        return self.since(base_ms - window_ms)

    def stop_polling(self) -> None:
        """Tell a running :method:`poll` to end. Safe from another thread, the loop
        body, or a signal handler. Cleared on the next :method:`poll` entry."""
        self._poll_stop.set()

    def poll(self, interval: float = DEFAULT_WIFI_MSGS_POLL_INTERVAL,
             since_ts: Optional[int] = None,
             stop=None,
             max_seconds: Optional[float] = None):
        """Poll /wifi-msgs and yield each new WifiMessage as it appears.

        Open-ended generator; Stop it with ``break``, :method:`stop_polling`,
        a ``stop`` predicate, or ``max_seconds``.

        ``since_ts`` is the epoch-ms cursor; the first message yielded is the next
        one strictly after it. Default: the newest message at entry, so only new
        traffic is yielded (0 if the buffer is empty).
        """
        self._poll_stop.clear()
        if since_ts is None:
            newest = self.latest()
            since_ts = newest.timestamp_ms if newest else 0
        cursor = int(since_ts)
        deadline = time.time() + max_seconds if max_seconds else None

        while not self._poll_stop.is_set() and not (stop and stop()):
            if deadline and time.time() >= deadline:
                return
            batch = self.since(cursor + 1)   # +1: since=time is inclusive
            for msg in sorted(batch, key=lambda m: m.timestamp_ms or 0):
                yield msg
                if msg.timestamp_ms:
                    cursor = max(cursor, msg.timestamp_ms)
            if self._poll_stop.wait(interval):
                return


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------
def render_raw(messages: List[WifiMessage], stream) -> None:
    """The message text lines, nothing else."""
    for msg in messages:
        for line in msg.text:
            stream.write(line + "\n")


def render_json(messages: List[WifiMessage], stream) -> None:
    """A JSON array of the untouched /wifi-msgs entries (each message's ``.raw``)."""
    json.dump([msg.raw for msg in messages], stream, indent=2)
    stream.write("\n")


RENDERERS = {"raw": render_raw, "json": render_json}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=__file__,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    conn = parser.add_argument_group("connection")
    conn.add_argument("--mgr", "--host", dest="mgr", default="localhost",
                      help="LANforge GUI host/IP (default: localhost)")
    conn.add_argument("--mgr_port", "--port", dest="mgr_port", type=int, default=8080,
                      help="LANforge GUI port (default: 8080)")

    mode = parser.add_argument_group("query mode (choose one; default: --last 25)")
    mx = mode.add_mutually_exclusive_group()
    mx.add_argument("--last", type=int, metavar="N",
                    help="the most recent N messages")
    mx.add_argument("--first", type=int, metavar="N",
                    help="the oldest N messages still buffered")
    mx.add_argument("--since", metavar="TIMESTAMP",
                    help="every message since a LANforge epoch-ms time-stamp")
    mx.add_argument("--duration", type=parse_duration, metavar="WINDOW",
                    help="every message from the last WINDOW (e.g. 30s, 5m, 2h, 500ms)")
    mx.add_argument("--between", nargs="+", metavar="START END",
                    help="every message between two epoch-ms stamps ('A B' or 'A,B')")
    mx.add_argument("--poll", "-p", action="store_true",
                    help="print new messages as they arrive, from now on (Ctrl-C to stop)")

    out = parser.add_argument_group("output")
    out.add_argument("--output", choices=sorted(RENDERERS), default="raw",
                     help="raw (message text lines) or json (default: raw)")
    out.add_argument("--outfile", metavar="PATH",
                     help="write output to PATH instead of stdout")
    out.add_argument("--interval", type=parse_duration, default=DEFAULT_WIFI_MSGS_POLL_INTERVAL,
                     metavar="WINDOW", help="--poll interval (e.g. 2s, 500ms; default: 5s)")

    log = parser.add_argument_group("logging")
    log.add_argument("--log_level", default=None,
                     help="debug | info | warning | error | critical")
    log.add_argument("--lf_logger_config_json", help="path to a lf_logger JSON config")
    log.add_argument("--debug", action="store_true", help="verbose LANforge request logging")
    parser.add_argument("--help_summary", action="store_true", help="print a one-paragraph summary and exit")
    return parser


def fetch_messages(client: WifiMsgClient, args) -> List[WifiMessage]:
    """Run the one query mode selected on the command line and return its messages.

    Checks --since / --duration / --between / --first / --last in order; with none
    given, defaults to the last 25. (--poll is handled separately.)
    """
    if args.since is not None:
        return client.since(args.since)
    if args.duration is not None:
        return client.since_duration(args.duration)
    if args.between is not None:
        start, end = parse_between(args.between)
        return client.between(start, end)
    if args.first is not None:
        return client.first(args.first)
    return client.last(args.last if args.last is not None else 25)


def main(argv=None) -> int:
    """CLI entry point. Parses ``argv`` (defaults to ``sys.argv``), then either
    polls (--poll) or runs one query, rendering to stdout or --outfile."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.help_summary:
        print(HELP_SUMMARY)
        return 0

    if args.between is not None:
        try:
            parse_between(args.between)   # validate early: bad input prints usage, not a traceback
        except argparse.ArgumentTypeError as exc:
            parser.error(str(exc))

    logger_config = lf_logger_config.lf_logger_config()
    if args.log_level:
        logger_config.set_level(level=args.log_level)
    elif args.debug:
        logger_config.set_level(level="debug")
    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()

    client = WifiMsgClient.from_host(args.mgr, args.mgr_port, debug=args.debug)
    render = RENDERERS[args.output]

    out_stream = open(args.outfile, "w", newline="") if args.outfile else sys.stdout
    try:
        if args.poll:
            logger.info("polling /wifi-msgs every %ss (Ctrl-C to stop)", args.interval)
            try:
                for msg in client.poll(interval=args.interval):
                    render([msg], out_stream)
                    out_stream.flush()
            except KeyboardInterrupt:
                client.stop_polling()
                logger.info("polling stopped")
        else:
            messages = fetch_messages(client, args)
            logger.info("fetched %d wifi message(s)", len(messages))
            render(messages, out_stream)
        return 0
    finally:
        if out_stream is not sys.stdout:
            out_stream.close()


if __name__ == "__main__":
    sys.exit(main())
