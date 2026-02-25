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

# Create opencode.jsonc
@"
{
  "`$schema": "https://opencode.ai/config.json",
  "mcp": {
    "jcode": {
      "command": "python",
      "args": ["$JCodeMcpServer"],
      "enabled": true
    }
  }
}
"@ | Out-File -FilePath "$GlobalOpenCodeDir\opencode.jsonc" -Encoding UTF8
Write-Success "Created opencode.jsonc"

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
Write-Host "Restart your terminal, then run 'opencode'" -ForegroundColor Cyan
Write-Host "JCode tools will be available automatically" -ForegroundColor Cyan
