# Create directory if it doesn't exist
$sslDir = "nginx/ssl"
if (-not (Test-Path -Path $sslDir)) {
    New-Item -ItemType Directory -Path $sslDir | Out-Null
}

# Generate a self-signed certificate with proper extensions
$cert = New-SelfSignedCertificate `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -DnsName "branchloans.com", "www.branchloans.com" `
    -FriendlyName "Branch Loans Development Certificate" `
    -KeySpec Signature `
    -KeyExportPolicy Exportable `
    -KeyUsage DigitalSignature, KeyEncipherment `
    -KeyUsageProperty All `
    -Provider "Microsoft Enhanced RSA and AES Cryptographic Provider" `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.1") `
    -NotAfter (Get-Date).AddYears(1)

# Export the certificate to a .crt file (DER format)
$cert | Export-Certificate -FilePath "$sslDir/branchloans.crt" -Type CERT -Force

# Export the private key to a .key file (PEM format)
$privateKeyBytes = $cert.PrivateKey.ExportPkcs8PrivateKey()
$privateKeyPem = [System.Convert]::ToBase64String($privateKeyBytes, 'InsertLineBreaks')
$privateKeyPem = "-----BEGIN PRIVATE KEY-----`n$privateKeyPem`n-----END PRIVATE KEY-----"
$privateKeyPem | Out-File -FilePath "$sslDir/branchloans.key" -Encoding ascii

# Export the certificate to a .pem file (PEM format)
$certPem = @"
-----BEGIN CERTIFICATE-----
$([System.Convert]::ToBase64String($cert.RawData, 'InsertLineBreaks'))
-----END CERTIFICATE-----
"@
$certPem | Out-File -FilePath "$sslDir/branchloans.pem" -Encoding ascii

# Add the private key to the .pem file
$privateKeyPem | Out-File -FilePath "$sslDir/branchloans.pem" -Append -Encoding ascii

# Create a .pfx file for Windows
$password = ConvertTo-SecureString -String "password" -Force -AsPlainText
$cert | Export-PfxCertificate -FilePath "$sslDir/branchloans.pfx" -Password $password | Out-Null

Write-Host "SSL certificate and key generated in $sslDir/ directory" -ForegroundColor Green
Write-Host "Files created:" -ForegroundColor Cyan
Get-ChildItem -Path $sslDir | Select-Object Name, Length, LastWriteTime
