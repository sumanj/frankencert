#!/usr/bin/env python
from datetime import datetime, timedelta
import os
from OpenSSL import crypto
import subprocess
import sys

#write out all the certs
def dump_certs(certs, prefix, path, name_begin=0):
    for i,cert in enumerate(certs):
        key,certs = cert
        with open(os.path.join(path, "%s-%d.pem" % (prefix, name_begin+i)), \
                   "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
            for cert in certs:
                f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))


#load all certs from a directory
def load_dir(path):      
    certs = []        
    files = os.listdir(path)
    nfiles =  len(files)                                               
    files = map(lambda f : os.path.join(path, f), files)
    step = max(1,nfiles/10)
    count  = 0
    sys.stdout.write("Loading seed certificates") 
    for infile in files:
        count = (count+1) % step
        if (count==0):
            sys.stdout.write(".") 
            sys.stdout.flush()
        with open(infile) as f:
            buf = f.read()
            try:
                certs.append(crypto.load_certificate(crypto.FILETYPE_PEM, buf))
            except:
                print("Skipping: "+infile)
    sys.stdout.write("\n")
    sys.stdout.flush()
 
    return certs

#recycle an existing certfile containing arbitrarily long cert chains 
#with new CA  
def recycle_cert(inpath, outpath, cafile, fix_timestamps):
    incerts = []
    with open(inpath) as f:
        buf = f.read()
        pattern = "-----BEGIN CERTIFICATE-----"
        index  = 0
        while True:
            index = buf.find(pattern, index)
            if (index==-1):
                break
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, buf[index:])
            index = index + len(pattern)
            incerts.append(cert)
    with open(cafile) as f:
        buf = f.read()
        cacert = crypto.load_certificate(crypto.FILETYPE_PEM, buf)
    
    with open(cafile) as f:
        buf = f.read()
        cakey = crypto.load_privatekey(crypto.FILETYPE_PEM, buf)
    
    print(len(incerts))
   
    pkeys = [] 
    for i in range(len(incerts)):
        pkey = crypto.PKey()
        pkey.generate_key(crypto.TYPE_RSA, 1024)
        pkeys.append(pkey)
    
    for i in range(len(incerts)):
        incerts[i].set_pubkey(pkeys[i])
        if (fix_timestamps):
            now = b(datetime.now().strftime("%Y%m%d%H%M%SZ"))
            expire  = b((datetime.now() + timedelta(days=100))\
                   .strftime("%Y%m%d%H%M%SZ"))
            incerts[i].set_notBefore(now)
            incerts[i].set_notAfter(expire)
   
        if (i==len(incerts)-1): 
            incerts[i].set_issuer(cacert.get_subject())
            incerts[i].sign(cakey,"sha1")
        else:    
            incerts[i].set_issuer(incerts[i+1].get_subject())
            incerts[i].sign(pkeys[i+1],"sha1")

    
    with open(outpath, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkeys[0]))
        for i in range(len(incerts)):
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, incerts[i]))

#Print all certs in a file, openssl x509 only prints the first one 
#Uses the openssl x509 command, pretty hacky but it works 
def print_cert(inpath):
    output = ""

    with open(inpath) as f:
        buf = f.read()
        pattern = "-----BEGIN CERTIFICATE-----"
        index  = 0
        i = 0
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
    print(output.find("Certificate:"))
    print(output)
