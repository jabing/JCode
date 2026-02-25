# JCode 全局安装指南

本文档介绍如何将 JCode 安装到 OMO (Oh-my-opencode) 和 OpenCode 的全局环境中。

## 前提条件

- Python 3.10+ 已安装
- OMO (Oh-my-opencode) 已安装
- OpenCode 已安装

---

## 方法 1: pip 安装 (推荐)

### 步骤 1: 安装 JCode 包

```bash
cd C:\dev_projects\jcode
pip install -e .
```

这会将 JCode 以"可编辑模式"安装，修改代码后无需重新安装。

### 步骤 2: 验证安装

```bash
python -c "from core.agent_manager import AgentManager; print('JCode installed!')"
jcode_start.py status
```

---

## 方法 2: 添加到 PYTHONPATH

### Windows (PowerShell)

```powershell
# 添加到用户环境变量
[Environment]::SetEnvironmentVariable("PYTHONPATH", "C:\dev_projects\jcode;$env:PYTHONPATH", "User")

# 或添加到系统环境变量（需要管理员权限）
[Environment]::SetEnvironmentVariable("PYTHONPATH", "C:\dev_projects\jcode;$env:PYTHONPATH", "Machine")
```

### Windows (CMD)

```cmd
setx PYTHONPATH "C:\dev_projects\jcode;%PYTHONPATH%"
```

### Linux/macOS

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export PYTHONPATH="$PYTHONPATH:/path/to/jcode"' >> ~/.bashrc
source ~/.bashrc
```

---

## 配置 OMO

### 步骤 1: 找到 OMO 配置文件

OMO 配置文件通常位于：
- Windows: `%USERPROFILE%\.omo\config.yaml`
- Linux/macOS: `~/.omo/config.yaml`

### 步骤 2: 添加 JCode MCP 服务器

编辑 OMO 配置文件，添加 JCode：

```yaml
# ~/.omo/config.yaml

mcp_servers:
  jcode:
    command: python
    args:
      - C:\dev_projects\jcode\mcp\jcode_server.py
    enabled: true
    description: "JCode Governance Layer - 6 Agent tools"
```

### 步骤 3: 重启 OMO

```bash
# 重启 OMO 服务
omo restart
```

### 步骤 4: 验证 JCode 已加载

```bash
omo list-tools | grep jcode
```

应该看到：
```
jcode.analyze
jcode.plan
jcode.implement
jcode.review
jcode.test
jcode.conductor
```

---

## 配置 OpenCode

OpenCode 通过 OMO 间接使用 JCode。确保：

1. OMO 已正确配置（如上所述）
2. OpenCode 已连接到 OMO

### 验证 OpenCode 集成

在 OpenCode 中输入：

```
请使用 jcode.analyze 工具分析这个问题
```

如果 JCode 正确安装，OpenCode 应该能够调用 JCode 工具。

---

## 快速验证清单

```bash
# 1. 检查 Python 导入
python -c "from core.agent_manager import AgentManager; print('✅ Core modules OK')"

# 2. 检查 MCP 服务器
python -c "from mcp.jcode_server import create_server; s=create_server(); print(f'✅ MCP Server: {len(s.list_tools())} tools')"

# 3. 检查启动脚本
python jcode_start.py status

# 4. 启动 API 测试
python jcode_start.py api --port 8000
# 访问 http://localhost:8000/docs
```

---

## 故障排除

### 问题 1: ModuleNotFoundError

**解决方案**:
```bash
# 确保在项目目录或已添加到 PYTHONPATH
cd C:\dev_projects\jcode
pip install -e .
```

### 问题 2: OMO 未加载 JCode

**解决方案**:
1. 检查配置文件路径是否正确
2. 检查 jcode_server.py 路径是否正确
3. 重启 OMO

### 问题 3: OpenCode 无法调用 JCode

**解决方案**:
1. 确保 OMO 已正确配置
2. 检查 OpenCode 是否连接到 OMO
3. 查看 OMO 日志获取详细错误信息

---

## 目录结构参考

```
C:\dev_projects\jcode\
├── jcode_start.py          # 统一入口
├── core/                   # 核心模块
│   ├── agent_manager.py
│   ├── switch_manager.py
│   └── agents/
├── api/                    # REST API
│   └── main.py
├── cli/                    # CLI
│   └── commands.py
├── mcp/                    # MCP 服务器
│   └── jcode_server.py
├── config/                 # 配置
│   └── jcode_config.yaml
└── docs/                   # 文档
    └── INSTALLATION.md
```
