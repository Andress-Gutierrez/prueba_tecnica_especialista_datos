# =============================================================================
# Script   : validate_dw.ps1
# Proyecto : prueba_tecnica_especialista_datos
# Fase     : 3.4 — Validación del Data Warehouse
# Descripción:
#   Consulta metadatos en PostgreSQL (solo SELECT). No modifica la BD.
# Uso:
#   Desde la raíz del proyecto:
#     .\scripts\validate_dw.ps1
# =============================================================================

$ErrorActionPreference = "Stop"

$Container = "prueba_tecnica_postgres"
$DbUser = "dwh_user"
$DbName = "dwh_comercial"

$failed = 0

function Invoke-SqlScalar {
    param([string]$Sql)
    $raw = $Sql | docker exec -i $Container psql -U $DbUser -d $DbName -t -A 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "psql falló: $raw"
    }
    return ($raw | Out-String).Trim()
}

function Write-Check {
    param([string]$Name, [bool]$Ok, [string]$Detail = "")
    if ($Ok) {
        Write-Host ("[OK]    {0}{1}" -f $Name, $(if ($Detail) { " — $Detail" } else { "" })) -ForegroundColor Green
    }
    else {
        Write-Host ("[ERROR] {0}{1}" -f $Name, $(if ($Detail) { " — $Detail" } else { "" })) -ForegroundColor Red
        $script:failed++
    }
}

Write-Host "========================================"
Write-Host "Validación DW — dwh_comercial / schema dwh"
Write-Host "========================================"
Write-Host ""

try {
    $null = docker exec $Container pg_isready -U $DbUser -d $DbName 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Contenedor PostgreSQL no disponible." -ForegroundColor Red
        Write-Host ""
        Write-Host "VALIDACIÓN FALLIDA"
        exit 1
    }
}
catch {
    Write-Host "[ERROR] No se pudo contactar Docker/PostgreSQL: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "VALIDACIÓN FALLIDA"
    exit 1
}

# --- Esquema ---
$schemaCount = Invoke-SqlScalar "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = 'dwh';"
Write-Check "Esquema dwh" ($schemaCount -eq "1") "count=$schemaCount"

# --- Dimensiones ---
$dims = @(
    "dim_tiempo", "dim_region", "dim_canal", "dim_categoria",
    "dim_jerarquia_comercial", "dim_aliado", "dim_unidad_gestion",
    "dim_marca", "dim_vendedor", "dim_validez_venta",
    "dim_campana", "dim_segmento", "dim_tipo_contacto"
)
$dimList = ($dims | ForEach-Object { "'$_'" }) -join ","
$dimCount = Invoke-SqlScalar @"
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'dwh' AND table_type = 'BASE TABLE'
  AND table_name IN ($dimList);
"@
Write-Check "13 dimensiones" ($dimCount -eq "13") "encontradas=$dimCount"

foreach ($d in $dims) {
    $c = Invoke-SqlScalar "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='dwh' AND table_name='$d';"
    Write-Check "  tabla dwh.$d" ($c -eq "1")
}

# --- Hechos ---
$facts = @("fact_ventas", "fact_presupuesto", "fact_gestion_tmk")
$factList = ($facts | ForEach-Object { "'$_'" }) -join ","
$factCount = Invoke-SqlScalar @"
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'dwh' AND table_type = 'BASE TABLE'
  AND table_name IN ($factList);
"@
Write-Check "3 hechos" ($factCount -eq "3") "encontrados=$factCount"

foreach ($f in $facts) {
    $c = Invoke-SqlScalar "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='dwh' AND table_name='$f';"
    Write-Check "  tabla dwh.$f" ($c -eq "1")
}

# --- Índices (§6) ---
$indexes = @(
    "ix_fact_ventas_tiempo",
    "ix_fact_ventas_validez",
    "ix_fact_ventas_region_aliado",
    "ix_fact_ventas_jerarquia",
    "ix_fact_presupuesto_tiempo",
    "ix_fact_presupuesto_cruce",
    "ix_fact_gestion_tiempo",
    "ix_fact_gestion_campana_aliado",
    "ix_fact_gestion_tipo",
    "ix_dim_tiempo_periodo"
)
$ixList = ($indexes | ForEach-Object { "'$_'" }) -join ","
$ixCount = Invoke-SqlScalar @"
SELECT COUNT(*) FROM pg_indexes
WHERE schemaname = 'dwh' AND indexname IN ($ixList);
"@
Write-Check "10 índices (§6)" ($ixCount -eq "10") "encontrados=$ixCount"

# --- Primary Keys (13 dims + 3 facts = 16) ---
$pkCount = Invoke-SqlScalar @"
SELECT COUNT(*) FROM information_schema.table_constraints
WHERE table_schema = 'dwh' AND constraint_type = 'PRIMARY KEY';
"@
Write-Check "Primary Keys" ($pkCount -eq "16") "encontradas=$pkCount (esperado 16)"

# --- Foreign Keys (9 + 7 + 7 = 23) ---
$fkCount = Invoke-SqlScalar @"
SELECT COUNT(*) FROM information_schema.table_constraints
WHERE table_schema = 'dwh' AND constraint_type = 'FOREIGN KEY';
"@
Write-Check "Foreign Keys" ($fkCount -eq "23") "encontradas=$fkCount (esperado 23)"

# --- Seeds ---
$sk0Dims = @(
    "dim_tiempo", "dim_region", "dim_canal", "dim_categoria",
    "dim_jerarquia_comercial", "dim_aliado", "dim_unidad_gestion",
    "dim_marca", "dim_vendedor", "dim_campana", "dim_segmento", "dim_tipo_contacto"
)
$sk0Ok = $true
$sk0Detail = @()
foreach ($t in $sk0Dims) {
    $pkCol = switch ($t) {
        "dim_tiempo" { "sk_tiempo" }
        "dim_region" { "sk_region" }
        "dim_canal" { "sk_canal" }
        "dim_categoria" { "sk_categoria" }
        "dim_jerarquia_comercial" { "sk_jerarquia" }
        "dim_aliado" { "sk_aliado" }
        "dim_unidad_gestion" { "sk_unidad_gestion" }
        "dim_marca" { "sk_marca" }
        "dim_vendedor" { "sk_vendedor" }
        "dim_campana" { "sk_campana" }
        "dim_segmento" { "sk_segmento" }
        "dim_tipo_contacto" { "sk_tipo_contacto" }
    }
    $n = Invoke-SqlScalar "SELECT COUNT(*) FROM dwh.$t WHERE $pkCol = 0;"
    if ($n -ne "1") {
        $sk0Ok = $false
        $sk0Detail += "$t=$n"
    }
}
Write-Check "Seeds sk=0 (12 dims)" $sk0Ok $(if ($sk0Detail.Count) { ($sk0Detail -join "; ") } else { "1 fila sk=0 por dim" })

$validezCount = Invoke-SqlScalar "SELECT COUNT(*) FROM dwh.dim_validez_venta;"
Write-Check "Seed dim_validez_venta (4 filas)" ($validezCount -eq "4") "filas=$validezCount"

Write-Host ""
if ($failed -eq 0) {
    Write-Host "VALIDACIÓN COMPLETADA" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "VALIDACIÓN FALLIDA ($failed chequeo(s) con error)" -ForegroundColor Red
    exit 1
}
