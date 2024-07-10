#!/usr/bin/env python3
import pathlib
import platform
from subprocess import PIPE, call, run
import argparse
import os
import os.path
import sys
import sysconfig
from pprint import pprint

"""
List of packages
"""
pip_packages: list = [
    'cryptography',
    'kaleido',
    'matplotlib',
    'numpy',
    'pandas',
    'paramiko',
    'pdfkit',
    'pexpect-serial',
    'pip-search',
    'plotly',
    'psutil',
    'pyserial',
    'pyshark',
    'scipy',
    'scp',
    'simple-geometry',
    'websocket-client',
    'xlsxwriter',
]


class UpdateDependencies:
    def __init__(self, packages: list = None):
        self.packages: list = packages
        self.packages_installed: list = []
        self.packages_failed: list = []
        self.system_python_path: str = None
        self.chosen_python_path: str = None
        self.scripts_path: str = str(os.path.expanduser("~/scripts"))
        self.py_version: str = sys.version[0:sys.version.find('.', 2)]
        self.venv_path: str = f"{self.scripts_path}/venv-{self.py_version}"

    def upgrade_pip(self):
        print("Upgrading pip...")
        try:
            # this call (on fedora) very likely needs to be done thru sudo
            call('pip3 install --upgrade pip', shell=True)
        except Exception as e:
            print(e)

    def determine_py_path(self, possible_path: str = None):
        """
        Evaluates system python path
        :param possible_path: string pathname of python directory or executable
        :return: fully qualified python path
        """
        try:
            if os.name == "nt":
                self.system_python_path = run(["where", "python3"], shell=True, check=True, stdout=PIPE,
                                              timeout=1).stdout.decode('UTF-8').rstrip()
            else:
                self.system_python_path = run(["which", "python3"], stdout=PIPE, timeout=1).stdout.decode(
                    'UTF-8').rstrip()

            if not self.system_python_path:
                print("* unable to find python. Please use --use_python option to identify the python3 location")
                exit(1)

            print(f"Detected system python3 at [{self.system_python_path}]")

            if not possible_path:
                return self.system_python_path

            if os.path.isfile(possible_path):
                self.chosen_python_path = possible_path
                return possible_path

            if os.path.isdir(possible_path):
                if os.name == "nt" and pathlib.Path(f"{possible_path}/python3.exe").is_file():
                    self.chosen_python_path = f"{possible_path}\\python3.exe"
                elif pathlib.Path(f"{possible_path}/python3").is_file():
                    self.chosen_python_path = f"{possible_path}/python3"
            else:
                print(f"* unable to find python at {possible_path}")
                exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def remove_venv(self, venv_directory: pathlib.Path = None):
        """
        Check to see if the venv_directory has a bin/activate file. If so,
        remove the directory
        :param venv_directory:  containing virtual environment
        :return:
        """
        has_bin_activate = False
        if venv_directory and venv_directory.is_dir():
            if os.name == 'nt':
                if os.path.isfile(f"{venv_directory}\\bin\\activate.bat"):
                    print(f"Removing {venv_directory}...")
                    res = call(f"rmdir {venv_directory} /s /q")
                    return res == 0
                else:
                    print(f"* Not removing {venv_directory}, bin\\activate.bat not found.")
                    return False
            else:
                if os.path.isfile(f"{venv_directory}/bin/activate"):
                    print(f"Removing {venv_directory}...")
                    res = call(f"rm -rf {venv_directory}")
                    return res == 0
                else:
                    print(f"* Not removing {venv_directory}, bin/activate not found.")
                    return False
        else:
            print(f"* Directory does not exist: {venv_directory}")
            exit(1)

    def create_venv(self):
        """Create a virtual environment
        """
        print(f"Creating a python virtual environment at {self.venv_path}...")

    def install_pkg(self, package: str):
        if os.name == 'nt':
            command = f"pip3 install {package}"
        else:
            command = f"pip3 install {package} >/tmp/pip3-stdout 2>/tmp/pip3-stderr"
        print(" ", end="", flush=True)
        res = call(command, shell=True)
        if res == 0:
            print(f"✔{package}", end=" ", flush=True)
            self.packages_installed.append(package)
        else:
            print(f"✘{package}", end=" ", flush=True)
            self.packages_failed.append(package)

    def install_packages(self):
        """Use subprocess.call  commands to pip3 install packages without a virtual environment
        """
        print("Upgrading packages:", end=" ", flush=True)
        for package in self.packages:
            self.install_pkg(package=package)

        print("\nInstall complete.")
        print(f"Packages Installed Success: {self.packages_installed}\n")
        if not self.packages_failed:
            return
        print(f"Failed to install: {self.packages_failed}\n"
              + "(Some scripts may not need these packages) "
              + "To see errors try: pip3 install $package", flush=True)


def main():
    version = sys.version[0:sys.version.index('.', 2)]

    help_summary = "The lanforge-scripts/py-scripts and lanforge-scripts/py-json collection require "
    "a number of Pypi libraries. This script installs those libraries or creates "
    "a virtual environment for those libraries. This script has been updated to "
    "detect PEP 668 externally-managed libraries; in the presence of the externally-managed "
    f"condition, a virtual environment will be created in $home/scripts/venv-${version}. "
    "This script will update a symlink $home/lanforge/venv to default virtual environment "
    "as necessary."

    parser = argparse.ArgumentParser(
        prog="update_dependencies.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="NAME: update_dependencies.py\n"
                    "PURPOSE:  Installs python3 script package dependencies\n"
                    "OUTPUT: List of successful and unsuccessful installs\n"
                    "NOTES: Run this as lanforge user (not root)\n\n"
                    f"{help_summary}"
    )
    parser.add_argument("--create_venv", "-c",
                        default=False, required=False, action='store_true',
                        help=f"Create a virtual environment named $home/scritps/venv-{version} "
                             "by default. Will create a symlink $home/scripts/venv to point to "
                             "this virtual environment in the default case. "
                             "Symlink will not be created if --venv_path is specified.")

    parser.add_argument("--venv_path", "--venv",
                        type=str, default=None, required=False,
                        help=f"specify the path of the virtual environment to create. "
                             f"Default location is $home/scripts/venv-{version}, and symlink to $home/scripts/venv. "
                             "Specifying relative path will create named virtual environment in $home/scripts "
                             "but will NOT create the default venv symlink.")

    parser.add_argument("--destroy_venv", "--remove_venv",
                        type=str, required=False,
                        help="Remove the named python virtual environment. "
                             "May be used in conjunction with --create_venv to remove "
                             "the named virtual environment before creating a new one. "
                             "If $home/scripts/venv links to this directory, the symlink will be erased.")

    parser.add_argument("--use_python", "--python",
                        type=str, required=False,
                        help="Specify the full path of the desired version of "
                             "python to create the virtual environment with. If not specified, "
                             "the value of `which python3` from the system path will be assumed.")

    parser.add_argument("--do_pip_upgrade", "--upgrade_pip",
                        required=False, default=False, action="store_true",
                        help="The command `pip3 install --upgrade pip` will be run before the virtual environment "
                             "is created. Requires a version of python3-pip to be installed.")

    venv_detected: bool = False
    sysconfig_dir = sysconfig.get_path("stdlib")
    external_marker = pathlib.Path(f"{sysconfig_dir}/EXTERNALLY-MANAGED")
    if external_marker.is_file():
        print("PEP 668 EXTERNALLY-MANAGED detected. Testing for virtual environment...")
        if sys.prefix == sys.base_prefix:
            print("Cannot continue, pip3 commands are not in a virtual environment. "
                  "Please run this command with --create_venv parameter.")
            exit(1)
        else:
            print("Virtual environment detected, proceeding...")
            venv_detected = True
    else:
        print("PEP 668 not detected.")

    args = parser.parse_args()
    py_path = None
    upgrader = UpdateDependencies(packages=pip_packages)
    if args.use_python:
        py_path = upgrader.determine_py_path(args.use_python)
        if not py_path:
            print(f"* use_python[{args.use_python}] not found.")
            exit(1)
        print(f"Found python at {py_path}")
    else:
        py_path = upgrader.determine_py_path(sys.executable)
        if not py_path:
            print("* unable to determine python3 path, please use --use_python option")
            exit(1)

    if args.destroy_venv:
        venv_dirname = args.destroy_venv
        if not venv_dirname.startswith("/"):
            venv_dirname = f"/home/lanforge/scripts/{venv_dirname}"
        if not os.path.isdir(venv_dirname):
            print(f"* directory not found: {venv_dirname}")
            exit(1)
        venv_dir = pathlib.Path(venv_dirname)
        upgrader.remove_venv(venv_dir)

    if args.do_pip_upgrade:
        upgrader.upgrade_pip()
    else:
        print("Not upgrading pip")

    # creating a virtual environment will require
    # shelling back in and doing the install_packages() step
    if args.create_venv:
        upgrader.create_venv()
    else:
        upgrader.install_packages()

    print("...done.")


if __name__ == "__main__":
    main()
