# LANforge HTTP API Python Library

This Python library provides a set of generated methods, classes, and utilities to operate the
[LANforge HTTP API](http://www.candelatech.com/cookbook.php?vol=cli&book=JSON:+Querying+the+LANforge+Client+for+JSON+Data).
A brief overview of the HTTP API and Telnet CLI can be found [here](../README.md#lanforge-http-api-and-telnet-cli).

At a high level, this library consists of wrappers around the [LANforge CLI](https://www.candelatech.com/lfcli_ug.php),
enabling users to query and configure LANforge systems/testbeds without effort spent writing tedious boilerplate code.
Components of this library invoke the HTTP API by performing HTTP GETs and HTTP POSTs to HTTP endpoints presented
by the HTTP API. As detailed [here](../README.md#lanforge-http-api-and-telnet-cli), the HTTP API endpoints correspond
1:1 with LANforge GUI tabs. _HTTP GETs query system state_ and return JSON data. _HTTP POSTs configure system state_
and send JSON data when using this library (however, the HTTP API also supports HTTP POSTs with URL-encoded data as well).

If you are new to this API, please start at the beginning of the [LANforge Scripting Cookbook](http://www.candelatech.com/scripting_cookbook.php).
Simpler example scripts which use this library are available [here](./examples/), in addition to more complex scripts in
[`py-scripts/`](../py-scripts/).

## Requirements

- LANforge 5.4.5 or newer

- LANforge GUI active during usage of automation

  - The LANforge GUI runs the HTTP API, so it must be active in order to use most automation
  - Details on how to configure the LANforge GUI on a pre-installed system are available in [this cookbook](https://www.candelatech.com/cookbook.php?vol=misc&book=Automatically+starting+LANforge+GUI+on+login)

- LANforge Scripts/Automation Installation Setup complete
  - See the setup instructions [here](../README.md#setup-and-installation)

## Features

This Python library provides a set of generated methods, classes, and utilities to operate the
[LANforge HTTP API](http://www.candelatech.com/cookbook.php?vol=cli&book=JSON:+Querying+the+LANforge+Client+for+JSON+Data).

A brief listing of available library code is as follows:

- [`lanforge_api.py`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/lanforge_api.py)
  - Contains the core Python library including classes to configure and query LANforge systems
  - `LFSession`
    - Provides a session abstraction for querying/configuring the LANforge system
    - Additionally provides diagnostic tracing and callback IDs for specific types of CLI commands
  - `LFJsonQuery`
    - Defines HTTP GET requests to query the LANforge system
    - Available endpoints are visible by performing a GET request to the root endpoint or navigating to that endpoint in your browser
      - e.g. `http://192.168.1.101:8080/`
    - Each endpoint contains a corresponding `get_xxx()` method. For example, `/ports` can be queried by calling `get_port()`.
  - `LFJsonCommand`
    - Defines HTTP POST requests to configure the LANforge system
    - Each method corresponds to a respective CLI command
    - Helper classes define flags and types which the CLI commands require
    - For example, the [`add_sta`](http://www.candelatech.com/lfcli_ug.php#add_sta) CLI command can be configured using `post_add_sta()`.
- [`logg.py`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/logg.py)
  - `Logg` class and helper methods to configure LANforge API logging for `LFJsonQuery`s and `LFJsonCommand`s.
- [`strutil.py`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/strutil.py)
  - Helper functions for working with strings

## Intended Usage

### Suggested Workflow

Generally, the workflow for a script using LANforge API will look something like:

1. Import `lanforge_client`
2. Initiate a [`LFSession`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/lanforge_api.py#L24487)

- Ensure the script URI is directed at the manager LANforge for your testbed (should your testbed have more than one LANforge)
- Also make sure that the GUI is running. To configure the GUI to automatically start, see [this cookbook](https://www.candelatech.com/cookbook.php?vol=misc&book=Automatically+starting+LANforge+GUI+on+login) in the documentation.

3. Use a combination of [`LFJsonCommand`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/lanforge_api.py#L1392) to configure or [`LFJsonRequest`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/lanforge_api.py#L215) to query the LANforge, respectively.

### Things to Keep in Mind

This library can be used directly, plus it can be used in conjunction with the LANforge [Realm](https://github.com/greearb/lanforge-scripts/blob/master/py-json/realm.py) class. It is different than than the _Realm_ class. _Realm_ extends the [lfcli_base](https://github.com/greearb/lanforge-scripts/blob/master/py-json/LANforge/lfcli_base.py) class that provides its own (nearly identical) REST API. The lanforge*client REST methods are built into the \_BaseLFJsonRequest* class.

You would use the _Realm_ class to execute high-level operations like:

- creating groups of stations
- creating numerous connections
- reporting KPI events like test results

You would use the _lanforge_client_ package in places where:

- you want direct LANforge CLI control that hides the URLs
  - port specific flags
  - endpoint specific flags
- to get session tracking and using callback keys
- you want an API that hides the REST URLs

The Realm class is useful. As the _lanforge_client_ package stabilizes, we anticipate replacing lower level parts of the _Realm_ based operations to call into the _lanforge_client_ package.

## Getting started

**NOTE:** Example scripts are located in the [`examples/`](./examples/) directory. See the [`README.md`](./examples/README.md) for more information on available examples.

Below is an example of instantiating a LFSession object and getting the LFJsonQuery (for GETs) and LFJsonCommand (for POSTs).

```python
import lanforge_api
import lanforge_api.LFJsonCommand
import lanforge_api.LFJsonQuery

def main():
    session = lanforge_api.LFSession(lfclient_url="http://%s:8080" % args.host,
                                     debug=args.debug,
                                     connection_timeout_sec=2.0,
                                     stream_errors=True,
                                     stream_warnings=True,
                                     require_session=True,
                                     exit_on_error=True)
    command: LFJsonCommand
    command = session.get_command()
    query: LFJsonQuery
    query = session.get_query()

    command.post_rm_text_blob(p_type=args.type, name=args.name,
                              debug=args.debug, suppress_related_commands=True)
    command.post_show_text_blob(name='ALL', p_type='ALL', brief='yes')
    command.post_add_text_blob(p_type=args.type, name=args.name, text=txt_blob,
                               debug=True, suppress_related_commands=True)
    command.post_show_text_blob(name='ALL', p_type='ALL', brief='no')
    eid_str="%s.%s" % (args.type, args.name)
    print ("List of text blobs:")
    diagnostics=[]
    result = query.get_text(eid_list=eid_str, debug=True, errors_warnings=diagnostics)
    pprint.pprint(diagnostics)
    pprint.pprint(result)

```
