#!/bin/bash

# Create ssl directory if it doesn't exist
mkdir -p nginx/ssl

# Generate private key and self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/branchloans.key \
  -out nginx/ssl/branchloans.crt \
  -subj "/C=US/ST=California/L=San Francisco/O=Branch/CN=branchloans.com" \
  -addext "subjectAltName=DNS:branchloans.com,DNS:www.branchloans.com"

echo "SSL certificate and key generated in nginx/ssl/ directory"
