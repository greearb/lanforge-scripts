"""Check text selection, epoch display and logging with synthetic keys."""
import contextlib
import importlib.util
import io
from pathlib import Path
import shlex
import sys
import tempfile
import unittest
from unittest.mock import patch


MODULE = Path(__file__).resolve().parents[1] / "lf_wifi_decrypt.py"
spec = importlib.util.spec_from_file_location("decoder_display", MODULE)
wd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wd)


class DisplayTest(unittest.TestCase):
    def test_filter_composition_and_cli_flag(self):
        self.assertFalse(wd.parse_args(["--pcap", "input"]).remove_beamforming)
        self.assertTrue(wd.parse_args(["--pcap", "input", "--remove_beamforming"]).remove_beamforming)
        self.assertIsNone(wd.text_filter())
        self.assertEqual(wd.text_filter("ip || arp"), "(ip || arp)")
        self.assertEqual(wd.text_filter(remove_beamforming=True), wd.BEAMFORMING_FILTER)
        self.assertEqual(wd.text_filter("ip || arp", True, True),
                         "(ip || arp) && (wlan.fc.type == 2 && wlan.fc.protected == 1 && llc) && " + wd.BEAMFORMING_FILTER)

    def test_render_options_and_redacted_callback_in_both_modes(self):
        secret = "ab" * 16
        selection = f'wlan.ssid == "{secret}"'
        for mode in ["brief", "verbose"]:
            with self.subTest(mode=mode), contextlib.closing(wd.MemoryFrameStore()) as store:
                store.add_decoded(1, False, 0, "wlan:llc")
                commands, events = [], []
                body = "1 synthetic packet\n" if mode == "brief" else "Frame 1: synthetic packet\n  details\n"

                def run(command, env, timeout, secrets, output, _body=body, _commands=commands):
                    _commands.append(command)
                    output.write(_body)

                stdout, stderr = io.StringIO(), io.StringIO()
                with patch.object(wd, "run_checked", side_effect=run), \
                        contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    wd.render_batch("path with spaces/tshark", Path("capture with spaces.pcap"), {}, 10,
                                    store, 0, mode, selection, True, [secret],
                                    remove_beamforming=True, progress=events.append)
                command = commands[0]
                self.assertEqual(command[command.index("-t") + 1], "e")
                self.assertEqual(command[command.index("-Y") + 1], wd.text_filter(selection, True, True))
                self.assertEqual(command.count("-Y"), 1)
                self.assertEqual("-V" in command, mode == "verbose")
                for field in ["%F", "wlan_radio.signal_dbm", "wlan.fixed.category_code",
                              "wlan.eht.action", "wlan.he.action", "wlan.vht.action"]:
                    columns = next(argument for argument in command if argument.startswith("gui.column.format:"))
                    self.assertIn(field, columns)
                self.assertEqual(list(store.iter_text()), [body])
                self.assertEqual(stdout.getvalue() + stderr.getvalue(), "")
                self.assertEqual(events[0]["stage"], "command")
                self.assertNotIn(secret, events[0]["command"])
                self.assertIn("<redacted>", events[0]["command"])
                self.assertIn(secret, command[command.index("-Y") + 1])

    def test_posix_command_quotes_paths_and_filter_as_single_arguments(self):
        command = ["path with spaces/tshark", "-r", "capture's name.pcap", "-Y", "ip || arp"]
        with patch.object(wd.os, "name", "posix"):
            self.assertEqual(shlex.split(wd.command_text(command, [])), command)

    def test_api_report_and_cli_quiet_keep_control_of_logging(self):
        def packets(command, env, timeout, secrets, output):
            if "-T" in command:
                chain = "wlan:data" if Path(env["WIRESHARK_CONFIG_DIR"]).name == "baseline" else "wlan:llc:ip"
                output.write(f"1\t{chain}\t1\t2\t02:00:00:00:00:01\n")
            else:
                output.write("1 synthetic frame\n")

        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.pcap"
            source.touch()
            stream, stderr = io.StringIO(), io.StringIO()
            with patch.object(wd, "run_checked", side_effect=packets), contextlib.redirect_stderr(stderr):
                report = wd.decrypt_capture(source, temporal_keys=["ab" * 16], output_stream=stream,
                                            display_filter="ip || arp", remove_beamforming=True)
            self.assertEqual(stderr.getvalue(), "")
            self.assertTrue(report["remove_beamforming"])
            self.assertEqual(report["output_filter"], "ip || arp")
            self.assertEqual(report["effective_output_filter"], wd.text_filter("ip || arp", False, True))
            self.assertEqual(report["newly_decoded_protected_frames"], 1)
            for quiet in [False, True]:
                with self.subTest(quiet=quiet):
                    stdout, stderr = io.StringIO(), io.StringIO()
                    args = ["--pcap", str(source), "--tk", "ab" * 16, "--remove_beamforming"]
                    if quiet:
                        args.append("--quiet")
                    with patch.object(wd, "run_checked", side_effect=packets), \
                            contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                        code = wd.main(args)
                    self.assertEqual(code, 0)
                    self.assertEqual(stdout.getvalue(), "1 synthetic frame\n")
                    self.assertEqual("tshark command:" in stderr.getvalue(), not quiet)
                    self.assertIn("Newly decoded protected data frames: 1", stderr.getvalue())
                    self.assertNotIn("ab" * 16, stderr.getvalue())


if __name__ == "__main__":
    if sys.argv[1:] == ["--help_summary"]:
        print("Check decoder text filters, epoch display and render-command logging.")
    else:
        unittest.main()
