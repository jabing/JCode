# JCode MCP 服务器 - 自动启动方案

JCode MCP 服务器不需要每次都手动运行！以下是 **5 种自动启动方案**，选择最适合你的方式。

---

## 方案 1: VSCode 自动启动 ⭐⭐⭐⭐⭐ (推荐)

**优点**: 最简单，打开 VSCode 自动启动  
**适用**: 日常开发，VSCode 用户

### 配置方法

在 `.vscode/settings.json` 中添加：

```json
{
  "mcp.enabled": true,
  "mcp.autoStart": true,
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

### 效果
- ✅ 打开 VSCode 自动启动 JCode MCP 服务器
- ✅ 关闭 VSCode 自动停止服务器
- ✅ 无需任何手动操作

### 使用 `configure_vscode.py` 自动配置
```bash
python configure_vscode.py --project
# 自动启用 mcp.autoStart
```

---

## 方案 2: 开机自启动 ⭐⭐⭐⭐

**优点**: 系统启动后一直可用  
**适用**: 专职开发，JCode 重度用户

### Windows - 创建快捷方式

1. **创建批处理文件** `C:\dev_projects\jcode\start_jcode_server.bat`:
```batch
@echo off
cd /d C:\dev_projects\jcode
python -m mcp.server --port 8080
pause
```

2. **创建快捷方式**:
   - 右键 `start_jcode_server.bat` → 创建快捷方式
   - 将快捷方式复制到启动文件夹：
     - 按 `Win+R`，输入 `shell:startup`
     - 粘贴快捷方式

### macOS/Linux - 添加 Systemd 服务

**创建服务文件** `/etc/systemd/system/jcode-mcp.service`:
```ini
[Unit]
Description=JCode MCP Server
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/jcode
ExecStart=/usr/bin/python3 -m mcp.server --port 8080
Restart=always
Environment=PYTHONPATH=/path/to/jcode

[Install]
WantedBy=multi-user.target
```

**启用服务**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable jcode-mcp
sudo systemctl start jcode-mcp
```

**检查状态**:
```bash
sudo systemctl status jcode-mcp
```

---

## 方案 3: VSCode 任务自动启动 ⭐⭐⭐⭐

**优点**: 一键启动，可配置快捷键  
**适用**: 需要控制启动时机的用户

### 配置方法

`.vscode/tasks.json` 已包含启动任务：

```json
{
  "label": "JCode: Start MCP Server",
  "type": "shell",
  "command": "python -m mcp.server --port 8080",
  "options": {
    "cwd": "C:/dev_projects/jcode"
  },
  "isBackground": true,
  "problemMatcher": []
}
```

### 使用方式

1. **手动触发**:
   - `Ctrl+Shift+P` → `Tasks: Run Task` → `JCode: Start MCP Server`

2. **配置快捷键** (推荐):
   - 打开 `.vscode/keybindings.json`
   ```json
   {
     "key": "ctrl+alt+j",
     "command": "workbench.action.tasks.runTask",
     "args": "JCode: Start MCP Server"
   }
   ```

3. **自动启动** (打开项目时):
   - 在 `.vscode/settings.json` 添加:
   ```json
   {
     "task.autoDetect": "on",
     "tasks": {
       "version": "2.0.0",
       "tasks": [
         {
           "label": "JCode: Start MCP Server",
           "group": {
             "kind": "build",
             "isDefault": true
           }
         }
       ]
     }
   }
   ```

---

## 方案 4: Docker 后台运行 ⭐⭐⭐

**优点**: 环境隔离，不依赖本地 Python  
**适用**: 多项目，需要环境隔离

### 启动容器

```bash
docker run -d \
  --name jcode-mcp \
  -p 8080:8080 \
  -v $(pwd):/app \
  -w /app \
  python:3.10-slim \
  python -m mcp.server --port 8080 --host 0.0.0.0
```

### 配置 Docker Compose (推荐)

创建 `docker-compose.yml`:
```yaml
version: '3.8'

services:
  jcode-mcp:
    image: python:3.10-slim
    container_name: jcode-mcp
    working_dir: /app
    volumes:
      - .:/app
    ports:
      - "8080:8080"
    command: python -m mcp.server --port 8080 --host 0.0.0.0
    restart: unless-stopped
    environment:
      - PYTHONPATH=/app
```

**启动**:
```bash
docker-compose up -d
```

**停止**:
```bash
docker-compose down
```

**开机自启**:
```bash
docker-compose up -d
# 添加 systemd 服务管理 docker-compose
```

### VSCode 配置

在 `.vscode/settings.json` 中配置远程 MCP：
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

## 方案 5: PM2 进程管理 ⭐⭐⭐⭐

**优点**: 自动重启，日志管理，多实例  
**适用**: 生产环境，需要高可用

### 安装 PM2

```bash
npm install -g pm2
```

### 创建 PM2 配置文件 `ecosystem.config.js`

```javascript
module.exports = {
  apps: [{
    name: 'jcode-mcp',
    script: 'python',
    args: '-m mcp.server --port 8080',
    cwd: 'C:/dev_projects/jcode',
    env: {
      PYTHONPATH: 'C:/dev_projects/jcode'
    },
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    error_file: './logs/jcode-error.log',
    out_file: './logs/jcode-out.log',
    log_file: './logs/jcode-combined.log',
    time: true
  }]
};
```

### 启动服务

```bash
# 启动
pm2 start ecosystem.config.js

# 开机自启
pm2 startup
# 按提示运行生成的命令

# 保存当前进程列表
pm2 save
```

### 常用命令

```bash
# 查看状态
pm2 status

# 查看日志
pm2 logs jcode-mcp

# 重启
pm2 restart jcode-mcp

# 停止
pm2 stop jcode-mcp

# 删除
pm2 delete jcode-mcp
```

### VSCode 配置

使用本地 MCP 配置即可，PM2 会保证服务器一直运行：
```json
{
  "mcp.servers": {
    "jcode": {
      "type": "local",
      "command": "python",
      "args": ["-m", "mcp.server", "--port", "8080"],
      "cwd": "C:/dev_projects/jcode"
    }
  }
}
```

---

## 方案对比

| 方案 | 难度 | 自动化程度 | 适用场景 |
|------|------|------------|----------|
| **VSCode 自动启动** | ⭐ | ⭐⭐⭐⭐⭐ | 日常开发 (推荐) |
| **开机自启动** | ⭐⭐ | ⭐⭐⭐⭐⭐ | 专职开发 |
| **VSCode 任务** | ⭐ | ⭐⭐⭐⭐ | 按需启动 |
| **Docker** | ⭐⭐⭐ | ⭐⭐⭐⭐ | 环境隔离 |
| **PM2** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 生产环境 |

---

## 推荐配置组合

### 方案 A: 轻量级开发 (推荐新手)

```bash
# 使用 VSCode 自动启动
python configure_vscode.py --project
```

**效果**: 打开 VSCode 自动启动，关闭自动停止

---

### 方案 B: 专业开发 (推荐)

```bash
# 1. 使用 PM2 管理进程
pm2 start ecosystem.config.js
pm2 startup
pm2 save

# 2. VSCode 配置远程连接
# 在 .vscode/settings.json 中配置:
{
  "mcp.servers": {
    "jcode": {
      "type": "remote",
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

**效果**: JCode 服务器一直可用，重启后自动恢复

---

### 方案 C: 多项目管理

```bash
# 使用 Docker Compose 管理多个 MCP 服务
# 每个项目一个容器
docker-compose up -d
```

**效果**: 项目间环境隔离，互不干扰

---

## 故障排查

### 问题 1: VSCode 自动启动失败

**检查**:
```json
// .vscode/settings.json
{
  "mcp.enabled": true,      // 必须是 true
  "mcp.autoStart": true,    // 必须是 true
  "mcp.servers": {          // 配置必须正确
    "jcode": { ... }
  }
}
```

**解决**:
1. 重启 VSCode
2. 查看 MCP 扩展日志
3. 检查端口是否被占用：`netstat -ano | findstr :8080`

---

### 问题 2: 开机自启动不生效

**Windows**:
```powershell
# 检查启动文件夹
shell:startup

# 确认快捷方式存在
# 确保批处理文件路径正确
```

**Linux**:
```bash
# 检查服务状态
sudo systemctl status jcode-mcp

# 查看日志
sudo journalctl -u jcode-mcp -f

# 重新启用
sudo systemctl enable jcode-mcp
sudo systemctl start jcode-mcp
```

---

### 问题 3: PM2 重启失败

```bash
# 查看详细错误
pm2 logs jcode-mcp --lines 100

# 检查 Python 路径
pm2 describe jcode-mcp | grep "script path"

# 重新配置
pm2 delete jcode-mcp
pm2 start ecosystem.config.js
```

---

## 高级技巧

### 技巧 1: 动态端口 (避免冲突)

```bash
# 使用端口 0 自动分配可用端口
python -m mcp.server --port 0
```

在 VSCode 配置中使用动态端口：
```json
{
  "mcp.servers": {
    "jcode": {
      "type": "local",
      "command": "python",
      "args": ["-m", "mcp.server", "--port", "0"],
      "autoAssignPort": true
    }
  }
}
```

---

### 技巧 2: 多实例运行

```bash
# 开发环境 - 端口 8080
python -m mcp.server --port 8080 --env development

# 测试环境 - 端口 8081
python -m mcp.server --port 8081 --env testing
```

---

### 技巧 3: 健康检查脚本

创建 `health_check.py`:
```python
import requests
import sys

try:
    response = requests.get("http://localhost:8080/health")
    if response.status_code == 200:
        print("✓ JCode MCP Server is running")
        sys.exit(0)
    else:
        print("✗ JCode MCP Server returned non-200 status")
        sys.exit(1)
except requests.ConnectionError:
    print("✗ JCode MCP Server is not running")
    sys.exit(1)
```

**使用**:
```bash
python health_check.py
# ✓ JCode MCP Server is running
```

---

## 总结

**最佳实践**:

1. **日常开发**: 使用 VSCode 自动启动 (方案 1)
2. **专职开发**: 使用开机自启 + PM2 (方案 2 + 5)
3. **多项目**: 使用 Docker (方案 4)
4. **生产环境**: 使用 PM2 (方案 5)

**一句话**: 配置一次，永久自动运行！

---

**JCode MCP: Set it and forget it.**
