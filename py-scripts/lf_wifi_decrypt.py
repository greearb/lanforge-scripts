#!/usr/bin/env python3
r"""
NAME:       lf_wifi_decrypt.py

PURPOSE:    Decode a Wi-Fi capture using keys from LANforge Wi-Fi events or
            supplicant logs. Keep keys from multiple stations, reconnects
            and group rekeys, and write brief or verbose TShark text.

EXAMPLE:    # Decode one capture using events from multiple resources
            ./lf_wifi_decrypt.py --pcap capture.pcapng \
                --events resource1.txt --events resource2.txt -o decoded.txt

            # Show only decoded protected data, with packet details
            ./lf_wifi_decrypt.py --pcap capture.pcapng \
                --events wifi_events.txt --mode verbose --decrypted-only \
                -o details.txt

NOTES:      Requires Python 3.8+ and TShark with the "tk" key type.
            Matching TK/GTK values allow decoding without captured EAPOL.
            Keys are tried across the capture, independent of event times.
            The report verifies frames; it does not label reconnect sessions.

            Python callers can import decrypt_capture without running the CLI.
"""

import argparse
import csv
import getpass
import hashlib
import io
import json
import os
import re
import sqlite3
import stat
import subprocess
import sys
import tempfile
from collections import Counter
from contextlib import ExitStack, contextmanager, nullcontext
from pathlib import Path
from urllib.parse import quote


MAX_KEYS_PER_PASS = 64
WORKSPACE_PREFIX = "lf_wifi_decrypt_"
WORKSPACE_MARKER = ".workspace.json"
WORKSPACE_LOCK = ".workspace.lock"
COLUMNS = ('"No.","%m","Time","%t","Source","%s",'
           '"Destination","%d","Protocol","%p","Length","%L","Info","%i"')
EVENT_RECORD = re.compile(r"^wifi_event\s+(\S+)\s+\S+\s+\S+\s+'(.*)'$")
KEY_EVENT = re.compile(r"WPA:\s*(PMK|PTK|TK|GTK)\s+([0-9a-fA-F]+)\s*$")
SCOPE = re.compile(r"(?:(?<![\d.])(\d{1,3}\.\d{1,3}):\s+)?IFNAME=(\S+)")
RAW_SCOPE = re.compile(r"^\d+(?:\.\d+)?:\s+([\w.-]+):\s+")
HEX_EVENT = re.compile(
    r"WPA:\s*(PMK|PTK|TK|GTK)\s+- hexdump\(len=(\d+)\):\s*"
    r"((?:[0-9a-fA-F]{2}\s*)+)$"
)
GTK_EVENT = re.compile(
    r"(?:WPA: GTK in EAPOL-Key|RSN: received GTK in pairwise handshake)"
    r" - hexdump\(len=(\d+)\):\s*((?:[0-9a-fA-F]{2}\s*)+)$"
)
SCAN_FIELDS = ("frame.number", "frame.protocols", "wlan.fc.protected",
               "wlan.fc.type", "wlan.ra")


def parse_event_lines(lines, interfaces=(), resources=()):
    """Return unique TK/GTK values, PMKs and warnings from an event iterator.

    Scope PTK parsing by resource/interface so interleaved stations do not
    overwrite each other's pending negotiations. Retain every distinct key
    across reconnects and rekeys, rather than keeping only the latest key.
    """
    tks, pmks, warnings, pending = [], [], [], {}
    for line_no, line in enumerate(lines, 1):
        wrapper = EVENT_RECORD.match(line.rstrip())
        wrapper_interface = wrapper.group(1) if wrapper else None
        if wrapper:
            line = wrapper.group(2)
        # Event clocks and capture clocks can differ. Use interface/resource
        # labels for log selection; leave key-to-frame matching to TShark.
        scope_match = SCOPE.search(line)
        raw_match = RAW_SCOPE.search(line)
        # Event exports identify the resource and interface. File logs use
        # IFNAME or an interface name after the timestamp.
        scope = (scope_match.groups() if scope_match
                 else (None, raw_match.group(1) if raw_match else None))
        if scope[1] is None and wrapper_interface:
            scope = (scope[0], wrapper_interface)
        if interfaces and scope[1] not in interfaces:
            continue
        if resources and scope[0] not in resources:
            continue
        match = KEY_EVENT.search(line)
        hexdump = HEX_EVENT.search(line)
        if hexdump:
            kind, declared, value = hexdump.groups()
            value = "".join(value.split())
            if len(value) != int(declared) * 2:
                warnings.append(f"Invalid {kind} hexdump length on line {line_no}.")
                continue
        elif match:
            kind, value = match.groups()
        else:
            kind, value = None, None
        if value is not None:
            value = value.lower()
            if kind == "PTK":
                if scope in pending and pending[scope][0] != value:
                    warnings.append(f"PTK on line {pending[scope][1]} lacks a matching negotiation event.")
                pending[scope] = (value, line_no)
            elif kind == "PMK" and len(value) in (64, 96):
                pmks.append(value)
            elif kind in ("TK", "GTK") and len(value) in (32, 64):
                tks.append(value)
            else:
                warnings.append(f"Unsupported {kind} length on line {line_no}.")
        gtk_match = GTK_EVENT.search(line)
        if gtk_match:
            # These records include a key index and other metadata. Only the
            # GTK bytes belong in TShark's key table.
            declared, value = gtk_match.groups()
            data = bytes.fromhex(value)
            gtk = None
            if len(data) == int(declared):
                if "GTK in EAPOL-Key" in line:
                    if (len(data) in (24, 40) and data[0] == 0xdd
                            and data[1] == len(data) - 2
                            and data[2:6] == b"\x00\x0f\xac\x01"
                            and data[6] & 0xf8 == 0 and data[7] == 0):
                        gtk = data[8:]
                elif (len(data) in (18, 34) and data[0] & 0xf8 == 0 and data[1] == 0):
                    gtk = data[2:]
            if gtk is not None:
                tks.append(gtk.hex())
            else:
                warnings.append(f"Unsupported GTK metadata or length on line {line_no}.")
        cipher = re.search(r"Key negotiation completed.*\[PTK=([^\s\]]+)", line)
        if cipher and scope in pending:
            value, key_line = pending.pop(scope)
            if scope[1] and cipher.group(1) == "CCMP" and len(value) == 96:
                # A 48-byte CCMP PTK is KCK(16) + KEK(16) + TK(16).
                tks.append(value[64:96])
            else:
                warnings.append(f"PTK on line {key_line}: unsupported layout/cipher or missing interface; use an explicit --tk.")
    for _, line_no in pending.values():
        warnings.append(f"PTK on line {line_no} has no matching negotiation event; its cipher could not be confirmed.")
    return list(dict.fromkeys(tks)), list(dict.fromkeys(pmks)), warnings


def parse_events(text, interfaces=(), resources=()):
    """Read event text; return unique temporal keys, PMKs and warnings."""
    return parse_event_lines(text.splitlines(), interfaces, resources)


def valid_tk(value):
    """Validate a CLI temporal key without guessing its cipher from its length."""
    if not re.fullmatch(r"(?:[0-9a-fA-F]{32}|[0-9a-fA-F]{64})", value):
        raise argparse.ArgumentTypeError("TK must contain 32 or 64 hexadecimal characters.")
    return value.lower()


def choose_keys(source, tks, pmks, ssid=None, password=None):
    """Build ordered, unique TShark key entries for the selected key sources.

    This is the complete candidate pool. The per-pass key limit is applied
    later, so duplicate logs are harmless and older session keys are retained.
    """
    groups = {
        "tk": [("tk", value) for value in tks],
        "pmk": [("wpa-psk", value) for value in pmks],
        "password": [],
    }
    if ssid is not None and password is not None:
        groups["password"] = [("wpa-pwd", quote(password, safe="") + ":" + quote(ssid, safe=""))]
    if source == "auto":
        keys = groups["tk"] + groups["pmk"] + groups["password"]
        used = [kind for kind, values in groups.items() if values]
        source = used[0] if len(used) == 1 else "mixed"
    elif source in groups:
        keys = groups[source]
    else:
        raise ValueError("Unknown key source.")
    keys = list(dict.fromkeys(keys))
    if not keys:
        raise ValueError("No usable keys. Supply matching --events, --tk, or both --ssid and --password.")
    return source, keys


def file_sha256(path):
    """Hash an input in chunks to detect capture changes without loading it."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lock_workspace(stream):
    """Take a nonblocking OS lock; closing the stream/process releases it."""
    if os.name == "nt":
        import msvcrt
        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def workspace_identity(storage):
    """Identify our workspace without putting any session keys in its marker."""
    return {"tool": "lf_wifi_decrypt", "version": 1, "storage": storage,
            "user": getpass.getuser(), "uid": os.getuid() if hasattr(os, "getuid") else None}


@contextmanager
def temporary_workspace(storage):
    """Keep the workspace locked through child/store cleanup; close before removal."""
    with tempfile.TemporaryDirectory(prefix=WORKSPACE_PREFIX) as directory:
        root = Path(directory)
        with (root / WORKSPACE_LOCK).open("xb+") as guard:
            guard.write(b"0")
            guard.flush()
            lock_workspace(guard)
            (root / WORKSPACE_MARKER).write_text(json.dumps(workspace_identity(storage)), encoding="utf-8")
            yield root


def owned_plain_path(path, directory=False):
    """Reject links/junctions and, on Unix, entries belonging to another account."""
    info = path.lstat()
    reparse = getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    kind = stat.S_ISDIR if directory else stat.S_ISREG
    return (not reparse and kind(info.st_mode)
            and (not hasattr(os, "getuid") or info.st_uid == os.getuid()))


def workspace_files(root):
    """Recognize the entire cache layout before deleting any of its contents.

    Only the DB, its sidecars, our metadata and numbered key profiles belong
    here. An unexpected item leaves the whole directory untouched.
    """
    files, profiles = [], []
    names = {"frames.sqlite", "frames.sqlite-journal", "frames.sqlite-wal", "frames.sqlite-shm",
             WORKSPACE_MARKER, WORKSPACE_LOCK}
    for item in root.iterdir():
        if item.name in names and owned_plain_path(item):
            files.append(item)
        elif re.fullmatch(r"baseline|batch_\d+", item.name) and owned_plain_path(item, directory=True):
            for key_file in item.iterdir():
                if key_file.name != "80211_keys" or not owned_plain_path(key_file):
                    raise ValueError("unrecognized key-profile contents")
                files.append(key_file)
            profiles.append(item)
        else:
            raise ValueError("unrecognized workspace contents")
    return files, profiles


def sqlite_workspace(root):
    """Recognize marked caches, or old Unix caches with a valid SQLite header.

    Old releases have no marker/lock: the operator must ensure they are idle.
    Unmarked Windows directories are left alone because Unix UID ownership
    checks are not available there.
    """
    if not owned_plain_path(root, directory=True):
        return False
    marker = root / WORKSPACE_MARKER
    if marker.exists():
        if not owned_plain_path(marker) or marker.stat().st_size > 1024:
            return False
        return json.loads(marker.read_text(encoding="utf-8")) == workspace_identity("sqlite")
    database = root / "frames.sqlite"
    if os.name == "nt" or not owned_plain_path(database):
        return False
    with database.open("rb") as stream:
        return stream.read(16) == b"SQLite format 3\0"


def purge_sqlite_workspaces(temp_root=None):
    """Remove recognized abandoned SQLite workspaces, never user output files.

    Scan the current temp root only. Lock every candidate before removing any;
    a busy cache aborts the purge. Locks protect current releases, not legacy
    unmarked caches. Run this maintenance operation when decoding is idle.
    """
    parent = Path(temp_root if temp_root is not None else tempfile.gettempdir()).resolve(strict=True)
    removed, skipped, candidates = [], [], []
    with ExitStack() as guards:
        for root in sorted(parent.glob(WORKSPACE_PREFIX + "*")):
            try:
                if not sqlite_workspace(root):
                    skipped.append(root.name)
                    continue
                workspace_files(root)
                guard = guards.enter_context((root / WORKSPACE_LOCK).open("ab+"))
                try:
                    lock_workspace(guard)
                except OSError as exc:
                    raise RuntimeError("Cleanup stopped: a SQLite workspace is busy. Run purge when decoding is idle.") from exc
                candidates.append((root, guard))
            except (FileNotFoundError, ValueError):
                skipped.append(root.name)
        for root, guard in candidates:
            # Recheck under the lock. Delete only enumerated files/directories,
            # without following links or recursively removing unknown items.
            files, profiles = workspace_files(root)
            for item in files:
                if item.name != WORKSPACE_LOCK:
                    item.unlink()
            for profile in profiles:
                profile.rmdir()
            guard.close()  # Windows cannot unlink an open lock file.
            (root / WORKSPACE_LOCK).unlink()
            root.rmdir()
            removed.append(root.name)
    return {"temp_root": str(parent), "removed": removed, "skipped": skipped}


def make_profile(root, name, keys):
    """Create one temporary TShark key table and its process environment.

    Keep key bytes out of command arguments and leave the user's Wireshark
    profile alone. The caller owns the temporary directory and its cleanup.
    """
    path = root / name
    path.mkdir(mode=0o700)
    with (path / "80211_keys").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writerows(keys)
    env = dict(os.environ, WIRESHARK_CONFIG_DIR=str(path))
    if os.name != "nt":
        env["LC_ALL"] = "C"
    return env


def base_command(tshark, pcap, enabled):
    """Use the same capture and resolution settings for baseline and key passes."""
    return [str(tshark), "-n", "-r", str(pcap), "-o",
            "wlan.enable_decryption:" + ("TRUE" if enabled else "FALSE")]


def run_checked(command, env, timeout, secrets, stdout):
    """Run TShark with a deadline and redact this pass's keys from errors.

    SQLite mode streams packet output to a temporary file. Memory mode uses
    a StringIO buffer. Stop and reap the child before unwinding on Ctrl-C,
    errors or timeouts, so it cannot outlive its private key profiles.
    """
    in_memory = isinstance(stdout, io.StringIO)
    with subprocess.Popen(command, stdout=subprocess.PIPE if in_memory else stdout,
                          stderr=subprocess.PIPE, encoding="utf-8", errors="replace", env=env) as process:
        try:
            text, stderr = process.communicate(timeout=timeout)
        except BaseException:
            # In particular, SIGINT may reach Python without reaching TShark.
            # Wait for the killed child before closing buffers/removing keys.
            process.kill()
            process.communicate()
            raise
    if process.returncode:
        message = stderr
        for secret in secrets:
            message = message.replace(secret, "<redacted>")
        raise RuntimeError(f"TShark exited with {process.returncode}: {message.strip()}")
    if in_memory:
        stdout.write(text)


class MemoryFrameStore:
    """Keep frame metadata and rendered text in Python containers, without SQLite.

    The first successful batch owns a frame in both backends. A set deduplicates
    EAPOL numbers, and the final text is sorted by original capture frame number.
    """

    storage = "memory"

    def __init__(self):
        self.decoded = {}
        self.eapol = set()
        self.output = {}

    def transaction(self):
        return nullcontext()

    def add_eapol(self, number):
        self.eapol.add(number)

    def add_decoded(self, number, baseline, owner, protocols):
        self.decoded.setdefault(number, (baseline, owner, protocols))

    def decoded_count(self, new_only=False):
        return sum(not row[0] for row in self.decoded.values()) if new_only else len(self.decoded)

    def eapol_count(self):
        return len(self.eapol)

    def protocol_counts(self):
        return dict(Counter(row[2] for row in self.decoded.values()))

    def examples(self):
        return sorted(number for number, row in self.decoded.items() if not row[0])[:20]

    def owners(self):
        return {row[1] for row in self.decoded.values()}

    def add_output(self, number, body, batch):
        if self.decoded.get(number, (False, 0, ""))[1] == batch:
            self.output[number] = body

    def text_count(self):
        return len(self.output)

    def iter_text(self):
        for number in sorted(self.output):
            yield self.output[number]

    def close(self):
        self.decoded.clear()
        self.eapol.clear()
        self.output.clear()


class SqliteFrameStore:
    """Keep the same frame records in a fresh, per-run on-disk database.

    The caller closes this connection before removing its temporary workspace.
    SQLite's journal and any associated files are inside that workspace too.
    """

    storage = "sqlite"

    def __init__(self, path):
        self.database = sqlite3.connect(str(path))
        try:
            self.database.executescript(
                "CREATE TABLE decoded(frame INTEGER PRIMARY KEY, baseline INTEGER, owner INTEGER, protocols TEXT);"
                "CREATE TABLE eapol(frame INTEGER PRIMARY KEY);"
                "CREATE TABLE output(frame INTEGER PRIMARY KEY, body TEXT);"
            )
        except BaseException:
            self.database.close()
            raise

    def transaction(self):
        return self.database

    def add_eapol(self, number):
        self.database.execute("INSERT OR IGNORE INTO eapol VALUES (?)", (number,))

    def add_decoded(self, number, baseline, owner, protocols):
        self.database.execute("INSERT OR IGNORE INTO decoded VALUES (?, ?, ?, ?)",
                              (number, int(baseline), owner, protocols))

    def decoded_count(self, new_only=False):
        where = " WHERE baseline = 0" if new_only else ""
        return self.database.execute("SELECT COUNT(*) FROM decoded" + where).fetchone()[0]

    def eapol_count(self):
        return self.database.execute("SELECT COUNT(*) FROM eapol").fetchone()[0]

    def protocol_counts(self):
        return dict(self.database.execute("SELECT protocols, COUNT(*) FROM decoded GROUP BY protocols"))

    def examples(self):
        return [row[0] for row in self.database.execute(
            "SELECT frame FROM decoded WHERE baseline = 0 ORDER BY frame LIMIT 20")]

    def owners(self):
        return {row[0] for row in self.database.execute("SELECT DISTINCT owner FROM decoded")}

    def add_output(self, number, body, batch):
        self.database.execute(
            "INSERT OR REPLACE INTO output SELECT ?, ? "
            "WHERE COALESCE((SELECT owner FROM decoded WHERE frame = ?), 0) = ?",
            (number, body, number, batch),
        )

    def text_count(self):
        return self.database.execute("SELECT COUNT(*) FROM output").fetchone()[0]

    def iter_text(self):
        for row in self.database.execute("SELECT body FROM output ORDER BY frame"):
            yield row[0]

    def close(self):
        self.database.close()


def packet_buffer(store):
    """Use the chosen storage medium for each TShark pass's packet text too."""
    if store.storage == "memory":
        return io.StringIO()
    return tempfile.TemporaryFile(mode="w+", encoding="utf-8", errors="replace")


def scan(tshark, pcap, env, timeout, store, batch, secrets):
    """Scan a pass and retain successful protected frame numbers in the store.

    A protected frame containing LLC is a decoding candidate. The baseline
    marks frames already readable with decryption disabled, so they cannot
    count as new successes. Frame-number keys deduplicate results across passes.
    """
    command = base_command(tshark, pcap, batch is not None)
    command += ["-Y", "eapol || (wlan.fc.type == 2 && wlan.fc.protected == 1)",
                "-T", "fields", "-E", "occurrence=f"]
    for field in SCAN_FIELDS:
        command += ["-e", field]
    counts = Counter(eapol=0, protected_data=0, protected_unicast=0,
                     protected_group=0, decoded_protected_llc=0)
    with packet_buffer(store) as output:
        run_checked(command, env, timeout, secrets, output)
        output.seek(0)
        with store.transaction():
            for line in output:
                row = line.rstrip("\r\n").split("\t")
                row += [""] * (len(SCAN_FIELDS) - len(row))
                number, chain, protected, frame_type, receiver = row[:5]
                if not number:
                    continue
                number = int(number)
                protocols = chain.split(":")
                if "eapol" in protocols:
                    counts["eapol"] += 1
                    store.add_eapol(number)
                if protected.lower() not in ("1", "true") or frame_type != "2":
                    continue
                counts["protected_data"] += 1
                if receiver:
                    group = bool(int(receiver.split(":")[0], 16) & 1)
                    counts["protected_group" if group else "protected_unicast"] += 1
                if "llc" in protocols:
                    counts["decoded_protected_llc"] += 1
                    # Preserve the first successful pass for rendering. An
                    # owner identifies a key batch, not an individual key or
                    # reconnect session; several keys can share that batch.
                    store.add_decoded(number, batch is None, batch or 0, chain)
    return dict(counts)


def packet_text(stream, mode):
    """Yield original capture frame numbers and their TShark text records.

    Brief mode has one record per line. Verbose mode has variable-length
    blocks, so its Frame headers define boundaries. Preserve the text verbatim.
    """
    if mode == "brief":
        for line in stream:
            if not line.strip():
                continue
            match = re.match(r"^\s*(\d+)(?:\s|$)", line)
            if not match:
                raise RuntimeError("Cannot identify a frame number in TShark brief output.")
            yield int(match.group(1)), line
        return
    number, block = None, []
    for line in stream:
        match = re.match(r"^Frame (\d+):", line)
        if match:
            if number is not None:
                yield number, "".join(block)
            number, block = int(match.group(1)), []
        elif number is None and line.strip():
            raise RuntimeError("Cannot identify a frame boundary in TShark verbose output.")
        if number is not None:
            block.append(line)
    if number is not None:
        yield number, "".join(block)


def render_batch(tshark, pcap, env, timeout, store, batch, mode,
                 display_filter, decrypted_only, secrets):
    """Store each frame's text from its first successful decoding batch.

    Other frames come from batch zero. Rendering follows verification, so an
    output display filter can narrow text without changing capture-wide counts.
    TShark's stream reassembly remains local to each batch.
    """
    command = base_command(tshark, pcap, True)
    command += ["-o", "gui.column.format:" + COLUMNS]
    filters = [f"({display_filter})"] if display_filter else []
    if decrypted_only:
        filters.append("(wlan.fc.type == 2 && wlan.fc.protected == 1 && llc)")
    if filters:
        command += ["-Y", " && ".join(filters)]
    if mode == "verbose":
        command.append("-V")
    with packet_buffer(store) as output:
        run_checked(command, env, timeout, secrets, output)
        output.seek(0)
        with store.transaction():
            for number, body in packet_text(output, mode):
                # The earliest successful batch owns a decrypted frame.
                # Other frames are emitted from batch zero exactly once.
                store.add_output(number, body, batch)


def write_text(store, path, stream):
    """Write stored records in capture order to a stream or replace a text file.

    Build file output beside its destination and rename it only when complete.
    A caller-supplied stream is written directly and remains open for its owner.
    """
    if path is None:
        if stream is not None:
            for body in store.iter_text():
                stream.write(body)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="",
                                         dir=path.parent, prefix=".lf_wifi_decrypt_",
                                         delete=False) as output:
            temporary = Path(output.name)
            for body in store.iter_text():
                output.write(body)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def decrypt_capture(pcap, *, events=(), temporal_keys=(), ssid=None, password=None,
                    key_source="auto", mode="brief", display_filter=None,
                    decrypted_only=False, output=None, report_path=None,
                    tshark="tshark", timeout=120, key_batch_size=64,
                    interfaces=(), resources=(), progress=None, output_stream=None,
                    storage="sqlite"):
    """Decode a capture and return a JSON-compatible verification report.

    Supply an output path for decoded text, or output_stream for a text stream.
    With neither, only verification runs. This function does not print, change
    global logging or exit the caller. Errors raise exceptions. The caller may
    provide progress(dict) to receive stage and batch counts without key values.

    Read every supplied event file, keep all distinct session keys, and scan
    the full capture for each key batch. Packet times are not used to discard
    keys. Missing session keys can therefore leave a partially decoded capture;
    callers should inspect protected_data_remaining as well as verified.

    storage="memory" keeps packet records/text in Python containers and avoids
    SQLite. The default "sqlite" backend limits packet-text RAM usage. Both
    use private, per-call temporary key profiles and clean up on normal Ctrl-C.
    """
    pcap = Path(pcap)
    if isinstance(events, (str, Path)):
        events = [events]
    events = [Path(path) for path in events]
    output = Path(output) if output is not None else None
    report_path = Path(report_path) if report_path is not None else None
    inputs = {path.resolve() for path in [pcap] + events}
    destinations = [path.resolve() for path in [output, report_path] if path is not None]
    if any(path in inputs for path in destinations) or len(destinations) != len(set(destinations)):
        raise ValueError("Output and report paths must differ from each other and from the inputs.")
    if not pcap.is_file():
        raise ValueError("Capture file does not exist.")
    if mode not in ("brief", "verbose"):
        raise ValueError("Output mode must be brief or verbose.")
    if timeout <= 0:
        raise ValueError("Timeout must be positive.")
    if not 1 <= key_batch_size <= MAX_KEYS_PER_PASS:
        raise ValueError("Key batch size must be between 1 and 64.")
    if storage not in ("sqlite", "memory"):
        raise ValueError("Storage must be sqlite or memory.")
    # Gather the whole key history. A reconnect does not invalidate earlier
    # keys: earlier frames in this same capture still need them.
    tks, pmks, warnings = [], [], []
    for path in events:
        with path.open(encoding="utf-8", errors="replace") as stream:
            temporal, master, messages = parse_event_lines(stream, interfaces, resources)
        tks.extend(temporal)
        pmks.extend(master)
        warnings.extend(f"{path.name}: {message}" for message in messages)
    for key in temporal_keys:
        if not re.fullmatch(r"(?:[0-9a-fA-F]{32}|[0-9a-fA-F]{64})", key):
            raise ValueError("TK must contain 32 or 64 hexadecimal characters.")
        tks.append(key.lower())
    source, keys = choose_keys(key_source, tks, pmks, ssid, password)
    batches = [keys[start:start + key_batch_size] for start in range(0, len(keys), key_batch_size)]
    digest = file_sha256(pcap)
    notify = progress or (lambda event: None)
    with temporary_workspace(storage) as root:
        store = None
        try:
            store = MemoryFrameStore() if storage == "memory" else SqliteFrameStore(root / "frames.sqlite")
            notify({"stage": "baseline"})
            baseline_env = make_profile(root, "baseline", [])
            # Compare keyed decoding against a clean profile with decryption
            # disabled, including captures that already contain readable data.
            before = scan(tshark, pcap, baseline_env, timeout, store, None, [])
            profiles, tried = {}, 0
            for index, batch in enumerate(batches):
                notify({"stage": "keys", "batch": index + 1, "batches": len(batches)})
                profiles[index] = make_profile(root, f"batch_{index}", batch)
                scan(tshark, pcap, profiles[index], timeout, store, index,
                     [value for _, value in batch])
                tried += 1
                count = store.decoded_count()
                # Stop only after all counted protected data is readable.
                # Otherwise later batches may hold keys for older/newer sessions.
                if before["protected_data"] and count == before["protected_data"]:
                    break
            newly_decoded = store.decoded_count(new_only=True)
            after = dict(before)
            after["eapol"] = store.eapol_count()
            after["decoded_protected_llc"] = store.decoded_count()
            protocols = store.protocol_counts()
            examples = store.examples()
            if output is not None or output_stream is not None:
                owners = {0} | store.owners()
                for index in sorted(owners):
                    notify({"stage": "text", "batch": index + 1, "batches": len(batches)})
                    render_batch(tshark, pcap, profiles[index], timeout, store, index, mode,
                                 display_filter, decrypted_only, [value for _, value in batches[index]])
            if file_sha256(pcap) != digest:
                raise RuntimeError("Capture changed during decoding; use a completed capture.")
            report = {
                "pcap": str(pcap.resolve()), "sha256": digest,
                "storage": storage,
                "key_source": source, "key_count": len(keys),
                "key_types": dict(Counter(kind for kind, _ in keys)),
                "key_batch_size": key_batch_size, "key_batches": len(batches),
                "batches_tried": tried, "warnings": warnings,
                "baseline": before, "with_keys": after, "decoded_protocols": protocols,
                "newly_decoded_protected_frames": newly_decoded,
                "example_frame_numbers": examples, "verified": bool(newly_decoded),
                "protected_data_remaining": before["protected_data"] - after["decoded_protected_llc"],
                "verification_scope": "Full capture; newly decoded protected data with LLC versus decryption disabled",
                "output_filter": display_filter, "decrypted_only": decrypted_only,
                "text_frames_written": store.text_count(),
                "text_reassembly_scope": "Per key batch; cross-batch stream reassembly is not combined",
            }
            write_text(store, output, output_stream)
            if report_path is not None:
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            return report
        finally:
            if store is not None:
                store.close()


def parse_args(argv=None):
    """Parse offline capture inputs and output options for the command line."""
    parser = argparse.ArgumentParser(
        prog="lf_wifi_decrypt.py",
        description=__doc__,
        epilog=("Example: python3 lf_wifi_decrypt.py --pcap capture.pcapng "
                "--events wifi_events.txt --decrypted-only -o decoded.txt\n"
                "Repeat --events for multiple files. Exit codes: 0 = some decryption "
                "verified, 2 = none verified, 1 = processing error."),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--help_summary", action="version",
                        version=("Decode a Wi-Fi capture using all supplied session keys from "
                                 "LANforge Wi-Fi events or supplicant logs. Supports reconnects, "
                                 "multiple stations and brief/verbose TShark text."),
                        help="Show a short script summary and exit")
    parser.add_argument("--pcap", type=Path)
    parser.add_argument("--purge_sqlite", action="store_true",
                        help="Remove recognized abandoned SQLite workspaces from the current temp directory; run only when decoding is idle")
    parser.add_argument("--events", action="append", default=[], type=Path,
                        help="Matching Wi-Fi events or supplicant log; repeat for multiple files")
    parser.add_argument("--tk", action="append", default=[], type=valid_tk,
                        help="Explicit pairwise/group temporal key; repeat for multiple keys")
    parser.add_argument("--ssid")
    parser.add_argument("--password", help="WPA/WPA2-Personal password; WPA3-SAE needs session keys")
    parser.add_argument("--key-source", choices=("auto", "tk", "pmk", "password"), default="auto",
                        help="auto tries all supplied temporal keys, PMKs and password")
    parser.add_argument("--interface", action="append", default=[],
                        help="Keep keys from this interface name; repeat as needed")
    parser.add_argument("--resource", action="append", default=[],
                        help="Keep keys from this resource, e.g. 1.1; requires resource-tagged logs")
    parser.add_argument("--mode", choices=("brief", "verbose"), default="brief")
    parser.add_argument("--filter", help="Display filter for text; verification scans the full capture")
    parser.add_argument("--decrypted-only", action="store_true")
    parser.add_argument("-o", "--output", type=Path, help="Decoded text; default is standard output")
    parser.add_argument("--report", type=Path, help="JSON report; defaults to OUTPUT.json")
    parser.add_argument("--tshark", default="tshark")
    parser.add_argument("--timeout", type=float, default=120, help="Timeout per TShark invocation")
    parser.add_argument("--key-batch-size", type=int, default=64, help="Keys per pass, from 1 to 64")
    storage_group = parser.add_mutually_exclusive_group()
    storage_group.add_argument("--storage", choices=("sqlite", "memory"),
                               help="Packet/text storage: sqlite on disk (default) or Python memory")
    storage_group.add_argument("--no-sqlite", dest="storage", action="store_const", const="memory",
                               help="Keep packet records and text in Python RAM instead of SQLite")
    parser.set_defaults(storage="sqlite")
    parser.add_argument("--quiet", action="store_true", help="Hide batch progress")
    args = parser.parse_args(argv)
    if args.purge_sqlite:
        if any([args.pcap, args.events, args.tk, args.ssid, args.password, args.output, args.report]):
            parser.error("Use --purge_sqlite by itself, without capture/key/output arguments.")
    elif args.pcap is None:
        parser.error("--pcap is required for decoding.")
    if args.output is not None and args.report is None:
        args.report = Path(str(args.output) + ".json")
    return args


def main(argv=None):
    """Adapt the reusable API to CLI progress, text output and exit statuses."""
    args = parse_args(argv)

    # Keep progress on stderr so stdout remains usable as decoded packet text.
    def progress(event):
        if args.quiet:
            return
        if event["stage"] == "keys":
            print(f"Checking key batch {event['batch']}/{event['batches']}", file=sys.stderr)

    try:
        if args.purge_sqlite:
            result = purge_sqlite_workspaces()
            print(f"Removed {len(result['removed'])} SQLite workspace(s) from {result['temp_root']}. "
                  f"Skipped {len(result['skipped'])} unrecognized or non-SQLite workspace(s).")
            return 0
        report = decrypt_capture(
            args.pcap, events=args.events, temporal_keys=args.tk, ssid=args.ssid,
            password=args.password, key_source=args.key_source, mode=args.mode,
            display_filter=args.filter, decrypted_only=args.decrypted_only,
            output=args.output, report_path=args.report, tshark=args.tshark,
            timeout=args.timeout, key_batch_size=args.key_batch_size,
            interfaces=args.interface, resources=args.resource, progress=progress,
            output_stream=sys.stdout if args.output is None else None,
            storage=args.storage,
        )
        for warning in report["warnings"][:20]:
            print("Warning: " + warning, file=sys.stderr)
        if len(report["warnings"]) > 20:
            print(f"{len(report['warnings']) - 20} more warnings are in the report.", file=sys.stderr)
        print(f"Newly decoded protected data frames: {report['newly_decoded_protected_frames']}. "
              f"Still undecoded: {report['protected_data_remaining']}.", file=sys.stderr)
        return 0 if report["verified"] else 2
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except (OSError, ValueError, RuntimeError, sqlite3.Error, subprocess.TimeoutExpired) as exc:
        message = "TShark timed out; increase --timeout if needed." if isinstance(exc, subprocess.TimeoutExpired) else str(exc)
        print("Error: " + message, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
