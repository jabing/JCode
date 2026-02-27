#!/usr/bin/env python3
"""
JCode OpenCode 卸载脚本
从 OpenCode 全局或项目配置中移除 JCode

Usage:
    python uninstall.py              # 交互式卸载
    python uninstall.py --global     # 卸载全局
    python uninstall.py --project    # 卸载项目
    python uninstall.py --all        # 卸载全部
"""

import os
import sys
import json
import shutil
from pathlib import Path

# 颜色输出
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_info(msg): print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")
def print_success(msg): print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")
def print_warning(msg): print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")
def print_error(msg): print(f"{Colors.RED}✗{Colors.RESET} {msg}")

OPENCODE_GLOBAL = Path.home() / ".config" / "opencode"
OPENCODE_PROJECT = Path.cwd() / ".opencode"

AGENT_FILES = [
    "jcode-analyst.md",
    "jcode-planner.md",
    "jcode-implementer.md",
    "jcode-reviewer.md",
    "jcode-tester.md",
    "jcode-conductor.md",
]

def uninstall_scope(scope: str) -> dict:
    """卸载指定范围的 JCode"""
    if scope == "global":
        config_dir = OPENCODE_GLOBAL
    else:
        config_dir = OPENCODE_PROJECT
    
    result = {
        "agents_removed": 0,
        "mcp_removed": False,
        "skill_removed": False,
        "errors": []
    }
    
    print_info(f"卸载范围: {scope} ({config_dir})")
    
    # 1. 移除 Agent 配置
    agent_dir = config_dir / "agent"
    for agent_file in AGENT_FILES:
        target = agent_dir / agent_file
        if target.exists():
            try:
                target.unlink()
                result["agents_removed"] += 1
                print_success(f"移除 Agent: {agent_file}")
            except Exception as e:
                result["errors"].append(f"移除 {agent_file} 失败: {e}")
                print_error(f"移除失败: {agent_file}")
    
    # 2. 移除 MCP 配置
    config_file = config_dir / "opencode.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if "mcp" in config and "jcode" in config["mcp"]:
                del config["mcp"]["jcode"]
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                result["mcp_removed"] = True
                print_success("移除 MCP 服务器配置")
        except Exception as e:
            result["errors"].append(f"移除 MCP 配置失败: {e}")
            print_error(f"移除 MCP 配置失败: {e}")
    
    # 3. 移除 SKILL
    skill_dir = config_dir / "skills" / "jcode-mcp"
    if skill_dir.exists():
        try:
            shutil.rmtree(skill_dir)
            result["skill_removed"] = True
            print_success("移除 SKILL 目录")
        except Exception as e:
            result["errors"].append(f"移除 SKILL 失败: {e}")
            print_error(f"移除 SKILL 失败: {e}")
    
    # 4. 移除工作流
    workflow_file = config_dir / "workflows" / "jcode-pipeline.yaml"
    if workflow_file.exists():
        try:
            workflow_file.unlink()
            print_success("移除工作流配置")
        except Exception as e:
            pass  # 静默失败
    
    return result

def uninstall_all():
    """卸载全部"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}卸载 JCode{Colors.RESET}\n")
    
    # 全局
    print(f"{Colors.YELLOW}>>> 卸载全局配置{Colors.RESET}")
    global_result = uninstall_scope("global")
    
    print()
    
    # 项目
    print(f"{Colors.YELLOW}>>> 卸载项目配置{Colors.RESET}")
    project_result = uninstall_scope("project")
    
    # 汇总
    print(f"\n{Colors.BOLD}卸载完成{Colors.RESET}")
    print(f"  全局 Agents: {global_result['agents_removed']}/6")
    print(f"  项目 Agents: {project_result['agents_removed']}/6")
    print(f"  MCP 配置: {'已移除' if global_result['mcp_removed'] or project_result['mcp_removed'] else '无'}")
    print(f"  SKILL: {'已移除' if global_result['skill_removed'] or project_result['skill_removed'] else '无'}")
    
    if global_result['errors'] or project_result['errors']:
        print(f"\n{Colors.YELLOW}警告:{Colors.RESET}")
        for err in global_result['errors'] + project_result['errors']:
            print(f"  - {err}")

def interactive():
    """交互式卸载"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}JCode 卸载工具{Colors.RESET}\n")
    print_info("请选择卸载范围:")
    print(f"  {Colors.CYAN}1{Colors.RESET}) 仅全局")
    print(f"  {Colors.CYAN}2{Colors.RESET}) 仅项目")
    print(f"  {Colors.CYAN}3{Colors.RESET}) 全部")
    print(f"  {Colors.CYAN}q{Colors.RESET}) 取消")
    print()
    
    choice = input(f"{Colors.BLUE}请输入选项: {Colors.RESET}").strip().lower()
    
    if choice == "1":
        print()
        uninstall_scope("global")
    elif choice == "2":
        print()
        uninstall_scope("project")
    elif choice == "3":
        uninstall_all()
    elif choice == "q":
        print_info("已取消")
    else:
        print_error("无效选项")
        interactive()

def main():
    if len(sys.argv) == 1:
        interactive()
        return
    
    arg = sys.argv[1]
    
    if arg == "--global":
        uninstall_scope("global")
    elif arg == "--project":
        uninstall_scope("project")
    elif arg == "--all":
        uninstall_all()
    elif arg in ["-h", "--help"]:
        print("Usage: python uninstall.py [--global|--project|--all]")
    else:
        print_error(f"未知参数: {arg}")

if __name__ == "__main__":
    main()
