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
import logging
from http import server
from http.server import HTTPServer, BaseHTTPRequestHandler
from ssl import wrap_socket
from urllib.parse import urlparse, parse_qs
import pprint
from pprint import pprint

class LabelPrinterRequestHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200);
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        self.send_response(200);
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):
        hostname = "";
        mac_address = "";
        model = "";
        serial = "";
        
        length = int(self.headers['Content-Length'])
        field_data = self.rfile.read(length)
        print("Field_data: %s\n"%field_data);
        fields = parse_qs(field_data)
        pprint(fields)
        
        for name in fields:
            print("key %s"%name)
            
        if "mac" in fields:
            mac_address = fields["mac"]
        else:
            self.send_response(400)
            self.send_header("X-Error", "mac address not submitted")
            self.end_headers();
            self.wfile.write(b"Bullshit\n");
            return
        
        if "model" in fields:
            model = fields["model"]
        else:
            self.send_response(400)
            self.send_header("X-Error", "missing model name")
            self.wfile.write(b"Bullshit\n");
            return
                
        if (mac_address is None) or ("" == mac_address):
            self.send_resonse(400)
            self.send_header("X-Error", "mac address empty or unset")
            self.end_headers()
            self.wfile.write(b"missing mac address")
            self.wfile.write(b"Bullshit\n");
            return
            
        if (model is None) or (model == ""):
            self.send_reponse(400)
            self.send_header("X-Error", "missing model name")
            self.end_headers()
            self.wfile.write(b"missing model name")
            return
        
        if fields[hostname] is None:
            hostname = "%s-%s"%(model, mac.substr(-5).replace(":", ""))    
        else:
            hostname = fields[hostname]
            
        print("HOSTNAME "+hostname)

        self.send_response(200);
        self.send_header("Content-type", "text/html")
        self.end_headers()
        print("I'm in POST")


def __main__():
    logging.info("Main Method. Creating CGI Handler")   
    httpd = HTTPServer(('', 8082), LabelPrinterRequestHandler)
    print("Starting LabelPrinter service...")
    httpd.serve_forever()

if __name__ == "__main__":
    __main__()

