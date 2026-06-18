# install-ghidra.ps1 - Install Ghidra and launch it on Windows 10/11.
# Linux: use install-ghidra.sh (see GHIDRA.md)
# Installer version: 1.1.1
<#
.SYNOPSIS
  Download, install, and launch Ghidra on Windows.

.DESCRIPTION
  Installs JDK 21 via winget when needed, downloads the official Ghidra PUBLIC
  release from GitHub, verifies SHA-256, extracts under %LOCALAPPDATA%\Ghidra,
  creates Start Menu and PATH launchers, and runs ghidraRun.bat.

.PARAMETER InstallOnly
  Install without launching Ghidra.

.PARAMETER RunOnly
  Launch an existing install without downloading or installing.

.PARAMETER Version
  Pin a Ghidra release, e.g. 12.1.2

.PARAMETER Force
  Re-download and reinstall even if Ghidra is already present.

.PARAMETER DesktopShortcut
  Also create a Desktop shortcut.

.EXAMPLE
  .\install-ghidra.ps1

.EXAMPLE
  .\install-ghidra.ps1 -InstallOnly -DesktopShortcut
#>

#Requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$InstallOnly,
    [switch]$RunOnly,
    [string]$Version,
    [string]$InstallDir,
    [string]$CacheDir,
    [switch]$Force,
    [switch]$SkipSha256,
    [switch]$DesktopShortcut,
    [switch]$Help
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Script:GitHubApi = 'https://api.github.com/repos/NationalSecurityAgency/ghidra'
$Script:UserAgent = 'ghidra-install-script/1.0 (Windows PowerShell)'

function Write-Ok($Message)   { Write-Host "  [OK]   $Message" -ForegroundColor Green }
function Write-Warn($Message) { Write-Host "  [WARN] $Message" -ForegroundColor Yellow }
function Write-Fail($Message) { Write-Host "  [FAIL] $Message" -ForegroundColor Red; exit 1 }
function Write-Info($Message) { Write-Host "  [INFO] $Message" -ForegroundColor Cyan }
function Write-Banner($Message) { Write-Host "`n[[ $Message ]]" -ForegroundColor Cyan -BackgroundColor Black }

if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Detailed
    exit 0
}

if ($RunOnly -and $Force) {
    Write-Fail '-RunOnly and -Force cannot be used together'
}

if (-not $InstallDir) {
    $InstallDir = Join-Path $env:LOCALAPPDATA 'Ghidra'
}
if (-not $CacheDir) {
    $CacheDir = Join-Path $env:LOCALAPPDATA 'Ghidra\cache'
}

Write-Host ''
Write-Host '===============================================================' -ForegroundColor Cyan
Write-Host '     Ghidra installer v1.1.1 // Windows 10/11                  ' -ForegroundColor Cyan
Write-Host '===============================================================' -ForegroundColor Cyan

function Get-JavaVersionLine {
    param([string]$JavaExe = 'java')

    if (-not (Get-Command $JavaExe -ErrorAction SilentlyContinue)) {
        return $null
    }

    $javaPath = (Get-Command $JavaExe).Source

    # java -version writes to stderr; with $ErrorActionPreference = Stop that becomes
    # a terminating NativeCommandError in Windows PowerShell 5.1. Use cmd to capture both streams.
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $lines = @(cmd /c "`"$javaPath`" -version 2>&1")
    } finally {
        $ErrorActionPreference = $previous
    }

    if (-not $lines -or $lines.Count -eq 0) {
        return $null
    }

    return [string]$lines[0]
}

function Test-Java21Plus {
    param([string]$JavaExe = 'java')

    if (-not (Get-Command $JavaExe -ErrorAction SilentlyContinue)) {
        return $null
    }

    $versionLine = Get-JavaVersionLine -JavaExe $JavaExe
    if (-not $versionLine) {
        return $null
    }

    if ($versionLine -match 'version "(\d+)') {
        $major = [int]$Matches[1]
        if ($major -ge 21) {
            return $major
        }
    }
    return $null
}

function Find-JavaHome {
    $javaCmd = Get-Command java -ErrorAction SilentlyContinue
    if ($javaCmd) {
        $javaBin = Split-Path -Parent $javaCmd.Source
        return (Split-Path -Parent $javaBin)
    }

    $searchRoots = @(
        "${env:ProgramFiles}\Microsoft",
        "${env:ProgramFiles}\Eclipse Adoptium",
        "${env:ProgramFiles}\Java",
        "${env:ProgramFiles(x86)}\Java"
    )

    foreach ($root in $searchRoots) {
        if (-not (Test-Path $root)) { continue }
        $candidate = Get-ChildItem -Path $root -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match 'jdk-?21|jdk.*21|temurin-21' } |
            Sort-Object FullName -Descending |
            Select-Object -First 1
        if ($candidate -and (Test-Path (Join-Path $candidate.FullName 'bin\java.exe'))) {
            return $candidate.FullName
        }
    }

    return $null
}

function Install-Jdk21 {
    Write-Banner '1. JDK 21'

    $existing = Test-Java21Plus
    if ($existing) {
        $versionLine = Get-JavaVersionLine
        Write-Ok "Java $existing already available ($versionLine)"
        return
    }

    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Write-Fail @(
            'JDK 21 is required but was not found, and winget is unavailable.'
            'Install JDK 21 manually from https://adoptium.net/temurin/releases/ (version 21, Windows x64),'
            'then re-run this script.'
        ) -join ' '
    }

    Write-Info 'Installing JDK 21 via winget (Temurin)...'
    $wingetArgs = @(
        'install', '--id', 'EclipseAdoptium.Temurin.21.JDK',
        '-e', '--accept-source-agreements', '--accept-package-agreements'
    )

    $proc = Start-Process -FilePath 'winget' -ArgumentList $wingetArgs -Wait -PassThru -NoNewWindow
    if ($proc.ExitCode -ne 0) {
        Write-Warn 'Temurin install via winget failed; trying Microsoft OpenJDK 21...'
        $wingetArgs = @(
            'install', '--id', 'Microsoft.OpenJDK.21',
            '-e', '--accept-source-agreements', '--accept-package-agreements'
        )
        $proc = Start-Process -FilePath 'winget' -ArgumentList $wingetArgs -Wait -PassThru -NoNewWindow
        if ($proc.ExitCode -ne 0) {
            Write-Fail 'Could not install JDK 21 automatically. Install JDK 21 manually and re-run.'
        }
    }

    $env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
                [System.Environment]::GetEnvironmentVariable('Path', 'User')

    if (-not (Test-Java21Plus)) {
        Write-Fail 'JDK 21 install finished but java is still not on PATH. Open a new terminal and re-run, or set JAVA_HOME manually.'
    }

    Write-Ok 'JDK 21 installed'
}

function Get-ReleaseMetadata {
    if ($Version) {
        $Version = $Version -replace '^Ghidra_', '' -replace '_build$', '' -replace '^ghidra_', ''
        $apiUrl = "$Script:GitHubApi/releases/tags/Ghidra_${Version}_build"
    } else {
        $apiUrl = "$Script:GitHubApi/releases/latest"
    }

    Write-Info "Querying GitHub release metadata: $apiUrl"
    $headers = @{ 'User-Agent' = $Script:UserAgent }
    $release = Invoke-RestMethod -Uri $apiUrl -Headers $headers

    $sha256 = ''
    if ($release.body -match 'SHA-256:\s*`([0-9a-f]+)`') {
        $sha256 = $Matches[1].ToLowerInvariant()
    }

    $asset = $release.assets | Where-Object {
        $_.name -like 'ghidra_*_PUBLIC_*.zip'
    } | Select-Object -First 1

    if (-not $asset) {
        Write-Fail 'No PUBLIC release zip found in GitHub assets'
    }

    return [pscustomobject]@{
        Tag          = $release.tag_name
        ZipName      = $asset.name
        DownloadUrl  = $asset.browser_download_url
        Sha256       = $sha256
    }
}

function Find-InstallDirectory {
    $currentLink = Join-Path $InstallDir 'current'
    if (Test-Path $currentLink) {
        $resolved = (Get-Item $currentLink).Target
        if (-not $resolved) {
            $resolved = (Get-Content (Join-Path $InstallDir 'current.txt') -ErrorAction SilentlyContinue)
        }
        if ($resolved -and (Test-Path (Join-Path $resolved 'ghidraRun.bat'))) {
            return $resolved
        }
    }

    $candidate = Get-ChildItem -Path $InstallDir -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like 'ghidra_*' -and (Test-Path (Join-Path $_.FullName 'ghidraRun.bat')) } |
        Sort-Object Name -Descending |
        Select-Object -First 1

    if ($candidate) {
        return $candidate.FullName
    }

    return $null
}

function Set-CurrentInstall {
    param([string]$TargetDir)

    $currentLink = Join-Path $InstallDir 'current'
    if (Test-Path $currentLink) {
        Remove-Item $currentLink -Force -Recurse -ErrorAction SilentlyContinue
    }

    try {
        cmd /c mklink /J "$currentLink" "$TargetDir" | Out-Null
    } catch {
        Set-Content -Path (Join-Path $InstallDir 'current.txt') -Value $TargetDir -Encoding ASCII
    }
}

function New-GhidraShortcut {
    param(
        [string]$InstallPath,
        [string]$ShortcutPath
    )

    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($ShortcutPath)
    $shortcut.TargetPath = Join-Path $InstallPath 'ghidraRun.bat'
    $shortcut.WorkingDirectory = $InstallPath
    $icon = Join-Path $InstallPath 'Ghidra\images\GhidraIcon128.png'
    if (Test-Path $icon) {
        $shortcut.IconLocation = "$icon,0"
    }
    $shortcut.Description = 'Ghidra software reverse engineering framework'
    $shortcut.Save()
}

function Install-GhidraRelease {
    param(
        [Parameter(Mandatory)][pscustomobject]$Release
    )

    Write-Banner "2. Download Ghidra $($Release.Tag)"

    New-Item -ItemType Directory -Force -Path $InstallDir, $CacheDir | Out-Null

    $zipPath = Join-Path $CacheDir $Release.ZipName
    if ((Test-Path $zipPath) -and -not $Force) {
        Write-Ok "Using cached archive: $zipPath"
    } else {
        Write-Info "Downloading $($Release.ZipName) (~550 MB) - this can take a few minutes..."
        Invoke-WebRequest -Uri $Release.DownloadUrl -OutFile "$zipPath.part" -UserAgent $Script:UserAgent
        Move-Item -Force "$zipPath.part" $zipPath
        Write-Ok "Download complete: $zipPath"
    }

    if (-not $SkipSha256 -and $Release.Sha256) {
        Write-Info 'Verifying SHA-256 checksum'
        $actual = (Get-FileHash -Path $zipPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $Release.Sha256) {
            Write-Fail "Checksum mismatch for $($Release.ZipName)`n         expected: $($Release.Sha256)`n         got:      $actual"
        }
        Write-Ok 'SHA-256 verified'
    } elseif (-not $Release.Sha256) {
        Write-Warn 'Release notes did not include SHA-256; skipping checksum verification'
    }

    Write-Banner '3. Install Ghidra'

    if ($Force) {
        Get-ChildItem -Path $InstallDir -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -like 'ghidra_*' } |
            ForEach-Object { Remove-Item $_.FullName -Recurse -Force }
        Remove-Item (Join-Path $InstallDir 'current') -Force -Recurse -ErrorAction SilentlyContinue
        Remove-Item (Join-Path $InstallDir 'current.txt') -Force -ErrorAction SilentlyContinue
    }

    $installPath = Find-InstallDirectory
    if ($installPath -and -not $Force) {
        Write-Ok "Ghidra already installed at $installPath"
    } else {
        Write-Info "Extracting to $InstallDir ..."
        if (Get-Command tar -ErrorAction SilentlyContinue) {
            & tar -xf $zipPath -C $InstallDir
        } else {
            Expand-Archive -Path $zipPath -DestinationPath $InstallDir -Force
        }
        $installPath = Find-InstallDirectory
        if (-not $installPath) {
            Write-Fail "Extraction succeeded but ghidraRun.bat was not found under $InstallDir"
        }
        Write-Ok "Extracted to $installPath"
    }

    if ($installPath -match '!') {
        Write-Fail 'Ghidra cannot run from a path containing "!" - choose a different -InstallDir'
    }

    Set-CurrentInstall -TargetDir $installPath

    $launcherDir = Join-Path $env:LOCALAPPDATA 'Ghidra\bin'
    New-Item -ItemType Directory -Force -Path $launcherDir | Out-Null
    $launcherPath = Join-Path $launcherDir 'ghidra.cmd'
    @"
@echo off
setlocal
cd /d "$installPath"
call ghidraRun.bat %*
"@ | Set-Content -Path $launcherPath -Encoding ASCII

    $startMenuDir = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'
    New-GhidraShortcut -InstallPath $installPath -ShortcutPath (Join-Path $startMenuDir 'Ghidra.lnk')

    if ($DesktopShortcut) {
        $desktop = [Environment]::GetFolderPath('Desktop')
        New-GhidraShortcut -InstallPath $installPath -ShortcutPath (Join-Path $desktop 'Ghidra.lnk')
    }

    $ghidraRunBat = Join-Path $installPath 'ghidraRun.bat'
    Write-Ok 'Launchers installed:'
    Write-Info "  Start Menu: $startMenuDir\Ghidra.lnk"
    Write-Info "  CLI helper: $launcherPath"
    Write-Info "  Install:    $installPath"
    Write-Info "  Direct run: $ghidraRunBat"

    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($userPath -notlike "*$launcherDir*") {
        Write-Warn 'Adding Ghidra launcher directory to your user PATH'
        [Environment]::SetEnvironmentVariable('Path', "$userPath;$launcherDir", 'User')
        $env:Path = "$env:Path;$launcherDir"
        Write-Warn 'Open a new terminal (or log out/in) if ghidra is not found immediately'
    }

    return $installPath
}

function Start-Ghidra {
    param(
        [Parameter(Mandatory)][string]$InstallPath,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$GhidraArgs
    )

    Write-Banner '4. Launch Ghidra'

    if ($Script:JavaHome) {
        $env:JAVA_HOME = $Script:JavaHome
        $env:Path = "$($Script:JavaHome)\bin;$env:Path"
    }

    $runBat = Join-Path $InstallPath 'ghidraRun.bat'
    if (-not (Test-Path $runBat)) {
        Write-Fail "ghidraRun.bat not found at $runBat"
    }

    Write-Ok "Starting Ghidra from $InstallPath"
    if ($GhidraArgs -and $GhidraArgs.Count -gt 0) {
        Start-Process -FilePath $runBat -WorkingDirectory $InstallPath -ArgumentList $GhidraArgs
    } else {
        Start-Process -FilePath $runBat -WorkingDirectory $InstallPath
    }
}

# ====================================================================
# STAGE 0 - Pre-flight
# ====================================================================
Write-Banner '0. Pre-flight'

if ($env:OS -ne 'Windows_NT') {
    Write-Fail 'This script is for Windows only'
}

$os = Get-CimInstance Win32_OperatingSystem
Write-Ok "Windows $($os.Caption) ($($os.OSArchitecture))"

if ($os.OSArchitecture -notmatch '64') {
    Write-Fail 'Ghidra public Windows builds require 64-bit Windows'
}

# ====================================================================
# Main flow
# ====================================================================
if (-not $RunOnly) {
    Install-Jdk21
}

$Script:JavaHome = Find-JavaHome
if ($Script:JavaHome) {
    $env:JAVA_HOME = $Script:JavaHome
    $env:Path = "$($Script:JavaHome)\bin;$env:Path"
    Write-Ok "JAVA_HOME=$($Script:JavaHome)"
} elseif (-not $RunOnly) {
    Write-Fail 'Could not locate JAVA_HOME after JDK setup'
}

if ($RunOnly) {
    $installPath = Find-InstallDirectory
    if (-not $installPath) {
        Write-Fail 'Ghidra is not installed. Run without -RunOnly first.'
    }
    Start-Ghidra -InstallPath $installPath
    exit 0
}

$release = Get-ReleaseMetadata
$installPath = Install-GhidraRelease -Release $release

if ($InstallOnly) {
    $ghidraRunBat = Join-Path $installPath 'ghidraRun.bat'
    Write-Host ''
    Write-Host '===============================================================' -ForegroundColor Green
    Write-Host '                     INSTALL COMPLETE                          ' -ForegroundColor Green
    Write-Host '===============================================================' -ForegroundColor Green
    Write-Host ''
    Write-Host '  Launch Ghidra:'
    Write-Host '    Start Menu -> Ghidra'
    Write-Host '    ghidra'
    Write-Host "    $ghidraRunBat"
    Write-Host ''
    exit 0
}

Start-Ghidra -InstallPath $installPath
