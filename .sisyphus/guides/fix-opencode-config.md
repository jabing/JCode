# 修复 OpenCode JCode MCP 配置

## 问题
OpenCode 中 JCode MCP 连接失败，错误：`jcode MCP error -32000: Connection closed`

## 根本原因
1. **模块名错误**：配置使用 `python -m mcp.server`，但应该是 `python -m jcode_mcp.server`
2. **键名错误**：使用 `environment` 而不是 `env`

## 解决方案

### 方法 1：手动编辑（推荐）

编辑 `~/.config/opencode/opencode.json`，找到 `jcode` 部分：

**修改前（错误）：**
```json
"jcode": {
  "type": "local",
  "command": [
    "python",
    "-m",
    "mcp.server",        // ← 错误
    "--port",
    "8080"
  ],
  "environment": {       // ← 错误
    "PYTHONPATH": "C:/dev_projects/jcode"
  },
  "enabled": true
}
```

**修改后（正确）：**
```json
"jcode": {
  "type": "local",
  "command": [
    "python",
    "-m",
    "jcode_mcp.server",  // ← 正确
    "--port",
    "8080"
  ],
  "env": {               // ← 正确
    "PYTHONPATH": "C:/dev_projects/jcode"
  },
  "enabled": true
}
```

### 方法 2：PowerShell 一键修复

```powershell
$configPath = "$env:USERPROFILE\.config\opencode\opencode.json"
$content = Get-Content $configPath -Raw

# 修复模块名
$content = $content -replace '"mcp\.server"', '"jcode_mcp.server"'

# 修复键名
$content = $content -replace '"environment":', '"env":'

# 保存
$content | Set-Content $configPath -Encoding UTF8

Write-Host "✓ OpenCode 配置已修复"
```

### 方法 3：Python 脚本修复

```python
import json
from pathlib import Path

config_path = Path.home() / ".config" / "opencode" / "opencode.json"

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 修复 jcode 配置
if "jcode" in config.get("mcp", {}):
    jcode = config["mcp"]["jcode"]
    
    # 修复命令
    if "command" in jcode:
        jcode["command"] = [
            cmd if cmd != "mcp.server" else "jcode_mcp.server"
            for cmd in jcode["command"]
        ]
    
    # 修复键名
    if "environment" in jcode:
        jcode["env"] = jcode.pop("environment")

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("✓ OpenCode 配置已修复")
```

## 验证

修复后，重启 OpenCode 并测试：

```bash
# 1. 测试 MCP 服务器（独立）
cd C:\dev_projects\jcode
set PYTHONPATH=C:\dev_projects\jcode
python -m jcode_mcp.server --port 8080

# 2. 在另一个终端测试
curl http://localhost:8080/health
# 应返回：{"status":"ok","tools":6}

curl -X POST http://localhost:8080/mcp -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
# 应返回 6 个工具

# 3. 重启 OpenCode
opencode

# 4. 在 OpenCode 中测试
/agents
# 应显示 jcode 为已连接状态
```

## 服务器已验证工作

```
✓ Health endpoint: {"status":"ok","tools":6}
✓ Tools/list: 返回 6 个工具 (analyze, plan, implement, review, test, conductor)
✓ Tools/call: analyze 工具可以正常调用
```

## 下一步

1. 应用上述配置修复
2. 重启 OpenCode
3. 使用 `@jcode-analyst 分析这个需求` 测试连接
