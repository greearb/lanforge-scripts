# LANforge Python Scripts
This directory contains Python scripts to configure and test devices with LANforge Traffic Generators.

For more information, see the following online documentation or email [`support@candelatech.com`](mailto:support@candelatech.com) with questions.
* [LANforge Scripting Cookbook](http://www.candelatech.com/scripting_cookbook.php)
* [Querying the LANforge JSON API using Python Cookbook](https://www.candelatech.com/cookbook/cli/json-python)


## Setup
**NOTE: LANforge Python scripts require Python 3.7+** (which is backwards compatible to Fedora 27 systems).

There are two primary methods to use LANforge scripts, on a LANforge system with the scripts pre-installed or by cloning the scripts from the Git repo.

### Pre-installed LANforge System Usage
For pre-installed LANforge systems, these scripts are installed in `/home/lanforge/scripts/py-scripts/` and require no further setup (dependencies are pre-installed as well). These pre-installed scripts match the LANforge software version on the system.

### Cloning from Git Repository Usage
For users who clone these scripts from the Git repo, some setup is required.

First, ensure that the LANforge scripts version you cloned matches that of your LANforge system (it is possible to run with the latest version, but this is not recommended). You can do this by doing the following:
1. Get the version-tagged commits of the repository: `git fetch --tags`
2. List the version-tagged commits available: `git tag`
3. Selecting the matching tag for your LANforge system's version by running `git checkout`, e.g. `git checkout lf-5.4.7` to select the LANforge 5.4.7 version of LANforge scripts.

Next, run the `update_dependencies.py` script to install the required script dependencies. We recommend doing so within a Python virtual environment using a tool like [`venv`](https://docs.python.org/3/tutorial/venv.html). This will isolate LANforge script dependencies from other software on your system's dependencies.

Once you have completed dependency installation, you can now use the LANforge Python scripts.


## Using LANforge Python Scripts

There are many scripts available within not just the LANforge Python scripts but the entire LANforge scripts repository. While we recognize and continue to address documenting these scripts, this section details some information that may be useful when using these scripts.

To learn more about what a script does, most scripts support a `--help_summary` option which prints a short summary detailing what the script does. All scripts support a `--help` option which prints all arguments supported by a given script.

To learn more about automating Chamber View tests like TR-398, WiFi Capacity Test, and others, see the [Chamber View Examples](./cv_examples/README.md) subdirectory for more information.

### LANforge Python Scripts in py-scripts General Classifications

* create_ - creates network element in LANforge wiphy radio
* lf_ or test_ - performs a test against an Access Point or Wifi network
* other files  are various utilities

## LANforge Python Scripts Directory Structure
* py-scripts - configuration, unit test, module, and library scripts
* cv_examples - bash scripts for ochastrating Chamberview tests 
* py-json - core libraries providing direct intraction with LANforge Traffic Generator
* py-json/LANforge - JSON intraction with LANforge Traffic Generator.
* lanforge_client/ - alpha version of JSON interface to LANforge Traffic Generator.

## Scripts accessing Serial ports. 
* to access serial ports add user to `dialout` and `tty` groups to gain access to serial ports without needing root access.
* Most scripts run in user space to use the installed python package and not affect the os python packages.