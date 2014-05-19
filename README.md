Frankencert - Adversarial Testing of Certificate Validation in SSL/TLS Implementations
=======================================================================================

###What are frankencerts?
Frankencerts are specially crafted SSL certificates for testing certificate 
validation code in SSL/TLS implementations. The technique is described in 
detail in the 2014 IEEE Symposium on Security and Privacy (Oakland) paper -
*Using Frankencerts for Automated Adversarial Testing of Certificate Validation 
in SSL/TLS Implementations* by Chad Brubaker, Suman Jana, Baishakhi Ray, 
Sarfraz Khurshid, and Vitaly Shmatikov. 


###Why is frankencert generator useful?
Frankencert generator is essentially a smart fuzzer for testing SSL/TLS 
certificate validation code. If you are a developer who is implementing 
any sort of SSL/TLS certificate validation code (either as part of an SSL/TLS 
library or an application), you can use the frankencert generator to 
auto-generate different test certificates involving complex corner cases. 

We have successfully used frankencerts to find serious vulnerabilities 
in GnuTLS, PolarSSL, CyaSSL, and MatrixSSL as described in our Oakland 
2014 paper. We also found several discrepancies between how different 
SSL/TLS implementations report errors back to the user. For example, 
when presented with an expired, self-signed certificate, NSS, Chrome on 
Linux, and Safari report that the certificate has expired but not that 
the issuer is invalid.


###How do frankencerts work?
The basic idea of frankencerts is to take a bunch of certificates as seeds 
and use random mutations on different fields and extensions to create new 
test certificates (frankencerts). Using frankencerts as server-side inputs 
into an SSL/TLS handshake can help systematically test correctness of the 
certificate validation code.

###Installation and Usage
- Install OpenSSL libraries and utilities if you don't have them already.

- The frankencert generator needs a modified version of PyOpenSSL. 
   We have included the source for our modified version of PyOpenSSL. 
   You will need to install it in order to use the frankencert generator. 
   First, uninstall any other version of PyOpenSSL that you may have 
   installed on your computer. Go to the `pyOpenSSL-0.13` directory and 
   build/install PyOpenSSL by issuing `sudo python setup.py install`.

- Once you have the patched pyOpenSSL set up, to generate frankencerts, 
   use the `franken_generate.py` script: `python franken_generate.py 
   seed_certs_dir ca_cert output_dir count [config_file]`.

   The arguments are explained below.

    - `seed_certs_dir`: Frankencert generator needs a set of seed certificates. 
       Any SSL cert in PEM fromat can act as a seed cert. `seed_certs_dir`
       can be any directory containing the seed certs stored as PEM files.
   
       You can either use tools like ZMap (https://zmap.io/) to collect SSL seed 
       certificates, or use some of the SSL certs available from https://www.eff.org/observatory.
       Please note that these are not our tools and repositories - you may want
       to contact their respective developers and maintainers to ensure that your
       usage of the certificates they collected is compatible with the intended purpose.
       You do not need access to the corresponding private keys to use the certs 
       as seeds. 
   
       For your convenience, we have included a tarball containing around 1000 seed 
       certificates in `utils/sample_seed_certs.tar.gz`. 

    - `ca_cert`: You will also need to create a self-signed CA certificate to sign 
       the frankencerts. You can either use the included sample CA certificate 
       `utils/rootCA_key_cert.pem` or use the `utils/create_new_ca.sh` script to 
       create your own root CA. For any root CA that you use for frankencert 
       generation, make sure that your SSL certificate validation code treats 
       its certificate as a trusted root certificate.
       
       VERY IMPORTANT: this root certificate should be trusted ONLY during testing.
       If you accidentally or intentionally deploy SSL/TLS with this certificate still 
       among the trusted root certificates, your SSL/TLS connections may be vulnerable 
       to server impersonation and man-in-the-middle attacks. Be sure to REMOVE this 
       certificate from your trusted root certificates once the testing is finished.

    - `output_dir`: It will contain the generated frankencerts. The frankencerts 
       will be named as `frankencert-<number>.pem`. 

    - `count`: Number of frankencerts to be generated. 

    - `config_file`: An optional argument to tune the frankencert generation process.
      Take a look at the `utils/sample_franken.conf` for a sample config file.

- To test your SSL/TLS client with the generated frankencerts, you should use 
  the `utils/test_ssl_server.py` script to set up an SSL server that can present 
  the generated frankencerts as part of the SSL handshake. 

- If you want to perform differential testing (i.e. compare your SSL/TLS client's 
  behavior with other libraries' behaviors for a given franekencert), you can do 
  so by running SSL clients using those libraries and connecting to a server serving 
  the frankencert. The following example shows how to do this for OpenSSL.
    - Start a SSL server serving the target frankencert using: `./test_ssl_server.py frankencert_name port_no`,
      where `frankencert_name` is the path of the target frankencert and `port_no` is the port the server
      will listen to.
    - Use the command `openssl s_client -CAfile ca_cert -connect host_name:port_no`  to connect to 
      the server and check the certificate verification result printed on the console. The `ca_cert` argument 
      should be the CA certificate you used to generate the frankencert, `port_no` should be the same one that 
      you used for running `test_ssl_server`, and `host_name` should be either localhost or the name of 
      the host running the `test_ssl_server` script. 
  
  NOTE: We plan to make the automated scripts that we used for differential testing available soon. 

### Project structure
 - The `frankengen` directory contains the frankencert generator code
 - Our patched version of pyOpenSSL is inside `pyOpenSSL-0.13` directory
 - Several useful tools are included in `utils`
    - `cert_print.py`: a tool for printing frankencerts. It requires OpenSSL
      to be installed and present in the path.
    - `rootCA_key_cert.pem`: private key and self-signed cert of a sample CA
      that can be used for signing frankencerts.
    - `create_new_ca.sh`: a script for creating new CA with a self-signed cert.
      It creates the output cert and private key in `rootCA.pem` (requires OpenSSL). 
    - `test_ssl_server.py`: a sample SSL/TLS server for presenting frankencerts 
      to SSL/TLS clients
    - `sample_seed_certs.tar.gz`: Some sample certs that may be used as seeds for 
      frankencert generation. 
    - `sample_franken.conf`: A sample config file that can be used to tune 
      different parameters of the frankencert generation process. 

