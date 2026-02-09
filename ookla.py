#!/usr/bin/env python3
import time, csv, tempfile, argparse, subprocess, concurrent.futures, re, os
from pathlib import Path

import os,json
try:
    import requests
except Exception:
    requests = None


UI_XML_NAME = "speedtest_view.xml"


# Here serial will be in the form of 1.3.RZ8RB24HXNE instead of RZ8RB24HXNE Since ADB helpers only work with serials like RZ8RB24HXNE
# ----------------- ADB helpers -----------------
def adb_shell(serial, *args):
    return subprocess.run(["adb","-s",serial,"shell",*args],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def adb_run(serial, *args):
    return subprocess.run(["adb","-s",serial,"shell",*args])

def adb_pull(serial, remote_path, local_path):
    return subprocess.run(["adb","-s",serial,"pull",remote_path,local_path],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def dump_ui(serial, remote_xml):
    out = adb_shell(serial, "uiautomator", "dump", "--compressed", remote_xml)
    if out.stderr.strip():
        print(f"[{serial}] uiautomator dump stderr: {out.stderr.strip()}")


# ----------------- Parsing helpers -----------------
def parse_visible_tokens_and_nodes(xml_text):
    tokens, nodes = [], []
    for m in re.finditer(r'<node[^>]+>', xml_text):
        node = m.group(0)
        txt  = re.search(r'text="([^"]*)"', node)
        desc = re.search(r'content-desc="([^"]*)"', node)
        b    = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        val  = (txt.group(1) if txt and txt.group(1).strip()
                else desc.group(1) if desc and desc.group(1).strip()
                else "")
        if val:
            clean = (val.replace("\u202f"," ").replace("\xa0"," ").replace(",",".").strip())
            tokens.append(clean)
            nodes.append({"text": clean, "bounds": tuple(map(int, b.groups())) if b else None})
    return tokens, nodes

def parse_speedtest_from_xml(xml_text):
    tokens, _ = parse_visible_tokens_and_nodes(xml_text)

    mbps_pat = re.compile(r'(\d+(?:\.\d+)?)\s*(?:Mbps|Mb/s|megabits?\s+per\s+second)', re.I)
    ms_pat   = re.compile(r'(\d+(?:\.\d+)?)\s*(?:ms|milliseconds)', re.I)

    def pick(pat, s):
        m = pat.search(s)
        return m.group(1) if m else None

    def pick_all(pat, s):
        return pat.findall(s)

    dl = ul = ping = idle = dlat = ulat = None

    for t in tokens:
        low = t.lower()

        if dl is None and ("download speed" in low or low.startswith("download")):
            v = pick(mbps_pat, t);  dl = v or dl
        if ul is None and ("upload speed" in low or low.startswith("upload")):
            v = pick(mbps_pat, t);  ul = v or ul

        # Latencies (worded as "ping result ..." or classic labels)
        # if idle is None and "idle ping result" in low:
        #     idle = pick(ms_pat, t)
        # if dlat is None and "download ping result" in low:
        #     dlat = pick(ms_pat, t)
        # if ulat is None and "upload ping result" in low:
        #     ulat = pick(ms_pat, t)

        if "idle ping result" in low and "download ping result" in low and "upload ping result" in low:
            ms = pick_all(ms_pat, t)
            if len(ms) >= 3:
                idle = ms[0]
                dlat = ms[1]
                ulat = ms[2]
                continue

        # if "idle ping result" in low and idle is None:
        #     ms = pick_all(ms_pat, t)
        #     if ms: idle = ms[0]

        # if "download ping result" in low and dlat is None:
        #     ms = pick_all(ms_pat, t)
        #     if ms: dlat = ms[1] if len(ms) > 1 else ms[0]

        # if "upload ping result" in low and ulat is None:
        #     ms = pick_all(ms_pat, t)
        #     if ms: ulat = ms[2] if len(ms) > 2 else ms[0]

        if ping is None and ("ping" in low and "result" not in low):
            ping = pick(ms_pat, t)
        if idle is None and "idle latency" in low:
            idle = pick(ms_pat, t)
        if dlat is None and "download latency" in low:
            dlat = pick(ms_pat, t)
        if ulat is None and "upload latency" in low:
            ulat = pick(ms_pat, t)

    # Fallbacks: first two Mbps anywhere
    if dl is None or ul is None:
        mb = []
        for t in tokens:
            v = pick(mbps_pat, t)
            if v: mb.append(v)
        if dl is None and len(mb) >= 1: dl = mb[0]
        if ul is None and len(mb) >= 2: ul = mb[1]

    # If ping missing, use idle (Speedtest usually equates ping to idle latency)
    if ping is None and idle is not None:
        ping = idle

    def clean(v):
        return (v.strip() if v and re.match(r'^\d+(?:\.\d+)?$', v.strip()) else None)

    return {
        "download_mbps":       clean(dl),
        "upload_mbps":         clean(ul),
        "ping_ms":             clean(ping),
        "idle_ms":             clean(idle),
        "download_latency_ms": clean(dlat),
        "upload_latency_ms":   clean(ulat),
    }

# ----------------- Android runner -----------------
class SpeedtestAdb:
    def __init__(self):
        self.WAIT_DURATION = 50
        self.REMOTE_XML = f"/sdcard/{UI_XML_NAME}"
        self.PACKAGE_NAME = "org.zwanoo.android.speedtest"

    def get_connected_devices(self):
        out = subprocess.run(["adb","devices"], capture_output=True, text=True).stdout
        lines = out.strip().split("\n")[1:]
        return [l.split()[0] for l in lines if "device" in l and "unauthorized" not in l]

    def launch_speedtest_app(self, serial):
        print(f"[{serial}] Launching Speedtest app...")
        #  adb -s J0AA002436J82910421 shell monkey -p org.zwanoo.android.speedtest -c android.intent.category.LAUNCHER 1
        adb_run(serial, "monkey", "-p", self.PACKAGE_NAME, "-c", "android.intent.category.LAUNCHER", "1")

        time.sleep(10)

    def tap_go_button(self, serial):
        try:
            size = adb_shell(serial, "wm", "size").stdout
            m = re.search(r'(\d+)\s*x\s*(\d+)', size)
            w, h = map(int, m.groups())

            # Tap coordinates based on screen size
            taps = [
                (int(w * 0.50), int(h * 0.42)),
                (int(w * 0.52), int(h * 0.44)),
                (int(w * 0.48), int(h * 0.40)),
                (350),(650),
                (650,)(350),
            ]
        except (ValueError, AttributeError, Exception):
            # Fallback tap coordinates (hardcoded)
            taps = [(530, 930), (360, 610), (540, 900), (580, 1000),\
                    (610,360), (360, 610), (370, 675)] # Tab Go button

        # Execute tap attempts
        for x, y in taps:
            adb_run(serial, "input", "tap", str(x), str(y))
            time.sleep(0.8)


    def stop_speedtest_app(self, serial):
        print(f"[{serial}] Stopping Speedtest app?")
        adb_run(serial, "am", "force-stop", self.PACKAGE_NAME)

    def dump_and_parse_results(self, serial, retries=6, delay=4):
        # local_dir = Path("adb_results")
        # local_dir.mkdir(exist_ok=True) 
        local_xml = Path(f"{serial}_{UI_XML_NAME}")
        tokens = None
        for attempt in range(1, retries+1):
            dump_ui(serial, self.REMOTE_XML)
            adb_pull(serial, self.REMOTE_XML, str(local_xml))

            if local_xml.exists() and local_xml.stat().st_size > 0:
                xml_text = local_xml.read_text(encoding="utf-8", errors="ignore")
                if attempt == 1:
                    tokens, _ = parse_visible_tokens_and_nodes(xml_text)
                    print(f"[{serial}] Preview tokens (attempt {attempt}):\n" + "\n".join(tokens[:40]) + "\n")
                res = parse_speedtest_from_xml(xml_text)

                # ? Accept as soon as download & upload are present
                if res.get("download_mbps") and res.get("upload_mbps"):
                    if res.get("ping_ms") is None and res.get("idle_ms"):
                        res["ping_ms"] = res["idle_ms"]
                    return res

            print(f"[{serial}] Results not ready (try {attempt}/{retries})?")
            print(tokens[:40] if tokens else "No tokens yet")
            time.sleep(delay)
        return None

    def run_speedtest_on_device(self, serial, ip, post_url):
        # reduce animations to help dumps
        for k in ("window_animation_scale","transition_animation_scale","animator_duration_scale"):
            adb_run(serial, "settings", "put", "global", k, "0")

        self.stop_speedtest_app(serial)
        # try:
        #     print(f"[{serial}] Removing old {UI_XML_NAME} if any")
        #     print(os.path.abspath(f"{serial}_{UI_XML_NAME}"))
        #     os.remove(f"{serial}_{UI_XML_NAME}")
        # except Exception:
        #     try:
        #         Path(f"{serial}_{UI_XML_NAME}").unlink(missing_ok=True)
        #     except Exception:
        #         pass
        #     try:
        #         Path(f"{serial}_{UI_XML_NAME}").unlink()
        #     except Exception:
        #         pass

        # Waiting a bit before launching app
        self.launch_speedtest_app(serial)
        self.tap_go_button(serial)

        time.sleep(self.WAIT_DURATION)

        print(f"[{serial}] Reading results from UI")
        results = self.dump_and_parse_results(serial)

        if not (results and results.get("download_mbps") and results.get("upload_mbps")):
            results = self.dump_and_parse_results(serial)
            print(f"[{serial}] Falling back to Share Clipboard parse ")
            print(f"[{serial}] Reading results from UI")


        if not results:
            print(f"[{serial}] Could not parse results.")
            return None

        d  = results.get("download_mbps") or "0.00"
        u  = results.get("upload_mbps")   or "0.00"
        p  = results.get("ping_ms")       or "0.00"
        il = results.get("idle_ms")       or "N/A"
        dl = results.get("download_latency_ms") or "N/A"
        ul = results.get("upload_latency_ms")   or "N/A"

        # Print exactly like desktop
        print(f" Download Speed     : {d} Mbps")
        print(f" Upload Speed       : {u} Mbps")
        print(f" Idle Latency       : {il} ms")
        print(f" Download Latency   : {dl} ms")
        print(f" Upload Latency     : {ul} ms")

        self.stop_speedtest_app(serial)
        # results_dir = Path("adb_results")
        # results_dir.mkdir(exist_ok=True)

        #TODO if no IP is passed, we should use serial in filename instead of ip
        # out = Path(f"{ip.replace('.', '_')}_speedtest.txt")

        # if out.exists():
        #     print(f"[{ip.replace('.', '_')}] Overwriting previous {out}")
        #     try:
        #         os.remove(out)
        #     except Exception:
        #         pass

        # out.write_text(
        #     f"Upload speed       : {u} Mbps\n"
        #     f"Download speed     : {d} Mbps\n"
        #     f"Idle Latency       : {il} ms\n"
        #     f"Download Latency   : {dl} ms\n"
        #     f"Upload Latency     : {ul} ms\n", encoding="utf-8"
        # )

        payload = {
            "ip": ip,
            "hostname": None,
            "serial": serial,
            "device_id": None,
            "download_mbps": d,
            "upload_mbps":   u,
            "idle_ms":       il,
            "download_latency_ms": dl,
            "upload_latency_ms":   ul,
        }
        maybe_post(post_url, payload)
        return {"serial": serial, "download": d, "upload": u, "ping": p,
                "idle": il, "dlat": dl, "ulat": ul}

# ----------------- Desktop Selenium -----------------
def speed_test_by_ookla():
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    chrome_options = Options()
    prefs = {"profile.managed_default_content_settings.notifications":1,
            "profile.managed_default_content_settings.geolocation":1,
            "profile.managed_default_content_settings.media_stream":1}
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--new-window")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")

    user_data_dir = tempfile.mkdtemp(); chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.speedtest.net/")

    try:
        consent = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        ); consent.click()
    except Exception: pass

    go_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CLASS_NAME, "start-text")))
    go_button.click()
    time.sleep(40)

    download_speed = driver.find_element(By.CLASS_NAME, "download-speed").text
    upload_speed   = driver.find_element(By.CLASS_NAME, "upload-speed").text
    idle_latency   = driver.find_element(By.XPATH, "//span[@title='Idle Latency']").text
    download_latency = driver.find_element(By.XPATH, "//span[@title='Download Latency']").text
    upload_latency   = driver.find_element(By.XPATH, "//span[@title='Upload Latency']").text

    print(" Download Speed     :", download_speed, "Mbps")
    print(" Upload Speed       :", upload_speed, "Mbps")
    print(" Idle Latency       :", idle_latency, "ms")
    print(" Download Latency   :", download_latency, "ms")
    print(" Upload Latency     :", upload_latency, "ms")
    driver.quit()

    print('REMOVING TEMP USER DATA DIR')
    return download_speed, upload_speed, idle_latency, download_latency, upload_latency

# ----------------- speedtest-cli -----------------
def speed_test_using_cli():
    try:
        result = subprocess.run(["speedtest-cli","--csv"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        fields = list(csv.reader([result.stdout.strip()]))[0]
        d = float(fields[5]) / 1_000_000 if fields[5] else 0.0
        u = float(fields[6]) / 1_000_000 if fields[6] else 0.0
        p = float(fields[7]) if fields[7] else 0.0
        print(f"\nDownload: {d:.2f} Mbps"); print(f"Upload  : {u:.2f} Mbps"); print(f"Ping    : {p:.2f} ms")
        return f"{d:.2f}", f"{u:.2f}", f"{p:.2f}"
    except subprocess.CalledProcessError as e:
        print("Error running speedtest-cli:", e.stderr); return "0.00","0.00","0.00"

# ----------------- main -----------------
def parse_args():
    p = argparse.ArgumentParser(description='Speed Test')
    p.add_argument('--type', choices=['cli','ookla','adb'], default='ookla')
    p.add_argument('--adb_devices', help='Comma-separated ADB serials (default: all connected)')
    p.add_argument('--ip', help='IP address (for adb)')
    p.add_argument('--post_url', help='Optional: POST results JSON to this URL')
    return p.parse_args()

def maybe_post(post_url, payload):
    if not post_url:
        return
    if requests is None:
        print("[WARN] requests not available; skipping POST")
        return
    try:
        r = requests.post(post_url, json=payload, timeout=5)
        print('-----------------------------------[POST]------------------------------------')
        print('[POST] Sending payload to POST URL:', post_url)
        print(payload)
        print(f"[STATUS CODE] {r.status_code}")
        print('-----------------------------------------------------------------------')

    except Exception as e:
        print(f"[POST] failed: {e}")

def main():
    args = parse_args()
    if args.type != 'adb':
        if args.type == 'ookla':
            download, upload, idle, dlat, ulat = speed_test_by_ookla()
        else:
            download, upload, ping = speed_test_using_cli(); idle = dlat = ulat = "N/A"
        out = Path("speedtest.txt")
        if out.exists():
            try:
                print('REMOVING OLD FILES')
                out.unlink()
            except Exception:
                pass
            try:
                os.remove(out)
            except Exception:
                pass
            print('REMOVED OLD FILES')
        time.sleep(1)
        # out.write_text(
        #     f"Upload speed       : {upload} Mbps\n"
        #     f"Download speed     : {download} Mbps\n"
        #     f"Idle Latency       : {idle} ms\n"
        #     f"Download Latency   : {dlat} ms\n"
        #     f"Upload Latency     : {ulat} ms\n", encoding="utf-8"
        # )


        print('POSTING DATA')
        payload = {
            "ip": args.ip, # os.popen("hostname -I 2>/dev/null").read().strip().split()[0] if os.name != "nt" else ""
            "hostname": os.environ.get("COMPUTERNAME") or os.popen("hostname").read().strip(),
            "serial": None,
            "device_id": None,
            "download_mbps": str(download),
            "upload_mbps":   str(upload),
            "idle_ms":       str(idle).replace(" ms",""),
            "download_latency_ms": str(dlat).replace(" ms",""),
            "upload_latency_ms":   str(ulat).replace(" ms",""),
        }
        maybe_post(args.post_url, payload)
        return

    else:
        android = SpeedtestAdb()
        devices = [s.strip() for s in args.adb_devices.split(',')] if args.adb_devices else android.get_connected_devices()
        if not devices: print("No connected ADB devices found."); return
        print(f"Found {len(devices)} device(s): {devices}")

        results = []
        with concurrent.futures.ThreadPoolExecutor() as ex:
            #TODO since ip takes only one value, we are passing same ip to all devices this needs to be fixed if we run for multiple devices at once
            for f in concurrent.futures.as_completed([ex.submit(android.run_speedtest_on_device, s, args.ip, args.post_url) for s in devices]):
                r = f.result()
                if r: results.append(r)

        # if len(results) == 1:
        #     r = results[0]
        #     Path(f"{(args.ip).replace('.', '_')}_speedtest.txt").write_text(
        #         f"Upload speed       : {r['upload']} Mbps\n"
        #         f"Download speed     : {r['download']} Mbps\n"
        #         f"Idle Latency       : {r['idle']} ms\n"
        #         f"Download Latency   : {r['dlat']} ms\n"
        #         f"Upload Latency     : {r['ulat']} ms\n", encoding="utf-8"
        #     )
        # elif results:
        #     Path(f"{(args.ip).replace('.', '_')}_speedtest.txt").write_text(
        #         "\n".join([f"[{r['serial']}]\n"
        #                 f"Upload speed       : {r['upload']} Mbps\n"
        #                 f"Download speed     : {r['download']} Mbps\n"
        #                 f"Idle Latency       : {r['idle']} ms\n"
        #                 f"Download Latency   : {r['dlat']} ms\n"
        #                 f"Upload Latency     : {r['ulat']} ms\n"
        #                 for r in results]), encoding="utf-8"
        #     )


if __name__ == "__main__":
    main()