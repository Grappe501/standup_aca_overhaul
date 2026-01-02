# Recursively rename all .docx files to .html
# Run from the project root

$root = Get-Location

Write-Host "Scanning for .docx files under $root"
Write-Host ""

$files = Get-ChildItem -Path $root -Recurse -File -Filter *.docx

if ($files.Count -eq 0) {
    Write-Host "No .docx files found."
    exit
}

Write-Host "=== DRY RUN ==="
foreach ($file in $files) {
    $newPath = [System.IO.Path]::ChangeExtension($file.FullName, ".html")
    Write-Host "$($file.FullName)  ->  $newPath"
}

Write-Host ""
$confirm = Read-Host "Type YES to rename ALL of these files to .html"

if ($confirm -ne "YES") {
    Write-Host "Aborted. No files were changed."
    exit
}

Write-Host ""
Write-Host "Renaming files..."

foreach ($file in $files) {
    $newPath = [System.IO.Path]::ChangeExtension($file.FullName, ".html")

    if (Test-Path $newPath) {
        Write-Host "SKIP (exists): $newPath"
        continue
    }

    Rename-Item -Path $file.FullName -NewName $newPath
    Write-Host "RENAMED: $($file.FullName)"
}

Write-Host ""
Write-Host "Done."
