#!/usr/bin/env python3
"""
This is a small python webserver intended to run on a testing network resource
where the lf_kinstall.pl script can post build machine information to. A useful
place to install this script would be on an APU2 being used as a VPN gateway.

Use these commands to install the script:

$ sudo cp label-printer.py /usr/local/bin
$ sudo chmod a+x /usr/local/bin/label-printer.py

$ sudo cp label-printer.service /lib/systemd/system
$ sudo systemctl add-wants multi-user.target label-printer.service
$ sudo systemctl daemon-reload
$ sudo systemctl restart label-printer.service

At this point, if you use `ss -ntlp` you should see this script listening on port 8082.

If you are running ufw on your label-printer host, please use this command to allow
traffice to port 8082:
$ sudo ufw allow 8082/tcp
$ sudo ufw reload

Using kinstall to print labels:

$ ./lf_kinstall.pl --print-label http://192.168.9.1:8082/


"""
