#!/usr/bin/env python3
"""
Shared, lightweight API call logger.

This exists so any code path that talks to a LANforge GUI -- the legacy
py-json/LANforge/LFRequest.py request layer (used via LFCliBase/Realm), or
lanforge_api.py's own request layer -- can record the same kind of entry
(url, payload, response code, session id) to the same kind of rotating log
file, without each path reimplementing rotation/formatting itself.
"""
import os
import json
import logging
import logging.handlers
import datetime

_api_loggers = {}


def get_api_logger(filename, max_bytes=10 * 1024 * 1024, backup_count=10):
    """
    Return a cached, rotating file logger for `filename`. Callers that pass the same
    filename (even from different LFCliBase/Realm instances, or a different request layer
    entirely) share one logger/handler, so log lines are never duplicated and the file
    rotates once instead of racing multiple independent handlers against each other.
    :param filename: path to the api log file
    :param max_bytes: rotate once the active file reaches this size
    :param backup_count: number of rotated backups to keep
    :return: a logging.Logger configured with a RotatingFileHandler
    """
    key = os.path.abspath(filename)
    if key in _api_loggers:
        return _api_loggers[key]
    api_logger = logging.getLogger("lanforge_client.api_call_logger.%s" % key)
    api_logger.setLevel(logging.INFO)
    api_logger.propagate = False
    handler = logging.handlers.RotatingFileHandler(filename, maxBytes=max_bytes, backupCount=backup_count)
    handler.setFormatter(logging.Formatter("%(message)s"))
    api_logger.addHandler(handler)
    _api_loggers[key] = api_logger
    return api_logger


def log_api_call(api_logger, method, url, session_id=None, data=None, response_code=None, error=None,
                 diagnostics=None):
    """
    Format and emit one lightweight record of an API call via api_logger. No-op if
    api_logger is None, so callers can pass through a possibly-absent logger without
    guarding every call site themselves.
    :param api_logger: a logger from get_api_logger(), or None to skip silently
    :param method: "GET" | "POST" | "PUT" | "DELETE"
    :param url: requested url
    :param session_id: the lanforge_api session id ("cookie") tying this call to the
    LANforge GUI's own request logs, if available
    :param data: payload sent (POST/PUT only)
    :param response_code: HTTP status code returned by the call, if any
    :param error: exception raised by the call, if any -- marks the entry as ERROR
    :param diagnostics: one-line summary of a caught HTTPError/URLError (reason,
    X-Error-* headers, etc.)
    """
    if api_logger is None:
        return
    if error is not None:
        status = "ERROR"
    elif response_code is not None:
        status = "OK" if 200 <= response_code < 300 else "ERROR"
    else:
        status = "UNKNOWN"
    lines = ["%s session=%s %s %s [%s]" %
            (datetime.datetime.now().isoformat(), session_id or '-', method, url, status)]
    if data is not None:
        lines.append("  payload: %s" % json.dumps(data, default=str))
    if error is not None:
        lines.append("  error: %s" % error)
    if response_code is not None:
        lines.append("  response_code: %s" % response_code)
    if diagnostics is not None:
        lines.append("  diagnostics: %s" % diagnostics)
    try:
        api_logger.info("\n".join(lines))
    except Exception:
        logging.getLogger(__name__).debug("log_api_call: unable to emit log line", exc_info=True)
