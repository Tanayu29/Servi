# ==============================
# Folder structure exporter
# ==============================

$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PROJECT_ROOT

$OUTPUT = "structure.txt"

Write-Host "Exporting folder structure..."

# dist / build / __pycache__ を除外
tree $PROJECT_ROOT /F `
    | Select-String -NotMatch "\\dist\\|\\build\\|__pycache__" `
    | Out-File $OUTPUT -Encoding utf8

Write-Host "Saved to $OUTPUT"
