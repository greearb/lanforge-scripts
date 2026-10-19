#!/usr/bin/env python3

'''
    NAME: lf_interop_bg_ping.py

    PURPOSE: lf_interop_bg_ping.py lets any interop test run a ping on its real clients in the
    background while the test itself drives traffic, and appends the collected ping statistics to
    the test report.

    The ping runs on the LANforge side as a generic cross-connect (lfping), so it keeps running
    without the calling script having to drive it. A sampler thread polls the endpoints while the
    test runs so latency and loss are captured even for long runs.

    EXAMPLE-1:
    Enabling the background ping from any interop script that supports it
    python3 lf_interop_qos.py --ap_name Cisco --mgr 192.168.207.75 --mgr_port 8080 --upstream_port eth1 --traffic_type lf_udp
    --tos "VO,VI,BE,BK" --download 0 --upload 1000000 --test_duration 1m --device_list 1.20,1.59,1.65
    --enable_bg_ping --bg_ping_target 1.1.eth1

    EXAMPLE-2:
    Enabling the background ping with a custom packet interval and sampling interval
    python3 lf_interop_qos.py --ap_name Cisco --mgr 192.168.207.75 --mgr_port 8080 --upstream_port eth1 --traffic_type lf_udp
    --tos "VO,VI,BE,BK" --download 0 --upload 1000000 --test_duration 1m --device_list 1.20,1.59,1.65
    --enable_bg_ping --bg_ping_target 192.168.50.178 --bg_ping_interval 0.5 --bg_ping_sample_interval 10

    EXAMPLE-3:
    Enabling the background ping for http script
    python3 lf_webpage.py --mgr 192.168.207.75 --upstream_port 1.eth1 --client_type Real --bands 5G --file_size 8MB
    --duration 1m --fiveg_passwd sharedsecret --device_list 1.59 --wifi_analysis --enable_bg_ping --bg_ping_target 8.8.8.8

    SCRIPT_CLASSIFICATION : Library/Utils

    SCRIPT_CATEGORIES: Report Generation

    NOTES:
    1.The target may be an IP, a domain name or a LANforge port such as 1.1.eth1, which is resolved to its IP
    2.iOS devices are skipped because generic endpoints are not supported on them
    3.The background ping never aborts the calling test, all failures are logged and the test continues

    License: Free to distribute and modify. LANforge systems must be licensed.
    Copyright (C) 2020-2026 Candela Technologies Inc.
'''

import os
import re
import sys
import time
import logging
import threading

import pandas as pd

_PY_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_DIR = os.path.dirname(_PY_SCRIPTS_DIR)
for _import_dir in (_PY_SCRIPTS_DIR, os.path.join(_REPO_DIR, 'py-json'), _REPO_DIR):
    if _import_dir not in sys.path:
        sys.path.append(_import_dir)

from lf_interop_ping import Ping  # noqa: E402

logger = logging.getLogger(__name__)

CUMULATIVE_PATTERN = re.compile(r'min/avg/max:?\s*([0-9]+\.?[0-9]*)/([0-9]+\.?[0-9]*)/([0-9]+\.?[0-9]*)')
DROP_PATTERN = re.compile(r'drop:\s*([0-9]+)')
RX_PATTERN = re.compile(r'rx:\s*([0-9]+)')
RTT_PATTERN = re.compile(r'time[=<]\s*([0-9]+\.?[0-9]*)\s*ms', re.IGNORECASE)
SEQ_PATTERN = re.compile(r'icmp_seq=([0-9]+)')
DROPPED_DETECTED_PATTERN = re.compile(r'Dropped packets detected:\s*sq\[(\d+)\]\s*last_sq\+1\[(\d+)\]')

OS_TYPE_LABELS = {
    'android': 'Android',
    'windows': 'Windows',
    'linux': 'Linux',
    'macos': 'Mac',
}


class BackgroundPing:
    """Runs lfping on real clients in the background for the duration of another interop test.

    The calling script only needs to construct the object, call start() before its traffic
    begins, stop() once its traffic ends and add_to_report() while building its report.
    """

    NAME_PREFIX = 'bgping'

    def __init__(self,
                 host=None,
                 port=8080,
                 target=None,
                 interval=1,
                 device_list=None,
                 sample_interval=10,
                 lanforge_password='lanforge',
                 debug=False):
        self.host = host
        self.port = port
        self.target = target
        self.interval = interval
        self.sample_interval = sample_interval
        self._sequence_poll_interval = max(0.25, self.interval / 2)
        self.debug = debug
        self.requested_devices = list(device_list) if device_list else []

        self.ping = Ping(host=host,
                         port=port,
                         target=target,
                         interval=interval,
                         lanforge_password=lanforge_password,
                         sta_list=[],
                         real=True,
                         virtual=False,
                         duration=0,
                         debug=debug)
        self.ping.generic_endps_profile.name_prefix = self.NAME_PREFIX

        self.device_os = {}
        self.device_data = {}
        self.samples = {}
        self.timeline_samples = {}
        self.sequence_rtts = {}
        self.sequence_dropped_total = {}
        self.started = False
        self.start_time = None
        self.stop_time = None
        self.monitor_window_start = None
        self.monitor_window_end = None
        self.stats = {}
        self._previous_lines = {}
        self._stop_event = threading.Event()
        self._sampler_thread = None
        self._sequence_sampler_thread = None

    def json_get(self, path):
        try:
            return self.ping.json_get(path)
        except Exception as e:
            logger.warning('Background ping query %s failed: %s', path, e)
            return None

    def resolve_target(self):
        """Converts a LANforge port such as 1.1.eth1 into the IP the clients should ping."""
        if not self.target:
            return None

        if self.target.count('.') == 3 and all(part.isdigit() for part in self.target.split('.')):
            return self.target

        eid = self.ping.name_to_eid(self.target)
        if len(eid) < 3 or not eid[2]:
            return self.target

        response = self.json_get('/port/{}/{}/{}?fields=ip'.format(eid[0], eid[1], eid[2]))
        if response and 'interface' in response and response['interface'].get('ip'):
            resolved = response['interface']['ip']
            logger.info('Background ping target %s resolved to %s', self.target, resolved)
            return resolved

        logger.warning('Could not resolve the background ping target %s, using it as given', self.target)
        return self.target

    def discover_devices(self):
        """Builds the ping capable subset of the devices the calling test was given.

        Only the devices the calling test is running on are considered, never anything else on
        the testbed. Of those, phantom, down, address-less and iOS devices are dropped because a
        ping cannot be run on them.
        """
        requested_ports = set()
        requested_resources = set()
        for device in self.requested_devices:
            device = str(device).strip()
            if not device:
                continue
            parts = device.split('.')
            if len(parts) == 1:
                requested_resources.add('1.' + parts[0])
            elif len(parts) == 2:
                requested_resources.add(device)
            else:
                requested_ports.add('.'.join(parts[:3]))

        if not requested_ports and not requested_resources:
            logger.error('The background ping was given no devices to run on, skipping it')
            return []

        ports_named_for = {'.'.join(port.split('.')[:2]) for port in requested_ports}
        requested_resources -= ports_named_for

        resources = self.json_get('/resource/all')
        if not resources or 'resources' not in resources:
            logger.warning('Background ping could not read the resource list')
            return []

        resource_os = {}
        resource_name = {}
        ios_resources = set()
        for resource_entry in resources['resources']:
            resource_id = list(resource_entry.keys())[0]
            resource_data = resource_entry[resource_id]
            if not isinstance(resource_data, dict) or 'hw version' not in resource_data:
                continue

            if resource_data.get('ct-kernel'):
                continue

            resource_name[resource_id] = resource_data.get('user', '') or resource_data.get('hostname', '')

            hw_version = resource_data.get('hw version', '')
            app_id = resource_data.get('app-id', '')
            kernel = resource_data.get('kernel', '')

            if 'Apple' in hw_version and app_id != '' and (app_id != '0' or kernel == ''):
                ios_resources.add(resource_id)
                continue

            if 'Win/x86' in hw_version:
                resource_os[resource_id] = 'windows'
            elif 'Apple/x86' in hw_version:
                resource_os[resource_id] = 'macos'
            elif 'Linux/x86' in hw_version:
                resource_os[resource_id] = 'linux'
            else:
                resource_os[resource_id] = 'android'

        ports = self.json_get('/ports/all')
        if not ports or 'interfaces' not in ports:
            logger.warning('Background ping could not read the port list')
            return []

        selected = []
        matched_requests = set()
        for port_entry in ports['interfaces']:
            port_id = list(port_entry.keys())[0]
            port_data = port_entry[port_id]
            parts = port_id.split('.')
            if len(parts) != 3:
                continue
            resource_id = parts[0] + '.' + parts[1]

            if port_id in requested_ports:
                request = port_id
            elif resource_id in requested_resources and port_data.get('parent dev') == 'wiphy0':
                request = resource_id
            else:
                continue

            matched_requests.add(request)

            if resource_id in ios_resources:
                logger.info('Skipping the iOS device %s for the background ping, a ping cannot be run on it', resource_id)
                continue

            if resource_id not in resource_os:
                logger.info('Skipping %s for the background ping, it is not a real client', port_id)
                continue

            if port_data.get('phantom') or port_data.get('down'):
                logger.info('Skipping %s for the background ping, the port is down or phantom', port_id)
                continue

            port_ip = port_data.get('ip')
            if not port_ip or port_ip == '0.0.0.0':
                logger.info('Skipping %s for the background ping, the client has no IP', port_id)
                continue

            selected.append(port_id)
            self.device_os[port_id] = resource_os[resource_id]
            device_data = dict(port_data)
            device_data.setdefault('user', resource_name.get(resource_id, ''))
            self.device_data[port_id] = device_data

        unmatched = sorted((requested_ports | requested_resources) - matched_requests)
        if unmatched:
            logger.warning('Background ping could not find the devices %s on the LANforge', unmatched)

        logger.info('The background ping will run on %s of the %s devices the test was given',
                    selected, len(self.requested_devices))

        return selected

    def pre_cleanup(self):
        """Removes background ping endpoints left over by an earlier run."""
        response = self.json_get('/generic/list?fields=name')
        if not response:
            return

        endpoints = response.get('endpoints', response.get('endpoint', []))
        if isinstance(endpoints, dict):
            endpoints = [endpoints]

        stale_endps = []
        for endpoint in endpoints:
            if not isinstance(endpoint, dict):
                continue
            for key, value in endpoint.items():
                name = value.get('name') if isinstance(value, dict) else key
                if name and name.startswith(self.NAME_PREFIX + '-'):
                    stale_endps.append(name)

        if not stale_endps:
            return

        logger.info('Removing the stale background ping endpoints %s', stale_endps)
        self.ping.generic_endps_profile.created_endp = stale_endps
        self.ping.generic_endps_profile.created_cx = ['CX_{}'.format(name) for name in stale_endps]
        self.ping.generic_endps_profile.cleanup()
        self.ping.generic_endps_profile.created_endp = []
        self.ping.generic_endps_profile.created_cx = []

    def start(self):
        """Creates and starts the ping endpoints. Returns True when the ping is running."""
        if not self.target:
            logger.error('No background ping target was given, the background ping is disabled')
            return False

        if not self.ping.check_tab_exists():
            logger.error('The Generic tab is not available, skipping the background ping')
            return False

        self.target = self.resolve_target()
        self.ping.target = self.target
        self.ping.generic_endps_profile.dest = self.target
        self.ping.generic_endps_profile.interval = self.interval

        devices = self.discover_devices()
        if not devices:
            logger.error('No ping capable real devices were found, skipping the background ping')
            return False

        self.ping.real_sta_list = devices
        self.ping.sta_list = list(devices)
        self.samples = {device: self._empty_sample() for device in devices}
        self.timeline_samples = {
            device: [{'time': 0.0, 'sent': 0, 'received': 0, 'dropped': 0}]
            for device in devices
        }
        self.sequence_rtts = {device: {} for device in devices}
        self.sequence_dropped_total = {device: 0 for device in devices}
        self._previous_lines = {device: [] for device in devices}

        try:
            self.pre_cleanup()
            os_types = [self.device_os[device] for device in devices]
            if not self.ping.generic_endps_profile.create(ports=devices, sleep_time=.5, real_client_os_types=os_types):
                logger.error('Background ping endpoint creation failed')
                return False
            for endpoint in self.ping.generic_endps_profile.created_endp:
                self.ping.generic_endps_profile.set_report_timer(endp_name=endpoint, timer=250)
            self.ping.start_generic()
        except Exception as e:
            logger.error('Background ping could not be started: %s', e)
            return False

        self.started = True
        self.start_time = time.time()
        logger.info('Background ping started on %s devices towards %s', len(devices), self.target)

        if self.sample_interval:
            self._stop_event.clear()
            self._sampler_thread = threading.Thread(target=self._sampler, daemon=True)
            self._sampler_thread.start()
            self._sequence_sampler_thread = threading.Thread(target=self._sequence_sampler, daemon=True)
            self._sequence_sampler_thread.start()

        return True

    def _sampler(self):
        while not self._stop_event.is_set():
            if self._stop_event.wait(self.sample_interval):
                break
            try:
                self.sample()
            except Exception as e:
                logger.warning('Background ping sampling failed: %s', e)

    def _sequence_sampler(self):
        while not self._stop_event.is_set():
            if self._stop_event.wait(self._sequence_poll_interval):
                break
            try:
                self._sample_sequences()
            except Exception as e:
                logger.warning('Background ping per-packet sampling failed: %s', e)

    def _results_by_device(self):
        """Returns the raw endpoint data of every background ping endpoint, keyed by device."""
        results = self.ping.get_results()
        by_device = {}

        if isinstance(results, dict):
            if 'name' in results:
                results = [{results['name']: results}]
            else:
                results = [results]

        if not isinstance(results, list):
            return by_device

        for entry in results:
            if not isinstance(entry, dict):
                continue
            for key, value in entry.items():
                if not isinstance(value, dict):
                    continue
                name = value.get('name', key)
                if not name.startswith(self.NAME_PREFIX + '-'):
                    continue
                by_device[name[len(self.NAME_PREFIX) + 1:]] = value

        return by_device

    @staticmethod
    def _empty_sample():
        return {'min': None, 'avg': None, 'max': None, 'rx': None, 'drop': None,
                'count': 0, 'total': 0.0, 'observed_min': None, 'observed_max': None,
                'last_line': ''}

    def sample(self, record_timeline=True):
        """Reads the endpoint output once and folds it into the running per device statistics.

        Sampling while the test runs means the statistics survive an endpoint that stops
        reporting, and it keeps 'last results' from rolling over unread on long runs.
        """
        sample_time = time.time()
        for device, endpoint_data in self._results_by_device().items():
            if device not in self.samples:
                continue

            if record_timeline:
                self._record_timeline_sample(device, endpoint_data, sample_time)

            last_results = endpoint_data.get('last results', '') or ''
            lines = [line for line in last_results.split('\n') if line.strip()]
            if not lines:
                continue

            stats = self.samples[device]
            stats['last_line'] = lines[-1]

            cumulative_found = False
            for line in reversed(lines):
                match = CUMULATIVE_PATTERN.search(line)
                if not match:
                    continue
                stats['min'] = float(match.group(1))
                stats['avg'] = float(match.group(2))
                stats['max'] = float(match.group(3))

                drop_match = DROP_PATTERN.search(line)
                if drop_match:
                    stats['drop'] = int(drop_match.group(1))
                rx_match = RX_PATTERN.search(line)
                if rx_match:
                    stats['rx'] = int(rx_match.group(1))

                cumulative_found = True
                break

            new_lines = self._new_lines(self._previous_lines.get(device, []), lines)
            self._previous_lines[device] = lines

            if cumulative_found:
                continue

            for line in new_lines:
                match = RTT_PATTERN.search(line)
                if not match:
                    continue
                rtt = float(match.group(1))
                stats['count'] += 1
                stats['total'] += rtt
                if stats['observed_min'] is None or rtt < stats['observed_min']:
                    stats['observed_min'] = rtt
                if stats['observed_max'] is None or rtt > stats['observed_max']:
                    stats['observed_max'] = rtt

    def _sample_sequences(self):
        """Reads and reprocesses each endpoint's whole reply buffer every poll (like lf_interop_ping_plotter.py), so a gap can only come from real eviction, never a diffing mismatch."""
        for device, endpoint_data in self._results_by_device().items():
            if device not in self.sequence_rtts:
                continue

            last_results = endpoint_data.get('last results', '') or ''
            lines = [line for line in last_results.split('\n') if line.strip()]
            if not lines:
                continue

            authoritative_dropped = self._as_int(endpoint_data.get('dropped'))
            self._record_sequence_samples(device, lines, authoritative_dropped)

    def _record_sequence_samples(self, device, lines, authoritative_dropped):
        """Records each reply's icmp_seq -> RTT; lfping's own 'Dropped packets detected' lines mark exactly
        which sequences were lost, with a rise in authoritative_dropped as a fallback for anything that
        line doesn't catch."""
        sequence_rtts = self.sequence_rtts.setdefault(device, {})
        previous_drop_total = self.sequence_dropped_total.get(device, 0)
        latest_seq = None

        for line in lines:
            detected_match = DROPPED_DETECTED_PATTERN.search(line)
            if detected_match:
                arrived_seq, expected_seq = int(detected_match.group(1)), int(detected_match.group(2))
                for lost_seq in range(expected_seq, arrived_seq):
                    sequence_rtts.setdefault(lost_seq, 0.0)

            seq_match = SEQ_PATTERN.search(line)
            rtt_match = RTT_PATTERN.search(line)
            if not seq_match or not rtt_match:
                continue

            seq_number = int(seq_match.group(1))
            sequence_rtts[seq_number] = float(rtt_match.group(1))
            latest_seq = seq_number

        if latest_seq is not None and authoritative_dropped > previous_drop_total:
            for offset in range(1, authoritative_dropped - previous_drop_total + 1):
                sequence_rtts.setdefault(latest_seq - offset, 0.0)
            previous_drop_total = authoritative_dropped

        self.sequence_dropped_total[device] = previous_drop_total

    def _record_timeline_sample(self, device, endpoint_data, sample_time):
        """Stores cumulative packet counters for the connectivity timeline."""
        if self.start_time is None:
            return

        sent = self._as_int(endpoint_data.get('tx pkts'))
        received = self._as_int(endpoint_data.get('rx pkts'))
        dropped = self._as_int(endpoint_data.get('dropped'))
        if not sent:
            sent = received + dropped

        self.timeline_samples.setdefault(device, []).append({
            'time': max(0.0, sample_time - self.start_time),
            'sent': sent,
            'received': received,
            'dropped': dropped,
        })

    def connectivity_timeline_payload(self):
        """Build connectivity rows for every client, retaining no-data rows without up/drop bars."""
        if not self.start_time:
            return None

        if self.monitor_window_start is not None and self.monitor_window_end is not None:
            window_start = self.monitor_window_start
            window_end = self.monitor_window_end
        else:
            window_start = self.start_time
            window_end = self.stop_time if self.stop_time else time.time()
        duration = max(0.1, window_end - window_start)
        offset = window_start - self.start_time
        clients = []
        stations = []
        segments = []

        for device in self.ping.real_sta_list:
            seq_rtts = self.sequence_rtts.get(device) or {}
            device_data = self.device_data.get(device, {})
            label = device_data.get('user', '') or device_data.get('hostname', '') or device
            client_index = len(clients)
            clients.append(label)
            stations.append(device)

            if not seq_rtts:
                segments.append({
                    'clientIndex': client_index,
                    'start': 0.0,
                    'end': round(duration, 3),
                    'status': 'no_data',
                })
                continue

            client_segments = []

            def append_segment(status, start, end, client_segments=client_segments, client_index=client_index):
                if client_segments and client_segments[-1]['status'] == status:
                    client_segments[-1]['end'] = round(end, 3)
                else:
                    client_segments.append({
                        'clientIndex': client_index,
                        'start': round(start, 3),
                        'end': round(end, 3),
                        'status': status,
                    })

            covered_until = 0.0
            for seq in sorted(seq_rtts):
                status = 'drop' if seq_rtts[seq] == 0 else 'up'
                start = max(0.0, (seq - 1) * self.interval - offset)
                end = min(duration, seq * self.interval - offset)
                if end <= start:
                    continue

                if start > covered_until:
                    append_segment('up', covered_until, start)

                append_segment(status, start, end)
                covered_until = max(covered_until, end)

            if covered_until < duration:
                append_segment('up', covered_until, duration)

            segments.extend(client_segments)

        if not clients or not segments:
            return None

        return {
            'clients': clients,
            'stations': stations,
            'segments': segments,
            'duration': round(duration, 3),
            'emptyMessage': 'No time-series ping samples were collected',
        }

    @staticmethod
    def _new_lines(previous_lines, current_lines):
        """Returns the lines of current_lines that were not already present in previous_lines."""
        if not previous_lines:
            return current_lines

        overlap = min(len(previous_lines), len(current_lines))
        while overlap > 0:
            if previous_lines[-overlap:] == current_lines[:overlap]:
                return current_lines[overlap:]
            overlap -= 1

        return current_lines

    def stop(self):
        """Stops the ping endpoints and builds the final per device statistics."""
        if not self.started:
            return {}

        self._stop_event.set()
        if self._sampler_thread:
            self._sampler_thread.join(timeout=self.sample_interval + 5)
        if self._sequence_sampler_thread:
            self._sequence_sampler_thread.join(timeout=self._sequence_poll_interval + 5)

        try:
            self._sample_sequences()
            self.sample()
        except Exception as e:
            logger.warning('Final live background ping sample could not be collected: %s', e)

        self.stop_time = time.time()

        try:
            self.ping.stop_generic()
        except Exception as e:
            logger.warning('Background ping could not be stopped cleanly: %s', e)

        time.sleep(2)
        try:
            self._sample_sequences()
            self.sample(record_timeline=False)
            self.stats = self._build_stats()
        except Exception as e:
            logger.warning('Background ping results could not be collected: %s', e)
            self.stats = {}

        self.started = False
        return self.stats

    def _build_stats(self):
        stats = {}
        results = self._results_by_device()

        for device in self.ping.real_sta_list:
            endpoint_data = results.get(device, {})
            sampled = self.samples.get(device, self._empty_sample())

            last_point = (self.timeline_samples.get(device) or [None])[-1]
            if last_point:
                sent, received, dropped = last_point['sent'], last_point['received'], last_point['dropped']
            else:
                sent = self._as_int(endpoint_data.get('tx pkts'))
                received = self._as_int(endpoint_data.get('rx pkts'))
                dropped = self._as_int(endpoint_data.get('dropped'))

            if not received and sampled.get('rx') is not None:
                received = sampled['rx']
            if not dropped and sampled.get('drop') is not None:
                dropped = sampled['drop']
            if not sent:
                sent = received + dropped

            seq_rtts = self.sequence_rtts.get(device)
            if seq_rtts and len(seq_rtts) > sent:
                sent = len(seq_rtts)
                dropped = sum(1 for rtt in seq_rtts.values() if rtt == 0)
                received = sent - dropped

            minimum = sampled.get('min')
            average = sampled.get('avg')
            maximum = sampled.get('max')
            if minimum is None and sampled.get('count'):
                minimum = sampled['observed_min']
                maximum = sampled['observed_max']
                average = sampled['total'] / sampled['count']

            known_drop_total = dropped
            if seq_rtts and known_drop_total is not None:
                attributed_drops = sum(1 for rtt in seq_rtts.values() if rtt == 0)
                if known_drop_total > attributed_drops:
                    max_seq = max(seq_rtts)
                    for offset in range(known_drop_total - attributed_drops):
                        seq_rtts.setdefault(max_seq + 1 + offset, 0.0)

            device_data = self.device_data.get(device, {})
            os_type = self.device_os.get(device, 'linux')
            entry = {
                'device': device,
                'name': device_data.get('user', '') or device_data.get('hostname', '') or device,
                'os': OS_TYPE_LABELS.get(os_type, os_type),
                'mac': device_data.get('mac', ''),
                'ssid': device_data.get('ssid', ''),
                'channel': device_data.get('channel', ''),
                'mode': device_data.get('mode', ''),
                'target': self.target,
                'command': endpoint_data.get('command', ''),
                'sent': sent,
                'recv': received,
                'dropped': dropped,
                'loss_percent': round(((sent - received) / sent) * 100, 2) if sent else 0,
                'min_rtt': round(minimum, 2) if minimum is not None else 0,
                'avg_rtt': round(average, 2) if average is not None else 0,
                'max_rtt': round(maximum, 2) if maximum is not None else 0,
                'last_result': sampled.get('last_line', ''),
                'remarks': [],
            }
            entry['remarks'] = self.ping.generate_remarks(entry)

            if not sent and not received:
                logger.warning('The background ping produced no output on %s. The client did not run "%s", check '
                               'that the ping is runnable there.', device, entry['command'])

            stats[device] = entry

        return stats

    @staticmethod
    def _as_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def cleanup(self):
        """Removes the background ping endpoints."""
        try:
            self.ping.generic_endps_profile.cleanup()
            self.ping.generic_endps_profile.created_cx = []
            self.ping.generic_endps_profile.created_endp = []
        except Exception as e:
            logger.warning('Background ping cleanup failed: %s', e)

    def set_monitor_window(self, start_dt, end_dt):
        """Sets the exact datetime.datetime window the calling test's monitor loop covered, so the graph/duration line up with it instead of bg_ping's own wider start-to-stop lifetime."""
        if start_dt is None or end_dt is None:
            return
        try:
            self.monitor_window_start = start_dt.timestamp()
            self.monitor_window_end = end_dt.timestamp()
        except (AttributeError, OSError, OverflowError, ValueError) as e:
            logger.warning('Background ping could not use the given monitor window (%r, %r): %s', start_dt, end_dt, e)

    def duration_string(self):
        if self.monitor_window_start is not None and self.monitor_window_end is not None:
            total_seconds = int(self.monitor_window_end - self.monitor_window_start)
        else:
            if not self.start_time:
                return ''
            end = self.stop_time if self.stop_time else time.time()
            total_seconds = int(end - self.start_time)
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

    def to_dataframe(self, device_info=None):
        """Builds the ping statistics table.

        device_info: optional {device: {'mac': ..., 'channel': ..., 'rssi': ...}}, e.g. from a
        throughput test's own per-device MAC/channel/RSSI tracking, to fold into the "MAC",
        "Channel" and "RSSI (dBm)" columns. Falls back to '' for any device/field not present.
        """
        if not self.stats:
            return None

        device_info = device_info or {}
        rows = list(self.stats.values())
        table = {
            'Wireless Client': [row['name'] for row in rows],
            'MAC': [device_info.get(row['device'], {}).get('mac', '') for row in rows],
            'RSSI (dBm)': [device_info.get(row['device'], {}).get('rssi', '') for row in rows],
            'Channel': [device_info.get(row['device'], {}).get('channel', '') for row in rows],
            'Packets Sent': [row['sent'] for row in rows],
            'Packets Received': [row['recv'] for row in rows],
            'Packet Loss %': [row['loss_percent'] for row in rows],
            'AVG RTT (ms)': [row['avg_rtt'] for row in rows],
        }

        return pd.DataFrame(table)

    def add_to_report(self, report, device_info=None, timeline_labels=None):
        """Appends the ping statistics table to the test's own report.

        Safe to call unconditionally, nothing is added when the background ping did not run.
        See to_dataframe() for device_info.
        """
        dataframe = self.to_dataframe(device_info=device_info)
        if dataframe is None:
            return False

        try:
            timeline = self.connectivity_timeline_payload()
            if timeline and hasattr(report, 'build_echarts_chart'):
                timeline.update(timeline_labels or {})
                report.set_obj_html(
                    _obj_title='Client Connectivity Results Throughout the Test Duration',
                    _obj=('The graph illustrates the connectivity status of all wireless clients during the '
                          'test based on connectivity monitoring during the test execution. Green segments '
                          'represent successful responses, while red segments indicate packet loss or '
                          'connectivity drops observed during the test. Clients with no recorded ping '
                          'samples are shown without a status bar.'))
                report.build_objective()
                report.build_echarts_chart(
                    chart_id='background-ping-connectivity-timeline',
                    chart_type='connectivity_timeline',
                    payload=timeline,
                    title='Wireless Client Connectivity Status vs Time')

            report.set_table_title(
                'Ping statistics collected for all wireless clients during the test '
                '(target {}, duration {}, {}s interval)'.format(
                    self.target, self.duration_string(), self.interval))
            report.build_table_title()
            report.set_table_dataframe(dataframe)
            report.build_table()
        except Exception as e:
            logger.warning('Background ping statistics could not be added to the report: %s', e)
            return False

        return True


def add_arguments(parser):
    """Adds the shared background ping arguments to an interop script argument parser."""
    group = parser.add_argument_group('Background ping')
    group.add_argument('--enable_bg_ping', '--bg_ping',
                       action='store_true',
                       help='Run a ping on the real clients in the background while the test runs and report its '
                            'statistics at the end of the report')
    group.add_argument('--bg_ping_target',
                       type=str,
                       default=None,
                       help='IP, domain name or LANforge port the background ping should target. Defaults to the '
                            'upstream port or server IP of the test when not given')
    group.add_argument('--bg_ping_interval',
                       type=float,
                       default=1,
                       help='Packet interval of the background ping in seconds. Defaults to 1')
    group.add_argument('--bg_ping_sample_interval',
                       type=float,
                       default=10,
                       help='How often the background ping endpoints are sampled, in seconds. Defaults to 10')
    return parser


def from_args(args, host, port=8080, device_list=None, default_target=None):
    """Builds and starts a BackgroundPing from parsed arguments.

    Returns None when the background ping was not requested or could not be started, so the
    calling script can keep the return value and call it unconditionally.
    """
    if not (getattr(args, 'enable_bg_ping', False) or getattr(args, 'bg_ping', False)):
        return None

    target = getattr(args, 'bg_ping_target', None) or default_target
    if not target:
        logger.error('--enable_bg_ping was given without --bg_ping_target and the test has no upstream to fall back on, '
                     'skipping the background ping')
        return None

    background_ping = BackgroundPing(host=host,
                                     port=port,
                                     target=target,
                                     interval=getattr(args, 'bg_ping_interval', 1),
                                     device_list=device_list,
                                     sample_interval=getattr(args, 'bg_ping_sample_interval', 10),
                                     debug=getattr(args, 'debug', False))

    if not background_ping.start():
        return None

    return background_ping
