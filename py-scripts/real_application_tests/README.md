# flake8: noqa
# Zoom, YouTube Video Streaming, and Real Browser Automation

## Objective
This project aims to automate Zoom call tests, YouTube video streaming tests, and Real Browser tests across multiple laptops, collect network performance statistics, and store the data in a CSV file. Additionally, automated graphs will be generated using the collected data.

## Hardware Requirements

| Device         | Supported Version         |
|---------------|--------------------------|
| LANforge Unit | f36                      |
| Linux Laptop  | Ubuntu 20.04.6 and above |
| Windows Laptop | Windows 10 and above    |
| MacBook       | v12.7.4 and above        |


---

# Zoom Call Automation Test

## Overview of Scripts

| Script                 | Description |
|------------------------|-------------|
| `gen_cxprofile.py`     | Base file for creating and managing generic cross-connections. |
| `install_dependencies.py` | Installs Python dependencies required for the Real Application Tests. |
| `DeviceConfig.py`      | Configures devices to a specific SSID. |
| `lf_interop_zoom.py`   | Main script for handling generic cross-connections, monitoring tests, generating reports, and creating a Flask server. |
| `zoom_host.py`         | Python Selenium script that launches a browser and creates a Zoom meeting. |
| `zoom_client.py`       | Python Selenium script that joins the Zoom meeting created by the host. |
| `ctzoom.bash`          | Bash script for pre-cleanup, post-cleanup, and triggering Zoom scripts on Linux and macOS. |

## Script Files and Their Placement

| Device          | Path                                      | Files |
|---------------|--------------------------------|-------|
| Lanforge       | `/home/lanforge/lanforge-scripts/py-json` | `gen_cxprofile.py` |
| Lanforge       | `/home/lanforge/lanforge-scripts/py-scripts/` | `install_dependencies.py`, `lf_interop_zoom.py`, `DeviceConfig.py` |
| Windows        | `C:\Program Files (x86)\LANforge-Server` | `install_dependencies.py`, `zoom_host.py`, `zoom_client.py` |
| Linux         | `/home/lanforge` | `install_dependencies.py`, `zoom_host.py`, `zoom_client.py`, `ctzoom.bash` |
| MacOS         | `/Users/lanforge` | `install_dependencies.py`, `zoom_host.py`, `zoom_client.py`, `ctzoom.bash` |

## Prerequisites
- Cluster all laptops to LANforge.
- Ensure real clients access the internet only via the wireless interface by disabling the Ethernet interface.
- Ensure files are placed in the respective paths as per the table above.
- Install Python (>=3.9.x) and Selenium (>4.17.x).
- Disable public and private firewalls on Windows laptops.
- Install the necessary dependencies before running the tests using install_dependencies.py file.

## Additional Packages for Linux Laptops

**Linux Devices:**
```bash
sudo apt install xclip
sudo apt install python3-tk python3-dev
```


## Running the Zoom Automation Test
Navigate to `/home/lanforge/lanforge-scripts/py-scripts/real_application_tests` and execute the script:

```bash
python3 lf_interop_zoom.py --duration 1 --lanforge_ip "192.168.214.219" --sigin_email "demo@gmail.com" --sigin_passwd "Demo@123" --participants 3 --audio --video --resources 1.400,1.200 --zoom_host 1.95 --server_ip 192.168.214.123
```

---

# YouTube Video Streaming Test

## Overview of Scripts

| Script              | Description |
|---------------------|-------------|
| `lf_interop_youtube.py` | Main script for creating cross-connections, monitoring the test, generating reports, and creating a Flask server. |
| `youtube.py`       | Selenium script that launches a browser, opens a YouTube video, sets resolution, and opens 'Stats for Nerds'. |
| `youtube_stream.bat` | Windows batch script for pre-cleanup, post-cleanup, and triggering `youtube.py`. |
| `ctyt.bash`       | Linux/macOS script for pre-cleanup, post-cleanup, and triggering `youtube.py`. |

## Script Files and Their Placement

| Device          | Path                                      | Files |
|---------------|--------------------------------|-------|
| Lanforge       | `/home/lanforge/lanforge-scripts/py-scripts/` | `lf_interop_youtube.py` |
| Windows        | `C:\Program Files (x86)\LANforge-Server` | `youtube.py`, `youtube_stream.bat` |
| Linux         | `/home/lanforge` | `youtube.py`, `ctyt.bash` |
| MacOS         | `/Users/lanforge` | `youtube.py`, `ctyt.bash` |

## Running the YouTube Streaming Test
Navigate to `/home/lanforge/lanforge-scripts/py-scripts/real_application_tests` and execute the script:

```bash
python3 lf_interop_youtube.py --mgr 192.168.214.219 --url "https://youtu.be/-SQop2bI8Eg" --duration 2 --res 1080p --flask_ip 192.168.214.131
```

---

# Real Browser Test

## Overview of Scripts

| Script              | Description |
|---------------------|-------------|
| `lf_interop_real_browser_test.py` | Main script for creating cross-connections, monitoring the test, generating reports, and creating a Flask server. |
| `real_browser.py`  | Python Selenium script for opening a browser and reloading a test URL. |
| `real_browser.bat` | Windows batch script for pre-cleanup, post-cleanup, and triggering `real_browser.py`. |
| `ctrb.bash`       | Linux/macOS script for pre-cleanup, post-cleanup, and triggering `real_browser.py`. |

## Running the Real Browser Test
Navigate to `/home/lanforge/lanforge-scripts/py-scripts/real_application_tests` and execute the script:
```bash
python3 lf_interop_real_browser_test.py --mgr 192.168.214.219 --url "https://mi.com" --duration 1m --debug --flask_ip 192.168.214.131 --server_ip 192.168.214.219 --device_list 1.23,1.95,1.375 --postcleanup
```

---


## Notes:
- **Please run the `install_dependencies.py` file on both the client side and the LANforge side before executing any tests.**

