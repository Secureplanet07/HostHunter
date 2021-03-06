#
#    | $$  | $$                      | $$    | $$  | $$                      | $$
#    | $$  | $$  /$$$$$$   /$$$$$$$ /$$$$$$  | $$  | $$ /$$   /$$ /$$$$$$$  /$$$$$$    /$$$$$$   /$$$$$$
#    | $$$$$$$$ /$$__  $$ /$$_____/|_  $$_/  | $$$$$$$$| $$  | $$| $$__  $$|_  $$_/   /$$__  $$ /$$__  $$
#    | $$__  $$| $$  \ $$|  $$$$$$   | $$    | $$__  $$| $$  | $$| $$  \ $$  | $$    | $$$$$$$$| $$  \__/
#    | $$  | $$| $$  | $$ \____  $$  | $$ /$$| $$  | $$| $$  | $$| $$  | $$  | $$ /$$| $$_____/| $$
#    | $$  | $$|  $$$$$$/ /$$$$$$$/  |  $$$$/| $$  | $$|  $$$$$$/| $$  | $$  |  $$$$/|  $$$$$$$| $$
#    |__/  |__/ \______/ |_______/    \___/  |__/  |__/ \______/ |__/  |__/   \___/   \_______/|__/1
#
# Author : Andreas Georgiou (superhedgy)
# Email  : ageorgiou@trustwave.com
# Version: v1.0
#
#
# Usage Example:
#
# $ python hosthunter.py <targets.txt>
#
# $ cat vhosts.csv
#

import argparse
import sys
import ssl
import socket
import time
import requests
import OpenSSL
import urllib2
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

path = sys.argv[1]
targets = open(path,"r")
vhostsf = open("vhosts.csv", "wb")
vhostsf.write("IP Address,Port/Protocol,Domains,Operating System,OS Version,Notes\n") #vhosts.csv Header
counter=0
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_OPTIONAL
context.load_default_certs()

start_time = time.time()
print "\n HostHunter v1.0"
print " Author: ageorgiou@trustwave.com\n"
version='v1.0'

# Read targets.txt file
for ip in targets:
    ip=ip.replace("\n","")
    print "\n[+] Target: %s" % ip
    hostnames=''
# Querying HackerTarget.com API
    try:
        r2 = urllib2.urlopen('https://api.hackertarget.com/reverseiplookup/?q=%s' % ip).read()

        if (r2.find("No DNS A records found")==-1) and (r2.find("API count exceeded")==-1):
            hostnames=r2
        else:
            hostnames=''
    except urllib2.HTTPError as e:
        print "[*] Error connecting with HackerTarget.com API"

# Fetch SSL certificate
    try:
        # Hack to make things faster
        r = requests.get('https://%s' % ip, timeout=5,verify=False)
        cert=ssl.get_server_certificate((ip, 443))
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
        cert_hostname=x509.get_subject().CN
        hostnames = hostnames + cert_hostname
    except (requests.ConnectionError,requests.Timeout,socket.error) as e:
        pass

    if hostnames != "":
        print "[+] Hostnames: \n%s" % hostnames
        row = "\"" + ip + "\"," + "\"443/tcp\"" + "," + "\"" + hostnames.replace("\n",",") + "\""  + "\n"
        counter += 1
        vhostsf.write(row)
    else:
        print "[-] Hostnames: no results "
        continue

# END IF
targets.close()

#  Robtex
#  https://freeapi.robtex.com/pdns/reverse/193.56.46.229


print "\n\n Reconnaissance Completed!\n"
print "\n %s hostnames were discovered in %s sec\n\n" % (counter,round(time.time() - start_time,2))
