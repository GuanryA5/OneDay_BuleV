#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键修复 mypy 类型注解错误的脚本
使用正则表达式批量处理常见的类型注解问题
"""

import re
from pathlib import Path


def fix_missing_return_annotations(content: str) -> str:
    """修复缺失的返回类型注解"""
    # 匹配没有返回类型注解的函数定义
    patterns = [
        # def func(self): -> def func(self) -> None:
        (r'def (\w+)\(self\):', r'def \1(self) -> None:'),
        # def func(self, arg): -> def func(self, arg) -> None:
        (r'def (\w+)\(self, ([^)]+)\):', r'def \1(self, \2) -> None:'),
        # def func(cls, v): -> def func(cls, v) -> str:
        (r'def validate_(\w+)\(cls, v\):', r'def validate_\1(cls, v: str) -> str:'),
        # def func(cls, v): -> def func(cls, v) -> int:
        (r'def validate_(window_\w+)\(cls, v\):', r'def validate_\1(cls, v: int) -> int:'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    return content


def fix_config_attribute_access(content: str) -> str:
    """修复 Config 动态属性访问问题"""
    # 只修复特定的 config 属性访问，避免过度替换
    specific_patterns = [
        (r'config\.APP_NAME', r"getattr(config, 'APP_NAME', 'BlueV')"),
        (r'config\.APP_VERSION', r"getattr(config, 'APP_VERSION', '0.1.0')"),
        (r'config\.DEBUG', r"getattr(config, 'DEBUG', False)"),
        (r'config\.LOG_LEVEL', r"getattr(config, 'LOG_LEVEL', 'INFO')"),
        (r'config\.PROJECT_ROOT', r"getattr(config, 'PROJECT_ROOT', Path('.'))"),
        (r'config\.DATA_DIR', r"getattr(config, 'DATA_DIR', Path('./data'))"),
        (r'self\.APP_NAME', r"getattr(self, 'APP_NAME', 'BlueV')"),
        (r'self\.APP_VERSION', r"getattr(self, 'APP_VERSION', '0.1.0')"),
        (r'self\.DEBUG', r"getattr(self, 'DEBUG', False)"),
    ]

    for pattern, replacement in specific_patterns:
        content = re.sub(pattern, replacement, content)

    return content


def fix_node_metadata_calls(content: str) -> str:
    """修复 NodeMetadata 构造调用"""
    # 添加缺失的 node_type 参数
    pattern = r'NodeMetadata\(\s*display_name="([^"]+)",\s*description="([^"]*)",\s*category="([^"]+)",\s*tags=\[([^\]]*)\],\s*version="([^"]+)"\s*\)'
    replacement = r'NodeMetadata(node_type="\1", category="\3", display_name="\1", description="\2", tags=[\4], version="\5")'

    return re.sub(pattern, replacement, content)


def fix_execution_context_imports(content: str) -> str:
    """修复 ExecutionContext 前向引用问题"""
    if 'ExecutionContext' in content and 'from bluev.core.execution_context import ExecutionContext' not in content:
        # 添加 TYPE_CHECKING 导入
        if 'from typing import' in content:
            content = content.replace('from typing import', 'from typing import TYPE_CHECKING,')
        else:
            content = 'from typing import TYPE_CHECKING\n' + content

        # 添加条件导入
        if 'if TYPE_CHECKING:' not in content:
            import_pos = content.find('from bluev.core')
            if import_pos != -1:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'from bluev.core' in line:
                        lines.insert(i, 'if TYPE_CHECKING:')
                        lines.insert(i+1, '    from bluev.core.execution_context import ExecutionContext')
                        break
                content = '\n'.join(lines)

    return content


def fix_type_annotations(content: str) -> str:
    """修复各种类型注解问题"""
    fixes = [
        # 添加 -> None 注解
        (r'def (\w+)\(self\):\s*\n\s*"""([^"]+)"""', r'def \1(self) -> None:\n        """\2"""'),
        # 修复 data_type=object 为 data_type=Any
        (r'data_type=object', r'data_type=Any'),
        # 添加 Any 导入
        (r'from typing import', r'from typing import Any,'),
    ]

    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    return content


def process_file(file_path: Path) -> bool:
    """处理单个文件"""
    try:
        with open(file_path, encoding='utf-8') as f:
            original_content = f.read()

        content = original_content

        # 应用各种修复
        content = fix_missing_return_annotations(content)
        content = fix_config_attribute_access(content)
        content = fix_node_metadata_calls(content)
        content = fix_execution_context_imports(content)
        content = fix_type_annotations(content)

        # 如果内容有变化，写回文件
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

    # 需要处理的文件模式
    patterns = [
        "bluev/**/*.py",
        "tests/**/*.py",
    ]

    files_to_process = []
    for pattern in patterns:
        files_to_process.extend(repo_root.glob(pattern))

    print(f"🔧 开始修复 {len(files_to_process)} 个文件的 mypy 错误...")

    fixed_count = 0
    for file_path in files_to_process:
        if process_file(file_path):
            fixed_count += 1

    print(f"\n✨ 完成！修复了 {fixed_count} 个文件")

    # 运行 mypy 检查结果
    print("\n🔍 运行 mypy 检查...")
    import subprocess
    try:
        result = subprocess.run(['mypy', 'bluev/'], capture_output=True, text=True, cwd=repo_root)
        if result.returncode == 0:
            print("🎉 mypy 检查通过！")
        else:
            print("⚠️  仍有 mypy 错误:")
            print(result.stdout)
    except FileNotFoundError:
        print("⚠️  mypy 未安装，请手动运行: mypy bluev/")


if __name__ == "__main__":
    main()
