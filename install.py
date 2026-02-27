#!/usr/bin/env python3
"""
JCode OpenCode 安装脚本
将 JCode Agent 系统安装到 OpenCode 全局或项目配置中

Usage:
    python install.py              # 交互式安装
    python install.py --global     # 全局安装
    python install.py --project    # 项目安装
    python install.py --uninstall  # 卸载
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# 颜色输出
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_info(msg): print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")
def print_success(msg): print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")
def print_warning(msg): print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")
def print_error(msg): print(f"{Colors.RED}✗{Colors.RESET} {msg}")
def print_header(): print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}{Colors.RESET}")
def print_title(msg): print(f"{Colors.BOLD}{Colors.MAGENTA}  {msg}{Colors.RESET}")
print_header(); print_title("JCode OpenCode Installer")

# 配置
JCODE_ROOT = Path(__file__).parent.resolve()
OPENCODE_GLOBAL = Path.home() / ".config" / "opencode"
OPENCODE_PROJECT = Path.cwd() / ".opencode"

AGENT_FILES = [
    "jcode.md",  # 主入口Agent
    "jcode-analyst.md",
    "jcode-planner.md", 
    "jcode-implementer.md",
    "jcode-reviewer.md",
    "jcode-tester.md",
    "jcode-conductor.md",
]

MCP_CONFIG = {
    "jcode": {
        "type": "local",
        "command": ["python", "-m", "mcp.server", "--port", "8080"],
        "environment": {
            "PYTHONPATH": str(JCODE_ROOT)
        },
        "enabled": True
    }
}

def get_opencode_config_path(scope: str) -> Path:
    """获取 OpenCode 配置目录路径"""
    if scope == "global":
        return OPENCODE_GLOBAL
    else:
        return OPENCODE_PROJECT

def backup_file(path: Path) -> Path:
    """备份文件"""
    if path.exists():
        backup = path.with_suffix(f".backup.{datetime.now().strftime('%Y%m%d%H%M%S')}")
        shutil.copy2(path, backup)
        return backup
    return None

def install_agents(scope: str) -> int:
    """安装 Agent 配置文件"""
    config_dir = get_opencode_config_path(scope)
    agent_dir = config_dir / "agent"
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    installed = 0
    source_dir = JCODE_ROOT / "config" / "agents"
    
    # 如果源目录不存在，使用默认内容
    if not source_dir.exists():
        source_dir = JCODE_ROOT / ".config" / "opencode" / "agent"
    
    for agent_file in AGENT_FILES:
        target = agent_dir / agent_file
        source = source_dir / agent_file
        
        if source.exists():
            shutil.copy2(source, target)
            installed += 1
            print_success(f"安装 Agent: {agent_file}")
        else:
            # 创建默认 Agent 配置
            create_default_agent(target, agent_file)
            installed += 1
            print_success(f"创建 Agent: {agent_file}")
    
    return installed

def create_default_agent(target: Path, filename: str):
    """创建默认 Agent 配置"""
    agent_name = filename.replace(".md", "").replace("jcode-", "")
    
    descriptions = {
        "analyst": ("问题侦察官", "司马迁", "分析需求、评估风险、判断可验证性"),
        "planner": ("法令制定官", "商鞅", "制定可验证任务、定义验收标准"),
        "implementer": ("执行工匠", "鲁班", "按任务实现代码"),
        "reviewer": ("否决官", "包拯", "代码审查，二元判断 APPROVED/REJECTED"),
        "tester": ("证据官", "张衡", "测试验证，提供可复现证据"),
        "conductor": ("终局裁决", "韩非子", "最终裁决 DELIVER/ITERATE/STOP"),
    }
    
    role, persona, desc = descriptions.get(agent_name, ("Agent", "Unknown", "JCode Agent"))
    
    content = f'''---
mode: subagent
description: |
  JCode {role} ({persona}) - {desc}
  通过 MCP 协议调用 jcode-{agent_name} 工具
tools:
  - read
  - grep
  - glob
  - mcp
mcp_servers:
  - jcode
---

# JCode {agent_name.capitalize()} Agent ({role})

## 人格锚点
{persona}

## 职责
{desc}

## 调用方式

通过 MCP 工具调用：
```json
{{
  "method": "tools/call",
  "params": {{
    "name": "jcode-{agent_name}",
    "arguments": {{
      "context_lock_id": "{{session_id}}",
      "input_data": {{}},
      "mode": "full"
    }}
  }}
}}
```
'''
    
    target.write_text(content, encoding='utf-8')

def install_mcp_config(scope: str) -> bool:
    """安装 MCP 服务器配置"""
    config_dir = get_opencode_config_path(scope)
    config_file = config_dir / "opencode.json"
    
    # 备份现有配置
    if config_file.exists():
        backup_file(config_file)
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}
    
    # 添加 MCP 服务器配置 (使用正确的 key: "mcp")
    if "mcp" not in config:
        config["mcp"] = {}

    config["mcp"]["jcode"] = {
        "type": "local",
        "command": ["python", "-m", "mcp.server", "--port", "8080"],
        "environment": {
            "PYTHONPATH": str(JCODE_ROOT)
        },
        "enabled": True
    }
    
def install_skill(scope: str) -> bool:
    """安装 SKILL.md"""
    config_dir = get_opencode_config_path(scope)
    skill_dir = config_dir / "skills" / "jcode-mcp"
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    source = JCODE_ROOT / "skills" / "jcode-mcp" / "SKILL.md"
    target = skill_dir / "SKILL.md"
    
    if source.exists():
        shutil.copy2(source, target)
        print_success(f"安装 SKILL: {target}")
    else:
        # 创建默认 SKILL.md
        content = '''---
name: jcode-mcp
description: |
  JCode MCP Server - 6 agent governance tools for OpenCode.
  Tools: jcode-analyst, jcode-planner, jcode-implementer, jcode-reviewer, jcode-tester, jcode-conductor
version: "3.0.0"
mcp:
  command: python -m mcp.server
  args: ["--port", "8080"]
---

# JCode MCP Server

JCode v3.0 治理扩展层，提供 6 个 Agent 工具：

| 工具 | 描述 |
|------|------|
| jcode-analyst | 问题分析 |
| jcode-planner | 任务规划 |
| jcode-implementer | 代码实现 |
| jcode-reviewer | 代码审查 |
| jcode-tester | 测试验证 |
| jcode-conductor | 最终裁决 |
'''
        target.write_text(content, encoding='utf-8')
        print_success(f"创建 SKILL: {target}")
    
    return True

def install_workflow(scope: str) -> bool:
    """安装工作流配置"""
    config_dir = get_opencode_config_path(scope)
    workflow_dir = config_dir / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    source = JCODE_ROOT / "workflows" / "jcode-pipeline.yaml"
    target = workflow_dir / "jcode-pipeline.yaml"
    
    if source.exists():
        shutil.copy2(source, target)
        print_success(f"安装工作流: {target}")
    else:
        print_info(f"跳过工作流安装 (源文件不存在)")
    
    return True

def uninstall(scope: str) -> bool:
    """卸载 JCode"""
    config_dir = get_opencode_config_path(scope)
    
    # 移除 Agent 配置
    agent_dir = config_dir / "agent"
    removed_agents = 0
    for agent_file in AGENT_FILES:
        target = agent_dir / agent_file
        if target.exists():
            target.unlink()
            removed_agents += 1
            print_success(f"移除 Agent: {agent_file}")
    
    # 移除 MCP 配置
    config_file = config_dir / "opencode.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if "mcpServers" in config and "jcode" in config["mcpServers"]:
            del config["mcpServers"]["jcode"]
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print_success("移除 MCP 服务器配置")
    
    # 移除 SKILL
    skill_dir = config_dir / "skills" / "jcode-mcp"
    if skill_dir.exists():
        shutil.rmtree(skill_dir)
        print_success("移除 SKILL 目录")
    
    print_info(f"已卸载 {removed_agents} 个 Agent 配置")
    return True

def install(scope: str):
    """执行安装"""
    print_info(f"安装范围: {scope}")
    print_info(f"JCode 目录: {JCODE_ROOT}")
    print_info(f"目标目录: {get_opencode_config_path(scope)}")
    print()
    
    # 1. 安装 Agent 配置
    print_header(); print_title("1. 安装 Agent 配置")
    agents_installed = install_agents(scope)
    print_info(f"已安装 {agents_installed} 个 Agent")
    
    # 2. 安装 MCP 配置
    print_header(); print_title("2. 配置 MCP 服务器")
    install_mcp_config(scope)
    
    # 3. 安装 SKILL
    print_header(); print_title("3. 安装 SKILL")
    install_skill(scope)
    
    # 4. 安装工作流
    print_header(); print_title("4. 安装工作流")
    install_workflow(scope)
    
    # 完成
    print_header()
    print_title("安装完成!")
    print()
    print_success("JCode 已成功安装到 OpenCode")
    print()
    print_info("使用方法:")
    print(f"  {Colors.CYAN}@jcode-analyst{Colors.RESET} 分析需求")
    print(f"  {Colors.CYAN}@jcode-planner{Colors.RESET} 制定任务")
    print(f"  {Colors.CYAN}@jcode-implementer{Colors.RESET} 实现代码")
    print(f"  {Colors.CYAN}@jcode-reviewer{Colors.RESET} 审查代码")
    print(f"  {Colors.CYAN}@jcode-tester{Colors.RESET} 测试验证")
    print(f"  {Colors.CYAN}@jcode-conductor{Colors.RESET} 最终裁决")
    print()
    print_info("启动 MCP 服务器:")
    print(f"  {Colors.YELLOW}python -m mcp.server --port 8080{Colors.RESET}")
    print()
    print_info("重启 OpenCode 以加载新配置")

def interactive_install():
    """交互式安装"""
    print()
    print_info("请选择安装方式:")
    print(f"  {Colors.CYAN}1{Colors.RESET}) 全局安装 (所有项目可用)")
    print(f"  {Colors.CYAN}2{Colors.RESET}) 项目安装 (仅当前项目)")
    print(f"  {Colors.CYAN}3{Colors.RESET}) 卸载全局 JCode")
    print(f"  {Colors.CYAN}4{Colors.RESET}) 卸载项目 JCode")
    print(f"  {Colors.CYAN}q{Colors.RESET}) 退出")
    print()
    
    choice = input(f"{Colors.WHITE}请输入选项 [1-4/q]: {Colors.RESET}").strip().lower()
    
    if choice == "1":
        install("global")
    elif choice == "2":
        install("project")
    elif choice == "3":
        uninstall("global")
    elif choice == "4":
        uninstall("project")
    elif choice == "q":
        print_info("已取消")
    else:
        print_error("无效选项")
        interactive_install()

def main():
    parser = argparse.ArgumentParser(
        description="JCode OpenCode 安装脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python install.py              # 交互式安装
  python install.py --global     # 全局安装
  python install.py --project    # 项目安装
  python install.py --uninstall  # 卸载全局
  python install.py --uninstall --project  # 卸载项目
        """
    )
    parser.add_argument("--global", dest="scope_global", action="store_true",
                        help="全局安装")
    parser.add_argument("--project", action="store_true",
                        help="项目安装")
    parser.add_argument("--uninstall", action="store_true",
                        help="卸载 JCode")
    parser.add_argument("--status", action="store_true",
                        help="查看安装状态")
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.uninstall:
        scope = "project" if args.project else "global"
        uninstall(scope)
    elif args.scope_global:
        install("global")
    elif args.project:
        install("project")
    else:
        interactive_install()

def show_status():
    """显示安装状态"""
    print_header(); print_title("JCode 安装状态")
    print()
    
    # 检查全局安装
    global_agent_dir = OPENCODE_GLOBAL / "agent"
    global_config = OPENCODE_GLOBAL / "opencode.json"
    
    print(f"{Colors.BOLD}全局安装:{Colors.RESET}")
    print(f"  目录: {OPENCODE_GLOBAL}")
    
    global_agents = []
    for agent_file in AGENT_FILES:
        if (global_agent_dir / agent_file).exists():
            global_agents.append(agent_file)
    
    print(f"  Agents: {len(global_agents)}/6")
    
    if global_config.exists():
        with open(global_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        has_jcode = "jcode" in config.get("mcp", {})
        print(f"  MCP: {'已配置' if has_jcode else '未配置'}")
    else:
        print(f"  MCP: 未配置")
    
    print()
    
    # 检查项目安装
    project_agent_dir = OPENCODE_PROJECT / "agent"
    project_config = OPENCODE_PROJECT / "opencode.json"
    
    print(f"{Colors.BOLD}项目安装:{Colors.RESET}")
    print(f"  目录: {OPENCODE_PROJECT}")
    
    project_agents = []
    for agent_file in AGENT_FILES:
        if (project_agent_dir / agent_file).exists():
            project_agents.append(agent_file)
    
    print(f"  Agents: {len(project_agents)}/6")
    
    if project_config.exists():
        with open(project_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        has_jcode = "jcode" in config.get("mcp", {})
        print(f"  MCP: {'已配置' if has_jcode else '未配置'}")
    else:
        print(f"  MCP: 未配置")

if __name__ == "__main__":
    main()
