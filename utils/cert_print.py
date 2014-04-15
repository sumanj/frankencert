#!/usr/bin/env python
import subprocess
import sys
#Print all certs in a file, openssl x509 only prints the first one 
#Uses the openssl x509 command, pretty hacky but it works 
def print_cert(inpath):
    output = ""
    i = 0

    with open(inpath) as f:
        buf = f.read()
        pattern = "-----BEGIN CERTIFICATE-----"
        index  = 0
        while True:
            index = buf.find(pattern, index)
            if (index==-1):
                break
                p = subprocess.Popen(["openssl", "x509", "-text"], \
                                stdout=subprocess.PIPE, stdin=subprocess.PIPE,\
                                stderr=subprocess.STDOUT)
                output += p.communicate(input=buf[index:])[0]
            index = index + len(pattern)
            i += 1
    print output 

if (len(sys.argv)<2):
    print "Usage: "+sys.argv[0]+" "+"cert_file"

print "Printing all certs from "+sys.argv[1]+":"
print_cert(sys.argv[1])
