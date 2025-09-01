#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键修复 ruff 代码质量问题的脚本
"""

import re
import subprocess
from pathlib import Path


def run_ruff_with_unsafe_fixes():
    """运行 ruff 自动修复（包括不安全修复）"""
    try:
        result = subprocess.run(
            ['ruff', 'check', '.', '--fix', '--unsafe-fixes'],
            capture_output=True, text=True, cwd=Path.cwd()
        )
        print("🔧 Ruff 自动修复完成")
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ ruff 未安装")
        return False


def fix_specific_issues(file_path: Path, content: str) -> str:
    """修复特定的代码质量问题"""

    # 1. 修复 __init__ 函数名问题 (N807)
    if 'decorators.py' in str(file_path):
        content = content.replace(
            'def __init__(self, *args, **kwargs):',
            'def __init_wrapper__(self, *args, **kwargs):'
        )

    # 2. 修复未使用的循环变量 (B007)
    content = re.sub(r'for category, node_types in', r'for _category, node_types in', content)

    # 3. 修复未使用的变量 (F841)
    content = re.sub(r'converted_value = self\.data_type\(value\)', r'self.data_type(value)', content)
    content = re.sub(r'node_type = _require_str', r'_node_type = _require_str', content)

    # 4. 修复前向引用问题 (F821)
    if 'node_types.py' in str(file_path):
        content = content.replace(
            'NodeClassType = Type["BaseNode"]',
            'from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from bluev.core.base_node import BaseNode\nNodeClassType = Type["BaseNode"]'
        )

    # 5. 修复 ExecutionContext 前向引用
    if 'async def execute(self, context: "ExecutionContext")' in content:
        if 'from typing import TYPE_CHECKING' not in content:
            content = 'from typing import TYPE_CHECKING\n' + content
        if 'if TYPE_CHECKING:' not in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'from bluev.core' in line:
                    lines.insert(i, 'if TYPE_CHECKING:')
                    lines.insert(i+1, '    from bluev.core.execution_context import ExecutionContext')
                    break
            content = '\n'.join(lines)

    # 6. 修复异常链 (B904)
    content = re.sub(
        r'raise (\w+Error)\(([^)]+)\)',
        r'raise \1(\2) from e',
        content
    )

    # 7. 修复星号导入 (F403, F405)
    if 'nodes/__init__.py' in str(file_path):
        content = content.replace('from bluev.nodes.control import *', 'from bluev.nodes.control.delay_node import DelayNode')
        content = content.replace('from bluev.nodes.image import *', 'from bluev.nodes.image.screenshot_node import ScreenshotNode\nfrom bluev.nodes.image.find_image_node import FindImageNode')
        content = content.replace('from bluev.nodes.interaction import *', 'from bluev.nodes.interaction.click_node import ClickNode')
        content = content.replace('from bluev.nodes.utility import *', 'from bluev.nodes.utility.log_node import LogNode')

    # 8. 修复变量命名 (N806, E741)
    content = re.sub(r'\bD = make_dummy', r'dummy_class = make_dummy', content)
    content = re.sub(r'\bn = D\(\)', r'n = dummy_class()', content)
    content = re.sub(r'\bl = LogNode', r'log_node = LogNode', content)
    content = re.sub(r'eng\.add_node\(l\)', r'eng.add_node(log_node)', content)

    # 9. 修复复杂度问题 - 简化函数
    if 'C901' in content or 'too complex' in content:
        # 这需要手动重构，先标记
        content = '# TODO: 函数复杂度过高，需要重构\n' + content

    # 10. 修复随机数安全问题 (S311)
    content = content.replace('import random', 'import secrets')
    content = content.replace('random.uniform', 'secrets.SystemRandom().uniform')

    return content


def process_file(file_path: Path) -> bool:
    """处理单个文件"""
    try:
        with open(file_path, encoding='utf-8') as f:
            original_content = f.read()

        content = fix_specific_issues(file_path, original_content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 修复: {file_path}")
            return True
        else:
            print(f"⏭️  跳过: {file_path}")
            return False

    except Exception as e:
        print(f"❌ 错误: {file_path} - {e}")
        return False


def main():
    """主函数"""
    repo_root = Path(__file__).resolve().parents[1]

    print("🔧 开始修复 ruff 代码质量问题...")

    # 1. 先运行 ruff 自动修复
    print("\n📝 步骤 1: 运行 ruff 自动修复...")
    run_ruff_with_unsafe_fixes()

    # 2. 手动修复特定问题
    print("\n🛠️  步骤 2: 手动修复特定问题...")

    problem_files = [
        "bluev/core/decorators.py",
        "bluev/core/node_registry.py",
        "bluev/core/node_types.py",
        "bluev/core/workflow_engine.py",
        "bluev/core/workflow_loader.py",
        "bluev/nodes/__init__.py",
        "bluev/nodes/control/delay_node.py",
        "bluev/nodes/image/find_image_node.py",
        "bluev/nodes/image/screenshot_node.py",
        "bluev/nodes/interaction/click_node.py",
        "bluev/nodes/utility/log_node.py",
        "bluev/utils/logging.py",
        "bluev/utils/system_adapter.py",
        "tests/unit/test_base_node_validation.py",
        "tests/unit/test_engine_errors.py",
    ]

    fixed_count = 0
    for file_path in problem_files:
        full_path = repo_root / file_path
        if full_path.exists() and process_file(full_path):
            fixed_count += 1

    print(f"\n✨ 手动修复完成！处理了 {fixed_count} 个文件")

    # 3. 再次运行 ruff 检查结果
    print("\n🔍 步骤 3: 验证修复结果...")
    try:
        result = subprocess.run(['ruff', 'check', '.'], capture_output=True, text=True, cwd=repo_root)
        if result.returncode == 0:
            print("🎉 所有 ruff 检查通过！")
        else:
            print("⚠️  仍有部分问题需要手动处理:")
            print(result.stdout)
    except FileNotFoundError:
        print("⚠️  请手动运行: ruff check .")


if __name__ == "__main__":
    main()
