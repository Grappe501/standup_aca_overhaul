# Convert all .docx files to MDX for Astro
# Run from repo root:
# powershell -ExecutionPolicy Bypass -File .\tools\convert_docx_to_mdx.ps1

$ErrorActionPreference = "Stop"

$RepoRoot = Get-Location
$OutRoot = Join-Path $RepoRoot "src\content\docs"

function Slugify([string]$s) {
  $t = $s.ToLowerInvariant()
  $t = $t -replace "\.docx$", ""
  $t = $t -replace "[’']", ""
  $t = $t -replace "[^a-z0-9]+", "-"
  $t = $t.Trim("-")
  if ([string]::IsNullOrWhiteSpace($t)) { $t = "untitled" }
  return $t
}

# Ensure output folder exists
if (!(Test-Path $OutRoot)) {
  New-Item -ItemType Directory -Force -Path $OutRoot | Out-Null
}

# Find docx files (exclude node/dist/.git)
$docxFiles = Get-ChildItem -Recurse -File -Filter *.docx |
  Where-Object { $_.FullName -notmatch "\\node_modules\\|\\dist\\|\\\.git\\" }

if ($docxFiles.Count -eq 0) {
  Write-Host "No .docx files found."
  exit
}

foreach ($f in $docxFiles) {
  $base = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
  $slug = Slugify $base

  $dest = Join-Path $OutRoot ($slug + ".mdx")

  Write-Host "Converting: $($f.FullName)"
  Write-Host " -> $dest"

  $tmp = New-TemporaryFile

  & "C:\Program Files\Pandoc\pandoc.exe" "$($f.FullName)" -t markdown --wrap=none -o "$($tmp.FullName)"

  $md = Get-Content -Raw $tmp.FullName

  $frontmatter = @"
---
title: "$base"
route: "/$slug"
source: "$($f.Name)"
---
"@

  Set-Content -Path $dest -Value ($frontmatter + "`n" + $md.Trim()) -Encoding UTF8
  Remove-Item $tmp.FullName
}

Write-Host "Done converting Word docs to MDX."
