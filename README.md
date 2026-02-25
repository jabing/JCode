# JCode v3.0 - OpenCode/Superpowers Governance Extension Layer

## Overview

JCode is a code governance system for OpenCode that implements a 6-agent workflow with 4-level switch mechanism.

## Features

- **6 JCode Agents**: Analyst, Planner, Implementer, Reviewer, Tester, Conductor
- **4-Level Switch**: Global, Mode, Agent, Rule
- **5 Execution Modes**: full, light, safe, fast, custom
- **REST API**: FastAPI-based endpoints
- **CLI**: Click-based command-line interface
- **Audit Logging**: JSON Lines format with integrity verification

## Project Structure

```
jcode/
├── core/               # Core modules
│   ├── switch_manager.py   # 4-level switch mechanism
│   ├── audit_logger.py     # Audit logging
│   ├── rule_engine.py      # Rule execution
│   ├── context_lock.py     # Context locking
│   ├── incremental_build.py # Incremental build
│   ├── mcp_client.py       # MCP protocol client
│   └── agent_manager.py    # Agent lifecycle
├── api/                # REST API
│   ├── main.py             # FastAPI application
│   ├── routes/             # API endpoints
│   └── models/             # Pydantic models
├── cli/                # Command-line interface
│   ├── commands.py         # CLI commands
│   └── config.py           # Configuration management
├── config/             # Configuration files
│   └── jcode_config.yaml   # Default configuration
├── tests/              # Test suite
└── governance/         # Governance documentation
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Start API Server
```bash
python -m api.main
# or
uvicorn api.main:app --reload
```

### Use CLI
```bash
python cli/commands.py --help
python cli/commands.py show
python cli/commands.py enable
python cli/commands.py mode safe
```

### Run Tests
```bash
python -m pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /api/v1/config | Get configuration |
| POST | /api/v1/config/enable | Enable JCode |
| POST | /api/v1/config/disable | Disable JCode |
| POST | /api/v1/jcode/analyze | Analyst agent |
| POST | /api/v1/jcode/plan | Planner agent |
| POST | /api/v1/jcode/implement | Implementer agent |
| POST | /api/v1/jcode/review | Reviewer agent |
| POST | /api/v1/jcode/test | Tester agent |
| POST | /api/v1/jcode/conductor | Conductor agent |

## CLI Commands

| Command | Description |
|---------|-------------|
| jcode show | Show current configuration |
| jcode enable | Enable JCode |
| jcode disable | Disable JCode |
| jcode mode <mode> | Set execution mode |
| jcode agent <enable/disable> <name> | Enable/disable agent |
| jcode analyze | Run analyst agent |

## Configuration

See `config/jcode_config.yaml` for default configuration.

## License

MIT

## Overview

JCode is a code governance system for OpenCode that implements a 6-agent workflow with 4-level switch mechanism.

## Features

- **6 JCode Agents**: Analyst, Planner, Implementer, Reviewer, Tester, Conductor
- **4-Level Switch**: Global, Mode, Agent, Rule
- **5 Execution Modes**: full, light, safe, fast, custom
- **REST API**: FastAPI-based endpoints
- **CLI**: Click-based command-line interface
- **Audit Logging**: JSON Lines format with integrity verification

## Project Structure

```
jcode/
├── core/               # Core modules
│   ├── switch_manager.py   # 4-level switch mechanism
│   ├── audit_logger.py     # Audit logging
│   ├── rule_engine.py      # Rule execution
│   ├── context_lock.py     # Context locking
│   ├── incremental_build.py # Incremental build
│   ├── mcp_client.py       # MCP protocol client
│   └── agent_manager.py    # Agent lifecycle
├── api/                # REST API
│   ├── main.py             # FastAPI application
│   ├── routes/             # API endpoints
│   └── models/             # Pydantic models
├── cli/                # Command-line interface
│   ├── commands.py         # CLI commands
│   └── config.py           # Configuration management
├── config/             # Configuration files
│   └── jcode_config.yaml   # Default configuration
├── tests/              # Test suite
└── governance/         # Governance documentation
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Start API Server
```bash
python -m api.main
# or
uvicorn api.main:app --reload
```

### Use CLI
```bash
python cli/commands.py --help
python cli/commands.py show
python cli/commands.py enable
python cli/commands.py mode safe
```

### Run Tests
```bash
python -m pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /api/v1/config | Get configuration |
| POST | /api/v1/config/enable | Enable JCode |
| POST | /api/v1/config/disable | Disable JCode |
| POST | /api/v1/jcode/analyze | Analyst agent |
| POST | /api/v1/jcode/plan | Planner agent |
| POST | /api/v1/jcode/implement | Implementer agent |
| POST | /api/v1/jcode/review | Reviewer agent |
| POST | /api/v1/jcode/test | Tester agent |
| POST | /api/v1/jcode/conductor | Conductor agent |

## CLI Commands

| Command | Description |
|---------|-------------|
| jcode show | Show current configuration |
| jcode enable | Enable JCode |
| jcode disable | Disable JCode |
| jcode mode <mode> | Set execution mode |
| jcode agent <enable/disable> <name> | Enable/disable agent |
| jcode analyze | Run analyst agent |

## Configuration

See `config/jcode_config.yaml` for default configuration.

## License

MIT
