#!/usr/bin/env python3

"""
NAME:       http_regression_test/comparators.py

PURPOSE:    A collection of comparators extended from a base endpoint Comparator class. Each comparator is
            responsible for comparing the results for a given http endpoint.

            Each comparator class must register which endpoint(s) it is capable of comparing, which allows
            responses from a given test iteration to be dispatched to the correct comparator.
"""

import traceback
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING, List, Optional, Union
if TYPE_CHECKING:
    from http_regression import Response


class Result():
    def __init__(self, messages: Optional[List[str]] = None):
        self._messages = messages or []
        self.key = -1

    def __or__(self, other: 'Result') -> 'Result':
        result_type: type = type(self) if (self.key > other.key) else type(other)
        new_result: Result = result_type()

        new_result._messages.extend(self._messages)
        new_result._messages.extend(other._messages)

        return new_result

    @property
    def message(self):
        return "\n".join(self._messages)


class Success(Result):
    def __init__(self):
        super().__init__()
        self.key = 0


class Warning(Result):
    def __init__(self, message: Optional[str] = None):
        super().__init__()
        self.key = 1

        if message is not None:
            self._messages.append(f"(warning) {message}")


class Failure(Result):
    def __init__(self, message: Optional[str] = None):
        super().__init__()
        self.key = 1

        if message is not None:
            self._messages.append(f"(failure) {message}")

#
# Comparator Base Class
#


class Comparator(ABC):
    """
    An abstract class containing a compare() method, which compares results
    for a particular REST endpoint.
    """

    def __init__(self, host: str, response_ver: str, baseline_ver: str):
        self.host = host
        self.response_ver = response_ver
        self.baseline_ver = baseline_ver

    comparator_mappings: Optional[dict] = None

    @classmethod
    def fetch_comparator_cls(cls, endpoint: str) -> type:
        if cls.comparator_mappings is None:
            cls._populate_comparator_mappings()

        return cls.comparator_mappings[endpoint]

    @classmethod
    def _populate_comparator_mappings(cls) -> None:
        cls.comparator_mappings = {}
        for comparator_cls in Comparator.__subclasses__():
            endpoints: List[str] = comparator_cls.handles_endpoints()

            duplicate_keys = [k for k in endpoints if k in cls.comparator_mappings]
            if len(duplicate_keys) > 0:
                msg = f"Attempted to register {duplicate_keys[0]} for {comparator_cls.__name__}, " + \
                      f"which is already registered for {cls.comparator_mappings[duplicate_keys[0]].__name__}" + \
                      (f" (and {len(duplicate_keys) - 1} more conflicts)" if len(duplicate_keys) > 1 else "")
                raise ValueError(msg)

            cls.comparator_mappings.update({
                endpoint: comparator_cls for endpoint in endpoints
            })

    @staticmethod
    @abstractmethod
    def handles_endpoints() -> List[str]:
        """Returns a list of endpoints that the current comparator class is
        capable of handling. Used for dispatching comparison tasks to the
        correct Comparator class"""

        pass

    def compare(self, response: 'Response', reference: 'Response') -> Result:
        try:
            return self._compare(response, reference)
        except Exception:
            return Failure(f"Exception in {type(self).__name__}: {traceback.format_exc()}")

    @abstractmethod
    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        """Compare the given response to the given reference baseline response.
        Both response and reference are dictionaries of json-structured date
        representing the response of a LANforge REST AI endpoint to a single
        query. """
        pass


#
# Helpers
#
def zip_json(a_val, b_val) -> Union[tuple, dict, list]:
    """
    Given two json-structured objects (list or dict), fold them together such
    that every leaf-element with matching keys/indices is a tuple of (a_value, b_value).
    Values that are dict or list will be recursively zipped together.
    """
    if isinstance(a_val, list) and isinstance(b_val, list):
        value = _zip_list(a_val, b_val)

    elif isinstance(a_val, dict) and isinstance(b_val, dict):
        value = _zip_dict(a_val, b_val)

    else:
        value = (a_val, b_val)

    return value


def _zip_list(a: list, b: list) -> list:
    """Helper for zip_json that handles list elements"""

    if len(a) < len(b):
        a += [None] - (len(b) - len(a))
    if len(b) < len(b):
        b += [None] - (len(a) - len(b))

    return [
        zip_json(a_val, b_val)
        for a_val, b_val in zip(a, b)
    ]


def _zip_dict(a: dict, b: dict) -> dict:
    keys = set(a.keys() | b.keys())

    return {
        k: zip_json(a.get(k, None), b.get(k, None))
        for k in keys
    }


def check_tolerance(value1, value2, tol=0.2) -> bool:
    """Check if value 1 is within tol*value2 of value2"""
    return value2*(1-tol) <= value1 <= value2*(1+tol)


def mismatch_message(name, value1, value2):
    return f"Value of '{name}' ({value1}) does not match expected value ({value2})."


def tolerance_message(name, value1, value2):
    return f"Value of '{name}' ({value1}) is not within the expected tolerances of {value2}."


def mismatch_type_message(name, value1, value2):
    return f"Type of '{name}' ({value1}: {type(value1)}) does not match expected type ({value2}: {type(value2)})."


#
# Concrete Comparator Implementations
#

# The NotImplemented classes that

class DatabaseComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["database", "databases", "db"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class MloComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["mlo"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class RfgenComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["rfgen"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class AdbComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["adb"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class AdvancedPortStatsComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["wifi-stats"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class PortProbeComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["portprobe", "probe"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class AttenuatorComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["atten", "attenuator", "attenuators"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class CxGroupsComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["cxg", "cx-group", "cxgroup", "cx-groups", "cxgroups", "test-group",
                "testgroup", "test-groups", "testgroups", "tg"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class VrComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["virtual-routers", "virtualrouters", "vr"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class VrCxComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["vr-cx", "vrcx"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class VoipComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["voip"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class VoipEndpComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["voip-endp"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class StationScanComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["scan", "scan-results", "scanresults"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class FileIOComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["fileio"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class StationsComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["stations"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class GuiCliComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["gui-cli", "gui_cli", "gui-cli", "gui-cmd", "gui_cmd", "gui-json", "gui_json"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class ChamberComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["chamber", "chambers"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class WlEndpComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["wl-endp", "wl_endp", "wlendp", "wl-ep", "wl_ep"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class WlComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["wl"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class ArmageddonComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["arm", "arm", "arm-endp", "arm-endp"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class GenericEndpComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["generic"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class DUTComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["dut"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class ProfilesComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["profile", "profiles"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class L4Comparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["layer4"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class RadioReportComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["radiostatus"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class CxComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["cx"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class EventsComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["alerts", "events"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class WifiMsgsComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["wifi-msgs"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class TextBlobsComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["text"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class PortComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["port", "ports"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class EndpComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["endp"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class ResourceComparator(Comparator):

    all_known_keys = [
        "app-id", "bps-rx-3s", "bps-tx-3s", "build date", "cli-port", "cpu", "ct-kernel", "ctrl-ip",
        "ctrl-port", "device type", "df-boot", "df-home", "df-root", "eid", "entity id", "free mem",
        "free swap", "gps", "hostname", "hw version", "kernel", "load", "max if-up", "max staged",
        "mem", "phantom", "ports", "rf-path", "rx bytes", "shelf", "sta up", "swap", "sw version",
        "tx bytes", "user", "_links",
    ]

    exact_match_keys = [
        "app-id", "cli-port", "cpu", "ct-kernel", "ctrl-ip", "ctrl-port", "device type", "eid", "entity id",
        "gps", "hostname", "hw version", "max if-up", "max staged", "phantom", "ports", "rf-path", "shelf",
        "user", "_links",
    ]

    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["shelf", "resource"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        result = Success()

        if response is None:
            if reference is not None:
                return Failure("Response has no value")
            else:
                return Success()

        if response.status != reference.status:
            result |= Failure(mismatch_message("status code", response.status, reference.status))

        if response.content is None:
            if reference.content is not None:
                return Failure("Response missing content.")
            else:
                return result

        # Some resource requests redirect to ports
        if "HttpPort" in response.content["handler"]:
            port_comparator = PortComparator(self.host, self.response_ver, self.baseline_ver)
            return port_comparator.compare(response, reference)

        if response.status != reference.status:
            result |= Failure(mismatch_message("status code", response.status, reference.status))

        resources = zip_json(
            self.get_resource_list(response.content),
            self.get_resource_list(reference.content)
        )
        for resource in resources:
            new_result = self._compare_single_resource(resource)
            result |= new_result

        return result

    def get_resource_list(self, content: dict):
        if "resources" in content.keys():
            return content["resources"]
        else:
            fields = content["resource"]
            return [{"resource": fields}]

    def _compare_single_resource(self, resource: dict) -> Result:
        result = Success()

        zipped_content = list(resource.values())[0]
        for key, (response_val, reference_val) in zipped_content.items():
            if response_val is None is not reference_val:
                # Missing value
                result |= Failure(f"'{key}' is missing from the reference.")

            elif response_val is not None is reference_val:
                # Extra value
                result |= Warning(f"(warning) '{key}' is present in the response but not the reference.")

            elif key in self.exact_match_keys:
                # Exact match
                if response_val != reference_val:
                    result |= Failure(mismatch_message(key, response_val, reference_val))

            elif type(response_val) is not type(reference_val):
                result |= Failure(mismatch_type_message(key, response_val, reference_val))

        if key not in self.all_known_keys:
            result |= Warning(f"(warning) '{key}' is a new field unrecognized by the comparator.")

        return result


class CliComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["cli"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class CliFormComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["cli-form", "cli-form"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class CliJsonComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["cli-json"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class HelpComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["help"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class StatusDataComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["status-msg"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class WebSocketMessageComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["ws-msg"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class MiscComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["misc"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


class ControlComparator(Comparator):
    @staticmethod
    def handles_endpoints() -> List[str]:
        return ["newsession", "endsession", "quit", "control"]

    def _compare(self, response: 'Response', reference: 'Response') -> Result:
        # TODO: Implement
        raise NotImplementedError()


# Called after all subclasses are defined
Comparator._populate_comparator_mappings()
