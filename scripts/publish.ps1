param([Parameter(Mandatory=$true)][string]$Registry, [string]$Tag = "v1")
$ErrorActionPreference = "Stop"
if ($Registry -notmatch '^[a-z0-9-]+-docker\.pkg\.dev/[a-z][a-z0-9-]+/[a-z0-9_-]+$') { throw "Ruta de Artifact Registry inválida" }
if ($Tag -notmatch '^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$') { throw "Tag inválido" }
$root = Split-Path $PSScriptRoot -Parent
foreach ($image in @("frontend", "vehicles", "tickets", "postgres")) {
  $context = switch ($image) { "vehicles" {"services/vehicles"} "tickets" {"services/tickets"} "postgres" {"database"} default {"frontend"} }
  & docker build --platform linux/amd64 -t "${Registry}/${image}:${Tag}" (Join-Path $root $context)
  if ($LASTEXITCODE -ne 0) { throw "Falló build de $image" }
  & docker push "${Registry}/${image}:${Tag}"
  if ($LASTEXITCODE -ne 0) { throw "Falló push de $image" }
}
