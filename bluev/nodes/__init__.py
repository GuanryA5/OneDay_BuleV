# -*- coding: utf-8 -*-
"""
BlueV 节点模块

包含所有节点类型的实现，按功能分类组织：
- image: 图像处理节点
- control: 控制流节点
- utility: 工具类节点
- interaction: 用户交互节点
"""

# 导入所有节点类型，便于统一管理和注册
from bluev.nodes.control.delay_node import DelayNode
from bluev.nodes.image.find_image_node import FindImageNode
from bluev.nodes.image.screenshot_node import ScreenshotNode
from bluev.nodes.interaction.click_node import ClickNode
from bluev.nodes.utility.log_node import LogNode

__all__ = [
    # 图像处理节点
    "ScreenshotNode",
    "FindImageNode",
    # 控制流节点
    "DelayNode",
    # 工具类节点
    "LogNode",
    # 用户交互节点
    "ClickNode",
]
