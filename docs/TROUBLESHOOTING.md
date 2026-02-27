# JCode OpenCode 安装问题排查

## 问题："Invalid input mcp.jcode" 或 "Unrecognized key: mcpServers"

### 原因

OpenCode 的 MCP 配置格式与标准 MCP 客户端有所不同：

1. **使用 `"mcp"` 而不是 `"mcpServers"`**
2. **不支持 `"cwd"` 属性** - 这会导致配置验证失败

### 正确配置格式

```json
{
  "mcp": {
    "jcode": {
      "type": "local",
      "command": ["python", "-m", "mcp.server", "--port", "8080"],
      "environment": {
        "PYTHONPATH": "C:/dev_projects/jcode"
      },
      "enabled": true
    }
  }
}
```

### 错误配置示例

```json
{
  "mcpServers": {  // ❌ 错误：应该使用 "mcp"
    "jcode": {
      "type": "local",
      "command": ["python", "-m", "mcp.server", "--port", "8080"],
      "cwd": "C:/dev_projects/jcode",  // ❌ 错误：不支持 cwd
      "environment": {},
      "enabled": true
    }
  }
}
```

### 解决方案

由于 OpenCode 不支持 `cwd`，我们使用 `PYTHONPATH` 环境变量来告诉 Python 在哪里找到 JCode 模块：

```json
"environment": {
  "PYTHONPATH": "C:/dev_projects/jcode"
}
```

### 验证配置

```bash
# 检查 OpenCode 是否能正常启动
opencode --version

# 应该输出版本号，没有错误
```

### 如果仍然报错

1. **检查是否有残留的 `mcpServers` 键**：
   ```bash
   grep "mcpServers" ~/.config/opencode/opencode.json
   ```
   如果有输出，需要删除 `mcpServers` 对象。

2. **检查配置格式**：
   ```bash
   # 验证 JSON 格式
   python -c "import json; json.load(open('$HOME/.config/opencode/opencode.json'))"
   ```

3. **临时移除 jcode 配置测试**：
   ```bash
   # 备份配置
   cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.backup
   
   # 移除 jcode 后测试
   opencode --version
   ```

### 手动修复步骤

如果安装脚本导致配置损坏，可以手动修复：

```bash
# 1. 备份当前配置
cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.backup.$(date +%Y%m%d%H%M%S)

# 2. 编辑配置文件，删除 "mcpServers" 键和 "jcode" 的 "cwd" 属性
# 使用你喜欢的编辑器
nano ~/.config/opencode/opencode.json

# 3. 确保只有 "mcp" 键，且格式正确

# 4. 测试
opencode --version
```

### 相关文档

- [OpenCode Configuration Schema](https://opencode.ai/config.json)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
