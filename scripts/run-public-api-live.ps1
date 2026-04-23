param(
    [int]$Port = 8000,
    [string]$App = "main:app",
    [string]$HealthPath = "/chatbot/health",
    [int]$StartupTimeoutSeconds = 300
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

    $preferredPython = 'D:\ALCAS\chatbot\venv\Scripts\python.exe'
    if (Test-Path $preferredPython) {
        return @{
            FilePath = $preferredPython
            Arguments = @("-m", "uvicorn")
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
            Write-Host "Waiting for $Label..." -ForegroundColor DarkGray
            Start-Sleep -Milliseconds 750
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

function Get-NgrokCommand {
    param([string]$RepoRoot)

    $candidatePaths = @(
        (Join-Path $RepoRoot "ngrok.exe"),
        (Join-Path $RepoRoot "ngrok\ngrok.exe")
    )

    $envPath = (Get-Item env:NGROK_PATH -ErrorAction SilentlyContinue).Value
    if ($envPath) {
        $candidatePaths += $envPath
    }

    $command = Get-Command ngrok -ErrorAction SilentlyContinue
    if ($command) {
        $candidatePaths += $command.Source
    }

    $candidatePaths += @(
        'C:\Users\Atheeq\Pictures\ngrok.exe',
        'C:\Program Files\ngrok\ngrok.exe',
        'C:\Program Files (x86)\ngrok\ngrok.exe',
        "$env:LOCALAPPDATA\ngrok\ngrok.exe",
        "$env:USERPROFILE\AppData\Local\ngrok\ngrok.exe",
        "$env:USERPROFILE\AppData\Local\Programs\ngrok\ngrok.exe"
    )

    foreach ($candidate in $candidatePaths | Where-Object { $_ } | Select-Object -Unique) {
        if (Test-Path $candidate) {
            return @{ Source = (Resolve-Path $candidate).Path }
        }
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

function Quote-ProcessArgument {
    param([string]$Argument)

    if ($null -eq $Argument) {
        return '""'
    }

    if ($Argument -match '[\s"`]' ) {
        return '"' + ($Argument -replace '"', '\"') + '"'
    }

    return $Argument
}

function Join-ProcessArguments {
    param([string[]]$Arguments)

    return ($Arguments | ForEach-Object { Quote-ProcessArgument $_ }) -join ' '
}

function Start-LiveProcess {
    param(
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory,
        [string]$Name,
        [ConsoleColor]$Color
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
        $psi.Arguments = Join-ProcessArguments -Arguments $Arguments
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    $process.EnableRaisingEvents = $true

    $stdoutAction = {
        if ($EventArgs.Data) {
            Write-Host "[$($Event.MessageData.Name)] $($EventArgs.Data)" -ForegroundColor $Event.MessageData.Color
        }
    }

    $stderrAction = {
        if ($EventArgs.Data) {
            Write-Host "[$($Event.MessageData.Name)] $($EventArgs.Data)" -ForegroundColor Red
        }
    }

    if (-not $process.Start()) {
        throw "Failed to start $Name"
    }

    $outEvent = Register-ObjectEvent -InputObject $process -EventName OutputDataReceived -MessageData @{ Name = $Name; Color = $Color } -Action $stdoutAction
    $errEvent = Register-ObjectEvent -InputObject $process -EventName ErrorDataReceived -MessageData @{ Name = $Name; Color = $Color } -Action $stderrAction

    $process.BeginOutputReadLine()
    $process.BeginErrorReadLine()

    return @{
        Process = $process
        OutEvent = $outEvent
        ErrEvent = $errEvent
        Name = $Name
    }
}

function Stop-LiveProcess {
    param([hashtable]$Handle)

    if (-not $Handle) {
        return
    }

    foreach ($eventSub in @($Handle.OutEvent, $Handle.ErrEvent)) {
        if ($eventSub) {
            try {
                Unregister-Event -SubscriptionId $eventSub.Id -ErrorAction SilentlyContinue
            } catch {
            }
            try {
                Remove-Job -Id $eventSub.Action.Id -Force -ErrorAction SilentlyContinue
            } catch {
            }
        }
    }

    $process = $Handle.Process
    if ($process -and -not $process.HasExited) {
        try {
            $null = $process.CloseMainWindow()
            if (-not $process.WaitForExit(1500)) {
                $process.Kill($true)
                $process.WaitForExit()
            }
        } catch {
            try {
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            } catch {
            }
        }
    }
}

$repoRoot = Get-RepoRoot
$envFile = Join-Path $repoRoot ".env"
$localHealthUrl = "http://127.0.0.1:$Port$HealthPath"

$uvicornHandle = $null
$ngrokHandle = $null

try {
    Write-Step "Starting API and ngrok in this terminal"

    $pythonSpec = Get-PythonLaunchSpec -RepoRoot $repoRoot
    $uvicornArgs = @()
    $uvicornArgs += $pythonSpec.Arguments
    $uvicornArgs += @($App, "--host", "0.0.0.0", "--port", "$Port")

    Write-Step "Starting uvicorn with $($pythonSpec.Display)"
    Write-Host "Waiting up to $StartupTimeoutSeconds seconds for the local API to warm up." -ForegroundColor DarkGray
    $uvicornHandle = Start-LiveProcess `
        -FilePath $pythonSpec.FilePath `
        -Arguments $uvicornArgs `
        -WorkingDirectory $repoRoot `
        -Name "uvicorn" `
        -Color Green

    Wait-ForHttpOk -Url $localHealthUrl -TimeoutSeconds $StartupTimeoutSeconds -Label "Local API" | Out-Null

    $ngrokCommand = Get-NgrokCommand -RepoRoot $repoRoot
    if (-not $ngrokCommand) {
        throw "ngrok was not found. Add ngrok.exe to the repo root, set NGROK_PATH to the full ngrok.exe path, or install it with `winget install ngrok.ngrok`, then run `ngrok config add-authtoken <token>`."
    }

    Write-Step "Starting ngrok tunnel"
    $ngrokHandle = Start-LiveProcess `
        -FilePath $ngrokCommand.Source `
        -Arguments @("http", "$Port") `
        -WorkingDirectory $repoRoot `
        -Name "ngrok" `
        -Color Yellow

    $publicBaseUrl = $null
    $deadline = (Get-Date).AddSeconds($StartupTimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if ($uvicornHandle.Process.HasExited) {
            throw "uvicorn exited unexpectedly during startup."
        }
        if ($ngrokHandle.Process.HasExited) {
            throw "ngrok exited unexpectedly during startup."
        }

        Write-Host "Waiting for ngrok to publish a public URL..." -ForegroundColor DarkGray
        Start-Sleep -Seconds 1
        $publicBaseUrl = Get-HttpsTunnelUrl -TunnelInfo (Get-NgrokTunnelInfo)
        if ($publicBaseUrl) {
            break
        }
    }

    if (-not $publicBaseUrl) {
        throw "ngrok did not publish a public HTTPS URL within $StartupTimeoutSeconds seconds."
    }

    Upsert-EnvValue -FilePath $envFile -Key "VOICE_PUBLIC_BASE_URL" -Value $publicBaseUrl

    Write-Host ""
    Write-Host "System is ready." -ForegroundColor Green
    Write-Host "Local health:  $localHealthUrl"
    Write-Host "Public base:   $publicBaseUrl"
    Write-Host "Public health: $publicBaseUrl$HealthPath"
    Write-Host "Voice webhook: $publicBaseUrl/voice?session_id=demo-session"
    Write-Host ""
    Write-Host "Press Ctrl+C to stop uvicorn and ngrok." -ForegroundColor Cyan
    Write-Host ""

    while ($true) {
        if ($uvicornHandle.Process.HasExited) {
            throw "uvicorn exited unexpectedly."
        }
        if ($ngrokHandle.Process.HasExited) {
            throw "ngrok exited unexpectedly."
        }

        Wait-Event -Timeout 1 | Out-Null
    }
} finally {
    Write-Host ""
    Write-Step "Shutting down child processes"
    Stop-LiveProcess -Handle $ngrokHandle
    Stop-LiveProcess -Handle $uvicornHandle
}






