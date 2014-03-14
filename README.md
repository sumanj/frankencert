FrankenCert - Adversarial Testing of Certificate Validation in SSL/TLS Implementations
=======================================================================================

###What are FrankenCerts?
FrankenCerts are specifically crafted SSL certificates for testing certificate 
validation code in SSL/TLS implementations. The technique is described in 
detail in the IEEE Symposium on Security and Privacy (Oakland) 2014 paper -
*Using Frankencerts for Automated Adversarial Testing of Certificate Validation 
in SSL/TLS Implementations* by Chad Brubaker, Suman Jana, Baishakhi Ray, 
Sarfraz Khurshid, and Vitaly Shmatikov. 


###Why is FrankenCert useful?
FrankenCert is essentially a smart fuzzer for SSL/TLS certificate validation
code. If you are a developer who is implementing any sort of SSL/TLS certificate 
validation code (either as part of a SSL/TLS library or an application), you 
can use the frankencert generator to auto-generate different test certificates 
involving complex corner cases. 

We have successfully used FrankenCerts to find serious vulnerabilities 
in GnuTLS, PolarSSL, CyaSSL, and MatrixSSL as described in the Oakland 
2014 paper. We also found several how SSL/TLS implementations report 
errors back to the user. For example, when presented with an expired,
self-signed certificate, NSS, Chrome on Linux, and Safari reports that 
the certificate has expired but not that the issuer is invalid.


###How does FrankenCert work?
The basic idea of FrankenCert is to take a bunch of certificates as seeds 
and use random mutations on different fields and extensions to creat new 
test certificates(frankencerts). Thus, FrankenCertS can help in systematically 
testing correctness of the certificate validation code.

###Installation & Usage
1. Install OpenSSL libraries and utilities  if you already haven not.

2. The frankencert generator needs a modified verison of PyOpenSSL. 
   We have included the source for our modified version of PyOpenSSL. 
   You will need to install it in order to use the frankencert geneartor. 
   First, uninstall any other version of PyOpenSSL that you may have 
   installed on your computer. Go to the `pyOpenSSL-0.13` directory and 
   build/install PyOpenSSL by issuing `sudo python setup.py install`.

3. Once you have the patched pyOpenSSL set up, to generate frankencerts, 
   use the `franken_generate.py` script: `python franken_generate.py 
   seed_certs_dir ca_cert output_dir count [config_file]`.

   The arguments are explained below.

   - `seed_certs_dir`: FrankenCert generator needs a set of seed certificates. 
      Any SSL cert in PEM fromat can act as a seed cert. `seed_certs_dir`
      can be any directory containing the seed certs stored as PEM files.
   
      You can either use tools like ZMap(https://zmap.io/) to collect SSL seed 
      certificates or use some of the SSL certs available from https://www.eff.org/observatory.
      You do not need access to the corresponding private keys to use the certs 
      as seeds. 
   
      For your convenience, we have included a tarball containing around 1000 seed 
      certificates in `utils/sample_seed_certs.tar.gz`. 

   - `ca_cert`: You will also need to create a self-signed CA certificate to sign 
      the frankencerts. You can either use the included sample CA certificate 
      `utils/rootCA_key_cert.pem` or use the `utils/create_new_ca.sh` script to 
      create your own root CA. For any root CA that you use for frankencert 
      generation, make sure that your SSL certificate validation code treats 
      it as a trusted certificate.

   - `output_dir`: It will contain the generated frankencerts. The frankencerts 
      will be named as `frankencert-<number>.pem`. 

   - `count`: Number of frankencerts to be generated. 

   - `config_file`: An optional argument to tune the frankencert generation process.
      Take a look at the `utils/sample_franken.conf` for a sample config file.

4. If you want to test your SSL/TLS client with the generated frankencerts, you 
   should use the `utils/test_ssl_server.py` script to set up a SSL server that 
   can send the generated frankencerts as part of the SSL handshake. 


### Project structure
 - The `frankengen` directory contains the frankencert generator code
 - Our patched version of pyOpenSSL is inside `pyOpenSSL-0.13` directory
 - Several useful tools are included in `utils`
    - `cert_print.py`: a tool for printing frankencerts. It requires OpenSSL
      to be installed and present in the path.
    - `rootCA_key_cert.pem`: private key and self-signed cert of a sample CA
      that can be used for signing frankencerts.
    - `create_new_ca.sh`: a script for creating new CA with a self-signed cert.
      It creates the output cert and private key in rootCA.pem (requires OpenSSL). 
    - `test_ssl_server.py`: a SSL/TLS sample server for serving frankencerts 
      to SSL clients
    - `sample_seed_certs.tar.gz`: Some sample certs that may be used as seeds for 
      frankencert generation. 
    - `sample_franken.conf`: A sample config file that can be used to tune 
      different parameters of the frankencer generation process. 

