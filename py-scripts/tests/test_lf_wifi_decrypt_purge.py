"""Exercise explicit cache cleanup using synthetic, isolated temporary roots."""
import importlib.util
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


MODULE = Path(__file__).resolve().parents[1] / "lf_wifi_decrypt.py"
spec = importlib.util.spec_from_file_location("lf_wifi_decrypt", MODULE)
wd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wd)


class PurgeTest(unittest.TestCase):
    def cache(self, parent, name="stale", marked=True):
        root = parent / (wd.WORKSPACE_PREFIX + name)
        root.mkdir()
        with closing(sqlite3.connect(root / "frames.sqlite")) as db:
            db.execute("CREATE TABLE synthetic(frame INTEGER)")
            db.commit()
        wd.make_profile(root, "baseline", [])
        wd.make_profile(root, "batch_0", [("tk", "ab" * 16)])
        if marked:
            (root / wd.WORKSPACE_MARKER).write_text(json.dumps(wd.workspace_identity("sqlite")))
            (root / wd.WORKSPACE_LOCK).write_bytes(b"0")
        return root

    def test_stale_cache_including_journal_and_keys_removed(self):
        with tempfile.TemporaryDirectory() as area:
            parent = Path(area)
            root = self.cache(parent)
            for sidecar in ["-journal", "-wal", "-shm"]:
                (root / ("frames.sqlite" + sidecar)).touch()
            unrelated = parent / "decoded.txt"
            unrelated.write_text("keep completed output")
            result = wd.purge_sqlite_workspaces(parent)
            self.assertEqual(result["removed"], [root.name])
            self.assertFalse(root.exists())
            self.assertEqual(unrelated.read_text(), "keep completed output")
            self.assertEqual(wd.purge_sqlite_workspaces(parent)["removed"], [])

    def test_busy_run_prevents_all_removals(self):
        with tempfile.TemporaryDirectory() as area:
            parent = Path(area)
            stale = self.cache(parent, "a_stale")
            with patch.object(wd.tempfile, "tempdir", area), wd.temporary_workspace("sqlite") as active:
                with self.assertRaisesRegex(RuntimeError, "busy"):
                    wd.purge_sqlite_workspaces(parent)
                self.assertTrue(active.is_dir())
                self.assertTrue(stale.is_dir())
            self.assertEqual(wd.purge_sqlite_workspaces(parent)["removed"], [stale.name])

    def test_unknown_memory_invalid_and_other_owner_skipped(self):
        with tempfile.TemporaryDirectory() as area:
            parent = Path(area)
            unknown = self.cache(parent, "unknown")
            (unknown / "keep.txt").write_text("not owned by this cleanup")
            invalid = self.cache(parent, "invalid")
            (invalid / wd.WORKSPACE_MARKER).write_text("{bad JSON")
            foreign = self.cache(parent, "foreign")
            marker = wd.workspace_identity("sqlite")
            marker["user"] += "_another_user"
            (foreign / wd.WORKSPACE_MARKER).write_text(json.dumps(marker))
            memory = self.cache(parent, "memory")
            (memory / wd.WORKSPACE_MARKER).write_text(json.dumps(wd.workspace_identity("memory")))
            result = wd.purge_sqlite_workspaces(parent)
            self.assertEqual(result["removed"], [])
            self.assertEqual(len(result["skipped"]), 4)
            self.assertTrue((unknown / "keep.txt").is_file())
            self.assertTrue(all(path.is_dir() for path in [unknown, invalid, foreign, memory]))

    def test_legacy_cache_policy(self):
        with tempfile.TemporaryDirectory() as area:
            parent = Path(area)
            root = self.cache(parent, marked=False)
            result = wd.purge_sqlite_workspaces(parent)
            self.assertEqual(result["removed"], [] if os.name == "nt" else [root.name])
            self.assertEqual(root.exists(), os.name == "nt")

    def test_links_are_not_followed(self):
        with tempfile.TemporaryDirectory() as area:
            parent = Path(area)
            target = self.cache(parent, "target")
            link = parent / (wd.WORKSPACE_PREFIX + "linked")
            try:
                link.symlink_to(target, target_is_directory=True)
            except OSError:
                self.skipTest("Creating symlinks requires local OS permission")
            # Exclude the target itself from the cache prefix.
            renamed = parent / "outside"
            target.rename(renamed)
            link.unlink()
            link.symlink_to(renamed, target_is_directory=True)
            result = wd.purge_sqlite_workspaces(parent)
            self.assertEqual(result["removed"], [])
            self.assertTrue((renamed / "frames.sqlite").is_file())

    @unittest.skipUnless(hasattr(os, "getuid"), "Unix UID ownership check")
    def test_foreign_unix_owner_skipped(self):
        with tempfile.TemporaryDirectory() as area:
            parent = Path(area)
            root = self.cache(parent)
            with patch.object(wd.os, "getuid", return_value=os.getuid() + 1):
                self.assertEqual(wd.purge_sqlite_workspaces(parent)["removed"], [])
            self.assertTrue(root.exists())

    def test_purge_cli_works_without_capture_or_keys(self):
        with tempfile.TemporaryDirectory() as area:
            parent = Path(area)
            root = self.cache(parent)
            env = dict(os.environ, TMPDIR=area, TMP=area, TEMP=area)
            result = subprocess.run([sys.executable, str(MODULE), "--purge_sqlite"], env=env,
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Removed 1 SQLite workspace", result.stdout)
            self.assertFalse(root.exists())

    def test_cli_rejects_purge_with_capture_and_requires_capture_for_decode(self):
        for argv in [[], ["--purge_sqlite", "--pcap", "capture.pcap"], ["--purge_sqllite"], ["--purge-sqlite"]]:
            with self.subTest(argv=argv), patch.object(wd.sys, "stderr"):
                with self.assertRaises(SystemExit) as raised:
                    wd.parse_args(argv)
                self.assertEqual(raised.exception.code, 2)

    def test_concurrent_processes_and_killed_run_recovery(self):
        # Real independent Python processes share one controlled temp root.
        # Kill one without cleanup; its cache must survive while another is
        # active, then be removable after that other process finishes.
        worker = r'''
import importlib.util
from pathlib import Path
import sys
import time
spec = importlib.util.spec_from_file_location("decoder", sys.argv[1])
wd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wd)
with wd.temporary_workspace("sqlite") as root:
    store = wd.SqliteFrameStore(root / "frames.sqlite")
    try:
        wd.make_profile(root, "batch_0", [("tk", "ab" * 16)])
        Path(sys.argv[2]).write_text(str(root))
        while not Path(sys.argv[3]).exists():
            time.sleep(.02)
    finally:
        store.close()
'''
        with tempfile.TemporaryDirectory() as area:
            parent = Path(area)
            cache = parent / "cache"
            cache.mkdir()
            env = dict(os.environ, TMPDIR=str(cache), TMP=str(cache), TEMP=str(cache))
            processes = []
            try:
                roots = []
                for index in range(2):
                    ready, stop = parent / f"ready{index}", parent / f"stop{index}"
                    process = subprocess.Popen([sys.executable, "-c", worker, str(MODULE), str(ready), str(stop)],
                                               env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    processes.append(process)
                    deadline = time.monotonic() + 10
                    while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
                        time.sleep(.02)
                    self.assertTrue(ready.exists(), "Worker did not create its cache")
                    roots.append(Path(ready.read_text()))
                self.assertNotEqual(roots[0], roots[1])
                self.assertTrue(all((root / "frames.sqlite").is_file() for root in roots))
                processes[0].kill()
                processes[0].communicate(timeout=10)
                with self.assertRaisesRegex(RuntimeError, "busy"):
                    wd.purge_sqlite_workspaces(cache)
                self.assertTrue(all(root.exists() for root in roots))
                (parent / "stop1").touch()
                _, error = processes[1].communicate(timeout=10)
                self.assertEqual(processes[1].returncode, 0, error)
                self.assertFalse(roots[1].exists())
                result = wd.purge_sqlite_workspaces(cache)
                self.assertEqual(result["removed"], [roots[0].name])
                self.assertFalse(roots[0].exists())
            finally:
                for process in processes:
                    if process.poll() is None:
                        process.kill()
                    process.communicate(timeout=10)


if __name__ == "__main__":
    if sys.argv[1:] == ["--help_summary"]:
        print("Check manual SQLite workspace cleanup and active-run protection with synthetic data.")
    else:
        unittest.main()
