param(
    [int]$Port = 8000,
    [string]$App = "main:app",
    [string]$HealthPath = "/chatbot/health",
    [int]$StartupTimeoutSeconds = 60
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Get-RepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Get-PythonLaunchSpec {
    param([string]$RepoRoot)

    $preferredPython = 'C:\Users\Atheeq\venvs\student-project\Scripts\python.exe'
    if (Test-Path $preferredPython) {
        return @{
            FilePath = $preferredPython
            Arguments = @('-m', 'uvicorn')
            Display = $preferredPython
        }
    }

    $venvPython = Join-Path $RepoRoot '.venv\Scripts\python.exe'
    if (Test-Path $venvPython) {
        return @{
            FilePath = $venvPython
            Arguments = @("-m", "uvicorn")
            Display = $venvPython
        }
    }

    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCommand) {
        return @{
            FilePath = $pyCommand.Source
            Arguments = @("-3.11", "-m", "uvicorn")
            Display = "py -3.11"
        }
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        return @{
            FilePath = $pythonCommand.Source
            Arguments = @("-m", "uvicorn")
            Display = "python"
        }
    }

    throw "Python was not found. Create a .venv or install Python 3.11+."
}

function Wait-ForHttpOk {
    param(
        [string]$Url,
        [int]$TimeoutSeconds,
        [string]$Label
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        } catch {
            Start-Sleep -Seconds 1
        }
    }

    throw "$Label did not become ready within $TimeoutSeconds seconds: $Url"
}

function Get-NgrokTunnelInfo {
    try {
        return Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 5
    } catch {
        return $null
    }
}

function Get-HttpsTunnelUrl {
    param([object]$TunnelInfo)

    if (-not $TunnelInfo -or -not $TunnelInfo.tunnels) {
        return $null
    }

    $httpsTunnel = $TunnelInfo.tunnels | Where-Object { $_.public_url -like "https://*" } | Select-Object -First 1
    if ($httpsTunnel) {
        return $httpsTunnel.public_url
    }

    return $null
}

function Upsert-EnvValue {
    param(
        [string]$FilePath,
        [string]$Key,
        [string]$Value
    )

    if (Test-Path $FilePath) {
        $content = Get-Content $FilePath
    } else {
        $content = @()
    }

    $updated = $false
    $newContent = foreach ($line in $content) {
        if ($line -match "^\s*$([regex]::Escape($Key))=") {
            $updated = $true
            "$Key=$Value"
        } else {
            $line
        }
    }

    if (-not $updated) {
        $newContent += "$Key=$Value"
    }

    Set-Content -Path $FilePath -Value $newContent
}

$repoRoot = Get-RepoRoot
$envFile = Join-Path $repoRoot ".env"
$logDir = Join-Path $repoRoot "scripts\logs"
$uvicornOut = Join-Path $logDir "uvicorn.out.log"
$uvicornErr = Join-Path $logDir "uvicorn.err.log"
$ngrokOut = Join-Path $logDir "ngrok.out.log"
$ngrokErr = Join-Path $logDir "ngrok.err.log"
$localHealthUrl = "http://127.0.0.1:$Port$HealthPath"

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

Write-Step "Checking local API"
$apiReady = $false
try {
    Wait-ForHttpOk -Url $localHealthUrl -TimeoutSeconds 2 -Label "Local API" | Out-Null
    $apiReady = $true
} catch {
    $apiReady = $false
}

if (-not $apiReady) {
    $pythonSpec = Get-PythonLaunchSpec -RepoRoot $repoRoot
    Write-Step "Starting uvicorn with $($pythonSpec.Display)"
    $uvicornArgs = @()
    $uvicornArgs += $pythonSpec.Arguments
    $uvicornArgs += @($App, "--host", "0.0.0.0", "--port", "$Port", "--reload")

    $uvicornProcess = Start-Process `
        -FilePath $pythonSpec.FilePath `
        -ArgumentList $uvicornArgs `
        -WorkingDirectory $repoRoot `
        -RedirectStandardOutput $uvicornOut `
        -RedirectStandardError $uvicornErr `
        -PassThru

    try {
        Wait-ForHttpOk -Url $localHealthUrl -TimeoutSeconds $StartupTimeoutSeconds -Label "Local API" | Out-Null
    } catch {
        if ($uvicornProcess -and -not $uvicornProcess.HasExited) {
            Stop-Process -Id $uvicornProcess.Id -Force
        }
        throw "uvicorn failed to start. Check $uvicornErr and $uvicornOut"
    }
} else {
    Write-Step "Local API is already responding on port $Port"
}

$ngrokCommand = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $ngrokCommand) {
    throw "ngrok is not installed or not on PATH. Install it with `winget install ngrok.ngrok`, then run `ngrok config add-authtoken <token>`."
}

Write-Step "Checking ngrok tunnel"
$tunnelInfo = Get-NgrokTunnelInfo
$publicBaseUrl = Get-HttpsTunnelUrl -TunnelInfo $tunnelInfo

if (-not $publicBaseUrl) {
    Write-Step "Starting ngrok for port $Port"
    $ngrokProcess = Start-Process `
        -FilePath $ngrokCommand.Source `
        -ArgumentList @("http", "$Port") `
        -WorkingDirectory $repoRoot `
        -RedirectStandardOutput $ngrokOut `
        -RedirectStandardError $ngrokErr `
        -PassThru

    $deadline = (Get-Date).AddSeconds($StartupTimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if ($ngrokProcess.HasExited) {
            throw "ngrok exited early. Check $ngrokErr and $ngrokOut"
        }

        Start-Sleep -Seconds 1
        $tunnelInfo = Get-NgrokTunnelInfo
        $publicBaseUrl = Get-HttpsTunnelUrl -TunnelInfo $tunnelInfo
        if ($publicBaseUrl) {
            break
        }
    }

    if (-not $publicBaseUrl) {
        throw "ngrok did not publish a public HTTPS URL within $StartupTimeoutSeconds seconds. Check $ngrokErr and $ngrokOut"
    }
} else {
    Write-Step "Reusing existing ngrok tunnel"
}

Write-Step "Updating .env with VOICE_PUBLIC_BASE_URL"
Upsert-EnvValue -FilePath $envFile -Key "VOICE_PUBLIC_BASE_URL" -Value $publicBaseUrl

Write-Host ""
Write-Host "Public API is ready." -ForegroundColor Green
Write-Host "Local health:  $localHealthUrl"
Write-Host "Public base:   $publicBaseUrl"
Write-Host "Public health: $publicBaseUrl$HealthPath"
Write-Host "Voice webhook: $publicBaseUrl/voice?session_id=demo-session"
Write-Host ""
Write-Host "Logs:"
Write-Host "  uvicorn stdout: $uvicornOut"
Write-Host "  uvicorn stderr: $uvicornErr"
Write-Host "  ngrok stdout:   $ngrokOut"
Write-Host "  ngrok stderr:   $ngrokErr"
Write-Host ""
Write-Host "If the app was already running before this script, restart it once so it reloads the updated .env value." -ForegroundColor Yellow



