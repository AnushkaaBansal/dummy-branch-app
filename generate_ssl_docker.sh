#!/bin/bash

# Create ssl directory if it doesn't exist
mkdir -p nginx/ssl

# Generate a private key and self-signed certificate using Docker
cat > nginx/ssl/generate_ssl.sh << 'EOF'
#!/bin/sh

# Create a temporary directory
TEMP_DIR=$(mktemp -d)

# Generate a private key
openssl genrsa -out "$TEMP_DIR/branchloans.key" 2048

# Create a self-signed certificate
openssl req -new -x509 \
    -key "$TEMP_DIR/branchloans.key" \
    -out "$TEMP_DIR/branchloans.crt" \
    -days 3650 \
    -subj "/CN=branchloans.com" \
    -addext "subjectAltName=DNS:branchloans.com,DNS:www.branchloans.com,IP:127.0.0.1"

# Create a combined PEM file (certificate + key)
cat "$TEMP_DIR/branchloans.key" "$TEMP_DIR/branchloans.crt" > "$TEMP_DIR/branchloans.pem"

# Copy the files to the output directory
cp "$TEMP_DIR/branchloans.key" "/ssl/"
cp "$TEMP_DIR/branchloans.crt" "/ssl/"
cp "$TEMP_DIR/branchloans.pem" "/ssl/"

# Set proper permissions
chmod 400 "/ssl/branchloans.key" "/ssl/branchloans.crt" "/ssl/branchloans.pem"

# Clean up
rm -rf "$TEMP_DIR"

echo "SSL certificate and key generated in /ssl/"
ls -la /ssl/
EOF

# Make the script executable
chmod +x nginx/ssl/generate_ssl.sh

# Run the script inside a Docker container
docker run --rm -v "$(pwd)/nginx/ssl:/ssl" alpine sh -c "\
    apk add --no-cache openssl && \
    /bin/sh /ssl/generate_ssl.sh"

# Clean up
rm -f nginx/ssl/generate_ssl.sh

echo "SSL certificates have been generated in nginx/ssl/"
ls -la nginx/ssl/
