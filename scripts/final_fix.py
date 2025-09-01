#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终精准修复剩余的关键问题
"""

import re
from pathlib import Path


def fix_core_init(content: str) -> str:
    """修复 core/__init__.py"""
    # 移除开头的 Any
    content = re.sub(r'^Any\s*\n', '', content)

    # 移动导入到文件顶部
    lines = content.split('\n')
    imports = []
    other_lines = []

    for line in lines:
        if line.startswith('from .') or line.startswith('import '):
            imports.append(line)
        else:
            other_lines.append(line)

    # 重新组织
    result = []
    result.append('# -*- coding: utf-8 -*-')
    result.append('')
    result.extend(imports)
    result.append('')
    result.extend([line for line in other_lines if line.strip() and not line.startswith('#')])

    return '\n'.join(result)


def fix_nodes_init(content: str) -> str:
    """修复 nodes/__init__.py 的星号导入"""
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
    return content


def fix_decorators(content: str) -> str:
    """修复装饰器问题"""
    # 修复函数名问题
    content = content.replace('def __init_wrapper__', 'def _deprecated_init_wrapper')
    content = content.replace('cls.__init__ = __init__', 'cls.__init__ = _deprecated_init_wrapper')
    return content


def fix_node_registry(content: str) -> str:
    """修复 node_registry 问题"""
    # 修复字典推导式中的变量名
    content = content.replace(
        'category: len(node_types)\n                    for _category, node_types in self._categories.items()',
        '_category: len(node_types)\n                    for _category, node_types in self._categories.items()'
    )
    return content


def fix_workflow_loader(content: str) -> str:
    """修复 workflow_loader 语法错误"""
    # 修复损坏的字符串
    content = re.sub(r'raise WorkflowValidationError\}[^"]*"[^)]*\)',
                     'raise WorkflowValidationError(f"节点 {node.node_id} 未定义{(\'输入\' if kind==\'input\' else \'输出\')}端口")',
                     content)
    return content


def fix_click_node(content: str) -> str:
    """修复 click_node 语法错误"""
    # 修复损坏的字符串
    content = re.sub(r'raise ValueError [^"]*坐标元组[^)]*\)',
                     'raise ValueError("位置参数必须是包含两个数字的坐标元组")',
                     content)
    content = re.sub(r'raise ValueError [^"]*超出屏幕范围[^)]*\)',
                     'raise ValueError(f"点击位置 ({x}, {y}) 超出屏幕范围 ({self.screen_width}x{self.screen_height})")',
                     content)
    return content


def fix_main_window(content: str) -> str:
    """修复 main_window 中的 config 引用"""
    # 修复 self.getattr(config, ...) 为 getattr(self.config, ...)
    content = re.sub(r'self\.getattr\(config, \'([^\']+)\', \'[^\']*\'\)',
                     r"getattr(self.config, '\1', 'Unknown')",
                     content)
    return content


def fix_main_py(content: str) -> str:
    """修复 main.py 中的注解赋值错误"""
    # 修复错误的注解赋值语法
    content = re.sub(r'getattr\([^)]+\): Optional\[[^\]]+\] = ', 'self.app: Optional[QApplication] = ', content, count=1)
    content = re.sub(r'getattr\([^)]+\): Optional\[[^\]]+\] = ', 'self.main_window: Optional[MainWindow] = ', content, count=1)
    return content


def process_file(file_path: Path) -> bool:
    """处理单个文件"""
    try:
        with open(file_path, encoding='utf-8') as f:
            original_content = f.read()

        content = original_content

        # 根据文件路径应用特定修复
        if 'core/__init__.py' in str(file_path):
            content = fix_core_init(content)
        elif 'nodes/__init__.py' in str(file_path):
            content = fix_nodes_init(content)
        elif 'decorators.py' in str(file_path):
            content = fix_decorators(content)
        elif 'node_registry.py' in str(file_path):
            content = fix_node_registry(content)
        elif 'workflow_loader.py' in str(file_path):
            content = fix_workflow_loader(content)
        elif 'click_node.py' in str(file_path):
            content = fix_click_node(content)
        elif 'main_window.py' in str(file_path):
            content = fix_main_window(content)
        elif 'main.py' in str(file_path) and 'bluev' in str(file_path):
            content = fix_main_py(content)

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

    print("🎯 开始精准修复剩余关键问题...")

    # 重点修复的文件
    critical_files = [
        "bluev/core/__init__.py",
        "bluev/nodes/__init__.py",
        "bluev/core/decorators.py",
        "bluev/core/node_registry.py",
        "bluev/core/workflow_loader.py",
        "bluev/nodes/interaction/click_node.py",
        "bluev/ui/main_window.py",
        "bluev/main.py",
    ]

    fixed_count = 0
    for file_path in critical_files:
        full_path = repo_root / file_path
        if full_path.exists() and process_file(full_path):
            fixed_count += 1

    print(f"\n✨ 精准修复完成！处理了 {fixed_count} 个关键文件")


if __name__ == "__main__":
    main()
