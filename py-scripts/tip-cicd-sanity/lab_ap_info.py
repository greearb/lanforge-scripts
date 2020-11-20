#!/usr/bin/python3

ap_models = ["ec420","ea8300","ecw5211","ecw5410"]

##AP Models for firmware upload
cloud_sdk_models = {
    "ec420": "EC420-G1",
    "ea8300": "EA8300-CA",
    "ecw5211": "ECW5211",
    "ecw5410": "ECW5410"
}

mimo_5g = {
    "ec420": "4x4",
    "ea8300": "2x2",
    "ecw5211": "2x2",
    "ecw5410": "4x4"
}

mimo_2dot4g = {
    "ec420": "2x2",
    "ea8300": "2x2",
    "ecw5211": "2x2",
    "ecw5410": "4x4"
}

sanity_status = {
    "ea8300": "failed",
    "ecw5211": 'passed',
    "ecw5410": 'failed',
    "ec420": 'failed'
}

##Equipment IDs for Lab APs under test
equipment_id_dict = {
    "ea8300": "13",
    "ecw5410": "12",
    "ecw5211": "6",
    "ec420": "11"
}

equipment_ip_dict = {
    "ea8300": "10.10.10.103",
    "ecw5410": "10.10.10.105",
    "ec420": "10.10.10.104",
    "ecw5211": "10.10.10.102"
}

eqiupment_credentials_dict = {
    "ea8300": "openwifi",
    "ecw5410": "openwifi",
    "ec420": "openwifi",
    "ecw5211": "admin123"
}
###Testing AP Profile Information
profile_info_dict = {
    "ecw5410": {
        "profile_id": "2",
        "fiveG_WPA2_SSID": "ECW5410_5G_WPA2",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "ECW5410_5G_WPA",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "ECW5410_5G_OPEN",
        "fiveG_WPA2-EAP_SSID": "ECW5410_5G_WPA2-EAP",
        "twoFourG_OPEN_SSID": "ECW5410_2dot4G_OPEN",
        "twoFourG_WPA2_SSID": "ECW5410_2dot4G_WPA2",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID":"ECW5410_2dot4G_WPA",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "ECW5410_2dot4G_WPA2-EAP"
        },

    "ea8300": {
        "profile_id": "153",
        "fiveG_WPA2_SSID": "EA8300_5G_WPA2",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "EA8300_5G_WPA",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "EA8300_5G_OPEN",
        "fiveG_WPA2-EAP_SSID": "EA8300_5G_WPA2-EAP",
        "twoFourG_OPEN_SSID": "EA8300_2dot4G_OPEN",
        "twoFourG_WPA2_SSID": "EA8300_2dot4G_WPA2",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID":"EA8300_2dot4G_WPA",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "EA8300_2dot4G_WPA2-EAP"
        },

    "ec420": {
        "profile_id": "20",
        "fiveG_WPA2_SSID": "EC420_5G_WPA2",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "EC420_5G_WPA",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "EC420_5G_OPEN",
        "fiveG_WPA2-EAP_SSID": "EC420_5G_WPA2-EAP",
        "twoFourG_OPEN_SSID": "EC420_2dot4G_OPEN",
        "twoFourG_WPA2_SSID": "EC420_2dot4G_WPA2",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID":"EC420_2dot4G_WPA",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "EC420_2dot4G_WPA2-EAP"
        },

    "ecw5211": {
        "profile_id": "27",
        "fiveG_WPA2_SSID": "ECW5211_5G_WPA2",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "ECW5211_5G_WPA",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "ECW5211_5G_OPEN",
        "fiveG_WPA2-EAP_SSID": "ECW5211_5G_WPA2-EAP",
        "twoFourG_OPEN_SSID": "ECW5211_2dot4G_OPEN",
        "twoFourG_WPA2_SSID": "ECW5211_2dot4G_WPA2",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID":"ECW5211_2dot4G_WPA",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "ECW5211_2dot4G_WPA2-EAP"
        },
    
    "ecw5410_nat": {
        "profile_id": "68",
        "fiveG_WPA2_SSID": "ECW5410_5G_WPA2_NAT",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "ECW5410_5G_WPA_NAT",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "ECW5410_5G_OPEN_NAT",
        "fiveG_WPA2-EAP_SSID": "ECW5410_5G_WPA2-EAP_NAT",
        "twoFourG_OPEN_SSID": "ECW5410_2dot4G_OPEN_NAT",
        "twoFourG_WPA2_SSID": "ECW5410_2dot4G_WPA2_NAT",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID":"ECW5410_2dot4G_WPA_NAT",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "ECW5410_2dot4G_WPA2-EAP_NAT"
        },

    "ea8300_nat": {
        "profile_id": "67",
        "fiveG_WPA2_SSID": "EA8300_5G_WPA2_NAT",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "EA8300_5G_WPA_NAT",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "EA8300_5G_OPEN_NAT",
        "fiveG_WPA2-EAP_SSID": "EA8300_5G_WPA2-EAP_NAT",
        "twoFourG_OPEN_SSID": "EA8300_2dot4G_OPEN_NAT",
        "twoFourG_WPA2_SSID": "EA8300_2dot4G_WPA2_NAT",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID":"EA8300_2dot4G_WPA_NAT",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "EA8300_2dot4G_WPA2-EAP_NAT"
        },

    "ec420_nat": {
        "profile_id": "70",
        "fiveG_WPA2_SSID": "EC420_5G_WPA2_NAT",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "EC420_5G_WPA_NAT",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "EC420_5G_OPEN_NAT",
        "fiveG_WPA2-EAP_SSID": "EC420_5G_WPA2-EAP_NAT",
        "twoFourG_OPEN_SSID": "EC420_2dot4G_OPEN_NAT",
        "twoFourG_WPA2_SSID": "EC420_2dot4G_WPA2_NAT",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID":"EC420_2dot4G_WPA_NAT",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "EC420_2dot4G_WPA2-EAP_NAT"
        },

    "ecw5211_nat": {
        "profile_id": "69",
        "fiveG_WPA2_SSID": "ECW5211_5G_WPA2_NAT",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "ECW5211_5G_WPA_NAT",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "ECW5211_5G_OPEN_NAT",
        "fiveG_WPA2-EAP_SSID": "ECW5211_5G_WPA2-EAP_NAT",
        "twoFourG_OPEN_SSID": "ECW5211_2dot4G_OPEN_NAT",
        "twoFourG_WPA2_SSID": "ECW5211_2dot4G_WPA2_NAT",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID":"ECW5211_2dot4G_WPA_NAT",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "ECW5211_2dot4G_WPA2-EAP_NAT"
        },

    "ecw5410_vlan": {
        "profile_id": "338",
        "fiveG_WPA2_SSID": "ECW5410_5G_WPA2_VLAN",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "ECW5410_5G_WPA_VLAN",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "ECW5410_5G_OPEN_VLAN",
        "fiveG_WPA2-EAP_SSID": "ECW5410_5G_WPA2-EAP_VLAN",
        "twoFourG_OPEN_SSID": "ECW5410_2dot4G_OPEN_VLAN",
        "twoFourG_WPA2_SSID": "ECW5410_2dot4G_WPA2_VLAN",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID":"ECW5410_2dot4G_WPA_VLAN",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "ECW5410_2dot4G_WPA2-EAP_VLAN"
        },

    "ea8300_vlan": {
        "profile_id": "319",
        "fiveG_WPA2_SSID": "EA8300_5G_WPA2_VLAN",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "EA8300_5G_WPA_VLAN",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "EA8300_5G_OPEN_VLAN",
        "fiveG_WPA2-EAP_SSID": "EA8300_5G_WPA2-EAP_VLAN",
        "twoFourG_OPEN_SSID": "EA8300_2dot4G_OPEN_VLAN",
        "twoFourG_WPA2_SSID": "EA8300_2dot4G_WPA2_VLAN",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID":"EA8300_2dot4G_WPA_VLAN",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "EA8300_2dot4G_WPA2-EAP_VLAN"
        },

    "ec420_vlan": {
        "profile_id": "357",
        "fiveG_WPA2_SSID": "EC420_5G_WPA2_VLAN",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "EC420_5G_WPA_VLAN",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "EC420_5G_OPEN_VLAN",
        "fiveG_WPA2-EAP_SSID": "EC420_5G_WPA2-EAP_VLAN",
        "twoFourG_OPEN_SSID": "EC420_2dot4G_OPEN_VLAN",
        "twoFourG_WPA2_SSID": "EC420_2dot4G_WPA2_VLAN",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID":"EC420_2dot4G_WPA_VLAN",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "EC420_2dot4G_WPA2-EAP_VLAN"
        },

    "ecw5211_vlan": {
        "profile_id": "364",
        "fiveG_WPA2_SSID": "ECW5211_5G_WPA2_VLAN",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "ECW5211_5G_WPA_VLAN",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "ECW5211_5G_OPEN_VLAN",
        "fiveG_WPA2-EAP_SSID": "ECW5211_5G_WPA2-EAP_VLAN",
        "twoFourG_OPEN_SSID": "ECW5211_2dot4G_OPEN_VLAN",
        "twoFourG_WPA2_SSID": "ECW5211_2dot4G_WPA2_VLAN",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID":"ECW5211_2dot4G_WPA_VLAN",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "ECW5211_2dot4G_WPA2-EAP_VLAN"
        }
}