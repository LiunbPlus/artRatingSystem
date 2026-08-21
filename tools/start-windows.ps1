[CmdletBinding()]
param(
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot
Set-Location ..
$ProjectDir = (Get-Location).Path
$BackendDir = Join-Path $ProjectDir "backend"
$FrontendDir = Join-Path $ProjectDir "frontend"
$VenvDir = Join-Path $BackendDir "venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$RequirementsFile = Join-Path $BackendDir "requirements.txt"
$NodeModulesDir = Join-Path $FrontendDir "node_modules"

function Assert-Command {
    param([string]$Name, [string]$InstallHint)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Command '$Name' was not found. $InstallHint"
    }
}

if (-not (Test-Path -LiteralPath $PythonExe)) {
    if ($SkipInstall) {
        throw "Python virtual environment does not exist at '$VenvDir'. Run again without -SkipInstall."
    }

    $PythonLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($PythonLauncher) {
        Write-Host "[setup] Creating the Python virtual environment..."
        & py -3 -m venv $VenvDir
    }
    else {
        Assert-Command "python" "Install Python 3.10 or newer and add it to PATH."
        Write-Host "[setup] Creating the Python virtual environment..."
        & python -m venv $VenvDir
    }
}

if (-not $SkipInstall) {
    Write-Host "[setup] Installing/checking backend dependencies..."
    & $PythonExe -m pip install -r $RequirementsFile
    if ($LASTEXITCODE -ne 0) {
        throw "Backend dependency installation failed."
    }
}

Assert-Command "npm.cmd" "Install Node.js 20 LTS or newer and add it to PATH."
if (-not (Test-Path -LiteralPath $NodeModulesDir)) {
    if ($SkipInstall) {
        throw "Frontend dependencies are not installed. Run again without -SkipInstall."
    }

    Write-Host "[setup] Installing frontend dependencies..."
    Push-Location $FrontendDir
    try {
        & npm.cmd install
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend dependency installation failed."
        }
    }
    finally {
        Pop-Location
    }
}

function ConvertTo-EncodedCommand {
    param([string]$Command)

    return [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Command))
}

function Escape-SingleQuotedString {
    param([string]$Value)

    return $Value.Replace("'", "''")
}

$EscapedBackendDir = Escape-SingleQuotedString $BackendDir
$EscapedFrontendDir = Escape-SingleQuotedString $FrontendDir
$EscapedPythonExe = Escape-SingleQuotedString $PythonExe

$BackendCommand = @"
`$Host.UI.RawUI.WindowTitle = 'Art Rating System - Backend'
Set-Location -LiteralPath '$EscapedBackendDir'
Write-Host 'Backend: http://127.0.0.1:8000'
Write-Host 'Close this terminal window to stop the backend.'
& '$EscapedPythonExe' -m uvicorn main:app --host 0.0.0.0 --port 8000
`$ServiceExitCode = `$LASTEXITCODE
Write-Host "Backend exited with code `$ServiceExitCode."
"@

$FrontendCommand = @"
`$Host.UI.RawUI.WindowTitle = 'Art Rating System - Frontend'
Set-Location -LiteralPath '$EscapedFrontendDir'
Write-Host 'Frontend: http://127.0.0.1:7999'
Write-Host 'Close this terminal window to stop the frontend.'
& npm.cmd run dev
`$ServiceExitCode = `$LASTEXITCODE
Write-Host "Frontend exited with code `$ServiceExitCode."
"@

Write-Host "[start] Opening the backend terminal..."
Start-Process -FilePath "powershell.exe" -WorkingDirectory $BackendDir -ArgumentList @(
    "-NoLogo", "-NoProfile", "-NoExit", "-EncodedCommand",
    (ConvertTo-EncodedCommand $BackendCommand)
)

Write-Host "[start] Opening the frontend terminal..."
Start-Process -FilePath "powershell.exe" -WorkingDirectory $FrontendDir -ArgumentList @(
    "-NoLogo", "-NoProfile", "-NoExit", "-EncodedCommand",
    (ConvertTo-EncodedCommand $FrontendCommand)
)

Write-Host "Two service terminals have been opened. Close each window to stop its service."
