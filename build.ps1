[CmdletBinding()]
param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$buildRoot = Join-Path $projectRoot ".build"
$pyInstallerWork = Join-Path ([System.IO.Path]::GetTempPath()) ("yt-dlp-gui-pyinstaller-" + [guid]::NewGuid().ToString("N"))
$ffmpegRoot = Join-Path $buildRoot "ffmpeg"
$ytDlpRoot = Join-Path $buildRoot "yt-dlp"
$archive = Join-Path $buildRoot "ffmpeg-release-essentials.zip"
$extractRoot = Join-Path $buildRoot "ffmpeg-extract"
$ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$ytDlpUrl = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"

New-Item -ItemType Directory -Force -Path $buildRoot | Out-Null
& $Python -m pip install --upgrade -r (Join-Path $projectRoot "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }

if (-not (Test-Path (Join-Path $ffmpegRoot "ffmpeg.exe"))) {
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile $archive
    Expand-Archive -Path $archive -DestinationPath $extractRoot -Force
    $binDirectory = Get-ChildItem -Path $extractRoot -Filter "ffmpeg.exe" -Recurse |
        Select-Object -First 1 -ExpandProperty DirectoryName
    if (-not $binDirectory) { throw "The FFmpeg archive did not contain ffmpeg.exe." }

    New-Item -ItemType Directory -Force -Path $ffmpegRoot | Out-Null
    Copy-Item (Join-Path $binDirectory "ffmpeg.exe") $ffmpegRoot
    Copy-Item (Join-Path $binDirectory "ffprobe.exe") $ffmpegRoot
}

New-Item -ItemType Directory -Force -Path $ytDlpRoot | Out-Null
Invoke-WebRequest -Uri $ytDlpUrl -OutFile (Join-Path $ytDlpRoot "yt-dlp.exe")

Push-Location $projectRoot
try {
    & $Python -m PyInstaller `
        --noconfirm `
        --clean `
        --workpath $pyInstallerWork `
        --specpath $buildRoot `
        --onefile `
        --windowed `
        --name "yt-dlp-gui" `
        --add-binary "$ffmpegRoot\ffmpeg.exe;ffmpeg" `
        --add-binary "$ffmpegRoot\ffprobe.exe;ffmpeg" `
        --add-binary "$ytDlpRoot\yt-dlp.exe;yt-dlp" `
        app.py
    if ($LASTEXITCODE -ne 0) { throw "Executable packaging failed." }
}
finally {
    Pop-Location
}

Write-Host "Created: $projectRoot\dist\yt-dlp-gui.exe"
