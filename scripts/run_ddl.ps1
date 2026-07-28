# =============================================================================
# Script   : run_ddl.ps1
# Proyecto : prueba_tecnica_especialista_datos
# Fase     : 3.2 — Implementación DDL
# Descripción:
#   Ejecuta en orden alfabético todos los scripts *.sql de sql/ddl
#   contra PostgreSQL (contenedor prueba_tecnica_postgres / BD dwh_comercial).
# Uso:
#   Desde la raíz del proyecto:
#     .\scripts\run_ddl.ps1
# =============================================================================

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$DdlDir = Join-Path $ProjectRoot "sql\ddl"

if (-not (Test-Path -Path $DdlDir -PathType Container)) {
    Write-Error "ERROR: No existe la carpeta sql/ddl en la raíz del proyecto: $DdlDir"
    exit 1
}

$SqlFiles = Get-ChildItem -Path $DdlDir -Filter "*.sql" -File |
    Sort-Object -Property Name

if ($SqlFiles.Count -eq 0) {
    Write-Error "ERROR: No se encontraron archivos *.sql en sql/ddl."
    exit 1
}

$Container = "prueba_tecnica_postgres"
$DbUser = "dwh_user"
$DbName = "dwh_comercial"

foreach ($file in $SqlFiles) {
    Write-Host "----------------------------------------"
    Write-Host "Ejecutando: $($file.Name)"
    Write-Host "----------------------------------------"

    try {
        Get-Content -Path $file.FullName -Raw -Encoding UTF8 |
            docker exec -i $Container psql -U $DbUser -d $DbName -v ON_ERROR_STOP=1

        if ($LASTEXITCODE -ne 0) {
            Write-Host ""
            Write-Host "ERROR: Falló la ejecución de $($file.Name) (código $LASTEXITCODE)." -ForegroundColor Red
            exit $LASTEXITCODE
        }
    }
    catch {
        Write-Host ""
        Write-Host "ERROR: Falló la ejecución de $($file.Name)." -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host "DDL ejecutado correctamente"
Write-Host "Base de datos: dwh_comercial"
Write-Host "Schema: dwh"
Write-Host "========================================"

exit 0
