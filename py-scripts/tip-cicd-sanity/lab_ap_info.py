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
    "ea8300": "19",
    "ecw5410": "20",
    "ecw5211": "21",
    "ec420": "27"
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
        "childProfileIds": [
            129,
            3,
            10,
            11,
            12,
            13,
            190,
            191
        ],
        "fiveG_WPA2_SSID": "ECW5410_5G_WPA2",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "ECW5410_5G_WPA",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "ECW5410_5G_OPEN",
        "fiveG_WPA2-EAP_SSID": "ECW5410_5G_WPA2-EAP",
        "twoFourG_OPEN_SSID": "ECW5410_2dot4G_OPEN",
        "twoFourG_WPA2_SSID": "ECW5410_2dot4G_WPA2",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID": "ECW5410_2dot4G_WPA",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "ECW5410_2dot4G_WPA2-EAP",
        "ssid_list": [
            "ECW5410_5G_WPA2",
            "ECW5410_5G_WPA",
            "ECW5410_5G_WPA2-EAP",
            "ECW5410_2dot4G_WPA2",
            "ECW5410_2dot4G_WPA",
            "ECW5410_2dot4G_WPA2-EAP"
        ]
    },

    "ea8300": {
        "profile_id": "153",
        "childProfileIds": [
            17,
            129,
            18,
            201,
            202,
            10,
            14,
            15
        ],
        "fiveG_WPA2_SSID": "EA8300_5G_WPA2",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "EA8300_5G_WPA",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "EA8300_5G_OPEN",
        "fiveG_WPA2-EAP_SSID": "EA8300_5G_WPA2-EAP",
        "twoFourG_OPEN_SSID": "EA8300_2dot4G_OPEN",
        "twoFourG_WPA2_SSID": "EA8300_2dot4G_WPA2",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID": "EA8300_2dot4G_WPA",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "EA8300_2dot4G_WPA2-EAP",
        # EA8300 has 2x 5GHz SSIDs because it is a tri-radio AP!
        "ssid_list": [
            "EA8300_5G_WPA2",
            "EA8300_5G_WPA2",
            "EA8300_5G_WPA",
            "EA8300_5G_WPA",
            "EA8300_5G_WPA2-EAP",
            "EA8300_5G_WPA2-EAP",
            "EA8300_2dot4G_WPA2",
            "EA8300_2dot4G_WPA",
            "EA8300_2dot4G_WPA2-EAP"
        ]
    },

    "ec420": {
        "profile_id": "20",
        "childProfileIds": [
            129,
            209,
            210,
            21,
            22,
            24,
            25,
            10
        ],
        "fiveG_WPA2_SSID": "EC420_5G_WPA2",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "EC420_5G_WPA",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "EC420_5G_OPEN",
        "fiveG_WPA2-EAP_SSID": "EC420_5G_WPA2-EAP",
        "twoFourG_OPEN_SSID": "EC420_2dot4G_OPEN",
        "twoFourG_WPA2_SSID": "EC420_2dot4G_WPA2",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID": "EC420_2dot4G_WPA",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "EC420_2dot4G_WPA2-EAP",
        "ssid_list": [
            "EC420_5G_WPA2",
            "EC420_5G_WPA",
            "EC420_5G_WPA2-EAP",
            "EC420_2dot4G_WPA2",
            "EC420_2dot4G_WPA",
            "EC420_2dot4G_WPA2-EAP"
        ]
    },

    "ecw5211": {
        "profile_id": "27",
        "childProfileIds": [
            32,
            129,
            10,
            28,
            29,
            205,
            206,
            31
        ],
        "fiveG_WPA2_SSID": "ECW5211_5G_WPA2",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "ECW5211_5G_WPA",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "ECW5211_5G_OPEN",
        "fiveG_WPA2-EAP_SSID": "ECW5211_5G_WPA2-EAP",
        "twoFourG_OPEN_SSID": "ECW5211_2dot4G_OPEN",
        "twoFourG_WPA2_SSID": "ECW5211_2dot4G_WPA2",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID": "ECW5211_2dot4G_WPA",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "ECW5211_2dot4G_WPA2-EAP",
        "ssid_list": [
            "ECW5211_5G_WPA2",
            "ECW5211_5G_WPA",
            "ECW5211_5G_WPA2-EAP",
            "ECW5211_2dot4G_WPA2",
            "ECW5211_2dot4G_WPA",
            "ECW5211_2dot4G_WPA2-EAP"
        ]
    },

    "ecw5410_nat": {
        "profile_id": "68",
        "childProfileIds": [
            192,
            129,
            81,
            193,
            82,
            10,
            78,
            79
        ],
        "fiveG_WPA2_SSID": "ECW5410_5G_WPA2_NAT",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "ECW5410_5G_WPA_NAT",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "ECW5410_5G_OPEN_NAT",
        "fiveG_WPA2-EAP_SSID": "ECW5410_5G_WPA2-EAP_NAT",
        "twoFourG_OPEN_SSID": "ECW5410_2dot4G_OPEN_NAT",
        "twoFourG_WPA2_SSID": "ECW5410_2dot4G_WPA2_NAT",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID": "ECW5410_2dot4G_WPA_NAT",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "ECW5410_2dot4G_WPA2-EAP_NAT",
        "ssid_list": [
            "ECW5410_5G_WPA2_NAT",
            "ECW5410_5G_WPA_NAT",
            "ECW5410_5G_WPA2-EAP_NAT",
            "ECW5410_2dot4G_WPA2_NAT",
            "ECW5410_2dot4G_WPA_NAT",
            "ECW5410_2dot4G_WPA2-EAP_NAT"
        ]
    },

    "ea8300_nat": {
        "profile_id": "67",
        "childProfileIds": [
            129,
            72,
            73,
            10,
            75,
            203,
            76,
            204
        ],
        "fiveG_WPA2_SSID": "EA8300_5G_WPA2_NAT",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "EA8300_5G_WPA_NAT",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "EA8300_5G_OPEN_NAT",
        "fiveG_WPA2-EAP_SSID": "EA8300_5G_WPA2-EAP_NAT",
        "twoFourG_OPEN_SSID": "EA8300_2dot4G_OPEN_NAT",
        "twoFourG_WPA2_SSID": "EA8300_2dot4G_WPA2_NAT",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID": "EA8300_2dot4G_WPA_NAT",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "EA8300_2dot4G_WPA2-EAP_NAT",
        # EA8300 has 2x 5GHz SSIDs because it is a tri-radio AP!
        "ssid_list": [
            "EA8300_5G_WPA2_NAT",
            "EA8300_5G_WPA2_NAT",
            "EA8300_5G_WPA_NAT",
            "EA8300_5G_WPA_NAT",
            "EA8300_5G_WPA2-EAP_NAT",
            "EA8300_5G_WPA2-EAP_NAT",
            "EA8300_2dot4G_WPA2_NAT",
            "EA8300_2dot4G_WPA_NAT",
            "EA8300_2dot4G_WPA2-EAP_NAT"
        ]
    },

    "ec420_nat": {
        "profile_id": "70",
        "childProfileIds": [
            129,
            211,
            212,
            90,
            10,
            91,
            93,
            94
        ],
        "fiveG_WPA2_SSID": "EC420_5G_WPA2_NAT",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "EC420_5G_WPA_NAT",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "EC420_5G_OPEN_NAT",
        "fiveG_WPA2-EAP_SSID": "EC420_5G_WPA2-EAP_NAT",
        "twoFourG_OPEN_SSID": "EC420_2dot4G_OPEN_NAT",
        "twoFourG_WPA2_SSID": "EC420_2dot4G_WPA2_NAT",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID": "EC420_2dot4G_WPA_NAT",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "EC420_2dot4G_WPA2-EAP_NAT",
        "ssid_list": [
            "EC420_5G_WPA2_NAT",
            "EC420_5G_WPA_NAT",
            "EC420_5G_WPA2-EAP_NAT",
            "EC420_2dot4G_WPA2_NAT",
            "EC420_2dot4G_WPA_NAT",
            "EC420_2dot4G_WPA2-EAP_NAT"
        ]
    },

    "ecw5211_nat": {
        "profile_id": "69",
        "childProfileIds": [
            208,
            129,
            84,
            85,
            87,
            88,
            10,
            207
        ],
        "fiveG_WPA2_SSID": "ECW5211_5G_WPA2_NAT",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "ECW5211_5G_WPA_NAT",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "ECW5211_5G_OPEN_NAT",
        "fiveG_WPA2-EAP_SSID": "ECW5211_5G_WPA2-EAP_NAT",
        "twoFourG_OPEN_SSID": "ECW5211_2dot4G_OPEN_NAT",
        "twoFourG_WPA2_SSID": "ECW5211_2dot4G_WPA2_NAT",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID": "ECW5211_2dot4G_WPA_NAT",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "ECW5211_2dot4G_WPA2-EAP_NAT",
        "ssid_list": [
            "ECW5211_5G_WPA2_NAT",
            "ECW5211_5G_WPA_NAT",
            "ECW5211_5G_WPA2-EAP_NAT",
            "ECW5211_2dot4G_WPA2_NAT",
            "ECW5211_2dot4G_WPA_NAT",
            "ECW5211_2dot4G_WPA2-EAP_NAT"
        ]
    },

    "ecw5410_vlan": {
        "profile_id": "338",
        "childProfileIds": [
            336,
            320,
            129,
            337,
            10,
            333,
            334,
            335
        ],
        "fiveG_WPA2_SSID": "ECW5410_5G_WPA2_VLAN",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "ECW5410_5G_WPA_VLAN",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "ECW5410_5G_OPEN_VLAN",
        "fiveG_WPA2-EAP_SSID": "ECW5410_5G_WPA2-EAP_VLAN",
        "twoFourG_OPEN_SSID": "ECW5410_2dot4G_OPEN_VLAN",
        "twoFourG_WPA2_SSID": "ECW5410_2dot4G_WPA2_VLAN",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID": "ECW5410_2dot4G_WPA_VLAN",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "ECW5410_2dot4G_WPA2-EAP_VLAN",
        "ssid_list": [
            "ECW5410_5G_WPA2_VLAN",
            "ECW5410_5G_WPA_VLAN",
            "ECW5410_5G_WPA2-EAP_VLAN",
            "ECW5410_2dot4G_WPA2_VLAN",
            "ECW5410_2dot4G_WPA_VLAN",
            "ECW5410_2dot4G_WPA2-EAP_VLAN"
        ]
    },

    "ea8300_vlan": {
        "profile_id": "319",
        "childProfileIds": [
            129,
            313,
            10,
            314,
            315,
            316,
            317,
            318
        ],
        "fiveG_WPA2_SSID": "EA8300_5G_WPA2_VLAN",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "EA8300_5G_WPA_VLAN",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "EA8300_5G_OPEN_VLAN",
        "fiveG_WPA2-EAP_SSID": "EA8300_5G_WPA2-EAP_VLAN",
        "twoFourG_OPEN_SSID": "EA8300_2dot4G_OPEN_VLAN",
        "twoFourG_WPA2_SSID": "EA8300_2dot4G_WPA2_VLAN",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID": "EA8300_2dot4G_WPA_VLAN",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "EA8300_2dot4G_WPA2-EAP_VLAN",
        # EA8300 has 2x 5GHz SSIDs because it is a tri-radio AP!
        "ssid_list": [
            "EA8300_5G_WPA2_VLAN",
            "EA8300_5G_WPA2_VLAN",
            "EA8300_5G_WPA_VLAN",
            "EA8300_5G_WPA_VLAN",
            "EA8300_5G_WPA2-EAP_VLAN",
            "EA8300_5G_WPA2-EAP_VLAN",
            "EA8300_2dot4G_WPA2_VLAN",
            "EA8300_2dot4G_WPA_VLAN",
            "EA8300_2dot4G_WPA2-EAP_VLAN"
        ]
    },

    "ec420_vlan": {
        "profile_id": "357",
        "childProfileIds": [
            352,
            129,
            353,
            354,
            355,
            356,
            10,
            351
        ],
        "fiveG_WPA2_SSID": "EC420_5G_WPA2_VLAN",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "EC420_5G_WPA_VLAN",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "EC420_5G_OPEN_VLAN",
        "fiveG_WPA2-EAP_SSID": "EC420_5G_WPA2-EAP_VLAN",
        "twoFourG_OPEN_SSID": "EC420_2dot4G_OPEN_VLAN",
        "twoFourG_WPA2_SSID": "EC420_2dot4G_WPA2_VLAN",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID": "EC420_2dot4G_WPA_VLAN",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "EC420_2dot4G_WPA2-EAP_VLAN",
        "ssid_list": [
            "EC420_5G_WPA2_VLAN",
            "EC420_5G_WPA_VLAN",
            "EC420_5G_WPA2-EAP_VLAN",
            "EC420_2dot4G_WPA2_VLAN",
            "EC420_2dot4G_WPA_VLAN",
            "EC420_2dot4G_WPA2-EAP_VLAN"
        ]
    },

    "ecw5211_vlan": {
        "profile_id": "364",
        "childProfileIds": [
            129,
            358,
            359,
            360,
            361,
            10,
            362,
            363
        ],
        "fiveG_WPA2_SSID": "ECW5211_5G_WPA2_VLAN",
        "fiveG_WPA2_PSK": "Connectus123$",
        "fiveG_WPA_SSID": "ECW5211_5G_WPA_VLAN",
        "fiveG_WPA_PSK": "Connectus123$",
        "fiveG_OPEN_SSID": "ECW5211_5G_OPEN_VLAN",
        "fiveG_WPA2-EAP_SSID": "ECW5211_5G_WPA2-EAP_VLAN",
        "twoFourG_OPEN_SSID": "ECW5211_2dot4G_OPEN_VLAN",
        "twoFourG_WPA2_SSID": "ECW5211_2dot4G_WPA2_VLAN",
        "twoFourG_WPA2_PSK": "Connectus123$",
        "twoFourG_WPA_SSID": "ECW5211_2dot4G_WPA_VLAN",
        "twoFourG_WPA_PSK": "Connectus123$",
        "twoFourG_WPA2-EAP_SSID": "ECW5211_2dot4G_WPA2-EAP_VLAN",
        "ssid_list": [
            "ECW5211_5G_WPA2_VLAN",
            "ECW5211_5G_WPA_VLAN",
            "ECW5211_5G_WPA2-EAP_VLAN",
            "ECW5211_2dot4G_WPA2_VLAN",
            "ECW5211_2dot4G_WPA_VLAN",
            "ECW5211_2dot4G_WPA2-EAP_VLAN"
        ]
    }
}
