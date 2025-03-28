#!/usr/bin/env python3
import sys
import os
import importlib
import logging
import pprint

sys.path.append(os.path.join(os.path.abspath(__file__ + "../../../")))

lfcli_base = importlib.import_module("py-json.LANforge.lfcli_base")
LFCliBase = lfcli_base.LFCliBase

logger = logging.getLogger(__name__)


class MULTICASTProfile(LFCliBase):
    def __init__(self,
                 lfclient_host,
                 lfclient_port,
                 local_realm,
                 side_a_min_bps=256000,  # rx
                 side_b_min_bps=256000,  # tx
                 side_a_max_bps=0,
                 side_b_max_bps=0,
                 side_a_min_pdu=-1,
                 side_b_min_pdu=-1,
                 side_a_max_pdu=0,
                 side_b_max_pdu=0,
                 side_a_ip_port=9999,  # the default needs to be the dest port
                 side_b_ip_port=9999,
                 side_a_is_rate_bursty='NO',
                 side_b_is_rate_bursty='NO',
                 side_a_is_pkt_sz_random='NO',
                 side_b_is_pkt_sz_random='NO',
                 side_a_payload_pattern='INCREASING',
                 side_b_payload_pattern='INCREASING',
                 side_a_use_checksum='NO',
                 side_b_use_checksum='NO',
                 side_a_ttl=32,
                 side_b_ttl=32,
                 side_a_send_bad_crc_per_million=0,
                 side_b_send_bad_crc_per_million=0,
                 side_a_multi_conn=0,
                 side_b_multi_conn=0,
                 side_a_mcast_group="224.9.9.9",
                 side_b_mcast_group="224.9.9.9",
                 side_a_mcast_dest_port=9999,
                 side_b_mcast_dest_port=9999,
                 side_a_rcv_mcast='Yes',
                 side_b_rcv_mcast='NO',
                 report_timer_=3000,
                 name_prefix_="Unset",
                 number_template_="00000",
                 debug_=False):
        """

        :param lfclient_host:
        :param lfclient_port:
        :param local_realm:
        :param name_prefix_: prefix string for connection
        :param number_template_: how many zeros wide we padd, possibly a starting integer with left padding
        :param debug_:
        """
        super().__init__(lfclient_host, lfclient_port, debug_)
        self.lfclient_url = "http://%s:%s" % (lfclient_host, lfclient_port)
        self.debug = debug_
        self.local_realm = local_realm
        self.report_timer = report_timer_
        self.created_mc = {}
        self.name_prefix = name_prefix_
        self.number_template = number_template_

        self.side_a_min_pdu = side_a_min_pdu
        self.side_b_min_pdu = side_b_min_pdu
        self.side_a_max_pdu = side_a_max_pdu
        self.side_b_max_pdu = side_b_max_pdu

        self.side_a_min_bps = side_a_min_bps
        self.side_b_min_bps = side_b_min_bps
        self.side_a_max_bps = side_a_max_bps
        self.side_b_max_bps = side_b_max_bps

        self.side_a_ip_port = side_a_ip_port
        self.side_b_ip_port = side_b_ip_port

        self.side_a_is_rate_bursty = side_a_is_rate_bursty
        self.side_b_is_rate_bursty = side_b_is_rate_bursty
        self.side_a_is_pkt_sz_random = side_a_is_pkt_sz_random
        self.side_b_is_pkt_sz_random = side_b_is_pkt_sz_random
        self.side_a_payload_pattern = side_a_payload_pattern
        self.side_b_payload_pattern = side_b_payload_pattern
        self.side_a_use_checksum = side_a_use_checksum
        self.side_b_use_checksum = side_b_use_checksum
        self.side_a_ttl = side_a_ttl
        self.side_b_ttl = side_b_ttl
        self.side_a_send_bad_crc_per_million = side_a_send_bad_crc_per_million
        self.side_b_send_bad_crc_per_million = side_b_send_bad_crc_per_million
        self.side_a_multi_conn = side_a_multi_conn
        self.side_b_multi_conn = side_b_multi_conn
        self.side_a_mcast_group = side_a_mcast_group
        self.side_b_mcast_group = side_b_mcast_group
        self.side_a_mcast_dest_port = side_a_mcast_dest_port
        self.side_b_mcast_dest_port = side_b_mcast_dest_port
        self.side_a_rcv_mcast = side_a_rcv_mcast
        self.side_b_rcv_mcast = side_b_rcv_mcast

    def clean_mc_lists(self):
        # Clean out our local lists, this by itself does NOT remove anything from LANforge manager.
        # but, if you are trying to modify existing connections, then clearing these arrays and
        # re-calling 'create' will do the trick.
        self.created_mc = {}

    def get_mc_names(self):
        return self.created_mc.keys()

    def refresh_mc(self, debug_=False):
        for endp_name in self.get_mc_names():
            self.json_post("/cli-json/show_endpoints", {
                "endpoint": endp_name
            }, debug_=debug_)

    def start_mc(self, suppress_related_commands=None, debug_=False):
        if self.debug:
            debug_ = True

        logger.info(f"Starting multicast endpoint(s): {self.get_mc_names()}")
        for endp_name in self.get_mc_names():
            logger.debug(f"Starting multicast endpoint: {endp_name}")
            json_data = {
                "endp_name": endp_name
            }
            url = "cli-json/start_endp"
            self.local_realm.json_post(url, json_data, debug_=debug_,
                                       suppress_related_commands_=suppress_related_commands)

    def stop_mc(self, suppress_related_commands=None, debug_=False):
        if self.debug:
            debug_ = True
        for endp_name in self.get_mc_names():
            json_data = {
                "endp_name": endp_name
            }
            url = "cli-json/stop_endp"
            self.local_realm.json_post(url, json_data, debug_=debug_,
                                       suppress_related_commands_=suppress_related_commands)

        pass

    def cleanup_prefix(self):
        self.local_realm.cleanup_cxe_prefix(self.name_prefix)

    def cleanup(self, suppress_related_commands=None, debug_=False):
        if self.debug:
            debug_ = True

        for endp_name in self.get_mc_names():
            self.local_realm.rm_endp(endp_name, debug_=debug_, suppress_related_commands_=suppress_related_commands)

    def create_mc_tx(self,
                     endp_type,
                     side_tx,
                     tos=None,
                     add_tos_to_name=False,
                     suppress_related_commands=None,
                     debug_=False):
        if self.debug:
            debug_ = True

        side_tx_info = self.local_realm.name_to_eid(side_tx)
        side_tx_shelf = side_tx_info[0]
        side_tx_resource = side_tx_info[1]
        side_tx_port = side_tx_info[2]
        if tos and add_tos_to_name:
            side_tx_name = "%smtx-%s-%s-%i" % (self.name_prefix, tos, side_tx_port, len(self.created_mc))
        else:
            side_tx_name = "%smtx-%s-%i" % (self.name_prefix, side_tx_port, len(self.created_mc))

        # add_endp mcast-xmit-sta 1 1 side_tx mc_udp -1 NO 4000000 0 NO 1472 0 INCREASING NO 32 0 0
        json_data = {
            'alias': side_tx_name,
            'shelf': side_tx_shelf,
            'resource': side_tx_resource,
            'port': side_tx_port,
            'type': endp_type,
            'ip_port': self.side_b_ip_port,
            'is_rate_bursty': self.side_b_is_rate_bursty,
            'min_rate': self.side_b_min_bps,
            'max_rate': self.side_b_max_bps,
            'is_pkt_sz_random': self.side_b_is_pkt_sz_random,
            'min_pkt': self.side_b_min_pdu,
            'max_pkt': self.side_b_max_pdu,
            'payload_pattern': self.side_b_payload_pattern,
            'use_checksum': self.side_b_use_checksum,
            'ttl': self.side_b_ttl,
            'send_bad_crc_per_million': self.side_b_send_bad_crc_per_million,
            'multi_conn': self.side_b_multi_conn
        }

        url = "/cli-json/add_endp"
        self.local_realm.json_post(url, json_data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

        json_data = {
            'name': side_tx_name,
            'ttl': self.side_b_ttl,
            'mcast_group': self.side_b_mcast_group,
            'mcast_dest_port': self.side_b_mcast_dest_port,
            'rcv_mcast': self.side_b_rcv_mcast
        }

        url = "cli-json/set_mc_endp"
        self.local_realm.json_post(url, json_data, debug_=debug_, suppress_related_commands_=suppress_related_commands)

        self.created_mc[side_tx_name] = side_tx_name

        these_endp = [side_tx_name]

        if tos:
            self.local_realm.set_endp_tos(side_tx_name, tos)

        self.local_realm.wait_until_endps_appear(these_endp, debug=debug_)

    def create_mc_rx(self,
                     endp_type,
                     side_rx,
                     tos=None,
                     add_tos_to_name=False,
                     suppress_related_commands=None,
                     debug_=False):
        if self.debug:
            debug_ = True

        these_endp = []

        for port_name in side_rx:
            side_rx_info = self.local_realm.name_to_eid(port_name)
            side_rx_shelf = side_rx_info[0]
            side_rx_resource = side_rx_info[1]
            side_rx_port = side_rx_info[2]
            if tos and add_tos_to_name:
                side_rx_name = "%smrx-%s-%s-%i" % (self.name_prefix, tos, side_rx_port, len(self.created_mc))
            else:
                side_rx_name = "%smrx-%s-%i" % (self.name_prefix, side_rx_port, len(self.created_mc))
            # add_endp mcast-rcv-sta-001 1 1 sta0002 mc_udp 9999 NO 0 0 NO 1472 0 INCREASING NO 32 0 0
            json_data = {
                'alias': side_rx_name,
                'shelf': side_rx_shelf,
                'resource': side_rx_resource,
                'port': side_rx_port,
                'type': endp_type,
                'type': endp_type,
                'ip_port': self.side_a_ip_port,
                'is_rate_bursty': self.side_a_is_rate_bursty,
                'min_rate': self.side_a_min_bps,
                'max_rate': self.side_a_max_bps,
                'is_pkt_sz_random': self.side_a_is_pkt_sz_random,
                'min_pkt': self.side_a_min_pdu,
                'max_pkt': self.side_a_max_pdu,
                'payload_pattern': self.side_a_payload_pattern,
                'use_checksum': self.side_a_use_checksum,
                'ttl': self.side_a_ttl,
                'send_bad_crc_per_million': self.side_a_send_bad_crc_per_million,
                'multi_conn': self.side_a_multi_conn
            }

            url = "cli-json/add_endp"
            self.local_realm.json_post(url, json_data, debug_=debug_,
                                       suppress_related_commands_=suppress_related_commands)
            json_data = {
                'name': side_rx_name,
                'ttl': self.side_a_ttl,
                'mcast_group': self.side_a_mcast_group,
                'mcast_dest_port': self.side_a_mcast_dest_port,
                'rcv_mcast': self.side_a_rcv_mcast
            }
            url = "cli-json/set_mc_endp"
            self.local_realm.json_post(url, json_data, debug_=debug_,
                                       suppress_related_commands_=suppress_related_commands)

            self.created_mc[side_rx_name] = side_rx_name
            these_endp.append(side_rx_name)

            if tos:
                self.local_realm.set_endp_tos(side_rx_name, tos)

        self.local_realm.wait_until_endps_appear(these_endp, debug=debug_)

    def to_string(self):
        pprint.pprint(self)
