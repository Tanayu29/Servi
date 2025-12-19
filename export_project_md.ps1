Write-Host 'Exporting project to single file...'

$OutputFile = 'servi_project_dump.md'

$writer = New-Object System.IO.StreamWriter($OutputFile, $false, [System.Text.Encoding]::UTF8)

try {
    $writer.WriteLine('Servi Project Dump')
    $writer.WriteLine('Generated at: ' + (Get-Date))
    $writer.WriteLine('')
    $writer.WriteLine('==== Directory Structure ====')

    $tree = tree /F | Out-String
    $writer.WriteLine($tree)

    $writer.WriteLine('')
    $writer.WriteLine('==== Source Files ====')

    $extensions = @('*.py', '*.ps1', '*.yaml', '*.yml', '*.md', '*.spec')

    foreach ($ext in $extensions) {

        Get-ChildItem -Recurse -File -Filter $ext |
        Where-Object {
            $_.FullName -notmatch '\\dist\\|\\build\\|\\__pycache__\\'
        } |
        ForEach-Object {

            $writer.WriteLine('')
            $writer.WriteLine('---- FILE START ----')
            $writer.WriteLine('PATH: ' + $_.FullName)
            $writer.WriteLine('TYPE: ' + $ext)
            $writer.WriteLine('---- CONTENT ----')

            foreach ($line in Get-Content $_.FullName) {
                $writer.WriteLine($line)
            }

            $writer.WriteLine('---- FILE END ----')
        }
    }
}
finally {
    $writer.Close()
}

Write-Host 'Export completed successfully.'
