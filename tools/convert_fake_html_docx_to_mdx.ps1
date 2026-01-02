# Converts files ending in .html that are actually DOCX (zip with word/document.xml)
# Forces pandoc input format: -f docx (critical because extension is .html)
# Outputs MDX into src\content\docs_migrated\ mirroring folder structure
# Run:
# powershell -ExecutionPolicy Bypass -File .\tools\convert_fake_html_docx_to_mdx.ps1

$ErrorActionPreference = "Stop"

$RepoRoot = (Get-Location).Path
$Pandoc   = "C:\Program Files\Pandoc\pandoc.exe"
$OutRoot  = Join-Path $RepoRoot "src\content\docs_migrated"

if (!(Test-Path $Pandoc)) {
  Write-Host "ERROR: Pandoc not found at $Pandoc" -ForegroundColor Red
  Write-Host "Update `$Pandoc in this script or reinstall Pandoc." -ForegroundColor Red
  exit 1
}

function Slugify([string]$s) {
  $t = $s.ToLowerInvariant()
  $t = $t -replace "[’']", ""
  $t = $t -replace "[^a-z0-9]+", "-"
  $t = $t.Trim("-")
  if ([string]::IsNullOrWhiteSpace($t)) { $t = "untitled" }
  return $t
}

function IsDocxZipWithWordXml([string]$path) {
  try {
    # DOCX is a ZIP; starts with "PK"
    $fs = [System.IO.File]::OpenRead($path)
    try {
      $b1 = $fs.ReadByte()
      $b2 = $fs.ReadByte()
      if ($b1 -ne 0x50 -or $b2 -ne 0x4B) { return $false }
    } finally {
      $fs.Close()
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem | Out-Null
    $zip = [System.IO.Compression.ZipFile]::OpenRead($path)
    try {
      foreach ($e in $zip.Entries) {
        if ($e.FullName -ieq "word/document.xml") { return $true }
      }
      return $false
    } finally {
      $zip.Dispose()
    }
  } catch {
    return $false
  }
}

New-Item -ItemType Directory -Force -Path $OutRoot | Out-Null

Write-Host "Repo root: $RepoRoot"
Write-Host "Output:    $OutRoot"
Write-Host ""

$allHtml = Get-ChildItem -Path $RepoRoot -Recurse -File -Filter *.html |
  Where-Object { $_.FullName -notmatch "\\node_modules\\|\\dist\\|\\\.git\\|\\src\\content\\docs_migrated\\" }

$targets = @()
foreach ($f in $allHtml) {
  if (IsDocxZipWithWordXml $f.FullName) { $targets += $f }
}

if ($targets.Count -eq 0) {
  Write-Host "No '.html' files detected as DOCX containers. Nothing to convert." -ForegroundColor Yellow
  exit 0
}

Write-Host "Detected $($targets.Count) '.html' files that are actually DOCX." -ForegroundColor Green
Write-Host ""

Write-Host "=== DRY RUN (conversion targets) ==="
foreach ($f in $targets) { Write-Host $f.FullName }
Write-Host ""

$confirm = Read-Host "Type YES to convert these to MDX into src\content\docs_migrated"
if ($confirm -ne "YES") {
  Write-Host "Aborted. No files were changed."
  exit 0
}

$converted = 0
$failed = 0

foreach ($f in $targets) {
  $tmp = $null
  try {
    $relative = $f.FullName.Substring($RepoRoot.Length).TrimStart("\")
    $relativeDir = Split-Path $relative -Parent
    if ([string]::IsNullOrWhiteSpace($relativeDir)) { $relativeDir = "." }

    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)  # strips .html
    $slug = Slugify $baseName

    $destDir = Join-Path $OutRoot $relativeDir
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null

    $destPath = Join-Path $destDir ($slug + ".mdx")
    $routeFolder = ($relativeDir -replace "\\", "/").Trim(".")
    $route = if ($routeFolder -eq "" -or $routeFolder -eq ".") { "/" + $slug } else { "/" + $routeFolder.Trim("/") + "/" + $slug }

    Write-Host "CONVERT: $($f.FullName)"
    Write-Host "   ->   $destPath"

    $tmp = New-TemporaryFile

    # Force input format to DOCX because the file extension is .html
    & $Pandoc -f docx "$($f.FullName)" -t markdown --wrap=none -o "$($tmp.FullName)" 2>$null

    if ($LASTEXITCODE -ne 0) {
      throw "Pandoc failed (exit code $LASTEXITCODE)."
    }

    $md = Get-Content -Raw -Path $tmp.FullName

    $frontmatter = @"
---
title: "$baseName"
route: "$route"
source: "$relative"
---
"@

    Set-Content -Path $destPath -Value ($frontmatter + "`n" + $md.Trim() + "`n") -Encoding UTF8

    $converted++
    Write-Host ""
  }
  catch {
    Write-Host "FAILED: $($f.FullName)" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    $failed++
  }
  finally {
    if ($tmp -and (Test-Path $tmp.FullName)) {
      Remove-Item $tmp.FullName -ErrorAction SilentlyContinue
    }
  }
}

Write-Host "Done."
Write-Host "Converted: $converted"
Write-Host "Failed:    $failed"
