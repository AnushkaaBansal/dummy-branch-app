# Create directory if it doesn't exist
$sslDir = "nginx/ssl"
if (-not (Test-Path -Path $sslDir)) {
    New-Item -ItemType Directory -Path $sslDir | Out-Null
}

# Create a simple self-signed certificate using OpenSSL in Docker
docker run --rm -v "${PWD}/nginx/ssl:/ssl" alpine sh -c "\
    apk add --no-cache openssl && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /ssl/branchloans.key \
    -out /ssl/branchloans.crt \
    -subj '/CN=branchloans.com' \
    -addext 'subjectAltName=DNS:branchloans.com,DNS:www.branchloans.com,IP:127.0.0.1' && \
    cat /ssl/branchloans.key /ssl/branchloans.crt > /ssl/branchloans.pem"

# Set proper permissions on the generated files
if (Test-Path -Path "$sslDir/branchloans.key") {
    icacls "$sslDir/branchloans.key" /inheritance:r /grant:r "$env:USERNAME:(R)" | Out-Null
}
if (Test-Path -Path "$sslDir/branchloans.crt") {
    icacls "$sslDir/branchloans.crt" /inheritance:r /grant:r "$env:USERNAME:(R)" | Out-Null
}
if (Test-Path -Path "$sslDir/branchloans.pem") {
    icacls "$sslDir/branchloans.pem" /inheritance:r /grant:r "$env:USERNAME:(R)" | Out-Null
}

Write-Host "SSL certificate and key generated in $sslDir/ directory" -ForegroundColor Green
Write-Host "Files created:" -ForegroundColor Cyan
Get-ChildItem -Path $sslDir | Select-Object Name, Length, LastWriteTime
