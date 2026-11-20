"""Exercise actual POSIX SIGINT/timeout cleanup with a synthetic TShark child."""
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest


MODULE = Path(__file__).resolve().parents[1] / "lf_wifi_decrypt.py"
FAKE_TSHARK = r'''
import json
import os
from pathlib import Path
import sys
import time

profile = Path(os.environ["WIRESHARK_CONFIG_DIR"])
stage = ("baseline" if profile.name == "baseline" else "keys") if "-T" in sys.argv else "text"
if stage == os.environ["HOLD_STAGE"]:
    Path(os.environ["READY_FILE"]).write_text(json.dumps({"pid": os.getpid(), "stage": stage}))
    while True:
        time.sleep(60)
if "-T" in sys.argv:
    protocols = "wlan:data" if stage == "baseline" else "wlan:llc:ip"
    print("1\t" + protocols + "\t1\t2\t02:00:00:00:00:01")
else:
    print("1 decoded synthetic frame")
'''


@unittest.skipIf(os.name == "nt", "Actual SIGINT process tests require POSIX; portable interrupt paths have unit coverage")
class InterruptCleanupTest(unittest.TestCase):
    def check_cleanup(self, storage, stage, interrupt):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache = root / "temporary"
            cache.mkdir()
            unrelated = cache / "unrelated.txt"
            unrelated.write_text("preserve another run's data")
            capture = root / "synthetic.pcap"
            capture.touch()
            fake = root / "fake_tshark"
            fake.write_text("#!" + sys.executable + "\n" + FAKE_TSHARK)
            fake.chmod(0o700)
            output = root / "decoded.txt"
            output.write_text("previous complete output\n")
            ready = root / "ready.json"
            env = dict(os.environ, TMPDIR=str(cache), TMP=str(cache), TEMP=str(cache),
                       READY_FILE=str(ready), HOLD_STAGE=stage, PYTHONDONTWRITEBYTECODE="1")
            args = [sys.executable, str(MODULE), "--pcap", str(capture), "--tk", "ab" * 16,
                    "--tshark", str(fake), "--storage", storage, "-o", str(output),
                    "--timeout", "20" if interrupt else "1"]
            process = subprocess.Popen(args, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True, start_new_session=True)
            try:
                deadline = time.monotonic() + 8
                while time.monotonic() < deadline and not ready.exists() and process.poll() is None:
                    time.sleep(.02)
                self.assertTrue(ready.exists(), "Synthetic child did not reach the requested stage")
                child = json.loads(ready.read_text())["pid"]
                workspaces = list(cache.glob("lf_wifi_decrypt_*"))
                self.assertEqual(len(workspaces), 1)
                workspace = workspaces[0]
                self.assertTrue(list(workspace.glob("*/80211_keys")))
                self.assertEqual((workspace / "frames.sqlite").exists(), storage == "sqlite")
                if stage == "text" and storage == "sqlite":
                    connection = sqlite3.connect(str(workspace / "frames.sqlite"))
                    try:
                        self.assertEqual(connection.execute("SELECT COUNT(*) FROM decoded").fetchone()[0], 1)
                    finally:
                        connection.close()
                if interrupt:
                    # Signal Python alone: the helper must explicitly stop/reap
                    # the child rather than depend on terminal group delivery.
                    process.send_signal(signal.SIGINT)
                stdout, stderr = process.communicate(timeout=8)
                self.assertEqual(process.returncode, 130 if interrupt else 1, stderr)
                self.assertIn("Interrupted." if interrupt else "TShark timed out", stderr)
                self.assertEqual(stdout, "")
                self.assertFalse(workspace.exists())
                self.assertEqual(unrelated.read_text(), "preserve another run's data")
                self.assertEqual(output.read_text(), "previous complete output\n")
                self.assertFalse(list(root.glob(".lf_wifi_decrypt_*")))
                with self.assertRaises(ProcessLookupError):
                    os.kill(child, 0)
            finally:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.communicate(timeout=5)

    def test_ctrl_c_during_scan_and_render(self):
        for storage in ["sqlite", "memory"]:
            for stage in ["baseline", "keys", "text"]:
                with self.subTest(storage=storage, stage=stage):
                    self.check_cleanup(storage, stage, interrupt=True)

    def test_timeout_stops_child_and_cleans_workspace(self):
        for storage in ["sqlite", "memory"]:
            with self.subTest(storage=storage):
                self.check_cleanup(storage, "keys", interrupt=False)


if __name__ == "__main__":
    if sys.argv[1:] == ["--help_summary"]:
        print("Check lf_wifi_decrypt.py Ctrl-C and timeout cleanup with a synthetic child.")
    else:
        unittest.main()
