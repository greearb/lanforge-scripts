#!/usr/bin/env python3
# flake8: noqa
import random
import string
import subprocess
import sys
import time
from pprint import pprint
from statistics import mean

# List of fake website name components
prefixes: list = ["alpha", "beta", "omega", "nebula", "cosmo", "stellar"]
suffixes: list = ["web", "site", "hub", "net", "link", "zone"]
# Number of website names to generate
num_names: int = 1000
tt_queries: int = 0
queries_mark: int = 0
duration_sec: int = 0


# Generate a random website name
def generate_fake_website_name():
    prefix = random.choice(prefixes)
    suffix = random.choice(suffixes)
    random_string = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 7)))
    return f"www.{prefix}{suffix}-{random_string}.com"


def report(time_b: float = None,
           time_e: float = None,
           num_queries: int = None,
           times: list = None):
    if not times:
        return
    ave_query_time = mean(query_times)
    qps: float = num_queries / (time_e - time_b)
    print(f"queries: {num_queries}, queries_per_sec {qps:02.2f}, ave_query_time: {ave_query_time:02.2f}ms")
    query_times.clear()


# - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  #
#           M A I N
# - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  #
nameserver = ""
if len(sys.argv) < 2:
    print("please specify a port")
    exit(1)
port = sys.argv[1]
#pprint(["argv:", sys.argv])
if port.find(".") >= 0:
    print(f"port[{port}]")
    port = port[port.rfind("."):]
    print(f"port now[{port}]")
if len(sys.argv) >= 3:
    for arg in sys.argv[2:]:
        if arg.startswith("nameserver="):
            nameserver = arg[arg.find('=')+1:]
        if arg.startswith("duration="):
            duration_sec = float(arg[arg.find('=')+1:])

ave_query_time = -1
query_times: list = []

# Generate and print random fake website names
start_time: float = time.time()
time_mark = start_time
loctim: float = 0.0
# pprint(["start_time:", start_time])
print_report = False
for query_num in range(num_names):
    website_name = generate_fake_website_name()
    # print(website_name)
    try:
        cmd_args : list = ["./vrf_exec.bash", port, "dig", "-t", "a", website_name, nameserver]
        fmt_cmd = f"command: {' '.join(cmd_args)}"
        with subprocess.Popen(cmd_args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as proc:

            for line_b in proc.stdout.readlines():
                line_s = str(line_b).lower()
                #print(line_s)
                pos = line_s.find("query time")
                if pos >= 0:
                    query_time_str = line_s[(line_s.find(':') + 1):].strip()
                    query_times.append(float(query_time_str[0: query_time_str.find(' ')]))
                    break

            rv = proc.wait()
            if rv != 0:
                print(f"problem with command: {fmt_cmd}")
                exit(rv)
            # pprint(["query_times:", query_times])

    except:
        pprint(sys.exc_info())
        exit(1)
    loctim = time.time()
    if loctim >= int(time_mark + 2):
        time_mark = loctim
        report(start_time, loctim, (query_num - queries_mark), query_times)
        queries_mark = query_num
    if loctim >= (start_time + duration_sec):
        print("duration reached")
        num_names = query_num
        break
report(start_time, loctim, num_names, query_times)
exit(0)
#
