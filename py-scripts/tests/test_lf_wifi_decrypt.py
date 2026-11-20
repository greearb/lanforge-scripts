import contextlib
import io
from pathlib import Path
import unittest
import tempfile
from unittest.mock import MagicMock, patch

import importlib.util
import sys

MODULE_PATH = Path(__file__).resolve().parents[1] / "lf_wifi_decrypt.py"
spec = importlib.util.spec_from_file_location("lf_wifi_decrypt", MODULE_PATH)
wd = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = wd
spec.loader.exec_module(wd)


class KeyEventsTest(unittest.TestCase):
    def test_interleaved_resources_and_rotated_sessions(self):
        a, b, c = "11" * 48, "22" * 48, "33" * 48
        events = (f"1.1: IFNAME=sta0 WPA: PTK {a}\n"
                  f"1.2: IFNAME=sta0 WPA: PTK {b}\n"
                  "1.2: IFNAME=sta0 WPA: Key negotiation completed [PTK=CCMP GTK=CCMP]\n"
                  "1.1: IFNAME=sta0 WPA: Key negotiation completed [PTK=CCMP GTK=CCMP]\n"
                  f"1.1: IFNAME=sta0 WPA: PTK {c}\n"
                  "1.1: IFNAME=sta0 WPA: Key negotiation completed [PTK=CCMP GTK=CCMP]\n")
        tks, _, warnings = wd.parse_events(events)
        self.assertEqual(tks, ["22" * 16, "11" * 16, "33" * 16])
        self.assertEqual(warnings, [])

    def test_unsupported_and_unconfirmed_ptks_are_not_truncated(self):
        for cipher, length in (("TKIP", 64), ("CCMP-256", 64), ("CCMP", 64)):
            events = f"IFNAME=sta0 WPA: PTK {'aa' * length}\nIFNAME=sta0 WPA: Key negotiation completed [PTK={cipher} GTK=CCMP]"
            tks, _, warnings = wd.parse_events(events)
            self.assertEqual(tks, [])
            self.assertTrue(warnings)
        tks, _, warnings = wd.parse_events("IFNAME=sta0 WPA: PTK " + "aa" * 48)
        self.assertEqual(tks, [])
        self.assertTrue(warnings)

    def test_direct_keys_and_pmk(self):
        events = f"WPA: TK {'ab' * 16}\nWPA: GTK {'cd' * 16}\nWPA: PMK {'ef' * 32}\nWPA: TK abc"
        tks, pmks, warnings = wd.parse_events(events)
        self.assertEqual(tks, ["ab" * 16, "cd" * 16])
        self.assertEqual(pmks, ["ef" * 32])
        self.assertTrue(warnings)
        self.assertEqual(wd.choose_keys("auto", tks, pmks)[0], "mixed")
        self.assertEqual(wd.choose_keys("pmk", tks, pmks)[1], [("wpa-psk", "ef" * 32)])

    def test_password_escaping_and_large_key_sets(self):
        source, keys = wd.choose_keys("password", [], [], "My:SSID%", "pass:word%")
        self.assertEqual(keys, [("wpa-pwd", "pass%3Aword%25:My%3ASSID%25")])
        _, keys = wd.choose_keys("tk", [f"{i:032x}" for i in range(1024)] + ["00" * 16], [])
        self.assertEqual(len(keys), 1024)

    @staticmethod
    def database():
        return wd.SqliteFrameStore(":memory:")

    def test_boolean_rendering_and_cleartext_do_not_fake_decryption(self):
        rows = ("1\tradiotap:wlan:llc:arp\tTrue\t2\t00:00:00:00:00:02\n"
                "2\tradiotap:wlan:data\t1\t2\t01:00:5e:00:00:fb\n"
                "3\tradiotap:wlan:llc:ip\tFalse\t2\t00:00:00:00:00:02\n"
                "4\tradiotap:wlan:llc:eapol\tFalse\t2\t00:00:00:00:00:02\n")
        database = self.database()
        try:
            def run(command, env, timeout, secrets, stdout):
                stdout.write(rows)
            with patch.object(wd, "run_checked", side_effect=run):
                counts = wd.scan("tshark", Path("x.pcap"), {}, 1, database, 0, [])
            self.assertEqual(database.examples(), [1])
            self.assertEqual(counts["protected_data"], 2)
            self.assertEqual(counts["protected_group"], 1)
            self.assertEqual(counts["eapol"], 1)
        finally:
            database.close()

    def test_output_cannot_overwrite_input(self):
        with tempfile.TemporaryDirectory() as area:
            capture = Path(area) / "capture.pcap"
            capture.touch()
            with self.assertRaises(ValueError):
                wd.decrypt_capture(capture, output=capture)
            with self.assertRaises(ValueError):
                wd.decrypt_capture(capture, output=Path(area) / "x",
                                   report_path=Path(area) / "x")

    def test_raw_supplicant_scope_and_duplicate_key_forms(self):
        ptk = "aa" * 16 + "bb" * 16 + "cc" * 16
        dump = " ".join(ptk[i:i+2] for i in range(0, len(ptk), 2))
        text = (f"1794760000.1: IFNAME=sta0 <2>WPA: PTK - hexdump(len=48): {dump}\n"
                f"1794760000.2: sta0: WPA: PTK {ptk}\n"
                "1794760000.3: sta0: WPA: Key negotiation completed [PTK=CCMP GTK=CCMP]\n")
        tks, _, warnings = wd.parse_events(text)
        self.assertEqual(tks, ["cc" * 16])
        self.assertEqual(warnings, [])

    def test_gtk_metadata_is_removed_and_igtk_is_not_used_as_gtk(self):
        gtk = "01 00 " + "ab " * 16
        kde = "dd 16 00 0f ac 01 " + gtk
        text = (f"IFNAME=sta0 WPA: GTK in EAPOL-Key - hexdump(len=24): {kde}\n"
                f"IFNAME=sta0 RSN: received GTK in pairwise handshake - hexdump(len=18): {gtk}\n"
                f"IFNAME=sta0 WPA: IGTK - hexdump(len=16): {'cd ' * 16}\n")
        tks, _, warnings = wd.parse_events(text)
        self.assertEqual(tks, ["ab" * 16])
        self.assertEqual(warnings, [])

    def test_wrong_kde_selector_or_lengths_are_rejected(self):
        for kde in ("dd 16 00 0f ac 09 01 00 " + "ab " * 16,
                    "dd 16 00 0f ac 01 01 00 " + "ab " * 15,
                    "dd 15 00 0f ac 01 01 00 " + "ab " * 16):
            tks, _, warnings = wd.parse_events(f"IFNAME=sta0 WPA: GTK in EAPOL-Key - hexdump(len=24): {kde}")
            self.assertEqual(tks, [])
            self.assertTrue(warnings)

    def test_pmk_hexdump_is_parsed_with_declared_length(self):
        tks, pmks, warnings = wd.parse_events("IFNAME=sta0 WPA: PMK - hexdump(len=32): " + "ab " * 32)
        self.assertEqual(pmks, ["ab" * 32])
        self.assertEqual(warnings, [])

    def test_quoted_btbits_records(self):
        ptk = "aa" * 16 + "bb" * 16 + "cc" * 16
        lines = [
            f"wifi_event sta0 misc NA '1795000000.1: IFNAME=sta0 <3>WPA: PTK {ptk}'",
            "wifi_event sta0 misc NA '1795000000.2: IFNAME=sta0 <3>WPA: Key negotiation completed [PTK=CCMP GTK=CCMP]'",
            f"wifi_event sta0 misc NA '1795000000.3: IFNAME=sta0 <3>WPA: GTK {'dd' * 16}'",
        ]
        tks, _, warnings = wd.parse_events("\n".join(lines))
        self.assertEqual(tks, ["cc" * 16, "dd" * 16])
        self.assertEqual(warnings, [])

    def test_resource_and_interface_selection(self):
        text = (f"1.1: IFNAME=sta0 <3>WPA: TK {'11' * 16}\n"
                f"1.2: IFNAME=sta0 <3>WPA: TK {'22' * 16}\n"
                f"1.1: IFNAME=sta1 <3>WPA: TK {'33' * 16}\n")
        keys, _, _ = wd.parse_events(text, interfaces=["sta0"], resources=["1.2"])
        self.assertEqual(keys, ["22" * 16])

    def test_batches_keep_first_success_and_do_not_double_count_eapol(self):
        database = self.database()
        streams = [
            "1\twlan:data\t1\t2\t00:00:00:00:00:02\n"
            "2\twlan:data\t1\t2\t00:00:00:00:00:02\n"
            "3\twlan:llc:eapol\t0\t2\t00:00:00:00:00:02\n",
            "1\twlan:llc:ip\t1\t2\t00:00:00:00:00:02\n"
            "2\twlan:data\t1\t2\t00:00:00:00:00:02\n"
            "3\twlan:llc:eapol\t0\t2\t00:00:00:00:00:02\n",
            "1\twlan:llc:ip\t1\t2\t00:00:00:00:00:02\n"
            "2\twlan:llc:arp\t1\t2\t00:00:00:00:00:02\n"
            "3\twlan:llc:eapol\t0\t2\t00:00:00:00:00:02\n",
        ]

        def run(command, env, timeout, secrets, stdout):
            stdout.write(streams.pop(0))
        try:
            with patch.object(wd, "run_checked", side_effect=run):
                for batch in [None, 0, 1]:
                    wd.scan("tshark", Path("x.pcap"), {}, 1, database, batch, [])
            self.assertEqual(database.examples(), [1, 2])
            self.assertEqual(database.owners(), {0, 1})
            self.assertEqual(database.eapol_count(), 1)
        finally:
            database.close()

    def test_text_is_written_once_per_frame_in_capture_order(self):
        database = self.database()
        with database.transaction():
            database.add_decoded(1, False, 0, "wlan:llc")
            database.add_decoded(2, False, 1, "wlan:llc")
        streams = ["1 first\n2 encrypted\n", "1 duplicate\n2 second\n"]

        def run(command, env, timeout, secrets, stdout):
            stdout.write(streams.pop(0))
        try:
            with patch.object(wd, "run_checked", side_effect=run):
                for batch in [0, 1]:
                    wd.render_batch("tshark", Path("x"), {}, 1, database, batch, "brief", None, False, [])
            output = io.StringIO()
            wd.write_text(database, None, output)
            self.assertEqual(output.getvalue(), "1 first\n2 second\n")
        finally:
            database.close()

    def test_verbose_blocks_preserve_tshark_text(self):
        text = "Frame 1: 100 bytes on wire\n    Radio\n\nFrame 4: 80 bytes on wire\n    IPv4\n\n"
        records = list(wd.packet_text(io.StringIO(text), "verbose"))
        self.assertEqual([row[0] for row in records], [1, 4])
        self.assertEqual("".join(row[1] for row in records), text)

    def test_key_values_are_removed_from_tshark_errors(self):
        secret = "ab" * 16
        process = MagicMock()
        process.returncode = 1
        process.communicate.return_value = ("", "bad key " + secret)
        with patch.object(wd.subprocess, "Popen") as popen:
            popen.return_value.__enter__.return_value = process
            with self.assertRaises(RuntimeError) as caught:
                wd.run_checked(["tshark"], {}, 1, [secret], io.StringIO())
        self.assertNotIn(secret, str(caught.exception))

    def test_timeout_message_does_not_expose_arguments(self):
        error = wd.subprocess.TimeoutExpired(["tshark", "sensitive-value"], 1)
        stderr = io.StringIO()
        with patch.object(wd, "decrypt_capture", side_effect=error):
            with contextlib.redirect_stderr(stderr):
                result = wd.main(["--pcap", "x"])
        self.assertEqual(result, 1)
        self.assertNotIn("sensitive-value", stderr.getvalue())

    def test_invalid_batch_sizes_fail_before_tshark(self):
        with tempfile.TemporaryDirectory() as area:
            capture = Path(area) / "x.pcap"
            capture.touch()
            for size in [0, 65]:
                with self.assertRaises(ValueError):
                    wd.decrypt_capture(capture, temporal_keys=["ab" * 16], key_batch_size=size)

    def test_storage_options(self):
        self.assertEqual(wd.parse_args(["--pcap", "x"]).storage, "sqlite")
        self.assertEqual(wd.parse_args(["--pcap", "x", "--no-sqlite"]).storage, "memory")
        self.assertEqual(wd.parse_args(["--pcap", "x", "--storage", "memory"]).storage, "memory")
        with tempfile.TemporaryDirectory() as area:
            capture = Path(area) / "x.pcap"
            capture.touch()
            with self.assertRaises(ValueError):
                wd.decrypt_capture(capture, temporal_keys=["ab" * 16], storage="unknown")

    def test_store_backends_preserve_first_success_and_order(self):
        for storage in ["sqlite", "memory"]:
            with self.subTest(storage=storage), tempfile.TemporaryDirectory() as area:
                store = wd.SqliteFrameStore(Path(area) / "frames.sqlite") if storage == "sqlite" else wd.MemoryFrameStore()
                with contextlib.closing(store):
                    with store.transaction():
                        store.add_decoded(9, False, 1, "wlan:llc:ip")
                        store.add_decoded(9, False, 2, "wrong")
                        store.add_decoded(3, True, 0, "wlan:llc:arp")
                        store.add_eapol(7)
                        store.add_eapol(7)
                        store.add_output(9, "wrong\n", 2)
                        store.add_output(9, "decoded\n", 1)
                        store.add_output(3, "baseline\n", 0)
                        store.add_output(4, "wrong\n", 1)
                        store.add_output(4, "other\n", 0)
                    self.assertEqual(store.decoded_count(), 2)
                    self.assertEqual(store.decoded_count(new_only=True), 1)
                    self.assertEqual(store.examples(), [9])
                    self.assertEqual(store.owners(), {0, 1})
                    self.assertEqual(store.eapol_count(), 1)
                    self.assertEqual(store.protocol_counts(), {"wlan:llc:ip": 1, "wlan:llc:arp": 1})
                    self.assertEqual(list(store.iter_text()), ["baseline\n", "other\n", "decoded\n"])
                    self.assertEqual(store.text_count(), 3)

    @staticmethod
    def fake_packets(command, env, timeout, secrets, stdout):
        if "-T" in command:
            protocols = "wlan:data" if Path(env["WIRESHARK_CONFIG_DIR"]).name == "baseline" else "wlan:llc:ip"
            stdout.write(f"1\t{protocols}\t1\t2\t02:00:00:00:00:01\n")
        else:
            stdout.write("1 decoded synthetic frame\n")

    def test_memory_mode_opens_no_sqlite_or_packet_spool(self):
        with tempfile.TemporaryDirectory() as area:
            capture = Path(area) / "x.pcap"
            capture.touch()
            output = io.StringIO()
            with patch.object(wd.sqlite3, "connect", side_effect=AssertionError("SQLite was used")), \
                    patch.object(wd.tempfile, "TemporaryFile", side_effect=AssertionError("Disk packet spool was used")), \
                    patch.object(wd, "run_checked", side_effect=self.fake_packets):
                report = wd.decrypt_capture(capture, temporal_keys=["ab" * 16], storage="memory", output_stream=output)
            self.assertEqual(report["storage"], "memory")
            self.assertEqual(report["newly_decoded_protected_frames"], 1)
            self.assertEqual(output.getvalue(), "1 decoded synthetic frame\n")

    def test_workspaces_removed_on_success_error_and_interrupt(self):
        directory_factory = tempfile.TemporaryDirectory
        for storage in ["sqlite", "memory"]:
            for failure in [None, RuntimeError, KeyboardInterrupt]:
                with self.subTest(storage=storage, failure=failure), directory_factory() as area:
                    capture = Path(area) / "x.pcap"
                    capture.touch()
                    roots, stores = [], []
                    store_class = wd.SqliteFrameStore if storage == "sqlite" else wd.MemoryFrameStore

                    def directory(_roots=roots, **kwargs):
                        context = directory_factory(dir=area, **kwargs)
                        _roots.append(Path(context.name))
                        return context

                    def make_store(*args, _factory=store_class, _stores=stores):
                        store = _factory(*args)
                        _stores.append(store)
                        return store

                    def packets(*args, _roots=roots, _storage=storage, _failure=failure):
                        self.assertEqual((_roots[0] / "frames.sqlite").exists(), _storage == "sqlite")
                        if _failure:
                            raise _failure("synthetic failure")
                        return self.fake_packets(*args)

                    name = "SqliteFrameStore" if storage == "sqlite" else "MemoryFrameStore"
                    with patch.object(wd.tempfile, "TemporaryDirectory", side_effect=directory), \
                            patch.object(wd, name, side_effect=make_store), \
                            patch.object(wd, "run_checked", side_effect=packets):
                        if failure:
                            with self.assertRaises(failure):
                                wd.decrypt_capture(capture, temporal_keys=["ab" * 16], storage=storage)
                        else:
                            result = wd.decrypt_capture(capture, temporal_keys=["ab" * 16], storage=storage)
                            self.assertTrue(result["verified"])
                    self.assertTrue(roots)
                    self.assertTrue(all(not root.exists() for root in roots))
                    if storage == "sqlite":
                        with self.assertRaises(wd.sqlite3.ProgrammingError):
                            stores[0].database.execute("SELECT 1")
                    else:
                        self.assertEqual(stores[0].decoded, {})

    def test_sqlite_initialization_error_closes_connection(self):
        connection = MagicMock()
        connection.executescript.side_effect = wd.sqlite3.OperationalError("synthetic initialization error")
        with patch.object(wd.sqlite3, "connect", return_value=connection):
            with self.assertRaises(wd.sqlite3.OperationalError):
                wd.SqliteFrameStore("unused")
        connection.close.assert_called_once()

    def test_interrupt_and_timeout_stop_child_before_unwinding(self):
        for failure in [KeyboardInterrupt(), wd.subprocess.TimeoutExpired(["tshark"], 1)]:
            with self.subTest(failure=type(failure).__name__), patch.object(wd.subprocess, "Popen") as popen:
                process = popen.return_value.__enter__.return_value
                process.communicate.side_effect = [failure, ("", "")]
                with self.assertRaises(type(failure)):
                    wd.run_checked(["tshark"], {}, 1, [], io.StringIO())
                process.kill.assert_called_once()
                self.assertEqual(process.communicate.call_count, 2)

    def test_interrupted_text_write_keeps_previous_output_and_removes_partial(self):
        with tempfile.TemporaryDirectory() as area, contextlib.closing(wd.MemoryFrameStore()) as store:
            output = Path(area) / "decoded.txt"
            output.write_text("previous complete output\n")

            def interrupted():
                yield "partial new text\n"
                raise KeyboardInterrupt()

            with patch.object(store, "iter_text", side_effect=interrupted):
                with self.assertRaises(KeyboardInterrupt):
                    wd.write_text(store, output, None)
            self.assertEqual(output.read_text(), "previous complete output\n")
            self.assertEqual([p.name for p in Path(area).iterdir()], ["decoded.txt"])


if __name__ == "__main__":
    # py-scripts' help checker also visits standalone regression scripts.
    if sys.argv[1:] == ["--help_summary"]:
        print("Run synthetic-key regression tests for lf_wifi_decrypt.py.")
    else:
        unittest.main()
