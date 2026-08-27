# LANforge `lf_test_generic.py` Toolbox Mode — CLI Reference & Usage Guide

## 1. Overview
The `--toolbox` mode in [`lf_test_generic.py`](../lf_test_generic.py) provides standalone building-block operations for generic endpoints (ping, iperf3, curl, speedtest) and cross-connections without running full test suites.

### Key Characteristics
- **Modular Lifecycle**: Build, start, stop, and delete generic endpoints/CXs independently.
- **Custom Naming**: Name endpoints and cross-connections via `--endp_names`.
- **Existing Ports**: Attach generic endpoints to existing stations or ethernet ports (`--use_existing_eid`).
- **Scoped `all`**: Actions using `all` apply only to Generic tab items and never affect other test types.

---

## 2. CLI Reference

| Flag / Option | Arguments | Description |
| :--- | :--- | :--- |
| `--toolbox` / `--tool_box` | *None* | Enables toolbox mode and exits immediately after completing requested action(s). |
| `--build` | *None* | Builds stations (if configured), generic endpoints, and cross-connections. |
| `--endp_names` / `--cx_names` | `<name1,name2...>` | Custom name(s) for the generic endpoint(s) and cross-connection(s). |
| `--test_type` | `ping`, `iperf3`, `iperf3-client`, `iperf3-server`, `lfcurl`, `speedtest` | Test type to configure for generic endpoints during build. |
| `--target` | `<hostname/IP/EID>` | Target destination for ping, iperf3, or curl. |
| `--interval` | `<seconds>` | Interval between transmissions (e.g. `0.2`, `0.01`). |
| `--cmd` | `"<custom command>"` | Custom shell command for generic endpoint execution. |
| `--use_existing_eid` | `<eid1,eid2...>` | Attach endpoints to existing ports (e.g. `1.1.sta0000`, `1.1.eth1`). |
| `--radio`, `--num_stations`, `--ssid`, `--passwd`, `--security` | Radio/Wi-Fi parameters | Parameters to auto-create Wi-Fi stations during build. |
| `--port_wait_time` | `<seconds>` | Max timeout in seconds to wait for port actions (appear, up, ip). Default: `60`. |
| `--start_gen_cx` | `<name(s)>` or `all` | Starts specified generic CX(s) or `all` generic CXs on the manager into `RUNNING` state. |
| `--stop_gen_cx` | `<name(s)>` or `all` | Stops specified generic CX(s) or `all` generic CXs on the manager (`STOPPED` state). |
| `--del_gen_cx` | `<name(s)>` or `all` | Deletes specified generic CX(s) & endpoints or `all` generic CXs & endpoints on the manager. |

---

## 3. Usage Guide & Examples

### 1. Build (Create Endpoints & CXs without running traffic)

- **Create new Wi-Fi stations + Ping generic endpoints**:
  ```bash
  python3 py-scripts/lf_test_generic.py --mgr 192.168.244.45 --toolbox --build \
      --test_type ping --target www.google.com \
      --radio wiphy1 --num_stations 2 --ssid TestSSID --passwd 12345678 --security wpa2 \
      --endp_names ping_sta0,ping_sta1
  ```

- **Build on an already-existing station (e.g., sub-second roaming ping)**:
  ```bash
  python3 py-scripts/lf_test_generic.py --mgr 192.168.244.45 --toolbox --build \
      --test_type ping --target 8.8.8.8 --use_existing_eid 1.1.sta0000 \
      --interval 0.01 --endp_names roam_ping_sta0
  ```

- **Build iPerf3 client endpoint**:
  ```bash
  python3 py-scripts/lf_test_generic.py --mgr 192.168.244.45 --toolbox --build \
      --test_type iperf3-client --target 192.168.1.100 --client_port 5201 \
      --use_existing_eid 1.1.sta0000 --endp_names iperf_client0
  ```

---

### 2. Start Generic Cross-Connections (`--start_gen_cx`)

- **Start specific CX**:
  ```bash
  python3 py-scripts/lf_test_generic.py --mgr 192.168.244.45 --toolbox --start_gen_cx ping_sta0
  ```

- **Start multiple CXs**:
  ```bash
  python3 py-scripts/lf_test_generic.py --mgr 192.168.244.45 --toolbox --start_gen_cx ping_sta0,ping_sta1
  ```

- **Start all generic CXs**:
  ```bash
  python3 py-scripts/lf_test_generic.py --mgr 192.168.244.45 --toolbox --start_gen_cx all
  ```

---

### 3. Stop Generic Cross-Connections (`--stop_gen_cx`)

- **Stop specific CX**:
  ```bash
  python3 py-scripts/lf_test_generic.py --mgr 192.168.244.45 --toolbox --stop_gen_cx ping_sta0
  ```

- **Stop all generic CXs**:
  ```bash
  python3 py-scripts/lf_test_generic.py --mgr 192.168.244.45 --toolbox --stop_gen_cx all
  ```

---

### 4. Delete Generic Cross-Connections & Endpoints (`--del_gen_cx`)

- **Delete specific CX and its endpoint**:
  ```bash
  python3 py-scripts/lf_test_generic.py --mgr 192.168.244.45 --toolbox --del_gen_cx ping_sta0
  ```

- **Delete all generic CXs and generic endpoints**:
  ```bash
  python3 py-scripts/lf_test_generic.py --mgr 192.168.244.45 --toolbox --del_gen_cx all
  ```

---

### 5. Chained Workflow (Build and Start in one line)

- **Build stations/endpoints and start traffic immediately**:
  ```bash
  python3 py-scripts/lf_test_generic.py --mgr 192.168.244.45 --toolbox --build \
      --test_type ping --target www.google.com \
      --radio wiphy1 --num_stations 2 --ssid TestSSID --passwd 12345678 --security wpa2 \
      --endp_names ping_sta0,ping_sta1 --start_gen_cx all
  ```
