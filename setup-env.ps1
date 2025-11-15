# Create .env file if it doesn't exist
if (-not (Test-Path -Path ".env")) {
    Write-Host "Creating .env file from .env.example" -ForegroundColor Cyan
    Copy-Item -Path ".env.example" -Destination ".env" -Force
    
    # Generate a secure secret key
    $secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    $salt = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    
    # Update the .env file with generated values
    (Get-Content .env) -replace 'SECRET_KEY=.*', "SECRET_KEY=$secretKey" | Set-Content .env
    (Get-Content .env) -replace 'SECURITY_PASSWORD_SALT=.*', "SECURITY_PASSWORD_SALT=$salt" | Set-Content .env
    
    Write-Host "Generated new SECRET_KEY and SECURITY_PASSWORD_SALT in .env file" -ForegroundColor Green
} else {
    Write-Host ".env file already exists, skipping creation" -ForegroundColor Green
}

# Update the database configuration in the .env file
$dbUser = "postgres"
$dbPass = "postgres"
$dbName = "microloans"
$dbHost = "db"
$dbPort = 5432

# Update the .env file with database configuration
(Get-Content .env) -replace 'POSTGRES_USER=.*', "POSTGRES_USER=$dbUser" | Set-Content .env
(Get-Content .env) -replace 'POSTGRES_PASSWORD=.*', "POSTGRES_PASSWORD=$dbPass" | Set-Content .env
(Get-Content .env) -replace 'POSTGRES_DB=.*', "POSTGRES_DB=$dbName" | Set-Content .env
(Get-Content .env) -replace 'POSTGRES_HOST=.*', "POSTGRES_HOST=$dbHost" | Set-Content .env
(Get-Content .env) -replace 'POSTGRES_PORT=.*', "POSTGRES_PORT=$dbPort" | Set-Content .env

# Set DATABASE_URI in the environment
$databaseUri = "postgresql://${dbUser}:${dbPass}@${dbHost}:${dbPort}/${dbName}"
[Environment]::SetEnvironmentVariable("DATABASE_URI", $databaseUri, "Process")

Write-Host "Environment setup complete!" -ForegroundColor Green
Write-Host "Database URI: $databaseUri" -ForegroundColor Cyan
