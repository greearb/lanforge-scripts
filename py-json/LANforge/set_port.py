set_port_current_flags = {
    "if_down":              0x1,  # Interface Down
    "fixed_10bt_hd":        0x2,  # Fixed-10bt-HD (half duplex)
    "fixed_10bt_fd":        0x4,  # Fixed-10bt-FD
    "fixed_100bt_hd":       0x8,  # Fixed-100bt-HD
    "fixed_100bt_fd":       0x10,  # Fixed-100bt-FD
    "auto_neg":             0x100,  # auto-negotiate
    "adv_10bt_hd":          0x100000,  # advert-10bt-HD
    "adv_10bt_fd":          0x200000,  # advert-10bt-FD
    "adv_100bt_hd":         0x400000,  # advert-100bt-HD
    "adv_100bt_fd":         0x800000,  # advert-100bt-FD
    "adv_flow_ctl":         0x8000000,  # advert-flow-control
    "promisc":              0x10000000,  # PROMISC
    "use_dhcp":             0x80000000,  # USE-DHCP
    "adv_10g_hd":           0x400000000,  # advert-10G-HD
    "adv_10g_fd":           0x800000000,  # advert-10G-FD
    "tso_enabled":          0x1000000000,  # TSO-Enabled
    "lro_enabled":          0x2000000000,  # LRO-Enabled
    "gro_enabled":          0x4000000000,  # GRO-Enabled
    "ufo_enabled":          0x8000000000,  # UFO-Enabled
    "gso_enabled":          0x10000000000,  # GSO-Enabled
    "use_dhcpv6":           0x20000000000,  # USE-DHCPv6
    "rxfcs":                0x40000000000,  # RXFCS
    "no_dhcp_rel":          0x80000000000,  # No-DHCP-Release
    "staged_ifup":          0x100000000000,  # Staged-IFUP
    "http_enabled":         0x200000000000,  # Enable HTTP (nginx) service for this port.
    "ftp_enabled":          0x400000000000,  # Enable FTP (vsftpd) service for this port.
    "aux_mgt":              0x800000000000,  # Enable Auxillary-Management flag for this port.
    "no_dhcp_restart":      0x1000000000000,  # Disable restart of DHCP on link connect (ie, wifi).
                                        # This should usually be enabled when testing wifi
                                        # roaming so that the wifi station can roam
                                        # without having to re-acquire a DHCP lease each
                                        # time it roams.
    "ignore_dhcp":          0x2000000000000,  # Don't set DHCP acquired IP on interface,
                                        # instead print CLI text message. May be useful
                                        # in certain wifi-bridging scenarios where external
                                        # traffic-generator cannot directly support DHCP.

    "no_ifup_post":         0x4000000000000,  # Skip ifup-post script if we can detect that we
                                        # have roamed. Roaming  is considered true if
                                        # the IPv4 address has not changed.

    "radius_enabled":       0x20000000000000,  # Enable RADIUS service (using hostapd as radius server)
    "ipsec_client":         0x40000000000000,  # Enable client IPSEC xfrm on this port.
    "ipsec_concentrator":   0x80000000000000,  # Enable concentrator (upstream) IPSEC xfrm on this port.
    "service_dns":          0x100000000000000,  # Enable DNS (dnsmasq) service on this port.
}
set_port_cmd_flags = {
    "reset_transceiver":    0x1,  # Reset transciever
    "restart_link_neg":     0x2,  # Restart link negotiation
    "force_MII_probe":      0x4,  # Force MII probe
    "no_hw_probe":          0x8,  # Don't probe hardware
    "probe_wifi":           0x10,  # Probe WIFI
    "new_gw_probe":         0x20,  # Force new GW probe
    "new_gw_probe_dev":     0x40,  # Force new GW probe for ONLY this interface
    "from_user":            0x80,  # from_user (Required to change Mgt Port config
                                    # (IP, DHCP, etc)
    "skip_port_bounce":     0x100,  # skip-port-bounce  (Don't ifdown/up
                                    # interface if possible.)
    "from_dhcp":            0x200,  # Settings come from DHCP client.
    "abort_if_scripts":     0x400,  # Forceably abort all ifup/down scripts on this Port.
    "use_pre_ifdown":       0x800,  # Call pre-ifdown script before bringing interface down.
}
