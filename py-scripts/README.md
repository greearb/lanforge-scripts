# LANforge Python Scripts
This directory contains Python scripts to configure and test devices with LANforge traffic generation and network impairment systems.

For more information, see the following online documentation or email [`support@candelatech.com`](mailto:support@candelatech.com) with questions.
* [LANforge Scripting Cookbook](http://www.candelatech.com/scripting_cookbook.php)
* [Querying the LANforge JSON API using Python Cookbook](https://www.candelatech.com/cookbook/cli/json-python)


## Setup
**NOTE: LANforge Python scripts require Python 3.7+** (which is backwards compatible to Fedora 27 systems).

There are two primary methods to access LANforge scripts (either for use or development):

1. [LANforge system with the scripts pre-installed](#pre-installed-lanforge-system-usage)

2. [Cloning or downloading the scripts from the Git repository](#cloning-from-git-repository-usage) (repository linked [here](https://github.com/greearb/lanforge-scripts))

### Pre-installed LANforge System Usage
On pre-installed LANforge systems, LANforge scripts are installed in `/home/lanforge/scripts/py-scripts/`. No further setup is required (dependencies come pre-installed). These pre-installed scripts match the LANforge software version on the system.

### Cloning from Git Repository Usage
**NOTE:** This process is generally for more advanced users or developers. However, customers under support may email [`support@candelatech.com`](mailto:support@candelatech.com) with any questions, and we can guide you through.

For users who clone or download these scripts from the Git repo, some setup is required.

We assume you are familiar with the command line (e.g. `bash`) and already have both Python and Git installed (recall that Python 3.7 is the minimum supported version).

Please complete the following two steps before running LANforge scripts on a non-LANforge system (outlined in this [section](#setup-instructions)):
1. Ensure that the LANforge scripts version cloned matches your LANforge system version
   - It is possible to run with the latest version, but this is not recommended
2. Install the required LANforge scripts dependencies
   - We strongly suggest virtual environments (e.g. `virtualenv`) to avoid possible dependency issues. This is common practice when working with Python projects.

#### Setup Instructions

**NOTE:** Developers and anyone looking to contribute to LANforge scripts should also familiarize themselves with the information outlined in the [`CONBTRIBUTING.md` document](../CONTRIBUTING.md).

1. Open a shell and clone LANforge scripts

    ```Bash
    git clone https://github.com/greearb/lanforge-scripts
    ```

2. Get the version-tagged commits of the repository

    ```Bash
    git fetch --tags
    ```

3. List the version-tagged commits available

    ```Bash
    git tag
    ```

4. Select the matching tag for your LANforge system's version

    ```Bash
    # Checkout LANforge 5.4.7 version of LANforge scripts.
    git checkout lf-5.4.7
    ```

5. Create and source a Python virtual environment (optional but **strongly suggested**)

    We suggest Python's [builtin virtual environment tool](https://docs.python.org/3/tutorial/venv.html) for simplicity, although other tools requiring more configuration like [Anaconda](https://anaconda.org/) will work as well.

    ```Bash
    # Create Python virtual environment named 'venv'
    virtualenv venv

    # Enter the Python virtual environment (Linux)
    source venv/bin/activate
    ```

6. Enter the `lanforge-scripts/py-scripts/` directory

7. Run the dependency installation script

    ```Bash
    ./update_dependencies.py
    ```

Once you have successfully completed these steps, you can now use the LANforge Python scripts.


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
On Linux, you must explicitly allow users to access serial devices. Otherwise, using a USB serial device requires root permissions (e.g. have to use `sudo`).

There are several methods to do so, each depending on the distribution (all requiring root access to the system). Often the easiest is to perform the following:

1. Add your user to the `dialout` and `tty` groups

    ```Bash
    sudo usermod -a -G dialout,tty $USER
    ```

2. Log out and log back in (full logout required, not just closing the terminal)

    - Can also run the `newgrp` command, but this will only affect the currently running login session (i.e. that shell)
