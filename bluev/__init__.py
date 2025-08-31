# -*- coding: utf-8 -*-
"""
BlueV 游戏自动化蓝图框架

一个基于 PySide6 的可视化游戏自动化工具，让用户通过拖拽节点的方式
创建复杂的游戏自动化工作流程。
"""

__version__ = "0.1.0"
__author__ = "BlueV Team"
__email__ = "team@bluev.dev"
__description__ = "BlueV游戏自动化蓝图框架"

# 导出核心组件
from .config import Config
from .main import main

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "Config",
    "main",
]
