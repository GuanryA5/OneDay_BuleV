#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复语法错误的脚本
"""

import re
from pathlib import Path


def fix_getattr_assignments(content: str) -> str:
    """修复错误的 getattr 赋值语句"""
    # 修复 self.attr = value 这种错误语法
    pattern = r"getattr\(self, '(\w+)', '[^']*'\)\s*="
    replacement = r"self.\1 ="

    return re.sub(pattern, replacement, content)


def fix_getattr_calls(content: str) -> str:
    """修复不必要的 getattr 调用"""
    # 修复 self.method() 这种调用
    pattern = r"getattr\(self, '(\w+)', '[^']*'\)\(\)"
    replacement = r"self.\1()"

    return re.sub(pattern, replacement, content)


def main():
    """主函数"""
    repo_root = Path(__file__).resolve().parents[1]

    # 重点修复有问题的文件
    problem_files = [
        "bluev/ui/main_window.py",
        "bluev/config.py",
        "bluev/utils/logging.py",
    ]

    for file_path in problem_files:
        full_path = repo_root / file_path
        if not full_path.exists():
            continue

        try:
            with open(full_path, encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 应用修复
            content = fix_getattr_assignments(content)
            content = fix_getattr_calls(content)

            # 特定修复
            if "main_window.py" in str(full_path):
                # 修复状态栏相关的错误
                content = content.replace(
                    "statusbar = self.statusBar()",
                    "statusbar = self.statusBar()"
                )
                content = content.replace(
                    "getattr(self, 'status_label', 'Unknown')",
                    "self.status_label"
                )

            if content != original_content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 修复: {full_path}")
            else:
                print(f"⏭️  跳过: {full_path}")

        except Exception as e:
            print(f"❌ 错误: {full_path} - {e}")


if __name__ == "__main__":
    main()
