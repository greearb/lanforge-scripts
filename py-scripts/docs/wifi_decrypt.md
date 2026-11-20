# Decode Wi-Fi captures from key events

`lf_wifi_decrypt.py` reads matching LANforge Wi-Fi events or supplicant logs
and runs TShark to produce brief or verbose text. It also writes a JSON report
showing whether protected data frames actually decoded. The input capture is
left unchanged. Python 3.8+ and TShark with the `tk` key type are required.

From the `py-scripts` directory:

```sh
python3 lf_wifi_decrypt.py --pcap capture.pcapng --events wifi_events.txt -o decoded.txt
python3 lf_wifi_decrypt.py --pcap capture.pcapng --events wifi_events.txt --mode verbose --decrypted-only -o details.txt
python3 lf_wifi_decrypt.py --pcap capture.pcapng --events resource1.txt --events resource2.txt -o combined.txt
```

The report defaults to `OUTPUT.json`. Exit status is 0 when some new
decryption is verified, 2 when none is verified, and 1 on a processing error.
Check `protected_data_remaining` to distinguish partial from complete decoding.
The report covers the whole capture even when `--filter` narrows the text.

## Storage and cleanup

By default `--storage sqlite` keeps frame metadata and decoded text in an
on-disk SQLite database. Use `--storage memory` or `--no-sqlite` to keep those
records and TShark packet-output buffers in Python RAM, without opening SQLite:

```sh
python3 lf_wifi_decrypt.py --pcap capture.pcapng --events wifi_events.txt --no-sqlite -o decoded.txt
```

Both backends preserve the same frame ordering and deduplication. Memory use
grows with the retained records and text in RAM mode, particularly for verbose
output. Temporary TShark key profiles are still written in a private per-run
directory; the user's Wireshark profile is left alone. The report records the
selected `storage` backend.

Each call creates a fresh temporary workspace; earlier databases are never
reopened. On normal completion, processing errors, timeouts or Ctrl-C, the
script stops and waits for any active TShark child, closes its storage/buffers,
then removes its own temporary directory, including the SQLite database and
key profiles. Interrupted text-file writes remove the partial temporary file
and preserve any earlier completed output at the requested destination.

Forced termination such as SIGKILL or power loss cannot run Python cleanup and
may leave a temporary workspace. The script does not delete other directories
by prefix or age, which could affect concurrent runs. Requested output files
are kept separately from the temporary cache.

## Reconnects in one capture

The same station can reconnect many times, and many stations can share one
capture. Supply the event history covering all those connections and group
rekeys. Every distinct TK/GTK is retained; a new connection does not replace
the keys needed by earlier frames. Captured EAPOL is optional when matching
temporal keys are available.

Event timestamps are not used to select packet ranges. TShark tries the key
candidates against the encrypted frames, so different log and capture clock
offsets do not discard otherwise usable keys. Event times alone cannot decrypt
traffic: the events must contain the required key values. Missing keys can
leave some sessions readable and others encrypted; check the remaining count.

Decoded text keeps original capture frame numbers. Verbose output includes
802.11 addresses for packet inspection. The JSON report gives capture-wide
counts, not an exact frame-to-key or reconnect-session map. Internally a frame
belongs to its first successful key batch; that batch may contain several
stations and sessions. Shared GTKs also do not identify a unique station.

Each key batch scans the full capture. For large completed files, allow enough
disk space for temporary output and raise the per-process `--timeout` if
needed. Capture duration alone is not a key-selection limit.

## Many stations and rekeys

The reader accepts raw INFO events, LANforge exports, quoted `wifi_event`
records from btbits, and the supported supplicant hexdump formats. Repeated
keys are deduplicated; different connection and group-rekey keys are retained.
Repeat `--events` for multiple files. Optional `--interface sta0000` and
`--resource 1.1` select log records; resource selection requires tagged logs.

[Wireshark supports 64 configured Wi-Fi keys per pass](https://www.wireshark.org/docs/wsug_html/).
The script handles larger sets in batches of up to 64, combines successful
frame results, and writes each frame once in capture order. More batches mean
more capture scans. Text protocol/stream reassembly is limited to the keys in
each pass; it is not combined across batches. `--key-batch-size` can reduce
the batch size. A temporary private configuration holds each key table; the
script does not change the user's Wireshark profile or place keys in TShark's
arguments or its JSON report.

## Key sources

The default `--key-source auto` tries all supplied TK/GTK values, PMKs and an
optional SSID/password. Use `--key-source tk`, `pmk` or `password` to select one.
For example:

```sh
python3 lf_wifi_decrypt.py --pcap capture.pcapng --events wifi_events.txt --key-source tk -o decoded.txt
python3 lf_wifi_decrypt.py --pcap capture.pcapng --ssid LabSSID --password LabPassword -o decoded.txt
```

With no captured four-way handshake, matching TK/GTK events are needed.
A password alone does not decrypt WPA3-SAE; use session keys. Legacy PTK
extraction is restricted to a confirmed 48-byte CCMP layout. Other PTK layouts
are skipped with a warning rather than guessed; direct TK events are preferred.
IGTK/BIGTK are not treated as data-decryption keys. Authentication/cipher support
ultimately depends on the installed TShark. This tool verifies protected data
with LLC; it does not verify protected management frames or produce a rewritten
decrypted pcap.

## Python callers

Add `py-scripts` to the caller's module search path, then:

```python
from lf_wifi_decrypt import decrypt_capture

report = decrypt_capture(
    "capture.pcapng",
    events=["wifi_events.txt"],
    output="decoded.txt",
    report_path="decoded.json",
    mode="brief",
    storage="memory",  # Omit to use the default on-disk SQLite store.
)
```

The function returns the report, raises exceptions on processing errors, and
does not print or exit the caller. Omit `output` for verification only. A
`progress` callback can receive stage/batch counts. A btserver/GUI caller may
also invoke the CLI and read its exit status and JSON report; GUI integration
is not included here.

Run the standalone tests from the repository root:

```sh
python3 -m unittest discover -s py-scripts/tests -p 'test_lf_wifi_decrypt*.py' -v
```
