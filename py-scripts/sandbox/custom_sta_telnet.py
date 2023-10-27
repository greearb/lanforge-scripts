#!/usr/bin/env python3


# https://docs.python.org/3.8/library/telnetlib.html

# This python script will create a station with customized variables. The command lines will be constructed and then sent over telnet.

# main idea is to provide easy way for user to automate changing station via python
# import getpass
import telnetlib

MGR="192.168.102.211"
PORT="4001"
RESOURCE = 1
RADIO = "wiphy4"
STA_NAME = "sta000"

#add sta args
SSID= "ssid-eap-ap"
KEY = '[BLANK]'
AP = 'DEFAULT'
MAC = '00:11:22:33:41:55'
MODE = 12
ADD_STA_FLAGS = 33555456

#set port
CURRENT_FLAGS = 2147483648
INTEREST_FLAGS = 67158018
REPORT_TIMER = 1000

#set wifi extra
KEY_MANAGEMENT = "WPA-EAP"
PAIRWISE_CIPHERS = "'TKIP CCMP'"
GROUP_CIPHERS = "'TKIP CCMP'"
EAP_METHODS = "TTLS"
EAP_IDENTITY = "testuser"
EAP_ANON_IDENTITY = "anonymous@anon.net"
EAP_PASSWORD = "testpasswd"
PHASE_2 = "auth=MSCHAPV2"

#set wifi custom
CUSTOM_TEXT = ' '


ADD_STA = "add_sta 1 " + str(RESOURCE) + " " + RADIO + " " + STA_NAME + " " + str(ADD_STA_FLAGS) + " " + SSID + " NA " + KEY + " " + AP + " NA " + MAC + " " + str(MODE)
SET_PORT= "set_port 1 " + str(RESOURCE) + " " + STA_NAME + " NA NA NA NA " + str(CURRENT_FLAGS) + " " + MAC + " NA NA NA " + str(INTEREST_FLAGS) + " " + str(REPORT_TIMER)
SET_WIFI_EXTRA = "set_wifi_extra 1 " + str(RESOURCE) + " " + STA_NAME + " " + KEY_MANAGEMENT + " " + PAIRWISE_CIPHERS + " " + GROUP_CIPHERS + " NA NA NA " +  EAP_METHODS + " " + EAP_IDENTITY + " " + EAP_ANON_IDENTITY + " NA " + PHASE_2 + " " + EAP_PASSWORD
#SET_WIFI_CUSTOM =  "set_wifi_custom 1 " + str(RESOURCE) + " " + STA_NAME + " NA " + CUSTOM_TEXT
RESET_PORT = "reset_port 1 " + str(RESOURCE) + " " + STA_NAME + " NA NA"
# commented out lines are for if password is needed
# user = raw_input("Enter your remote account: ")
# password = getpass.getpass()

tn = telnetlib.Telnet(MGR,port=PORT) # Telnet(host=None, port=0[, timeout])

# sample commands
#CMD=b"set_endp_tx_bounds LT-sta0000-0-BE-A 200000 0"
#cmd=b'set_endp_tx_bounds LT-sta0000-0-BE-A 0 300000'

# reading login information
# tn.read_until("login: ")xx:xx:xx:*:*:xx
# tn.write(user + "\n")
# if password:
#    tn.read_until("Password: ")
#    tn.write(password + "\n")
for cmd in [ADD_STA, SET_PORT, SET_WIFI_EXTRA, RESET_PORT]:
    print(cmd)
    cmd_as_bytes = str.encode(cmd)
    tn.read_until(b">>")
    # tn.write(b"set_endp_tx_bounds LT-sta0000-0-BE-A 2000000" +b"\n")
    tn.write(cmd_as_bytes +b"\n")
    #tn.write(b"set_endp_tx_bounds LT-sta0000-0-BE-A 3000000" +b"\n")
tn.write(b"exit\n")

print(tn.read_all().decode('ascii'))
