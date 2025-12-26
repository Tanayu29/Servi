Write-Host 'Exporting project to single file...'

$ProjectRoot = $PSScriptRoot
Write-Host "Project root: $ProjectRoot"

$OutputFile = Join-Path $ProjectRoot 'servi_project_dump.md'

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$writer = New-Object System.IO.StreamWriter($OutputFile, $false, $utf8NoBom)

try {
    $writer.WriteLine('Servi Project Dump')
    $writer.WriteLine('Generated at: ' + (Get-Date))
    $writer.WriteLine('')
    $writer.WriteLine('==== Directory Structure ====')

    Push-Location $ProjectRoot
    $tree = tree /F | Out-String
    Pop-Location

    $writer.WriteLine($tree)
    $writer.WriteLine('')
    $writer.WriteLine('==== Source Files ====')

    $extensions = @('*.py', '*.ps1', '*.yaml', '*.yml', '*.md', '*.spec')

    # --- 対象ファイルを事前収集 ---
    $files = @()
    foreach ($ext in $extensions) {
        $files += Get-ChildItem `
            -Path $ProjectRoot `
            -Recurse `
            -File `
            -Filter $ext |
            Where-Object {
                $_.FullName -notmatch '\\dist\\|\\build\\|\\__pycache__\\'
            }
    }

    $total = $files.Count
    $index = 0

    foreach ($file in $files) {
        $index++

        $percent = [int](($index / $total) * 100)
        $shortPath = $file.FullName.Substring(
            [Math]::Max(0, $file.FullName.Length - 60)
        )

        Write-Progress `
            -Activity 'Exporting project files' `
            -Status "[$index / $total] $shortPath" `
            -PercentComplete $percent

        $writer.WriteLine('')
        $writer.WriteLine('---- FILE START ----')
        $writer.WriteLine('PATH: ' + $file.FullName)
        $writer.WriteLine('TYPE: ' + $file.Extension)
        $writer.WriteLine('---- CONTENT ----')

        foreach ($line in Get-Content $file.FullName -Encoding UTF8) {
            $writer.WriteLine($line)
        }

        $writer.WriteLine('---- FILE END ----')
    }

    Write-Progress -Activity 'Exporting project files' -Completed
}
finally {
    $writer.Close()
}

Write-Host 'Export completed successfully.'
