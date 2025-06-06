#!/usr/bin/env python3
# flake8: noqa
import argparse
import os
import os.path
import pathlib
import sys
import sysconfig
from subprocess import PIPE, call, run

"""
List of packages
"""
pip_packages: list = [
    'dlipower',
    'setuptools',
    'cryptography',
    'kaleido',
    'matplotlib',
    'numpy',
    'pandas',
    'paramiko',
    'pdfkit',
    'pexpect',
    'pexpect-serial',
    'plotly',
    'psutil',
    'pyserial',
    'pyshark',
    'requests',
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
        # self.venv_activate: str = f"{self.venv_path}/bin/activate"
        self.py = "python3"
        if os.name == "nt":
            self.venv_path = f"{self.scripts_path}\\venv-{self.py_version}"
            # self.venv_activate = f"{self.venv_path}\\bin\\activate.bat"
            self.py = "py.exe"

    @staticmethod
    def venv_detected():
        return sys.prefix != sys.base_prefix

    def upgrade_pip(self):
        print("Upgrading pip...")
        try:
            # this call (on fedora) very likely needs to be done thru sudo
            call('sudo -S pip3 install --upgrade pip', shell=True)
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
                self.system_python_path = run(["where", "py.exe"], shell=True, check=True, stdout=PIPE,
                                              stderr=sys.stderr,
                                              timeout=1).stdout.decode('UTF-8').rstrip()
            else:
                self.system_python_path = run(["which", "python3"], stdout=PIPE, timeout=1,
                                              stderr=sys.stderr).stdout.decode(
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
                if os.name == "nt" and pathlib.Path(f"{possible_path}/{self.py}").is_file():
                    self.chosen_python_path = f"{possible_path}\\{self.py}"
                elif pathlib.Path(f"{possible_path}/python3").is_file():
                    self.chosen_python_path = f"{possible_path}/{self.py}"
            else:
                print(f"* Unable to find python at {possible_path}")
                exit(1)
        except Exception as e:
            print(e)
            exit(1)

    def get_venv_path(self):
        return self.venv_path

    def get_venv_activate(self):
        if os.name == "nt":
            return f"{self.venv_path}\\bin\\activate.bat"
        return f"{self.venv_path}/bin/activate"

    def remove_venv(self, venv_directory: pathlib.Path = None):
        """
        Check to see if the venv_directory has a bin/activate file. If so,
        remove the directory. This method does not refer to self.venv_path because
        self.venv_path refers to the creation target.
        :param venv_directory:  containing virtual environment
        :return: False if unable to find directory
        """
        has_bin_activate = False
        if venv_directory and venv_directory.is_dir():
            if os.name == 'nt':
                if os.path.isfile(f"{venv_directory}\\bin\\activate.bat"):
                    print(f"Removing {venv_directory}...")
                    res = call(f"rmdir {venv_directory} /s /q", stderr=sys.stderr, stdout=sys.stdout, shell=True)
                    return res == 0
                else:
                    print(f"* Not removing {venv_directory}, bin\\activate.bat not found.")
                    return False
            else:
                if os.path.isfile(f"{venv_directory}/bin/activate"):
                    print(f"Removing {venv_directory}...")
                    res = call(f"rm -rf {venv_directory}", stderr=sys.stderr, stdout=sys.stdout, shell=True)
                    return res == 0
                else:
                    print(f"* Not removing {venv_directory}, bin/activate not found.")
                    return False
        else:
            print(f"* Directory does not exist: {venv_directory}")
            exit(1)

    def create_venv(self):
        """Create a virtual environment. Tests for bin/activate first and does not attempt to recreate it.
        """
        if not (self.venv_path.startswith("/") or self.venv_path.startswith("C:")):
            raise Exception("self.venv_path needs to be a fully qualified path")

        print(f"Checking for venv at {self.venv_path}...")
        if not os.path.isfile(self.get_venv_activate()):
            print(f"Creating a python virtual environment at [{self.venv_path}]...")
            proc = run([self.py, "-m", "venv", self.venv_path], stdout=PIPE, stderr=PIPE)
            if proc.returncode == 0:
                # double check
                if os.path.isfile(self.get_venv_activate()):
                    print("...created")
                else:
                    raise Exception("venv finished but no bin/activate found")
            else:
                print(proc.stdout.decode('UTF-8'))
                print(proc.stderr.decode('UTF-8'))
                print("* unable to proceed")
                exit(1)

        # enter the venv and install packages
        print("Entering venv and installing packages...")
        proc = run(f"""bash -c ". {self.get_venv_activate()} && {__file__} --venv_path {self.venv_path}" """,
                   stdout=sys.stdout,
                   stderr=sys.stderr,
                   shell=True)
        if proc.returncode == 0:
            print("...installed")
        else:
            print(proc.stdout.decode('UTF-8'))
            print(proc.stderr.decode('UTF-8'))
            print("* failed to install packages")
            exit(1)

    def make_symlink(self, source):
        if not (source.startswith("/") or source.startswith("C:")):
            raise Exception("symlink requires full path")
        if os.path.islink(f"{self.scripts_path}/venv"):
            print("Found default venv link. Removing...")
            os.unlink(f"{self.scripts_path}/venv")
        print(f"Symlinking {source} -> {self.scripts_path}/venv")
        os.symlink(source, f"{self.scripts_path}/venv")

    def install_pkg(self, package: str):
        if os.name == 'nt':
            command = f"{self.py} -m pip install {package}"
        else:
            command = f"pip3 install {package} >/tmp/pip3-stdout 2>/tmp/pip3-stderr"
        print(" ", end="", flush=True)
        res = call(command, shell=True)
        if res == 0:
            print(f"✔", end=" ", flush=True)
            self.packages_installed.append(package)
        else:
            print(f"✘", end=" ", flush=True)
            self.packages_failed.append(package)

    def install_packages(self):
        """Use subprocess.call  commands to pip3 install packages without a virtual environment
        """
        print("Upgrading packages:", end=" ", flush=True)
        for package in self.packages:
            self.install_pkg(package=package)

        print("\nInstall complete.")
        print(f"Successfully installed : {self.packages_installed}\n")
        if not self.packages_failed:
            return
        print(f"Failed to install: {self.packages_failed}\n"
              + "(Some scripts may not need these packages) "
              + "To see errors try: pip3 install $package", flush=True)


def main():
    upgrader = UpdateDependencies(packages=pip_packages)
    version = upgrader.py_version

    help_summary = f'''\
The lanforge-scripts/py-scripts and lanforge-scripts/py-json collection require
a number of Pypi libraries. This script installs those libraries or creates
a virtual environment for those libraries. This script has been updated to
detect PEP 668 externally-managed libraries; in the presence of the externally-managed
condition, a virtual environment will be created in $home/scripts/venv-${version}.
This script will update a symlink $home/lanforge/venv to default virtual environment
as necessary.'''

    parser = argparse.ArgumentParser(
        prog="update_dependencies.py",
        formatter_class=argparse.RawTextHelpFormatter,
        description="NAME: update_dependencies.py\n"
                    "PURPOSE:  Installs python3 script package dependencies\n"
                    "OUTPUT: List of successful and unsuccessful installs\n"
                    "NOTES: Run this as lanforge user (not root)\n\n"
                    f"{help_summary}",
        epilog="Examples:\n"
               "* Install on Fedora:\n"
               "    ./update_dependencies.py\n"
               "* Install on Python 3.11+ Externally Managed system:\n"
               "    ./update_dependencies.py --create_venv\n"
               "    (This creates a symlink at /home/lanforge/scripts/venv)\n"
               "* Install venv with a name:\n"
               "    ./update_dependencies.py --create_venv --venv_path v311\n"
               "* Install venv to a specific directory:\n"
               "    ./update_dependencies.py --create_venv --venv_path /usr/local/venvs/lf548"
               "* Remove a venv and stop:\n"
               "    ./update_dependencies.py --destroy_venv v311 --only_remove\n"
               "* Re-create the default virtual environment:\n"
               "    ./update_dependencies.py --destroy_venv --create_venv"
               "* Upgrade system pip3 (use when there are permission errors):\n"
               "    ./update_dependencies.py --upgrade_pip\n"
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
                        type=str, required=False, const=upgrader.venv_path, nargs='?',
                        help="Remove the named python virtual environment. "
                             "May be used in conjunction with --create_venv to remove "
                             "the named virtual environment before creating a new one. "
                             "If $home/scripts/venv links to this directory, the symlink will be erased.")

    parser.add_argument("--only_remove", "--remove_only",
                        default=False, action="store_true",
                        help="Stop after removing virtual environment. Use with --destroy_venv. "
                             "Will not upgrade pip. Will remove default symlink if it matches.")

    parser.add_argument("--use_python", "--python",
                        type=str, required=False,
                        help="Specify the full path of the desired version of "
                             "python to create the virtual environment with. If not specified, "
                             "the value of `which python3` from the system path will be assumed.")

    parser.add_argument("--symlink", "--link",
                        default=False, action="store_true",
                        help="Creates a symlink to the created virtual environment. Use with --create_venv. "
                             "If no venv path or python version is explicitly listed, then this defaults to True. "
                             "When a python path or named venv is provided, no symlink will be created by default. "
                             "This option forces a symlink $home/scripts/venv to be created.")

    parser.add_argument("--no_symlink", "--nosymlink", "--nolink",
                        default=False, action="store_true",
                        help="Do not create the $home/scripts/venv symlink.")

    parser.add_argument("--do_pip_upgrade", "--upgrade_pip",
                        required=False, default=False, action="store_true",
                        help="The command `sudo pip3 install --upgrade pip` will be run before the virtual "
                             "environment is created. Requires a version of python3-pip to be installed. "
                             "This option will help if pip is installed but packages fail with permission errors. "
                             "Do not use this option in PEP 668 externally managed environments.")

    # help summary
    parser.add_argument('--help_summary',
                        default=None,
                        action="store_true",
                        help='Show summary of what this script does')


    args = parser.parse_args()
    if args.help_summary:
        print(help_summary)
        exit(0)

    py_path = None
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

    if args.only_remove and not args.destroy_venv:
        print("* --only_remove requires --destroy_venv")
        exit(1)
    if args.destroy_venv:
        venv_dirname = args.destroy_venv
        if not venv_dirname.startswith("/"):
            venv_dirname = f"{upgrader.scripts_path}/{venv_dirname}"
        if not os.path.isdir(venv_dirname):
            print(f"* directory not found: {venv_dirname}")
            exit(1)
        venv_dir = pathlib.Path(venv_dirname)
        print(f"Will delete {venv_dirname}...")
        upgrader.remove_venv(venv_dir)
        if args.only_remove:
            print("Only removing virtual environment: done.")
            exit(0)
    else:
        print("Not deleting venv.")

    if args.do_pip_upgrade:
        if upgrader.venv_detected():
            print("* Cannot upgrade pip in a externally managed environment.")
        else:
            upgrader.upgrade_pip()
    else:
        print("Not upgrading pip")

    # creating a virtual environment will require
    # shelling back in and doing the install_packages() step
    if args.venv_path:
        if not (args.venv_path.startswith('/') or args.venv_path.startswith('C:')):
            if os.name == "nt":
                upgrader.venv_path = f"{upgrader.scripts_path}\\{args.venv_path}"
            else:
                upgrader.venv_path = f"{upgrader.scripts_path}/{args.venv_path}"
        else:
            upgrader.venv_path = args.venv_path
        print(f"Set venv path to [{upgrader.venv_path}]")

    if upgrader.venv_detected():
        print("Virtual environment detected.")
    if args.create_venv and not upgrader.venv_detected():
        upgrader.create_venv()
        print("...created venv")
    elif upgrader.venv_detected():
        print(f"Installing packages to venv {upgrader.venv_path}...")
        upgrader.install_packages()
        exit(0)
    else:
        print(f"Installing packages to system scope...")
        sysconfig_dir = sysconfig.get_path("stdlib")
        external_marker = pathlib.Path(f"{sysconfig_dir}/EXTERNALLY-MANAGED")
        if external_marker.is_file():
            print("PEP 668 EXTERNALLY-MANAGED detected. Testing for virtual environment...")
            if not upgrader.venv_detected():
                print("Cannot continue, pip3 commands are not in a virtual environment. "
                      "Please run this command with --create_venv parameter.\n"
                      f"Called as: {sys.argv}")
                exit(1)
        else:
            print("PEP 668 not detected.")
            upgrader.install_packages()

    if args.no_symlink or (not args.create_venv):
        print("Not creating symlink.")
        exit(0)

    make_symlink = args.symlink or (args.create_venv and not args.venv_path)
    if make_symlink:
        upgrader.make_symlink(upgrader.venv_path)


if __name__ == "__main__":
    main()
