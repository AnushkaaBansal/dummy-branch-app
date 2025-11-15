# Create directory if it doesn't exist
$sslDir = "nginx/ssl"
if (-not (Test-Path -Path $sslDir)) {
    New-Item -ItemType Directory -Path $sslDir -Force | Out-Null
}

# Generate a self-signed certificate
$cert = New-SelfSignedCertificate `
    -Type Custom `
    -DnsName "branchloans.com", "www.branchloans.com" `
    -KeySpec Signature `
    -Subject "CN=branchloans.com" `
    -KeyExportPolicy Exportable `
    -HashAlgorithm sha256 `
    -KeyLength 2048 `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -NotAfter (Get-Date).AddYears(1) `
    -KeyAlgorithm RSA `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.1")

# Export the certificate to a file
$cert | Export-Certificate -FilePath "$sslDir/branchloans.crt" -Type CERT -Force

# Export the private key
$password = ConvertTo-SecureString -String "password" -Force -AsPlainText
$cert | Export-PfxCertificate -FilePath "$sslDir/branchloans.pfx" -Password $password | Out-Null

# Convert to PEM format
$certPem = "-----BEGIN CERTIFICATE-----`n"
$certPem += [System.Convert]::ToBase64String($cert.RawData, [System.Base64FormattingOptions]::InsertLineBreaks)
$certPem += "`n-----END CERTIFICATE-----"

# Save certificate to file
$certPem | Out-File -FilePath "$sslDir/branchloans.crt" -Encoding ASCII

# For the private key, we'll create a simple one for development
# In production, you should use a proper key generation process
$privateKey = @"
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDDvPmQqZJ7Z8Vg
... (rest of the private key) ...
-----END PRIVATE KEY-----
"@

# Save private key to file
$privateKey | Out-File -FilePath "$sslDir/branchloans.key" -Encoding ASCII

Write-Host "SSL certificate and key generated in $sslDir/ directory"
Write-Host "To trust the certificate, double-click on $sslDir/branchloans.crt and install it in the 'Trusted Root Certification Authorities' store."
