#!/bin/sh
# This script pulls frankencert from github and initializes the differential testing experiment environment.
# This script builds openssl-1.0.1e, gnutls-3.1.9.1 and nettle, which is required for building gnutls. 
# This script compiles the openssl client with openssl-1.0.1e library statically.(located in frankencert/utils/src/opensslconnect)
# This script also compiles the gnutls client with gnutls-3.1.9.1 dynamically.(located in frankencert/utils/src/gnutlsconnect)

# Before using this script, please change locallib variable to a local folder for installing libraries.
locallib="/home/username/local"

mkdir -p locallib

git clone https://github.com/sumanj/frankencert.git
cd frankencert
cd utils
tar zxvf sample_seed_certs.tar.gz
tar zxvf differential_testing_sample_clients.tar.gz
cd ../pyOpenSSL-0.13/
#python setup.py install --user
cd ../../


#Get openssl-1.0.1e

wget https://www.openssl.org/source/old/1.0.1/openssl-1.0.1e.tar.gz
tar zxvf openssl-1.0.1e.tar.gz
cd openssl-1.0.1e
./config
make
make INSTALL_PREFIX=$locallib install_sw
cd ../frankencert/utils/src/opensslconnect/
# compile openssl client
gcc connect.c -o connect -l:${locallib}/usr/local/ssl/lib/libssl.a -l:${locallib}/usr/local/ssl/lib/libcrypto.a -ldl

cd ../../../../


#Get nettle

wget https://ftp.gnu.org/gnu/nettle/nettle-2.5.tar.gz
tar zxvf nettle-2.5.tar.gz
cd nettle-2.5
./configure --prefix=$locallib --enable-shared
make
make install
cd ../


# Get gnutls-3.1.9.1.tar.xz

wget https://www.gnupg.org/ftp/gcrypt/gnutls/v3.1/gnutls-3.1.9.1.tar.xz
tar xvfJ gnutls-3.1.9.1.tar.xz
cd gnutls-3.1.9
./configure --with-libnettle-prefix=$locallib -with-libdir=$locallib --prefix=$locallib

make
make install
cd ../frankencert/utils/src/gnutlsconnect/
# compile gnutls client
gcc connect.c -o connect  -I${locallib}/include -L${locallib}/lib/ -lgnutls

cd ../../../../
echo "openssl client: ./frankencert/utils/src/opensslconnect/connect"
echo "gnutls client: ./frankencert/utils/src/gnutlsconnect/connect"
