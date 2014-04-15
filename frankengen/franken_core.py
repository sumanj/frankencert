from OpenSSL import crypto
import random
import collections
import sys

def get_extension_dict(certs):
    d = collections.defaultdict(dict)
    for cert in certs:
        extensions = get_extensions(cert)
        for i,extension in enumerate(extensions):
            """
            PyOpenSSL's get_short_name return UNKN for all unknown extensions
            This is bad for a mapping, our patched PyOpenSSL code has a 
            get_oid function.
            """
            d[extension.get_oid()][extension.get_data()] = extension
    for k in d.keys():
        d[k] = d[k].values()
    return d

def get_extensions(cert):
    return  [cert.get_extension(i) \
                for i in range(0, cert.get_extension_count())]

def generate_cert(certificates, pkey, signing_key, issuer, max_extensions, \
                  extensions, flip_probability=0.25, \
                  ext_mod_probability=0.0, invalid_ts_probability = 0.0, \
                  hash_for_sign="sha1", randomize_serial=False):
    cert = crypto.X509()
   

    cert.set_pubkey(pkey)
    pick = random.choice(certificates)
    cert.set_notAfter(pick.get_notAfter())
    pick = random.choice(certificates)
    cert.set_notBefore(pick.get_notBefore())
    if randomize_serial:
        cert.set_serial_number(random.randint(2**128,2**159))
    else:
        pick = random.choice(certificates)
        cert.set_serial_number(pick.get_serial_number())
    pick = random.choice(certificates)
    cert.set_subject(pick.get_subject())
    if not issuer is None:
        cert.set_issuer(issuer)
    else:
        cert.set_issuer(cert.get_subject())

    # overwrite the timestamps if asked by the user
    if random.random() < invalid_ts_probability:
        if random.random() < 0.5:
            notvalidyet = b(datetime.now() + timedelta(days=1).\
                                strftime("%Y%m%d%H%M%SZ"))
            cert.set_notBefore(notvalidyet)
        else:
            expired = b(datetime.now() - timedelta(days=1).\
                                strftime("%Y%m%d%H%M%SZ"))
            cert.set_notBefore(expired)
                
        
    # handle the extensions
    # Currently we chose [0,max] extension types
    # then pick one entry randomly from each type
    # Hacked pyOpenSSL to support poking into the data
    # TODO: Multiple extensions of the same type?
    sample = random.randint(0, max_extensions)
    choices = random.sample(extensions.keys(), sample)
    new_extensions = [random.choice(extensions[name]) for name in choices]
    for extension in new_extensions:
        if random.random() < flip_probability:
            extension.set_critical(1 - extension.get_critical())
        if random.random() < ext_mod_probability:
            randstr = "".join( chr(random.randint(0, 255)) for i in range(7))
            extension.set_data(randstr)
        
    cert.add_extensions(new_extensions)
    if not issuer is None:
        cert.sign(signing_key, hash_for_sign)
    else:
        cert.sign(pkey,hash_for_sign)
    return pkey, cert

def generate(certificates, ca_cert, ca_key, fconfig, count=1, \
             extensions = None):

    certs = []

    flip_probability = fconfig["flip_critical_prob"]
    self_signed_probability = fconfig["self_signed_prob"]
    max_depth = fconfig["max_depth"]
    max_extensions = fconfig["max_extensions"]
    public_key_len = fconfig["public_key_len"]

    if extensions is None:
        extensions = get_extension_dict(certificates)

    max_extensions = min(max_extensions, len(extensions.keys()))
  
    #generate the key pairs once and reuse them for faster 
    #frankencert generation  
    pkeys = []
    for i in range(max_depth):
        pkey = crypto.PKey()
        pkey.generate_key(crypto.TYPE_RSA, public_key_len)
        pkeys.append(pkey)        

    progressbar_size = 10
    if (count>progressbar_size):
        step = count/progressbar_size
    else:
        step = 1 
    for i in range(count):
        if (i%step==0):
                sys.stdout.write(".")     
                sys.stdout.flush()     
            
        chain = []
        signing_key = ca_key
        issuer = ca_cert.get_subject()
        key = None
        length = random.randint(1,max_depth)
        if length == 1 and random.random() < self_signed_probability:
            issuer = None
        for j in range(length):
            key, cert = generate_cert(certificates, pkeys[j], signing_key, issuer, \
                         max_extensions, extensions, fconfig["flip_critical_prob"], \
                          fconfig["ext_mod_prob"], fconfig["invalid_ts_prob"], \
                        fconfig["hash_for_sign"], fconfig["randomize_serial"])
            signing_key = key
            issuer = cert.get_subject()
            chain.append(cert)
        certs.append((key,list(reversed(chain))))
    
    return certs
