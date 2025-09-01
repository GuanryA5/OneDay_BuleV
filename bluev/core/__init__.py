# -*- coding: utf-8 -*-
"""
BlueV 核心业务逻辑模块

包含工作流引擎、节点系统、执行引擎、事件系统等核心组件。
"""

# 核心类型和枚举
# 基础节点类
from .base_node import BaseNode

# 装饰器
from .decorators import (
    bluev_node,
    control_flow_node,
    deprecated_node,
    image_processing_node,
    input_node,
    output_node,
    user_interaction_node,
    utility_node,
)

# 执行上下文
from .execution_context import ExecutionContext, ExecutionMetrics

# 节点注册系统
from .node_registry import NodeRegistry, node_registry
from .node_types import (
    NodeConnection,
    NodeExecutionResult,
    NodeInput,
    NodeMetadata,
    NodeOutput,
    NodeState,
)

# 工作流引擎
from .workflow_engine import (
    CircularDependencyError,
    WorkflowEngine,
    WorkflowExecutionError,
)

__all__ = [
    # 类型和枚举
    "NodeState",
    "NodeInput",
    "NodeOutput",
    "NodeConnection",
    "NodeExecutionResult",
    "NodeMetadata",
    # 核心类
    "BaseNode",
    "ExecutionContext",
    "ExecutionMetrics",
    "NodeRegistry",
    "WorkflowEngine",
    # 全局实例
    "node_registry",
    # 装饰器
    "bluev_node",
    "input_node",
    "output_node",
    "image_processing_node",
    "control_flow_node",
    "user_interaction_node",
    "utility_node",
    "deprecated_node",
    # 异常
    "WorkflowExecutionError",
    "CircularDependencyError",
]
