openssl genrsa -out rootCA.key 1024
openssl req -x509 -new -nodes -key rootCA.key -days 1024 -out rootCA.pem
