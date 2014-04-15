import ConfigParser
def parse_config(configfile):
    fconfig = {}

    parser = ConfigParser.SafeConfigParser(defaults={'max_extensions':'20', \
                                'max_depth': '3', \
                                'ext_mod_prob': '0.0', \
                                'flip_critical_prob': '0.25', \
                                'self_signed_prob': '0.25', \
                                'invalid_ts_prob': '0.0', \
                                'public_key_len': '1024', \
                                'hash_for_sign': 'sha1', \
                                'randomize_serial': 'True', \
                                            })
    if (configfile!=""):
        parser.read(configfile)
    
    fconfig = parser.defaults() 
    boolean_trues = ['true', 'yes', 'y', '1']

    fconfig["max_extensions"] = int(fconfig["max_extensions"])
    fconfig["max_depth"] = int(fconfig["max_depth"])
    fconfig["ext_mod_prob"] = float(fconfig["ext_mod_prob"])
    fconfig["flip_critical_prob"] = float(fconfig["flip_critical_prob"])
    fconfig["self_signed_prob"] = float(fconfig["self_signed_prob"])
    fconfig["invalid_ts_prob"] = float(fconfig["invalid_ts_prob"])
    fconfig["public_key_len"] = int(fconfig["public_key_len"])
    fconfig["randomize_serial"] = fconfig["randomize_serial"].lower() in boolean_trues
    
    return fconfig
