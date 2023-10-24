#!/usr/bin/env python3


# https://docs.python.org/3.8/library/telnetlib.html

# This python script will modify the layer 3 endp traffic 
#   11. Small bursts of data of about 1K (can be configurable) at a 30 second long ransom interval
#    2. Emulate a brief upstream video (e.g. when someone is at the door)

# main idea is to provide easy way for user to automate changing a l3 cx behavior via bash / python
# import getpass
import telnetlib

MGR="192.168.0.103"
PORT="4001"

# commented out lines are for if password is needed
# user = raw_input("Enter your remote account: ")
# password = getpass.getpass()

tn = telnetlib.Telnet(MGR,port=PORT) # Telnet(host=None, port=0[, timeout])

# sample commands
CMD=b'set_endp_tx_bounds LT-sta0000-0-BE-A 300000'
#CMD=b"set_endp_tx_bounds LT-sta0000-0-BE-A 200000 0"
#CMD=b'set_endp_tx_bounds LT-sta0000-0-BE-A 0 300000'

# reading login information
# tn.read_until("login: ")
# tn.write(user + "\n")
# if password:
#    tn.read_until("Password: ")
#    tn.write(password + "\n")
tn.read_until(b">>")
# tn.write(b"set_endp_tx_bounds LT-sta0000-0-BE-A 2000000" +b"\n")
tn.write(CMD +b"\n")
#tn.write(b"set_endp_tx_bounds LT-sta0000-0-BE-A 3000000" +b"\n")
tn.write(b"exit\n")

print(tn.read_all().decode('ascii'))
