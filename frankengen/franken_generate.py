#!/usr/bin/env python
from __future__ import print_function
import franken_core
import franken_util
from OpenSSL import crypto 
import sys
import franken_conf_parse

if (len(sys.argv)<5):
    print("Usage: "+sys.argv[0]+" "+"seed_cert_path"+" ca_cert "+\
                " out_cert_path "+ " count " +" [config] ")
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
sys.stdout.write("Generating frankencerts")
max_certs_in_mem = 200
nc = int(n_outcert/max_certs_in_mem)
remaining_cnt = n_outcert
for i in range(nc+1):
    if (remaining_cnt > max_certs_in_mem):
        franken_certs = franken_core.generate(certs, ca_cert, ca_private_key, \
                                    fconf, count=max_certs_in_mem)
        remaining_cnt = remaining_cnt - max_certs_in_mem
    else:
        franken_certs = franken_core.generate(certs, ca_cert, ca_private_key, \
                                    fconf, count=remaining_cnt)
        remaining_cnt = 0
                
    franken_util.dump_certs(franken_certs, "frankencert", out_cert_path, max_certs_in_mem*i)
    del franken_certs

sys.stdout.write("\n")     
sys.stdout.flush()   
