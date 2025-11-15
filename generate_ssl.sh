#!/bin/bash

# Create a temporary directory for certificate generation
TEMP_DIR=$(mktemp -d)

# Generate a private key
openssl genrsa -out $TEMP_DIR/branchloans.key 2048

# Create a self-signed certificate
openssl req -new -x509 \
    -key $TEMP_DIR/branchloans.key \
    -out $TEMP_DIR/branchloans.crt \
    -days 3650 \
    -subj "/CN=branchloans.com" \
    -addext "subjectAltName=DNS:branchloans.com,DNS:www.branchloans.com,IP:127.0.0.1"

# Create a combined PEM file (certificate + key)
cat $TEMP_DIR/branchloans.key $TEMP_DIR/branchloans.crt > $TEMP_DIR/branchloans.pem

# Copy the files to the nginx/ssl directory
mkdir -p nginx/ssl
cp $TEMP_DIR/branchloans.* nginx/ssl/

# Set proper permissions
chmod 400 nginx/ssl/branchloans.*

# Clean up
echo "SSL certificates have been generated in nginx/ssl/"
ls -la nginx/ssl/
