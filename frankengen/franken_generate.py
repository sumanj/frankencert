#!/usr/bin/env python
import franken_core
import franken_util
from OpenSSL import crypto 
import sys
import franken_conf_parse

if (len(sys.argv)<5):
    print "Usage: "+sys.argv[0]+" "+"[seed_cert_path]"+" [ca_cert] "+\
		" [out_cert_path] "+ " [count] " +" <config> "
    sys.exit(-1)

input_cert_path = sys.argv[1]
ca_cert_path = sys.argv[2]
out_cert_path = sys.argv[3]
n_outcert = int(sys.argv[4])

if (len(sys.argv)>5):
    configfile = sys.argv[5]
else:
    configfile = ""

fconf = franken_conf_parse.parse_config(configfile) 
certs = franken_util.load_dir(input_cert_path)
with open(ca_cert_path, 'rt') as ca_cert_file:
    ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, ca_cert_file.read())

with open(ca_cert_path, 'rt') as ca_key_file:
    ca_private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, \
						ca_key_file.read()) 

franken_certs = franken_core.generate(certs, ca_cert, ca_private_key, \
				fconf, count=n_outcert)

franken_util.dump_certs(franken_certs, "frankencert", out_cert_path)
