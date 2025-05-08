#!/usr/bin/env python3
"""
This script is designed to perform a simple "help check" on all
Python scripts located in the 'py-scripts/' directory.

A "help check" primarily serves as an indicator for larger issues.
It is not meant to replace proper testing.
"""
import argparse
import logging
import os
import subprocess
from time import sleep, time

THIS_SCRIPT_NAME = os.path.basename(__file__)


def parse_args():
    """Configure and perform argument parsing for help check script"""
    parser = argparse.ArgumentParser(
        description="Help check script for LANforge Python scripts in "
                    "the \'py-scripts\' directory of the LANforge "
                    "scripts repository"
    )
    parser.add_argument(
        "--parallelism",
        dest="group_size",
        help="Number of scripts to invoke in parallel",
        type=int,
        default=10,
    )
    parser.add_argument("--debug", help="Enable verbose logging", action="store_true")
    return parser.parse_args()


def configure_logging(debug: bool = False):
    """Configure logging for the help check script"""
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s: %(message)s"
    )

    # Configure this modules' logger
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # If debugging specified, then increase logging verbosity
    if debug:
        logger.setLevel(logging.DEBUG)


def main(scripts: list, group_size: int, **kwargs):
    """
    Run help parallelized help check on provided scripts

    :param scripts: List of scripts to run help check
    :param group_size: Maximum number of scripts to group together
                       for parallelized help checks
    :return int, list: Integer representing pass or fail (0 or 1),
                       tuple containing two lists of failed scripts (if any).
                       First list is scripts that failed help check, second list is
                       scripts that failed help summary check.
    :rtype tuple:
    """
    any_failed = False

    script_groups = generate_script_groups(scripts, group_size)
    check_data = run_checks(script_groups)

    help_data = check_data[0]
    help_summary_data = check_data[1]

    failed_help_scripts = []
    for script, data in help_data.items():
        if data["timed_out"] or data["return_code"] != 0:
            any_failed = True
            failed_help_scripts.append(script)
            logger.error(f"Script \'{script}\' failed help check")
            logger.error(f"Script \'{script}\' stdout:\n{data['stdout']}")
            logger.error(f"Script \'{script}\' stderr:\n{data['stderr']}")

    failed_help_summary_scripts = []
    for script, data in help_summary_data.items():
        if data["timed_out"] or data["return_code"] != 0:
            any_failed = True
            failed_help_summary_scripts.append(script)
            logger.error(f"Script \'{script}\' failed help summary check")
            logger.error(f"Script \'{script}\' stdout:\n{data['stdout']}")
            logger.error(f"Script \'{script}\' stderr:\n{data['stderr']}")

    if not any_failed:
        return 0, None
    else:
        return 1, (failed_help_scripts, failed_help_summary_scripts)


def desired_script(file):
    """
    Filtering function to match only desired scripts.

    Mainly serves to check that the script is a Python file
    and is not the help check script (don't want to start a
    recursion doom loop).

    :param file: Script to check
    :return bool: Keep script if true, otherwise ignore
    :rtype bool:
    """

    if not os.path.isfile(file):
        return False
    elif not file.endswith(".py"):
        return False
    elif file == THIS_SCRIPT_NAME:
        return False
    elif file == "__init__.py":
        return False

    return True


def generate_script_groups(scripts: list,
                           group_size: int) -> list:
    """
    Separate scripts into groups to run in parallel

    :param scripts: List of scripts to segment based on group size
    :param group_size: Maximum number of scripts to group together
                       for parallelized help checks
    :return script_groups: List of list of strings where each sub-list
                           contains a list of scripts to check in parallel
    :rtype list:
    """
    num_pyscripts = len(scripts)
    script_groups = []

    # Call to 'int()' will floor (round down) the resulting value
    for ix in range(int(num_pyscripts / group_size)):
        lower_ix = ix * group_size
        upper_ix = (ix + 1) * group_size
        script_groups.append(scripts[lower_ix:upper_ix])

    # Group any remaining scripts into final group
    num_remain_scripts = num_pyscripts % group_size
    if num_remain_scripts != 0:
        script_groups.append(scripts[-num_remain_scripts:])

    return script_groups


def run_checks(script_groups: list) -> dict:
    """
    Run help and help summary checks on segmented script groups,
    returning post-check status after completion.

    :param script_groups: List of list of strings where each sub-list
                          contains a list of scripts to check in parallel
    :return: Dictionary containing script help check data, where the script
             name is the key and the following data are the values:
             'timed_out', 'return_code', 'stdout', 'stderr'
    :rtype dict:
    """
    # Start checks in parallel, indicating success/failure based on return code
    # and if script timed out
    all_start_time = time()

    # Run help check
    help_data = {script: None for script in scripts}
    for group in script_groups:
        help_group_data = run_group_check(group, ["--help"])
        help_data.update(help_group_data)

    # Run help summary check
    help_summary_data = {script: None for script in scripts}
    for group in script_groups:
        help_summary_group_data = run_group_check(group, ["--help_summary"])
        help_summary_data.update(help_summary_group_data)

    all_elapsed_time = time() - all_start_time
    logger.debug(
        f"All script checks took {all_elapsed_time:.2f} seconds to complete"
    )

    return help_data, help_summary_data


def run_group_check(group: list, script_options: list) -> list:
    """
    Run check on script group with specified options appended,
    reporting back data on checks.

    :param groups: List of strings where each string is a script to check
                   in parallel
    :return: Dictionary containing script help check data, where the script
             name is the key and the following data are the values:
             'timed_out', 'return_code', 'stdout', 'stderr'
    :rtype list:
    """
    script_data = {}
    group_start_time = time()

    # Start scripts in parallel
    logger.debug(f"Running check for script group: {group}")
    script_procs = {}
    for script in group:
        # Start the script in the background, ignoring any output
        # and only checking the return code when complete
        proc = subprocess.Popen(
            ["python3", script] + script_options,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        script_procs[script] = proc

    # Wait up to timeout seconds, checking all scripts for completion periodically
    wait_ms = 100
    num_iters = (1_000 * 10) // wait_ms
    for _ in range(num_iters):
        sleep(wait_ms / 1_000)

        iter_script_procs = script_procs.copy()
        for script, proc in iter_script_procs.items():
            # Poll to see if complete. If not, will return None
            ret = proc.poll()
            if ret is not None:
                # Remove script from tracking dict for active scripts
                del script_procs[script]

                stdout, stderr = proc.communicate()
                script_data[script] = {
                    "timed_out": False,
                    "return_code": proc.returncode,
                    "stdout": stdout.decode('utf-8'),
                    "stderr": stderr.decode('utf-8'),
                }

        # Check if all scripts complete
        if len(script_procs) == 0:
            break

    # Any remaining scripts in 'scripts_proc' dictionary timed out
    # All others were removed when they completed in above check
    for script, proc in script_procs.items():
        # Kill process and save stderr
        # Need to convert data from byte array
        proc.kill()
        stdout, stderr = proc.communicate()

        script_data[script] = {
            "timed_out": True,
            "return_code": proc.returncode,
            "stdout": stdout.decode("UTF-8"),
            "stderr": stderr.decode("UTF-8"),
        }

    group_elapsed_time = time() - group_start_time
    logger.debug(
        f"Script group checks took {group_elapsed_time:.2f} seconds to complete"
    )

    return script_data


if __name__ == "__main__":
    args = parse_args()
    configure_logging(debug=args.debug)

    # Scripts need to run w/ CWD set to 'py-scripts/'
    cwd = os.getcwd()
    if os.path.basename(cwd) != "py-scripts":
        logger.error("This script must be run from the 'py-scripts' directory")
        exit(2)

    # Gather all Python scripts
    scripts = [file for file in os.listdir(".") if desired_script(file)]
    num_scripts = len(scripts)
    logger.info(f"Running LANforge scripts \'py-scripts\' parallelized help and help summary checks on {num_scripts} scripts")
    logger.debug(f"Running help and help summary check on the following scripts: {scripts}")

    # Run parallelized help checks
    ret, failed_scripts = main(scripts=scripts, **vars(args))

    # Summarize checks and exit
    if ret == 0:
        logger.info("All scripts passed help check")
    else:
        failed_help_scripts, failed_help_summary_scripts = failed_scripts
        logger.error(f"The following scripts failed help check: {failed_help_scripts}")
        logger.error(f"The following scripts failed help summary check: {failed_help_summary_scripts}")
    exit(ret)
