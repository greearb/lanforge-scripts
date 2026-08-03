"""
Process-wide, opt-in CSV logging of LANforge API calls (GET/POST/PUT/DELETE), for
debugging a particular test run.

Call configure_api_call_logging() once, near the start of a script; every API call
made afterward in the same process is then recorded automatically.
"""
import csv
import datetime
import json
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

# CSV header for API call logs with prefixed column names to avoid ambiguity across reports.
CSV_FIELDS = ['api_timestamp', 'api_method', 'api_url', 'api_status', 'api_response_code',
              'api_elapsed_ms', 'api_payload', 'api_error', 'api_diagnostics']

_logging_enabled = False
_logging_paused = False
_log_filename = None


def configure_api_call_logging(enabled: bool, log_filename: Optional[str] = None) -> None:
    """
    Enable or disable process-wide API-call logging.

    Args:
        enabled: True to turn logging on, False to turn it off.
        log_filename: Path to the CSV log file; defaults to ~/lf_api_calls.csv when not set.

    Returns:
        None.
    """
    global _logging_enabled, _log_filename, _logging_paused
    _logging_enabled = bool(enabled)
    _logging_paused = False
    if not _logging_enabled:
        return
    _log_filename = log_filename or os.path.join(os.path.expanduser('~'), 'lf_api_calls.csv')
    # start each run with a clean log file
    try:
        with open(_log_filename, 'w', newline='') as csv_file:
            csv.writer(csv_file).writerow(CSV_FIELDS)
    except Exception as x:
        logger.debug("api_logger: unable to reset %s: %s" % (_log_filename, x))


def pause() -> None:
    """
    Temporarily stop recording API calls until resume() is called.

    Returns:
        None.
    """
    global _logging_paused
    _logging_paused = True


def resume() -> None:
    """
    Resume recording API calls after pause().

    Returns:
        None.
    """
    global _logging_paused
    _logging_paused = False


def is_enabled() -> bool:
    """
    Check whether API-call logging is currently enabled.

    Returns:
        True if logging is enabled, False otherwise.
    """
    return _logging_enabled


def get_log_filename() -> Optional[str]:
    """
    Get the path of the API-call log CSV file.

    Returns:
        The log file path, or None if logging has not been configured.
    """
    return _log_filename


def record_api_call(method: str, url: str, data: Optional[Any] = None, response_code: Optional[int] = None,
                    error: Optional[Exception] = None, diagnostics: Optional[str] = None,
                    sent_at: Optional[datetime.datetime] = None,
                    elapsed_ms: Optional[float] = None) -> None:
    """
    Append one CSV row for a json_get/json_post/json_put/json_delete call. No-op unless
    configure_api_call_logging(enabled=True) was called first, or while paused (see pause()/resume()).

    Args:
        method: "GET" | "POST" | "PUT" | "DELETE".
        url: Requested url.
        data: Payload sent (POST/PUT only).
        response_code: HTTP status code returned by the call, if any.
        error: Exception raised by the call, if any -- marks the entry as ERROR.
        diagnostics: One-line summary from LFRequest.print_diagnostics(), if the call
            went through a caught HTTPError/URLError (reason, X-Error-* headers, etc.)
        sent_at: Timestamp captured by the caller right before the request was issued.
            Falls back to datetime.now() (this function's call time) when not provided,
            which is captured well after the request completed and is less accurate.
        elapsed_ms: Wall-clock duration of the underlying urlopen() call in milliseconds,
            measured by the caller with time.perf_counter() around just the request itself
            (excludes diagnostics/logging overhead). None when not measured.

    Returns:
        None.
    """
    if not _logging_enabled or _logging_paused:
        return
    if error:
        status = "ERROR"
    elif response_code:
        status = "OK" if 200 <= response_code < 300 else "ERROR"
    else:
        status = "UNKNOWN"
    try:
        with open(_log_filename, 'a', newline='') as csv_file:
            csv.writer(csv_file).writerow([
                (sent_at or datetime.datetime.now()).isoformat(),
                method,
                url,
                status,
                response_code if response_code is not None else 'No response_code',
                round(elapsed_ms, 3) if elapsed_ms is not None else 'Unknown',
                json.dumps(data, default=str) if data is not None else '-',
                error,
                diagnostics if diagnostics is not None else 'No diagnostics',
            ])
    except Exception as x:
        logger.debug("api_logger: unable to write %s: %s" % (_log_filename, x))
