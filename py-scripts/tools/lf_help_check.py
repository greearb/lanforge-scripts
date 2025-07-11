#!/usr/bin/env python3
"""
This script is designed to perform a simple "help check" on all
Python scripts located in the 'py-scripts/' directory.

A "help check" primarily serves as an indicator for larger issues.
It is not meant to replace proper testing.
"""
import argparse
import glob
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


def main(help_check_scripts: list, help_summary_scripts: list, group_size: int, **kwargs):
    """
    Run help parallelized help checks on provided scripts

    :param help_check_scripts: List of scripts to run help check
    :param help_summary_scripts: List of scripts to run help summary check
    :param group_size: Maximum number of scripts to group together
                       for parallelized help checks
    :return int, list: Integer representing pass or fail (0 or 1),
                       tuple containing two lists of failed scripts (if any).
                       First list is scripts that failed help check, second list is
                       scripts that failed help summary check.
    :rtype tuple:
    """
    def report_results(result_data: dict):
        """Internal helper function to report result data

        :return: Dictionary containing script help check data, where the script
                 name is the key and the following data are the values:
                 'timed_out', 'return_code', 'stdout', 'stderr'
        :return int, list: Integer representing pass or fail (0 or 1),
                           list of failed scripts (if any).
        """
        any_failed = False
        failed_scripts = []

        for script, data in result_data.items():
            if data["timed_out"] or data["return_code"] != 0:
                any_failed = True
                failed_scripts.append(script)
                logger.error(f"Script \'{script}\' failed check")
                logger.error(f"Script \'{script}\' stdout:\n{data['stdout']}")
                logger.error(f"Script \'{script}\' stderr:\n{data['stderr']}")

        return any_failed, failed_scripts

    any_failed = False

    help_check_script_groups = generate_script_groups(help_check_scripts, group_size)
    help_summary_script_groups = generate_script_groups(help_summary_scripts, group_size)

    results = run_checks(help_check_script_groups, help_summary_script_groups)

    # Report help check results
    logger.info("Help check results")
    any_failed, failed_help_check_scripts = report_results(results[0])

    # Report help summary check results
    logger.info("Help summary check results")
    any_failed, failed_help_summary_scripts = report_results(results[1])

    if not any_failed:
        return 0, None
    else:
        return 1, (failed_help_check_scripts, failed_help_summary_scripts)


def desired_script(file, help_summary: bool = False):
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
        # Recursive glob search takes care of this but leave here just in case
        return False
    elif file == THIS_SCRIPT_NAME:
        return False
    elif file == "__init__.py":
        return False

    # Only consider directory where script is located. Otherwise, may accidentally
    # filter out all scripts if these strings are somehow used in the full path
    directory_name = os.path.dirname(file)
    if 'tools' in directory_name \
            or 'sandbox' in directory_name \
            or 'scripts_deprecated' in directory_name:
        return False

    # Don't run help summary check on examples, as many currently do not implement it
    if help_summary and 'examples' in file:
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


def run_checks(help_check_script_groups: list, help_summary_script_groups: list) -> dict:
    """
    Run help and help summary checks on segmented script groups,
    returning post-check status after completion.

    :param help_check_script_groups: List of list of strings where each sub-list
                                     contains a list of scripts to check in parallel
    :param help_summary_script_groups: List of list of strings where each sub-list
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
    help_data = {}
    for group in help_check_script_groups:
        for script in group:
            help_data[script] = None
        help_group_data = run_group_check(group, ["--help"])
        help_data.update(help_group_data)

    # Run help summary check
    help_summary_data = {}
    for group in help_summary_script_groups:
        for script in group:
            help_summary_data[script] = None
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

    # Gather all Python scripts in all sub-directories
    all_scripts = glob.glob("./*.py") + glob.glob("./**/*.py")

    # Gather and report help check scripts
    help_check_scripts = [file for file in all_scripts if desired_script(file)]
    num_help_check_scripts = len(help_check_scripts)
    logger.info(f"Running LANforge scripts \'py-scripts\' parallelized help checks on {num_help_check_scripts} scripts")
    logger.debug(f"Running help check on the following scripts: {help_check_scripts}")

    # Gather and report help summary check scripts
    help_summary_scripts = [file for file in help_check_scripts if desired_script(file, help_summary=True)]
    num_help_summary_scripts = len(help_summary_scripts)
    logger.info(f"Running LANforge scripts \'py-scripts\' parallelized help summary checks on {num_help_summary_scripts} scripts")
    logger.debug(f"Running help summary check on the following scripts: {help_summary_scripts}")

    # Run parallelized help checks
    ret, failed_scripts = main(help_check_scripts=help_check_scripts, help_summary_scripts=help_summary_scripts, **vars(args))

    # Summarize checks and exit
    if ret == 0:
        logger.info("All scripts passed help check")
    else:
        failed_help_scripts, failed_help_summary_scripts = failed_scripts
        logger.error(f"The following scripts failed help check: {failed_help_scripts}")
        logger.error(f"The following scripts failed help summary check: {failed_help_summary_scripts}")
    exit(ret)
