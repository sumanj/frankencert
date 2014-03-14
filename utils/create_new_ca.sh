#!/usr/bin/env bash
openssl genrsa -out tmpCA.key 1024
openssl req -x509 -new -nodes -key tmpCA.key -days 1024 -out tmpCA.pem
cat tmpCA.key > rootCA.pem
cat tmpCA.pem >> rootCA.pem
rm tmpCA.pem tmpCA.key
