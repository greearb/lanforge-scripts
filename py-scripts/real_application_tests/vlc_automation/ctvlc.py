import subprocess
import socket
import time
import argparse
import sys
import os
import platform
import logging
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_log_fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_log_fmt)
logger.addHandler(_console_handler)

_file_handler = logging.FileHandler(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ctvlc.log"),
    mode="w",
)
_file_handler.setFormatter(_log_fmt)
logger.addHandler(_file_handler)


def linux_display_available():
    """True if an X display exists for VLC's Qt interface.

    LANforge sets DISPLAY by convention, but if no X server is listening there
    VLC dies on startup and every downstream symptom (RC socket refused, no
    stats, no video) follows from that.
    """
    display = os.environ.get("DISPLAY")
    if not display:
        return False
    try:
        num = display.split(":")[-1].split(".")[0]
        return os.path.exists(f"/tmp/.X11-unix/X{num}")
    except Exception:
        return False


def find_vlc_path():
    system_os = platform.system()
    if system_os == "Windows":
        for path in [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        ]:
            if os.path.exists(path):
                return path
        raise FileNotFoundError("VLC not found in standard locations on Windows.")
    elif system_os == "Darwin":
        return "open"
    else:
        return "vlc"


def build_vlc_command(
    mode,
    media_file,
    mcast_ip,
    port,
    rc_port,
    client_id,
    multi_stream=False,
    miface=None,
    headless=False,
    vb=None,
    ab=96,
    network_caching=None,
    simple=False,
):
    system_os = platform.system()
    vlc = find_vlc_path()
    stream_url = f"udp://@{mcast_ip}:{port}"

    if system_os == "Darwin":
        # macOS: launch via LaunchServices ("open"), which runs in the
        # logged-in GUI session. A direct binary launch from a service
        # context (e.g. a LANforge endpoint) has no access to WindowServer,
        # so no video appears. -n forces a new instance; without it
        # LaunchServices activates a running VLC and discards --args.
        cmd = [vlc, "-n", "-a", "VLC", "--args"]
    else:
        cmd = [vlc]

    if mode == "host":
        cmd.append(media_file)
        chain = f"std{{access=udp,mux=ts,dst={mcast_ip}:{port}}}"
        if vb:
            # Transcode down: multicast over WiFi is sent at a low basic rate
            # with no retries, so high-bitrate streams often arrive too
            # damaged to decode.
            transcode = (
                f"transcode{{vcodec=h264,vb={vb},acodec=mp4a,ab={ab},channels=2,scale=1}}"
            )
            sout = f"#{transcode}:{chain}" if headless else f"#{transcode}:duplicate{{dst=display,dst={chain}}}"
        else:
            sout = f"#{chain}" if headless else f"#duplicate{{dst=display,dst={chain}}}"
        cmd += ["--sout", sout]
    elif mode == "client" and not multi_stream:
        # Multi-stream clients get their URLs via the RC playlist instead,
        # so the order queued is known exactly (see seed_playlist).
        cmd.append(stream_url)

    if headless:
        cmd += ["--intf", "dummy"]
    elif system_os == "Linux" and not linux_display_available():
        # No display: --intf qt would exit immediately and take the RC socket
        # (and all stats) with it. Dummy still receives and reports.
        logger.warning(
            "No usable X display (DISPLAY=%r); using --intf dummy. Stats will be "
            "collected but no video window will appear.",
            os.environ.get("DISPLAY"),
        )
        cmd += ["--intf", "dummy"]
    elif system_os != "Darwin":
        cmd += ["--intf", "qt"]

    if system_os == "Linux":
        # --miface is the multicast OUTPUT interface. It does NOT control
        # which interface a client joins on -- that is the OS routing table /
        # service order, so a dual-homed client needs WiFi prioritised there.
        sta_id = miface
        if not sta_id:
            sta_name = client_id.split(".")
            sta_id = sta_name[2] if len(sta_name) >= 3 else None
        if sta_id:
            cmd += ["--miface", f"{sta_id}"]

    if network_caching:
        cmd += ["--network-caching", str(network_caching)]

    if not simple:
        cmd += ["--extraintf", "rc", "--rc-host", f"localhost:{rc_port}"]

    if mode == "host" or multi_stream:
        # Host: loop the local file for the whole test. Multi-stream client:
        # needed so "next" wraps from the last item back to the first.
        # Deliberately NOT set for a single-stream client -- on a live udp://
        # input it makes VLC treat any hiccup as end-of-item and reconnect.
        cmd.append("--loop")

    return cmd


def connect_rc_socket(rc_port):
    for _ in range(20):
        try:
            sock = socket.create_connection(("localhost", rc_port), timeout=2)
            try:
                sock.recv(4096)
            except Exception as e:
                logger.warning("RC socket recv error: %s", e)
            return sock
        except Exception as e:
            logger.warning("RC socket connect attempt failed: %s", e)
            time.sleep(1)
    return None


def rc_send(sock, command, wait=0.5):
    """Send one RC command and drain the reply."""
    try:
        sock.sendall((command + "\n").encode())
        time.sleep(wait)
        return sock.recv(4096).decode(errors="ignore")
    except Exception as e:
        logger.warning("RC command %r failed: %s", command, e)
        return ""


def seed_playlist(sock, urls):
    """Load every URL into the playlist: first plays, rest are queued.

    "clear" first so playlist position stays predictable for switching.
    """
    rc_send(sock, "clear")
    rc_send(sock, f"add {urls[0]}")
    for url in urls[1:]:
        rc_send(sock, f"enqueue {url}")


def get_current_input(sock):
    """Ask VLC which MRL is playing right now."""
    reply = rc_send(sock, "status", wait=0.3)
    for line in reply.splitlines():
        if "new input" in line.lower():
            return line.split(":", 1)[-1].strip()
    return None


def switch_playlist_stream(sock):
    """Advance to the next queued item.

    With --loop set, "next" cycles the playlist and wraps around, so this
    works for any number of streams without tracking absolute indices.
    """
    rc_send(sock, "next")


def monitor_stats(sock, duration, fserver, client_id):
    start_time = time.time()
    try:
        while True:
            if time.time() - start_time > duration:
                logger.info("Done collecting stats for %d seconds.", duration)
                break
            try:
                sock.sendall(b"stats\n")
                time.sleep(1)
                data = sock.recv(8192).decode()
                stats = parse_stats(data)
                report_starts_to_server(stats, client_id, fserver)
                time.sleep(2)
            except Exception as e:
                logger.error("Error during stats collection: %s", e)
                time.sleep(2)
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    finally:
        try:
            logger.info("Stopping VLC RC connection.")
            sock.sendall(b"quit\n")
            sock.close()
        except Exception as e:
            logger.error("Error stopping VLC RC connection: %s", e)


def monitor_stats_multi(
    sock, duration, fserver, client_id, urls, switch_mode, switch_interval, switch_every
):
    """Poll stats while cycling through several multicast streams.

    Each sample is tagged with the active stream; each switch is additionally
    reported as a transition record carrying the outgoing stream's last stats.
    """
    start_time = time.time()
    total = len(urls)
    active_idx = 0
    iter_count = 0
    last_switch = time.time()

    try:
        while True:
            if time.time() - start_time > duration:
                logger.info("Done collecting stats for %d seconds.", duration)
                break

            try:
                sock.sendall(b"stats\n")
                time.sleep(1)
                stats = parse_stats(sock.recv(8192).decode())
                stats["active_stream"] = active_idx + 1
                stats["active_url"] = urls[active_idx]
                stats["total_streams"] = total
                report_starts_to_server(stats, client_id, fserver)
                time.sleep(2)
            except Exception as e:
                logger.error("Error during stats collection: %s", e)
                time.sleep(2)

            iter_count += 1
            now = time.time()
            due = (switch_mode == "time" and (now - last_switch) >= switch_interval) or (
                switch_mode == "iteration" and iter_count >= switch_every
            )
            if not due:
                continue

            # Snapshot the outgoing stream immediately before the cut.
            try:
                sock.sendall(b"stats\n")
                time.sleep(1)
                pre_stats = parse_stats(sock.recv(8192).decode())
            except Exception as e:
                logger.error("Error reading pre-switch stats: %s", e)
                pre_stats = {}

            to_idx = (active_idx + 1) % total
            switch_playlist_stream(sock)

            transition = {
                "transition": True,
                "switch_time": time.time(),
                "switch_mode": switch_mode,
                "from_stream": active_idx + 1,
                "to_stream": to_idx + 1,
                "from_url": urls[active_idx],
                "to_url": urls[to_idx],
                "confirmed_playing": get_current_input(sock),
                "pre_switch_stats": pre_stats,
            }
            report_starts_to_server(transition, client_id, fserver)
            logger.info("Switched stream %d -> %d (%s)", active_idx + 1, to_idx + 1, urls[to_idx])

            active_idx = to_idx
            iter_count = 0
            last_switch = time.time()

    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    finally:
        try:
            logger.info("Stopping VLC RC connection.")
            sock.sendall(b"quit\n")
            sock.close()
        except Exception as e:
            logger.error("Error stopping VLC RC connection: %s", e)


def parse_stats(text):
    stats = {}

    for line in text.splitlines():
        line = line.strip()
        if "input bytes read" in line:
            stats["input_bytes_read"] = line.split(":")[-1].strip()
        elif "input bitrate" in line:
            stats["input_bitrate"] = line.split(":")[-1].strip()
        elif "demux bytes read" in line:
            stats["demux_bytes_read"] = line.split(":")[-1].strip()
        elif "demux bitrate" in line:
            stats["demux_bitrate"] = line.split(":")[-1].strip()
        elif "demux corrupted" in line:
            stats["demux_corrupted"] = line.split(":")[-1].strip()
        elif "discontinuities" in line:
            stats["discontinuities"] = line.split(":")[-1].strip()
        elif "video decoded" in line:
            stats["video_decoded"] = line.split(":")[-1].strip()
        elif "frames displayed" in line:
            stats["frames_displayed"] = line.split(":")[-1].strip()
        elif "frames lost" in line:
            stats["frames_lost"] = line.split(":")[-1].strip()
        elif "audio decoded" in line:
            stats["audio_decoded"] = line.split(":")[-1].strip()
        elif "buffers played" in line:
            stats["buffers_played"] = line.split(":")[-1].strip()
        elif "buffers lost" in line:
            stats["buffers_lost"] = line.split(":")[-1].strip()

    defaults = {
        "input_bytes_read": "0",
        "input_bitrate": "0 kb/s",
        "demux_bytes_read": "0",
        "demux_bitrate": "0 kb/s",
        "demux_corrupted": "0",
        "discontinuities": "0",
        "video_decoded": "0",
        "frames_displayed": "0",
        "frames_lost": "0",
        "audio_decoded": "0",
        "buffers_played": "0",
        "buffers_lost": "0",
    }
    for k, v in defaults.items():
        stats.setdefault(k, v)
    logger.debug("Parsed stats: %s", stats)
    return stats


def report_starts_to_server(
    stats, client_id="client1", server_url="http://0.0.0.0:5959/stats"
):
    # 0.0.0.0 is a bind-any address, not a reachable destination: it only
    # appears when no --fserver was given, so there is nothing to report to.
    if not server_url or "0.0.0.0" in server_url:
        return
    try:
        payload = {client_id: stats}
        res = requests.post(server_url, json=payload)
        logger.info("Sent stats: HTTP %s", res.status_code)
    except Exception as e:
        logger.error("Error sending stats to server: %s", e)


def main():
    parser = argparse.ArgumentParser(
        description="Cross-platform VLC Launcher (host/client)"
    )
    parser.add_argument(
        "mode", choices=["host", "client"], help="Launch VLC as host or client"
    )
    parser.add_argument("--media", help="Path to media file (host only)")
    parser.add_argument("--mcast_ip", default="239.255.0.1", help="Multicast IP")
    parser.add_argument("--port", type=int, default=1234, help="Multicast port")
    parser.add_argument(
        "--rc_port", type=int, default=4212, help="RC port for remote control"
    )
    parser.add_argument(
        "--duration", type=int, default=30, help="Duration in seconds to collect stats"
    )
    parser.add_argument("--fserver", type=str, default="0.0.0.0:5959")
    parser.add_argument("--client_id", type=str, default=None)
    parser.add_argument(
        "--extra_streams",
        type=str,
        default=None,
        help="Comma-separated ip:port pairs for additional streams (client mode). "
        "Enables switching between them. Max 5 streams in total.",
    )
    parser.add_argument(
        "--switch_mode",
        choices=["time", "iteration"],
        default="time",
        help="Switch trigger: elapsed seconds or poll cycles",
    )
    parser.add_argument(
        "--switch_interval",
        type=int,
        default=30,
        help="Seconds between switches when --switch_mode=time",
    )
    parser.add_argument(
        "--switch_every",
        type=int,
        default=5,
        help="Poll cycles between switches when --switch_mode=iteration",
    )
    parser.add_argument(
        "--miface",
        type=str,
        default=None,
        help="Linux only: multicast interface. Defaults to the one derived from --client_id.",
    )
    parser.add_argument(
        "--miface_addr",
        type=str,
        default=None,
        help="Station IP lf_interop_vlc.py sends for non-bash clients. Accepted so the launch "
             "does not fail on an unknown argument; not applied to VLC's input side.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Host mode on a machine with no display: multicast output only, no local playback.",
    )
    parser.add_argument(
        "--vb",
        type=int,
        default=None,
        help="Host mode: transcode video to this bitrate in kb/s (e.g. 800).",
    )
    parser.add_argument(
        "--ab", type=int, default=96, help="Host mode: audio bitrate in kb/s when --vb is used."
    )
    parser.add_argument(
        "--network_caching",
        type=int,
        default=None,
        help="Client mode: input buffer in ms. Helps absorb bursty multicast loss.",
    )
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Client mode: play only, no RC socket and no stats.",
    )

    args = parser.parse_args()

    logger.info("ctvlc.py running from %s", os.path.abspath(__file__))

    if args.mode == "host" and not args.media:
        logger.error("Host mode requires --media argument.")
        sys.exit(1)

    client_id = args.client_id
    if not client_id:
        client_id = socket.gethostname()

    all_urls = [f"udp://@{args.mcast_ip}:{args.port}"]
    if args.mode == "client" and args.extra_streams:
        for pair in args.extra_streams.split(","):
            pair = pair.strip()
            if not pair:
                continue
            if ":" not in pair:
                logger.error("Malformed --extra_streams entry (expected ip:port): %s", pair)
                sys.exit(1)
            ip, port = pair.rsplit(":", 1)
            all_urls.append(f"udp://@{ip.strip()}:{port.strip()}")

    if len(all_urls) > 5:
        logger.error("%d total streams configured -- 5 is the maximum.", len(all_urls))
        sys.exit(1)

    multi_stream = args.mode == "client" and len(all_urls) > 1

    cmd = build_vlc_command(
        args.mode,
        args.media,
        args.mcast_ip,
        args.port,
        args.rc_port,
        client_id,
        multi_stream=multi_stream,
        miface=args.miface,
        headless=args.headless,
        vb=args.vb,
        ab=args.ab,
        network_caching=args.network_caching,
        simple=args.simple,
    )

    if platform.system() == "Darwin":
        # "open" reuses a running instance, so make sure the old one is gone.
        subprocess.run(["pkill", "-f", "VLC.app"], capture_output=True)
        time.sleep(2)

    logger.info("Launching VLC in %s mode...", args.mode.upper())
    logger.info("Command: %s", cmd)

    if platform.system() == "Darwin":
        # "open" exits as soon as LaunchServices takes over, so capture its
        # result: a non-zero exit is how a missing GUI session shows up.
        vlc_proc = subprocess.run(cmd, capture_output=True, text=True)
        if vlc_proc.returncode != 0:
            logger.error(
                "open failed (exit %s): %s",
                vlc_proc.returncode,
                (vlc_proc.stderr or vlc_proc.stdout).strip(),
            )
            logger.error(
                "This usually means no logged-in GUI session is available to show a window."
            )
    else:
        vlc_proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    if args.simple:
        logger.info("Playback-only mode: playing %s for %ds (no stats).", all_urls[0], args.duration)
        try:
            time.sleep(args.duration)
        except KeyboardInterrupt:
            logger.info("Interrupted by user.")
    else:
        logger.info("Connecting to RC socket on port %d...", args.rc_port)
        sock = connect_rc_socket(args.rc_port)
        if not sock:
            logger.error("Could not connect to VLC RC socket.")
            if hasattr(vlc_proc, "terminate"):
                vlc_proc.terminate()
            sys.exit(1)

        fserver_url = "http://" + args.fserver + "/stats"
        if multi_stream:
            logger.info("Multi-stream mode: %d streams %s", len(all_urls), all_urls)
            seed_playlist(sock, all_urls)
            monitor_stats_multi(
                sock,
                args.duration,
                fserver_url,
                client_id,
                all_urls,
                args.switch_mode,
                args.switch_interval,
                args.switch_every,
            )
        else:
            monitor_stats(sock, args.duration, fserver_url, client_id)

    logger.info("Terminating VLC process.")
    if hasattr(vlc_proc, "terminate"):
        vlc_proc.terminate()
    if platform.system() == "Darwin":
        subprocess.Popen("osascript -e 'quit app \"VLC\"'", shell=True)


if __name__ == "__main__":
    main()
