# Setup development environment for Branch Loans API

# Create .env file if it doesn't exist
if (-not (Test-Path -Path ".env")) {
    Write-Host "Creating .env file from .env.example" -ForegroundColor Cyan
    Copy-Item -Path ".env.example" -Destination ".env" -Force
}

# Create SSL certificates directory if it doesn't exist
$sslDir = "nginx/ssl"
if (-not (Test-Path -Path $sslDir)) {
    Write-Host "Creating SSL directory" -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $sslDir -Force | Out-Null
}

# Generate SSL certificates if they don't exist
if (-not (Test-Path -Path "$sslDir/branchloans.crt")) {
    Write-Host "Generating SSL certificates..." -ForegroundColor Cyan
    & .\generate_ssl_simple.ps1
} else {
    Write-Host "SSL certificates already exist, skipping generation" -ForegroundColor Green
}

# Add hosts file entry
$hostsEntry = "127.0.0.1    branchloans.com www.branchloans.com"
$hostsPath = "$env:windir\System32\drivers\etc\hosts"
$hostsContent = Get-Content -Path $hostsPath -ErrorAction SilentlyContinue

if ($hostsContent -notcontains $hostsEntry) {
    Write-Host "Adding entry to hosts file..." -ForegroundColor Cyan
    try {
        Add-Content -Path $hostsPath -Value "`n# Branch Loans local development" -Force -ErrorAction Stop
        Add-Content -Path $hostsPath -Value $hostsEntry -Force -ErrorAction Stop
        Write-Host "Added branchloans.com to hosts file" -ForegroundColor Green
    } catch {
        Write-Host "Failed to update hosts file. Please run as Administrator or add the following line manually:" -ForegroundColor Yellow
        Write-Host $hostsEntry -ForegroundColor Yellow
    }
} else {
    Write-Host "Hosts file entry already exists" -ForegroundColor Green
}

# Build and start containers
Write-Host "`nBuilding and starting containers..." -ForegroundColor Cyan
$env:COMPOSE_DOCKER_CLI_BUILD=1
$env:DOCKER_BUILDKIT=1

docker-compose up -d --build

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "Access the application at: https://branchloans.com:8443" -ForegroundColor Green
Write-Host "View API documentation at: https://branchloans.com:8443/docs" -ForegroundColor Green
