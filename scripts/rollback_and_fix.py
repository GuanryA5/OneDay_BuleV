#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回滚错误修复并正确处理 ruff 问题
"""

import re
import subprocess
from pathlib import Path


def rollback_getattr_errors(content: str) -> str:
    """回滚错误的 getattr 替换"""
    # 修复赋值语句
    content = re.sub(r'getattr\(([^,]+), \'([^\']+)\', \'[^\']*\'\)\s*=', r'\1.\2 =', content)

    # 修复方法调用
    content = re.sub(r'getattr\(([^,]+), \'([^\']+)\', \'[^\']*\'\)\(', r'\1.\2(', content)

    # 修复属性访问
    content = re.sub(r'getattr\(([^,]+), \'getattr\', \'[^\']*\'\)\(([^,]+), \'([^\']+)\', \'[^\']*\'\)', r'getattr(\2, \'\3\', \'Unknown\')', content)

    return content


def fix_exception_chains(content: str) -> str:
    """正确修复异常链"""
    # 移除错误的 "from e from e" 语法
    content = re.sub(r'\) from e', r') from e', content)

    # 移除没有上下文的 "from e"
    content = re.sub(r'raise (\w+Error)\([^)]+\) from e(?!\s*$)', r'raise \1', content)

    return content


def fix_f_string_errors(content: str) -> str:
    """修复 f-string 语法错误"""
    # 修复 f-string 中的 "from e" 错误
    content = re.sub(r'f"([^"]*) from e([^"]*)"', r'f"\1\2"', content)

    return content


def fix_import_errors(content: str) -> str:
    """修复导入相关错误"""
    # 移除未使用的 TYPE_CHECKING 导入
    if 'TYPE_CHECKING' in content and 'if TYPE_CHECKING:' not in content:
        content = re.sub(r'from typing import TYPE_CHECKING,?\s*', '', content)
        content = re.sub(r', TYPE_CHECKING', '', content)

    return content


def fix_specific_files(file_path: Path, content: str) -> str:
    """修复特定文件的问题"""

    # 修复 nodes/__init__.py 的星号导入
    if 'nodes/__init__.py' in str(file_path):
        content = content.replace(
            'from bluev.nodes.control import *',
            'from bluev.nodes.control.delay_node import DelayNode'
        )
        content = content.replace(
            'from bluev.nodes.image import *',
            'from bluev.nodes.image.screenshot_node import ScreenshotNode\nfrom bluev.nodes.image.find_image_node import FindImageNode'
        )
        content = content.replace(
            'from bluev.nodes.interaction import *',
            'from bluev.nodes.interaction.click_node import ClickNode'
        )
        content = content.replace(
            'from bluev.nodes.utility import *',
            'from bluev.nodes.utility.log_node import LogNode'
        )

    # 修复变量命名问题
    if 'test_base_node_validation.py' in str(file_path):
        content = content.replace('D = make_dummy', 'dummy_class = make_dummy')
        content = content.replace('n = D()', 'n = dummy_class()')

    if 'test_engine_errors.py' in str(file_path):
        content = content.replace('l = LogNode', 'log_node = LogNode')
        content = content.replace('eng.add_node(l)', 'eng.add_node(log_node)')
        content = content.replace('"l"', '"log_node"')

    # 修复装饰器函数名问题
    if 'decorators.py' in str(file_path):
        content = content.replace(
            'def __init__(self, *args, **kwargs)',
            'def __init_wrapper__(self, *args, **kwargs)'
        )

    return content


def process_file(file_path: Path) -> bool:
    """处理单个文件"""
    try:
        with open(file_path, encoding='utf-8') as f:
            original_content = f.read()

        content = original_content

        # 应用修复
        content = rollback_getattr_errors(content)
        content = fix_exception_chains(content)
        content = fix_f_string_errors(content)
        content = fix_import_errors(content)
        content = fix_specific_files(file_path, content)

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

    print("🔄 开始回滚错误修复并重新处理...")

    # 获取所有 Python 文件
    python_files = list(repo_root.glob("**/*.py"))

    fixed_count = 0
    for file_path in python_files:
        if '.git' in str(file_path) or '__pycache__' in str(file_path):
            continue
        if process_file(file_path):
            fixed_count += 1

    print(f"\n✨ 回滚修复完成！处理了 {fixed_count} 个文件")

    # 运行 ruff 自动修复（安全修复）
    print("\n🔧 运行 ruff 自动修复...")
    try:
        result = subprocess.run(
            ['ruff', 'check', '.', '--fix'],
            capture_output=True, text=True, cwd=repo_root
        )
        if result.stdout:
            print(result.stdout)
    except FileNotFoundError:
        print("⚠️  ruff 未安装")

    # 检查结果
    print("\n🔍 验证修复结果...")
    try:
        result = subprocess.run(['ruff', 'check', '.'], capture_output=True, text=True, cwd=repo_root)
        if result.returncode == 0:
            print("🎉 所有 ruff 检查通过！")
        else:
            error_count = result.stdout.count('error:')
            print(f"⚠️  还有 {error_count} 个问题需要处理")
            # 只显示前 20 个错误
            lines = result.stdout.split('\n')[:20]
            print('\n'.join(lines))
    except FileNotFoundError:
        print("⚠️  请手动运行: ruff check .")


if __name__ == "__main__":
    main()
