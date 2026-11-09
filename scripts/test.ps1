param([string]$Python = "python")
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
foreach ($service in @("vehicles", "tickets")) {
  Push-Location (Join-Path $root "services/$service")
  try {
    & $Python -m pytest tests -q
    if ($LASTEXITCODE -ne 0) { throw "Fallaron las pruebas de $service" }
  } finally { Pop-Location }
}
