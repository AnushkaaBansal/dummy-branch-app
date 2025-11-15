#!/bin/bash

# Create directory if it doesn't exist
mkdir -p nginx/ssl

# Generate a private key
openssl genrsa -out nginx/ssl/branchloans.key 2048

# Create a self-signed certificate
openssl req -new -x509 \
    -key nginx/ssl/branchloans.key \
    -out nginx/ssl/branchloans.crt \
    -days 365 \
    -subj "/CN=branchloans.com" \
    -addext "subjectAltName=DNS:branchloans.com,DNS:www.branchloans.com"

echo "SSL certificate and key generated in nginx/ssl/ directory"
echo "To trust the certificate on Linux, run:"
echo "sudo cp nginx/ssl/branchloans.crt /usr/local/share/ca-certificates/"
echo "sudo update-ca-certificates"
