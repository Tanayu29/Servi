# ==============================
# Servi Release Script
# ==============================

$ErrorActionPreference = "Stop"

$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PROJECT_ROOT

Write-Host "=== Servi Release Start ==="

# ------------------------------
# Build exe
# ------------------------------
Write-Host "Running build.ps1"
.\build.ps1

# ------------------------------
# Copy config.yaml
# ------------------------------
$DIST_DIR = Join-Path $PROJECT_ROOT "dist"
$CONFIG_SRC = Join-Path $PROJECT_ROOT "config.yaml"
$CONFIG_DST = Join-Path $DIST_DIR "config.yaml"

if (-Not (Test-Path $CONFIG_SRC)) {
    throw "config.yaml not found in project root"
}

Write-Host "Copying config.yaml to dist/"
Copy-Item $CONFIG_SRC $CONFIG_DST -Force

# ------------------------------
# Copy data directory (optional but recommended)
# ------------------------------
$DATA_SRC = Join-Path $PROJECT_ROOT "data"
$DATA_DST = Join-Path $DIST_DIR "data"

if (Test-Path $DATA_SRC) {
    Write-Host "Copying data/ to dist/"
    if (Test-Path $DATA_DST) {
        Remove-Item $DATA_DST -Recurse -Force
    }
    Copy-Item $DATA_SRC $DATA_DST -Recurse -Force
}

# ------------------------------
# Export folder structure
# ------------------------------
Write-Host "Exporting folder structure"
.\export_tree.ps1

Write-Host "=== Release Completed ==="
