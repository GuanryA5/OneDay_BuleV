# -*- coding: utf-8 -*-
"""
图像处理节点模块

包含所有与图像处理相关的节点：
- ScreenshotNode: 屏幕截图节点
- FindImageNode: 图像查找节点
"""

from .find_image_node import FindImageNode
from .screenshot_node import ScreenshotNode

__all__ = [
    "ScreenshotNode",
    "FindImageNode",
]
