# JCode v3.0 - MCP-Based Agent Governance System

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-Protocol-orange.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**JCode** is a 6-step governance workflow system for AI coding assistants, exposed via the Model Context Protocol (MCP). It brings structure, accountability, and quality control to AI-generated code.

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Installation](#installation)

---

## 🎯 What is JCode?

JCode implements a complete governance layer that ensures AI-generated code meets quality standards through a structured 6-step workflow:

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   Analyst   │ → │   Planner   │ → │ Implementer │
│  (司马迁)   │   │   (商鞅)    │   │   (鲁班)    │
└─────────────┘   └─────────────┘   └─────────────┘
                                              ↓
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Conductor  │ ← │    Tester   │ ← │   Reviewer  │
│  (韩非子)   │   │   (张衡)    │   │   (包拯)    │
└─────────────┘   └─────────────┘   └─────────────┘
```

Each step validates the previous, ensuring only high-quality code reaches production.

---

## ✨ Features

### 6 Specialized Agents

| Agent | Role | Output |
|-------|------|--------|
| **@jcode-analyst** | Problem analysis & risk assessment | Analysis + Verifiability |
| **@jcode-planner** | Task decomposition & planning | Verifiable task list |
| **@jcode-implementer** | Code implementation | Code changes |
| **@jcode-reviewer** | Code review | APPROVED / REJECTED |
| **@jcode-tester** | Test verification | PASSED / FAILED |
| **@jcode-conductor** | Final arbitration | DELIVER / ITERATE / STOP |

### MCP Protocol Integration

- **Standard Protocol**: Implements [Model Context Protocol](https://modelcontextprotocol.io/) (JSON-RPC 2.0)
- **Tool Discovery**: Auto-discoverable by MCP clients
- **Stateless Design**: Each invocation is independent
- **Multi-Client Support**: Works with OpenCode, VSCode, Claude Desktop, etc.

### Auto-Start Options

- ✅ VSCode auto-start on project open
- ✅ System service (systemd/launchd)
- ✅ Docker container
- ✅ PM2 process management

---

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/jabing/JCode.git
cd JCode
pip install -r requirements.txt
```

### 2. Configure OpenCode (or your MCP client)

Edit `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "jcode": {
      "type": "local",
      "command": ["python", "-m", "jcode_mcp.server", "--port", "8080"],
      "env": {"PYTHONPATH": "/path/to/jcode"},
      "enabled": true
    }
  }
}
```

### 3. Use JCode

In your MCP client:

```
@jcode 实现一个用户登录功能
```

Or use individual agents:

```
@jcode-analyst 分析这个需求的风险
@jcode-reviewer 检查这段代码
@jcode-tester 运行测试
```

---

## 📚 Documentation

### Core Documentation

- [📖 Agent System Overview](agents/AGENTS.md) - Architecture & 6-agent workflow
- [🔧 Installation Guide](docs/INSTALLATION.md) - Detailed setup instructions
- [⚙️ VSCode Integration](docs/VSCODE_INTEGRATION.md) - VSCode setup & configuration
- [🚀 Auto-Start Guide](docs/AUTO_START_GUIDE.md) - 5 methods to auto-start server
- [🛠️ Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues & solutions

### Governance Framework

- [📜 Agent Constitution](governance/AGENT_CONSTITUTION.md) - Core principles & constraints
- [🏛️ Governance Documentation](governance/) - Complete governance framework
- [📋 Output Format Guidelines](governance/OUTPUT_FORMAT_GUIDELINES.md)

### API Reference

- [💻 MCP Server API](jcode_mcp/server.py) - FastAPI-based MCP server
- [🔌 SKILL Registration](skills/jcode-mcp/SKILL.md) - OpenCode SKILL format

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  MCP Client                          │
│         (OpenCode / VSCode / Claude)                 │
└────────────────────┬────────────────────────────────┘
                     │ JSON-RPC 2.0
                     ▼
┌─────────────────────────────────────────────────────┐
│              JCode MCP Server                        │
│  ┌──────────┬──────────┬──────────┬───────────────┐  │
│  │ /health  │  /mcp    │ /docs    │   /openapi    │  │
│  └──────────┴──────────┴──────────┴───────────────┘  │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │
│  │  analyze │ │   plan   │ │ implement│ │ review │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘  │
│  ┌──────────┐ ┌──────────┐                          │
│  │   test   │ │ conductor│                          │
│  └──────────┘ └──────────┘                          │
└─────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│               Core Agents                            │
│   Analyst / Planner / Implementer / Reviewer /      │
│   Tester / Conductor                                │
└─────────────────────────────────────────────────────┘
```

---

## 🎨 Agent Personalities

Each JCode agent has a historical Chinese personality anchor that constrains its behavior:

| Agent | Personality | Constraint |
|-------|-------------|------------|
| **Analyst** | 司马迁 (Sima Qian) | Records facts only, no judgment |
| **Planner** | 商鞅 (Shang Yang) | Creates laws, doesn't execute |
| **Implementer** | 鲁班 (Lu Ban) | Follows blueprint exactly |
| **Reviewer** | 包拯 (Bao Zheng) | Binary verdict only, no suggestions |
| **Tester** | 张衡 (Zhang Heng) | Provides evidence, no speculation |
| **Conductor** | 韩非子 (Han Feizi) | Final arbiter, no analysis |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run integration tests
pytest tests/integration/test_mcp_server.py -v

# Run with coverage
pytest tests/ --cov=jcode_mcp --cov-report=html
```

---

## 📦 Project Structure

```
jcode/
├── jcode_mcp/              # MCP Server implementation
│   ├── server.py           # FastAPI + JSON-RPC 2.0
│   ├── jcode_server.py     # Tool definitions
│   └── __init__.py
├── core/agents/            # 6 Agent implementations
│   ├── analyst.py
│   ├── planner.py
│   ├── implementer.py
│   ├── reviewer.py
│   ├── tester.py
│   └── conductor.py
├── config/agents/          # OpenCode Agent configs
│   ├── jcode.md            # Primary orchestrator
│   ├── jcode-analyst.md
│   ├── jcode-planner.md
│   ├── jcode-implementer.md
│   ├── jcode-reviewer.md
│   ├── jcode-tester.md
│   └── jcode-conductor.md
├── skills/jcode-mcp/       # OpenCode SKILL registration
│   └── SKILL.md
├── docs/                   # Documentation
│   ├── AUTO_START_GUIDE.md
│   ├── VSCODE_INTEGRATION.md
│   └── TROUBLESHOOTING.md
├── governance/             # Governance framework
│   ├── AGENT_CONSTITUTION.md
│   └── ...
└── tests/                  # Test suite
    └── integration/
```

---

## 🛣️ Roadmap

- [x] MCP Server implementation
- [x] 6 Agent tools exposed via MCP
- [x] VSCode integration
- [x] Auto-start configuration
- [ ] Web dashboard for workflow monitoring
- [ ] Multi-project support
- [ ] Custom agent plugins
- [ ] Enterprise SSO integration

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run linting
ruff check .
black --check .

# Run tests
pytest
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) - For the standardized tool protocol
- [OpenCode](https://opencode.ai/) - For the AI coding assistant framework
- [FastAPI](https://fastapi.tiangolo.com/) - For the high-performance web framework

---

## 📞 Support

- 📚 [Documentation](docs/)
- 🐛 [Issues](https://github.com/jabing/JCode/issues)
- 💬 [Discussions](https://github.com/jabing/JCode/discussions)

---

<p align="center">
  <b>JCode: Governance as a Tool</b><br>
  <i>让AI不只是写代码，而是写好代码</i>
</p>
