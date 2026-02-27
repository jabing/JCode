# 修复 JCode MCP 连接错误

## 问题诊断

错误信息：`jcode MCP error -32000: Connection closed`

### 根本原因

1. **模块名称冲突**：JCode 使用 `mcp/` 目录名，与系统安装的官方 MCP SDK (`mcp` 包) 冲突
2. **配置错误**：OpenCode 配置中使用了错误的模块名 `python -m mcp.server`

## 解决方案

### 方案 1：修复 OpenCode 配置（推荐）

编辑 `~/.config/opencode/opencode.json`，找到 `jcode` MCP 配置部分：

```json
{
  "mcp": {
    "jcode": {
      "type": "local",
      "command": [
        "python",
        "-m",
        "mcp.server",        // ← 错误的模块名
        "--port",
        "8080"
      ],
      "environment": {
        "PYTHONPATH": "C:/dev_projects/jcode"
      },
      "enabled": true
    }
  }
}
```

**修改为**：

```json
{
  "mcp": {
    "jcode": {
      "type": "local",
      "command": [
        "python",
        "-m",
        "jcode_mcp.server",  // ← 正确的模块名
        "--port",
        "8080"
      ],
      "env": {              // ← 改为 "env" 而不是 "environment"
        "PYTHONPATH": "C:/dev_projects/jcode"
      },
      "enabled": true
    }
  }
}
```

### 方案 2：使用自动配置脚本

运行修复脚本：

```bash
cd C:\dev_projects\jcode
python fix_opencode_config.py
```

这会自动：
1. 检测 OpenCode 配置文件位置
2. 修正 MCP 模块名称
3. 修正环境变量键名（`environment` → `env`）
4. 备份原配置文件

### 方案 3：手动启动服务器（临时方案）

如果不想修改配置，可以手动启动服务器：

```bash
# 1. 启动 JCode MCP 服务器
cd C:\dev_projects\jcode
set PYTHONPATH=C:\dev_projects\jcode
python -m jcode_mcp.server --port 8080

# 2. 在另一个终端打开 OpenCode
opencode
```

然后在 OpenCode 中使用：
```
@jcode-analyst 分析这个需求
```

---

## 验证修复

### 1. 测试服务器启动

```bash
cd C:\dev_projects\jcode
set PYTHONPATH=C:\dev_projects/jcode
python -m jcode_mcp.server --port 8080
```

**预期输出**：
```
JCode MCP Server v3.0.0
Available tools: 6 (analyst, planner, implementer, reviewer, tester, conductor)
Health endpoint: http://0.0.0.0:8080/health
JSON-RPC endpoint: http://0.0.0.0:8080/rpc
Server starting...
```

### 2. 测试健康端点

```bash
curl http://localhost:8080/health
```

**预期响应**：
```json
{
  "status": "ok",
  "tools": 6
}
```

### 3. 测试 OpenCode 连接

在 OpenCode 中运行：
```
/agents
```

应该看到 `jcode` 显示为已连接状态。

---

## 常见问题

### Q1: 服务器启动后立即退出

**原因**：缺少 `trio` 依赖

**解决**：
```bash
pip install trio
```

### Q2: 端口 8080 被占用

**检查**：
```bash
netstat -ano | findstr :8080
```

**解决**：使用其他端口
```bash
python -m jcode_mcp.server --port 8081
```

然后修改配置中的端口号。

### Q3: 环境变量不生效

**原因**：Windows 下 `environment` 应该改为 `env`

**解决**：在 `opencode.json` 中使用：
```json
"env": {
  "PYTHONPATH": "C:/dev_projects/jcode"
}
```

---

## 配置参考

完整的 `~/.config/opencode/opencode.json` 配置示例：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "zhipuai-coding-plan/glm-5",
  "small_model": "zhipuai-coding-plan/glm-4.7-flashx",
  "plugin": [
    "file:///C:/dev_projects/oh-my-opencode"
  ],
  "mcp": {
    "jcode": {
      "type": "local",
      "command": [
        "python",
        "-m",
        "jcode_mcp.server",
        "--port",
        "8080"
      ],
      "env": {
        "PYTHONPATH": "C:/dev_projects/jcode"
      },
      "enabled": true
    }
  }
}
```

---

## 总结

**错误原因**：
- ✅ 模块名称冲突（`mcp` vs `jcode_mcp`）
- ✅ 配置中的模块名错误

**修复方法**：
1. 修改 `opencode.json` 中的 `command` 字段
2. 将 `python -m mcp.server` 改为 `python -m jcode_mcp.server`
3. 将 `environment` 改为 `env`

**一行命令修复**（PowerShell）：
```powershell
(Get-Content ~/.config/opencode/opencode.json) -replace 'mcp\.server', 'jcode_mcp.server' -replace '"environment"', '"env"' | Set-Content ~/.config/opencode/opencode.json
```

然后重启 OpenCode 即可！
