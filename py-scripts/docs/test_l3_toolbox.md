# LANforge `test_l3.py` Toolbox Mode — CLI Reference & Usage Guide

## 1. Overview
The `--toolbox` mode in [`test_l3.py`](../test_l3.py) provides standalone building-block operations for station management, Layer-3 cross-connections, and port administration without running full test loops.

### Key Characteristics
- **Modular Actions**: Create stations, build cross-connections, toggle port states, and clean up.
- **Custom CX Naming**: Assign custom names to cross-connections via `--cx_names`.
- **Admin State Control**: Set ports Admin UP or DOWN (`--ports_up`, `--ports_down`).
- **Collision Avoidance**: Auto-detects existing stations and adjusts offsets to avoid conflicts.
- **Selective / Bulk Control**: Target specific items by name or apply across `all`.
- **Automation Ready**: Returns `0` on success and `1` on error.

---

## 2. Command Line Arguments Reference

| Flag / Option | Arguments | Description |
| :--- | :--- | :--- |
| `--toolbox` / `--tool_box` | *None* | Enables standalone toolbox mode and exits upon action completion. |
| `--create_station` | *None* | Action: Creates Wi-Fi stations using specified `--radio` configuration. |
| `--radio` | `"radio==<r> stations==<n> ssid==<s> ..."` | Configuration key-value string for station creation (e.g. `radio==wiphy0 stations==2 ssid==TestAP security==wpa2`). |
| `--ports` / `--downstream_ports` | `<eid1,eid2...>` | Specifies target/downstream port EIDs or aliases (e.g. `1.1.eth2`, `sta0000`). |
| `--upstream_port` | `<eid>` | Specifies the upstream port EID for cross-connection building (e.g. `1.1.eth1`). |
| `--cx_names` / `--cx_name` | `<name1,name2...>` | Custom cross-connection name or prefix (e.g. `wlan0`, `toolbox`). |
| `--build_cxs` / `--build_cx` | *None* | Action: Builds Layer-3 cross-connections between `--upstream_port` and `--ports`. |
| `--start_cx` | `<name>` or `all` | Action: Starts specified cross-connection(s) or `all` existing cross-connections. |
| `--stop_cx` | `<name>` or `all` | Action: Stops specified cross-connection(s) or `all` existing cross-connections. |
| `--del_cx` | `<name>` or `all` | Action: Deletes specified cross-connection(s) or `all` existing cross-connections. |
| `--del_stations` | `<name>` or `all` | Action: Deletes specified station ports (e.g. `sta5000`) or `all` station ports. |
| `--ports_up` | `<name>` or `all` | Action: Sets specified ports or `all` station ports Admin UP. |
| `--ports_down` | `<name>` or `all` | Action: Sets specified ports or `all` station ports Admin DOWN. |

---

## 3. Usage Guide & CLI Examples

### 1. Create Wi-Fi Stations
Creates 2 stations on radio `wiphy0` with WPA2 security:
```bash
python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox \
  --create_station --radio "radio==wiphy0 stations==2 ssid==TestAP ssid_pw==12345678 security==wpa2"
```

### 2. Build Layer-3 Cross-Connections
- **Build with Default Names** (between upstream `1.1.eth1` and station ports `1.1.sta5000,1.1.sta5001`):
  ```bash
  python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox \
    --build_cxs --upstream_port 1.1.eth1 --ports 1.1.sta5000,1.1.sta5001
  ```

- **Build with Custom CX Name (`--cx_names`)**:
  ```bash
  python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox \
    --build_cxs --upstream_port 1.1.eth1 --ports 1.1.sta0000 --cx_names toolbox
  ```

- **Build Ethernet/VLAN Cross-Connections (`--downstream_ports`)**:
  ```bash
  python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox \
    --build_cxs --upstream_port 1.1.eth1 --downstream_ports 1.1.eth2 --cx_names eth_link
  ```

### 3. Start Cross-Connections (`--start_cx`)
- **Start specific CX by name**:
  ```bash
  python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox --start_cx toolbox
  ```
- **Start all CXs**:
  ```bash
  python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox --start_cx all
  ```

### 4. Stop Cross-Connections (`--stop_cx`)
- **Stop specific CX by name**:
  ```bash
  python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox --stop_cx toolbox
  ```
- **Stop all CXs**:
  ```bash
  python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox --stop_cx all
  ```

### 5. Set Port Admin State (`--ports_down` & `--ports_up`)
- **Set Admin DOWN**:
  ```bash
  python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox --ports_down 1.1.sta5000,1.1.eth2
  ```
- **Set Admin UP**:
  ```bash
  python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox --ports_up 1.1.sta5000,1.1.eth2
  ```

### 6. Delete Cross-Connections & Stations
- **Delete specific CX by name**:
  ```bash
  python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox --del_cx toolbox
  ```
- **Delete all CXs**:
  ```bash
  python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox --del_cx all
  ```
- **Delete specific stations**:
  ```bash
  python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox --del_stations sta5000,sta5001
  ```
- **Delete all station ports**:
  ```bash
  python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox --del_stations all
  ```

---

### 7. Chained Workflows

- **Create Stations + Build CXs in Single Execution**:
  ```bash
  python3 py-scripts/test_l3.py --lfmgr 192.168.244.45 --toolbox \
    --create_station --radio "radio==wiphy0 stations==2 ssid==TestAP ssid_pw==12345678 security==wpa2" \
    --build_cxs --upstream_port 1.1.eth1 --cx_names test_flow
  ```
