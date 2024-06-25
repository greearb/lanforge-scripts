# LANforge API Examples

**NOTE:** These examples require the environment variable `LF_SCRIPTS` to exist and point to the LANforge scripts base directory.

For example, to invoke the `query_all_ports.py` script:

```Bash
LF_SCRIPTS=/home/lanforge/scripts ./query_all_ports.py
```

## Example Scripts

| Script                                                 | Purpose                                                           |
| ------------------------------------------------------ | ----------------------------------------------------------------- |
| [`query_all_ports.py`](./query_all_ports.py)           | Query and display basic port data for all ports.                  |
| [`query_json_endpoint.py`](./query_json_endpoint.py)   | Query and display data for arbitrary LANforge API JSON endpoints. |
| [`query_specific_port.py`](./query_specific_port.py)   | Query and display variable data for a specific port.              |
| [`query_vap_stations.py`](./query_all_vap_stations.py) | Query and display stations associated to all LANforge vAPs.       |
| [`visualize_latency.py`](./visualize_latency.py)       | Query and visualize latency for a specific endpoint.              |
