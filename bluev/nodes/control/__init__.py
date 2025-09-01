# -*- coding: utf-8 -*-
"""
控制流节点模块

包含所有与工作流控制相关的节点：
- DelayNode: 延迟等待节点
"""

from .delay_node import DelayNode

__all__ = [
    "DelayNode",
]
