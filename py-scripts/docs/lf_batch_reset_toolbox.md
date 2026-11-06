# LANforge `lf_batch_reset.py` Toolbox Mode — CLI Reference & Usage Guide

## 1. Overview
The `--toolbox` mode in [`lf_batch_reset.py`](../lf_batch_reset.py) provides standalone building-block operations for the batch-reset client-cycling test (create stations, build cross-connects, reset a batch, start/stop traffic, verify rate limits, admin up/down, delete, cleanup) without running the full timed test. No report or CSV is written in toolbox mode.

### Key Characteristics
- **Fixed Lifecycle Order**: One flag or several in one command always run in this order, regardless of the order typed: `create_stations → build_cross_connects → reset_batch → admin_up → start_traffic → verify_rate_limit → stop_traffic → admin_down → del_cxs → del_stations → cleanup`.
- **Station Set**: `--radio` builds new station names (only `--create_stations` needs it); `--use_existing_eid` acts on exactly those ports; neither discovers every station already on LANforge (`--mgr`) - manager-wide, not scoped to this script's own naming.
- **Selector (`SEL`)**: `all` (default) | `batchN` (1-based) | a comma list of station names/EIDs (`--del_cxs` also takes full cx names).
- **Per-Radio RADIUS Logins**: `--radio` can carry its own `eap_identity==`/`eap_password==`/`rate_limit_dl==`/`rate_limit_ul==` and a `batch==<label>`, for radios that each use a different RADIUS login with a different assigned cap.
- **Batch Labels Persist**: Once created with `batch==<label>`, the batch layout is read straight back off the station names (`B<label>_staXXXX`) on any later command - no `--radio` needed, and `--num_batches` is ignored.
- **Scoped `all` exception**: `--del_cxs` / `--del_stations`' `'all'` reaches every cross-connect/station on `--mgr`, not just this test's own - unlike every other `SEL` action.

---

## 2. CLI Reference

| Flag / Option | Arguments | Description |
| :--- | :--- | :--- |
| `--toolbox` / `--tool_box` | *None* | Enables toolbox mode and exits immediately after completing requested action(s). |
| `--radio` / `-r` | `"radio==<eid> stations==<N> [ssid==.. ssid_pw==.. security==.. eap_identity==.. eap_password==.. rate_limit_dl==.. rate_limit_ul==.. batch==..]"` | Radio spec, repeatable. Fields left out fall back to the matching global flag. `batch==<label>` groups radios sharing a label into one batch. Only `--create_stations` needs it. |
| `--num_stations` | `<N>` | Station count for a single bare `--radio` with no `stations==` (default 50). |
| `--num_batches` | `<B>` | Split the station set into `B` contiguous batches (default 5); ignored once any `--radio` sets `batch==`. |
| `--use_existing_eid` / `--use_existing_eids` | `<eid1,eid2...>` | Act on exactly these ports (e.g. `1.1.sta0000,1.1.sta0001`); each port's parent radio is read back from LANforge. |
| `--create_stations` / `--create_station` | *None* | Creates the stations on `--radio` (pre-cleans every station/cx/endpoint on the manager first unless `--no_pre_cleanup`). Rejects `--use_existing_eid`. |
| `--build_cross_connects` / `--build_cx` | *None* | Creates the Layer-3 cross-connects between the stations and `--upstream_port`. |
| `--reset_batch` | `<N>` or `batchN` | One reset of batch `N`: stop traffic, randomize MAC, reconnect to `--ssid`/`--ssid_list`, re-auth. Leaves traffic stopped; does not loop or verify. |
| `--admin_up` | `<SEL>` or `all` | Sets the matching station ports admin UP. |
| `--start_traffic` | `<SEL>` or `all` | Sets the matching stations' cross-connects to `RUNNING`. |
| `--verify_rate_limit` | `<SEL>` or `all` | Measures per-station DL/UL throughput and grades it against `--rate_limit_dl` / `--rate_limit_ul` (or a station's own per-radio override), within `--rate_limit_tolerance_percent` (default 5). |
| `--stop_traffic` | `<SEL>` or `all` | Sets the matching stations' cross-connects to `STOPPED`. |
| `--admin_down` | `<SEL>` or `all` | Sets the matching station ports admin DOWN. |
| `--del_cxs` / `--del_cx` / `--delete_cross_connections` | `<SEL>` or `all` | Stops and removes cross-connects for `batchN` / a comma list (found by live discovery), or every cross-connect on `--mgr` for `all`. |
| `--del_stations` / `--del_station` / `--delete_stations` | `<SEL>` or `all` | Admin-downs and removes the matching station ports; `all` reaches every station on `--mgr`. |
| `--cleanup` | *None* | Removes every cross-connect, L3 endpoint, and station on `--mgr` (manager-wide). |

---

## 3. Usage Guide & Examples

### 1. Create Stations & Cross-Connects

- **Create the 802.1X EAP stations**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --create_stations \
      --radio "radio==1.1.wiphy0 stations==50" --num_batches 5 \
      --ssid ENT-A --eap_identity user --eap_password secret
  ```

- **WPA2-PSK instead of EAP**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --create_stations \
      --radio "radio==1.1.wiphy0 stations==50" --num_batches 5 \
      --eap NONE --ssid PSK-A --ssid_pw secret123
  ```

- **Build the cross-connects to the upstream port**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --build_cross_connects \
      --upstream_port 1.1.eth2
  ```

- **Build cross-connects on an explicit port list**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --build_cross_connects \
      --upstream_port 1.1.eth2 --use_existing_eid 1.1.sta0000,1.1.sta0001
  ```

---

### 2. Reset a Batch (`--reset_batch`)

`--reset_batch` only resets. Resume and grade it with `--start_traffic` / `--verify_rate_limit` in the same command (they run after the reset).

- **Reset batch 2 onto ENT-B**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --reset_batch 2 --num_batches 5 \
      --ssid ENT-B --eap_identity user --eap_password secret
  ```

- **Reset batch 2, resume its traffic, then check its rate limit — each once, in lifecycle order**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --num_batches 5 \
      --reset_batch 2 --start_traffic batch2 --verify_rate_limit batch2 \
      --ssid ENT-B --eap_identity user --eap_password secret \
      --rate_limit_dl 20Mbps --rate_limit_ul 10Mbps
  ```

---

### 3. Traffic & Admin State

- **Admin up / start / stop all**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --admin_up all
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --start_traffic all
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --stop_traffic all
  ```

- **Act on one batch or a specific station list**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --num_batches 5 --start_traffic batch1
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --start_traffic sta0000,sta0001
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --num_batches 5 --admin_down batch3
  ```

---

### 4. Verify Rate Limits (`--verify_rate_limit`)

- **All stations, DL + UL caps**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --verify_rate_limit all \
      --rate_limit_dl 20Mbps --rate_limit_ul 10Mbps
  ```

- **One batch, tighter grade: 20 samples over 40s, 3% headroom**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --num_batches 5 \
      --verify_rate_limit batch2 --rate_limit_dl 20Mbps \
      --rate_limit_window 40s --polling_interval 2s --rate_limit_tolerance_percent 3
  ```

---

### 5. Delete & Cleanup

- **Delete cross-connects / stations, scoped or manager-wide**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --num_batches 5 --del_cxs batch1
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --del_stations sta0000,sta0001
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --del_stations all
  ```

- **Full manager-wide cleanup**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --cleanup
  ```

---

### 6. Chained Workflow (Build and Start in one line)

- **Create → build CXs → start traffic in one command**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox \
      --create_stations --build_cross_connects --start_traffic all \
      --radio "radio==1.1.wiphy0 stations==50" --num_batches 5 --upstream_port 1.1.eth2 \
      --ssid ENT-A --eap_identity user --eap_password secret
  ```

- **Tear it all down**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox \
      --stop_traffic all --del_cxs all --del_stations all
  ```

---

### 7. Per-Radio RADIUS Logins, Caps, and `batch==` Grouping

- **500 clients, 5 radios, 5 different RADIUS logins each with its own RADIUS-assigned cap**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --create_stations --ssid ENT-A \
      --radio "radio==1.1.wiphy0 stations==100 batch==1 eap_identity==user1 eap_password==pass rate_limit_dl==30M rate_limit_ul==20M" \
      --radio "radio==1.1.wiphy1 stations==100 batch==2 eap_identity==user2 eap_password==pass rate_limit_dl==50M rate_limit_ul==60M" \
      --radio "radio==1.1.wiphy2 stations==100 batch==3 eap_identity==user3 eap_password==pass rate_limit_dl==10M rate_limit_ul==50M" \
      --radio "radio==1.1.wiphy3 stations==100 batch==4 eap_identity==user4 eap_password==pass rate_limit_dl==50M rate_limit_ul==10M" \
      --radio "radio==1.1.wiphy4 stations==100 batch==5 eap_identity==user5 eap_password==pass rate_limit_dl==88M rate_limit_ul==66M"
  ```

- **Batch layout persists - no `--radio` needed on a later, separate command**:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --build_cross_connects --upstream_port 1.1.eth2
  ```

- **`--reset_batch` / `--verify_rate_limit` still need the same `--radio` repeated**, since `eap_identity==`/`rate_limit_dl==` are not stored on LANforge:
  ```bash
  python3 py-scripts/lf_batch_reset.py --mgr 192.168.244.45 --toolbox --reset_batch 2 --ssid ENT-B \
      --radio "radio==1.1.wiphy1 stations==100 batch==2 eap_identity==user2 eap_password==pass rate_limit_dl==50M rate_limit_ul==60M"
  ```
