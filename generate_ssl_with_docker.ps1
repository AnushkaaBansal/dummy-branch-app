# Script to generate SSL certificates using Docker

# Create directories if they don't exist
$sslDir = "nginx/ssl"
if (-not (Test-Path -Path $sslDir)) {
    New-Item -ItemType Directory -Path $sslDir | Out-Null
}

# Check if Docker is running
try {
    $dockerVersion = docker --version
    Write-Host "Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "Docker is not installed or not running. Please install Docker Desktop and start it before running this script." -ForegroundColor Red
    exit 1
}

# Generate SSL certificates using Docker
Write-Host "Generating SSL certificates using Docker..." -ForegroundColor Cyan

docker run --rm -v "${PWD}/nginx/ssl:/ssl" alpine/openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /ssl/branchloans.key \
  -out /ssl/branchloans.crt \
  -subj "/C=US/ST=California/L=San Francisco/O=Branch/CN=branchloans.com" \
  -addext "subjectAltName=DNS:branchloans.com,DNS:www.branchloans.com"

# Create combined certificate file for Nginx
Write-Host "Creating combined certificate file..." -ForegroundColor Cyan
Get-Content "$sslDir/branchloans.crt", "$sslDir/branchloans.key" | Set-Content "$sslDir/branchloans.pem" -Encoding UTF8

# Set proper permissions (not strictly necessary on Windows, but good practice)
if ($IsLinux -or $IsMacOS) {
    chmod 400 "$sslDir/branchloans.key"
    chmod 444 "$sslDir/branchloans.crt"
}

Write-Host "`nSSL certificates generated successfully in '$sslDir'" -ForegroundColor Green
Write-Host "Files created:" -ForegroundColor Yellow
Get-ChildItem -Path $sslDir\* | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize

# Install certificate in Windows Certificate Store (requires admin privileges)
try {
    Write-Host "`nInstalling certificate in Windows Certificate Store..." -ForegroundColor Cyan
    $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2("$PWD\$sslDir\branchloans.crt")
    $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "LocalMachine")
    $store.Open("ReadWrite")
    $store.Add($cert)
    $store.Close()
    Write-Host "Certificate installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "`nWarning: Could not install certificate automatically." -ForegroundColor Yellow
    Write-Host "Please install the certificate manually by double-clicking on '$sslDir\branchloans.crt'" -ForegroundColor Yellow
    Write-Host "and selecting 'Install Certificate' -> 'Local Machine' -> 'Place all certificates in the following store' -> 'Trusted Root Certification Authorities'" -ForegroundColor Yellow
}

Write-Host "`nSetup complete! You can now start the application using 'docker-compose up -d'" -ForegroundColor Green
