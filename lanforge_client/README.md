# LANforge API Python Library

---

This library provides a set of methods to operate the [LANforge JSON REST API](http://www.candelatech.com/cookbook.php?vol=cli&book=JSON:+Querying+the+LANforge+Client+for+JSON+Data). This is a generated library that includes Python classes and methods to perform JSON POSTs for every [LANforge CLI command](https://www.candelatech.com/lfcli_ug.php) and JSON GETs for JSON endpoints presented by the LANforge GUI.

If you are new to this API, please start at the beginning of the [LANforge Scripting Cookbook](http://www.candelatech.com/scripting_cookbook.php). 

## Requirements

**NOTE:** Most users also run scripts in [`lanforge-scripts/py-scripts/`](https://github.com/greearb/lanforge-scripts/tree/master/py-scripts), so make sure to follow the [setup instructions](https://github.com/greearb/lanforge-scripts/blob/master/py-scripts/README.md#setup) to use them.

- Minimum LANforge GUI 5.4.5
  - As the GUI runs the JSON API, you must ensure that the GUI is running when using the JSON API
  - To configure the GUI to automatically start, see [this cookbook](https://www.candelatech.com/cookbook.php?vol=misc&book=Automatically+starting+LANforge+GUI+on+login) in the documentation.
- Minimum Python 3.7
  - This library is tested on systems which run Python 3.7+ or newer, including LANforge systems Fedora 30+, as they ship with Python 3.7 or newer
    - We discourage operation on earlier releases of Fedora (e.g. Fedora 27)

## Features

The **lanforge_client** package contains Python library code to query and configure LANforge systems in addition to utility and logging methods.

A brief listing of available library code is as follows:

- [`lanforge_api.py`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/lanforge_api.py)
  - Contains the core Python library including classes to configure and query LANforge systems
  - [`LFSession`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/lanforge_api.py#L24487)
    - Provides a session abstraction for querying/configuring the LANforge system
    - Additionally provides diagnostic tracing and callback IDs for specific types of CLI commands
  - [`LFJsonQuery`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/lanforge_api.py#L19610)
    - Defines GET requests to query the LANforge system
    - Available endpoints are visible by performing a GET request to the root endpoint or navigating to that endpoint in your browser
      - e.g. `http://192.168.1.101:8080/`
    - Each endpoint contains a corresponding `get_xxx()` method. For example, `/ports` can be queried by calling the [`get_port()`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/lanforge_api.py#L22141) method.
  - [`LFJsonCommand`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/lanforge_api.py#L1392)
    - Defines POST requests to configure the LANforge system
    - Each method corresponds to a respective CLI command
    - Helper classes define flags and types which the CLI commands require
    - For example, the [`add_sta`](http://www.candelatech.com/lfcli_ug.php#add_sta) CLI command can be configured using the [`post_add_sta()`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/lanforge_api.py#L4770) method.
- [`logg.py`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/logg.py)
  - [`Logg`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/logg.py#L17) class and helper methods to configure LANforge API logging for [`LFJsonQuery`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/lanforge_api.py#L19610)s and [`LFJsonCommand`](https://github.com/greearb/lanforge-scripts/blob/master/lanforge_client/lanforge_api.py#L1392)s.
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
This library can be used directly, plus it can be used in conjunction with the LANforge [Realm](https://github.com/greearb/lanforge-scripts/blob/master/py-json/realm.py) class. It is different than than the *Realm* class. *Realm* extends the [lfcli_base](https://github.com/greearb/lanforge-scripts/blob/master/py-json/LANforge/lfcli_base.py) class that provides its own (nearly identical) REST API. The lanforge_client REST methods are built into the *BaseLFJsonRequest* class. 

You would use the *Realm* class to execute high-level operations like:

* creating groups of stations
* creating numerous connections
* reporting KPI events like test results

You would use the *lanforge_client* package in places where:

* you want direct LANforge CLI control that hides the URLs
  * port specific flags
  * endpoint specific flags
* to get session tracking and using callback keys
* you want an API that hides the REST URLs

The Realm class is useful. As the *lanforge_client* package stabilizes, we anticipate replacing lower level parts of the *Realm* based operations to call into the *lanforge_client* package.

## Getting started

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

