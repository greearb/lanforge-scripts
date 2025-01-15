# Chamber View Automation Examples

## Overview

**The examples in this directory demonstrate how to use LANforge scripts to automate Chamber View tests.**

The Chamber View test suite is a well-utilized LANforge feature. Primarily focused on WiFi, these tests enable users to consistently and easily test their DUT WiFi equipment in a variety of scenarios. In addition to real-time test visualization, these tests also generate comprehensive reports and CSV data for later reference.

While a user can manually configure a test to their liking, save the database, and then re-run the exact same test, automated test invocation saves time and reduces potential for errors. LANforge offers a variety of scripts which can meet this goal, especially when used together. **However, it can be difficult to determine what scripts to use and how exactly to use them. This document and associated examples demonstrate how to do just that.**

## Example Test Automation

| Chamber View Test     | Automation Script                                                                  |
| --------------------- | ---------------------------------------------------------------------------------- |
| AP-Auto               | [`AP-Auto.bash`](./AP-Auto/AP-Auto.bash)                                           |
| Continuous Throughput | [`Continuous_Throughput.bash`](./Continuous_Throughput/Continuous_Throughput.bash) |
| Dataplane             | [`Dataplane.bash`](./Dataplane/Dataplane.bash)                                     |
| Rate vs Range         | [`Rate_vs_Range.bash`](./Rate_vs_Range/Rate_vs_Range.bash)                         |
| TR-398 Issue 2        | [`TR-398_Issue_2.bash`](./TR-398_Issue_2/TR-398_Issue_2.bash)                      |
| TR-398 Issue 4        | [`TR-398_Issue_4.bash`](./TR-398_Issue_4/TR-398_Issue_4.bash)                      |
| WiFi Capacity         | [`WiFi_Capacity.bash`](./WiFi_Capacity/WiFi_Capacity.bash)                         |

## Automating Chamber View in Your Testbed

As your use case for a given Chamber View test will be different than the examples shown, you will inevitably craft and adjust your automation scripts as your goals evolve. **To customize your scripts, we suggest the following workflow, which was used to create the examples in this directory.**

### Step 1: Manual Setup

In order to automate your Chamber View testing, you must first manually configure the test scenario.

#### 1. Create a DUT under the 'DUT' GUI tab

- The minimum DUT configuration required to run any meaningful Chamber View tests is:
  - DUT Name
  - At least one SSID with relevant authentication parameters
- We suggest specifying AP BSSIDs per SSID and enabling 'Provides DHCP on LAN', should these options be relevant.
  - Setting specific AP BSSIDs enables STAs created in Chamber View Scenarios to associate to only the selected BSSIDs (more info in next step).
  - Enabling 'Provides DHCP on LAN' similarly allows LAN upstream ports to automatically enable DHCP on bringup.

#### 2. Manually Create and Build a Chamber View Scenario

Specific configuration will depend on the test you're configuring, but generally we suggest configuring an upstream which maps to your DUT.

See [Chamber View Scenarios (and Test Assumptions)](#chamber-view-scenarios-and-test-assumptions) for more information on configuring Chamber View Scenarios.

#### 3. Manually configure your Chamber View test as desired in the GUI

**NOTE:** Make sure to enable options like 'Auto Save Report' and 'Collect CSV Data', should those options be relevant.

Specific configuration depends on the test you're configuring, but generally you should configure and run the test to verify that your configuration (both in software and physically) works as you expect.

#### 4. Save the LANforge Configuration

As you will likely need this configuration in the future, be it exactly or as a fallback, we suggest you save the current configuration in a new database.

1. Navigate to the 'Status' tab.
2. In the top right corner, use the 'Saved Test Configurations' section to save a new database.
   - You can reset to this configuration by selecting a saved configuration and clicking 'Load'.
   - **NOTE:** Loading a database will overwrite any existing configuration on the testbed.

### Step 2: Scripting Setup

#### 1. Transfer the test configuration to your script

**NOTE:** Do not transfer TR-398 test configuration between testbeds. Calibration data for your testbed is stored in the configuration, so transferring configuration from one testbed to another will overwrite the receiving testbed's calibration.

1. In your working, manually-configured Chamber View test, navigate to the 'Advanced Configuration' tab of the Chamber View test.
2. Click 'Show Config'
   - A pop-up window with configuration data will appear.
3. Select the entire config (Ctrl-A) and copy it to your clipboard (Ctrl-C).
4. Navigate to the where you will keep your test configs (e.g. to a directory on the LANforge system).
5. Open a new file in your preferred text editor and paste the contents (the test config) to the new file.

#### 2. Adjust the script to reflect your configured Chamber View Scenario

1. Navigate to 'Chamber View' by selecting the 'Chamber View' button at the top of the main LANforge GUI.
2. In the top right of the 'Chamber View' GUI under the 'Manage Scenarios' button, select the Chamber View Scenario for your test that you configured previously.
3. With the desired scenario selected, click 'Manage Scenarios'.
4. In the pop-up 'Create/Modify Scenario' GUI, click the 'Text Output' tab.
5. For each line in the 'Text Output' box, enter the text into a `--raw_line` option where your script invokes the `create_chamberview.py` script.
   - See the [example scripts](#chamber-view-automation-examples) for example usage.

#### 3. Adjust the script to reference the new test configuration

**NOTE:** If you specify an option on the command line that is different from the configuration file, the command line argument will take precedent.

- Depending on how you wrote your script, this may be by changing the command line arguments you invoke the script with or adjusting variables within the script.
  - Scripting examples here use environment variables set at the top of the script to configure the arguments passed to each script.
- If using an example script, adjust the `TEST_CFG` variable to point to your config file.

#### 4. Repeat as you adjust your Chamber View Scenario and Chamber View test configuration

- Any time you adjust the Chamber View test configuration in the GUI, repeat the [transfer the test configuration](#1-transfer-the-test-configuration-to-your-script), the [reflect the scenario](#2-adjust-the-script-to-reflect-your-configured-chamber-view-scenario), and [reference the configuration](#3-adjust-the-script-to-reference-the-new-test-configuration) steps to transfer the test configuration to your script. If you do not, the script will not use the changes you made.

## Chamber View Scenarios (and Test Assumptions)

### Overview

Chamber View and Chamber View Scenarios generally aim to make the process of running complex and/or large-scale tests easier. Rather than configure the testbed by hand for every test run, Chamber View allows a user to reproduce a test consistently and easily.

Chamber View Scenarios play a key role in this process of reproducible tests. Where a Chamber View test can be considered the process of making a recipe, a Chamber View Scenario would be the ingredients list, something gathered and prepared before cooking.

Just as a recipe assumes specific ingredient preparation, each Chamber View test assumes specific testbed configuration. Some Chamber View tests like 'WiFi Capacity' test assume the testbed is fully configured before test invocation. Other tests like the TR-398 suite assume some pre-configuration but do some of their own configuration as well. **All tests assume some configuration, though. That configuration is a Chamber View Scenario.**

**The following is configuration assumed by all Chamber View tests:**

- DUT configured as desired (including as a DUT object in LANforge)
- A LANforge port configured as an 'Upstream' profile in a Chamber View Scenario
- The Chamber View Scenario is applied and built successfully

### Chamber View Scenarios In Automation Scripts

The general workflow for configuring a scripted Chamber View test (and manual test) is as follows:

1. Create DUT
2. Create and build Chamber View Scenario
3. Run the Chamber View test

For more detail, see the [Automating Chamber View in Your Testbed](#automating-chamber-view-in-your-testbed) section.
