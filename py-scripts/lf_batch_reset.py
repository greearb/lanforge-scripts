#!/usr/bin/env python3
r"""
NAME: lf_batch_reset.py

PURPOSE:
    Batch-wise client reset test. Stations are split into batches. Every "batch reset interval" one batch is reset -
    stop its traffic, randomize its MACs, move it to the next SSID in a rotating list, re-authenticate, resume traffic,
    then check the per-station throughput against the rate limit - while the other batches keep running. It cycles batch
    by batch until --test_duration elapses, so the AP sees a steady trickle of clients leaving and rejoining.

    Connection defaults to 802.1X EAP + RADIUS (--eap PEAP). For plain WPA-PSK use --eap NONE with --ssid_pw; for open
    use --eap NONE --security open. Rate-limit verification still runs for any of them if a limit is set.

    Outputs: batch_reset_details.csv (per station per reset), overall_throughput.csv (aggregate throughput throughout
    the test), and an HTML/PDF report.

EXAMPLE:
    A (A1-A4) - Full test runs: create stations, connect, reset, verify rate limit, write the report.
    B (B1-B11) - Toolbox: standalone building blocks, in their fixed lifecycle order.
    C (C1-C3) - Toolbox: chaining several building blocks in one call.
    D (D1) - Combining --use_existing_eid (SET) with a batchN selector (SELECTOR).

    A1 is the full 500-client / 5-batch scenario;
    A2-A4 use 20 stations on one radio (5 batches of 4) to stay short.
    Change --mgr, --upstream_port, --radio, --ssid and the credentials to match your setup.

    # A1. 500 EAP-PEAP clients across 5 radios (100 each -> 5 batches of 100), reset one batch every
    #     10 min for 2 h; allow up to 15 min for every client to get an IP address:
    ./lf_batch_reset.py --mgr 192.168.1.101 --upstream_port 1.1.eth2 \
         --radio "radio==1.1.wiphy0 stations==100"  --radio "radio==1.1.wiphy1 stations==100" \
        --radio "radio==1.1.wiphy2 stations==100" --radio "radio==1.1.wiphy3 stations==100" \
        --radio "radio==1.1.wiphy4 stations==100" --num_batches 5 \
        --ssid ENT-A --ssid_list ENT-A,ENT-B,ENT-C --eap_identity user --eap_password secret \
        --traffic_type tcp+udp --direction bidi --rate_mode per_station --traffic_rate 5Mbps --payload_size 1472 \
        --test_duration 2h --batch_reset_interval 10m --wait_for_ip_sec 900 \
        --rate_limit_dl 20Mbps --rate_limit_ul 10Mbps

    # A1b. Same 500-client scenario as A1, but with a different RADIUS login with its own
    #      RADIUS-assigned cap (per-radio eap_identity==/eap_password==/rate_limit_dl==/rate_limit_ul==,
    #      batch==1..5) - no --num_batches needed, grouping and grading follow each radio's own identity:
    ./lf_batch_reset.py --mgr 192.168.1.101 --upstream_port 1.1.eth2 \
        --radio "radio==1.1.wiphy0 stations==100 batch==1 eap_identity==user1 eap_password==password rate_limit_dl==30M rate_limit_ul==20M" \
        --radio "radio==1.1.wiphy1 stations==100 batch==2 eap_identity==user2 eap_password==password rate_limit_dl==50M rate_limit_ul==60M" \
        --radio "radio==1.1.wiphy2 stations==100 batch==3 eap_identity==user3 eap_password==password rate_limit_dl==10M rate_limit_ul==50M" \
        --radio "radio==1.1.wiphy3 stations==100 batch==4 eap_identity==user4 eap_password==password rate_limit_dl==50M rate_limit_ul==10M" \
        --radio "radio==1.1.wiphy4 stations==100 batch==5 eap_identity==user5 eap_password==password rate_limit_dl==88M rate_limit_ul==66M" \
        --ssid ENT-A --ssid_list ENT-A,ENT-B,ENT-C --eap PEAP \
        --traffic_type tcp+udp --direction bidi --rate_mode per_station --traffic_rate 5Mbps --payload_size 64-1472 \
        --test_duration 2h --batch_reset_interval 10m --wait_for_ip_sec 900

    # A2. Full test - 802.1X EAP, reset a batch every 5 min for 1 hour, verify the RADIUS cap after each reconnect:
    ./lf_batch_reset.py --mgr 192.168.1.101 --upstream_port 1.1.eth2 \
        --radio "radio==1.1.wiphy0 stations==20" --num_batches 5 \
        --ssid ENT-A --ssid_list ENT-A,ENT-B,ENT-C --eap_identity user --eap_password secret \
        --traffic_type tcp --direction bidi --rate_mode per_station --traffic_rate 5Mbps --payload_size 1472 \
        --test_duration 1h --batch_reset_interval 5m --rate_limit_dl 20Mbps --rate_limit_ul 10Mbps

    # A3. Full test - WPA2-PSK instead of EAP (--eap NONE, use --ssid_pw):
    ./lf_batch_reset.py --mgr 192.168.1.101 --upstream_port 1.1.eth2 \
        --radio "radio==1.1.wiphy0 stations==20" --num_batches 5 \
        --eap NONE --ssid PSK-A --ssid_pw secret123 --ssid_list PSK-A,PSK-B \
        --traffic_type tcp --direction bidi --rate_mode per_station --traffic_rate 5Mbps \
        --test_duration 30m --batch_reset_interval 5m --rate_limit_dl 20Mbps

    # A4. Plain throughput run - no batch resets (just omit --batch_reset_interval):
    ./lf_batch_reset.py --mgr 192.168.1.101 --upstream_port 1.1.eth2 \
        --radio "radio==1.1.wiphy0 stations==20" --num_batches 5 \
        --ssid ENT-A --eap_identity user --eap_password secret \
        --traffic_type tcp --direction bidi --rate_mode per_station --traffic_rate 5Mbps --test_duration 20m

TOOLBOX MODE (--toolbox):
    Runs standalone building-block actions and exits - no report. When several are passed in one call they run in a
    fixed lifecycle order (create -> build CXs -> reset -> admin up -> start -> verify -> stop -> admin down ->
    del CXs -> del stations -> cleanup), not the order you typed them.

    The actions, in the order they run when combined (B1-B11):

    # B1. create_stations   (needs --radio; rejects --use_existing_eid; the stations do not exist yet)
    #     options: --radio (per-radio 'stations==N', or one bare radio + --num_stations)  --num_batches
    #              802.1X EAP [default]: --eap PEAP|TTLS|TLS  --eap_identity  --eap_password
    #                                    (TLS: --private_key [--pk_passwd] instead of --eap_password)
    #              WPA-PSK: --eap NONE --ssid_pw <pw>          open: --security open --eap NONE
    #              per-radio overrides: eap_identity==/eap_password==/rate_limit_dl==/rate_limit_ul==
    #              inside a --radio spec - different radios can use different RADIUS logins with
    #              different assigned caps (see B1f); falls back to the flags above when omitted.
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --create_stations --num_batches 5 \
        --radio "radio==1.1.wiphy0 stations==20" --ssid ENT-A --eap_identity user --eap_password secret

    # B1b. WPA-PSK instead of EAP:
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --create_stations --num_batches 5 \
        --radio "radio==1.1.wiphy0 stations==20" --eap NONE --ssid PSK-A --ssid_pw secret123

    # B1c. open (no security, no EAP):
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --create_stations \
        --radio "radio==1.1.wiphy0 stations==20" --security open --eap NONE --ssid OPEN-A

    # B1d. two radios, split across them (10 + 10):
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --create_stations --num_batches 5 \
        --radio "radio==1.1.wiphy0 stations==10" --radio "radio==1.1.wiphy1 stations==10" \
        --ssid ENT-A --eap_identity user --eap_password secret

    # B1e. one bare radio, count from --num_stations (only valid with a single --radio):
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --create_stations --num_batches 5 \
        --radio 1.1.wiphy0 --num_stations 20 --ssid ENT-A --eap_identity user --eap_password secret

    # B1f. 500 clients, 5 radios, 5 different RADIUS logins each with its own RADIUS-assigned cap
    #      batch==<label> names each radio's stations 'B<label>_staXXXX', so 'batch1'..'batch5' below (in the
    #      order first seen) grade against the right user's cap - and since the label lives in the station
    #      name, a later independent --toolbox call recognises the same batches with no --radio needed.
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --create_stations --ssid ENT-A \
        --radio "radio==1.1.wiphy0 stations==100 batch==1 eap_identity==user1 eap_password==password" \
        --radio "radio==1.1.wiphy1 stations==100 batch==2 eap_identity==user2 eap_password==password" \
        --radio "radio==1.1.wiphy2 stations==100 batch==3 eap_identity==user3 eap_password==password" \
        --radio "radio==1.1.wiphy3 stations==100 batch==4 eap_identity==user4 eap_password==password" \
        --radio "radio==1.1.wiphy4 stations==100 batch==5 eap_identity==user5 eap_password==password"

    # B1g. batch==<label>: one radio caps at 100 stations, but a login needs 200 - two radios
    #      share batch==1; a third (uneven, 50 stations) is its own batch==2. Grouping
    #      goes by label, not by radio order/size, so --num_batches is not even needed here:
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --create_stations --ssid ENT-A \
        --radio "radio==1.1.wiphy0 stations==100 batch==1 eap_identity==user1 eap_password==password" \
        --radio "radio==1.1.wiphy1 stations==100 batch==1 eap_identity==user1 eap_password==password" \
        --radio "radio==1.1.wiphy2 stations==50  batch==2 eap_identity==user2 eap_password==password"

    # B2. build_cross_connects   (station <-> --upstream_port)
    #     options: --upstream_port (required)  --traffic_type tcp|udp|tcp+udp  --direction dl|ul|bidi
    #              --rate_mode per_station|intended_load  --traffic_rate 5Mbps  --payload_size 1472 | 64-1472 | MTU
    #              station set: all stations on LANforge [default] or --use_existing_eid <eids>
    #              --traffic_type here names the cross-connects (staXXXX-tcp / staXXXX-udp); pass the
    #              SAME --traffic_type again on start_traffic / stop_traffic (B5, B7) below, or they
    #              default to tcp+udp and fail on whichever half was never built. verify_rate_limit
    #              (B6) doesn't error on a mismatch, but should still match for an accurate number.
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --build_cross_connects --upstream_port 1.1.eth2

    # B2b. udp only, downlink, custom rate/payload:
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --build_cross_connects --upstream_port 1.1.eth2 \
        --traffic_type udp --direction dl --traffic_rate 10Mbps --payload_size 64-1472

    # B2c. against specific existing ports instead of every station on LANforge:
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --build_cross_connects --upstream_port 1.1.eth2 \
        --use_existing_eid 1.1.sta0000,1.1.sta0001

    # B3. reset_batch N   (one reset: stops traffic, re-MAC + reconnect + re-auth;)
    #     options: --num_batches   --ssid <reconnect target>  (--ssid_list's first entry wins if given) --no_randomize_mac
    #              station set: all stations on LANforge [default] or --use_existing_eid <eids> or --radio "..."
    #              Without a batch== label at creation, 'batch N' is an arithmetic slice - pass the same
    #              --radio / --num_batches used at creation, or it could point at different stations.
    #              With batch==<label> (B1f/B1g), the layout is read from the station names instead, so no
    #              --radio/--num_batches is needed here to get the right batch back.
    #              It also stops the batch's traffic first, so --traffic_type must match how the
    #              cross-connects were built too (see B2 above).
    ./lf_batch_reset.py --mgr 192.168.1.101 --num_batches 5 --toolbox --reset_batch 2 --traffic_type tcp+udp \
        --ssid ENT-B --eap_identity user --eap_password secret

    # B3b. same with 'batch2' spelling:
    ./lf_batch_reset.py --mgr 192.168.1.101 --num_batches 5 --toolbox --reset_batch batch2 --traffic_type tcp+udp \
        --eap NONE --ssid PSK-B --ssid_pw secret123

    # B3c. skip MAC randomization on reset:
    ./lf_batch_reset.py --mgr 192.168.1.101 --num_batches 5 --toolbox --reset_batch 2 --no_randomize_mac --traffic_type tcp+udp \
        --ssid ENT-B --eap_identity user --eap_password secret

    # B3d. pin the set/layout with --radio (must match how the stations were created):
    ./lf_batch_reset.py --mgr 192.168.1.101 --num_batches 5 --toolbox --reset_batch 2 --traffic_type tcp+udp \
        --radio "radio==1.1.wiphy0 stations==20" --ssid ENT-B --eap_identity user --eap_password secret

    # B3e. reset a specific existing pair instead of the created set:
    ./lf_batch_reset.py --mgr 192.168.1.101 --num_batches 1 --toolbox --reset_batch 1 --traffic_type tcp+udp \
        --use_existing_eid 1.1.sta0004,1.1.sta0005 --ssid ENT-B --eap_identity user --eap_password secret

    # B4. admin_up SEL      (SEL forms below apply to every 'SEL' action, B4-B10)
    #     all      -> every station on LANforge
    #     batchN   -> those same stations split into --num_batches (default 5), Nth slice -
    #                 or, if created with batch==<label>, the Nth label's stations (--num_batches ignored)
    #     a list   -> only the named stations / EIDs
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --admin_up all
    ./lf_batch_reset.py --mgr 192.168.1.101 --num_batches 5 --toolbox --admin_up batch3
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --admin_up 1.1.sta0000,1.1.sta0001

    # B5. start_traffic SEL   (--traffic_type must match how the cross-connects were built, see B2)
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --start_traffic all --traffic_type tcp+udp
    ./lf_batch_reset.py --mgr 192.168.1.101 --num_batches 5 --toolbox --start_traffic batch3 --traffic_type tcp+udp
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --start_traffic sta0000,sta0004 --traffic_type tcp+udp

    # B6. verify_rate_limit SEL   (+ --rate_limit_dl / --rate_limit_ul; --rate_limit_tolerance_percent, default 5;
    #     --traffic_type should match too, for an accurate number - see B2)
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --verify_rate_limit all --traffic_type tcp+udp --rate_limit_dl 20Mbps --rate_limit_ul 10Mbps
    ./lf_batch_reset.py --mgr 192.168.1.101 --num_batches 5 --toolbox --verify_rate_limit batch2 --traffic_type tcp+udp --rate_limit_dl 20Mbps
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --verify_rate_limit sta0000,sta0004 --traffic_type tcp+udp --rate_limit_dl 20Mbps

    # B6b. steadier grade: average 20 samples over 40s (--rate_limit_window / --polling_interval), 3% headroom:
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --verify_rate_limit all --traffic_type tcp+udp --rate_limit_dl 20Mbps \
        --rate_limit_window 40s --polling_interval 2s --rate_limit_tolerance_percent 3

    # B7. stop_traffic SEL   (--traffic_type must match how the cross-connects were built, see B2)
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --stop_traffic all --traffic_type tcp+udp
    ./lf_batch_reset.py --mgr 192.168.1.101 --num_batches 5 --toolbox --stop_traffic batch3 --traffic_type tcp+udp
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --stop_traffic sta0000,sta0004 --traffic_type tcp+udp

    # B8. admin_down SEL
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --admin_down all
    ./lf_batch_reset.py --mgr 192.168.1.101 --num_batches 5 --toolbox --admin_down batch3
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --admin_down sta0000,sta0001

    # B9. del_cxs SEL   (stop and remove the cross-connects)
    #     a batchN selector deletes whatever cx's actually exist for those stations (tcp, udp, or
    #     both), found by live discovery - no need to match --traffic_type to how they were built.
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --del_cxs all
    ./lf_batch_reset.py --mgr 192.168.1.101 --num_batches 5 --toolbox --del_cxs batch1
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --del_cxs sta0000,sta0004

    # B10. del_stations SEL   (admin-down and remove the ports)
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --del_stations all
    ./lf_batch_reset.py --mgr 192.168.1.101 --num_batches 5 --toolbox --del_stations batch1
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --del_stations sta0000,sta0004

    # B11. cleanup   (no options - removes every cross-connect and station on the manager)
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --cleanup

    Combine several in one call (still runs in the order above):

    # C1. create 20 WPA2-PSK stations, wire them up, start traffic:
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --create_stations --build_cross_connects --start_traffic all \
        --radio "radio==1.1.wiphy0 stations==20" --num_batches 5 --upstream_port 1.1.eth2 --eap NONE --ssid PSK-A --ssid_pw secret123

    # C2. reset batch 2 onto ENT-B, resume its traffic, check its cap (each once, in order);
    #     --traffic_type here must match whatever the cross-connects were originally built with:
    ./lf_batch_reset.py --mgr 192.168.1.101 --num_batches 5 --toolbox \
        --reset_batch 2 --start_traffic batch2 --verify_rate_limit batch2 --traffic_type tcp+udp \
        --ssid ENT-B --eap_identity user --eap_password secret --rate_limit_dl 20Mbps --rate_limit_ul 10Mbps

    # C3. tear it all down (--traffic_type here matches how the cross-connects were built, for stop_traffic):
    ./lf_batch_reset.py --mgr 192.168.1.101 --toolbox --stop_traffic all --traffic_type tcp+udp --del_cxs all --del_stations all

    Two independent things pick the stations an action uses:
      1. the STATION SET - one of:
           --radio "radio==.. stations==N"   - build the sta* names (only --create_stations needs it)
           --use_existing_eid <eid,eid,..>   - act on exactly these ports - any name, not just sta*
           neither                           - use every station already on LANforge (--mgr)
      2. the SELECTOR (SEL) - picks WITHIN that set:
           all [default] | batchN (1-based) | a comma list of names or EIDs (sta0000,sta0004)
           exception: for --del_cxs / --del_stations, 'all' reaches every cross-connect / station
           on --mgr instead - not just this test's own set (batchN and a comma list still do).

    A 'batchN' selector (and --reset_batch) also needs --num_batches (default 5): it slices the chosen SET into that
    many batches. Use the same --num_batches the stations were created with, or 'batch2' won't be the same stations -
    unless any --radio set batch==<label> at creation (B1f/B1g), in which case the layout is read from the station
    names instead and --num_batches is ignored entirely.

    # D1. SET = --use_existing_eid (exactly these 4 ports, not every station on LANforge), SELECTOR =
    #     'batch1', --num_batches 2 -> the 4 ports split into two batches of 2, so only the first
    #     two (sta0100, sta0101) are admin-up'd:
    ./lf_batch_reset.py --mgr 192.168.1.101 --num_batches 2 --toolbox --admin_up batch1 \
        --use_existing_eid 1.1.sta0100,1.1.sta0101,1.1.sta0102,1.1.sta0103

    See also docs/lf_batch_reset_toolbox.md.

SCRIPT_CLASSIFICATION:  Traffic Generation, Stress / Longevity

SCRIPT_CATEGORIES:   Performance,  Functional,  Report Generation

NOTES:
    * The rate cap is assigned by the AP + RADIUS server; so this verifies the *effect* - per-station throughput vs
      --rate_limit_dl / --rate_limit_ul within --rate_limit_tolerance_percent, only for a direction that carries traffic
      and has a limit set.
    * Stations are split into --num_batches contiguous batches; if the count does not divide evenly, the leftover
      stations are added to the last batch. Skipped once any --radio sets batch==<label> (see B1g/B1f): stations are
      then named 'B<label>_staXXXX', and batches group on that label instead - recognised again on a later command with
      no need to re-pass --radio to identify the batch.
    * --radio's eap_identity==/eap_password==/rate_limit_dl==/rate_limit_ul== let different radios use different RADIUS
      logins with different caps (B1f). reset_batch groups a batch's stations by their own recorded (eap_identity,
      eap_password) before re-authenticating, so a batch spanning multiple logins still authenticates each one
      correctly; measure_rate_limit grades each station against its own recorded rate limit the same way.
    * --toolbox start_traffic / stop_traffic / reset_batch act on cross-connects named from THIS call's --traffic_type
      (default tcp+udp), not from what --build_cross_connects actually created. Use the SAME --traffic_type you built
      with - otherwise the half that doesn't match was never built as far as this call is concerned, and setting its
      state fails, even though the other half (and the CXs that do exist) work fine.
    * Discovery (no --radio / --use_existing_eid given) and pre_cleanup() (run automatically before every test unless
      --no_pre_cleanup) both act on every station on --mgr, not just ones this script created - on a manager shared with
      other tests, that includes theirs too.

STATUS: Functional

VERIFIED_ON:   Validate against a licensed LANforge system before production use.

LICENSE:
          Free to distribute and modify. LANforge systems must be licensed.
          Copyright (C) 2020-2026 Candela Technologies Inc

INCLUDE_IN_README: False
"""
from __future__ import annotations
from dataclasses import dataclass

import argparse
import csv
import datetime
import importlib
import logging
import os
import sys
import threading
import time

try:
    import pandas as pd
except ImportError as err:
    raise ImportError("lf_batch_reset.py requires pandas - install it with 'pip3 install pandas'") from err

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lf_report = importlib.import_module("py-scripts.lf_report")
lf_graph = importlib.import_module("py-scripts.lf_graph")
lf_logger_config = importlib.import_module("py-scripts.lf_logger_config")
LFUtils = importlib.import_module("py-json.LANforge.LFUtils")
realm = importlib.import_module("py-json.realm")
Realm = realm.Realm

logger = logging.getLogger(__name__)

# user-facing traffic type -> LANforge endpoint types
TRAFFIC_TYPE_TO_ENDP_TYPES = {
    "tcp": ["lf_tcp"],
    "udp": ["lf_udp"],
    "tcp+udp": ["lf_tcp", "lf_udp"],
}

STATION_PREFIX = "sta"
RADIO_STATION_BLOCK = 1000
MAC_RANDOM_PATTERN = "xx:xx:xx:*:*:xx"

EAP_METHODS = ["NONE", "DEFAULT", "MD5", "OTP", "GTC", "TLS", "PEAP", "TTLS", "SIM", "AKA",
               "PSK", "IKEV2", "FAST"]   # NONE = no 802.1X (plain WPA-PSK / open)
KEY_MGMTS = ["DEFAULT", "NONE", "WPA-PSK", "WPA-EAP", "WPA-PSK-SHA256", "WPA-EAP-SHA256",
             "FT-PSK", "FT-EAP", "FT-SAE", "SAE", "OWE", "IEEE8021X",
             "WPA-EAP-SUITE-B", "WPA-EAP-SUITE-B-192"]   # authentication key management; combinations supported
CIPHERS = ["[BLANK]", "DEFAULT", "CCMP", "TKIP", "NONE", "CCMP-TKIP", "CCMP-256",
           "GCMP", "GCMP-256", "CCMP/GCMP-256", "GCMP/CCMP-256",
           "WEP104", "WEP40", "GTK_NOT_USED", "ALL"]   # pairwise + groupwise cipher tokens


# --- parsing helpers ---
# TODO: Make it common utility functions available for all scripts.
def duration_to_seconds(value: str | int | float) -> int:
    """Convert a human-friendly duration to whole seconds.

    Args:
        value (str | int | float): Seconds as a number, or a string like '30s', '15m', '1h', '1d'.

    Returns:
        int: The duration expressed in seconds.

    Raises:
        ValueError: If value is a string that is neither a bare number nor
            <int><s|m|h|d> (e.g. '30s', '15m', '1h').
    """
    if isinstance(value, (int, float)):
        return int(value)
    value = str(value).strip().lower()
    if value.isdigit():
        return int(value)
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if value and value[-1] in units and value[:-1].isdigit():
        return int(value[:-1]) * units[value[-1]]
    raise ValueError("Cannot parse duration: %r (use e.g. 30s, 15m, 1h)" % value)


def parse_rate(value: str | int | float) -> int:
    """Parse a bandwidth string into bits per second.

    Args:
        value (str | int | float): Bits/sec as a number, or a string like '256k', '10M', '10Mbps', '1.5Gbps'.

    Returns:
        int: The rate in bits per second.

    Raises:
        ValueError: If the numeric part cannot be parsed as a float.
    """
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().lower().replace("bps", "").replace("/s", "")
    multiplier_map = {"k": 1_000, "m": 1_000_000, "g": 1_000_000_000}
    multiplier = 1
    if text and text[-1] in multiplier_map:
        multiplier = multiplier_map[text[-1]]
        text = text[:-1]
    try:
        return int(float(text) * multiplier)
    except ValueError:
        raise ValueError("Cannot parse rate: %r (use e.g. 256k, 10M, 1.5Gbps)" % value)


def batch_token(selector: str | int | None) -> str | None:
    """Return the digit token of a batch selector ('batchN' / 'N'), or None if selector isn't one.

    Args:
        selector: A selector value, e.g. a --reset_batch value or one of the SELECTOR_ACTIONS args.

    Returns:
        str | None: The 1-based batch number as a digit string, or None when selector
        does not look like a batch token (caller should try another interpretation).
    """
    text = "" if selector is None else str(selector).strip().lower()
    text = text[5:] if text.startswith("batch") else text
    return text if text.isdigit() else None


def parse_radio_arg(entry: str | list[str], default_ssid: str, default_ssid_pw: str,
                    default_security: str, default_eap_identity: str | None = None,
                    default_eap_password: str | None = None, default_rate_limit_dl: str = "",
                    default_rate_limit_ul: str = "") -> dict:
    """Turn a single --radio value into a normalised spec dict.

    Args:
        entry (str | list[str]): The raw --radio value. Either a key==value string like
        'radio==1.1.wiphy0 stations==25 ssid==.. ssid_pw==.. security==.. eap_identity==.. eap_password==..
        rate_limit_dl==.. rate_limit_ul==.. batch==..', or a bare radio EID like '1.1.wiphy0'.
        default_ssid (str): SSID to use when the entry has no 'ssid=='.
        default_ssid_pw (str): Password to use when the entry has no 'ssid_pw=='.
        default_security (str): Security to use when the entry has no 'security=='.
        default_eap_identity (str | None): EAP identity to use when the entry has no 'eap_identity=='.
        default_eap_password (str | None): EAP password to use when the entry has no 'eap_password=='.
        default_rate_limit_dl (str): Expected DL rate string to use when the entry has no 'rate_limit_dl=='.
        default_rate_limit_ul (str): Expected UL rate string to use when the entry has no 'rate_limit_ul=='.

    Returns:
        dict: Keys 'radio', 'stations', 'ssid', 'ssid_pw', 'security', 'eap_identity', 'eap_password',
        'rate_limit_dl', 'rate_limit_ul', 'batch'. 'stations' is an int, or None when the count was
        not given; the rate_limit_* values are raw rate strings (not yet parsed to bps); 'batch' is
        a free-form label string, or None when this radio has no batch== (see station_batch_label()).
        Keep labels short - they become part of the station name.

    Raises:
        ValueError: If no radio name can be read from entry, or 'stations==' is not an integer.
    """
    text = entry[0] if isinstance(entry, list) else entry
    text = str(text).replace('"', "").replace("'", "").replace(",", " ")
    if "==" in text:
        fields = {}
        for field in text.split():
            if "==" in field:
                key, _, val = field.partition("==")
                fields[key.strip().lower()] = val.strip()
        radio_name = fields.get("radio")
        try:
            station_count = int(fields["stations"]) if fields.get("stations") else None
        except ValueError:
            raise ValueError("--radio %r: 'stations==' must be an integer" % (entry,))
    else:
        fields = {}
        radio_name = text.strip() or None
        station_count = None
    if not radio_name:
        raise ValueError("Could not read a radio name from --radio %r" % (entry,))
    return {
        "radio": radio_name,
        "stations": station_count,
        "ssid": fields.get("ssid", default_ssid),
        "ssid_pw": fields.get("ssid_pw", default_ssid_pw),
        "security": fields.get("security", default_security),
        "eap_identity": fields.get("eap_identity", default_eap_identity),
        "eap_password": fields.get("eap_password", default_eap_password),
        "batch": fields.get("batch") or None,
        "rate_limit_dl": fields.get("rate_limit_dl", default_rate_limit_dl),
        "rate_limit_ul": fields.get("rate_limit_ul", default_rate_limit_ul),
    }


def station_batch_label(name: str) -> str | None:
    """A station's batch== label, read straight from its name ('B1_sta0007' -> 'B1', 'sta0007' -> None)."""
    idx = str(name).find("_" + STATION_PREFIX)
    return name[:idx] if idx > 0 else None


def group_stations_by_batch(all_stations: list[str], num_batches: int) -> list[list[str]]:
    """Group station names into batches, using each name's batch label when present.

    Falls back to a plain contiguous split - when none of the names carry a label.

    Args:
        all_stations (list[str]): Station names, in creation/discovery order.
        num_batches (int): Batch count to use when none of the names carry a batch label.

    Returns:
        list[list[str]]: One list of station names per batch. Labelled batches are ordered by each label's first
        appearance in all_stations; unlabelled batches are contiguous slices.

    Raises:
        ValueError: If num_batches is less than 1, or if some but not all station names carry a batch label.
    """
    labelled: dict[str, list[str]] = {}
    unlabelled: list[str] = []
    for name in all_stations:
        label = station_batch_label(name)
        if label is None:
            unlabelled.append(name)
        else:
            labelled.setdefault(label, []).append(name)

    if labelled:
        if unlabelled:
            raise ValueError("%d station(s) have no batch== label in their name while %d do - "
                             "add batch== to every --radio, or remove it from all of them" %
                             (len(unlabelled), sum(len(v) for v in labelled.values())))
        return list(labelled.values())

    # nobody used batch== - split into contiguous batches,
    if num_batches < 1:
        raise ValueError("--num_batches must be >= 1 (got %d)" % num_batches)
    total = len(all_stations)
    if total < num_batches:
        logger.warning("Station count (%d) < --num_batches (%d); using %d batch(es) of 1", total, num_batches, total)
        num_batches = max(total, 1)
    batch_size = total // num_batches   # floor: any leftover goes to the last batch
    batches = []
    for i in range(num_batches):
        start = i * batch_size
        end = total if i == num_batches - 1 else start + batch_size
        batches.append(all_stations[start:end])
    return batches


@dataclass
class StationData:
    """One station's data on its way into build_station_plan()'s registry."""
    name: str
    radio: str | None
    resource: str | int
    shelf: str | int
    ssid: str | None
    ssid_pw: str
    security: str
    eap_identity: str | None
    eap_password: str | None
    rate_limit_dl_bps: int | None
    rate_limit_ul_bps: int | None


def build_station_plan(radio, num_stations: int, use_existing_eid: str | None,
                       ssid: str | None, ssid_pw: str, security: str,
                       mgr: str, mgr_port: int, debug: bool = False,
                       allow_discovery: bool = False, eap_identity: str | None = None,
                       eap_password: str | None = None, rate_limit_dl: str = "",
                       rate_limit_ul: str = "") -> dict[str, dict]:
    """Build the station registry from whichever inputs are available.

    Chooses the source in order:
      * use_existing_eid - the stations already exist; nothing is created. Each station's radio is taken from a single
        `radio` if given, otherwise looked up per station from the manager ('parent dev').
      * radio - one 'stations==N' per radio spec; a lone bare radio with no count falls back to --num_stations.
        A spec may also override eap_identity==/eap_password==/rate_limit_dl==/rate_limit_ul== so different
        radios (e.g. different RADIUS logins with different assigned caps) get different per-station values.
      * discovery - when allow_discovery is set and neither of the above is given, every station already on the manager is used;
        each one's parent radio is resolved from the manager ('parent dev') so a discovered set can still be batch-reset.

    Args:
        radio (str | list | None): One --radio spec, a list of them, or None.
        num_stations (int): Count for a single bare radio spec.
        use_existing_eid (str | None): Comma/space list of station EIDs.
        ssid (str | None): Per-station SSID to record.
        ssid_pw (str): Per-station SSID password to record.
        security (str): Per-station security type to record.
        mgr (str): Manager host for the parent-dev and discovery lookups.
        mgr_port (int): Manager port for the parent-dev and discovery lookups.
        debug (bool): py-json debug on the probe connection.
        allow_discovery (bool): When True and neither radio nor use_existing_eid is given,
                                discover every station on the manager instead of raising.
        eap_identity (str | None): Default EAP identity; overridden per radio by eap_identity==.
        eap_password (str | None): Default EAP password; overridden per radio by eap_password==.
        rate_limit_dl (str): Default expected DL rate string; overridden per radio by rate_limit_dl==.
        rate_limit_ul (str): Default expected UL rate string; overridden per radio by rate_limit_ul==.

    Returns:
        dict[str, dict]: name -> per-station dict with keys 'radio', 'resource', 'eid' ('<shelf>.<resource>.<name>'),
        'ssid', 'ssid_pw', 'security', 'eap_identity', 'eap_password', 'rate_limit_dl_bps', 'rate_limit_ul_bps'
        (the last two are bps ints or None) and 'mac' (initially None). A station's batch, if any, is
        encoded in its name (see station_batch_label()), not stored here.

    Raises:
        ValueError: If use_existing_eid holds no parseable EIDs; if no station source is available
                    (no radio, no use_existing_eid, allow_discovery False); or if more than one radio spec omits 'stations==N'.
    """
    radio_specs = [radio] if isinstance(radio, str) else list(radio or [])
    default_dl_bps = parse_rate(rate_limit_dl) if rate_limit_dl else None
    default_ul_bps = parse_rate(rate_limit_ul) if rate_limit_ul else None

    def registry(rows: list[StationData]) -> dict[str, dict]:
        """Turn station rows into the name -> per-station dict registry."""
        return {
            row.name: {"radio": row.radio, "resource": row.resource,
                       "eid": "%s.%s.%s" % (row.shelf, row.resource, row.name),
                       "ssid": row.ssid, "ssid_pw": row.ssid_pw, "security": row.security,
                       "eap_identity": row.eap_identity, "eap_password": row.eap_password,
                       "rate_limit_dl_bps": row.rate_limit_dl_bps, "rate_limit_ul_bps": row.rate_limit_ul_bps,
                       "mac": None}
            for row in rows
        }

    if use_existing_eid:
        eids = [part.strip() for part in use_existing_eid.replace(" ", ",").split(",") if part.strip()]
        if not eids:
            raise ValueError("--use_existing_eid was given but no EIDs could be read from it")
        # a single radio pins every station to it; otherwise look each station's  radio up from the manager
        # so a mixed-radio list can still be reset
        provided_radio = (parse_radio_arg(radio_specs[0], ssid, ssid_pw, security)["radio"] if radio_specs else None)
        lf_conn = None if provided_radio else Realm(lfclient_host=mgr, lfclient_port=mgr_port, debug_=debug)
        entries = []
        for eid in eids:
            shelf, resource, name, *_ = LFUtils.name_to_eid(eid)
            station_radio = provided_radio
            if station_radio is None:
                port = (lf_conn.json_get("/port/1/%s/%s?fields=parent+dev" % (resource, name)) or {}).get("interface", {})
                if port.get("parent dev"):
                    station_radio = "%s.%s.%s" % (shelf, resource, port["parent dev"])
            entries.append(StationData(name=name, radio=station_radio, resource=resource, shelf=shelf,
                                       ssid=ssid, ssid_pw=ssid_pw, security=security,
                                       eap_identity=eap_identity, eap_password=eap_password,
                                       rate_limit_dl_bps=default_dl_bps, rate_limit_ul_bps=default_ul_bps))
        return registry(entries)

    specs = [parse_radio_arg(entry, ssid, ssid_pw, security, eap_identity, eap_password,
                             rate_limit_dl, rate_limit_ul) for entry in radio_specs]
    if not specs:
        if not allow_discovery:
            raise ValueError("--radio is required (e.g. --radio 'radio==1.1.wiphy0 stations==25')")
        # discover every station on the manager (not just this script's own naming) and resolve
        # each one's parent radio, so the discovered set can still be batch-reset without --radio
        lf_conn = Realm(lfclient_host=mgr, lfclient_port=mgr_port, debug_=debug)
        discovered = []
        for entry in lf_conn.station_list() or []:
            for eid in entry:
                shelf, resource, name, *_ = LFUtils.name_to_eid(eid)
                port = (lf_conn.json_get("/port/1/%s/%s?fields=parent+dev" % (resource, name)) or {}).get("interface", {})
                station_radio = ("%s.%s.%s" % (shelf, resource, port["parent dev"]) if port.get("parent dev") else None)
                discovered.append(StationData(name=name, radio=station_radio, resource=resource, shelf=shelf,
                                              ssid=ssid, ssid_pw=ssid_pw, security=security,
                                              eap_identity=eap_identity, eap_password=eap_password,
                                              rate_limit_dl_bps=default_dl_bps, rate_limit_ul_bps=default_ul_bps))
        return registry(sorted(discovered, key=lambda row: row.name))

    if len(specs) == 1 and specs[0]["stations"] is None:
        specs[0]["stations"] = num_stations
    missing_count = [spec["radio"] for spec in specs if spec["stations"] is None]
    if missing_count:
        raise ValueError("--radio needs 'stations==N' when more than one radio is given; missing for: %s" % ", ".join(missing_count))

    entries = []
    for radio_index, spec in enumerate(specs):
        shelf, resource, *_ = LFUtils.name_to_eid(spec["radio"])
        start_id = radio_index * RADIO_STATION_BLOCK
        name_prefix = "B%s_%s" % (spec["batch"], STATION_PREFIX) if spec["batch"] else STATION_PREFIX
        names = LFUtils.port_name_series(
            prefix=name_prefix,
            start_id=start_id,
            end_id=start_id + spec["stations"] - 1,
            padding_number=10000)
        spec_dl_bps = parse_rate(spec["rate_limit_dl"]) if spec["rate_limit_dl"] else None
        spec_ul_bps = parse_rate(spec["rate_limit_ul"]) if spec["rate_limit_ul"] else None
        for name in names:
            entries.append(StationData(name=name, radio=spec["radio"], resource=resource, shelf=shelf,
                                       ssid=spec["ssid"], ssid_pw=spec["ssid_pw"], security=spec["security"],
                                       eap_identity=spec["eap_identity"], eap_password=spec["eap_password"],
                                       rate_limit_dl_bps=spec_dl_bps, rate_limit_ul_bps=spec_ul_bps))
    return registry(entries)


def build_reconnect_ssids(ssid_list: str, ssid: str | None, ssid_pw: str) -> list[tuple[str, str]]:
    """Build the ordered list of SSIDs that batch resets reconnect onto (one per cycle).

    ssid_list wins if set; otherwise the single ssid is used. Each entry is 'ssid' or 'ssid:password'; a bare entry uses ssid_pw.

    Args:
        ssid_list (str): Comma list of 'ssid[:pw]' (the --ssid_list value).
        ssid (str | None): Single SSID fallback (the --ssid value).
        ssid_pw (str): Default password for entries with no ':pw' part.

    Returns:
        list[tuple[str, str]]: (ssid, password) tuples in rotation order. Empty
        when neither ssid_list nor ssid was given.
    """
    def split_entry(entry: str) -> tuple[str, str]:
        name, sep, password = entry.partition(":")
        return name.strip(), (password.strip() if sep else ssid_pw)

    if ssid_list:
        entries = ssid_list.split(",")
    elif ssid:
        entries = [ssid]
    else:
        return []
    return [split_entry(entry) for entry in entries if entry and entry.strip()]


class BatchResetTest(Realm):
    """Clients batch-reset throughput test with rate-limit verification.

    Creates stations, splits them into contiguous batches and runs Layer-3 traffic. Every batch_reset_interval one batch
    is reset (stop traffic, randomize MACs, reconnect to the next SSID in the rotation, re-auth, resume traffic) and its
    per-station throughput is checked against the expected rate limit while the other batches keep running. Cycles batch
    by batch until test_duration elapses, then writes CSVs and an HTML report.

    handle_toolbox() also drives this class for --toolbox mode ( to run building-block action(s), no timed loop, no report).
    """

    def __init__(self,
                 # connection
                 lfclient_host: str = "localhost",
                 lfclient_port: int = 8080,
                 upstream_port: str = "1.1.eth1",
                 radio=None,
                 num_stations: int = 50,
                 use_existing_eid: str | None = None,
                 allow_discovery: bool = False,
                 num_batches: int = 5,
                 # security / EAP
                 security: str = "wpa2",
                 ssid: str | None = None,
                 ssid_list: str = "",
                 ssid_pw: str = "[BLANK]",
                 key_mgmt: str = "WPA-EAP",
                 eap: str = "PEAP",
                 eap_identity: str | None = None,
                 eap_password: str | None = None,
                 eap_anonymous_identity: str = "",
                 eap_phase1: str = "",
                 eap_phase2: str = "",
                 pairwise_cipher: str = "[BLANK]",
                 groupwise_cipher: str = "[BLANK]",
                 ca_cert: str = "",
                 client_cert: str = "",
                 private_key: str = "",
                 pk_passwd: str = "",
                 pac_file: str = "",
                 # traffic (endpoint types / per-connection rates)
                 traffic_type: str = "tcp+udp",
                 direction: str = "bidi",
                 rate_mode: str = "per_station",
                 traffic_rate: str = "5Mbps",
                 payload_size: str = "",   # '' = default; fixed (1472 / MTU / AUTO) or 'lo-hi' range (64-1472)
                 # durations - seconds as int, or a string like '30m' / '1800'
                 test_duration: str | int = 1800,
                 batch_reset_interval: str | int = 0,   # 0 = no batch resets, plain throughput run
                 polling_interval: str | int = 10,
                 settle_time: str | int = 10,
                 connect_timeout: str | int = 120,
                 wait_for_ip_sec: str | int = 500,
                 rate_limit_window: str | int = 10,
                 # rate-limit verification - '' disables, else a rate string like '6Mbps'
                 rate_limit_dl: str = "",
                 rate_limit_ul: str = "",
                 rate_limit_tolerance_percent: float = 5.0,
                 randomize_mac: bool = True,
                 # lifecycle / report
                 local_lf_report_dir: str = "",
                 results_dir_name: str = "lf_batch_reset",
                 no_pre_cleanup: bool = False,
                 no_cleanup: bool = False,
                 debug: bool = False,
                 args: argparse.Namespace | None = None):
        """Build the station plan, reconnect SSID rotation, and batches, then record every test setting.

        Args:
            lfclient_host (str): LANforge manager hostname/IP.
            lfclient_port (int): LANforge manager HTTP port.
            upstream_port (str): Upstream EID used when building cross-connects.
            radio (str | list | None): One --radio spec, a list of them, or None. See build_station_plan.
            num_stations (int): Count for a single bare radio spec. See build_station_plan.
            use_existing_eid (str | None): Comma/space list of existing station EIDs to reuse
                instead of creating stations. See build_station_plan.
            allow_discovery (bool): When True and neither radio nor use_existing_eid is given,
                discover every station already on the manager. See build_station_plan.
            num_batches (int): Number of batches to split all_stations into for reset cycling.
                Ignored if any station has a batch== label in its name - see group_stations_by_batch().
            security (str): Security type recorded per station and used for the connect profile.
            ssid (str | None): Single SSID fallback for both stations and reconnect rotation.
            ssid_list (str): Comma list of 'ssid[:pw]' entries for the reconnect rotation;
                overrides ssid when set. See build_reconnect_ssids.
            ssid_pw (str): Default password for stations and for ssid_list entries with no ':pw' part.
            key_mgmt (str): wpa_supplicant key_mgmt string for the station security profile.
            eap (str): EAP method (e.g. 'PEAP'); combined with security to decide is_eap.
            eap_identity (str | None): EAP identity.
            eap_password (str | None): EAP password.
            eap_anonymous_identity (str): EAP anonymous identity.
            eap_phase1 (str): EAP phase1 string.
            eap_phase2 (str): EAP phase2 string.
            pairwise_cipher (str): Pairwise cipher for the station security profile.
            groupwise_cipher (str): Group cipher for the station security profile.
            ca_cert (str): CA certificate file for EAP.
            client_cert (str): Client certificate file for EAP.
            private_key (str): Private key file for EAP.
            pk_passwd (str): Private key password for EAP.
            pac_file (str): PAC file for EAP-FAST.
            traffic_type (str): Key into TRAFFIC_TYPE_TO_ENDP_TYPES selecting the L3 endpoint type(s).
            direction (str): 'dl', 'ul', or 'bidi' - which directions carry traffic.
            rate_mode (str): 'per_station' or 'intended_load'; the latter divides traffic_rate by num_stations.
            traffic_rate (str): Per-connection (or aggregate, in intended_load mode) rate string, e.g. '5Mbps'.
            payload_size (str): '' for the CX profile default; a fixed size or a 'lo-hi' range.
            test_duration (str | int): Total test run time; seconds as int or a duration string like '30m'.
            batch_reset_interval (str | int): Seconds between batch resets; 0 disables resets (plain throughput run).
            polling_interval (str | int): Seconds between status polls.
            settle_time (str | int): Seconds to let a batch settle after reconnect before resuming checks.
            connect_timeout (str | int): Seconds to wait for a station to associate.
            wait_for_ip_sec (str | int): Seconds to wait for a station to get an IP.
            rate_limit_window (str | int): Seconds of throughput samples used to verify a batch's rate limit.
            rate_limit_dl (str): Expected downlink rate string for verification; '' disables the DL check.
            rate_limit_ul (str): Expected uplink rate string for verification; '' disables the UL check.
            rate_limit_tolerance_percent (float): Allowed percent deviation from the expected rate limit.
            randomize_mac (bool): Randomize each station's MAC on reset.
            local_lf_report_dir (str): Local directory to write the report under; '' uses the default.
            results_dir_name (str): Name of the report subdirectory.
            no_pre_cleanup (bool): Skip removing pre-existing stations before the run.
            no_cleanup (bool): Skip removing stations/cross-connects after the run.
            debug (bool): py-json debug on the manager connection.
            args (argparse.Namespace | None): Parsed CLI args, kept for reference by callers (e.g. handle_toolbox).
        """
        super().__init__(lfclient_host=lfclient_host, lfclient_port=lfclient_port, debug_=debug)
        self.args = args
        self.report = None
        self.mgr = lfclient_host
        self.debug = debug
        self.station_details = build_station_plan(radio, num_stations, use_existing_eid, ssid, ssid_pw,
                                                  security, lfclient_host, lfclient_port, debug, allow_discovery,
                                                  eap_identity, eap_password, rate_limit_dl, rate_limit_ul)
        self.reconnect_ssids = build_reconnect_ssids(ssid_list, ssid, ssid_pw)
        self.all_stations = list(self.station_details)
        self.batches = group_stations_by_batch(self.all_stations, num_batches) if self.all_stations else []
        self.num_stations = len(self.all_stations)
        self.num_batches = len(self.batches) if self.batches else num_batches
        batch_sizes = [len(b) for b in self.batches] if self.batches else [0]
        self.batch_size = batch_sizes[0]
        self.batch_size_label = ("%d" % batch_sizes[0] if len(set(batch_sizes)) == 1 else "%d-%d" % (min(batch_sizes), max(batch_sizes)))
        self.radios = list(dict.fromkeys(self.station_details[n]["radio"] for n in self.all_stations))

        # security / EAP
        self.upstream_port = upstream_port
        self.security = security
        self.ssid = ssid
        self.ssid_pw = ssid_pw
        self.key_mgmt = key_mgmt
        self.eap = eap
        self.eap_identity = eap_identity
        self.eap_password = eap_password
        self.eap_anonymous_identity = eap_anonymous_identity
        self.eap_phase1 = eap_phase1
        self.eap_phase2 = eap_phase2
        self.pairwise_cipher = pairwise_cipher
        self.groupwise_cipher = groupwise_cipher
        self.ca_cert = ca_cert
        self.client_cert = client_cert
        self.private_key = private_key
        self.pk_passwd = pk_passwd
        self.pac_file = pac_file
        # EAP is on (the default) unless --security is open or --eap is cleared (NONE / DEFAULT)
        self.is_eap = (str(security).lower() not in ("open", "none", "")
                       and str(eap).strip().upper() not in ("", "NONE", "DEFAULT"))
        if str(security).lower() in ("open", "none", ""):
            self.ieee80211w = 0
        elif str(security).lower() == "wpa3":
            self.ieee80211w = 2                          # PMF required for WPA3
        else:
            self.ieee80211w = 1

        # traffic - endpoint types + per-connection rates from the raw CLI
        self.traffic_type = traffic_type
        self.direction = direction
        self.rate_mode = rate_mode
        rate_bps = parse_rate(traffic_rate)
        if rate_mode == "intended_load" and self.num_stations:
            rate_bps //= self.num_stations          # traffic_rate is an aggregate -> per station
        self.endp_types = list(TRAFFIC_TYPE_TO_ENDP_TYPES[traffic_type])
        self.dl_enabled = direction in ("dl", "bidi")
        self.ul_enabled = direction in ("ul", "bidi")
        self.dl_bps = rate_bps if self.dl_enabled else 0   # 0 => that direction carries no traffic
        self.ul_bps = rate_bps if self.ul_enabled else 0
        self.payload_size = payload_size   # '' => leave the CX profile default; else set on both sides

        # durations - accept ints or strings like '30m', normalised to seconds here
        self.test_duration = duration_to_seconds(test_duration)
        self.batch_reset_interval = duration_to_seconds(batch_reset_interval)
        self.polling_interval = duration_to_seconds(polling_interval)
        self.settle_time = duration_to_seconds(settle_time)
        self.connect_timeout = duration_to_seconds(connect_timeout)
        self.wait_for_ip_sec = duration_to_seconds(wait_for_ip_sec)
        self.rate_limit_window = duration_to_seconds(rate_limit_window)
        # batch resets step through reconnect_ssids; with resets enabled there must
        # be at least one SSID (ssid= or ssid_list=) to reconnect onto
        if self.batch_reset_interval > 0 and not self.reconnect_ssids:
            raise ValueError("Batch resets are enabled (batch_reset_interval > 0) but no reconnect "
                             "SSID was given - pass ssid= or ssid_list=")

        # rate-limit verification - '' disables the check, else parse the rate string to bps
        self.rate_limit_dl_bps = parse_rate(rate_limit_dl) if rate_limit_dl else None
        self.rate_limit_ul_bps = parse_rate(rate_limit_ul) if rate_limit_ul else None
        self.rate_limit_tolerance_percent = rate_limit_tolerance_percent
        self.randomize_mac = randomize_mac

        # lifecycle / report
        self.local_lf_report_dir = local_lf_report_dir
        self.results_dir_name = results_dir_name
        self.no_pre_cleanup = no_pre_cleanup
        self.no_cleanup = no_cleanup
        self.use_existing_eid = bool(use_existing_eid)

        # runtime state
        self.cx_profile = self.new_l3_cx_profile()
        self.cx_profile.name_prefix = STATION_PREFIX
        self.station_profiles = {}
        self.cycle_rows = []          # one row per batch reset
        self.rate_limit_rows = []     # one row per station per verification
        self.overall_throughput_rows = []          # aggregate throughput samples (background thread, whole test)
        self.test_start_time = None
        self._throughput_stop = threading.Event()
        self._throughput_thread = None
        # CSVs streamed row-by-row during run so data survives a kill.
        self._details_csv_path = None
        self._throughput_csv_path = None

    def station_eid(self, name: str) -> str:
        """Return the 'shelf.resource.name' EID string for a station name.

        Args:
            name (str): Station name, e.g. 'sta0001'.

        Returns:
            str: The port EID recorded in station_details.
        """
        return self.station_details[name]["eid"]

    @staticmethod
    def _cx_names(name: str, endp_type: str) -> tuple[str, str, str]:
        """Return the deterministic cross-connect and endpoint names for one station + endpoint type.

        The names are '<station>-tcp' / '<station>-udp' for the cross-connect and '<cx>-A' / '<cx>-B' for its two endpoints.

        Args:
            name (str): Station name, e.g. 'sta0007'.
            endp_type (str): One LANforge endpoint type - 'lf_tcp' or 'lf_udp' (anything not 'lf_tcp' is treated as udp).

        Returns:
            tuple[str, str, str]: (cx_name, side_a_endpoint, side_b_endpoint), e.g. ('sta0007-tcp', 'sta0007-tcp-A', 'sta0007-tcp-B').
        """
        cx = "%s-%s" % (name, "tcp" if endp_type == "lf_tcp" else "udp")
        return cx, cx + "-A", cx + "-B"

    @staticmethod
    def _shorten_list(items: list) -> list:
        """Shorten a list for logging: first 3 items, '...', last 2 - unchanged if 5 or fewer.

        Args:
            items (list): Items to shorten (e.g. station or cross-connect names).

        Returns:
            list: items unchanged if len(items) <= 5, else items[:3] + ['...'] + items[-2:].
        """
        return items if len(items) <= 5 else items[:3] + ["..."] + items[-2:]

    def _configure_station_profile(self, station_profile, ssid: str, password: str,
                                   security: str | None = None, eap_identity: str | None = None,
                                   eap_password: str | None = None) -> None:
        """Apply SSID and security settings to a station profile.

        WPA-PSK (key_mgmt + psk + 802.1X flag), or
        open (nothing more), or
        802.1X EAP (key_mgmt + eap params + 802.1X flag)

        Args:
            station_profile: The py-json station profile to mutate in place.
            ssid (str): SSID to set on the profile.
            password (str): PSK / key passphrase; '[BLANK]' when empty.
            security (str | None): Security override; defaults to self.security.
            eap_identity (str | None): EAP identity override; defaults to self.eap_identity.
            eap_password (str | None): EAP password override; defaults to self.eap_password.
        """
        sec = security or self.security
        station_profile.use_security(sec, ssid, password if password else "[BLANK]")
        station_profile.set_command_flag("add_sta", "create_admin_down", 1)
        station_profile.set_command_param("add_sta", "ieee80211w", self.ieee80211w)

        if not self.is_eap:
            if str(sec).lower() not in ("open", "none", ""):
                station_profile.set_wifi_extra(key_mgmt=self.key_mgmt, psk=password if password else "[BLANK]")
                station_profile.set_command_flag("add_sta", "8021x_radius", 1)
            return

        station_profile.set_command_flag("add_sta", "8021x_radius", 1)
        wifi_extra = dict(
            key_mgmt=self.key_mgmt,
            pairwise=self.pairwise_cipher,
            group=self.groupwise_cipher,
            eap=self.eap,
            identity=eap_identity or self.eap_identity,
            anonymous_identity=self.eap_anonymous_identity if self.eap_anonymous_identity else "[BLANK]",
            passwd=eap_password or self.eap_password,
            phase1=self.eap_phase1 if self.eap_phase1 else "[BLANK]",
            phase2=("auth=%s" % self.eap_phase2) if self.eap_phase2 else "[BLANK]",
        )
        if self.eap == "TLS" or self.ca_cert:
            wifi_extra["ca_cert"] = self.ca_cert or "[BLANK]"
        if self.eap == "TLS" or self.client_cert:
            wifi_extra["client_cert"] = self.client_cert or "[BLANK]"
        if self.eap == "TLS" or self.private_key:
            wifi_extra["private_key"] = self.private_key or "[BLANK]"
        if self.eap == "TLS" or self.pk_passwd:
            wifi_extra["pk_password"] = self.pk_passwd or "[BLANK]"
        if self.eap == "FAST" or self.pac_file:
            wifi_extra["pac_file"] = self.pac_file or "[BLANK]"
        station_profile.set_wifi_extra(**wifi_extra)

    def _enable_8021x_radius(self, station_names: list[str]) -> None:
        """Turn on the 802.1X / RADIUS add_sta flag for the given stations.

        Args:
            station_names (list[str]): Station names to update.
        """
        for name in station_names:
            station = self.station_details[name]
            if not station["radio"]:
                continue
            self.json_post("cli-json/add_sta", {
                "shelf": 1,
                "resource": station["resource"],
                "sta_name": name,
                "radio": LFUtils.name_to_eid(station["radio"])[2],
                "flags": 33554432,
                "flags_mask": 33554432,
            }, debug_=self.debug)

    def _endpoint_rx_rates(self) -> dict[str, float]:
        """Read the current receive rate of every endpoint on the LANforge.

        Uses 'rx rate (last)' - the rate over just the last measurement interval, so a batch dropping out during a reset
        shows as a sharp step rather than being smeared away by the ~30s moving average of plain 'rx rate'.

        Returns:
            dict[str, float]: endpoint name -> rx rate in bits/sec (0 when the value is missing). Empty if the query returns nothing.
        """
        response = self.json_get("/endp?fields=name,rx+rate,rx+rate+(last)")
        rx_rates = {}
        if not response or "endpoint" not in response:
            return rx_rates
        endpoints = response["endpoint"]
        if isinstance(endpoints, dict):
            endpoints = [endpoints]
        for item in endpoints:
            for _field_name, endpoint in item.items():
                if isinstance(endpoint, dict) and "name" in endpoint:
                    rate = endpoint.get("rx rate (last)", endpoint.get("rx rate", 0))
                    rx_rates[endpoint["name"]] = rate or 0
        return rx_rates

    def _wait_for_station_ips(self, station_names: list[str], timeout: float, require_all: bool = False) -> dict[str, str]:
        """Poll ports until each has an IPv4 address or the timeout expires.

        Also refreshes station_details[name]['mac'] whenever a MAC is seen.

        Args:
            station_names (list[str]): Station names to poll.
            timeout (float): Maximum seconds to wait.
            require_all (bool): When True, raise RuntimeError if any station is still missing an IPv4 once the timeout expires.

        Returns:
            dict[str, str]: station name -> IPv4 address, for the stations that got one (may be a subset of station_names on timeout).

        Raises:
            RuntimeError: If require_all is True and any station has no IPv4 within timeout.
        """
        unassigned_ip_values = {"0.0.0.0", "NA", "", "DELETED", "AUTO", None}
        deadline = time.time() + timeout
        stations_with_ip = {}
        while time.time() < deadline:
            stations_with_ip = {}
            for name in station_names:
                station = self.station_details[name]
                response = self.json_get("/port/1/%s/%s?fields=alias,ip,mac" % (station["resource"], name))
                interface = response.get("interface", {}) if response else {}
                ip_address = interface.get("ip")
                if ip_address not in unassigned_ip_values:
                    stations_with_ip[name] = ip_address
                    if interface.get("mac"):
                        station["mac"] = interface["mac"]
            if len(stations_with_ip) == len(station_names):
                break
            time.sleep(min(self.polling_interval, max(1, int(deadline - time.time()))))

        if require_all:
            logger.info("Stations with an IPv4: %d / %d", len(stations_with_ip), len(station_names))
            if len(stations_with_ip) < len(station_names):
                stations_without_ip = sorted(set(station_names) - set(stations_with_ip))
                raise RuntimeError("%d/%d stations did not get an IPv4 within %ds - "
                                   "aborting the test" % (len(stations_without_ip), len(station_names), timeout))
        return stations_with_ip

    def _prefix_station_ports(self) -> list[tuple[str, str]]:
        """List every station port on LANforge from a live query (not scoped to this script's own naming).

        Returns:
            list[tuple[str, str]]: (resource, name) for each station.
        """
        found = []
        for entry in self.station_list() or []:
            for eid in entry:
                _shelf, resource, name, *_ = LFUtils.name_to_eid(eid)
                found.append((resource, name))
        return found

    def pre_cleanup(self) -> None:
        """Remove every station, cross-connect, and L3 endpoint on the manager before a run."""
        logger.info("Cleanup: Removing every existing station, cross-connect, and L3 endpoint")
        self.delete_cross_connects("all")
        stations = self._prefix_station_ports()
        if stations:
            logger.info("Deleting stations: %s", self._shorten_list([name for _resource, name in stations]))
            for resource, name in stations:
                self.json_post("/cli-json/rm_vlan", {"shelf": 1, "resource": resource, "port": name})
        time.sleep(2)

    def _check_connect_config(self) -> None:
        """Fail early if the settings needed to associate new stations are incomplete.

        Checks the per-station eap_identity/eap_password recorded in station_details (each already
        resolved to its radio's eap_identity==/eap_password== override, or the global --eap_identity/
        --eap_password fallback), not just the global values - a run with no global --eap_identity
        but an eap_identity== on every --radio is valid.

        Raises:
            RuntimeError: If no SSID is set, or EAP is enabled with any station missing an identity,
                a password (non-TLS), or no private key / client cert test-wide (TLS).
        """
        if not self.ssid:
            raise RuntimeError("No SSID set - pass ssid= (the SSID stations connect to)")
        if not self.is_eap:
            return
        missing_identity = [name for name in self.all_stations if not self.station_details[name]["eap_identity"]]
        if missing_identity:
            raise RuntimeError("EAP is enabled but eap_identity is not set for %d station(s) - pass "
                               "--eap_identity, or eap_identity== on their --radio (set eap='NONE' for "
                               "plain WPA-PSK / open)" % len(missing_identity))
        if self.eap == "TLS":
            if not (self.private_key or self.client_cert):
                raise RuntimeError("EAP-TLS needs private_key= (or client_cert=)")
        else:
            missing_password = [name for name in self.all_stations if not self.station_details[name]["eap_password"]]
            if missing_password:
                raise RuntimeError("EAP method %s needs eap_password= for %d station(s) - pass "
                                   "--eap_password, or eap_password== on their --radio" % (self.eap, len(missing_password)))

    def create_stations(self) -> None:
        """Create (or, with --use_existing_eid, just bring up) all stations.

        Creates one station profile per (radio, ssid/security/eap-identity) group - a physical radio shared by multiple
        --radio entries with different eap_identity==/ssid==/etc (e.g. 5 RADIUS logins on one radio) still gets each
        group its own real identity, matching how reset_batch() already regroups by identity for reconnects. Enables
        802.1X if needed, admin-ups every station and waits for IPv4.

        Raises:
            RuntimeError: If the connect config is incomplete (no SSID, or EAP is on with no identity / password / TLS
                key), or from _wait_for_station_ips if a station never gets an IPv4.
        """
        if self.use_existing_eid:
            # stations already exist (--use_existing_eid): only bring them up
            logger.info("Using %d existing station(s); skipping creation", self.num_stations)
            for name in self.all_stations:
                self.admin_up(self.station_eid(name))
            self._wait_for_station_ips(self.all_stations, self.wait_for_ip_sec, require_all=True)
            return
        self._check_connect_config()
        logger.info("Creating %d station(s) across %d radio(s): %s",
                    self.num_stations, len(self.radios), ", ".join(self.radios))
        for radio in self.radios:
            radio_station_names = [name for name in self.all_stations if self.station_details[name]["radio"] == radio]
            groups: dict[tuple, list[str]] = {}
            for name in radio_station_names:
                station = self.station_details[name]
                key = (station["ssid"], station["ssid_pw"], station["security"],
                       station["eap_identity"], station["eap_password"])
                groups.setdefault(key, []).append(name)
            for (ssid, ssid_pw, security, eap_identity, eap_password), group_names in groups.items():
                logger.info("Creating %d station(s) on radio %s (identity: %s)",
                            len(group_names), radio, eap_identity or "-")
                station_profile = self.new_station_profile()
                station_profile.mode = 0
                self._configure_station_profile(station_profile, ssid, ssid_pw, security, eap_identity, eap_password)
                station_profile.create(radio=radio, sta_names_=group_names, debug=self.debug, timeout=self.connect_timeout)
                self.station_profiles.setdefault(radio, []).append(station_profile)
        if self.is_eap:
            self._enable_8021x_radius(self.all_stations)
        logger.info("Bringing all stations up (admin-up)")
        for name in self.all_stations:
            self.admin_up(self.station_eid(name))
        self._wait_for_station_ips(self.all_stations, self.wait_for_ip_sec, require_all=True)

    def build_cross_connects(self) -> None:
        """Create the Layer-3 cross-connects between every station and upstream."""
        self.cx_profile.side_a_min_bps = self.ul_bps
        self.cx_profile.side_b_min_bps = self.dl_bps
        self.cx_profile.side_a_max_bps = 0
        self.cx_profile.side_b_max_bps = 0
        if self.payload_size != "":
            parts = [p.strip() for p in self.payload_size.replace(":", "-").split("-") if p.strip()]
            pdu_min, pdu_max = (parts[0], parts[1]) if len(parts) == 2 else (self.payload_size.strip(),) * 2
            self.cx_profile.side_a_min_pdu = self.cx_profile.side_b_min_pdu = pdu_min
            self.cx_profile.side_a_max_pdu = self.cx_profile.side_b_max_pdu = pdu_max

        logger.info("Creating cross-connection(s) (%s): DL %d bps, UL %d bps, payload %s",
                    ",".join(self.endp_types), self.dl_bps, self.ul_bps, self.payload_size or "auto")
        failed_count = 0
        for name in self.all_stations:
            for endp_type in self.endp_types:
                cx_name = self._cx_names(name, endp_type)[0]
                created_cxs, _endpoints = self.cx_profile.create(
                    endp_type=endp_type,
                    side_a=[self.station_eid(name)],
                    side_b=self.upstream_port,
                    cx_name=cx_name,
                    suppress_related_commands=True,
                    sleep_time=0)
                if not created_cxs:
                    failed_count += 1
        if failed_count:
            logger.warning("Failed to create %d cross-connect(s)", failed_count)

    def batch_selector(self, selector: str | int | None) -> list[str] | None:
        """Return this test's stations for a batch selector ('batchN' / 'N'), or None if selector isn't one.

        The single place that validates a batch selector - every caller (resolve_existing_stations,
        --reset_batch, --del_cxs, --del_stations) routes through here, so the out-of-range check and
        the mistaken-label check below only need to exist once.

        Args:
            selector: A selector value, as passed to resolve_existing_stations() or to the
                --reset_batch / --del_cxs / --del_stations handling in handle_toolbox().

        Returns:
            list[str] | None: The stations in that 1-based batch, or None when selector
            does not look like a batch token (caller should try another interpretation).

        Raises:
            ValueError: If a batch selector is outside 1..num_batches, or selector is actually
                one of this test's batch labels (e.g. 'vip') used where a position was expected -
                selectors are positional, not by label.
        """
        token = batch_token(selector)
        if token is None:
            # Selectors are positional (--reset_batch 2, batch2), not by label - if the token
            # matches one of this test's batch labels, give a helpful error instead of a silent None.
            label = str(selector).strip() if selector is not None else None
            for position, batch in enumerate(self.batches, start=1):
                if label is not None and batch and station_batch_label(batch[0]) == label:
                    raise ValueError("'%s' is a batch label (batch %d) - selectors are positional, "
                                     "use 'batch%d' or '%d' instead" % (label, position, position, position))
            return None
        batch_index = int(token) - 1
        if not 0 <= batch_index < self.num_batches:
            raise ValueError("Batch %s out of range (1..%d)" % (token, self.num_batches))
        return list(self.batches[batch_index])

    def _query_cxs(self) -> list:
        """get_all_cxs(), retried once before treating a failure as "no cross-connects"."""
        existing_cxs = self.get_all_cxs()
        if existing_cxs is None:
            time.sleep(1)
            existing_cxs = self.get_all_cxs()
        return existing_cxs or []

    def delete_cross_connects(self, selector: str | int | None) -> bool:
        """Resolve a --del_cxs selector and delete the matching cross-connects.

        For a batch selector, deletes whatever cross-connects actually exist for those stations
        (tcp, udp, or both) by live discovery - not a name guess built from --traffic_type, which
        may not match what the cx's were actually created with.

        Args:
            selector: None / '' / 'all' (every cross-connect on the manager); an int or
                'batchN' / 'N' (this test's stations in that 1-based batch); or a comma
                list of station names / EIDs / cross-connect name fragments.

        Returns:
            bool: True if every targeted cross-connect is confirmed gone after this pass.

        Raises:
            ValueError: If a batch selector is outside 1..num_batches.
        """
        text = "" if selector is None else str(selector).strip()
        batch_names = self.batch_selector(text)
        existing_cxs = self._query_cxs()

        if batch_names is not None:
            # whatever cx's actually exist for these stations (tcp, udp, both) - not a guess built
            # from --traffic_type, which may not match what the cx's were actually created with
            station_prefixes = tuple(name + "-" for name in batch_names)
            cx_list = [cx for cx in existing_cxs if cx.startswith(station_prefixes)]
        elif not text or text.lower() == "all":
            cx_list = list(existing_cxs)
        else:
            cx_list = [part.strip() for part in text.split(",") if part.strip()]
        if not cx_list:
            logger.warning("No cross-connects found on %s - nothing to act on", self.mgr)
            return True
        logger.info("Deleting cross-connections: %s", self._shorten_list(cx_list))

        for cx_name in cx_list:
            matched_cx = self.is_cx_exists(cx_name, existing_cxs)
            if not matched_cx:
                continue
            self.rm_cx(matched_cx)
            if matched_cx.endswith("-tcp") or matched_cx.endswith("-udp"):
                self.rm_endp(matched_cx + "-A")
                self.rm_endp(matched_cx + "-B")

        still_present = [cx for cx in cx_list if self.is_cx_exists(cx, self._query_cxs())]
        action_success = not still_present
        if action_success:
            logger.info("Completed deleting %d cross-connection(s).", len(cx_list))
        else:
            logger.error("Completed deleting cross-connections with errors - %d of %d still present: %s",
                         len(still_present), len(cx_list), self._shorten_list(still_present))
        return action_success

    def delete_stations(self, selector: str | int | None) -> bool:
        """Resolve a --del_stations selector and delete the matching station ports.

        Args:
            selector: None / '' / 'all' (every WIFI-STA port on the manager); an int or
                'batchN' / 'N' (this test's stations in that 1-based batch); or a comma
                list of station names / EIDs.

        Returns:
            bool: True if every targeted station was deleted; False if the manager could
            not be queried or any deletion failed.

        Raises:
            ValueError: If a batch selector is outside 1..num_batches.
        """
        existing_stas = self.get_all_stations()
        if existing_stas is None:
            logger.error("Toolbox: Failed to query stations from LANforge manager")
            return False

        text = "" if selector is None else str(selector).strip()
        batch_names = self.batch_selector(text)
        if batch_names is not None:
            sta_list = [self.station_eid(name) for name in batch_names]
        elif not text or text.lower() == "all":
            sta_list = list(existing_stas)
        else:
            sta_list = [part.strip() for part in text.split(",") if part.strip()]

        shown = self._shorten_list(sta_list)
        logger.info("Toolbox: Deleting specified stations: %s", shown)
        action_success = True
        deleted_count = 0
        for sta_name in sta_list:
            matched_sta = self.is_port_exists(sta_name, existing_stas)
            if matched_sta:
                logger.info("Deleting station '%s'", matched_sta)
                self.admin_down(matched_sta)
                res = self.rm_port(matched_sta, check_exists=False)
                if res is False or res is None:
                    logger.error("Toolbox: Failed to delete station '%s'.", matched_sta)
                    action_success = False
                else:
                    deleted_count += 1
            else:
                logger.info("Requested station '%s' not found on LANforge manager (already deleted).", sta_name)
                deleted_count += 1

        if action_success:
            logger.info("Completed deleting %d station(s).", deleted_count)
        else:
            logger.error("Completed deleting stations with errors (%d of %d succeeded).", deleted_count, len(sta_list))
        return action_success

    def filter_existing(self, station_names: list[str]) -> list[str]:
        """Keep only the station names that currently exist as ports on LANforge.

        Args:
            station_names (list[str]): Candidate station names.

        Returns:
            list[str]: The subset whose ports exist right now.
        """
        return [name for name in station_names if self.port_exists("1.%s.%s" % (self.station_details[name]["resource"], name))]

    # --- traffic control ---
    def _set_cross_connect_state(self, station_names: list[str], state: str) -> None:
        """Set the CX state of every cross-connect belonging to these stations.

        Args:
            station_names (list[str]): Stations whose cross-connects to set.
            state (str): LANforge CX state, e.g. 'RUNNING' or 'STOPPED'.
        """
        for name in station_names:
            for endp_type in self.endp_types:
                cx = self._cx_names(name, endp_type)[0]
                self.json_post("/cli-json/set_cx_state", {"test_mgr": "default_tm", "cx_name": cx, "cx_state": state})

    def start_traffic(self, station_names: list[str] | None = None, context: str | None = None) -> None:
        """Set the cross-connects for the given stations to RUNNING.

        Args:
            station_names (list[str] | None): Stations to start; None means
                all stations.
            context (str | None): Optional 'cycle N | batch M' prefix for the log line.
        """
        station_names = station_names or self.all_stations
        self._set_cross_connect_state(station_names, "RUNNING")
        logger.info("%sStarting traffic on %d station(s)", context + " | " if context else "", len(station_names))

    def stop_traffic(self, station_names: list[str] | None = None, context: str | None = None) -> None:
        """Set the cross-connects for the given stations to STOPPED.

        Args:
            station_names (list[str] | None): Stations to stop; None means all stations.
            context (str | None): Optional 'cycle N | batch M' prefix for the log line.
        """
        station_names = station_names or self.all_stations
        self._set_cross_connect_state(station_names, "STOPPED")
        logger.info("%sStopping traffic on %d station(s)", context + " | " if context else "", len(station_names))

    # --- batch reset ---
    def next_reconnect_ssid(self, cycle_number: int) -> tuple[str, str]:
        """The (ssid, password) this cycle reconnects onto - entry (cycle_number - 1) of reconnect_ssids."""
        return self.reconnect_ssids[(cycle_number - 1) % len(self.reconnect_ssids)]

    def reset_batch(self, batch_index: int, cycle_number: int, target_ssid: str, target_password: str) -> dict:
        """Reset one batch: stop traffic, admin-down, re-MAC, reconnect onto target_ssid, re-auth, admin-up and wait for IPv4.

        Re-auth is grouped by each station's own (eap_identity, eap_password) - recorded per station
        at creation from --radio's eap_identity==/eap_password== - so a batch spanning multiple radios
        (e.g. two radios sharing one RADIUS login, split because one radio can't hold every station)
        still authenticates each station with its own login, not just the first station's.

        Args:
            batch_index (int): 0-based index into self.batches.
            cycle_number (int): 1-based cycle counter, used only for log labels.
            target_ssid (str): SSID to reconnect the batch onto.
            target_password (str): Passphrase for target_ssid ('' / '[BLANK]' for pure EAP / open).

        Returns:
            dict: Keys 'batch_index', 'cycle_number', 'stations' (list of names), 'ssid' (reconnect SSID), 'ips' (set of stations that got an
            IPv4), 'old_mac_by_station' and 'new_mac_by_station' (name -> MAC dicts).
        """
        station_names = self.batches[batch_index]
        tag = "cycle %d | batch %d" % (cycle_number, batch_index + 1)
        old_mac_by_station = {name: self.station_details[name]["mac"] for name in station_names}
        reset_start = time.time()

        logger.info("%s | %d station(s): %s", tag, len(station_names), self._shorten_list(station_names))
        self.stop_traffic(station_names, context=tag)

        logger.info("%s | Reconnecting %d station(s) to SSID '%s'%s", tag, len(station_names), target_ssid,
                    " with randomize MAC." if self.randomize_mac else "")
        for name in station_names:
            self.admin_down(self.station_eid(name))
        time.sleep(2)

        # reconfigure each station: new MAC + new SSID, same security settings. Grouped by
        # (eap_identity, eap_password) since a batch can span multiple radios / RADIUS logins.
        new_mac_by_station = {}
        groups: dict[tuple, list[str]] = {}
        for name in station_names:
            station = self.station_details[name]
            groups.setdefault((station["eap_identity"], station["eap_password"]), []).append(name)
        for (identity, password), group_names in groups.items():
            station_profile = self.new_station_profile()
            station_profile.mode = 0
            self._configure_station_profile(station_profile, target_ssid, target_password,
                                            eap_identity=identity, eap_password=password)
            station_profile.ssid = target_ssid
            station_profile.ssid_pass = target_password if target_password else "NA"
            for name in group_names:
                station_profile.station_names = [self.station_eid(name)]
                station_profile.mac = MAC_RANDOM_PATTERN if self.randomize_mac else None
                station_profile.modify(radio=self.station_details[name]["radio"])
                new_mac_by_station[name] = old_mac_by_station[name]   # real MAC re-read after DHCP
                self.station_details[name]["ssid"] = target_ssid
                self.station_details[name]["ssid_pw"] = target_password
        if self.is_eap:
            self._enable_8021x_radius(station_names)
        time.sleep(2)

        for name in station_names:
            self.admin_up(self.station_eid(name))
        station_ips = self._wait_for_station_ips(station_names, self.wait_for_ip_sec)
        for name in station_names:                     # refresh to the AP-visible MAC when available
            new_mac_by_station[name] = self.station_details[name]["mac"] or new_mac_by_station[name]
        logger.info("%s | Reconnected %d / %d , Reset completed in %ds", tag, len(station_ips), len(station_names), int(time.time() - reset_start))

        return {
            "batch_index": batch_index,
            "cycle_number": cycle_number,
            "stations": station_names,
            "ssid": target_ssid,
            "ips": set(station_ips),
            "old_mac_by_station": old_mac_by_station,
            "new_mac_by_station": new_mac_by_station,
        }

    def reset_verify_batch(self, batch_index: int, cycle_number: int,
                           target_ssid: str, target_password: str) -> tuple[dict, dict]:
        """Run one full batch cycle: reset, resume traffic, verify, record.

        Only stations that actually reconnected (got an IPv4) have traffic started and are
        rate-limit checked; stations that failed to reconnect get a recorded FAIL/N-A verdict
        and 0 bps instead of being silently skipped or given a false PASS from 0 measured bps.

        Args:
            batch_index (int): 0-based index into self.batches.
            cycle_number (int): 1-based cycle counter, used only for log labels.
            target_ssid (str): SSID to reconnect the batch onto.
            target_password (str): Passphrase for target_ssid.

        Returns:
            tuple[dict, dict]: (info, summary) - the reset_batch() info dict and the measure_rate_limit() summary dict.
        """
        tag = "cycle %d | batch %d" % (cycle_number, batch_index + 1)
        info = self.reset_batch(batch_index, cycle_number, target_ssid, target_password)

        reconnected = [name for name in info["stations"] if name in info["ips"]]
        not_reconnected = [name for name in info["stations"] if name not in info["ips"]]
        if not_reconnected:
            logger.warning("%s | %d/%d station(s) failed to reconnect - skipping traffic/rate-limit check for them: %s",
                           tag, len(not_reconnected), len(info["stations"]),
                           ", ".join(not_reconnected[:10]) + (" ..." if len(not_reconnected) > 10 else ""))

        time.sleep(self.settle_time)
        if reconnected:
            self.start_traffic(reconnected, context=tag)
        time.sleep(self.settle_time)

        per_station, result = self.measure_rate_limit(reconnected, tag)
        for name in not_reconnected:
            per_station[name] = {"dl_bps": 0.0, "ul_bps": 0.0,
                                 "dl_verdict": "FAIL" if self.dl_enabled else "N/A",
                                 "ul_verdict": "FAIL" if self.ul_enabled else "N/A"}
        if self._details_csv_path:
            for name, m in per_station.items():
                station = self.station_details[name]
                dl_limit_bps = station["rate_limit_dl_bps"]
                ul_limit_bps = station["rate_limit_ul_bps"]
                row = {
                    "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                    "cycle": cycle_number,
                    "batch": batch_index + 1,
                    "station": name,
                    "old_mac": info["old_mac_by_station"].get(name) or "",
                    "new_mac": info["new_mac_by_station"].get(name) or "",
                    "ssid": info["ssid"],
                    "associated": name in info["ips"],
                    "dl_mbps": round(m["dl_bps"] / 1e6, 3),
                    "ul_mbps": round(m["ul_bps"] / 1e6, 3),
                    "dl_expected_mbps": round(dl_limit_bps / 1e6, 3) if dl_limit_bps else "",
                    "ul_expected_mbps": round(ul_limit_bps / 1e6, 3) if ul_limit_bps else "",
                    "dl_verdict": m["dl_verdict"],
                    "ul_verdict": m["ul_verdict"],
                }
                self.rate_limit_rows.append(row)
                self._stream_row(self._details_csv_path, row)

            self.cycle_rows.append({
                "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                "elapsed_seconds": int(time.time() - self.test_start_time),
                "cycle": cycle_number,
                "batch": batch_index + 1,
                "reconnect_ssid": info["ssid"],
                "stations": len(info["stations"]),
                "reconnected": len(info["ips"]),
                "avg_dl_mbps": round(result["avg_dl_bps"] / 1e6, 3),
                "avg_ul_mbps": round(result["avg_ul_bps"] / 1e6, 3),
                "rate_limit_dl_pass": result["dl_pass"],
                "rate_limit_ul_pass": result["ul_pass"],
                "rate_limit_dl_checked": result["dl_checked"],
                "rate_limit_ul_checked": result["ul_checked"],
            })
        return info, result

    # --- rate-limit verification ---
    def _rate_limit_verdict(self, measured: float, expected: float | None) -> str:
        """Verify one measured per-station throughput against an expected limit.

        PASS when the measurement does not exceed the limit plus self.rate_limit_tolerance_percent
        (headroom for jitter), i.e. the rate limit is still being enforced; FAIL otherwise.

        Args:
            measured (float): Measured throughput in bits/sec.
            expected (float | None): Expected limit in bits/sec, or None.

        Returns:
            str: 'PASS', 'FAIL', or 'N/A' when expected is None.
        """
        if expected is None:
            return "N/A"
        threshold = expected * (1 + self.rate_limit_tolerance_percent / 100)
        return "PASS" if measured <= threshold else "FAIL"

    def measure_rate_limit(self, station_names: list[str], tag: str) -> tuple[dict[str, dict], dict]:
        """Sample, average and grade per-station DL/UL throughput.

        Each station is graded against its own recorded rate_limit_dl_bps/rate_limit_ul_bps (from --radio's
        rate_limit_dl==/rate_limit_ul==, or the global --rate_limit_dl/--rate_limit_ul when a radio has no override), so
        stations behind different RADIUS-assigned caps are graded correctly in the same call.

        Args:
            station_names (list[str]): Stations to measure.
            tag (str): Label for the log lines (e.g. 'cycle 3 | batch 2').

        Returns:
            tuple[dict, dict]: (per_station, summary).
            per_station[name] = {'dl_bps', 'ul_bps', 'dl_verdict', 'ul_verdict'}.
            summary = {'avg_dl_bps', 'avg_ul_bps', 'dl_pass', 'ul_pass',
            'dl_checked', 'ul_checked'}.
        """
        if not station_names:
            return {}, {
                "avg_dl_bps": 0, "avg_ul_bps": 0, "dl_pass": 0, "ul_pass": 0,
                "dl_checked": self.dl_enabled and self.rate_limit_dl_bps is not None,
                "ul_checked": self.ul_enabled and self.rate_limit_ul_bps is not None,
            }

        dl_limits = [self.station_details[name]["rate_limit_dl_bps"] for name in station_names]
        ul_limits = [self.station_details[name]["rate_limit_ul_bps"] for name in station_names]

        sample_count = max(1, self.rate_limit_window // max(1, self.polling_interval))
        logger.info("%s | Rate-limit check on %d station(s) (avg over %ds)",
                    tag, len(station_names), sample_count * self.polling_interval)
        dl_bps_by_station = {name: 0.0 for name in station_names}
        ul_bps_by_station = {name: 0.0 for name in station_names}
        for _ in range(sample_count):
            rx_rates = self._endpoint_rx_rates()
            for name in station_names:
                for endp_type in self.endp_types:
                    _cx, endp_a, endp_b = self._cx_names(name, endp_type)
                    dl_bps_by_station[name] += rx_rates.get(endp_a, 0)   # station rx == downlink
                    ul_bps_by_station[name] += rx_rates.get(endp_b, 0)   # upstream rx == uplink
            time.sleep(self.polling_interval)

        check_dl = self.dl_enabled and any(v is not None for v in dl_limits)
        check_ul = self.ul_enabled and any(v is not None for v in ul_limits)
        per_station = {}
        dl_pass_count = ul_pass_count = 0
        total_dl_bps = total_ul_bps = 0.0
        for name in station_names:
            station = self.station_details[name]
            dl_bps = dl_bps_by_station[name] / sample_count
            ul_bps = ul_bps_by_station[name] / sample_count
            total_dl_bps += dl_bps
            total_ul_bps += ul_bps
            dl_verdict = self._rate_limit_verdict(dl_bps, station["rate_limit_dl_bps"]) if self.dl_enabled else "N/A"
            ul_verdict = self._rate_limit_verdict(ul_bps, station["rate_limit_ul_bps"]) if self.ul_enabled else "N/A"
            if check_dl and dl_verdict == "PASS":
                dl_pass_count += 1
            if check_ul and ul_verdict == "PASS":
                ul_pass_count += 1
            per_station[name] = {"dl_bps": dl_bps, "ul_bps": ul_bps, "dl_verdict": dl_verdict, "ul_verdict": ul_verdict}

        if check_dl or check_ul:
            logger.info("%s | Rate-limit result: DL pass %s, UL pass %s",
                        tag,
                        ("%d/%d" % (dl_pass_count, len(station_names))) if check_dl else "N/A",
                        ("%d/%d" % (ul_pass_count, len(station_names))) if check_ul else "N/A")
        return per_station, {
            "avg_dl_bps": total_dl_bps / len(station_names) if station_names else 0,
            "avg_ul_bps": total_ul_bps / len(station_names) if station_names else 0,
            "dl_pass": dl_pass_count,
            "ul_pass": ul_pass_count,
            "dl_checked": check_dl,
            "ul_checked": check_ul,
        }

    # --- background overall-throughput recorder ---
    def _throughput_loop(self) -> None:
        """Sample aggregate throughput on a fixed interval for the whole test, including during batch resets, so the series has no gaps.

        Each sample is appended to self.overall_throughput_rows and streamed to the throughput CSV.
        """
        while not self._throughput_stop.is_set():
            try:
                rx_rates = self._endpoint_rx_rates()
                total_dl_bps = total_ul_bps = 0.0
                active_stations = 0
                for name in self.all_stations:
                    station_dl_bps = station_ul_bps = 0.0
                    for endp_type in self.endp_types:
                        _cx, endp_a, endp_b = self._cx_names(name, endp_type)
                        station_dl_bps += rx_rates.get(endp_a, 0)
                        station_ul_bps += rx_rates.get(endp_b, 0)
                    total_dl_bps += station_dl_bps
                    total_ul_bps += station_ul_bps
                    if station_dl_bps + station_ul_bps > 0:
                        active_stations += 1
                sample = {
                    "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
                    "elapsed_seconds": int(time.time() - self.test_start_time),
                    "dl_mbps": round(total_dl_bps / 1e6, 3),
                    "ul_mbps": round(total_ul_bps / 1e6, 3),
                    "stations_passing_traffic": active_stations,
                }
                self.overall_throughput_rows.append(sample)
                self._stream_row(self._throughput_csv_path, sample)
            except Exception as exc:              # keep the trace alive across transient API errors
                logger.debug("Overall-throughput reading failed: %s", exc)
            self._throughput_stop.wait(self.polling_interval)

    def _start_throughput(self) -> None:
        """Start the background daemon thread that records aggregate throughput."""
        self._throughput_stop.clear()
        self._throughput_thread = threading.Thread(target=self._throughput_loop, name="overall-throughput", daemon=True)
        self._throughput_thread.start()
        logger.info("Collecting overall throughput every %ds in the background", self.polling_interval)

    def _stop_throughput(self) -> None:
        """Signal the throughput recorder thread to stop and join it (no-op if it was never started)."""
        if self._throughput_thread is None:
            return
        self._throughput_stop.set()
        self._throughput_thread.join(timeout=self.polling_interval + 5)
        self._throughput_thread = None
        logger.info("Stopped collecting overall throughput (%d samples)", len(self.overall_throughput_rows))

    @staticmethod
    def _stream_row(path: str, row: dict) -> None:
        """Append one dict row to a CSV (writing the header if the file is new), then close the file so the data is flushed."""
        if not path:
            return
        try:
            new_file = not os.path.exists(path) or os.path.getsize(path) == 0
            with open(path, "a", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=list(row.keys()))
                if new_file:
                    writer.writeheader()
                writer.writerow(row)
        except OSError as exc:
            logger.debug("Could not stream row to %s: %s", path, exc)

    def _sleep_until(self, deadline: float, next_batch: int | None = None) -> None:
        """Sleep until an absolute time, in short chunks so Ctrl-C is honoured.

        Does no monitoring itself - the background thread keeps recording overall throughput throughout.

        Args:
            deadline (float): Target wall-clock time in epoch seconds. A deadline already in the past returns immediately.
            next_batch (int | None): 1-based index of the batch that will be reset when this wait ends, for the log line.
        """
        remaining = max(0, round(deadline - time.time()))
        if remaining == 0:
            return
        if self.batch_reset_interval <= 0:
            logger.info("Traffic running for %ds", remaining)
        elif next_batch is not None:
            logger.info("Next batch %d/%d reset in %ds", next_batch, self.num_batches, remaining)
        else:
            logger.info("Next batch reset in %ds", remaining)
        while time.time() < deadline:
            time.sleep(min(5, max(1, int(deadline - time.time()) + 1)))

    # --- orchestration ---
    def run(self) -> None:
        """Run the full timed test end to end.

        Pre-cleans (unless disabled), creates stations and cross-connects, starts traffic and lets it settle,
        then either sleeps for the whole test_duration (resets disabled) or loops - batch_reset_interval of steady
        traffic followed by one reset_verify_batch(), advancing batch by batch - until test_duration elapses.
        A background thread records aggregate throughput throughout.
        """
        setup_start = time.time()
        self.test_start_time = setup_start
        if not self.no_pre_cleanup and not self.use_existing_eid:
            self.pre_cleanup()
        try:
            self.create_stations()
        except RuntimeError as err:
            logger.error("%s", err)
            if not self.no_cleanup:
                self.cleanup()
            return
        self.build_cross_connects()
        self.start_traffic()
        logger.info("Waiting %ds for the traffic to settle", self.settle_time)
        time.sleep(self.settle_time)

        # clock starts here (traffic running) so setup time is not counted
        self.test_start_time = time.time()
        hard_stop_time = self.test_start_time + self.test_duration
        resets_enabled = self.batch_reset_interval > 0
        if resets_enabled:
            logger.info("Setup took %ds; cycling for %ds, resetting a batch every %ds",
                        int(self.test_start_time - setup_start), self.test_duration, self.batch_reset_interval)
        else:
            logger.info("Setup took %ds; --batch_reset_interval 0: plain throughput run for %ds, no batch resets",
                        int(self.test_start_time - setup_start), self.test_duration)

        report_kwargs = dict(_results_dir_name=self.results_dir_name,
                             _output_html="%s.html" % self.results_dir_name,
                             _output_pdf="%s.pdf" % self.results_dir_name)
        if self.local_lf_report_dir:
            report_kwargs["_path"] = self.local_lf_report_dir
        self.report = lf_report.lf_report(**report_kwargs)
        stream_dir = self.report.get_path_date_time()
        self._details_csv_path = os.path.join(stream_dir, "batch_reset_details.csv")
        self._throughput_csv_path = os.path.join(stream_dir, "overall_throughput.csv")

        self._start_throughput()
        try:
            if not resets_enabled:
                self._sleep_until(hard_stop_time)
                logger.info("Test duration reached (no resets)")
            else:
                cycle_number = 0
                while time.time() < hard_stop_time:
                    batch_index = cycle_number % self.num_batches
                    self._sleep_until(min(time.time() + self.batch_reset_interval, hard_stop_time), next_batch=batch_index + 1)
                    if time.time() >= hard_stop_time:
                        break
                    ssid, password = self.next_reconnect_ssid(cycle_number + 1)
                    self.reset_verify_batch(batch_index, cycle_number + 1, ssid, password)
                    cycle_number += 1
                logger.info("Test duration reached after %d reset cycle(s)", cycle_number)
        finally:
            self._stop_throughput()

        self.stop_traffic()
        self.write_reports()
        if not self.no_cleanup:
            self.cleanup()

    def cleanup(self) -> None:
        """Stop and remove every cross-connect and L3 endpoint on the manager, and its stations too unless --use_existing_eid kept them.

        Cross-connects are removed by live discovery (delete_cross_connects), same reasoning as
        pre_cleanup() - relying on cx_profile's own in-memory tracking misses everything when
        --cleanup is run as its own toolbox invocation (a fresh process created nothing itself).
        """
        self.delete_cross_connects("all")
        if self.use_existing_eid:
            logger.info("Cleanup: Removed cross-connects and L3 endpoints (kept --use_existing_eid stations)")
            return
        logger.info("Cleanup: Stopping and removing every cross-connect, L3 endpoint, and station on the manager")
        stations = self._prefix_station_ports()
        if stations:
            logger.info("Deleting stations: %s", self._shorten_list([name for _resource, name in stations]))
            for resource, name in stations:
                self.json_post("/cli-json/rm_vlan", {"shelf": 1, "resource": resource, "port": name})

    # --- reporting ---
    @staticmethod
    def _write_csv(path: str, rows: list[dict]) -> None:
        """Write a list of uniform dict rows to a CSV, header first.

        Args:
            path (str): Destination file path.
            rows (list[dict]): Rows to write; keys of the first row become the header. Does nothing when rows is empty.
        """
        if not rows:
            return
        with open(path, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    def _config_table(self) -> dict[str, object]:
        """Build the "Test Configuration" table for the HTML report.

        Returns:
            dict[str, Any]: Ordered parameter-name -> value pairs.
        """
        ciphers = " / ".join(c for c in (self.pairwise_cipher, self.groupwise_cipher) if c and str(c).upper() != "[BLANK]")
        table = {
            "Manager": self.mgr,
            "Upstream port": self.upstream_port,
            "Radios": ", ".join(r for r in self.radios if r) or "(existing EIDs)",
            "Stations / Batches": "%d / %d (%s per batch)" % (self.num_stations, self.num_batches, self.batch_size_label),
            "Security / key_mgmt / EAP": "%s / %s / %s" % (self.security, self.key_mgmt, self.eap),
            "EAP phase1 / phase2": "%s / %s" % (self.eap_phase1 or "-", self.eap_phase2 or "-"),
            "Pairwise / groupwise cipher": ciphers or None,
            "PMF (ieee80211w)": self.ieee80211w,
            "Initial SSID": self.ssid or "-",
            "Reconnect SSIDs": ", ".join(s for s, _ in self.reconnect_ssids),
            "Randomize MAC on reset": "%s (%s)" % (self.randomize_mac, MAC_RANDOM_PATTERN if self.randomize_mac else "-"),
            "Traffic type / direction": "%s / %s" % (self.traffic_type, self.direction),
            "Rate mode": self.rate_mode,
            "Per-station DL / UL": "%d / %d bps" % (self.dl_bps, self.ul_bps),
            "Payload size": self.payload_size or "auto",
            "Test duration": "%ds" % self.test_duration,
            "Batch reset interval": "%ds" % self.batch_reset_interval,
            "Rate-limit expected DL / UL": "%s / %s bps" % (
                self.rate_limit_dl_bps if self.rate_limit_dl_bps else "-",
                self.rate_limit_ul_bps if self.rate_limit_ul_bps else "-"),
            "Rate-limit tolerance": "%d%%" % round(self.rate_limit_tolerance_percent),
            "Reset cycles completed": len(self.cycle_rows),
        }
        return {key: value for key, value in table.items() if value is not None}

    def _per_cycle_display_rows(self) -> list[dict]:
        """Build the "Per-Cycle Results" rows for the HTML report.

        Each row carries the pass count as 'N/M' plus a PASS/FAIL verdict per direction (PASS only when every station honoured the limit).

        Returns:
            list[dict]: One display row per entry in self.cycle_rows.
        """
        rows = []
        for r in self.cycle_rows:
            def fmt(checked: bool, passed: int, total: int = r["stations"]) -> tuple[str, str]:
                """Format one direction as (count_str, verdict_str)."""
                if not checked:
                    return "N/A", "N/A"
                return "%d/%d" % (passed, total), ("PASS" if passed >= total else "FAIL")
            dl_count, dl_result = fmt(r["rate_limit_dl_checked"], r["rate_limit_dl_pass"])
            ul_count, ul_result = fmt(r["rate_limit_ul_checked"], r["rate_limit_ul_pass"])
            rows.append({
                "cycle": r["cycle"],
                "batch": r["batch"],
                "elapsed_s": r["elapsed_seconds"],
                "reconnect_ssid": r["reconnect_ssid"],
                "stations": r["stations"],
                "reconnected": r["reconnected"],
                "avg_dl_mbps": r["avg_dl_mbps"],
                "avg_ul_mbps": r["avg_ul_mbps"],
                "dl_rate_limit_pass": dl_count,
                "dl_result": dl_result,
                "ul_rate_limit_pass": ul_count,
                "ul_result": ul_result,
            })
        return rows

    def _build_throughput_graphs(self, report) -> None:
        """Add the aggregate-throughput line chart (DL and UL over time) to the report.

        Args:
            report (lf_report.lf_report): The report being built.
        """
        elapsed = [row["elapsed_seconds"] for row in self.overall_throughput_rows]
        step = max(1, len(elapsed) // 20)

        report.set_obj_html("Aggregate Throughput",
                            "Whole-test DL/UL throughput (all %d stations). Dips align with "
                            "batch resets; the other batches keep running throughout." % self.num_stations)
        report.build_objective()
        tput_graph = lf_graph.lf_line_graph(
            _data_set=[[row["dl_mbps"] for row in self.overall_throughput_rows],
                       [row["ul_mbps"] for row in self.overall_throughput_rows]],
            _xaxis_name="Test elapsed (s)",
            _yaxis_name="Throughput (Mbps)",
            _xaxis_categories=elapsed,
            _graph_title="Aggregate throughput over time",
            _graph_image_name="overall_throughput",
            _label=["DL Mbps", "UL Mbps"],
            _color=["blue", "orange"],
            _marker=["o", "o"],
            _xaxis_step=step,
            _figsize=(16, 6))
        report.set_graph_image(tput_graph.build_line_graph())
        report.move_graph_image()
        report.build_graph()

    def write_reports(self) -> None:
        """Write the two CSVs and the HTML/PDF report for the finished run."""
        report = self.report                      # built in run()
        report_path = report.get_path_date_time()

        # Two CSVs: per-station reset / rate-limit detail, and the aggregate throughput series.
        self._write_csv(os.path.join(report_path, "batch_reset_details.csv"), self.rate_limit_rows)
        self._write_csv(os.path.join(report_path, "overall_throughput.csv"), self.overall_throughput_rows)

        report.set_title("Batch-Reset Client Cycling Throughput Test")
        report.set_date(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        report.build_banner()

        report.set_table_title("Test Configuration")
        report.build_table_title()
        report.set_table_dataframe(pd.DataFrame(self._config_table().items(), columns=["Parameter", "Value"]))
        report.build_table()

        if self.cycle_rows:
            report.set_table_title("Per-Cycle Results")
            report.build_table_title()
            report.set_table_dataframe(pd.DataFrame(self._per_cycle_display_rows()))
            report.build_table()

        if self.rate_limit_rows:
            report.set_table_title("Per-Station Detail (also in batch_reset_details.csv)")
            report.build_table_title()
            report.set_table_dataframe(pd.DataFrame(self.rate_limit_rows))
            report.build_table()

        if self.overall_throughput_rows:
            self._build_throughput_graphs(report)

        report.build_footer()
        report.write_html()
        try:
            report.write_pdf()
        except Exception as exc:
            logger.warning("PDF generation failed (HTML still written): %s", exc)
        logger.info("Report written to %s", os.path.join(report_path, "%s.html" % self.results_dir_name))


def parse_args() -> argparse.Namespace:
    """Build the argument parser (including the --toolbox group).

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="lf_batch_reset.py",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Cycle batches of EAP-PEAP stations through MAC randomization + SSID reconnect\n"
               "while running configurable L3 traffic, verifying rate limits after every reconnect.",
        description=__doc__)

    connection_group = parser.add_argument_group("connection")
    connection_group.add_argument("--mgr", "--lfmgr", dest="mgr", default="localhost",
                                  help="hostname for where LANforge GUI is running")
    connection_group.add_argument("--mgr_port", "--port", dest="mgr_port", type=int, default=8080,
                                  help="port LANforge GUI HTTP service is running on")
    connection_group.add_argument("--upstream_port", "-u", default="1.1.eth1",
                                  help="non-station port that generates traffic, e.g. 1.1.eth2")

    scale_group = parser.add_argument_group("stations & batches")
    scale_group.add_argument("--num_stations", type=int, default=50,
                             help="Station count for a single bare --radio that omits 'stations=='; "
                                  "ignored once any --radio pins its own count (default: 50)")
    scale_group.add_argument("--radio", "-r", action="append", nargs=1,
                             help="Radio config (repeatable): --radio 'radio==1.1.wiphy0 stations==25 ssid==..\n"
                                  "ssid_pw==.. security==.. eap_identity==.. eap_password==.. rate_limit_dl==..\n"
                                  "rate_limit_ul==.. batch==..' - fields not given fall back to the matching\n"
                                  "--eap_identity/--rate_limit_dl/etc. batch==<label> groups radios into a batch by\n"
                                  "that label (every --radio must set it, or none); see A1b/B1f/B1g. A single bare\n"
                                  "'--radio 1.1.wiphy0' uses --num_stations.")
    scale_group.add_argument("--num_batches", type=int, default=5,
                             help="Number of contiguous batches to split the stations into "
                                  "(default: 5; ignored if any --radio sets batch==). When the count does not divide evenly, the "
                                  "leftover stations go to the last batch")
    scale_group.add_argument("--use_existing_eid", "--use_existing_eids", dest="use_existing_eid",
                             default=None, metavar="EIDS",
                             help="Run against existing stations instead of creating them, e.g. 1.1.sta0000,1.1.sta0001\n"
                                  "(comma list of EIDs). No pre-cleanup, kept on cleanup. Needs --ssid; each\n"
                                  "station's radio is looked up from the manager unless one --radio pins them all.")

    security_group = parser.add_argument_group("security / EAP")
    security_group.add_argument("--ssid", help="Initial SSID all stations connect to")
    security_group.add_argument("--ssid_pw", "--passwd", "--password", dest="ssid_pw", default="[BLANK]",
                                help="WPA-PSK passphrase; keep [BLANK] for pure 802.1X or open")
    security_group.add_argument("--security", default="wpa2", help="wpa2 / wpa3 / wpa / open")
    security_group.add_argument("--key_mgmt", default="WPA-EAP", choices=KEY_MGMTS,
                                help="Key management wpa_supplicant token (default: WPA-EAP). Used for both "
                                "EAP and WPA-PSK; ignored for --security open")
    security_group.add_argument("--eap", "--eap_method", dest="eap", default="PEAP", choices=EAP_METHODS,
                                help="EAP method (default: PEAP -> 802.1X + RADIUS, needs --eap_identity / "
                                "--eap_password, or --private_key for TLS). Set --eap NONE for plain "
                                "WPA-PSK (uses --ssid_pw) or open (--security open)")
    security_group.add_argument("--eap_identity", "--radius_identity", dest="eap_identity",
                                help="Synonymous with the RADIUS username; shared by all stations")
    security_group.add_argument("--eap_password", "--radius_passwd", dest="eap_password",
                                help="Synonymous with the RADIUS user's password; shared by all stations")
    security_group.add_argument("--eap_anonymous_identity", dest="eap_anonymous_identity", default="",
                                help="EAP outer / anonymous identity for PEAP / TTLS (optional)")
    security_group.add_argument("--eap_phase1", dest="eap_phase1", default="",
                                help='EAP Phase 1 (TLS tunnel) parameters, e.g. "peapver=0" or "auth=MSCHAPV2"')
    security_group.add_argument("--eap_phase2", default="",
                                help='EAP Phase 2 (inner auth) value, sent as "auth=<value>", e.g. MSCHAPV2')
    security_group.add_argument("--pairwise_cipher", default="[BLANK]", choices=CIPHERS,
                                help="Pairwise cipher (wpa_supplicant token); [BLANK] = driver default")
    security_group.add_argument("--groupwise_cipher", default="[BLANK]", choices=CIPHERS,
                                help="Groupwise cipher (wpa_supplicant token); [BLANK] = driver default")
    security_group.add_argument("--ca_cert", default="",
                                help="Enter path for certificate e.g: /home/lanforge/ca.pem (EAP-TLS / TTLS)")
    security_group.add_argument("--client_cert", default="",
                                help="EAP-TLS client certificate path (if separate from --private_key)")
    security_group.add_argument("--private_key", default="",
                                help="Enter private key path e.g: /home/lanforge/client.p12 (EAP-TLS)")
    security_group.add_argument("--pk_passwd", "--pk_password", dest="pk_passwd", default="",
                                help="Enter the private key password")
    security_group.add_argument("--pac_file", default="",
                                help="Enter the PAC file path e.g: /home/lanforge/tmp/abc.pac (EAP-FAST)")
    security_group.add_argument("--ssid_list", default="",
                                help="Comma list of ssid[:pw] used on resets; advances one entry per cycle")

    traffic_group = parser.add_argument_group("traffic")
    traffic_group.add_argument("--traffic_type", "--endp_type", dest="traffic_type",
                               default="tcp+udp", choices=list(TRAFFIC_TYPE_TO_ENDP_TYPES.keys()))
    traffic_group.add_argument("--direction", default="bidi", choices=["dl", "ul", "bidi"])
    traffic_group.add_argument("--rate_mode", default="per_station", choices=["intended_load", "per_station"])
    traffic_group.add_argument("--traffic_rate", default="5Mbps",
                               help="Rate per station (or aggregate if --rate_mode intended_load), applied to "
                               "each direction that carries traffic")
    traffic_group.add_argument("--payload_size", "--packet_size", "--pdu_size", dest="payload_size", default="",
                               help="Payload size for the test: a fixed value (bytes, or MTU / AUTO) or a\n"
                               "'lo-hi' range for random per-packet sizes (e.g. 64-1472). Default: LANforge auto")

    duration_group = parser.add_argument_group("durations")
    duration_group.add_argument("--test_duration", default="30m",
                                help="Total cycling time, measured from when traffic starts (setup not counted)")
    duration_group.add_argument("--batch_reset_interval", default="0",
                                help="Steady-traffic time between batch resets (the requirement's 'X'): after a "
                                "reset completes, run/monitor for this long, then reset the next batch. "
                                "Default 0 = skip all resets and run as a plain throughput test for --test_duration; "
                                "set e.g. 5m to enable batch-reset cycling")
    duration_group.add_argument("--polling_interval", default="5s")
    duration_group.add_argument("--settle_time", default="10s",
                                help="Wait after reconnect (and after resuming traffic) before measuring")
    duration_group.add_argument("--connect_timeout", default="120s", help="Timeout passed to station create()")
    duration_group.add_argument("--wait_for_ip_sec", default="500s",
                                help="How long to wait for stations to get an IPv4 after admin-up")
    duration_group.add_argument("--rate_limit_window", default="10s",
                                help="Averaging window for the rate-limit check (default 10s). One sample every\n"
                                "--polling_interval, so 10s / 5s = 2 samples averaged before the PASS/FAIL")

    rate_limit_group = parser.add_argument_group("rate-limit verification")
    rate_limit_group.add_argument("--rate_limit_dl", default="",
                                  help="Expected RADIUS-assigned downlink rate cap, e.g. 20M / 20Mbps / 20000000 "
                                  "(same format as --traffic_rate; empty = skip DL grading)")
    rate_limit_group.add_argument("--rate_limit_ul", default="",
                                  help="Expected RADIUS-assigned uplink rate cap, e.g. 10M / 10Mbps / 10000000 "
                                  "(same format as --traffic_rate; empty = skip UL grading)")
    rate_limit_group.add_argument("--rate_limit_tolerance_percent", "--rate_limit_tolerance",
                                  dest="rate_limit_tolerance_percent", type=float, default=5.0,
                                  help="Headroom above the cap, in percent, before a station is FAILed "
                                  "(default 5). PASS = measured <= cap * (1 + percent/100)")

    mac_group = parser.add_argument_group("MAC randomization")
    mac_group.add_argument("--no_randomize_mac", action="store_true",
                           help="Keep the existing MAC across resets (default: randomize with "
                                "the fixed pattern xx:xx:xx:*:*:xx)")

    report_group = parser.add_argument_group("report")
    report_group.add_argument("--local_lf_report_dir", default="",
                              help="override the report path (lanforge/html-reports)")
    report_group.add_argument("--results_dir_name", default="lf_batch_reset",
                              help="name of the results directory under the report path")

    add_toolbox_args(parser)   # see the TOOLBOX section

    lifecycle_group = parser.add_argument_group("lifecycle")
    lifecycle_group.add_argument("--no_pre_cleanup", action="store_true",
                                 help="Do not pre-cleanup stations / cross-connects on start")
    lifecycle_group.add_argument("--no_cleanup", action="store_true",
                                 help="Do not cleanup stations / cross-connects before exit")
    lifecycle_group.add_argument("--debug", action="store_true", help="Enable debugging in py-json methods")
    lifecycle_group.add_argument("--log_level", default=None,
                                 help="Set logging level: debug | info | warning | error | critical")
    lifecycle_group.add_argument("--lf_logger_config_json",
                                 help="--lf_logger_config_json <json file>, json configuration of logger")
    lifecycle_group.add_argument("--help_summary", action="store_true", help="show a short summary and exit")

    return parser.parse_args()


TOOLBOX_ACTION_ARGS = ("create_stations", "build_cross_connects", "start_traffic", "stop_traffic",
                       "reset_batch", "verify_rate_limit", "admin_up", "admin_down",
                       "del_cxs", "del_stations", "cleanup")
# toolbox actions that take a SEL ('all' / 'batchN' / comma list of stations)
SELECTOR_ACTIONS = ("start_traffic", "stop_traffic", "verify_rate_limit",
                    "admin_up", "admin_down", "del_cxs", "del_stations")


def add_toolbox_args(parser: argparse.ArgumentParser) -> None:
    """Register the --toolbox flag group on an argument parser.

    Called from parse_args(). Adds --toolbox plus one flag per building block
    (--create_stations, --build_cross_connects, --start_traffic, ...).

    Args:
        parser (argparse.ArgumentParser): The parser to extend in place.
    """
    toolbox_group = parser.add_argument_group("toolbox (run one or more building blocks in lifecycle order and exit)")
    toolbox_group.add_argument("--toolbox", "--tool_box", dest="toolbox", action="store_true",
                               help="Enable toolbox mode: run the requested building-block action(s) and exit.\n"
                               "Only --create_stations needs --radio; every other action (incl. --reset_batch\n"
                               "and batchN) runs against every station already on LANforge (--mgr), split\n"
                               "into --num_batches. --use_existing_eid also works.")
    toolbox_group.add_argument("--create_stations", "--create_station", dest="create_stations",
                               action="store_true",
                               help="Create the EAP-PEAP / RADIUS stations on --radio (pre-cleans first unless\n"
                               "--no_pre_cleanup). Rejects --use_existing_eid.")
    toolbox_group.add_argument("--build_cross_connects", "--build_cx", dest="build_cross_connects", action="store_true",
                               help="Create the Layer-3 cross-connects between the stations and --upstream_port.")
    toolbox_group.add_argument("--start_traffic", nargs="?", const="all", default=None, metavar="SEL",
                               help="Start traffic on 'all' [default], 'batchN', or a comma list of stations.")
    toolbox_group.add_argument("--stop_traffic", nargs="?", const="all", default=None, metavar="SEL",
                               help="Stop traffic on 'all' [default], 'batchN', or a comma list of stations.")
    toolbox_group.add_argument("--reset_batch", default=None, metavar="N",
                               help="One reset of 1-based batch N: randomize MAC + reconnect to --ssid (or the first\n"
                               "--ssid_list entry) + re-auth. Does not loop/rotate. Leaves the batch's traffic\n"
                               "stopped - add --start_traffic batchN to resume, --verify_rate_limit batchN to check.")
    toolbox_group.add_argument("--verify_rate_limit", nargs="?", const="all", default=None, metavar="SEL",
                               help="Measure per-station throughput vs the rate limits for 'all' [default], 'batchN', "
                               "or a comma list.")
    toolbox_group.add_argument("--admin_up", nargs="?", const="all", default=None, metavar="SEL",
                               help="Set 'all' [default] / 'batchN' / comma-listed stations admin UP.")
    toolbox_group.add_argument("--admin_down", nargs="?", const="all", default=None, metavar="SEL",
                               help="Set 'all' [default] / 'batchN' / comma-listed stations admin DOWN.")
    toolbox_group.add_argument("--del_cxs", "--del_cx", "--delete_cross_connections", dest="del_cxs",
                               nargs="?", const="all", default=None, metavar="SEL",
                               help="Stop and remove cross-connects for 'batchN' / a comma list, or 'all' [default] -\n"
                               "unlike the other SEL actions, 'all' here reaches every cross-connect on --mgr, not\n"
                               "just this test's own. The comma list accepts full cx names (e.g. B1_sta0000-tcp) as\n"
                               "well as station names/fragments.")
    toolbox_group.add_argument("--del_stations", "--del_station", "--delete_stations", dest="del_stations",
                               nargs="?", const="all", default=None, metavar="SEL",
                               help="Admin-down and remove 'batchN' / comma-listed station ports, or 'all' [default]\n"
                               "- unlike the other SEL actions, 'all' here reaches every station on --mgr, not\n"
                               "just this test's own.")
    toolbox_group.add_argument("--cleanup", action="store_true",
                               help="Stop and remove every cross-connect, L3 endpoint and station on --mgr\n"
                               "(manager-wide, not just this test's own).")


def handle_toolbox(args: argparse.Namespace) -> bool:
    """Run the requested --toolbox building-block action(s).

    Each flag is an independent building block. They always run in lifecycle order
    (1 create -> 2 build CXs -> 3 reset -> 4 admin-up -> 5 start traffic -> 6 verify
    -> 7 stop traffic -> 8 admin-down -> 9 del CXs -> 10 del stations -> 11 cleanup),
    regardless of the order given on the command line. Step 0 validates every
    requested action's arguments up front; after that the first hard failure halts the rest.

    Args:
        args (argparse.Namespace): Parsed CLI with --toolbox and at least one action flag set.

    Returns:
        bool: True if every requested action succeeded, False otherwise.
    """
    # Check the provided toolbox action.
    requested = [name for name in TOOLBOX_ACTION_ARGS if getattr(args, name)]
    if not requested:
        logger.error("Toolbox: No action specified; use one of: %s", ", ".join("--" + a for a in TOOLBOX_ACTION_ARGS))
        return False

    logger.info("Toolbox: Mode enabled - %s", ", ".join(requested))

    plan_source = ("radio" if args.radio else "existing-eid" if args.use_existing_eid else "discovery")
    if plan_source == "discovery" and args.create_stations:
        # nothing to discover before the stations exist, and --use_existing_eid is rejected below anyway
        logger.error("Toolbox: --create_stations needs --radio")
        return False

    # Construct the test first (GenTest style - it cooks the station plan / batches
    # internally); Step 0 range checks then validate against test.batches.
    try:
        test = BatchResetTest(
            lfclient_host=args.mgr,
            lfclient_port=args.mgr_port,
            upstream_port=args.upstream_port,
            radio=args.radio,
            num_stations=args.num_stations,
            use_existing_eid=args.use_existing_eid,
            allow_discovery=True,
            num_batches=args.num_batches,
            security=args.security,
            ssid=args.ssid,
            ssid_list=args.ssid_list,
            ssid_pw=args.ssid_pw,
            key_mgmt=args.key_mgmt,
            eap=args.eap,
            eap_identity=args.eap_identity,
            eap_password=args.eap_password,
            eap_anonymous_identity=args.eap_anonymous_identity,
            eap_phase1=args.eap_phase1,
            eap_phase2=args.eap_phase2,
            pairwise_cipher=args.pairwise_cipher,
            groupwise_cipher=args.groupwise_cipher,
            ca_cert=args.ca_cert,
            client_cert=args.client_cert,
            private_key=args.private_key,
            pk_passwd=args.pk_passwd,
            pac_file=args.pac_file,
            traffic_type=args.traffic_type,
            direction=args.direction,
            rate_mode=args.rate_mode,
            traffic_rate=args.traffic_rate,
            payload_size=args.payload_size,
            test_duration=args.test_duration,
            batch_reset_interval=args.batch_reset_interval,
            polling_interval=args.polling_interval,
            settle_time=args.settle_time,
            connect_timeout=args.connect_timeout,
            wait_for_ip_sec=args.wait_for_ip_sec,
            rate_limit_window=args.rate_limit_window,
            rate_limit_dl=args.rate_limit_dl,
            rate_limit_ul=args.rate_limit_ul,
            rate_limit_tolerance_percent=args.rate_limit_tolerance_percent,
            randomize_mac=not args.no_randomize_mac,
            local_lf_report_dir=args.local_lf_report_dir,
            results_dir_name=args.results_dir_name,
            no_pre_cleanup=args.no_pre_cleanup,
            no_cleanup=args.no_cleanup,
            debug=args.debug,
            args=args)
    except ValueError as err:
        logger.error("Toolbox: %s", err)
        return False
    if plan_source == "discovery":
        logger.info("Toolbox: Found %d existing station(s) on %s", test.num_stations, args.mgr)
        if test.num_stations == 0:
            logger.warning("Toolbox: No stations found on %s - nothing to act on", args.mgr)
            return False

        # Only relevant for the plain arithmetic split - when batches come from station-name
        # labels instead, __init__ already logged that (and --num_batches is ignored either way).
        labelled = test.batches and station_batch_label(test.batches[0][0]) is not None
        batch_in_use = args.reset_batch is not None
        for act in SELECTOR_ACTIONS:
            if batch_token(getattr(args, act)) is not None:
                batch_in_use = True
                break
        if batch_in_use and not labelled:
            num_batches_given = any(arg == "--num_batches" or arg.startswith("--num_batches=") for arg in sys.argv[1:])
            logger.info("Toolbox: Batch layout structured from the %d existing station(s) - %d batch(es) of %s each%s",
                        test.num_stations, len(test.batches), test.batch_size_label,
                        "" if num_batches_given else " (pass --num_batches to match how they were created)")

    # Step 0: validate the arguments each requested action needs
    reset_batch_index = None

    # --create_stations: not with --use_existing_eid; needs --ssid
    if args.create_stations:
        if args.use_existing_eid:
            logger.error("Toolbox: --create_stations cannot be combined with --use_existing_eid")
            return False
        if not args.ssid:
            logger.error("Toolbox: --create_stations needs --ssid")
            return False

    # --build_cross_connects: needs an upstream port
    if args.build_cross_connects and not args.upstream_port:
        logger.error("Toolbox: --build_cross_connects needs --upstream_port")
        return False

    # --reset_batch N: in-range batch and a reconnect SSID
    if args.reset_batch is not None:
        try:
            batch_names = test.batch_selector(args.reset_batch)
        except ValueError as err:
            logger.error("Toolbox: --reset_batch: %s", err)
            return False
        if batch_names is None:
            logger.error("Toolbox: --reset_batch N must be 1..%d", len(test.batches))
            return False
        if not (args.ssid or args.ssid_list):
            logger.error("Toolbox: --reset_batch needs --ssid or --ssid_list (the reconnect target)")
            return False
        reset_batch_index = int(batch_token(args.reset_batch)) - 1

    # SEL actions: any batch selector must be valid (in range, and not a mistaken batch label)
    for act in SELECTOR_ACTIONS:
        try:
            test.batch_selector(getattr(args, act))
        except ValueError as err:
            logger.error("Toolbox: --%s: %s", act, err)
            return False

    test.test_start_time = time.time()

    def resolve_existing_stations(label: str, selector: str | int | None) -> list[str] | None:
        """Selector -> the stations that exist on the manager right now, or None (logged) when the
        selector itself is invalid (e.g. an out-of-range batch).

        Args:
            label (str): Action name used in log messages, e.g. '--admin_up'.
            selector: None / '' / 'all' (every station in this test's plan); an int or
                'batchN' / 'N' (this test's stations in that 1-based batch); or
                a comma list of bare names or EIDs (unknown names are dropped with a warning).

        Returns:
            list[str] | None: The requested stations that currently exist on the manager;
            [] if the selector was 'all'/empty but nothing exists yet; None (logged) if the
            selector itself was invalid, or if specific stations were requested but none exist.
        """
        if selector is None or str(selector).strip().lower() in ("", "all"):
            names = list(test.all_stations)
        else:
            try:
                batch_names = test.batch_selector(selector)
            except ValueError as err:
                logger.error("Toolbox: %s: %s", label, err)
                return None
            if batch_names is not None:
                names = batch_names
            else:
                # accept bare names ('sta0001') or EIDs ('1.1.sta0001') in a comma list
                requested = [part.strip().split(".")[-1] for part in str(selector).strip().split(",") if part.strip()]
                names = [part for part in requested if part in test.station_details]
                for unknown in set(requested) - set(names):
                    logger.warning("Toolbox: Unknown station %r, skipping", unknown)

        present = test.filter_existing(names)
        missing = [n for n in names if n not in present]
        if missing:
            logger.warning("Toolbox: %s: %d of %d station(s) not found, skipping: %s%s",
                           label, len(missing), len(names), ", ".join(missing[:10]),
                           " ..." if len(missing) > 10 else "")
        if present:
            return present
        if selector is None or str(selector).strip().lower() in ("", "all"):
            logger.warning("Toolbox: %s: No stations on LANforge, skipping", label)
            return []
        logger.error("Toolbox: %s: No matching stations - halting remaining actions", label)
        return None

    # Actions run in lifecycle order; the first hard failure halts the rest.

    # TODO: Use a common module to handle common toolbox actions
    # Step 1: create the stations (--create_stations)
    if args.create_stations:
        if not args.no_pre_cleanup:
            test.pre_cleanup()
        try:
            test.create_stations()
        except RuntimeError as err:
            logger.error("Toolbox: --create_stations failed: %s - halting remaining actions", err)
            return False

    # Step 2: build the Layer-3 cross-connects (--build_cross_connects)
    if args.build_cross_connects:
        test.build_cross_connects()

    # Step 3: reset one batch (--reset_batch N) - re-MAC + reconnect.
    if reset_batch_index is not None:
        batch = test.batches[reset_batch_index]
        present = test.filter_existing(batch)
        missing = [name for name in batch if name not in present]
        if not present:
            logger.error("Toolbox: --reset_batch: Batch %d has no existing stations - "
                         "halting remaining actions", reset_batch_index + 1)
            return False
        if missing:
            logger.warning("Toolbox: --reset_batch: %d station(s) in batch not found: %s",
                           len(missing), ", ".join(missing[:10]))
        # reconnect target: first rotation entry (--ssid_list[0], else --ssid; Step 0 ensured one)
        target_ssid, target_password = test.next_reconnect_ssid(1)
        test.reset_batch(reset_batch_index, 1, target_ssid, target_password)

    # Step 4: admin-up the selected stations (--admin_up)
    if args.admin_up is not None:
        names = resolve_existing_stations("--admin_up", args.admin_up)
        if names is None:
            return False
        if names:
            logger.info("Toolbox: Admin-up %d station(s): %s", len(names), test._shorten_list(names))
            for name in names:
                test.admin_up(test.station_eid(name))

    # Step 5: start traffic on the selected stations (--start_traffic)
    if args.start_traffic is not None:
        names = resolve_existing_stations("--start_traffic", args.start_traffic)
        if names is None:
            return False
        if names:
            test.start_traffic(names)

    # Step 6: measure per-station throughput vs the rate limits (--verify_rate_limit)
    if args.verify_rate_limit is not None:
        names = resolve_existing_stations("--verify_rate_limit", args.verify_rate_limit)
        if names is None:
            return False
        if names:
            test.measure_rate_limit(names, "toolbox")

    # Step 7: stop traffic on the selected stations (--stop_traffic)
    if args.stop_traffic is not None:
        names = resolve_existing_stations("--stop_traffic", args.stop_traffic)
        if names is None:
            return False
        if names:
            test.stop_traffic(names)

    # Step 8: admin-down the selected stations (--admin_down)
    if args.admin_down is not None:
        names = resolve_existing_stations("--admin_down", args.admin_down)
        if names is None:
            return False
        if names:
            logger.info("Toolbox: Admin-down %d station(s): %s", len(names), test._shorten_list(names))
            for name in names:
                test.admin_down(test.station_eid(name))

    # Step 9: delete the cross-connects for the selected stations (--del_cxs)
    if args.del_cxs is not None:
        try:
            if not test.delete_cross_connects(args.del_cxs):
                logger.error("Toolbox: Delete cross-connections action failed. Halting remaining actions.")
                return False
        except ValueError as err:
            logger.error("Toolbox: --del_cxs: %s", err)
            return False

    # Step 10: delete the selected station ports (--del_stations)
    if args.del_stations is not None:
        try:
            if not test.delete_stations(args.del_stations):
                logger.error("Toolbox: Delete stations action failed. Halting remaining actions.")
                return False
        except ValueError as err:
            logger.error("Toolbox: --del_stations: %s", err)
            return False

    # Step 11: remove every cross-connect and station on the manager (--cleanup)
    if args.cleanup:
        test.cleanup()

    logger.info("Toolbox: Done")
    return True

# ------------------------------ END TOOLBOX ------------------------------


def main() -> None:
    """CLI entry point.

    Parses arguments, sets up logging, and then either runs the requested --toolbox action(s) and exits,
    or builds a BatchResetTest from the CLI and runs the full test.
    """
    args = parse_args()

    if args.help_summary:
        print('''\
Creates N stations (default 50) - 802.1X EAP+RADIUS by default, or WPA-PSK / open via --key_mgmt / --security - splits
them into B batches (default 5), runs configurable Layer-3 traffic, and every "batch reset interval" resets the next
batch: stop traffic, randomize MACs, reconnect to the next SSID in a rotating list, re-authenticate, resume traffic,
then measure per-station throughput and compare it against the expected RADIUS-assigned rate limits. Cycles through all
batches until the total test duration elapses and writes per-cycle / per-station CSVs and an HTML report.
--toolbox runs one or more standalone building blocks (create_stations / build_cross_connects / reset_batch / admin_up /
start_traffic / verify_rate_limit / stop_traffic / admin_down / del_cxs / del_stations / cleanup), in that fixed order,
and exits. Most act on the stations already on LANforge; only --create_stations needs --radio. --use_existing_eid drives
an explicit port list.''')
        sys.exit(0)

    logger_config = lf_logger_config.lf_logger_config()
    log_level = getattr(logging, str(args.log_level or "info").upper(), logging.INFO)
    try:
        # force= needs Python 3.8+ to actually override lf_logger_config()'s handler above
        logging.basicConfig(level=log_level, format='%(asctime)s %(levelname)-5s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S', stream=sys.stdout, force=True)
    except TypeError:
        pass  # Python < 3.8: keep lf_logger_config()'s default (raw epoch) timestamps
    if args.lf_logger_config_json:
        logger_config.lf_logger_config_json = args.lf_logger_config_json
        logger_config.load_lf_logger_config()
    # quiet py-json's per-station modify() chatter (we log our own cycle/batch progress)
    if str(args.log_level).lower() != "debug":
        logging.getLogger("py-json.station_profile").setLevel(logging.WARNING)

    if args.toolbox:
        sys.exit(0 if handle_toolbox(args) else 1)

    required = ["ssid"] if args.use_existing_eid else ["radio", "ssid"]
    missing = [name for name in required if not getattr(args, name)]
    if missing:
        logger.error("Missing required argument(s): %s", ", ".join("--" + m for m in missing))
        sys.exit(1)
    try:
        test = BatchResetTest(
            lfclient_host=args.mgr,
            lfclient_port=args.mgr_port,
            upstream_port=args.upstream_port,
            radio=args.radio,
            num_stations=args.num_stations,
            use_existing_eid=args.use_existing_eid,
            num_batches=args.num_batches,
            security=args.security,
            ssid=args.ssid,
            ssid_list=args.ssid_list,
            ssid_pw=args.ssid_pw,
            key_mgmt=args.key_mgmt,
            eap=args.eap,
            eap_identity=args.eap_identity,
            eap_password=args.eap_password,
            eap_anonymous_identity=args.eap_anonymous_identity,
            eap_phase1=args.eap_phase1,
            eap_phase2=args.eap_phase2,
            pairwise_cipher=args.pairwise_cipher,
            groupwise_cipher=args.groupwise_cipher,
            ca_cert=args.ca_cert,
            client_cert=args.client_cert,
            private_key=args.private_key,
            pk_passwd=args.pk_passwd,
            pac_file=args.pac_file,
            traffic_type=args.traffic_type,
            direction=args.direction,
            rate_mode=args.rate_mode,
            traffic_rate=args.traffic_rate,
            payload_size=args.payload_size,
            test_duration=args.test_duration,
            batch_reset_interval=args.batch_reset_interval,
            polling_interval=args.polling_interval,
            settle_time=args.settle_time,
            connect_timeout=args.connect_timeout,
            wait_for_ip_sec=args.wait_for_ip_sec,
            rate_limit_window=args.rate_limit_window,
            rate_limit_dl=args.rate_limit_dl,
            rate_limit_ul=args.rate_limit_ul,
            rate_limit_tolerance_percent=args.rate_limit_tolerance_percent,
            randomize_mac=not args.no_randomize_mac,
            local_lf_report_dir=args.local_lf_report_dir,
            results_dir_name=args.results_dir_name,
            no_pre_cleanup=args.no_pre_cleanup,
            no_cleanup=args.no_cleanup,
            debug=args.debug,
            args=args)
    except ValueError as err:
        logger.error("%s", err)
        sys.exit(1)
    test.run()


if __name__ == "__main__":
    main()
