# LANforge Query Metrics Script

## Overview
Script designed to gather LANforge metrics for another test runs, querying once per second for a specified duration. This script supports querying ports, CXs, and LANforge vAP-associated stations.

**This script assumes all specified ports, CXs, and vAPs to query already exist.**

Metrics data is output as CSV. Available data is as follows:
- Port metrics: Data in 'Port Mgr' tab
- CX metrics: Data in 'Layer-3' tab
   - This includes CX endpoint metrics (data in 'L3 Endps' tab)
- vAP-associated station(s) metrics: Data in 'vAP Stations' tab

By default, the script also clears port and CX counters for specified LANforge ports (including vAPs) and CXs. To disable this, specify the `--no_clear_port_counters` and `--no_clear_cx_counters` arguments, respectively. Clearing vAP-associated stations counters is not currently supported.

See the [Example Usage](#example-usage) section below or run the script with the `--help` option for more information. Example CSV output is located in the [`example_csv`](./example_csv/) directory.

## Initial Setup

If you intend to run this script on a LANforge system, no setup should be required. Just make sure to set the `LF_SCRIPTS` environment variable to `/home/lanforge/scripts`.

If you intend to run this script on a non-LANforge system, please follow the instructions in the [LANforge scripts README](https://github.com/greearb/lanforge-scripts/blob/master/py-scripts/README.md). In short, the primary requirements to run LANforge scripts are Python 3.7+, a folder containing the LANforge API library code, and the `pandas` module installed. The easiest way to meet these requirements is to follow the steps in the README.

## Example Usage

### Primary Options
- Specify desired ports using the `--port_eid` argument, once per port to query
- Specify desired CXs using the `--cx_name` argument, once per Layer 3 CX to query
   - Corresponding endpoints are automatically queried when this argument is specified
- Specify desired vAPs using the `--vap_eid` argument, once per vAP to query

### Examples
- Query the 192.168.1.101 LANforge manager for metrics related to the `1.1.wlan0` and `1.1.wlan1` LANforge ports for 30 seconds:
   ```Bash
   LF_SCRIPTS=/home/lanforge/scripts ./query_metrics.py \
      --mgr          192.168.1.101 \
      --duration     30 \
      --port_eid     '1.1.wlan0' \
      --port_eid     '1.1.wlan1'
   ```

- Query the 192.168.1.101 LANforge manager for metrics related to the `1.1.vap0000` and `1.1.vap0001` LANforge vAPs and any associated stations for 30 seconds:
   ```Bash
   LF_SCRIPTS=/home/lanforge/scripts ./query_metrics.py \
      --mgr          192.168.1.101 \
      --duration     30 \
      --vap_eid      '1.1.vap0000' \
      --vap_eid      '1.1.vap0001'
   ```

- Query the 192.168.1.101 LANforge manager for metrics related to the LANforge station `1.1.wlan0` and the LANforge CX named `UDP-test-CX`.
   ```Bash
   LF_SCRIPTS=/home/lanforge/scripts ./query_metrics.py \
      --mgr          192.168.1.101 \
      --port_eid     '1.1.wlan1' \
      --cx_name      'UDP-test-CX'
   ```

- Query the 192.168.1.101 LANforge manager for the specific metrics in the `--cx_fields` argument for the LANforge CX named `UDP-test-CX`. Options `--port_fields`, `--cx_fields`, and `--vap_fields` function similarly.
   ```Bash
   # The queried endpoint fields correspond to columns 'Rx Rate (1m)'
   # and 'Rx Drop %' in the LANforge GUI 'L3 Endps' tab
   LF_SCRIPTS=/home/lanforge/scripts ./query_metrics.py \
      --mgr          192.168.1.101 \
      --cx_name      'UDP-test-CX' \
      --endp_fields  'rx+rate+(1m),rx+drop+%25' # URL encoded
   ```