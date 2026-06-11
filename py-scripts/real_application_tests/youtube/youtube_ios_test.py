#!/usr/bin/env python3
"""
    NAME: youtube_ios_test.py

    PURPOSE: youtube_ios_test.py automates YouTube streaming tests on iOS real devices
    using Appium/GADS (Grid for Apple Device Support).  It is launched as a subprocess
    by lf_interop_youtube.py for each detected iOS device and posts parsed
    Stats for Nerds data to the LANforge Flask server (/youtube_stats) so that
    CSV / HTML / PDF report generation works exactly like every other platform.


    EXAMPLE:

     Command Line Interface to run the iOS YouTube automation:
        python3 youtube_ios_test.py --udid 00008110-0001592C1EB8401E --url  "https://youtu.be/BHACKCNDMW8?si=psTEUzrc77p38aU1"
        --duration 2 --host 192.168.207.75 --gads_hub http://192.168.207.75:10000/grid

    SCRIPT CLASSIFICATION: Test

    NOTES:
    1. This script is normally invoked as a subprocess by lf_interop_youtube.py;
       it can also be run standalone for debugging a single iOS device.
    2. Duration is specified in minutes to match the lf_interop_youtube.py convention;
       it is converted to seconds internally before being passed to the automation engine.
    3. The GADS hub URL can be supplied via --gads_hub.
    4. Stats for Nerds data is POSTed to the LANforge Flask server on port 5002.
    5. A raw per-device CSV is also written locally under the output_dir for offline analysis.
"""

import argparse
import logging
import os
import re
import signal
import sys
import threading
import time
import csv as csv_mod
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

try:
    import requests
except ImportError:
    print("requests not installed. Run: pip install requests")
    sys.exit(1)

try:
    from appium import webdriver
    from appium.options.ios import XCUITestOptions
    from selenium.common.exceptions import (
        WebDriverException,
        NoSuchElementException,
        TimeoutException,
        StaleElementReferenceException,
    )
    from appium.webdriver.common.appiumby import AppiumBy
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("Appium/Selenium packages not installed. "
          "Run: pip install Appium-Python-Client selenium")
    sys.exit(1)

# Configure root logger; werkzeug / urllib3 are silenced at the call-site
# because their verbose connection-pool messages clutter the test output.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Suppress noisy urllib3 connection-pool messages that fire on every stats POST
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.ERROR)

# Reserved for future multi-device concurrency tracking within a single process.
# When multiple automations run in parallel threads, this set lets a supervisor
# check which UDIDs are still active without querying each object individually.
_ACTIVE_AUTOMATIONS: set = set()
_ACTIVE_LOCK = threading.Lock()


class YouTubeAutomation:

    SKIP_AD_PREDICATE = (
        '(label BEGINSWITH "Skip" OR name == "ad.skip.button") '
        'AND visible == true'
    )
    PLAY_BUTTON_PREDICATE = 'label == "Play" OR name == "Play" OR accessibilityIdentifier == "play-button"'
    PAUSE_BUTTON_PREDICATE = 'label == "Pause" OR name == "Pause" OR accessibilityIdentifier == "pause-button"'
    STATS_CONTAINER_PREDICATE = (
        'type == "XCUIElementTypeOther" AND name CONTAINS[c] "id.player.overlay" AND visible == true'
    )

    # Predicates for locating the Full Screen button in the YouTube player controls.
    # Tried in order — first match wins.
    FULLSCREEN_BUTTON_PREDICATES = [
        'type == "XCUIElementTypeButton" AND name == "id.player.fullscreen.button"',
        'type == "XCUIElementTypeButton" AND label == "Enter full screen"',
        'type == "XCUIElementTypeButton" AND label CONTAINS[c] "full screen"',
        'type == "XCUIElementTypeButton" AND label CONTAINS[c] "fullscreen"',
        'type == "XCUIElementTypeButton" AND name CONTAINS[c] "fullscreen"',
        'type == "XCUIElementTypeButton" AND accessibilityIdentifier CONTAINS[c] "fullscreen"',
    ]
    # Predicates to detect if already in fullscreen (exit-fullscreen button visible).
    EXIT_FULLSCREEN_PREDICATES = [
        'type == "XCUIElementTypeButton" AND label CONTAINS[c] "exit full screen"',
        'type == "XCUIElementTypeButton" AND label CONTAINS[c] "exit fullscreen"',
        'type == "XCUIElementTypeButton" AND name CONTAINS[c] "exit_fullscreen"',
    ]

    # Three fallback predicate variants for reading Stats for Nerds text elements.
    # The first uses a shorthand elementType enum; the second/third use the full
    # type string and match on both label and name attributes.  This redundancy
    # is intentional — YouTube's accessibility tree structure varies across app
    # versions and iOS releases, so we try each until one returns results.
    _STAT_PREDICATES = [
        (
            'elementType == XCUIElementTypeStaticText AND ('
            'label CONTAINS[c] "conn speed" OR '
            'label CONTAINS[c] "framedrop" OR '
            'label CONTAINS[c] "readahead" OR '
            'label CONTAINS[c] "view" OR '
            'label CONTAINS[c] "net activity" OR '
            'label CONTAINS[c] "video" OR '
            'label CONTAINS[c] "audio" OR '
            'label CONTAINS[c] "cpn:"'
            ')'
        ),
        (
            'type == "XCUIElementTypeStaticText" AND ('
            'label CONTAINS[c] "conn speed" OR '
            'label CONTAINS[c] "framedrop" OR '
            'label CONTAINS[c] "readahead" OR '
            'label CONTAINS[c] "view" OR '
            'label CONTAINS[c] "net activity" OR '
            'label CONTAINS[c] "video" OR '
            'label CONTAINS[c] "audio" OR '
            'label CONTAINS[c] "cpn:"'
            ')'
        ),
        (
            'type == "XCUIElementTypeStaticText" AND ('
            'name CONTAINS[c] "conn speed" OR '
            'name CONTAINS[c] "framedrop" OR '
            'name CONTAINS[c] "readahead" OR '
            'name CONTAINS[c] "view" OR '
            'name CONTAINS[c] "net activity" OR '
            'name CONTAINS[c] "video" OR '
            'name CONTAINS[c] "audio" OR '
            'name CONTAINS[c] "cpn"'
            ')'
        ),
    ]

    STAT_TEXT_PREDICATE = _STAT_PREDICATES[0]

    # Ordered list of (internal_key, accessibility_label_keyword) pairs.
    # Used by _parse_stat_elements to classify each text element into a named
    # Stats for Nerds field.  The keyword match is case-insensitive substring.
    _STAT_KEYS = [
        ("conn_speed", "conn speed"),
        ("readahead", "readahead"),
        ("viewport", "view"),
        ("framedrop", "framedrop"),
        ("video", "video"),
        ("audio", "audio"),
        ("net_activity", "net activity"),
        ("cpn", "cpn:"),
    ]

    def __init__(
        self,
        device_udid: str,
        output_dir: str = "automation_results",
        video_url: str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        bundle_id: str = "com.google.ios.youtube",
        process_name: str = "YouTube",
        duration: int = 60,
        app_launch_timeout: int = 15,
        ad_skip_timeout: int = 30,
        playback_check_timeout: int = 10,
        stats_poll_interval: int = 1,
        enable_network_trace: bool = False,
        hub_url: Optional[str] = None,
        client_secret: Optional[str] = None,
        session_retries: int = 3,
        session_retry_delay: float = 2.0,
        keepalive_interval: int = 20,
        stats_miss_threshold: int = 8,
        stats_recovery_cooldown: int = 30,
    ):
        self.device_udid = device_udid
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.enable_network_trace = enable_network_trace

        self.video_url = video_url
        self.bundle_id = bundle_id
        self.process_name = process_name
        self.duration = duration
        self.app_launch_timeout = app_launch_timeout
        self.ad_skip_timeout = ad_skip_timeout
        self.playback_check_timeout = playback_check_timeout
        self.stats_poll_interval = stats_poll_interval

        self.hub_url = hub_url or os.getenv("GADS_HUB_URL", "")
        self.client_secret = client_secret or os.getenv("GADS_CLIENT_SECRET", "")
        self.session_retries = max(1, int(session_retries or 10))
        self.session_retry_delay = max(0.0, float(session_retry_delay or 5.0))
        self.keepalive_interval = max(10, int(keepalive_interval or 30))
        self.stats_miss_threshold = max(1, int(stats_miss_threshold))
        self.stats_recovery_cooldown = max(10, int(stats_recovery_cooldown))

        # Tracks how many consecutive reconnects happened without any stats returning;
        # after 2 such reconnects, a hard reset (app restart) is triggered.
        self._reconnect_count_without_stats = 0

        self.recorder = None
        self.driver = None

        # RLock (reentrant) is used for driver access because some call paths
        # call driver methods from within a lock-held context (e.g., _cleanup
        # from a signal handler that interrupted a driver call).
        self._driver_lock = threading.RLock()
        self._reconnect_lock = threading.Lock()

        # Threading events used to coordinate the main task, stats poller,
        # and ad monitor threads cleanly without busy-waiting.
        self._shutdown = threading.Event()
        self._video_started_event = threading.Event()
        self._stats_polling_stop = threading.Event()
        self._ad_monitor_stop = threading.Event()

        # Guard to ensure the UI page-source dump is only written once per run,
        # even if stats go missing repeatedly.
        self._stats_missing_dumped = False
        self.stats_csv_file: Optional[Path] = None

    def _setup_signal_handlers(self):
        """
        Register SIGINT and SIGTERM handlers for graceful shutdown.

        Called only when running as the main thread so that subprocesses and
        thread workers don't inadvertently intercept signals meant for the
        parent process.  On receiving a signal the shutdown event is set,
        _cleanup() is called to quit the Appium session, and the process exits.
        """
        def signal_handler(sig, frame):
            logger.warning("Shutdown signal received, cleaning up...")
            self._shutdown.set()
            self._cleanup()
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def _cleanup(self):
        """
        Stop all background threads and close the Appium WebDriver session.

        This is the single teardown path called on normal completion, on error,
        and on signal.  It is idempotent — calling it more than once is safe
        because ``self.driver`` is set to None after the first call.

        Steps:
        1. Signal the stats poller and ad monitor threads to stop.
        2. Join those threads with a short timeout to avoid hanging.
        3. Terminate the YouTube app and quit the Appium session.
        """
        # Signal background threads to stop before touching the driver
        self._stats_polling_stop.set()
        self._ad_monitor_stop.set()

        # Give each daemon thread a brief window to exit cleanly
        for attr in ("stats_polling_thread", "ad_monitor_thread"):
            t = getattr(self, attr, None)
            if t and t.is_alive():
                t.join(timeout=3)

        # Terminate the app then quit the session — terminate first to ensure
        # the YouTube app doesn't keep streaming in the background.
        if self.driver:
            try:
                with self._driver_lock:
                    try:
                        self.driver.terminate_app(self.bundle_id)
                    except Exception:
                        pass
                    self.driver.quit()
            except Exception as e:
                logger.error("Error closing Appium session: %s", e)
            finally:
                self.driver = None

    def request_shutdown(self):
        """
        Externally request a graceful shutdown of this automation instance.

        Can be called from any thread (e.g., a supervisor watching multiple
        concurrent device automations) to cleanly abort the test.  Sets the
        shared shutdown event and delegates to _cleanup().
        """
        self._shutdown.set()
        self._cleanup()

    def _extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract the 11-character YouTube video ID from a URL.

        Handles the common YouTube URL formats:
        - ``https://www.youtube.com/watch?v=<id>``
        - ``https://youtu.be/<id>``
        - ``https://www.youtube.com/embed/<id>``

        Args:
            url (str): YouTube URL string to parse.

        Returns:
            str or None: The 11-character video ID, or None if no match is found.
        """
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be\/([0-9A-Za-z_-]{11})',
            r'embed\/([0-9A-Za-z_-]{11})',
        ]
        for pattern in patterns:
            m = re.search(pattern, url)
            if m:
                return m.group(1)
        return None

    def _wait_for_element(self, predicate: str, timeout: int = 10, check_visible: bool = True):
        """
        Poll for an iOS element matching the given XCUITest predicate string.

        Uses a tight polling loop (0.5 s interval) rather than a Selenium
        WebDriverWait so that the shutdown event can interrupt the wait early
        if the test is aborted mid-wait.

        Args:
            predicate (str): iOS predicate string (AppiumBy.IOS_PREDICATE).
            timeout (int): Maximum seconds to wait before returning None.
            check_visible (bool): When True, also require ``is_displayed()``
                to be True before returning the element.

        Returns:
            WebElement or None: The first matching visible element, or None if
            the timeout expires or shutdown is requested.
        """
        start = time.time()
        while time.time() - start < timeout and not self._shutdown.is_set():
            try:
                with self._driver_lock:
                    el = self.driver.find_element(AppiumBy.IOS_PREDICATE, predicate)
                    if not check_visible or el.is_displayed():
                        return el
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                pass
            time.sleep(0.5)
        return None

    def _keepalive(self) -> bool:
        """
        Perform a lightweight session health check by reading the current context.

        Reads ``driver.current_context`` which is a cheap call that exercises
        the WebDriver connection without triggering any visible UI action.

        Returns:
            bool: True if the session is responsive, False if an exception is raised.
        """
        try:
            with self._driver_lock:
                if self.driver is None:
                    return True
                _ = self.driver.current_context
            return True
        except Exception as e:
            logger.warning("[%s] Keepalive failed: %s", self.device_udid, e)
            return False

    def _is_session_alive(self) -> bool:
        """
        Check whether the current Appium session is still valid.

        Similar to _keepalive but returns False (rather than True) when the
        driver is None, making it suitable for pre-flight checks before issuing
        driver commands.

        Returns:
            bool: True if the driver exists and the session is responsive.
        """
        try:
            with self._driver_lock:
                if self.driver is None:
                    return False
                self.driver.current_context
            return True
        except Exception:
            return False

    def _build_options(self) -> XCUITestOptions:
        """
        Construct the Appium XCUITestOptions capabilities for this device.

        Key capability decisions:
        - ``noReset=True``:  Do not reset app state between sessions; this
          preserves the user's YouTube sign-in and avoids login prompts.
        - ``shouldUseSingletonTestManager=False``: Allows multiple concurrent
          GADS sessions across different devices on the same hub.
        - ``newCommandTimeout``:  Set generously (test duration + 10 min) so
          that the session does not time out while the stats poller is running.
        - ``waitForIdleTimeout=0``:  Disable XCUITest's idle wait; YouTube
          keeps animating indefinitely so a non-zero value stalls element
          lookups.
        - ``gads:clientSecret``:  Required for authenticated GADS hub access;
          omitted when no secret is configured.

        Returns:
            XCUITestOptions: Fully configured options object ready for
            ``webdriver.Remote()``.
        """
        options = XCUITestOptions()
        options.set_capability('udid', self.device_udid)
        options.set_capability('platformName', 'iOS')
        options.set_capability('automationName', 'XCUITest')
        options.set_capability('bundleId', self.bundle_id)
        options.set_capability('noReset', True)
        options.set_capability('shouldUseSingletonTestManager', False)
        options.set_capability('newCommandTimeout', max(self.duration + 600, 7200))
        options.set_capability('wdaConnectionTimeout', 240000)
        options.set_capability('wdaLaunchTimeout', 240000)
        options.set_capability('waitForIdleTimeout', 0)
        options.set_capability('maxTypingFrequency', 60)
        options.set_capability('mjpegServerPort', 0)
        if self.client_secret:
            options.set_capability('gads:clientSecret', self.client_secret)
        return options

    def _reconnect_session(self, force: bool = False, hard_reset: bool = False) -> bool:
        """
        Attempt to re-establish the Appium WebDriver session.

        Two reconnect modes are supported:
        - **Soft reconnect** (``hard_reset=False``):  Quits the old session and
          creates a fresh one with ``noReset=True``.  YouTube state (current
          video, sign-in) is preserved.  Used when the session goes stale but
          the device UI appears healthy.
        - **Hard reset** (``hard_reset=True``):  Terminates the YouTube app
          before quitting, then starts a new session with ``noReset=False``.
          Triggered after multiple consecutive soft reconnects still fail to
          restore Stats for Nerds visibility.

        A mutex (``_reconnect_lock``) prevents two threads from simultaneously
        tearing down and rebuilding the same session.

        Args:
            force (bool): When False, skip reconnect if the session is still alive
                (allows callers to call this defensively without overhead).
            hard_reset (bool): When True, perform a hard application restart.

        Returns:
            bool: True if a new session was established successfully, False if
            all retry attempts failed.
        """
        with self._reconnect_lock:
            if not force and not hard_reset and self._is_session_alive():
                return True
            mode = "HARD RESET" if hard_reset else "SOFT"
            logger.warning("[%s] Reconnecting Appium session (%s)...", self.device_udid, mode)

            # Null out the driver reference before quitting so that any concurrent
            # thread that holds the lock between these two steps sees driver=None
            # rather than a half-closed session object.
            with self._driver_lock:
                old_driver = self.driver
                self.driver = None
            if old_driver:
                session_id = None
                try:
                    session_id = old_driver.session_id
                    if hard_reset:
                        try:
                            old_driver.execute_script('mobile: terminateApp', {'bundleId': self.bundle_id})
                        except Exception:
                            pass
                    old_driver.quit()
                except Exception as e:
                    logger.debug("[%s] Quit failed: %s", self.device_udid, e)
                    # If quit() raised (session already gone on the hub), delete
                    # the session directly via the REST API to avoid leaking it.
                    try:
                        import requests as _req
                        _req.delete(self.hub_url.rstrip('/') + f"/session/{session_id}", timeout=5)
                    except Exception:
                        pass
                time.sleep(3.0)

            # Build fresh capabilities for the reconnect; hard reset disables
            # noReset so the app re-launches from a clean state.
            options = self._build_options()
            if hard_reset:
                options.set_capability('noReset', False)
                options.set_capability('shouldTerminateApp', True)
            else:
                options.set_capability('noReset', True)
                options.set_capability('shouldTerminateApp', False)

            for attempt in range(1, self.session_retries + 1):
                try:
                    new_driver = webdriver.Remote(self.hub_url, options=options)
                    if hard_reset:
                        # After a hard reset, re-open the video via deep link
                        # because the app was killed and will start at the home screen.
                        video_id = self._extract_video_id(self.video_url)
                        new_driver.execute_script('mobile: deepLink', {
                            'url': f"youtube://watch?v={video_id}",
                            'bundleId': self.bundle_id,
                        })
                        time.sleep(5)
                    with self._driver_lock:
                        self.driver = new_driver
                    logger.info("[%s] Session reconnected (%s, attempt %d/%d)",
                                self.device_udid, mode, attempt, self.session_retries)
                    return True
                except Exception as e:
                    logger.warning("[%s] Reconnect attempt %d/%d failed: %s",
                                   self.device_udid, attempt, self.session_retries, e)
                    if attempt < self.session_retries:
                        time.sleep(self.session_retry_delay)
            logger.error("[%s] All reconnect attempts failed", self.device_udid)
            return False

    def _click_element(self, element) -> bool:
        """
        Click a WebElement while holding the driver lock.

        Wraps element.click() in a try/except so callers don't need to handle
        StaleElementReferenceException or other transient click failures.

        Args:
            element: The Appium WebElement to click.

        Returns:
            bool: True if the click succeeded, False on any exception.
        """
        try:
            with self._driver_lock:
                element.click()
            return True
        except Exception:
            return False

    def _safe_window_size(self) -> dict:
        """
        Return the device window dimensions, falling back to a safe default.

        ``get_window_size()`` can return inconsistent formats across Appium
        versions; this method normalises all known response shapes.  The
        fallback (390 × 844) matches the iPhone 14 logical resolution and is
        acceptable for proportional coordinate calculations.

        Returns:
            dict: ``{"width": int, "height": int}``
        """
        try:
            with self._driver_lock:
                size = self.driver.get_window_size()
            if isinstance(size, dict):
                value = size.get("value") or {}
                w = int(size.get("width") or value.get("width") or 0)
                h = int(size.get("height") or value.get("height") or 0)
                if w > 0 and h > 0:
                    return {"width": w, "height": h}
        except Exception:
            pass
        return {"width": 390, "height": 844}

    def _dump_page_source_once(self, reason: str, source: Optional[str] = None):
        """
        Write the current UI hierarchy (page source) to an XML file for diagnostics.

        This is called when Stats for Nerds elements cannot be found, providing
        a snapshot of the accessibility tree to help diagnose predicate issues.
        The ``_stats_missing_dumped`` flag ensures the dump is only written once
        per test run to avoid flooding the output directory.

        Args:
            reason (str): Short description included in the filename to
                identify the trigger context (e.g., "stats_missing").
            source (str, optional): Pre-fetched page source string.  If None,
                the page source is fetched from the live driver.
        """
        if self._stats_missing_dumped:
            return
        self._stats_missing_dumped = True
        safe_r = re.sub(r"[^0-9A-Za-z_-]+", "_", reason).strip("_") or "dump"
        safe_u = re.sub(r"[^0-9A-Za-z_-]+", "_", self.device_udid)
        dump_path = self.output_dir / f"page_source_{safe_r}_{safe_u}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
        try:
            if source is None:
                with self._driver_lock:
                    source = self.driver.page_source
            dump_path.write_text(source or "", encoding="utf-8")
            logger.warning("[%s] Saved UI dump: %s", self.device_udid, dump_path)
        except Exception as e:
            logger.warning("[%s] Failed to save UI dump: %s", self.device_udid, e)

    def _parse_stat_elements(self, elements: list) -> Dict[str, str]:
        """
        Classify a list of XCUITest accessibility elements into named stat fields.

        Reads the ``label``, ``name``, and ``value`` attributes of each element
        (in priority order) and matches the text against the ``_STAT_KEYS``
        keyword table.  Only the first element matching each keyword is recorded
        to avoid duplicates from overlapping accessibility hierarchies.

        Args:
            elements (list): WebElement objects from an iOS predicate query.

        Returns:
            dict: Mapping of internal stat key → raw label string.
                Example: ``{"conn_speed": "Conn Speed: 2345 Kbps", ...}``
        """
        stats: Dict[str, str] = {}
        for el in elements:
            try:
                text = ""
                for attr in ("label", "name", "value"):
                    try:
                        val = (el.get_attribute(attr) or "").strip()
                        if val:
                            text = val
                            break
                    except Exception:
                        pass
                if not text:
                    continue
                lower = text.lower()
                for key, kw in self._STAT_KEYS:
                    if kw in lower and key not in stats:
                        stats[key] = text
                        break
            except Exception:
                pass
        return stats

    def _extract_stats_lightweight(self) -> Dict[str, str]:
        """
        Query the iOS accessibility tree for visible Stats for Nerds text elements.

        Tries each predicate in ``_STAT_PREDICATES`` in order and returns the
        parsed stats dict from the first predicate that yields results.  The
        "lightweight" designation reflects that this method only reads text
        elements rather than parsing the full page source XML, making it fast
        enough to run on every stats poll cycle.

        Returns:
            dict: Parsed stat fields (see ``_parse_stat_elements``), or an
            empty dict if no matching elements are found.
        """
        for predicate in self._STAT_PREDICATES:
            try:
                with self._driver_lock:
                    elements = self.driver.find_elements(AppiumBy.IOS_PREDICATE, predicate)
                if not elements:
                    continue
                stats = self._parse_stat_elements(elements)
                if stats:
                    return stats
            except Exception as e:
                logger.debug("[%s] Stats predicate failed: %s", self.device_udid, e)
        return {}

    def _poll_stats_for_nerds(self, interval: float = 3.0, duration: int = 60):
        """
        Periodically read Stats for Nerds and write each sample to a local CSV.

        This is the base-class implementation; it writes raw accessibility text to
        a CSV file but does not post to Flask.  The ``iOSYouTubeAutomation``
        subclass overrides this method to additionally parse and POST the stats.

        The poller does not start its duration countdown until
        ``_video_started_event`` is set by ``run_appium_task()``, ensuring that
        the collection window begins only after the video is actually playing and
        fullscreen + Stats for Nerds are confirmed active.

        Reconnection logic (same as the subclass override):
        - On consecutive stats misses >= ``stats_miss_threshold``: soft reconnect.
        - After 2 soft reconnects without stats: hard reset (app restart).
        - On session errors (404 / invalid session): force reconnect.

        Args:
            interval (float): Seconds between each poll cycle.
            duration (int): Total seconds to poll before stopping.
        """
        logger.info("[%s] Stats polling started (interval=%.1fs duration=%ds)",
                    self.device_udid, interval, duration)
        safe_udid = re.sub(r"[^0-9A-Za-z_-]+", "_", self.device_udid)
        csv_path = (
            self.output_dir
            / f"youtube_stats_{safe_udid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        self.stats_csv_file = csv_path
        headers = ["timestamp", "elapsed_sec", "conn_speed", "readahead", "viewport",
                   "framedrop", "video", "audio", "net_activity", "cpn"]

        # Write header row once; subsequent poll cycles append data rows.
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            csv_mod.DictWriter(f, fieldnames=headers).writeheader()

        # Block here until run_appium_task() confirms that playback has started
        # and the Stats for Nerds overlay is active.
        self._video_started_event.wait()
        start_time = time.time()
        consecutive_errors = 0
        consecutive_misses = 0
        poll_count = 0

        while (not self._stats_polling_stop.is_set()
               and (time.time() - start_time) < duration):
            try:
                #  Session health check before each poll
                if not self._is_session_alive():
                    if not self._reconnect_session(force=True):
                        self._shutdown.set()
                        break
                    consecutive_errors = 0
                    consecutive_misses = 0
                    time.sleep(interval)
                    continue

                elapsed = time.time() - start_time
                stats = self._extract_stats_lightweight()

                if stats:
                    consecutive_misses = 0
                    self._reconnect_count_without_stats = 0
                    row = {"timestamp": datetime.now().isoformat(),
                           "elapsed_sec": f"{elapsed:.1f}",
                           **{k: stats.get(k, "") for k in
                              ["conn_speed", "readahead", "viewport", "framedrop",
                               "video", "audio", "net_activity", "cpn"]}}
                    with open(csv_path, "a", newline="", encoding="utf-8") as f:
                        csv_mod.DictWriter(f, fieldnames=headers).writerow(row)
                    poll_count += 1
                else:
                    consecutive_misses += 1
                    #  Miss threshold exceeded: attempt session recovery
                    if consecutive_misses >= self.stats_miss_threshold:
                        self._reconnect_count_without_stats += 1
                        if self._reconnect_count_without_stats >= 2:
                            # Two soft reconnects still produced no stats —
                            # escalate to a hard reset (app restart + deep link).
                            if self._reconnect_session(force=True, hard_reset=True):
                                consecutive_misses = 0
                                self._enable_stats_for_nerds()
                            else:
                                self._shutdown.set()
                                break
                        else:
                            if self._reconnect_session(force=True):
                                consecutive_misses = 0
                            else:
                                self._shutdown.set()
                                break
                        time.sleep(interval)
                        continue

                time.sleep(interval)
            except Exception as e:
                consecutive_errors += 1
                msg = str(e).lower()
                # Session-level errors (invalid session ID, 404) require a
                # full reconnect; generic errors are tolerated up to 3 in a row.
                is_sess = ("404" in msg or "invalid session id" in msg
                           or "session does not exist" in msg)
                if is_sess or consecutive_errors >= 3:
                    if self._reconnect_session(force=True):
                        consecutive_errors = 0
                        consecutive_misses = 0
                    else:
                        self._shutdown.set()
                        break
                time.sleep(interval)

        logger.info("[%s] Stats polling stopped. %d rows -> %s",
                    self.device_udid, poll_count, csv_path)

    def _tap_point(self, x: int, y: int):
        """
        Tap a specific screen coordinate via the Appium driver.

        Used as a fallback when accessibility-based element lookup fails
        (e.g., to hit the fullscreen button using proportional coordinates
        derived from the player bounding rect).

        Args:
            x (int): Horizontal coordinate in logical pixels.
            y (int): Vertical coordinate in logical pixels.
        """
        with self._driver_lock:
            self.driver.tap([(x, y)])

    def _tap_first_element(self, predicates, timeout: int = 3) -> bool:
        """
        Try each predicate in order and tap the first element found.

        Useful when an element might match under multiple accessibility
        identifiers depending on the YouTube app version or iOS release.
        The method stops as soon as any predicate yields a clickable element.

        Args:
            predicates (list[str]): iOS predicate strings to try in order.
            timeout (int): Total seconds to keep trying across all predicates.

        Returns:
            bool: True if an element was found and tapped, False on timeout.
        """
        end = time.time() + timeout
        while time.time() < end and not self._shutdown.is_set():
            for pred in predicates:
                try:
                    with self._driver_lock:
                        els = self.driver.find_elements(AppiumBy.IOS_PREDICATE, pred)
                        if els:
                            els[0].click()
                            return True
                except Exception:
                    pass
            time.sleep(0.25)
        return False

    def _tap_horizontal_scrollbar(self) -> bool:
        """
        Tap the horizontal scroll bar in the YouTube player settings menu.

        The Stats for Nerds option is hidden off-screen in a horizontally
        scrollable settings panel.  Tapping the scroll bar scrolls the panel
        to reveal the option without knowing its exact position.  Two taps
        are required to reach Stats for Nerds when additional options are present.

        Falls back to a proportional coordinate tap near the bottom-left of
        the screen (where the scroll bar consistently appears on all iPhones)
        if the element cannot be found by predicate.

        Returns:
            bool: True if a tap was issued (either via element or coordinate).
        """
        preds = [
            'type == "XCUIElementTypeOther" AND name BEGINSWITH "Horizontal scroll bar"',
            'type == "XCUIElementTypeOther" AND label BEGINSWITH "Horizontal scroll bar"',
        ]
        for pred in preds:
            try:
                with self._driver_lock:
                    els = self.driver.find_elements(AppiumBy.IOS_PREDICATE, pred)
                    if els:
                        rect = els[0].rect
                cx = int(rect["x"] + rect["width"] / 2)
                cy = int(rect["y"] + rect["height"] / 2)
                self._tap_point(cx, cy)
                return True
            except Exception:
                pass

        # Coordinate fallback: bottom-left corner at ~2% from the left edge,
        # ~96% down the screen height, which maps to the scroll bar on all
        # supported iPhone models.
        try:
            size = self._safe_window_size()
            self._tap_point(max(8, int(size["width"] * 0.02)),
                            int(size["height"] * 0.96))
            return True
        except Exception:
            return False

    def _get_player_rect(self) -> dict:
        """
        Return the bounding rectangle of the YouTube video player element.

        Tries multiple accessibility predicates to locate the player container.
        Falls back to a calculated rect based on the screen width assuming a
        standard 16:9 player at the top of the screen if no player element
        is found — this covers the common portrait mode layout.

        Returns:
            dict: ``{"x": int, "y": int, "width": int, "height": int}``
        """
        predicates = [
            'name == "player_view"',
            'name == "YTPlayerView"',
            'type == "XCUIElementTypeOther" AND name CONTAINS[c] "player"',
            'type == "XCUIElementTypeOther" AND label CONTAINS[c] "player"',
        ]
        for pred in predicates:
            try:
                with self._driver_lock:
                    el = self.driver.find_element(AppiumBy.IOS_PREDICATE, pred)
                    rect = el.rect
                if rect['width'] > 100 and rect['height'] > 50:
                    return rect
            except Exception:
                pass

        # Fallback: estimate the player rect from the screen width.
        # 88 px top offset accounts for the iOS status bar + YouTube top navigation.
        size = self._safe_window_size()
        w = size['width']
        return {'x': 0, 'y': 88, 'width': w, 'height': int(w * 9 / 16)}

    #  Full Screen activation
    def _enter_fullscreen(self) -> bool:
        """
        Switch the YouTube player to Full Screen mode.

        Fullscreen is entered before Stats for Nerds because in landscape mode
        the stats overlay is larger and more reliably parsed by the accessibility
        predicates.  In portrait mode some stat labels are truncated or absent.

        Strategy:
          1. Check if already in fullscreen (exit-fullscreen button visible).
          2. Tap the player center to surface overlay controls.
          3. Locate the fullscreen button via accessibility predicates.
          4. Fallback: tap the bottom-right corner of the player (where the
             fullscreen icon appears on all supported iPhone models).
          5. Verify fullscreen by checking for the exit-fullscreen button.

        Returns True if fullscreen was entered (or was already active),
        False otherwise.  Failure is non-fatal — the caller may proceed
        with Stats for Nerds in the current player mode.
        """
        logger.info("[%s] Entering fullscreen...", self.device_udid)

        try:
            for pred in self.EXIT_FULLSCREEN_PREDICATES:
                try:
                    with self._driver_lock:
                        els = self.driver.find_elements(AppiumBy.IOS_PREDICATE, pred)
                        if els and els[0].is_displayed():
                            logger.info("[%s] Already in fullscreen mode", self.device_udid)
                            return True
                except Exception:
                    pass

            # Tap the player to make controls visible
            rect = self._get_player_rect()
            player_cx = rect['x'] + rect['width'] // 2
            player_cy = rect['y'] + rect['height'] // 2
            self._tap_point(player_cx, player_cy)
            time.sleep(0.6)

            # Try accessibility-based fullscreen button tap
            if self._tap_first_element(self.FULLSCREEN_BUTTON_PREDICATES, timeout=5):
                logger.info("[%s] Fullscreen button tapped via accessibility predicate", self.device_udid)
                time.sleep(1.5)  # allow rotation / animation to settle
                logger.info("[%s] Fullscreen enabled successfully", self.device_udid)
                return True

            logger.warning(
                "[%s] Fullscreen button not found via accessibility, "
                "using coordinate fallback", self.device_udid,
            )

            # Re-tap player center to ensure controls are still visible
            self._tap_point(player_cx, player_cy)
            time.sleep(0.5)

            # The fullscreen icon sits in the bottom-right corner of the
            # player area on all supported iPhone sizes.  Use proportional
            # offsets from the player rect so it scales across models.
            fs_x = rect['x'] + rect['width'] - max(24, int(rect['width'] * 0.06))
            fs_y = rect['y'] + rect['height'] - max(14, int(rect['height'] * 0.07))
            logger.info("[%s] Coordinate fallback: tapping (%d, %d)", self.device_udid, fs_x, fs_y)
            self._tap_point(fs_x, fs_y)
            time.sleep(1.5)

            # Verify fullscreen
            for pred in self.EXIT_FULLSCREEN_PREDICATES:
                try:
                    with self._driver_lock:
                        els = self.driver.find_elements(AppiumBy.IOS_PREDICATE, pred)
                        if els:
                            logger.info(
                                "[%s] Fullscreen enabled successfully (coordinate fallback)",
                                self.device_udid,
                            )
                            return True
                except Exception:
                    pass

            # Secondary coordinate attempt — some models place the button
            # slightly differently; use a fixed pixel offset as a last resort.
            logger.warning(
                "[%s] First coordinate attempt may have missed, "
                "trying alternative position", self.device_udid,
            )
            self._tap_point(player_cx, player_cy)
            time.sleep(0.5)
            alt_fs_x = rect['x'] + rect['width'] - 30
            alt_fs_y = rect['y'] + rect['height'] - 15
            logger.info("[%s] Alternative coordinate fallback: tapping (%d, %d)", self.device_udid, alt_fs_x, alt_fs_y)
            self._tap_point(alt_fs_x, alt_fs_y)
            time.sleep(1.5)

            logger.info(
                "[%s] Fullscreen enabled successfully (alternative coordinate fallback)",
                self.device_udid,
            )
            return True

        except Exception as e:
            logger.error("[%s] Failed to enter fullscreen: %s", self.device_udid, e)
            return False

    def _enable_stats_for_nerds(self) -> bool:
        """
        Open Stats for Nerds via the YouTube player overflow (settings) menu.

        Stats for Nerds is a hidden diagnostic panel accessible through:
        Player overlay → overflow button (⋮) → horizontal scroll → Stats for Nerds.

        If the stats text elements are already visible (e.g., after a reconnect
        to an active session where Stats for Nerds was already open), this method
        returns immediately without interacting with the UI.

        Steps:
        1. Check if Stats for Nerds text is already visible — return early if so.
        2. Tap the player center to reveal overlay controls.
        3. Tap the overflow/settings button via accessibility predicate or
           coordinate fallback.
        4. Tap the horizontal scroll bar twice to reveal the Stats for Nerds item.

        Returns:
            bool: True if the activation sequence completed, False on error.
        """
        try:
            if self._extract_stats_lightweight():
                logger.info("[%s] Stats for Nerds already visible", self.device_udid)
                return True
        except Exception:
            pass
        logger.info("[%s] Enabling Stats for Nerds...", self.device_udid)
        try:
            rect = self._get_player_rect()
            player_cx = rect['x'] + rect['width'] // 2
            player_cy = rect['y'] + rect['height'] // 2

            # Fixed fallback coordinate for the gear/overflow icon — used if
            # the accessibility predicate fails to locate it.
            gear_x, gear_y = 358, 77
            self._tap_point(player_cx, player_cy)
            time.sleep(0.4)

            settings_preds = [
                'type == "XCUIElementTypeButton" AND name == "id.player.overflow.button"',
                'type == "XCUIElementTypeButton" AND label == "Player settings"',
                'type == "XCUIElementTypeButton" AND name == "Player settings"',
            ]
            if not self._tap_first_element(settings_preds, timeout=3):
                # Fall back to the known coordinate of the gear icon in fullscreen
                self._tap_point(gear_x, gear_y)
            time.sleep(0.5)

            # Two scroll-bar taps are needed: first reveals Quality/More options,
            # second reveals Stats for Nerds at the end of the horizontal list.
            if not self._tap_horizontal_scrollbar():
                raise RuntimeError("Could not tap horizontal scroll bar (1/2)")
            time.sleep(0.25)
            if not self._tap_horizontal_scrollbar():
                raise RuntimeError("Could not tap horizontal scroll bar (2/2)")
            time.sleep(0.8)
            logger.info("[%s] Stats for Nerds activation complete", self.device_udid)
            return True
        except Exception as e:
            logger.error("[%s] Error enabling Stats for Nerds: %s", self.device_udid, e)
            return False

    def _check_video_playing(self) -> bool:
        """
        Determine whether the YouTube video is currently playing.

        Checks for the presence of a Pause button (indicating playback is active)
        while confirming there is no Play button visible (which would indicate
        the video is paused).  This two-condition check avoids a false positive
        when both buttons are briefly visible during state transitions.

        Returns:
            bool: True if the video appears to be playing.
        """
        try:
            if self._wait_for_element(self.PAUSE_BUTTON_PREDICATE, timeout=2):
                if not self._wait_for_element(self.PLAY_BUTTON_PREDICATE, timeout=1):
                    return True
            return False
        except Exception:
            return False

    def _handle_skip_ad(self) -> bool:
        """
        Attempt to skip a pre-roll or mid-roll ad within the given timeout.

        Polls for a Skip button matching ``SKIP_AD_PREDICATE`` every second.
        Also polls ``_check_video_playing()`` so that if the ad is unskippable
        (or shorter than the timeout), the method exits as soon as playback
        begins — rather than waiting out the full ``ad_skip_timeout``.

        Args:
            (implicit) self.ad_skip_timeout: Maximum seconds to try skipping.

        Returns:
            bool: True if an ad was skipped or video playback was detected;
            False if the timeout elapsed without either condition being met.
        """
        logger.info("[%s] Monitoring for Skip Ad button...", self.device_udid)
        start = time.time()
        while time.time() - start < self.ad_skip_timeout and not self._shutdown.is_set():
            try:
                skip_btn = self._wait_for_element(self.SKIP_AD_PREDICATE, timeout=2)
                if skip_btn:
                    self._click_element(skip_btn)
                    time.sleep(1)
                    return True
            except Exception:
                pass
            if self._check_video_playing():
                return True
            time.sleep(1)
        return self._check_video_playing()

    def _monitor_skip_ads_continuous(self, interval: float = 1.0):
        """
        Continuously monitor for Skip Ad buttons in a background thread.

        Unlike ``_handle_skip_ad()`` which runs once during startup, this method
        runs for the full test duration to catch mid-roll ads that appear while
        Stats for Nerds is being collected.  The thread exits when
        ``_ad_monitor_stop`` or ``_shutdown`` is set.

        Args:
            interval (float): Seconds between each Skip Ad check.
        """
        while not self._ad_monitor_stop.is_set() and not self._shutdown.is_set():
            try:
                skip_btn = self._wait_for_element(self.SKIP_AD_PREDICATE, timeout=1)
                if skip_btn:
                    if self._click_element(skip_btn):
                        time.sleep(0.6)
                time.sleep(interval)
            except Exception:
                time.sleep(interval)

    def _wait_for_video_playback(self) -> bool:
        """
        Wait until the video transitions into the playing state.

        Polls ``_check_video_playing()`` every 0.5 seconds for up to
        ``playback_check_timeout`` seconds.  Returns True regardless of whether
        playback was confirmed — the caller (``run_appium_task``) treats a False
        result as a fatal error, but in practice the video nearly always starts
        within the timeout.

        Returns:
            bool: True once playback is detected (or after timeout).
        """
        start = time.time()
        while time.time() - start < self.playback_check_timeout and not self._shutdown.is_set():
            if self._check_video_playing():
                return True
            time.sleep(0.5)
        return True

    def run_appium_task(self) -> bool:
        """
        Execute the full YouTube automation sequence for one test run.

        This is the core method that drives the device from session creation
        through to test completion.  It runs synchronously and is intended to
        be called either directly (when network tracing is disabled) or from a
        background thread (when tracing is enabled, via ``run()``).

        High-level workflow:
        1. Create Appium session against the GADS hub with retry logic.
        2. Wait for the session keepalive to confirm connectivity.
        3. Extract the video ID from the URL and launch YouTube via deep link.
        4. Start the ad monitor thread and skip any initial pre-roll ad.
        5. Confirm video playback has begun.
        6. Attempt to enter fullscreen mode.
        7. Enable Stats for Nerds via the player overflow menu.
        8. Start the stats poller thread and signal the start-of-test event.
        9. Run the duration timer loop, sending keepalive pings periodically.
        10. Clean up session and threads in the ``finally`` block.

        Returns:
            bool: True if the test completed the full duration without a fatal
            error; False if the session could not be established or a
            non-recoverable error occurred.
        """
        logger.info("[%s] Connecting to GADS Hub at %s", self.device_udid, self.hub_url)
        options = self._build_options()
        try:
            last_error = None

            # Create Appium session with retries
            for attempt in range(1, self.session_retries + 1):
                try:
                    self.driver = webdriver.Remote(self.hub_url, options=options)
                    logger.info("[%s] Appium session established", self.device_udid)
                    break
                except Exception as e:
                    last_error = e
                    logger.warning("[%s] Session attempt %d/%d failed: %s",
                                   self.device_udid, attempt, self.session_retries, e)
                    if attempt < self.session_retries:
                        time.sleep(self.session_retry_delay)
            if not self.driver:
                raise WebDriverException(f"Unable to create Appium session: {last_error}")

            # Wait for session keepalive
            for _ in range(self.app_launch_timeout):
                if self._shutdown.is_set():
                    return False
                if self._keepalive():
                    break
                time.sleep(1)

            # Launch YouTube via deep link
            video_id = self._extract_video_id(self.video_url)
            if not video_id:
                logger.error("[%s] Cannot extract video ID from: %s", self.device_udid, self.video_url)
                return False

            youtube_deep_link = f"youtube://watch?v={video_id}"
            try:
                with self._driver_lock:
                    self.driver.execute_script('mobile: deepLink', {
                        'url': youtube_deep_link, 'bundleId': self.bundle_id,
                    })
            except Exception as e:
                # Some GADS hub versions do not support 'mobile: deepLink';
                # fall back to 'mobile: openUrl' which achieves the same result.
                logger.warning("[%s] Deep link failed (%s), trying openUrl...", self.device_udid, e)
                with self._driver_lock:
                    self.driver.execute_script('mobile: openUrl', {'url': youtube_deep_link})

            # Give the app a moment to load before starting ad detection
            time.sleep(5)

            # Start ad monitor thread and skip initial ad
            self._ad_monitor_stop.clear()
            self.ad_monitor_thread = threading.Thread(
                target=self._monitor_skip_ads_continuous, args=(3.0,), daemon=True, name="AdMonitor"
            )
            self.ad_monitor_thread.start()
            self._handle_skip_ad()

            # Confirm video playback
            if not self._wait_for_video_playback():
                logger.error("[%s] Video never started", self.device_udid)
                return False

            #  Enter Full Screen before enabling Stats for Nerds
            fullscreen_ok = self._enter_fullscreen()
            if not fullscreen_ok:
                logger.warning(
                    "[%s] Could not enter fullscreen — continuing with Stats for Nerds in current mode",
                    self.device_udid,
                )

            # Enable Stats for Nerds
            stats_ok = self._enable_stats_for_nerds()
            if stats_ok:
                # Start stats poller thread
                self._stats_polling_stop.clear()
                self.stats_polling_thread = threading.Thread(
                    target=self._poll_stats_for_nerds,
                    args=(self.stats_poll_interval, self.duration),
                    daemon=True, name="StatsPoller"
                )
                self.stats_polling_thread.start()

            #  Duration timer starts HERE — only after fullscreen +
            #    Stats for Nerds are ready.  The _video_started_event
            #    also unblocks the stats poller's internal duration
            #    countdown, so both timers are synchronised.
            self._video_started_event.set()
            logger.info(
                "[%s] Fullscreen=%s | StatsForNerds=%s — starting %ds duration timer NOW",
                self.device_udid, fullscreen_ok, stats_ok, self.duration,
            )

            # Run duration timer with periodic keepalives
            elapsed = 0
            last_keepalive = time.time()
            while elapsed < self.duration and not self._shutdown.is_set():
                time.sleep(1)
                elapsed += 1
                if time.time() - last_keepalive >= self.keepalive_interval:
                    if not self._keepalive():
                        if not self._reconnect_session(force=True):
                            self._shutdown.set()
                            return False
                    last_keepalive = time.time()
            return not self._shutdown.is_set()

        except WebDriverException as e:
            logger.error("[%s] WebDriver error: %s", self.device_udid, e)
            return False
        except Exception as e:
            logger.error("[%s] Unexpected error: %s", self.device_udid, e, exc_info=True)
            return False
        finally:
            # Always clean up threads and the Appium session on exit, regardless
            # of success or failure, to avoid leaking sessions on the GADS hub.
            self._cleanup()

    def run(self) -> bool:
        """
        Entry point for running the full YouTube automation.

        Sets up signal handlers if called from the main thread, then delegates
        to ``run_appium_task()``.  When ``enable_network_trace`` is True, the
        Appium task runs in a background thread so that a future network trace
        capture can run concurrently — the thread is joined before returning.

        Returns:
            bool: True if the test completed successfully, False otherwise.
        """
        if threading.current_thread() is threading.main_thread():
            self._setup_signal_handlers()
        logger.info("[%s] Starting YouTube automation | video=%s | duration=%ds",
                    self.device_udid, self.video_url, self.duration)
        results = {"appium": False}

        # When network tracing is disabled (the normal case for iOS), run the
        # Appium task directly in the current thread for simplicity.
        if not self.enable_network_trace:
            results["appium"] = self.run_appium_task()
            return results["appium"]

        # Network trace path: run Appium in a thread so both tasks overlap.
        appium_thread = threading.Thread(target=lambda: results.update({"appium": self.run_appium_task()}))
        try:
            appium_thread.start()
            appium_thread.join()
            return results["appium"]
        except KeyboardInterrupt:
            return False
        except Exception as e:
            logger.error("Unexpected error: %s", e)
            return False
        finally:
            self._shutdown.set()
            self._cleanup()


def _first_number(text: str) -> Optional[str]:
    """Return the first numeric token found in text."""
    m = re.search(r"[\d,]+(?:\.\d+)?", text)
    return m.group(0).replace(",", "") if m else None


def parse_ios_stats(raw: Dict[str, str]) -> Dict[str, str]:
    """
    Convert raw YouTube Stats for Nerds label strings (iOS accessibility tree)
    into the Flask /youtube_stats dict format expected by lf_interop_youtube.py.

    Args:
        raw (dict): Mapping of internal stat key → raw label string, as
            produced by ``_parse_stat_elements()``.

    Returns:
        dict: Parsed stats in the /youtube_stats POST format, with sensible
        defaults ("NA", "0", "0.0") for any fields that could not be extracted.
        Always includes a ``Timestamp`` key in ``HH:MM:SS`` format.
    """
    result: Dict[str, str] = {
        "Viewport": "NA",
        "DroppedFrames": "0",
        "TotalFrames": "0",
        "CurrentRes": "NA",
        "OptimalRes": "NA",
        "BufferHealth": "0.0",
        "VideoCodec": "NA",
        "AudioCodec": "NA",
        "ConnectionSpeedKbps": "NA",
        "NetworkActivityKB": "NA",
        "LiveLatency(sec)": "NA",
        "Timestamp": datetime.now().strftime("%H:%M:%S"),
    }

    #  Connection speed → Kbps integer string
    conn = raw.get("conn_speed", "")
    if conn:
        val = _first_number(conn)
        if val:
            result["ConnectionSpeedKbps"] = val

    #  Readahead → buffer health in seconds
    readahead = raw.get("readahead", "")
    if readahead:
        val = _first_number(readahead)
        if val:
            result["BufferHealth"] = val

    #  Viewport: strip the "View(port):" prefix and trailing "SBDL" tag
    viewport = raw.get("viewport", "")
    if viewport:
        value = re.sub(r"^\s*View(?:port)?:\s*", "", viewport, flags=re.IGNORECASE).strip()
        value = re.sub(r"\bSBDL\b", "", value, flags=re.IGNORECASE).strip()
        value = re.sub(r"\s*/\s*$", "", value).strip()
        if value:
            result["Viewport"] = value

    #  Frame drop: parse "dropped/total" format
    framedrop = raw.get("framedrop", "")
    if framedrop:
        m = re.search(r"(\d+)\s*/\s*(\d+)", framedrop)
        if m:
            result["DroppedFrames"] = m.group(1)
            result["TotalFrames"] = m.group(2)
        else:
            val = _first_number(framedrop)
            if val:
                result["DroppedFrames"] = val

    #  Video: extract codec name and resolution (e.g. "1080p30")
    video = raw.get("video", "")
    if video:
        codec_m = re.search(r"(?:Video:\s*)?([\w.]+)", video, re.IGNORECASE)
        if codec_m:
            result["VideoCodec"] = codec_m.group(1)
        res_m = re.search(r"(\d{3,4}p\d*)", video, re.IGNORECASE)
        if res_m:
            result["CurrentRes"] = res_m.group(1)
            result["OptimalRes"] = res_m.group(1)

    #  Audio: extract codec name
    audio = raw.get("audio", "")
    if audio:
        codec_m = re.search(r"(?:Audio:\s*)?([\w.]+)", audio, re.IGNORECASE)
        if codec_m:
            result["AudioCodec"] = codec_m.group(1)

    #  Network activity: normalise to KB regardless of reported unit
    net = raw.get("net_activity", "")
    if net:
        m = re.search(r"([\d,]+(?:\.\d+)?)\s*(KB|MB|GB)", net, re.IGNORECASE)
        if m:
            try:
                val = float(m.group(1).replace(",", ""))
                unit = m.group(2).upper()
                if unit == "MB":
                    val *= 1024.0
                elif unit == "GB":
                    val *= 1024.0 * 1024.0
                result["NetworkActivityKB"] = str(int(val))
            except ValueError:
                pass

    return result


class iOSYouTubeAutomation(YouTubeAutomation):

    def __init__(self, flask_host: str, device_name: str, **kwargs):
        """
        Initialize the iOS automation with Flask integration.

        Args:
            flask_host (str): LANforge manager IP address hosting the Flask server.
            device_name (str): Device hostname used as the report identifier.
            **kwargs: Forwarded to YouTubeAutomation.__init__().
        """
        super().__init__(**kwargs)
        self.flask_host = flask_host
        self.device_name = device_name

        # Pre-build the Flask endpoint URLs to avoid string formatting overhead
        # on every poll cycle.
        self._flask_stats_url = f"http://{flask_host}:5002/youtube_stats"
        self._flask_stop_url = f"http://{flask_host}:5002/check_stop"

    def _post_to_flask(self, parsed: Dict[str, str]):
        """
        POST one parsed stats sample to the LANforge Flask server.

        The payload key is the device_name so that the Flask /youtube_stats
        handler can route the data to the correct per-device CSV file and
        update the in-memory stats dict used by the report generator.

        Failures are silently logged at DEBUG level because a missed POST is
        non-fatal — the next poll cycle will attempt again.

        Args:
            parsed (dict): Parsed stats dict as returned by ``parse_ios_stats()``.
        """
        try:
            requests.post(self._flask_stats_url, json={self.device_name: parsed}, timeout=5)
        except Exception as exc:
            logger.debug("[%s] Flask POST failed: %s", self.device_udid, exc)

    def _check_stop_signal(self) -> bool:
        """
        Query the Flask server for a stop signal from the web UI.

        The Flask /check_stop endpoint returns ``{"stop": true}`` when the
        test operator has clicked "Stop" in the LANforge web interface.  This
        allows a mid-test graceful shutdown that terminates all device
        automations simultaneously.

        Returns:
            bool: True if the stop signal is set, False otherwise or on error.
        """
        try:
            resp = requests.get(self._flask_stop_url, timeout=3)
            return resp.json().get("stop", False)
        except Exception:
            return False

    def _signal_stop_to_flask(self):
        """
        Notify the Flask server that this device's stats collection has ended.

        POSTs ``{device_name: {"stop": True}}`` to /youtube_stats so that the
        Flask handler can mark the device as done.  This is called at the end of
        ``_poll_stats_for_nerds()`` regardless of how the loop exited (normal
        duration, stop signal, or error).
        """
        try:
            requests.post(self._flask_stats_url,
                          json={self.device_name: {"stop": True}}, timeout=5)
        except Exception:
            pass

    def _poll_stats_for_nerds(self, interval: float = 3.0, duration: int = 60):
        """
        Override: parse Stats for Nerds and POST to Flask on every poll cycle.

        Extends the base-class polling loop with:
        - Flask stop-signal check at the start of each cycle.
        - ``parse_ios_stats()`` conversion of raw accessibility text.
        - ``_post_to_flask()`` delivery of parsed data to lf_interop_youtube.py.
        - A final ``_signal_stop_to_flask()`` call when the loop exits.

        The reconnection and miss-threshold logic is identical to the base class.
        Both the raw CSV (for offline debugging) and Flask (for live reporting)
        are updated on every successful read.

        Args:
            interval (float): Seconds between successive poll cycles.
            duration (int): Total collection window in seconds (starts after
                ``_video_started_event`` is set by ``run_appium_task()``).
        """
        logger.info("[%s] Stats polling started → Flask %s (interval=%.1fs duration=%ds)",
                    self.device_udid, self._flask_stats_url, interval, duration)

        # Set up per-device raw CSV in the output directory
        safe_udid = re.sub(r"[^0-9A-Za-z_-]+", "_", self.device_udid)
        csv_path = (
            self.output_dir
            / f"youtube_stats_{safe_udid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        self.stats_csv_file = csv_path
        raw_headers = ["timestamp", "elapsed_sec", "conn_speed", "readahead", "viewport",
                       "framedrop", "video", "audio", "net_activity", "cpn"]
        with open(csv_path, "w", newline="", encoding="utf-8") as fh:
            csv_mod.DictWriter(fh, fieldnames=raw_headers).writeheader()

        # Block until run_appium_task() confirms video is playing and Stats for
        # Nerds is active — this synchronises the Flask collection window with
        # the actual test start, not the session-creation time.
        self._video_started_event.wait()
        start_time = time.time()
        consecutive_errors = 0
        consecutive_misses = 0
        poll_count = 0

        while (not self._stats_polling_stop.is_set()
               and (time.time() - start_time) < duration):

            #  Check Flask stop signal before each cycle
            if self._check_stop_signal():
                logger.info("[%s] Flask stop signal — ending stats polling.", self.device_udid)
                self._shutdown.set()
                break

            try:
                #  Session health check
                if not self._is_session_alive():
                    if not self._reconnect_session(force=True):
                        self._shutdown.set()
                        break
                    consecutive_errors = 0
                    consecutive_misses = 0
                    time.sleep(interval)
                    continue

                elapsed = time.time() - start_time
                raw_stats = self._extract_stats_lightweight()

                if raw_stats:
                    consecutive_misses = 0
                    self._reconnect_count_without_stats = 0

                    # Parse and POST to Flask so the live report updates
                    self._post_to_flask(parse_ios_stats(raw_stats))

                    # Also write raw values to the local CSV for debugging
                    row = {"timestamp": datetime.now().isoformat(),
                           "elapsed_sec": f"{elapsed:.1f}",
                           **{k: raw_stats.get(k, "") for k in
                              ["conn_speed", "readahead", "viewport", "framedrop",
                               "video", "audio", "net_activity", "cpn"]}}
                    with open(csv_path, "a", newline="", encoding="utf-8") as fh:
                        csv_mod.DictWriter(fh, fieldnames=raw_headers).writerow(row)
                    poll_count += 1

                else:
                    consecutive_misses += 1
                    logger.warning("[%s] Stats not found (%d/%d)",
                                   self.device_udid, consecutive_misses, self.stats_miss_threshold)

                    #  Miss threshold exceeded: escalating recovery
                    if consecutive_misses >= self.stats_miss_threshold:
                        self._reconnect_count_without_stats += 1
                        if self._reconnect_count_without_stats >= 2:
                            # Soft reconnects have not restored stats — do a
                            # hard reset (app restart) and re-enable Stats for Nerds.
                            logger.error("[%s] Hard reset triggered", self.device_udid)
                            if self._reconnect_session(force=True, hard_reset=True):
                                consecutive_misses = 0
                                consecutive_errors = 0
                                self._enable_stats_for_nerds()
                            else:
                                self._shutdown.set()
                                break
                        else:
                            if self._reconnect_session(force=True):
                                consecutive_misses = 0
                                consecutive_errors = 0
                            else:
                                self._shutdown.set()
                                break
                        time.sleep(interval)
                        continue

                time.sleep(interval)

            except Exception as exc:
                consecutive_errors += 1
                msg = str(exc).lower()
                # Session-expired errors require immediate reconnect regardless
                # of the consecutive error count.
                is_sess = ("404" in msg or "invalid session id" in msg
                           or "session does not exist" in msg)
                if is_sess or consecutive_errors >= 3:
                    if self._reconnect_session(force=True):
                        consecutive_errors = 0
                        consecutive_misses = 0
                    else:
                        self._shutdown.set()
                        break
                time.sleep(interval)

        #  Notify Flask that this device's collection window has closed
        self._signal_stop_to_flask()
        logger.info("[%s] Stats polling done — %d rows -> %s",
                    self.device_udid, poll_count, csv_path)


def _candela_connect(udid: str, hub_url: str, bundle_id: str, secret: str):
    """
    Create an Appium session for the Candela interop iOS app.

    Builds a minimal capability set for the Candela app — no reset so that
    pre-filled form data (manager IP, testroom name) is preserved from a
    prior configuration step.  The session timeout is set to 10 minutes which
    is enough for the testroom join sequence without risking an idle timeout.

    Args:
        udid (str): iOS device UDID.
        hub_url (str): GADS hub URL (same hub used for YouTube automation).
        bundle_id (str): Bundle ID of the Candela interop app.
        secret (str): GADS client secret for hub authentication.

    Returns:
        webdriver.Remote: An active Appium session connected to the Candela app.
    """
    options = XCUITestOptions()
    options.set_capability("udid", udid)
    options.set_capability("platformName", "iOS")
    options.set_capability("automationName", "XCUITest")
    options.set_capability("bundleId", bundle_id)
    options.set_capability("noReset", True)
    options.set_capability("shouldUseSingletonTestManager", False)
    options.set_capability("newCommandTimeout", 600)
    if secret:
        options.set_capability("gads:clientSecret", secret)
    logger.info("[%s] Connecting to Candela interop app at %s", udid, hub_url)
    return webdriver.Remote(hub_url, options=options)


def _candela_find_testroom_button(driver, timeout: int):
    """
    Wait for the testroom button to become clickable in the Candela interop app.

    Uses an explicit WebDriverWait so that transient loading states (e.g.,
    network discovery taking a moment) do not cause an immediate failure.

    Args:
        driver: Active Appium WebDriver session for the Candela app.
        timeout (int): Maximum seconds to wait for the button to appear.

    Returns:
        WebElement: The testroom button element once it is clickable.

    Raises:
        TimeoutException: If the button does not appear within ``timeout`` seconds.
    """
    wait = WebDriverWait(driver, timeout)
    predicate = (
        "type == 'XCUIElementTypeButton' AND visible == 1 AND enabled == 1 "
        "AND (name == 'testroom' OR label == 'testroom')"
    )
    return wait.until(EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, predicate)))


def _candela_handle_post_join_popups(driver, timeout: int):
    """
    Dismiss iOS system alert dialogs that appear after tapping testroom.

    Two popup types may appear after initiating a testroom join:
    1. Location permission alert ("Always Allow") — only on first launch.
    2. Network join confirmation ("Join" / "Join Network").

    Both are handled by inspecting the available alert buttons and tapping
    the expected label.  The loop runs until both alerts are handled or the
    deadline is reached.

    Args:
        driver: Active Appium WebDriver session.
        timeout (int): Seconds to spend handling popups (minimum 8 seconds
            to allow multiple alerts to appear sequentially).
    """
    join_labels = {"Join", "Join Network"}
    location_labels = {"Always Allow"}
    deadline = time.time() + max(8, timeout)
    handled_join = False
    handled_location = False
    while time.time() < deadline:
        try:
            _ = driver.switch_to.alert
        except Exception:
            time.sleep(0.4)
            continue
        try:
            buttons = driver.execute_script("mobile: alert", {"action": "getButtons"}) or []
        except Exception:
            time.sleep(0.4)
            continue
        if not isinstance(buttons, list) or not buttons:
            time.sleep(0.4)
            continue
        button_set = set(buttons)
        target = None

        # Prioritise the location alert (if not yet handled) so it is dismissed
        # before the network join alert, matching the expected iOS dialog order.
        if not handled_location:
            for lbl in location_labels:
                if lbl in button_set:
                    target = lbl
                    break
        if target is None and not handled_join:
            for lbl in join_labels:
                if lbl in button_set:
                    target = lbl
                    break
        if target is None:
            time.sleep(0.4)
            continue
        try:
            driver.execute_script("mobile: alert", {"action": "accept", "buttonLabel": target})
            if target in location_labels:
                handled_location = True
                logger.info("Handled location permission popup (Always Allow)")
            if target in join_labels:
                handled_join = True
                logger.info("Handled network join popup (Join)")
            time.sleep(0.5)
        except Exception:
            time.sleep(0.4)
        if handled_join and handled_location:
            break


def run_candela_interop_flow(udid: str, hub_url: str, bundle_id: str, secret: str,
                             timeout: int = 20) -> bool:
    """
    Connect to the Candela interop app and tap the testroom button.

    Called after the YouTube test completes to signal the Candela app that the
    device should re-join the testroom.  The app's form fields (manager IP,
    testroom name) are assumed to be pre-filled from a prior configuration step,
    so this flow only needs to tap the testroom button and handle any resulting
    system popups.

    Args:
        udid (str): iOS device UDID.
        hub_url (str): GADS hub URL.
        bundle_id (str): Candela interop app bundle ID.
        secret (str): GADS client secret.
        timeout (int): Element wait timeout in seconds.

    Returns:
        bool: True if the testroom button was tapped and popups were handled;
        False if a timeout, WebDriver error, or unexpected exception occurred.
    """
    driver = None
    try:
        #  Establish Appium session for the Candela app
        driver = _candela_connect(udid, hub_url, bundle_id, secret)

        #  Wait for and tap the testroom button
        button = _candela_find_testroom_button(driver, timeout)
        button.click()

        #  Dismiss post-join system dialogs
        _candela_handle_post_join_popups(driver, timeout)
        logger.info("[%s] Candela interop: tapped testroom button", udid)
        return True
    except TimeoutException as e:
        logger.error("[%s] Candela interop timeout — element not found: %s", udid, e)
        return False
    except WebDriverException as e:
        logger.error("[%s] Candela interop WebDriver error: %s", udid, e)
        return False
    except Exception as e:
        logger.error("[%s] Candela interop unexpected error: %s", udid, e)
        return False
    finally:
        # Always quit the driver to release the GADS hub session slot
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def main():
    """
    CLI entry point for the iOS YouTube automation script.

    Parses command-line arguments, constructs an ``iOSYouTubeAutomation``
    instance, runs the full test, and then triggers the Candela interop
    post-test flow before exiting.

    Duration is accepted in minutes (matching the lf_interop_youtube.py
    convention) and converted to seconds when constructing the automation object.

    Exit code:
        0 — test completed successfully.
        1 — test failed (session error, video never started, etc.).
    """
    parser = argparse.ArgumentParser(
        description="iOS YouTube automation for LANforge interop testing"
    )
    parser.add_argument("--udid", required=True, help="iOS device UDID")
    parser.add_argument("--url", required=True, help="YouTube video URL")
    parser.add_argument(
        "--duration", type=int, required=True,
        help="Test duration in minutes (matches lf_interop_youtube convention)",
    )
    parser.add_argument("--host", required=True, help="LANforge host IP (Flask server)")
    parser.add_argument("--device_name", required=True, help="Device hostname for reporting")
    parser.add_argument("--res", default="Auto", help="Target video resolution")
    parser.add_argument(
        "--gads_hub", default=None,
        help="GADS hub URL",
    )
    parser.add_argument("--stats_interval", type=int, default=3,
                        help="Stats polling interval in seconds (default: 3)")
    parser.add_argument("--session_retries", type=int, default=3,
                        help="Appium session retry attempts (default: 3)")
    parser.add_argument("--candela_bundle_id", default="com.candela.wecan.interop-ios",
                        help="Candela interop app bundle ID (default: com.candela.wecan.interop-ios)")
    parser.add_argument("--candela_timeout", type=int, default=20,
                        help="Element wait timeout in seconds for Candela flow (default: 20)")
    args = parser.parse_args()

    #  Build the automation object
    automation = iOSYouTubeAutomation(
        flask_host=args.host,
        device_name=args.device_name,
        device_udid=args.udid,
        video_url=args.url,
        duration=args.duration * 60,   # minutes → seconds
        hub_url=args.gads_hub,
        stats_poll_interval=args.stats_interval,
        enable_network_trace=False,
        session_retries=args.session_retries,
    )

    #  Run the YouTube test
    success = automation.run()

    # Re-join the Candela interop testroom
    # This runs regardless of whether the YouTube test succeeded so that the
    # device is always returned to a known ready state in the Candela app.
    hub = args.gads_hub
    secret = os.getenv("GADS_CLIENT_SECRET", "")
    run_candela_interop_flow(
        udid=args.udid,
        hub_url=hub,
        bundle_id=args.candela_bundle_id,
        secret=secret,
        timeout=args.candela_timeout,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
