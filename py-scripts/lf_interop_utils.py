"""
Shared helpers for interop test scripts (lf_webpage.py, lf_ftp.py, lf_interop_*.py, ...).

LANforge server versions occasionally rename layer4/CX API field names (for example, the
RX-rate 1-minute-average column has been seen as both 'rx rate (1m)' and 'rx-rate-1m' across
different server builds). Requesting a name a given server doesn't recognize fails the whole
layer4 query and logs a "Columns do not include" error from the server. Scripts that need to
work across server versions should resolve field names through resolve_layer4_fields() below
instead of hardcoding one spelling, so a server-side rename doesn't turn into a broken request
in every script that touches that field.
"""
import logging

logger = logging.getLogger(__name__)

# Known alternate spellings LANforge servers have used for the same layer4 column, newest
# known name first. Every field read from a layer4 record should have an entry here (even a
# single-alias one) so a future rename only needs a new alias added in one place.
LAYER4_FIELD_ALIASES = {
    'uc_avg': ['uc-avg'],
    'uc_max': ['uc-max'],
    'uc_min': ['uc-min'],
    'total_urls': ['total-urls'],
    'rx_rate_1m': ['rx-rate-1m', 'rx rate (1m)'],
    'tx_rate_1m': ['tx-rate-1m', 'tx rate (1m)'],
    'bytes_rd': ['bytes-rd'],
    'total_err': ['total-err'],
    'status': ['status'],
}


def resolve_layer4_fields(local_realm, cx_name, field_keys, defaults=None):
    """
    Determine which of each layer4 column's known alternate names this LANforge server
    actually uses, without ever sending a request that names an unsupported column (which
    would otherwise trigger a "Columns do not include" error from the server). Resolves every
    requested field from a single probe request.

    Args:
        local_realm: Realm instance used to make the probe request.
        cx_name: name of an existing CX to probe; its columns reflect what the server supports.
        field_keys: iterable of keys into LAYER4_FIELD_ALIASES to resolve.
        defaults: optional {field_key: name} overrides for the fallback if detection fails;
            otherwise the first known alias for that field is used.

    Returns:
        dict: {field_key: resolved_api_field_name}, one entry per requested field_key.
    """
    defaults = defaults or {}
    candidates_by_key = {key: LAYER4_FIELD_ALIASES.get(key, [key]) for key in field_keys}
    resolved = {key: defaults.get(key, candidates[0]) for key, candidates in candidates_by_key.items()}
    if not cx_name:
        return resolved
    try:
        # No 'fields' filter: the server returns every column it supports for this CX, so we
        # can check which alias is present without risking an invalid-field-name error.
        probe = local_realm.json_get('layer4/{}/list'.format(cx_name))
        endpoint = probe.get('endpoint') if probe else None
        if isinstance(endpoint, list) and endpoint:
            endpoint = list(endpoint[0].values())[0]
        if isinstance(endpoint, dict):
            for key, candidates in candidates_by_key.items():
                for candidate in candidates:
                    if candidate in endpoint:
                        resolved[key] = candidate
                        break
    except Exception:
        logger.warning("Could not probe layer4 columns, using default field names: %s", resolved)
    return resolved


def layer4_fields_query(resolved_fields, field_keys):
    """Build the comma-separated 'fields=' value for a layer4 list request, in order, from a
    resolve_layer4_fields() result."""
    return ','.join(resolved_fields[key] for key in field_keys)
