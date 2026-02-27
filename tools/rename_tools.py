#!/usr/bin/env python3
"""
简化MCP工具名称：去掉 jcode- 和 jcode. 前缀
"""

import re
from pathlib import Path

# 定义工具名称映射
TOOL_NAME_MAPPING = {
    # 从旧名称到新名称
    "jcode.analyze": "analyze",
    "jcode.plan": "plan",
    "jcode.implement": "implement",
    "jcode.review": "review",
    "jcode.test": "test",
    "jcode.conductor": "conductor",
    "jcode-analyst": "analyze",
    "jcode-planner": "plan",
    "jcode-implementer": "implement",
    "jcode-reviewer": "review",
    "jcode-tester": "test",
    "jcode-conductor": "conductor",
}

def update_jcode_server():
    """更新 jcode_server.py 中的工具名称"""
    file_path = Path("C:/dev_projects/jcode/mcp/jcode_server.py")
    content = file_path.read_text(encoding='utf-8')
    
    # 替换工具名称
    for old_name, new_name in TOOL_NAME_MAPPING.items():
        if old_name.startswith("jcode."):
            content = content.replace(f'"name": "{old_name}"', f'"name": "{new_name}"')
    
    file_path.write_text(content, encoding='utf-8')
    print("✓ Updated jcode_server.py")

def update_server():
    """更新 server.py 中的工具名称"""
    file_path = Path("C:/dev_projects/jcode/mcp/server.py")
    content = file_path.read_text(encoding='utf-8')
    
    # 替换工具名称检查
    for old_name, new_name in TOOL_NAME_MAPPING.items():
        if "-" in old_name:  # 处理 jcode-analyst 格式
            content = content.replace(f'tool_name == "{old_name}"', f'tool_name == "{new_name}"')
            content = content.replace(f'# Handle {old_name} tool', f'# Handle {new_name} tool')
    
    file_path.write_text(content, encoding='utf-8')
    print("✓ Updated server.py")

def update_skill_md():
    """更新 SKILL.md 中的工具名称"""
    file_path = Path("C:/dev_projects/jcode/skills/jcode-mcp/SKILL.md")
    content = file_path.read_text(encoding='utf-8')
    
    # 替换工具名称
    content = content.replace("jcode-analyst", "analyze")
    content = content.replace("jcode-planner", "plan")
    content = content.replace("jcode-implementer", "implement")
    content = content.replace("jcode-reviewer", "review")
    content = content.replace("jcode-tester", "test")
    content = content.replace("jcode-conductor", "conductor")
    
    # 更新 name 字段
    content = content.replace("name: jcode-analyst", "name: analyze")
    content = content.replace("name: jcode-planner", "name: plan")
    content = content.replace("name: jcode-implementer", "name: implement")
    content = content.replace("name: jcode-reviewer", "name: review")
    content = content.replace("name: jcode-tester", "name: test")
    content = content.replace("name: jcode-conductor", "name: conductor")
    
    file_path.write_text(content, encoding='utf-8')
    print("✓ Updated SKILL.md")

if __name__ == "__main__":
    update_jcode_server()
    update_server()
    update_skill_md()
    print("\n✅ All tool names simplified!")
    print("\nNew command format:")
    print("  /jcode-mcp analyze '需求分析'")
    print("  /jcode-mcp plan '制定任务'")
    print("  /jcode-mcp implement '实现代码'")
    print("  /jcode-mcp review '代码审查'")
    print("  /jcode-mcp test '测试验证'")
    print("  /jcode-mcp conductor '终局裁决'")
