# JCode 全局自动启用配置

## 快速安装 (推荐)

运行以下命令，JCode 将在任何目录下自动启用：

```powershell
cd C:\dev_projects\jcode
.\install-global.ps1
```

安装完成后：
1. **重启终端**（关闭并重新打开 PowerShell/CMD）
2. 在任何目录执行 `opencode`
3. JCode 工具将自动可用

---

## 安装脚本做了什么？

### 1. 创建全局配置目录

```
%USERPROFILE%\.opencode\
├── opencode.jsonc      # OpenCode 配置
└── skills\
    └── jcode-governance\
        └── README.md   # JCode 技能说明
```

### 2. 配置 JCode MCP 服务器

`opencode.jsonc` 内容：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "jcode": {
      "command": "python",
      "args": ["C:\dev_projects\jcode\mcp\jcode_server.py"],
      "enabled": true
    }
  }
}
```

### 3. 设置环境变量

- `JCODE_PATH` = JCode 安装路径
- `JCODE_ENABLED` = true
- `PYTHONPATH` 包含 JCode 路径

---

## 卸载

```powershell
.\install-global.ps1 -Uninstall
```

---

## 手动配置

如果自动安装失败，可以手动配置：

### 步骤 1: 创建配置目录

```powershell
mkdir $env:USERPROFILE\.opencode\skills\jcode-governance -Force
```

### 步骤 2: 创建配置文件

创建 `$env:USERPROFILE\.opencode\opencode.jsonc`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "jcode": {
      "command": "python",
      "args": ["C:\dev_projects\jcode\mcp\jcode_server.py"],
      "enabled": true
    }
  }
}
```

### 步骤 3: 设置环境变量

```powershell
[Environment]::SetEnvironmentVariable("JCODE_PATH", "C:\dev_projects\jcode", "User")
[Environment]::SetEnvironmentVariable("JCODE_ENABLED", "true", "User")

$pyPath = [Environment]::GetEnvironmentVariable("PYTHONPATH", "User")
$newPath = if ($pyPath) { "C:\dev_projects\jcode;$pyPath" } else { "C:\dev_projects\jcode" }
[Environment]::SetEnvironmentVariable("PYTHONPATH", $newPath, "User")
```

---

## 验证

重启终端后，在任何目录执行：

```powershell
# 检查环境变量
echo $env:JCODE_PATH
echo $env:JCODE_ENABLED

# 检查配置文件
cat $env:USERPROFILE\.opencode\opencode.jsonc

# 测试 JCode 导入
python -c "import jcode; print(jcode.__version__)"
```

---

## 在 OpenCode 中使用

启动 OpenCode 后，JCode 工具将自动可用：

```
# 在 OpenCode 中输入：
请使用 jcode.analyze 分析这个问题

# 或者：
使用 jcode.review 审查这段代码
```

可用的 6 个工具：
- `jcode.analyze` - 问题分析
- `jcode.plan` - 任务规划
- `jcode.implement` - 代码实现
- `jcode.review` - 代码审查
- `jcode.test` - 测试验证
- `jcode.conductor` - 终局裁决

---

## 故障排除

### 问题 1: OpenCode 找不到 JCode 工具

**解决方案**:
1. 确认 `opencode.jsonc` 文件存在
2. 确认路径正确（使用双反斜杠 `\`）
3. 重启终端和 OpenCode

### 问题 2: 环境变量未生效

**解决方案**:
1. 完全关闭所有终端
2. 重新打开终端
3. 检查：`echo $env:JCODE_PATH`

### 问题 3: Python 导入失败

**解决方案**:
```powershell
# 检查 PYTHONPATH
echo $env:PYTHONPATH

# 如果没有 JCode 路径，手动添加
$pyPath = [Environment]::GetEnvironmentVariable("PYTHONPATH", "User")
$newPath = if ($pyPath) { "C:\dev_projects\jcode;$pyPath" } else { "C:\dev_projects\jcode" }
[Environment]::SetEnvironmentVariable("PYTHONPATH", $newPath, "User")
```
