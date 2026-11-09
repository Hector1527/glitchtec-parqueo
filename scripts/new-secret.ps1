$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$secure = Read-Host "Contraseña PostgreSQL (usar la misma al recrear pods con PVC existente)" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
  $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
  if ($plain.Length -lt 16) { throw "Usa al menos 16 caracteres" }
  $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($plain))
  $dir = Join-Path $root "k8s/rendered"
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  $yaml = @"
apiVersion: v1
kind: Secret
metadata:
  name: parking-secret
  namespace: glitchtec
type: Opaque
data:
  POSTGRES_PASSWORD: $encoded
"@
  [IO.File]::WriteAllText((Join-Path $dir "secret.yaml"), $yaml, [Text.UTF8Encoding]::new($false))
  Write-Host "Secret preparado en k8s/rendered/secret.yaml (ignorado por Git). Base64 no es cifrado."
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
  $plain = $null
  $encoded = $null
}
