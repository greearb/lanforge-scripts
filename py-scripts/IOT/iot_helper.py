import asyncio
import os
import threading
import logging
import sys
import shutil
import pandas as pd
from collections import OrderedDict
from typing import Optional

logger = logging.getLogger(__name__)


# THREAD ENTRY POINT
def start_iot_thread(args):
    """
    Starts IoT execution in a separate thread.

    Args:
        - iot_test (bool): Enable IoT execution
        - iot_iterations (int): Number of iterations
        - duration (int): Test duration in minutes
        - iot_delay (int): Delay between iterations in seconds
        - iot_ip (str)
        - iot_port (str | int)
        - iot_device_list (str): Comma-separated device list
        - iot_testname (str)
        - iot_increment (str): Comma-separated integers

    Behavior:
        - Returns immediately if args.iot_test is False
        - Spawns a daemon or non-daemon thread based on iteration mode
    """
    if not args.iot_test:
        return

    # Case 1: Explicit iterations provided
    if args.iot_iterations > 1:
        iterations = args.iot_iterations
        daemon = False
    else:
        # Case 2: Auto-calculate based on test duration
        total_secs = int(args.duration) * 60
        iterations = max(1, total_secs // args.iot_delay)
        daemon = True

    t = threading.Thread(
        target=trigger_iot,
        args=(
            args.iot_ip,
            args.iot_port,
            iterations,
            args.iot_delay,
            args.iot_device_list,
            args.iot_testname,
            args.iot_increment
        ),
        daemon=daemon
    )
    t.start()


def get_automation_class():
    """
    Resolve IoT Automation class using repo-root-relative path.
    """
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../..")
    )

    iot_scripts_path = os.path.join(
        repo_root,
        "local/interop-webGUI/IoT/scripts"
    )

    if not os.path.exists(iot_scripts_path):
        raise ImportError(
            f"IoT scripts path not found: {iot_scripts_path}"
        )

    if iot_scripts_path not in sys.path:
        sys.path.insert(0, iot_scripts_path)

    from test_automation import Automation  # noqa: E402
    return Automation


def trigger_iot(ip, port, iterations, delay, device_list, testname, increment):
    """
    Entry point for IoT thread.
    """
    asyncio.run(
        run_iot(ip, port, iterations, delay, device_list, testname, increment)
    )


async def run_iot(ip='127.0.0.1',
                  port='8000',
                  iterations=1,
                  delay=5,
                  device_list='',
                  testname='',
                  increment=''):
    try:
        if delay < 5:
            raise ValueError("The minimum IoT delay should be 5 seconds.")

        if device_list:
            device_list = device_list.split(',')
        else:
            device_list = None

        if increment:
            try:
                increment = list(map(int, increment.split(',')))
                if any(i < 1 for i in increment):
                    raise ValueError("Increment values must be positive integers")
            except ValueError as e:
                raise ValueError(
                    "Invalid increment format. Use comma-separated integers."
                ) from e

        Automation = get_automation_class()

        automation = Automation(
            ip=ip,
            port=port,
            iterations=iterations,
            delay=delay,
            device_list=device_list,
            testname=testname,
            increment=increment
        )

        # Fetch devices
        automation.devices = await automation.fetch_iot_devices()

        # Select devices
        automation.select_iot_devices()

        # Run test
        automation.run_test()

        # Generate report
        automation.generate_report()

        await automation.session.close()
        logger.info("IoT Test Completed successfully.")

    except Exception as e:
        logger.error(f"IoT Test failed: {str(e)}", exc_info=True)
        raise


def with_iot_params_in_table(base: dict, iot_summary) -> dict:
    """
    Appends IoT parameters into the test setup table.

    Args:
        base (dict): Base test parameters table
        iot_summary (dict):
            Expected structure:
                {
                    "test_input_table": {
                        "Device List": str,
                        "Iterations": int,
                        "Delay (seconds)": int,
                        "Increment Pattern": str
                    }
                }

    Behavior:
        - Missing keys are ignored and defaulted to empty strings
        - Returns base unchanged if iot_summary is None or invalid
    """
    try:
        if not iot_summary:
            return base

        ti = iot_summary.get("test_input_table", {})
        out = OrderedDict(base)

        out["IoT Device List"] = ti.get("Device List", "")
        out["IoT Iterations"] = ti.get("Iterations", "")
        out["IoT Delay (s)"] = ti.get("Delay (seconds)", "")
        out["IoT Increment"] = ti.get("Increment Pattern", "")

        return out
    except Exception:
        return base


def copy_into_report(raw_path: str,
                     report_dir: str,
                     max_dirs: int = 500) -> Optional[str]:
    """
    Resolve and copy an image into the report directory.

    Args:
        raw_path (str): Source image path (absolute or relative)
        report_dir (str): Destination report directory
        max_dirs (int): Maximum directories to scan under results/

    Returns:
        str: New filename if copied successfully
        None: If source image is not found

    Raises:
        ValueError: If unsafe path is provided
        RuntimeError: If directory scan limit is exceeded
    """
    if not raw_path:
        return None

    abs_src = os.path.abspath(raw_path)

    # SAFETY CHECKS
    unsafe_paths = {
        os.path.abspath(os.getcwd()),
        os.path.abspath("/"),
        os.path.abspath("C:"),
        os.path.abspath("C:\\"),
    }

    if abs_src in unsafe_paths:
        raise ValueError(f"Unsafe path provided: {raw_path}")

    # DIRECT PATH EXISTS
    if os.path.exists(abs_src):
        dst = os.path.join(report_dir, os.path.basename(abs_src))
        if abs_src != os.path.abspath(dst):
            shutil.copy2(abs_src, dst)
        return os.path.basename(dst)

    # BOUNDED DIRECTORY SEARCH
    results_root = os.path.join(os.getcwd(), "results")
    scanned_dirs = 0

    for root, _, files in os.walk(results_root):
        scanned_dirs += 1
        if scanned_dirs > max_dirs:
            raise RuntimeError(
                "Directory scan limit exceeded"
            )

        if os.path.basename(raw_path) in files:
            abs_src = os.path.join(root, os.path.basename(raw_path))
            dst = os.path.join(report_dir, os.path.basename(abs_src))
            shutil.copy2(abs_src, dst)
            return os.path.basename(dst)

    return None


def build_iot_report_section(report, iot_summary):
    """
    Builds IoT-related charts, tables, and increment-wise reports.

    Args:
        report: Report object providing HTML, chart, and table helpers.
        iot_summary (dict):
            Expected keys:
                - statistics_img (str)
                - req_vs_latency_img (str)
                - overall_result_table (dict)
                - increment_reports (dict)

    Behavior:
        - Missing sections are skipped.
        - Image resolution is bounded and validated via copy_into_report().
    """
    if not iot_summary:
        return

    outdir = report.path_date_time
    os.makedirs(outdir, exist_ok=True)

    # Section Header
    report.set_custom_html('<div style="page-break-before: always;"></div>')
    report.build_custom()
    report.set_custom_html('<h2><u>IoT Results</u></h2>')
    report.build_custom()

    # Statistics Chart
    stats_png = copy_into_report(
        iot_summary.get("statistics_img"),
        outdir
    )
    if stats_png:
        report.build_chart_title("Test Statistics")
        report.set_custom_html(
            f'<img src="{stats_png}" style="width:100%; height:auto;">'
        )
        report.build_custom()

    # Request vs Latency Chart
    rvl_png = copy_into_report(
        iot_summary.get("req_vs_latency_img"),
        outdir
    )
    if rvl_png:
        report.build_chart_title("Request vs Average Latency")
        report.set_custom_html(
            f'<img src="{rvl_png}" style="width:100%; height:auto;">'
        )
        report.build_custom()

    # Overall Result Table
    ort = iot_summary.get("overall_result_table") or {}
    if ort:
        rows = [{
            "Device": dev,
            "Min Latency (ms)": stats.get("min_latency"),
            "Avg Latency (ms)": stats.get("avg_latency"),
            "Max Latency (ms)": stats.get("max_latency"),
            "Total Iterations": stats.get("total_iterations"),
            "Success Iters": stats.get("success_iterations"),
            "Failed Iters": stats.get("failed_iterations"),
            "No-Response Iters": stats.get("no_response_iterations"),
        } for dev, stats in ort.items()]

        df_overall = pd.DataFrame(rows).round(2)

        report.set_custom_html('<div style="page-break-inside: avoid;">')
        report.build_custom()
        report.set_obj_html(
            _obj_title="Overall IoT Result Table",
            _obj=" "
        )
        report.build_objective()
        report.set_table_dataframe(df_overall)
        report.build_table()
        report.set_custom_html('</div>')
        report.build_custom()

    # Increment-wise Reports
    inc = iot_summary.get("increment_reports") or {}
    if inc:
        report.set_custom_html('<h3>Reports by Increment Steps</h3>')
        report.build_custom()

        for step_name, rep in inc.items():

            report.set_custom_html(
                f'<h4><u>{step_name.replace("_", " ")}</u></h4>'
            )
            report.build_custom()

            # Average latency graph
            lat_png = copy_into_report(
                rep.get("latency_graph"),
                outdir
            )
            if lat_png:
                report.build_chart_title("Average Latency")
                report.set_custom_html(
                    f'<img src="{lat_png}" style="width:100%; height:auto;">'
                )
                report.build_custom()

            # Success / failure graph
            res_png = copy_into_report(
                rep.get("result_graph"),
                outdir
            )
            if res_png:
                report.build_chart_title("Success Count")
                report.set_custom_html(
                    f'<img src="{res_png}" style="width:100%; height:auto;">'
                )
                report.build_custom()

            # Detailed iteration table
            data_rows = rep.get("data") or []
            if data_rows:
                df = pd.DataFrame(data_rows).rename(
                    columns={
                        "latency__ms": "Latency_ms",
                        "latency_ms": "Latency_ms"
                    }
                )

                if "Latency_ms" in df.columns:
                    df["Latency_ms"] = (
                        pd.to_numeric(df["Latency_ms"], errors="coerce")
                        .round(3)
                    )

                if "Result" in df.columns:
                    df["Result"] = df["Result"].map(
                        lambda x: "Success" if bool(x) else "Failure"
                    )

                desired_cols = [
                    "Iteration",
                    "Device",
                    "Current State",
                    "Latency_ms",
                    "Result"
                ]
                df = df[[c for c in desired_cols if c in df.columns]]

                report.set_table_dataframe(df)
                report.build_table()

            report.set_custom_html('<hr>')
            report.build_custom()


def add_iot_report_section(report, iot_summary):
    if not iot_summary:
        return
    build_iot_report_section(report, iot_summary)
