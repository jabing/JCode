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

# Create opencode.jsonc
$ConfigContent = @"
{
  "`$schema": "https://opencode.ai/config.json",
  "provider": {
    "opencode": {
      "options": {}
    }
  },
  "mcp": {},
  "tools": {
    "jcode": true
  },
  "skills": {
    "jcode-governance": true
  }
}
"@
$ConfigContent | Out-File -FilePath "$GlobalOpenCodeDir\opencode.jsonc" -Encoding utf8NoBOM
Write-Success "Created opencode.jsonc"

# Create JCode skill
$SkillContent = @"
---
name: jcode-governance
description: "JCode 代码治理层 - 6个 Agent 工作流验证。触发词: 'jcode', 'code governance', '代码治理', 'governance check', 'code review', 'code analysis'"
---

# JCode Governance Layer

<role>
You are a JCode governance orchestrator. JCode provides 6 agent tools for code governance:
- jcode.analyze - 问题分析验证
- jcode.plan - 任务规划验证  
- jcode.implement - 代码实现验证
- jcode.review - 代码审查 (APPROVED/REJECTED)
- jcode.test - 测试验证 (PASSED/FAILED)
- jcode.conductor - 终局裁决

When governance is enabled, use these tools to validate code changes before proceeding.
</role>

## TRIGGERS
- "jcode"
- "code governance"
- "代码治理"
- "governance check"

## USAGE
Invoke JCode tools via:
- CLI: python $JCodePath\jcode_start.py cli {command}
- API: http://localhost:8000/api/v1/jcode/{agent}
"@
$SkillContent | Out-File -FilePath "$GlobalOpenCodeDir\skills\jcode-governance\SKILL.md" -Encoding utf8NoBOM
Write-Success "Created JCode skill"

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
Write-Host "Use: '请使用 jcode 分析这个问题'" -ForegroundColor White
