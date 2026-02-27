# JCode in VSCode - 集成指南

JCode 可以通过 **3 种方式** 在 VSCode 中使用，基于 MCP (Model Context Protocol) 协议。

---

## 方式 1: VSCode + MCP 扩展 (推荐)

### 前提条件
- VSCode 1.85+
- Python 3.10+
- Node.js 18+

### 步骤

#### 1. 安装 MCP 客户端扩展

在 VSCode 扩展市场搜索并安装：
- **MCP Client** (by Model Context Protocol)
- 或 **Continue** (支持 MCP 协议的 AI 编程助手)

#### 2. 配置 MCP 服务器

在 VSCode 设置中添加 MCP 配置：

**方法 A: 使用 settings.json**
```json
{
  "mcp.servers": {
    "jcode": {
      "type": "local",
      "command": "python",
      "args": ["-m", "mcp.server", "--port", "8080"],
      "cwd": "C:/dev_projects/jcode",
      "env": {
        "PYTHONPATH": "C:/dev_projects/jcode"
      }
    }
  }
}
```

**方法 B: 使用 .vscode/mcp.json**
```json
{
  "servers": [
    {
      "name": "jcode",
      "type": "local",
      "command": "python",
      "args": ["-m", "mcp.server", "--port", "8080"],
      "cwd": "${workspaceFolder}/../jcode",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/../jcode"
      }
    }
  ]
}
```

#### 3. 启动 MCP 服务器

在 VSCode 终端中运行：
```bash
cd C:/dev_projects/jcode
python -m mcp.server --port 8080
```

#### 4. 使用 JCode 工具

在 AI 聊天窗口中使用：
```
/jcode-mcp analyze "分析这个需求：实现用户登录功能"
/jcode-mcp plan "制定任务计划"
/jcode-mcp review "审查这段代码"
/jcode-mcp test "运行测试"
```

---

## 方式 2: VSCode + Continue 插件

### 安装 Continue

1. 在 VSCode 扩展市场搜索 **Continue**
2. 点击安装
3. 重启 VSCode

### 配置 Continue

编辑 `.continue/config.json`:

```json
{
  "models": [
    {
      "title": "JCode MCP",
      "provider": "openai-compatible",
      "model": "jcode",
      "apiBase": "http://localhost:8080"
    }
  ],
  "tabAutocompleteModel": {
    "title": "JCode Autocomplete",
    "provider": "openai-compatible",
    "model": "jcode",
    "apiBase": "http://localhost:8080"
  },
  "customCommands": [
    {
      "name": "jcode.analyze",
      "prompt": "/jcode-mcp analyze \"{{input}}\"",
      "description": "Analyze requirements with JCode"
    },
    {
      "name": "jcode.review",
      "prompt": "/jcode-mcp review \"{{input}}\"",
      "description": "Review code with JCode"
    },
    {
      "name": "jcode.plan",
      "prompt": "/jcode-mcp plan \"{{input}}\"",
      "description": "Plan tasks with JCode"
    }
  ]
}
```

### 使用方式

1. 选中代码
2. 右键 → Continue → 选择 `jcode.review`
3. 或按 `Ctrl+L` 打开聊天窗口，输入 `/jcode.analyze 需求描述`

---

## 方式 3: VSCode + REST API 调用

### 启动 JCode API 服务器

```bash
cd C:/dev_projects/jcode
python -m api.main --port 8000
```

### 创建 VSCode Snippets

在 `.vscode/jcode.code-snippets` 中添加：

```json
{
  "JCode Analyze": {
    "prefix": "jcode-analyze",
    "body": [
      "curl -X POST http://localhost:8000/api/v1/jcode/analyze \\",
      "  -H \"Content-Type: application/json\" \\",
      "  -d '${1:problem_statement}'"
    ],
    "description": "Call JCode Analyst API"
  },
  "JCode Review": {
    "prefix": "jcode-review",
    "body": [
      "curl -X POST http://localhost:8000/api/v1/jcode/review \\",
      "  -H \"Content-Type: application/json\" \\",
      "  -d '${1:code_to_review}'"
    ],
    "description": "Call JCode Reviewer API"
  },
  "JCode Plan": {
    "prefix": "jcode-plan",
    "body": [
      "curl -X POST http://localhost:8000/api/v1/jcode/plan \\",
      "  -H \"Content-Type: application/json\" \\",
      "  -d '${1:analysis_result}'"
    ],
    "description": "Call JCode Planner API"
  }
}
```

### 使用 Task 运行

在 `.vscode/tasks.json` 中添加：

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start JCode MCP Server",
      "type": "shell",
      "command": "python -m mcp.server --port 8080",
      "options": {
        "cwd": "${workspaceFolder}/../jcode"
      },
      "isBackground": true,
      "problemMatcher": []
    },
    {
      "label": "Start JCode API Server",
      "type": "shell",
      "command": "python -m api.main --port 8000",
      "options": {
        "cwd": "${workspaceFolder}/../jcode"
      },
      "isBackground": true,
      "problemMatcher": []
    },
    {
      "label": "JCode: Analyze Selection",
      "type": "shell",
      "command": "curl -X POST http://localhost:8080/mcp -H \"Content-Type: application/json\" -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"analyze\",\"arguments\":{\"input_data\":{\"problem_statement\":\"${selectedText}\"}}}}'",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

---

## API 端点参考

### MCP 协议端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/mcp` | POST | JSON-RPC 2.0 主端点 |

### REST API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/jcode/analyze` | POST | 调用 Analyst Agent |
| `/api/v1/jcode/plan` | POST | 调用 Planner Agent |
| `/api/v1/jcode/implement` | POST | 调用 Implementer Agent |
| `/api/v1/jcode/review` | POST | 调用 Reviewer Agent |
| `/api/v1/jcode/test` | POST | 调用 Tester Agent |
| `/api/v1/jcode/conductor` | POST | 调用 Conductor Agent |

---

## 示例工作流

### 1. 代码审查工作流

```bash
# 1. 启动 MCP 服务器
python -m mcp.server --port 8080

# 2. 在 VSCode 中打开终端，调用 review 工具
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "review",
      "arguments": {
        "input_data": {
          "code": "def login(username, password): ...",
          "requirements": ["必须验证密码强度"]
        }
      }
    }
  }'
```

### 2. 需求分析工作流

```bash
# 调用 analyze 工具
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "analyze",
      "arguments": {
        "input_data": {
          "problem_statement": "实现一个用户登录功能，支持邮箱和手机号"
        }
      }
    }
  }'
```

---

## 故障排查

### 问题 1: MCP 服务器无法启动

```bash
# 检查端口是否被占用
netstat -ano | findstr :8080

# 使用动态端口
python -m mcp.server --port 0
```

### 问题 2: VSCode 无法连接 MCP

1. 确认 MCP 服务器已启动
2. 检查 `settings.json` 中的路径配置
3. 查看 VSCode 开发者工具 → 网络 → MCP 请求

### 问题 3: Python 路径问题

```bash
# 设置环境变量
set PYTHONPATH=C:/dev_projects/jcode
python -m mcp.server --port 8080
```

---

## 高级配置

### 使用 Docker 运行 (可选)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "-m", "mcp.server", "--port", "8080", "--host", "0.0.0.0"]
```

```bash
docker build -t jcode .
docker run -p 8080:8080 jcode
```

然后在 VSCode 中配置：
```json
{
  "mcp.servers": {
    "jcode": {
      "type": "remote",
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

---

## 总结

| 方式 | 优点 | 适用场景 |
|------|------|----------|
| **MCP 扩展** | 原生集成，支持工具发现 | 日常开发 |
| **Continue 插件** | AI 编程助手，上下文感知 | 代码生成/审查 |
| **REST API** | 灵活，可自定义 | 自动化脚本 |

**推荐**: 使用 **方式 1 (MCP 扩展)** 获得最佳体验！

---

**JCode in VSCode: MCP-native governance at your fingertips.**
