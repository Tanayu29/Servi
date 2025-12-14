# ==============================
# Servi build script
# ==============================

$ErrorActionPreference = "Stop"

$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PROJECT_ROOT

Write-Host "=== Servi Build Start ==="

# Python 実行パス（必要なら変更）
$PYTHON = "python"

# 出力整理
if (Test-Path "dist") {
    Write-Host "Cleaning dist/"
    Remove-Item dist -Recurse -Force
}

if (Test-Path "build") {
    Remove-Item build -Recurse -Force
}

# ------------------------------
# servi.exe
# ------------------------------
Write-Host "Building servi.exe"

& $PYTHON -m PyInstaller `
    servi_main.py `
    --onefile `
    --name servi `
    --clean `
    --paths . `
    --hidden-import=yaml

if ($LASTEXITCODE -ne 0) {
    throw "servi.exe build failed"
}

# ------------------------------
# approve.exe
# ------------------------------
Write-Host "Building approve.exe"

& $PYTHON -m PyInstaller `
    cli/approve.py `
    --onefile `
    --name approve `
    --clean `
    --paths . `
    --hidden-import=yaml

if ($LASTEXITCODE -ne 0) {
    throw "approve.exe build failed"
}

Write-Host "=== Build Completed ==="
