# Verify Branch Loans API setup

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Check if containers are running
$containers = docker-compose ps --services --filter "status=running" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error checking container status. Make sure you've run setup-dev.ps1 first." -ForegroundColor Red
    exit 1
}

# Check required services
$requiredServices = @("db", "api", "nginx")
$missingServices = @()

foreach ($service in $requiredServices) {
    if ($containers -notcontains $service) {
        $missingServices += $service
    }
}

if ($missingServices.Count -gt 0) {
    Write-Host "The following services are not running:" -ForegroundColor Yellow
    $missingServices | ForEach-Object { Write-Host "- $_" -ForegroundColor Yellow }
    Write-Host "`nPlease run 'docker-compose up -d' to start the services." -ForegroundColor Yellow
    exit 1
}

# Test API health endpoint
$healthUrl = "https://localhost:8443/health"
Write-Host "`nTesting API health endpoint: $healthUrl" -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri $healthUrl -SkipCertificateCheck -ErrorAction Stop
    $status = $response.Content | ConvertFrom-Json
    
    if ($status.status -eq "ok") {
        Write-Host "✅ API is healthy!" -ForegroundColor Green
        Write-Host "Status: $($status.status)" -ForegroundColor Green
        Write-Host "Version: $($status.version)" -ForegroundColor Green
        Write-Host "Environment: $($status.environment)" -ForegroundColor Green
    } else {
        Write-Host "❌ API is not healthy" -ForegroundColor Red
        Write-Host "Status: $($status.status)" -ForegroundColor Red
        Write-Host "Error: $($status.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Failed to connect to the API" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test database connection
Write-Host "`nTesting database connection..." -ForegroundColor Cyan
try {
    $dbContainer = docker-compose ps -q db
    if ($dbContainer) {
        $dbCheck = docker exec $dbContainer pg_isready -U postgres -d microloans
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Database connection successful!" -ForegroundColor Green
            $dbVersion = docker exec $dbContainer psql -U postgres -d microloans -t -c "SELECT version();"
            Write-Host "Database: $($dbVersion.Trim())" -ForegroundColor Green
            
            # Check if tables exist
            $tables = docker exec $dbContainer psql -U postgres -d microloans -t -c "\dt" | Measure-Object -Line
            if ($tables.Lines -gt 1) {
                Write-Host "✅ Database tables exist" -ForegroundColor Green
            } else {
                Write-Host "⚠️  No tables found in the database. Did you run the migrations?" -ForegroundColor Yellow
            }
        } else {
            Write-Host "❌ Database connection failed" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Database container not found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Failed to check database connection" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test HTTPS access
Write-Host "`nTesting HTTPS access..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "https://branchloans.com:8443/health" -SkipCertificateCheck -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ HTTPS access is working!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  HTTPS access returned status code: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Failed to access via HTTPS" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Check if hosts file entry exists
$hostsEntry = "127.0.0.1    branchloans.com www.branchloans.com"
$hostsContent = Get-Content "$env:windir\System32\drivers\etc\hosts" -ErrorAction SilentlyContinue

if ($hostsContent -contains $hostsEntry) {
    Write-Host "✅ Hosts file entry exists" -ForegroundColor Green
} else {
    Write-Host "❌ Hosts file entry is missing" -ForegroundColor Red
    Write-Host "Please add the following line to your hosts file (C:\Windows\System32\drivers\etc\hosts):" -ForegroundColor Yellow
    Write-Host $hostsEntry -ForegroundColor White -BackgroundColor DarkGray
}

# Final status
Write-Host "`nSetup verification complete!" -ForegroundColor Cyan
Write-Host "Access the application at: https://branchloans.com:8443" -ForegroundColor Cyan
Write-Host "View API documentation at: https://branchloans.com:8443/docs" -ForegroundColor Cyan
