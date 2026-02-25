# JCode Global Installation Script for Windows
# Usage: .\install-global.ps1 [-JCodePath "C:\path\to\jcode"] [-Uninstall]

param(
    [string]$JCodePath = "C:\dev_projects\jcode",
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

function Write-Success { Write-Host "[OK] $args" -ForegroundColor Green }
function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Cyan }
function Write-Err { Write-Host "[ERROR] $_" -ForegroundColor Red }

$GlobalOpenCodeDir = "$env:USERPROFILE\.opencode"
$JCodeMcpServer = "$JCodePath\mcp\jcode_server.py"

if ($Uninstall) {
    Write-Info "Uninstalling JCode..."
    if (Test-Path $GlobalOpenCodeDir) {
        Remove-Item -Path $GlobalOpenCodeDir -Recurse -Force
        Write-Success "Removed global .opencode directory"
    }
    [Environment]::SetEnvironmentVariable("JCODE_PATH", $null, "User")
    [Environment]::SetEnvironmentVariable("JCODE_ENABLED", $null, "User")
    Write-Success "JCode uninstalled!"
    exit 0
}

Write-Info "Installing JCode to: $JCodePath"

# Create global .opencode directory
New-Item -ItemType Directory -Path "$GlobalOpenCodeDir\skills\jcode-governance" -Force | Out-Null
Write-Success "Created .opencode directory"

# Create opencode.jsonc using Python for proper JSON escaping
$PythonScript = @"
import json
import os

config_path = os.path.expanduser('~/.opencode/opencode.jsonc')

config = {
    '\$schema': 'https://opencode.ai/config.json',
    'mcp': {
        'jcode': {
            'command': 'python',
            'args': [r'$JCodeMcpServer'.replace('/', os.sep)],
            'enabled': True
        }
    }
}

content = json.dumps(config, indent=2)
with open(config_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('OK')
"@

$Result = python -c $PythonScript 2>&1
if ($Result -eq "OK") {
    Write-Success "Created opencode.jsonc (valid JSON)"
} else {
    Write-Err "Failed to create config: $Result"
    exit 1
}

# Set environment variables
[Environment]::SetEnvironmentVariable("JCODE_PATH", $JCodePath, "User")
[Environment]::SetEnvironmentVariable("JCODE_ENABLED", "true", "User")

$pyPath = [Environment]::GetEnvironmentVariable("PYTHONPATH", "User")
if ($pyPath -notlike "*$JCodePath*") {
    $newPath = if ($pyPath) { "$JCodePath;$pyPath" } else { $JCodePath }
    [Environment]::SetEnvironmentVariable("PYTHONPATH", $newPath, "User")
    Write-Success "Added to PYTHONPATH"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "JCode Installed Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Config file: $GlobalOpenCodeDir\opencode.jsonc" -ForegroundColor Cyan
Write-Host "Restart your terminal, then run 'opencode'" -ForegroundColor Cyan
Write-Host "JCode tools will be available automatically" -ForegroundColor Cyan
