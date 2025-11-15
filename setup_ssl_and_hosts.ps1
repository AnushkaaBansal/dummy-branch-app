# Setup SSL certificates and update hosts file for Windows

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "This script requires administrator privileges. Please run as administrator." -ForegroundColor Red
    exit 1
}

# Create directories if they don't exist
$sslDir = "nginx/ssl"
if (-not (Test-Path -Path $sslDir)) {
    New-Item -ItemType Directory -Path $sslDir -Force | Out-Null
}

# Generate SSL certificate
Write-Host "Generating SSL certificate..." -ForegroundColor Cyan
try {
    # Generate private key
    openssl genrsa -out "$sslDir/branchloans.key" 2048
    
    # Generate certificate signing request
    $subject = "/C=US/ST=California/L=San Francisco/O=Branch/CN=branchloans.com"
    openssl req -new -key "$sslDir/branchloans.key" -out "$sslDir/branchloans.csr" -subj $subject -addext "subjectAltName=DNS:branchloans.com,DNS:www.branchloans.com"
    
    # Generate self-signed certificate
    openssl x509 -req -days 365 -in "$sslDir/branchloans.csr" -signkey "$sslDir/branchloans.key" -out "$sslDir/branchloans.crt" -extfile <(echo "subjectAltName=DNS:branchloans.com,DNS:www.branchloans.com")
    
    # Create combined certificate file for Nginx
    Get-Content "$sslDir/branchloans.crt", "$sslDir/branchloans.key" | Set-Content "$sslDir/branchloans.pem"
    
    Write-Host "SSL certificate generated successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error generating SSL certificate: $_" -ForegroundColor Red
    exit 1
}

# Update hosts file
Write-Host "Updating hosts file..." -ForegroundColor Cyan
try {
    $hostsPath = "$env:windir\System32\drivers\etc\hosts"
    $hostsContent = Get-Content $hostsPath -Raw
    $entry = "127.0.0.1`tbranchloans.com www.branchloans.com"
    
    if ($hostsContent -match "branchloans\.com") {
        Write-Host "Hosts entry already exists, skipping..." -ForegroundColor Yellow
    } else {
        Add-Content -Path $hostsPath -Value "`n# Added for Branch Loans local development"
        Add-Content -Path $hostsPath -Value $entry
        Write-Host "Hosts file updated successfully!" -ForegroundColor Green
    }
} catch {
    Write-Host "Error updating hosts file: $_" -ForegroundColor Red
    Write-Host "Please add the following line to your hosts file manually:" -ForegroundColor Yellow
    Write-Host "127.0.0.1    branchloans.com www.branchloans.com" -ForegroundColor Cyan
}

# Install certificate in Windows Certificate Store
Write-Host "Installing certificate in Windows Certificate Store..." -ForegroundColor Cyan
try {
    $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2("$sslDir/branchloans.crt")
    $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "LocalMachine")
    $store.Open("ReadWrite")
    $store.Add($cert)
    $store.Close()
    Write-Host "Certificate installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error installing certificate: $_" -ForegroundColor Red
    Write-Host "Please install the certificate manually by double-clicking on $sslDir/branchloans.crt and selecting 'Install Certificate'" -ForegroundColor Yellow
}

Write-Host "`nSetup completed! You can now access the application at https://branchloans.com" -ForegroundColor Green
Write-Host "If you encounter any certificate warnings, please accept the self-signed certificate in your browser." -ForegroundColor Yellow
