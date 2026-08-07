#!/usr/bin/env python3
"""
NAME:       http_regression_test/main.py

PURPOSE:    Run repeated sets of queries against various endpoints of the LANforge JSON REST API and
            compare the results to previous baseline results from known good versions in order to
            prevent regressive changes to the API.

EXAMPLE:    Create a baseline for a given system on 5.5.2 from a few GET requests to resource endpoint
            $ python http_regression_test/main.py baseline 5.5.2 192.168.101.137 --save 5.5.2-baseline.json \
                --get /resource/1/1 --get /resource/1/all --get /resource/1/list --get /resource/1/1?fields=eid

            Evaluate a given system, now on 5.5.3, against the previous 5.5.2 baseline
            % python http_regression_test/main.py test 5.5.3 --baseline 5.5.2-baseline.json

NOTES:      The code the compares the endpoint responses exists in http_regression_test/comparators.py.
            The comparator for a given endpoint must be andimplemented in order to receive test
            results for requests against the corresponding endpoint.

            Some endpoint response comparators expect certain preconditions for evaluating the
            correctness of response content such as loading databases, running a known traffic
            profile for a fixed duration, etc. Such preconditions can be established by running an
            initialization script before the test using http_regression_test/init_wrapper.py.
"""

from __future__ import annotations

import json
import logging
import requests
import textwrap
import importlib

from enum import Enum
from dataclasses import dataclass
from typing import Tuple, Optional
from argparse import ArgumentParser, Namespace, Action
from comparators import Comparator, Result, Success, Warning, Failure

# Some shenannigans to import the logger config from a cousin file
import sys
from os import path
file_dir = path.dirname(path.realpath(__file__))
sys.path.insert(0, path.abspath(path.join(file_dir, "..")))

lf_logger_config = importlib.import_module("lf_logger_config")
logger = logging.getLogger(__name__)


class Method(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

    @staticmethod
    def from_str(val: str):
        if val in ["GET", "get"]:
            return Method.GET
        elif val in ["POST", "post"]:
            return Method.POST
        elif val in ["PUT", "put"]:
            return Method.PUT
        elif val in ["DELETE", "delete"]:
            return Method.DELETE

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Response:
    status: int
    reason: str
    content: Optional[dict]


@dataclass(frozen=True)
class Request:
    uri: str
    method: Method

    _request_funcs = {
        Method.GET:    requests.get,
        Method.POST:   requests.post,
        Method.PUT:    requests.put,
        Method.DELETE: requests.delete,
    }

    def make_request(self, host: str, port: int) -> Optional[Exchange]:
        try:
            method_func = self._request_funcs[self.method]
            requests_response: requests.models.Response = method_func(self.full_url(host, port))

        except requests.exceptions.ConnectionError as e:
            logger.warning(e)
            requests_response = None

        try:
            content = requests_response.json() if requests_response else None
        except requests.exceptions.JSONDecodeError as e:
            logger.warning(e)
            content = None

        if requests_response is None:
            return None
        else:
            response = Response(
                status=requests_response.status_code,
                reason=requests_response.reason,
                content=content,
            )

            return Exchange(self, response)

    def full_url(self, host: str, port: int):
        return (
            f"http://{host}:{port}" +
            ("/" if self.uri[0] != "/" else "") +
            self.uri
        )

    @property
    def endpoint(self):
        endp = self.uri.split("/")
        return endp[0] if endp[0] != "" else endp[1]


@dataclass(frozen=True)
class Exchange:
    request: Request
    response: Optional[Response]

    def format(self) -> dict:
        return {
            "uri":     self.request.uri,
            "method":  str(self.request.method),
            "status":  self.response.status if self.response else None,
            "reason":  self.response.reason if self.response else None,
            "content": self.response.content if self.response else None,
        }

    @staticmethod
    def parse(data: dict) -> 'Exchange':
        request = Request(
            data["uri"],
            Method.from_str(data["method"]),
        )

        if data["status"] is None or data["reason"] is None:
            response = None

        else:
            response = Response(
                data["status"],
                data["reason"],
                data["content"],
            )

        return Exchange(request, response)

    def __iter__(self):
        return iter((self.request, self.response))


@dataclass(frozen=True)
class Baseline:
    host: str
    port: int
    version: str
    metadata: Optional[dict]
    exchanges: Tuple[Exchange]

    def format(self: 'Baseline') -> dict:
        data = {}
        data["host"] = self.host
        data["port"] = self.port
        data["version"] = self.version

        if (self.metadata is not None):
            data["metadata"] = self.metadata

        data["exchanges"] = list(map(Exchange.format, self.exchanges))

        return data

    @staticmethod
    def parse(data: dict) -> 'Baseline':
        return Baseline(
            host=data["host"],
            port=data["port"],
            version=data["version"],
            metadata=data["metadata"] if ("metadata" in data.keys()) else None,
            exchanges=tuple(Exchange.parse(e) for e in data["exchanges"])
        )


#
# baseline subcommand
#

def run_baseline(args: Namespace):
    request_list: list[tuple[str, Method]] = (
        [Request(uri, Method.GET) for uri in args.get] +
        [Request(uri, Method.POST) for uri in args.post] +
        [Request(uri, Method.PUT) for uri in args.put] +
        [Request(uri, Method.DELETE) for uri in args.delete]
    )

    exchanges: tuple[Exchange] = tuple(
        request.make_request(args.host, args.port)
        for request in request_list
    )

    baseline = Baseline(
        host=args.host,
        port=args.port,
        version=args.version,
        metadata=args.metadata,
        exchanges=exchanges,
    )

    data = baseline.format()

    if args.save:
        with open(args.save, "w") as f:
            json.dump(data, f, indent=4)
    else:
        json.dump(data, sys.stdout, indent=4)


#
# test subcommand
#

LOG_WIDTH = 80


def pretty_log(msg: str, indent=0, level: str = "info", stacklevel=2):
    log = {"debug": logger.debug, "info": logger.info, "warning": logger.warning,
           "error": logger.error, "critical": logger.critical}
    log = log[level]

    if "\n" in msg:
        for line in msg.split("\n"):
            pretty_log(line, indent=indent, level=level, stacklevel=stacklevel+1)
    else:
        lines = textwrap.wrap(msg, LOG_WIDTH-(4*indent))
        for line in lines:
            def test(s):
                print(len(s), " : ", s)
            log(("    "*indent + line).ljust(LOG_WIDTH), stacklevel=stacklevel)


def log_exchange_preview(request: Request, base_version: str, version: str):
    pretty_log("=" * LOG_WIDTH)

    pretty_log(f"Baseline   : {base_version} - {request.method} - {request.uri}")
    pretty_log(f"Result     : {version} - {request.method} - {request.uri}")


def add_newline_indent(s):
    return s.replace('\n', '\n    ')


def log_exchange_response(comparator, base_response: Response, response: Response):
    pretty_log("Baseline   :", level="debug")

    pretty_log(f"{base_response.status} - {base_response.reason}", indent=1, level="debug")
    pretty_log(f"{add_newline_indent(json.dumps(base_response.content, indent=4))}", indent=1, level="debug")

    pretty_log("Result     :", level="debug")

    if response is None:
        pretty_log("None", indent=1, level="debug")
    else:
        pretty_log(f"{response.status} - {response.reason}", indent=1, level="debug")
        pretty_log(f"{add_newline_indent(json.dumps(response.content, indent=4))}", indent=1, level="debug")

    pretty_log(f"Comparator : {type(comparator).__name__}")


def log_success():
    pretty_log("SUCCESS")


def log_warning(strict: bool, message: str = ""):
    if strict:
        log_failure(message)
    else:
        pretty_log("WARNING:")
        pretty_log(f"{add_newline_indent(message)}", indent=1)


def log_failure(message: str = ""):
    pretty_log("FAILURE:")
    pretty_log(f"{add_newline_indent(message)}", indent=1)


def log_summary(results: dict):
    pretty_log("=" * 80)
    pretty_log("Summary:")
    pretty_log(f"Successes : {results['successes']}", indent=1)
    pretty_log(f"Warnings  : {results['warnings']}", indent=1)
    pretty_log(f"Failures  : {results['failures']}", indent=1)


def run_test(args: Namespace):
    if args.baseline:
        with open(args.baseline, "r") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    baseline = Baseline.parse(data)

    results = {
        "successes": 0,
        "warnings": 0,
        "failures": 0,
    }

    request: Request
    baseline_response: Response
    for request, baseline_response in baseline.exchanges:
        log_exchange_preview(request, baseline.version, args.version)

        new_response: Response = request.make_request(baseline.host, baseline.port).response
        comparator = Comparator.fetch_comparator_cls(request.endpoint)(
            baseline.host,
            baseline.version,
            args.version
        )
        result: Result = comparator.compare(new_response, baseline_response)

        log_exchange_response(comparator, baseline_response, new_response)

        if isinstance(result, Success):
            log_success()
            results["successes"] += 1
        elif isinstance(result, Warning):
            log_warning(args.strict, result.message)
            results["warnings"] += 1
        elif isinstance(result, Failure):
            log_failure(result.message)
            results["failures"] += 1
        else:
            logger.error(f"Unknown result type: {result}")

    log_summary(results)

#
# Initialization
#


class HelpSummaryAction(Action):
    """
    A custom argparse action that halts argument parsing when the --help_summary argument is encountered.
    Even if the program is missing otherwise required arguments, print the summary and exit
    """
    def __init__(self, option_strings, dest, nargs=0, **kwargs):
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        self.print_help_summary()
        parser.print_help()
        parser.exit(0)

    def print_help_summary(self):
        print("The http_Regression_test suite is intended to detect unintended changes to the\n"
              "external behavior of the LANforge HTTP JSON REST API. This script can execute in\n"
              "two modes \"baseline\", and \"test\".\n")

        print("The baseline mode produces a stable artifact that represents the behavior of\n"
              "a known-good version of the software, against which the behavior of future\n"
              "versions can be compared. In this mode, the script performs a given series of\n"
              "HTTP requests against the specified LANforge API host, saving the status and\n"
              "content of each response as a json-encoded artifact.\n")

        print("In test mode, the script accepts a previous baseline as ground truth, performs\n"
              "each of the same requests against the same host, and compares each of the new\n"
              "responses against that ground truth.\n")

        print("Since each LANforge HTTP endpoint has differing response content and requires\n"
              "different semantics for acceptable amounts of deviation, the test subcommand\n"
              "calls out to the http_regression_test.comparators module, which will implement\n"
              "comparator logic for each endpoint.\n")


def parse_args() -> Namespace:
    parser = ArgumentParser(prog="http_regression_test.py")
    parser.add_argument('--log_level', default=None, help='Set logging level: debug | info | warning | error | critical')
    parser.add_argument("--lf_logger_config_json", help="--lf_logger_config_json <json file> , json configuration of logger")
    parser.add_argument('--help_summary', help='Show summary of what this script does', action=HelpSummaryAction)

    subparsers = parser.add_subparsers(
        dest="mode",
        required=True,
        metavar="{baseline, test}",
        help="Required, the mode to run the script in"
    )

    # baseline subcommand
    parser_baseline = subparsers.add_parser(
        "baseline",
        help="Perform a series of specified HTTP requests against a given host "
        "and serialize the responses as a JSON baseline reference."
    )
    parser_baseline.add_argument("version",
                                 help="LANforge version of the host")

    parser_baseline.add_argument("host",
                                 help="Hostname or IP address of the target HTTP API")

    parser_baseline.add_argument("-p", "--port", default=8080,
                                 help="Port of the target HTTP API. Defaults to 8080 if omitted.")

    parser_baseline.add_argument("-s", "--save", nargs="?", default=None,
                                 help="Path to save the results to. If absent, "
                                 "writes the baseline JSON to stdout.")

    parser_baseline.add_argument("-c", "--copy", default=None,
                                 help="Create a new baseline with the same "
                                      "requests as a given baseline file.")

    parser_baseline.add_argument("--metadata",
                                 help="Optional JSON metadata such as comments,"
                                 "configuration information, or preconditions.")

    parser_baseline.add_argument("--get", action="append", default=[],
                                 help="URIs to process with http GET requests.")

    parser_baseline.add_argument("--post", action="append", default=[],
                                 help="URIs to process with http POST requests.")

    parser_baseline.add_argument("--put", action="append", default=[],
                                 help="URIs to process with http PUT requests.")

    parser_baseline.add_argument("--delete", action="append", default=[],
                                 help="URIs to process with http DELETE requests.")

    parser_baseline.set_defaults(handler=run_baseline)

    # test subcommand
    parser_test = subparsers.add_parser(
        "test",
        help="Given a saved baseline, perform the contained HTTP requests and "
        "compare responses to the baseline. Successes, Warnings, and Failures "
        "will be reported over stdout."
    )

    parser_test.add_argument("version",
                             help="The LANforge version of the host")

    parser_test.add_argument("-b", "--baseline", nargs="?",
                             help="Path to the baseline file to compare against. "
                                   "If absent, reads the baseline JSON from stdin.")
    parser_test.add_argument("-S", "--strict", action="store_true",
                             help="Treat Warning results as failures.")

    parser_test.set_defaults(handler=run_test)

    return parser.parse_args()


def init_logging(args):
    logger_config = lf_logger_config.lf_logger_config()
    if args.log_level:
        logger_config.set_level(level=args.log_level)

    if args.lf_logger_config_json:
        # logger_config.lf_logger_config_json = "lf_logger_config.json"
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()


if __name__ == "__main__":
    args = parse_args()

    init_logging(args)

    args.handler(args)
