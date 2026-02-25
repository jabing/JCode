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

# Create directories
New-Item -ItemType Directory -Path "$GlobalOpenCodeDir\skills\jcode-governance" -Force | Out-Null
Write-Success "Created .opencode directory"

# Create opencode.jsonc using Python (avoids encoding issues)
$PythonScript = @'
import json
import os

config_path = os.path.expanduser("~/.opencode/opencode.jsonc")
config = {
    "$schema": "https://opencode.ai/config.json",
    "provider": {"opencode": {"options": {}}},
    "mcp": {},
    "tools": {"jcode": True},
    "skills": {"jcode-governance": True}
}
with open(config_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(config, f, indent=2)
print("OK")
'@

$Result = python -c $PythonScript 2>&1
if ($Result -eq "OK") {
    Write-Success "Created opencode.jsonc"
} else {
    Write-Err "Failed to create config: $Result"
    exit 1
}

# Create JCode skill using Python
$SkillScript = @'
import os

skill_path = os.path.expanduser("~/.opencode/skills/jcode-governance/SKILL.md")
skill_content = """---
name: jcode-governance
description: "JCode 代码治理层 - 6个 Agent 工作流验证"
---

# JCode Governance Layer

<role>
You are a JCode governance orchestrator. JCode provides 6 agent tools:
- jcode.analyze - 问题分析验证
- jcode.plan - 任务规划验证  
- jcode.implement - 代码实现验证
- jcode.review - 代码审查 (APPROVED/REJECTED)
- jcode.test - 测试验证 (PASSED/FAILED)
- jcode.conductor - 终局裁决
</role>

## TRIGGERS
- jcode
- code governance
- 代码治理
- governance check

## USAGE
Invoke JCode tools via:
- CLI: python jcode_start.py cli {command}
- API: http://localhost:8000/api/v1/jcode/{agent}
"""
with open(skill_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(skill_content)
print("OK")
'@

$Result = python -c $SkillScript 2>&1
if ($Result -eq "OK") {
    Write-Success "Created JCode skill"
} else {
    Write-Err "Failed to create skill: $Result"
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
Write-Host "Skill: jcode-governance" -ForegroundColor Cyan
Write-Host "Triggers: 'jcode', 'code governance', '代码治理'" -ForegroundColor Cyan
Write-Host ""
Write-Host "Restart your terminal, then run 'opencode'" -ForegroundColor White
Write-Host "Use: 'jcode 分析这个问题'" -ForegroundColor White
