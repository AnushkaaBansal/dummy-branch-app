# Create directory if it doesn't exist
$sslDir = "nginx/ssl"
if (-not (Test-Path -Path $sslDir)) {
    New-Item -ItemType Directory -Path $sslDir | Out-Null
}

# Generate a private key
openssl genrsa -out "$sslDir/branchloans.key" 2048

# Create a self-signed certificate
openssl req -new -x509 \
    -key "$sslDir/branchloans.key" \
    -out "$sslDir/branchloans.crt" \
    -days 3650 \
    -subj "/CN=branchloans.com" \
    -addext "subjectAltName=DNS:branchloans.com,DNS:www.branchloans.com,IP:127.0.0.1"

# Create a combined PEM file (certificate + key)
Get-Content "$sslDir/branchloans.key", "$sslDir/branchloans.crt" | Set-Content "$sslDir/branchloans.pem"

Write-Host "SSL certificate and key generated in $sslDir/ directory"
Write-Host "Files created:"
Get-ChildItem -Path $sslDir | Select-Object Name, Length, LastWriteTime
