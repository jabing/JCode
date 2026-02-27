#!/bin/bash
# JCode OpenCode 安装脚本 (Unix/Linux/macOS)
# Usage: ./install.sh [--global|--project|--uninstall|--status]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# 路径
JCODE_ROOT="$(cd "$(dirname "$0")" && pwd)"
OPENCODE_GLOBAL="$HOME/.config/opencode"
OPENCODE_PROJECT="$(pwd)/.opencode"

# Agent 文件列表
AGENT_FILES=(
    "jcode-analyst.md"
    "jcode-planner.md"
    "jcode-implementer.md"
    "jcode-reviewer.md"
    "jcode-tester.md"
    "jcode-conductor.md"
)

# 打印函数
print_info() { echo -e "${BLUE}ℹ${RESET} $1"; }
print_success() { echo -e "${GREEN}✓${RESET} $1"; }
print_warning() { echo -e "${YELLOW}⚠${RESET} $1"; }
print_error() { echo -e "${RED}✗${RESET} $1"; }
print_header() { echo -e "\n${BOLD}${CYAN}$(printf '=%.0s' {1..50})${RESET}"; }
print_title() { echo -e "${BOLD}${PURPLE}  $1${RESET}"; }

# 显示帮助
show_help() {
    echo "JCode OpenCode 安装脚本"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --global      全局安装到 ~/.config/opencode"
    echo "  --project     项目安装到 ./.opencode"
    echo "  --uninstall   卸载 JCode"
    echo "  --status      查看安装状态"
    echo "  -h, --help    显示此帮助"
    echo ""
    echo "Examples:"
    echo "  $0                    # 交互式安装"
    echo "  $0 --global           # 全局安装"
    echo "  $0 --project          # 项目安装"
    echo "  $0 --uninstall        # 卸载全局"
    exit 0
}

# 安装 Agent 配置
install_agents() {
    local scope=$1
    local config_dir
    
    if [ "$scope" = "global" ]; then
        config_dir="$OPENCODE_GLOBAL"
    else
        config_dir="$OPENCODE_PROJECT"
    fi
    
    local agent_dir="$config_dir/agent"
    mkdir -p "$agent_dir"
    
    local source_dir="$JCODE_ROOT/config/agents"
    if [ ! -d "$source_dir" ]; then
        source_dir="$JCODE_ROOT/.config/opencode/agent"
    fi
    
    local installed=0
    
    for agent_file in "${AGENT_FILES[@]}"; do
        local source="$source_dir/$agent_file"
        local target="$agent_dir/$agent_file"
        
        if [ -f "$source" ]; then
            cp "$source" "$target"
            print_success "安装 Agent: $agent_file"
            ((installed++))
        else
            # 创建默认 Agent
            create_default_agent "$target" "$agent_file"
            print_success "创建 Agent: $agent_file"
            ((installed++))
        fi
    done
    
    return $installed
}

# 创建默认 Agent 配置
create_default_agent() {
    local target=$1
    local filename=$2
    local agent_name="${filename%.md}"
    agent_name="${agent_name#jcode-}"
    
    local role persona desc
    
    case "$agent_name" in
        analyst)
            role="问题侦察官"; persona="司马迁"
            desc="分析需求、评估风险、判断可验证性"
            ;;
        planner)
            role="法令制定官"; persona="商鞅"
            desc="制定可验证任务、定义验收标准"
            ;;
        implementer)
            role="执行工匠"; persona="鲁班"
            desc="按任务实现代码"
            ;;
        reviewer)
            role="否决官"; persona="包拯"
            desc="代码审查，二元判断 APPROVED/REJECTED"
            ;;
        tester)
            role="证据官"; persona="张衡"
            desc="测试验证，提供可复现证据"
            ;;
        conductor)
            role="终局裁决"; persona="韩非子"
            desc="最终裁决 DELIVER/ITERATE/STOP"
            ;;
    esac
    
    cat > "$target" << EOF
---
mode: subagent
description: |
  JCode $role ($persona) - $desc
  通过 MCP 协议调用 jcode-$agent_name 工具
tools:
  - read
  - grep
  - glob
  - mcp
mcp_servers:
  - jcode
---

# JCode ${agent_name^} Agent ($role)

## 人格锚点
$persona

## 职责
$desc

## 调用方式

通过 MCP 工具调用：
\`\`\`json
{
  "method": "tools/call",
  "params": {
    "name": "jcode-$agent_name",
    "arguments": {
      "context_lock_id": "{session_id}",
      "input_data": {},
      "mode": "full"
    }
  }
}
\`\`\`
EOF
}

# 安装 MCP 配置
install_mcp_config() {
    local scope=$1
    local config_dir
    
    if [ "$scope" = "global" ]; then
        config_dir="$OPENCODE_GLOBAL"
    else
        config_dir="$OPENCODE_PROJECT"
    fi
    
    local config_file="$config_dir/opencode.json"
    
    mkdir -p "$config_dir"
    
    # 备份现有配置
    if [ -f "$config_file" ]; then
        cp "$config_file" "$config_file.backup.$(date +%Y%m%d%H%M%S)"
    fi
    
    # 使用 Python 处理 JSON（更可靠）
    python3 - "$JCODE_ROOT" "$config_file" << 'PYTHON'
import sys
import json
from pathlib import Path

jcode_root = sys.argv[1]
config_file = Path(sys.argv[2])

if config_file.exists():
    with open(config_file) as f:
        config = json.load(f)
else:
    config = {}

if "mcpServers" not in config:
    config["mcpServers"] = {}

config["mcpServers"]["jcode"] = {
    "command": "python",
    "args": ["-m", "mcp.server", "--port", "8080"],
    "cwd": jcode_root,
    "env": {},
    "disabled": False
}

config_file.parent.mkdir(parents=True, exist_ok=True)
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"配置 MCP 服务器: {config_file}")
PYTHON

    print_success "配置 MCP 服务器: $config_file"
}

# 安装 SKILL
install_skill() {
    local scope=$1
    local config_dir
    
    if [ "$scope" = "global" ]; then
        config_dir="$OPENCODE_GLOBAL"
    else
        config_dir="$OPENCODE_PROJECT"
    fi
    
    local skill_dir="$config_dir/skills/jcode-mcp"
    mkdir -p "$skill_dir"
    
    local source="$JCODE_ROOT/skills/jcode-mcp/SKILL.md"
    local target="$skill_dir/SKILL.md"
    
    if [ -f "$source" ]; then
        cp "$source" "$target"
        print_success "安装 SKILL: $target"
    else
        # 创建默认 SKILL
        cat > "$target" << 'EOF'
---
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

JCode v3.0 治理扩展层，提供 6 个 Agent 工具
EOF
        print_success "创建 SKILL: $target"
    fi
}

# 卸载
do_uninstall() {
    local scope=$1
    local config_dir
    
    if [ "$scope" = "global" ]; then
        config_dir="$OPENCODE_GLOBAL"
    else
        config_dir="$OPENCODE_PROJECT"
    fi
    
    # 移除 Agent 配置
    local agent_dir="$config_dir/agent"
    local removed=0
    
    for agent_file in "${AGENT_FILES[@]}"; do
        local target="$agent_dir/$agent_file"
        if [ -f "$target" ]; then
            rm "$target"
            print_success "移除 Agent: $agent_file"
            ((removed++))
        fi
    done
    
    # 移除 MCP 配置
    local config_file="$config_dir/opencode.json"
    if [ -f "$config_file" ]; then
        python3 - "$config_file" << 'PYTHON'
import sys
import json
from pathlib import Path

config_file = Path(sys.argv[1])

with open(config_file) as f:
    config = json.load(f)

if "mcpServers" in config and "jcode" in config["mcpServers"]:
    del config["mcpServers"]["jcode"]
    
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("移除 MCP 配置")
PYTHON
        print_success "移除 MCP 服务器配置"
    fi
    
    # 移除 SKILL
    local skill_dir="$config_dir/skills/jcode-mcp"
    if [ -d "$skill_dir" ]; then
        rm -rf "$skill_dir"
        print_success "移除 SKILL 目录"
    fi
    
    print_info "已卸载 $removed 个 Agent 配置"
}

# 执行安装
do_install() {
    local scope=$1
    
    print_info "安装范围: $scope"
    print_info "JCode 目录: $JCODE_ROOT"
    
    if [ "$scope" = "global" ]; then
        print_info "目标目录: $OPENCODE_GLOBAL"
    else
        print_info "目标目录: $OPENCODE_PROJECT"
    fi
    
    echo ""
    
    print_header; print_title "1. 安装 Agent 配置"
    install_agents "$scope"
    
    print_header; print_title "2. 配置 MCP 服务器"
    install_mcp_config "$scope"
    
    print_header; print_title "3. 安装 SKILL"
    install_skill "$scope"
    
    print_header; print_title "安装完成!"
    echo ""
    print_success "JCode 已成功安装到 OpenCode"
    echo ""
    print_info "使用方法:"
    echo -e "  ${CYAN}@jcode-analyst${RESET} 分析需求"
    echo -e "  ${CYAN}@jcode-planner${RESET} 制定任务"
    echo -e "  ${CYAN}@jcode-implementer${RESET} 实现代码"
    echo -e "  ${CYAN}@jcode-reviewer${RESET} 审查代码"
    echo -e "  ${CYAN}@jcode-tester${RESET} 测试验证"
    echo -e "  ${CYAN}@jcode-conductor${RESET} 最终裁决"
    echo ""
    print_info "启动 MCP 服务器:"
    echo -e "  ${YELLOW}python -m mcp.server --port 8080${RESET}"
    echo ""
    print_info "重启 OpenCode 以加载新配置"
}

# 显示状态
show_status() {
    print_header; print_title "JCode 安装状态"
    echo ""
    
    echo -e "${BOLD}全局安装:${RESET}"
    echo "  目录: $OPENCODE_GLOBAL"
    
    local global_count=0
    for agent_file in "${AGENT_FILES[@]}"; do
        if [ -f "$OPENCODE_GLOBAL/agent/$agent_file" ]; then
            ((global_count++))
        fi
    done
    echo "  Agents: $global_count/6"
    
    echo ""
    echo -e "${BOLD}项目安装:${RESET}"
    echo "  目录: $OPENCODE_PROJECT"
    
    local project_count=0
    for agent_file in "${AGENT_FILES[@]}"; do
        if [ -f "$OPENCODE_PROJECT/agent/$agent_file" ]; then
            ((project_count++))
        fi
    done
    echo "  Agents: $project_count/6"
}

# 交互式安装
interactive() {
    echo ""
    print_info "请选择安装方式:"
    echo -e "  ${CYAN}1${RESET}) 全局安装 (所有项目可用)"
    echo -e "  ${CYAN}2${RESET}) 项目安装 (仅当前项目)"
    echo -e "  ${CYAN}3${RESET}) 卸载全局 JCode"
    echo -e "  ${CYAN}4${RESET}) 卸载项目 JCode"
    echo -e "  ${CYAN}q${RESET}) 退出"
    echo ""
    
    read -p "请输入选项 [1-4/q]: " choice
    
    case "$choice" in
        1) do_install "global" ;;
        2) do_install "project" ;;
        3) do_uninstall "global" ;;
        4) do_uninstall "project" ;;
        q) print_info "已取消" ;;
        *) print_error "无效选项"; interactive ;;
    esac
}

# 主函数
main() {
    local scope=""
    local action="install"
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --global) scope="global" ;;
            --project) scope="project" ;;
            --uninstall) action="uninstall" ;;
            --status) action="status" ;;
            -h|--help) show_help ;;
        esac
        shift
    done
    
    case "$action" in
        install)
            if [ -n "$scope" ]; then
                do_install "$scope"
            else
                interactive
            fi
            ;;
        uninstall)
            if [ -z "$scope" ]; then
                scope="global"
            fi
            do_uninstall "$scope"
            ;;
        status)
            show_status
            ;;
    esac
}

main "$@"
