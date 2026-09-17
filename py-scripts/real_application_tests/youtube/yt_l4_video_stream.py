import selenium
import glob
import functools
import shutil
import zipfile
import os
import time
import socket
import argparse
import signal
import sys, platform
import atexit
import subprocess
import re
import random
import requests
import json
import traceback
import ctypes
import psutil
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import TimeoutException
from typing import Optional, Callable, Dict, Tuple
from abc import ABC, abstractmethod #PEP8 style, import only one pkg per line, unless its "from", import first, then from keyword after.

class Logger:
    """Tagged console logger with optional debug output."""
    def __init__(self, debug: bool = False):
        self.debug_enabled = debug

    def set_debug(self, val: bool):
        self.debug_enabled = val

    def info(self, msg: str):
        print(f"[INFO] {msg}", flush=True)

    def debug(self, msg: str):
        if self.debug_enabled:
            print(f"[DEBUG] {msg}", flush=True)

    def warn(self, msg: str):
        print(f"[WARN] {msg}", flush=True)

    def error(self, msg: str):
        print(f"[ERROR] {msg}", flush=True)

    def exception(self, msg: str):
        print(f"[EXCEPTION] {msg}", flush=True)
        traceback.print_exc()

logger = Logger(False)

def with_driver_resilience(max_attempts: int = 3, delay: float = 0.5, on_fail: Optional[Callable] = None, recover_driver: Optional[Callable] = None):
    """Retry decorator for Selenium actions. Handles dead sessions and attempts driver recovery."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exc = None
            for attempt in range(max_attempts):
                if not getattr(self, "driver", None):
                    print(f"{func.__name__}: no driver available")

                    if recover_driver:
                        try:
                            self.driver = recover_driver(self)
                        except Exception as e:
                            logger.exception(f"Driver recovery failed: {e}")
                            return None
                    else:
                        return None
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_exc = e
                    msg = str(e).lower()
                    driver_dead = (
                        "invalid session" in msg or
                        "session deleted" in msg or
                        "connection" in msg or
                        "disconnected" in msg
                    )
                    if driver_dead:
                        print(f"{func.__name__}: driver died")
                        try:
                            if recover_driver:
                                self.driver = recover_driver(self)
                            else:
                                self.driver = None
                        except Exception as rec_err:
                            print(f"Recovery failed: {rec_err}", flush=True)
                            return None
                        return None
                    if attempt < max_attempts - 1:
                        if on_fail:
                            try:
                                on_fail(self, *args, **kwargs)
                            except Exception:
                                logger.exception("Caught Exception")

                        time.sleep(delay)
                        continue
            print(f"{func.__name__} failed after {max_attempts}: {last_exc}")
            return None
        return wrapper
    return decorator

def _download_with_fallback(url: str, dest: str, host_hint: str = "") -> bool:
    """Download file using requests first, curl fallback second."""
    try:
        with requests.get(url, stream=True, timeout=15) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return True

    except Exception as e:
        logger.exception("Caught Exception")
        print(f"requests failed: {e}")
    try:
        result = subprocess.run(
            ["curl", "-L", "-o", dest, url, "--fail"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return True

        print(f"curl failed: {result.stderr.strip()}")

    except Exception:
        logger.exception("curl error")

    return False

class OSContext:
    """
    System environment snapshot used to get browser selection,
    installation, and platform-specific behavior. Detects OS, distro,
    architecture, available browsers/drivers, RAM, display, and
    status at construction time.
    """
    __slots__ = (
        "os_type", "distro", "distro_version", "distro_major", "arch",
        "pkg_manager", "is_containerized","has_display", "can_sudo", "ram_gb",
        "windows_build","firefox_version", "chrome_version","firefox_path", 
        "chrome_path","geckodriver_path", "chromedriver_path","supports_snap_firefox",
        "is_deprecated_distro","is_low_ram",
    )
    
    _CFT_BASE = {
        "win32":  r"C:\Program Files (x86)\LANforge-Server\CfT",
        "darwin": "/Users/lanforge/CfT",
        "linux":  "/home/lanforge/CfT",
    }

    _PATHS = {
        "firefox": {
            "win32":   [r"C:\Program Files\Mozilla Firefox\firefox.exe", "firefox"],
            "darwin":  ["/Applications/Firefox.app/Contents/MacOS/firefox", "firefox"],
            "fedora":  ["/usr/bin/firefox", "firefox"],
            "debian":  ["/usr/bin/firefox-esr", "/usr/bin/firefox", "firefox-esr", "firefox"],
            "ubuntu":  ["/usr/bin/firefox-esr", "/usr/bin/firefox", "firefox-esr", "firefox"],
        },
        "chrome": {
            "win32": [
                r"C:\Program Files (x86)\LANforge-Server\CfT\chrome.exe",
                r"C:\Program Files (x86)\LANforge-Server\CfT\chrome-win64\chrome.exe",
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                "chrome",
            ],
            "darwin": [
                "/Users/lanforge/CfT/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
                "/Users/lanforge/CfT/chrome",
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "google-chrome",
            ],
            "fedora": [
                "/home/lanforge/CfT/chrome",
                "/home/lanforge/CfT/chrome-linux64/chrome",
                "/usr/bin/google-chrome",
                "/opt/google/chrome/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
                "google-chrome",
                "chromium",
            ],
            "debian": [
                "/home/lanforge/CfT/chrome",
                "/home/lanforge/CfT/chrome-linux64/chrome",
                "/usr/bin/google-chrome",
                "/opt/google/chrome/google-chrome",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "google-chrome",
                "chromium",
            ],
            "ubuntu": [
                "/home/lanforge/CfT/chrome",
                "/home/lanforge/CfT/chrome-linux64/chrome",
                "/usr/bin/google-chrome",
                "/opt/google/chrome/google-chrome",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "google-chrome",
                "chromium",
            ],
        },
    }

    @property
    def cft_dir(self):
        if self.os_type == "win32":
            return self._CFT_BASE["win32"]
        if self.os_type == "darwin":
            return self._CFT_BASE["darwin"]
        return self._CFT_BASE["linux"]

    @property
    def is_cft(self):
        if not self.chrome_path:
            return False
        return self.chrome_path.startswith(self.cft_dir)

    @property
    def is_windows(self):
        return self.os_type == "win32"

    @property
    def is_macos(self):
        return self.os_type == "darwin"

    @property
    def is_debian_based(self):
        return self.distro in ("debian", "ubuntu")

    @property
    def is_fedora_based(self):
        return self.distro in ("fedora")

    @property
    def is_aarch64(self):
        return self.arch in ("aarch64", "arm64")

    def __init__(self):
        self.os_type = sys.platform
        self.arch = platform.machine()

        self.distro, self.distro_version = self._detect_distro()
        self.distro_major = self._parse_major(self.distro_version)

        self.pkg_manager = self._detect_pkg_manager()
        self.has_display = self._check_display()
        self.can_sudo = self._check_sudo()

        self.windows_build = self._detect_windows_build()

        self.firefox_path, self.firefox_version = self._find_browser("firefox")
        self.chrome_path, self.chrome_version = self._find_browser("chrome")

        self.geckodriver_path = self._find_executable("geckodriver")
        self.chromedriver_path = self._find_executable("chromedriver")

        self.ram_gb = self._get_ram()
        self.is_low_ram = 0 < self.ram_gb < 4

        self.is_containerized = os.path.exists("/.dockerenv")

        self.supports_snap_firefox = (
            self.is_debian_based and shutil.which("snap") is not None
        )

        self.is_deprecated_distro = self._detect_deprecation()

    def report(self) -> None:
        """Print details for debug output."""
        print("OS CONTEXT REPORT")
        print(f"OS: {self.os_type} | {self.distro} {self.distro_version} (major {self.distro_major})")
        print(f"Arch: {self.arch}")
        print(f"RAM: {self.ram_gb:.2f} GB | low_ram={self.is_low_ram}")
        print(f"Container: {self.is_containerized}")

        print("\nEnvironment")
        print(f"display={self.has_display} sudo={self.can_sudo} pkg={self.pkg_manager} win_build={self.windows_build}")

        print("\nBrowsers")
        print(f"chrome={self.chrome_path} (v{self.chrome_version})")
        print(f"firefox={self.firefox_path} (v{self.firefox_version})")

        print("\nDrivers")
        print(f"chromedriver={self.chromedriver_path}")
        print(f"geckodriver={self.geckodriver_path}")

        print("\nFlags")
        print(
            f"snap_firefox={self.supports_snap_firefox} "
            f"deprecated={self.is_deprecated_distro}"
        )

    def _is_branded_chrome(self) -> bool:
        """Return True if chrome_path points to Google Chrome, not CfT or Chromium."""
        if not self.chrome_path:
            return False
        try:
            out = subprocess.run(
                [self.chrome_path, "--version"],
                capture_output=True, text=True, timeout=5
            )
            return "Google Chrome" in out.stdout and "for Testing" not in out.stdout
        except Exception:
            return False

    def kill_process(self, *names: str) -> None:
        """Kill browser and driver processes by name across platforms."""
        try:
            if self.is_windows:
                for name in names:
                    subprocess.run(
                        ["taskkill", "/F", "/IM", f"{name}.exe"],
                        capture_output=True
                    )
            else:
                for name in names:
                    subprocess.run(
                        ["pkill", "-f", name],
                        capture_output=True
                    )
        except Exception:
            logger.exception("Caught Exception")

    def clean_temp(self, patterns: list[str]) -> None:
        """Remove temp files and directories matching glob patterns."""
        for pattern in patterns:
            for path in glob.glob(pattern):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
                    else:
                        os.remove(path)
                except Exception:
                    logger.exception("Caught Exception")

    def _detect_distro(self):
        if self.os_type == "win32":
            return "windows", platform.version()

        if self.os_type == "darwin":
            return "macos", platform.mac_ver()[0]

        try:
            info = {}
            with open("/etc/os-release") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        info[k] = v.strip('"')

            return info.get("ID", "unknown"), info.get("VERSION_ID", "0")

        except Exception:
            logger.exception("Caught Exception")

    def _parse_major(self, version: str) -> int:
        try:
            return int(version.split(".")[0])
        except Exception:
            logger.exception("Caught Exception")

    def _detect_deprecation(self) -> bool:
        try:
            if self.distro in ("ubuntu", "debian"):
                return self.distro_major < 20
            if self.distro in ("fedora",):
                return self.distro_major < 36
        except Exception:
            logger.exception("Caught Exception")
        return False

    def _detect_pkg_manager(self):
        if self.os_type == "win32":
            return None
        if self.os_type == "darwin":
            return "brew" if shutil.which("brew") else None
        if shutil.which("dnf"):
            return "dnf"
        if shutil.which("apt-get"):
            return "apt"
        return None

    def _check_display(self):
        if self.os_type in ("win32", "darwin"):
            return True
        return bool(os.environ.get("DISPLAY"))

    def _check_sudo(self):
        if self.os_type in ("win32", "darwin"):
            return self.os_type == "darwin"
        try:
            return subprocess.run(
                ["sudo", "-n", "true"],
                capture_output=True,
                timeout=3
            ).returncode == 0
        except Exception:
            logger.exception("Caught Exception")

    def _detect_windows_build(self):
        if self.os_type != "win32":
            return 0
        try:
            return int(platform.version().split(".")[-1])
        except Exception:
            logger.exception("Caught Exception")

    def _get_ram(self) -> float:
        try:
            if os.path.exists("/proc/meminfo"):
                with open("/proc/meminfo") as f:
                    for line in f:
                        if line.startswith("MemTotal"):
                            kb = int(line.split()[1])
                            return kb / 1024 / 1024

            if self.os_type == "darwin":
                out = subprocess.check_output(["sysctl", "-n", "hw.memsize"])
                return int(out) / 1024 / 1024 / 1024

            if self.os_type == "win32":

                class Mem(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                    ]

                m = Mem()
                m.dwLength = ctypes.sizeof(Mem)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
                return m.ullTotalPhys / 1024 / 1024 / 1024

        except Exception:
           logger.exception("Caught Exception")

        return 0.0

    def _find_browser(self, key: str):
        candidates = self._candidates_for(key)

        for cmd in candidates:
            path = shutil.which(cmd) or (cmd if os.path.exists(cmd) else None)
            if path:
                try:
                    out = subprocess.run(
                        [path, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    version_str = out.stdout.strip().split()[-1]
                    return path, version_str
                except Exception:
                    return path, ""

        return None, ""

    def _find_executable(self, name: str):
        cft = self.cft_dir
        if self.os_type == "win32":
            name_exe = name if name.endswith(".exe") else f"{name}.exe"
        else:
            name_exe = name

        cft_path = os.path.join(cft, name_exe)
        if os.path.exists(cft_path):
            return cft_path

        return shutil.which(name)

    def _candidates_for(self, key):
        table = self._PATHS.get(key)
        if not table:
            logger.error(f"No path table for browser: {key}")
            return []

        candidates = table.get(self.os_type) or table.get(self.distro)

        if candidates is None:
            logger.error(
                f"Unsupported OS/distro for {key}: "
                f"os_type={self.os_type}, distro={self.distro}"
            )
            return []

        return candidates

class BrowserInstaller:
    """
    Handles download and extraction of Chrome for Testing and 
    chromedriver. Falls back to manual install instructions when
    downloads fail or the platform has no CfT builds (AT7).
    """
    def __init__(self, ctx: OSContext):
        self.ctx = ctx
        self.CFT_VER = ["148.0.7778.167"]

    def install_chrome(self) -> bool:
        if self.ctx.is_debian_based and self.ctx.is_aarch64:
            logger.info("CfT unavailable for linux-arm64. Install Chromium manually:\n"
                        "  sudo apt-get install -y chromium chromium-driver")
            return False

        platform_map = {
            ("win32", "AMD64"):     "win64",
            ("win32", "x86"):       "win32",
            ("darwin", "arm64"):    "mac-arm64",
            ("darwin", "x86_64"):   "mac-x64",
            ("linux", "x86_64"):    "linux64",
        }

        os_key = self.ctx.os_type if self.ctx.is_windows else (
            "darwin" if self.ctx.is_macos else "linux"
        )
        plat = platform_map.get((os_key, self.ctx.arch))

        if not plat:
            logger.error(f"No CfT build for {os_key}/{self.ctx.arch}")
            return False

        cft_dir = self.ctx.cft_dir
        os.makedirs(cft_dir, exist_ok=True)

        chrome_bin = "chrome.exe" if self.ctx.is_windows else "chrome"
        if os.path.exists(os.path.join(cft_dir, chrome_bin)):
            logger.info(f"CfT already installed at {cft_dir}")
            return True

        try:
            r = requests.get(
                "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json",
                timeout=15
            )
            r.raise_for_status()
            version = r.json()["channels"]["Stable"]["version"]
        except Exception:
            logger.exception("Failed to fetch CfT version info")
            self._cft_install_help(plat, version)
            return False

        version = self._get_cft_version()
        logger.info(f"Downloading CfT {version} for {plat}")

        if not self._try_download_version(version, plat, cft_dir):
            logger.warn(f"CfT {version} failed, trying fallbacks")
            success = False
            for fallback in self.CFT_VER:
                if fallback != version:
                    logger.info(f"Trying CfT {fallback}")
                    if self._try_download_version(fallback, plat, cft_dir):
                        version = fallback
                        success = True
                        break
            if not success:
                self._cft_install_help(plat, version)
                return False

        nested = os.path.join(cft_dir, f"chrome-{plat}")
        if os.path.isdir(nested):
            for item in os.listdir(nested):
                src = os.path.join(nested, item)
                dst = os.path.join(cft_dir, item)
                if not os.path.exists(dst):
                    shutil.move(src, dst)
            shutil.rmtree(nested, ignore_errors=True)

        nested_driver = os.path.join(cft_dir, f"chromedriver-{plat}")
        if os.path.isdir(nested_driver):
            for item in os.listdir(nested_driver):
                src = os.path.join(nested_driver, item)
                dst = os.path.join(cft_dir, item)
                if not os.path.exists(dst):
                    shutil.move(src, dst)
            shutil.rmtree(nested_driver, ignore_errors=True)

        if not self.ctx.is_windows:
            for item in os.listdir(cft_dir):
                p = os.path.join(cft_dir, item)
                if os.path.isfile(p):
                    os.chmod(p, 0o755)

            for name in ["chrome", "chromedriver", "chrome_crashpad_handler"]:
                p = os.path.join(cft_dir, name)
                if os.path.exists(p):
                    mode = oct(os.stat(p).st_mode)
                    logger.info(f"  {name}: {mode}")

        logger.info(f"CfT {version} installed to {cft_dir}")
        return True

    def _get_cft_version(self) -> str:
        try:
            r = requests.get(
                "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json",
                timeout=15
            )
            r.raise_for_status()
            return r.json()["channels"]["Stable"]["version"]
        except Exception:
            logger.exception("Failed to fetch CfT version, using fallback")
            return self.CFT_VER[0]

    def _try_download_version(self, version: str, plat: str, cft_dir: str) -> bool:
        base_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/{plat}"
        for component in ["chrome", "chromedriver"]:
            zip_name = f"{component}-{plat}.zip"
            zip_url = f"{base_url}/{zip_name}"
            zip_path = os.path.join(cft_dir, zip_name)
            if not _download_with_fallback(zip_url, zip_path):
                logger.error(f"Failed to download {zip_url}")
                return False
            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(cft_dir)
                os.remove(zip_path)
            except Exception:
                logger.exception(f"Failed to extract {zip_name}")
                return False
        return True

    def _cft_install_help(self, plat: str, version: str = ""):
        ver = version or "<VERSION>"
        base = f"https://storage.googleapis.com/chrome-for-testing-public/{ver}/{plat}"
        cft_dir = self.ctx.cft_dir

        logger.error("Automatic CfT download failed. Manual steps:")
        logger.error(f"  1. From a machine with internet, download:")
        logger.error(f"     {base}/chrome-{plat}.zip")
        logger.error(f"     {base}/chromedriver-{plat}.zip")
        logger.error(f"  2. Copy both zips to this machine")
        logger.error(f"  3. Extract into {cft_dir}/")
        logger.error(f"  4. Verify {cft_dir}/chrome and {cft_dir}/chromedriver exist")
        if not self.ctx.is_windows:
            logger.error(f"  5. chmod +x {cft_dir}/chrome {cft_dir}/chromedriver")
        logger.error(f"")
        logger.error(f"  Latest version lookup:")
        logger.error(f"     https://googlechromelabs.github.io/chrome-for-testing/")

    def install_chromedriver(self) -> bool:
        if self.ctx.is_debian_based and self.ctx.is_aarch64:
            logger.info("Install chromedriver via apt:\n"
                        "  sudo apt-get install -y chromium-driver")
            return False

        cft_dir = self.ctx.cft_dir
        driver_name = "chromedriver.exe" if self.ctx.is_windows else "chromedriver"
        driver_path = os.path.join(cft_dir, driver_name)

        if os.path.exists(driver_path):
            logger.info(f"chromedriver found at {driver_path}")
            return True

        if self.install_chrome():
            if os.path.exists(driver_path):
                return True

        logger.error(f"chromedriver not found at {driver_path}")
        logger.error("Run install_chrome first, or place chromedriver manually in the CfT directory.")
        return False


    def install_firefox(self) -> bool:
        if self.ctx.is_windows:
            logger.info("Install Firefox via LANforge Windows installer MSI.")
            return False

        if self.ctx.is_macos:
            logger.info("Install Firefox manually:\n  brew install --cask firefox && brew install geckodriver")
            return False

        if self.ctx.supports_snap_firefox:
            logger.info("Replace snap Firefox manually:\n  sudo snap remove firefox\n  sudo add-apt-repository ppa:mozillateam/ppa\n  sudo apt-get install -y -t o=LP-PPA-mozillateam firefox")
            return False

        if self.ctx.is_fedora_based:
            logger.info("Install Firefox manually:\n  sudo dnf install -y firefox geckodriver")
            return False

        if self.ctx.is_debian_based:
            pkg = "firefox-esr" if self.ctx.distro_major >= 20 else "firefox"
            logger.info(f"Install Firefox manually:\n  sudo apt-get install -y {pkg} firefox-geckodriver")
            return False

        logger.info("Install Firefox manually from https://www.mozilla.org/")
        return False
class TelnetMixin:
    """Manages TCP connections to mgmt port for reporting."""
    def __init__(self):
        self._telnet_sockets: Dict[int, socket.socket] = {}

    def telnet_connect(self, port: int, timeout: int = 5):
        sock = self._telnet_sockets.get(port)
        if sock and self._is_alive(sock):
            return sock
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect(("127.0.0.1", port))
            self._telnet_sockets[port] = sock
            logger.info(f"Connected to {port}")
            return sock
        except Exception:
            logger.exception("Caught Exception")
            return None

    def telnet_cmd(self, sock, command: bytes):
        if not sock:
            return False
        try:
            sock.sendall(command + b"\n")
            return True
        except Exception:
            logger.exception("telnet send failed")
            self._invalidate_socket(sock)
            return False

    def _invalidate_socket(self, sock):
        try:
            sock.close()
        except Exception:
            logger.exception("Caught Exception")

class NetworkAffinityMixin:
    """
    Windows-specific mixin that demotes Ethernet interface metrics so WiFi
    traffic is preferred during testing, then restores original metrics on cleanup.
    """
    def __init__(self):
        self._saved_metrics: Dict[str, int] = {}

    def toggle_ethernet_priority(self, demote: bool = True) -> None:

        if not getattr(self, "ctx", None) or not self.ctx.is_windows:
            return
        try:
            ps_get = """
            Get-NetIPInterface |
            Where-Object {
                $_.InterfaceAlias -like "*Ethernet*" -and $_.AddressFamily -eq "IPv4"
            } |
            Select-Object InterfaceAlias, InterfaceMetric |
            ConvertTo-Json
            """
            res = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_get],
                capture_output=True,
                text=True
            )
            if not res.stdout.strip():
                print("No Ethernet interfaces found.")
                return
            data = json.loads(res.stdout)
            if isinstance(data, dict):
                data = [data]
            for iface in data:
                name = iface["InterfaceAlias"]
                current_metric = int(iface["InterfaceMetric"])
                if name not in self._saved_metrics:
                    self._saved_metrics[name] = current_metric
                new_metric = 100 if demote else self._saved_metrics[name]
                set_cmd = f"""
                Set-NetIPInterface -InterfaceAlias "{name}" -InterfaceMetric {new_metric}
                """
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", set_cmd],
                    capture_output=True
                )
                print(f"{name}: metric {current_metric} → {new_metric}")
        except Exception:
            logger.exception("Caught Exception")

class StatsParser:
    """
    Extracts resolution, bitrate, network activity, and buffer stats
    from Stats for Nerds overlay and formats them for reporting.
    """
    def __init__(self, ctx):
        self.ctx = ctx

        self.bytes_read = 0
        self.buffer_count = 0
        self.rebuffer_count = 0
        self.total_wait_time = 0
        self.is_currently_buffering = False

    @staticmethod
    def extract_bitrate(codec_string: str) -> int:

        cid = "".join(ch for ch in codec_string if ch.isdigit())
        val = BitrateMap.DATA.get(cid, 0)
        return val[0] if isinstance(val, tuple) else val

    def parse_stats(self, stats_text: str) -> str:
            
            if not stats_text:
                logger.debug("parse_stats: empty stats_text received")
                return ""

            stats_text = stats_text.replace(" ", "")
            buf = []

            res_m = re.search(r"(\d+)x(\d+)@(\d+)", stats_text)
            if res_m:
                buf.append(
                    f"width={res_m.group(1)},"
                    f"height={res_m.group(2)},"
                    f"Frame-Rate={res_m.group(3)}"
                )

            bit_m = re.search(r"\((\d+)\)/.*\((\d+)\)", stats_text)
            if bit_m:
                buf.append(
                    f"Video-Format-Bitrate={self.extract_bitrate(bit_m.group(1))},"
                    f"Audio-Format-Bitrate={self.extract_bitrate(bit_m.group(2))}"
                )

            if self.ctx.is_aarch64:
                self.bytes_read = 0
            else:
                net_idx = stats_text.find("NetworkActivity")
                if net_idx != -1:
                    chunk = stats_text[net_idx:net_idx + 80]
                    net_m = re.findall(r"([\d.]+)(KB|MB|GB)", chunk)

                    if net_m:
                        val, unit = net_m[-1]
                        mult = {
                            "KB": 1_000,
                            "MB": 1_000_000,
                            "GB": 1_000_000_000,
                        }
                        self.bytes_read = int(float(val) * mult[unit])

            buf.append(f"Bytes-RD={self.bytes_read}")
            buf.append(
                f"Total-Buffers={self.buffer_count},"
                f"Total-Rebuffers={self.rebuffer_count},"
                f"Total-Wait-Time={self.total_wait_time}"
            )

            return ",".join(buf)

class BitrateMap:
    """Maps YouTube itag -> bitrate."""
    DATA = {
        "139": (48, 48), "140": (128, 128), "141": (256, 256),
        "171": (128, 128), "249": (50, 50), "250": (70, 70), "251": (160, 160),
        "256": (192, 192), "258": (384, 384), "327": (256, 256), "338": (480, 480),
        "5": (200, 400), "6": (400, 600), "17": (50, 150), "18": (500, 800), "22": (1000, 2000),
        "34": (300, 600), "35": (600, 1000), "36": (100, 250), "37": (3000, 5000), "38": (8000, 15000),
        "43": (500, 800), "44": (800, 1200), "45": (1500, 2500), "46": (3000, 5000),
        "82": (500, 800), "83": (800, 1200), "84": (1500, 2500), "85": (3000, 5000),
        "100": (500, 800), "101": (800, 1200), "102": (1500, 2500),
        "92": (150, 300), "93": (300, 600), "94": (600, 1000), "95": (1500, 2500),
        "96": (3000, 5000),
        "132": (150, 300), "151": (50, 100),
        "133": (200, 500), "134": (400, 800), "135": (800, 1500),
        "136": (1500, 2500), "137": (3000, 5000), "138": (12000, 20000),
        "160": (80, 150), "264": (8000, 15000), "266": (15000, 30000),
        "298": (2500, 4000), "299": (5000, 8000),
        "167": (400, 800), "168": (800, 1500), "169": (3000, 5000),
        "218": (800, 1500), "219": (80, 150),
        "242": (150, 300), "243": (300, 600), "244": (600, 1000),
        "245": (600, 1000), "246": (600, 1000), "247": (1500, 2500),
        "248": (2500, 4000),
        "271": (8000, 12000), "272": (15000, 25000),
        "278": (80, 150),
        "302": (2000, 3500), "303": (4000, 6500),
        "308": (12000, 20000), "313": (15000, 25000),
        "315": (25000, 45000),
        "330": (100, 200), "331": (200, 400), "332": (400, 800),
        "333": (800, 1500), "334": (2000, 3500),
        "335": (4000, 6500), "336": (12000, 20000),
        "337": (25000, 45000),
        "394": (100, 200), "395": (200, 400), "396": (400, 800),
        "397": (800, 1500), "398": (1500, 2500),
        "399": (3000, 5000), "400": (8000, 15000),
        "401": (15000, 25000), "402": (25000, 45000),
        "571": (25000, 45000), "702": (30000, 50000),
        "228": (50, 100), "598": (80, 300), "599": (100, 300),
        "600": (50, 150),
        "779": (800, 1500), "780": (800, 1500), "788": (800, 1500),
    }

    _DEFAULT = (0, 0)

    @classmethod
    def get(cls, itag: str):
        """Safe lookup. Always returns (min_bitrate, max_bitrate)"""
        return cls.DATA.get(itag, cls._DEFAULT)
class BrowserBase(ABC):
    """
    Abstract base for browser implementations. Defines the interface for
    launching, extension management, anti-bot strategies, and cleanup.
    Subclassed by FireBrow and ChromeBrow.
    """
    browser_name: str = ""

    def __init__(self, ctx: OSContext):
        self.driver: Optional[webdriver.Remote] = None
        self._pending_extension: Optional[str] = None
        self.anti_bot: Dict[str, Callable] = {}
        self.ctx = ctx

    @abstractmethod
    def launch(self) -> webdriver.Remote:
        raise NotImplementedError

    @abstractmethod
    def install_extension(self, ext_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def download_extension(self) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def kill_processes(self) -> None:
        raise NotImplementedError

    def clean_tmp(self) -> None:
        return
    
    def verify_extension(self, driver) -> bool:
        return True

    @classmethod
    def register_anti_bot(cls, name: str):
        def decorator(func: Callable):
            if not hasattr(cls, "_anti_bot_registry"):
                cls._anti_bot_registry = {}

            cls._anti_bot_registry[name] = func
            return func
        return decorator

    def run_anti_bot(self, driver) -> None:
        registry = getattr(self.__class__, "_anti_bot_registry", {})

        for name, strategy in registry.items():
            try:
                strategy(self, driver)
            except Exception:
                logger.exception("Caught Exception")
    
    def attach(self, driver):
        self.driver = driver

    def close(self):
        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            logger.exception("Caught Exception")

        self.driver = None
        self.kill_processes()

class FireBrow(BrowserBase):
    """Firefox browser implementation."""
    browser_name = "firefox"

    def __init__(self, ctx: OSContext):
        super().__init__(ctx)
        self.ctx = ctx
        self.options = FirefoxOptions()
        self._configure_options()

    def _configure_options(self) -> None:
        self.options.add_argument("--width=1920")
        self.options.add_argument("--height=1080")
        if self.ctx.firefox_path:
            self.options.binary_location = self.ctx.firefox_path
        self.options.set_preference("media.navigator.enabled", False)
        self.options.set_preference("privacy.trackingprotection.enabled", False)
        self.options.set_preference("network.http.sendRefererHeader", 2)

    def launch(self) -> webdriver.Firefox:
        service = None

        if self.ctx.geckodriver_path:
            service = FirefoxService(self.ctx.geckodriver_path)

        self.driver = (
            webdriver.Firefox(service=service, options=self.options)
            if service
            else webdriver.Firefox(options=self.options)
        )

        if self._pending_extension:
            self.install_extension(self._pending_extension)
            self._pending_extension = None

        return self.driver

    def install_extension(self, ext_path: str) -> None:
        if not ext_path or not os.path.exists(ext_path):
            return

        if not self.driver:
            self._pending_extension = ext_path
            return

        try:
            self.driver.install_addon(ext_path, temporary=True)
        except Exception:
            logger.exception("Caught Exception")

    def download_extension(self) -> Optional[str]:
        xpi_path = os.path.join(os.getcwd(), "ublock_origin.xpi")

        if os.path.exists(xpi_path):
            return xpi_path

        ff_version = self.ctx.firefox_version

        if ff_version < 115:
            url = "https://addons.mozilla.org/firefox/downloads/file/4141256/ublock_origin-1.51.0.xpi"
        else:
            url = "https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/latest.xpi"

        _download_with_fallback(url, xpi_path, "addons.mozilla.org")
        return xpi_path

    def kill_processes(self) -> None:
        self.ctx.kill_process("firefox", "geckodriver")

    def clean_tmp(self) -> None:
        if self.ctx.is_aarch64:
            self.ctx.clean_temp(["/tmp/rust_mozprofile*"])


@FireBrow.register_anti_bot("mouse_jitter")
def _ff_mouse_jitter(self, driver):
    actions = ActionChains(driver)
    for _ in range(random.randint(2, 4)):
        try:
            actions.move_by_offset(
                random.randint(-5, 5),
                random.randint(-5, 5)
            ).perform()
            time.sleep(random.uniform(0.15, 0.4))
        except Exception:
            logger.exception("Caught Exception")

class ChromeBrow(BrowserBase):
    """Chromium browser implementation."""
    browser_name = "chrome"

    def __init__(self, args, ctx: OSContext, e_id: str = "default"):
        super().__init__(ctx)
        self.args = args
        self.ctx = ctx
        self.e_id = e_id
        self.options = ChromeOptions()
        self._pending_extension: Optional[str] = None

        if ctx.chrome_path:
            self.options.binary_location = ctx.chrome_path

    def launch(self) -> webdriver.Chrome:
        """Launch Chrome with fully prepared profile + extension state."""
        profile_dir = f"/tmp/chrome-profile-{self.e_id}"
        for stale in ["SingletonLock", "SingletonCookie", "SingletonSocket"]:
            p = os.path.join(profile_dir, stale)
            try:
                os.remove(p)
            except FileNotFoundError:
                pass
            except OSError:
                pass

        self._apply_base_profile()

        # Define a custom runtime environment variable
        my_env = os.environ.copy()
        if self.args.ld_preload:
            my_env["LD_PRELOAD"] = self.args.ld_preload
        if self.args.servers_csv:
            my_env["SERVERS_CSV"] = self.args.servers_csv
        if self.args.my_resolv_conf:
            my_env["RESOLV_WRAPPER_CONF"] = self.args.my_resolv_conf

        print("ld-preload: %s  servers-csv: %s" % (my_env.get("LD_PRELOAD", "None"), my_env.get("SERVERS_CSV", "None")))

        if self._pending_extension and os.path.exists(self._pending_extension):
            logger.info(f"Loading unpacked extension at startup: {self._pending_extension}")
            self.options.add_argument(f"--load-extension={self._pending_extension}")
            self._pending_extension = None
        else:
            logger.warn("No valid extension loaded at launch.")

        service = (
            ChromeService(executable_path=self.ctx.chromedriver_path, port=0, env=my_env)
            if getattr(self.ctx, 'chromedriver_path', None)
            else None
        )

        try:
            if service:
                self.driver = webdriver.Chrome(service=service, options=self.options)
            else:
                self.driver = webdriver.Chrome(options=self.options)
        except Exception:
            logger.exception("Failed to launch Chrome WebDriver")
            raise

        try:
            if hasattr(self, "verify_extension"):
                self.verify_extension(self.driver)
        except Exception:
            logger.exception("Extension verification failed (non-fatal)")

        return self.driver
    
    def _apply_base_profile(self) -> None:
        profile_dir = f"/tmp/chrome-profile-{self.e_id}"
        self.options.add_argument(f"--user-data-dir={profile_dir}")
        self.options.add_argument("--autoplay-policy=no-user-gesture-required")
        self.options.add_argument("--disable-background-timer-throttling")
        self.options.add_argument("--disable-renderer-backgrounding")
        self.options.add_argument("--disable-background-networking")
        self.options.add_argument("--disable-features=Translate,MediaRouter,NetworkChangeNotifier")
        self.options.add_argument("--disable-sync")
        self.options.add_argument("--no-first-run")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--hide-crash-restore-bubble")
        self.options.add_argument("--disable-session-crashed-bubble")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        self.options.add_argument("--disable-dev-shm-usage")

        if not self.ctx.is_windows:
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-setuid-sandbox")

        if self.ctx.is_low_ram:
            self.options.add_argument("--disable-gpu")
            self.options.add_argument("--process-per-site")
            self.options.add_argument("--renderer-process-limit=2")

    def verify_extension(self, driver) -> bool:
        for attempt in range(10):
            try:
                targets = driver.execute_cdp_cmd("Target.getTargets", {})
                for t in targets.get("targetInfos", []):
                    if "adguard" in t.get("url", "").lower():
                        logger.info("AdGuard verified: extension is loaded.")
                        return True
                    if "adguard" in t.get("title", "").lower():
                        logger.info("AdGuard verified: extension is loaded.")
                        return True
            except Exception:
                logger.exception("Extension verification failed")
                return False
            time.sleep(1)
        logger.warn("AdGuard NOT loaded. Ads may interrupt stats collection.")
        return False

    def install_extension(self, ext_path: str) -> None:
        if not ext_path or not os.path.exists(ext_path):
            logger.error(f"Extension path invalid or missing: {ext_path}")
            return
        self._pending_extension = ext_path

    def download_extension(self) -> Optional[str]:
        """Download and extract the zip. Caching locally to survive offline runs."""
        url = "https://raw.githubusercontent.com/goyalsaurabh06/lanforge-scripts/real_application_tests/py-scripts/real_application_tests/youtube/adguard.zip"
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        zip_path = os.path.join(base_dir, "adguard.zip")
        ext_folder = os.path.join(base_dir, "adguard")

        if os.path.exists(ext_folder):
            final_path = os.path.abspath(ext_folder)
            if os.path.exists(os.path.join(final_path, "manifest.json")):
                return final_path
            for item in os.listdir(final_path):
                subfolder = os.path.join(final_path, item)
                if os.path.isdir(subfolder) and "manifest.json" in os.listdir(subfolder):
                    return subfolder

        if not os.path.exists(zip_path):
            logger.info("Zip not found locally. Attempting manual curl download.")
            try:
                if self.ctx.is_fedora_based:
                    curl_env = { #small issue here, sometimes when subprocessing out this many times will
                                 # cause curl to use the wrong ldd, this was seen with libnghttp2.so14 vs libnghttp3.so.9
                        "LD_LIBRARY_PATH": "/home/lanforge/local/lib",
                        "PATH": "/usr/bin:/bin:/usr/local/bin"
                    }
                subprocess.run(
                    f"cd {base_dir} && curl -O {url}", 
                    shell=True,
                    env=curl_env,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to download AdGuard zip: {e}")
                return None
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(ext_folder)
        except zipfile.BadZipFile:
            logger.error("Corrupted zip detected. Delete it manually or check network.")
            try:
                os.remove(zip_path)
            except OSError:
                pass
            return None

        final_path = os.path.abspath(ext_folder)
        if not os.path.exists(os.path.join(final_path, "manifest.json")):
            for item in os.listdir(final_path):
                subfolder = os.path.join(final_path, item)
                if os.path.isdir(subfolder) and "manifest.json" in os.listdir(subfolder):
                    final_path = subfolder
                    break
        
        return final_path

    def kill_processes(self) -> None:
        profile_dir = f"/tmp/chrome-profile-{self.e_id}"
        try:
            for proc in psutil.process_iter(['pid', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if profile_dir in cmdline:
                        logger.info(f"kill_processes: killing PID {proc.pid} matched {profile_dir}")
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            logger.exception("Caught Exception")

    def clean_tmp(self) -> None:
        if getattr(self.ctx, "is_aarch64", False):
            if hasattr(self.ctx, "clean_temp"):
                self.ctx.clean_temp(["/tmp/chrome-session"])

@ChromeBrow.register_anti_bot("mouse_jitter")
def _cr_mouse_jitter(self, driver):
    try:
        if not driver.current_url or driver.current_url in ("data:,", "about:blank", ""):
            return
        actions = ActionChains(driver)
        for _ in range(random.randint(2, 4)):
            actions.move_by_offset(
                random.randint(-3, 3),
                random.randint(-3, 3)
            ).perform()
            time.sleep(random.uniform(0.1, 0.2))
    except Exception:
        pass

BROWSERS: Dict[str, type] = {
    "firefox": FireBrow,
    "chrome": ChromeBrow,
}

def create_browser(args, choice: str, ctx: OSContext, installer: BrowserInstaller, e_id: str = "default") -> BrowserBase:
    choice = (choice or "chrome").lower()

    if choice == "firefox":
        if not ctx.firefox_path:
            installer.install_firefox()
            raise RuntimeError("Firefox requested but not found.")
        return FireBrow(ctx)

    if choice in ("auto", "chrome", ""):
        if ctx.chrome_path and ctx._is_branded_chrome():
            logger.warn("Branded Chrome detected, --load-extension unsupported. Switching to CfT.")
            ctx.chrome_path = None
            ctx.chromedriver_path = None

        if not ctx.chrome_path:
            logger.info("Chrome not found. Attempting CfT install.")
            if installer.install_chrome():
                _resolve_cft_paths(ctx)

            if not ctx.chrome_path:
                raise RuntimeError("Chrome not found and CfT install failed.")

        if not ctx.chromedriver_path:
            logger.info("chromedriver not found. Checking CfT directory.")
            if installer.install_chromedriver():
                _resolve_cft_paths(ctx)

            if not ctx.chromedriver_path:
                raise RuntimeError("chromedriver not found and CfT install failed.")

        return ChromeBrow(args, ctx, e_id)

    raise ValueError(f"Invalid browser choice: {choice}")


def _resolve_cft_paths(ctx: OSContext):
    """Re-resolve chrome and chromedriver paths from the CfT directory."""
    cft_dir = ctx.cft_dir
    chrome_bin = "chrome.exe" if ctx.is_windows else "chrome"
    driver_bin = "chromedriver.exe" if ctx.is_windows else "chromedriver"

    chrome_path = os.path.join(cft_dir, chrome_bin)
    driver_path = os.path.join(cft_dir, driver_bin)

    if os.path.exists(chrome_path):
        ctx.chrome_path = chrome_path
        try:
            out = subprocess.run(
                [chrome_path, "--version"],
                capture_output=True, text=True, timeout=5
            )
            ctx.chrome_version = out.stdout.strip().split()[-1]
        except Exception:
            ctx.chrome_version = ""

    if os.path.exists(driver_path):
        ctx.chromedriver_path = driver_path

class VideoStream(TelnetMixin, NetworkAffinityMixin, StatsParser):
    """
    Main controller for YouTube video streaming tests. Manages browser
    lifecycle, ad-blocker setup, video playback, Stats for Nerds scraping,
    and telemetry reporting to the mgmt port.
    """
    __slots__ = ("debug","url","mgmt_ip","mgmt_port","proxy_ip","e_id","resolution",
            "duration","ctx","driver","sock","browser","wait","installer",
            "_telnet_sockets","_saved_metrics","bytes_read","buffer_count",
            "rebuffer_count","total_wait_time","is_currently_buffering",
            "_stats_api_available")

    def __init__(self, url, mgmt_ip, mgmt_port, proxy_ip, e_id, args, ctx: OSContext, 
                 browser_choice="auto", res="Auto", duration=0, debug=False):

        self.args = args
        self.ctx = ctx
        self.debug = debug
        self.url = url
        self.mgmt_ip = mgmt_ip
        self.mgmt_port = mgmt_port
        self.proxy_ip = proxy_ip
        self.e_id = e_id
        self.resolution = res
        self.duration = duration

        self._cleaned_up = False

        self.driver = None
        self.sock = None
        self.wait = None
        self._stats_api_available = None

        TelnetMixin.__init__(self)
        NetworkAffinityMixin.__init__(self)
        StatsParser.__init__(self, ctx)

        if self.ctx.is_low_ram:
            print(f"WARNING: Low RAM system detected ({self.ctx.ram_gb:.1f}GB)")

        self.installer = BrowserInstaller(self.ctx)

        browser_choice = (browser_choice or "chrome").lower()
        self.browser = create_browser(self.args, browser_choice, self.ctx, self.installer, self.e_id)

        try:
            ext_path = self.browser.download_extension()
            self.browser.install_extension(ext_path)
        except Exception:
            logger.exception("Caught Exception")

        self.sock = self.telnet_connect(int(mgmt_port))
        if not self.sock:
            raise RuntimeError(f"Cannot reach management port {mgmt_port}")

        self.driver = self.browser.launch()
        timeout = 40 if self.ctx.is_low_ram else 20 # we're going to be REALLY slow (at7 I hope you have more than 2gb of ram...)
        self.wait = WebDriverWait(self.driver, timeout)

        atexit.register(self.cleanup)
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)

    def cleanup(self):
        if self._cleaned_up:
            return
        self._cleaned_up = True

        if self.browser:
            try:
                self.browser.kill_processes()
            except Exception:
                logger.exception("Caught Exception")
            try:
                self.browser.close()
            except Exception:
                logger.exception("Caught Exception")

        if self.sock:
            try:
                self.sock.close()
            except Exception:
                logger.exception("Caught Exception")
            self.sock = None

    def sig_handler(self, sig, frame):
        print(f"Received signal {sig}, shutting down...")
        self.cleanup()
        sys.exit(0)

    def _open_context_menu(self):
        self.driver.execute_script("""
            const p = document.getElementById('movie_player');
            if (!p) return;

            const r = p.getBoundingClientRect();
            p.dispatchEvent(new MouseEvent('contextmenu', {
                bubbles: true,
                cancelable: true,
                view: window,
                clientX: r.left + r.width / 2,
                clientY: r.top + r.height / 2
            }));
        """)

    def _play_if_needed(self):
        self.driver.execute_script("""
            const v = document.querySelector('video');
            if (v && v.paused) v.play();
        """)

    def _wait_for_video(self):
        return self.wait.until(
            lambda d: d.execute_script(
                "return document.querySelector('video') !== null"
            )
        )

    def _wait_until_playing(self):
        return self.wait.until(
            lambda d: d.execute_script(
                "const v = document.querySelector('video'); return v && !v.paused;"
            )
        )

    def select_resolution(self):
        if self.resolution == "Auto":
            return True

        try:
            self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".ytp-settings-button"))
            ).click()
            menu = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".ytp-menuitem-label")
                )
            )
            for item in menu:
                if "Quality" in item.text:
                    item.click()
                    break
            qualities = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".ytp-menuitem-label")
                )
            )
            for q in qualities:
                if self.resolution in q.text:
                    q.click()
                    print(f"Resolution set to {self.resolution}")
                    return True

        except Exception:
            logger.exception("Caught Exception")

        return False

    def open_stats_for_nerds(self):
        if self.driver.find_elements(By.CSS_SELECTOR, ".html5-video-info-panel-content"):
            return True

        if self.driver.find_elements(By.CSS_SELECTOR, ".ad-showing, .ad-interrupting"):
            logger.warn("Ad playing, skipping stats for nerds.")
            return False

        self._open_context_menu()
        time.sleep(0.5)

        self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(text(),'Stats for nerds')]")
            )
        ).click()

        self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".html5-video-info-panel-content")
            )
        )

        return True

    @staticmethod
    def format_stats(raw_data):
        """Extract report fields from YouTube's Stats for Nerds text."""
        stats_data = (raw_data or "").replace(" ", "")
        viewport_match = re.search(
            r"Viewport/Frames([\d+x]+)(?:\*[\d.]+)?/"
            r"([\d]+)droppedof([\d]+)",
            stats_data,
        )
        current_optimal_res_match = re.search(
            r"Current/OptimalRes([\d@x]+)/([\d@x]+)", stats_data
        )
        data = {}
        if viewport_match:
            data["Viewport"] = viewport_match.group(1)
            data["DroppedFrames"] = viewport_match.group(2)
            data["TotalFrames"] = viewport_match.group(3)

        if current_optimal_res_match:
            data["CurrentRes"] = current_optimal_res_match.group(1)
            data["OptimalRes"] = current_optimal_res_match.group(2)

        buffer_health_match = re.search(r"BufferHealth([\d.]+)s", stats_data)
        if buffer_health_match:
            data["BufferHealth"] = buffer_health_match.group(1)

        data["Timestamp"] = datetime.now().strftime("%H:%M:%S")
        return data

    def send_stats_to_api(self, stats, ip, stop=False):
        """Best-effort reporting that never controls the playback loop."""
        url = "http://localhost:5002/youtube_stats"
        data = {
            str(ip): stats,
            "stop": stop,
        }

        try:
            response = requests.post(url, json=data, timeout=(1, 2))
            response.raise_for_status()
        except requests.RequestException as exc:
            if self._stats_api_available is not False:
                logger.warn(
                    "YouTube stats API unavailable; reporting disabled until "
                    f"recovery: {exc}"
                )
            else:
                logger.debug(f"YouTube stats API remains unavailable: {exc}")
            self._stats_api_available = False
            return False

        if self._stats_api_available is False:
            logger.info("YouTube stats API reporting recovered.")
        self._stats_api_available = True
        logger.debug(f"Reported YouTube stats for {ip}: {stats}")
        return True

    def enable_loop(self):
        self._open_context_menu()

        self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(text(),'Loop')]")
            )
        ).click()

    def start_video(self):
        self.driver.get(self.url)

        main_handle = self.driver.current_window_handle

        for h in self.driver.window_handles:
            if h != main_handle:
                self.driver.switch_to.window(h)
                txt = (self.driver.current_url + self.driver.title).lower()
                if any(k in txt for k in ["adguard", "ublock", "thank you", "welcome"]):
                    self.driver.close()

        self.driver.switch_to.window(main_handle)
        self.browser.run_anti_bot(self.driver)

        try:
            self.driver.find_element(
                By.XPATH,
                "//button[@aria-label='Accept all' or contains(., 'Accept all') or contains(., 'I agree')]"
            ).click()
        except Exception:
            logger.debug("No consent banner found, continuing.")

        self._wait_for_video()
        self._play_if_needed()
        self._wait_until_playing()

        if self.duration > 0:
            self.enable_loop()

        self.select_resolution()
        self.open_stats_for_nerds()

    def _check_youtube_error(self):
        try:
            body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            if any(phrase in body for phrase in (
                "something went wrong",
                "please try again later",
                "content isn't available",
                "try again later",
            )):
                print("YouTube error detected, retrying")

                self.driver.refresh()

                self._wait_for_video()
                self.browser.run_anti_bot(self.driver)

                self._play_if_needed()
                self._wait_until_playing()

                self.open_stats_for_nerds()
                return True

        except Exception:
            logger.exception("Caught Exception")

        return False

    def query_loop(self):
        log_path = os.path.join(os.getcwd(), "yt_stream.log")
        MAX_STATS_FAILURES = 5

        try:
            self.start_video()

            start_time = datetime.now()
            stats_failures = 0
            backoff = 1

            while True:
                if self.duration > 0:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed > self.duration * 60:
                        break

                try:
                    if self._check_youtube_error():
                        stats_failures = 0
                        backoff = 1
                        continue
                    stats_raw = self.driver.find_element(
                        By.CSS_SELECTOR,
                        ".html5-video-info-panel-content"
                    ).text
                    formatted_stats = self.format_stats(stats_raw)
                    self.send_stats_to_api(formatted_stats, self.proxy_ip)

                    ended = self.driver.execute_script("const v = document.querySelector('video'); return v && v.ended;")
                    if ended:
                        logger.info("Video ended, reloading.")
                        self.driver.get(self.url)
                        self._wait_for_video()
                        self._play_if_needed()
                        self._wait_until_playing()
                        self.open_stats_for_nerds()
                        continue

                    telnet_data = self.parse_stats(stats_raw)

                    if self.debug:
                        print(telnet_data)

                    try:
                        with open(log_path, "w") as lf:
                            lf.write(f"timestamp={datetime.now().isoformat()}\n")
                            lf.write(f"url={self.url}\n")
                            lf.write(f"browser={self.browser.browser_name}\n")
                            lf.write(f"{telnet_data}\n")
                    except Exception:
                        logger.exception("Caught Exception")

                    self.telnet_cmd(
                        self.sock,
                        b"admin yt_video_stream %b %b" % (
                            str(self.e_id).encode(),
                            telnet_data.encode()
                        )
                    )

                    stats_failures = 0
                    backoff = 1
                
                except TimeoutException:
                    stats_failures += 1
                    if stats_failures >= MAX_STATS_FAILURES:
                        print("Too many stats timeouts, reloading video.")
                        self.driver.get(self.url)
                        self._wait_for_video()
                        self._play_if_needed()
                        self._wait_until_playing()
                        stats_failures = 0
                        backoff = 1
                    time.sleep(min(backoff, 8))
                    backoff *= 2
                    continue

                except Exception as e:
                    stats_failures += 1

                    if stats_failures == 1 or stats_failures >= MAX_STATS_FAILURES:
                        print(f"Stats failure {stats_failures}/{MAX_STATS_FAILURES}: {e}")

                    if stats_failures >= MAX_STATS_FAILURES:
                        print("Too many failures → aborting")
                        break

                    if not self._check_youtube_error():
                        if self.driver.find_elements(By.CSS_SELECTOR, ".ad-showing, .ad-interrupting"):
                            logger.warn("Ad playing, waiting...")
                            time.sleep(5)
                        else:
                            self.open_stats_for_nerds()

                    time.sleep(min(backoff, 8))
                    backoff *= 2
                    continue

                if random.random() < 0.1:
                    self.browser.run_anti_bot(self.driver)

                time.sleep(1)

        finally:
            self.cleanup()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="yt_l4_video_stream.py",
        description="Video streaming for LANforge Layer 4-7 testing.",
    )

    parser.add_argument("-U", "--url", required=True)
    parser.add_argument("-M", "--mgmt", required=True)
    parser.add_argument("-P", "--port", type=int, default=4001)
    parser.add_argument("-B", "--bind", required=True)
    parser.add_argument("-ID", "--id", required=True)
    parser.add_argument("--browser",default="auto",
                        choices=["auto", "firefox", "chrome"],
                        help="Browser to use. Default: auto (prefers Chrome)")
    parser.add_argument("--res", default="Auto")
    parser.add_argument("--duration", type=int, default=0)
    parser.add_argument("-D", "--debug", action="store_true")

    parser.add_argument('--servers_csv', required=False, default="", help='Configure the DNS servers, when using ld-preload.')
    parser.add_argument('--ld_preload', required=False, default="", help='Configure the LD_PRELOAD library.')
    parser.add_argument('--my_resolv_conf', required=False, default="", help='Configure the RESOLV_WRAPPER_CONF env var, for resolv_wrapper.')

    args = parser.parse_args()

    # TODO:  Fix this to use tmp dir and take ID into account.
    DEBUG_FLAG_PATH = "/home/lanforge/.yt_l4_debug"

    disp = os.environ.get("LF_DISP") or os.environ.get("DISPLAY")
    if not disp:
        raise RuntimeError("No display found. Set LF_DISP in lanforge.profile or ensure DISPLAY is set.")
    os.environ["DISPLAY"] = disp

    if os.path.exists(DEBUG_FLAG_PATH):
        try:
            log_dir = "/tmp" if sys.platform != "win32" else os.environ.get("TEMP", "C:\\Temp")
            log_path = os.path.join(log_dir, f"yt_l4_{args.id}.log")
            log_file = open(log_path, "w", buffering=1)
            sys.stdout = log_file
            sys.stderr = log_file
        except Exception as e:
            sys.stderr.write(f"Failed to open log file {log_path}: {e}\n")

    ctx = OSContext()

    if args.debug or os.path.exists(DEBUG_FLAG_PATH):
        ctx.report()

    streamer = None

    try:
        browser_choice = args.browser.lower()

        if browser_choice == "auto":
            browser_choice = "chrome"

        streamer = VideoStream(args.url,args.mgmt,args.port,args.bind,
                               args.id, args, ctx=ctx, browser_choice=browser_choice,
                               res=args.res,duration=args.duration,debug=args.debug)
        if ctx.is_windows:
            streamer.toggle_ethernet_priority(demote=True)

        streamer.query_loop()

    except KeyboardInterrupt:
        print("Interrupted by user", flush=True)

    except Exception:
        logger.exception("Caught Exception")
        raise

    finally:
        try:
            if streamer and ctx.is_windows:
                streamer.toggle_ethernet_priority(demote=False)
        except Exception:
            pass

        try:
            if streamer:
                streamer.cleanup()
        except Exception:
            logger.exception("Caught Exception")

if __name__ == "__main__":
    main()
