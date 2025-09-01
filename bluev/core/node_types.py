# -*- coding: utf-8 -*-
"""
BlueV 节点类型定义

定义节点系统的核心数据结构、状态枚举和类型定义。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union

if TYPE_CHECKING:
    from bluev.core.base_node import BaseNode


class NodeState(Enum):
    """节点执行状态枚举"""

    READY = "ready"  # 就绪状态，可以执行
    RUNNING = "running"  # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 执行失败
    CANCELLED = "cancelled"  # 已取消


@dataclass
class NodeInput:
    """节点输入参数定义"""

    name: str  # 参数名称
    data_type: Type  # 数据类型
    default_value: Any = None  # 默认值
    required: bool = True  # 是否必需
    description: str = ""  # 参数描述
    validation_rules: Optional[Dict[str, Any]] = None  # 验证规则

    def __post_init__(self) -> None:
        """初始化后处理"""
        if self.validation_rules is None:
            self.validation_rules = {}

    def validate(self, value: Any) -> bool:
        """验证输入值是否符合要求"""
        if not self._validate_required(value):
            return False

        if not self._validate_data_type(value):
            return False

        if not self._validate_rules(value):
            return False

        return True

    def _validate_required(self, value: Any) -> bool:
        """验证必需参数"""
        if self.required and value is None:
            return False
        return True

    def _validate_data_type(self, value: Any) -> bool:
        """验证数据类型"""
        # 如果值为 None 且不是必需的，则通过验证
        if value is None and not self.required:
            return True

        # 检查数据类型
        if not isinstance(value, self.data_type):
            # 尝试类型转换
            try:
                self.data_type(value)
                return True
            except (ValueError, TypeError):
                return False
        return True

    def _validate_rules(self, value: Any) -> bool:
        """验证规则"""
        if not self.validation_rules:
            return True

        if not self._validate_numeric_range(value):
            return False

        if not self._validate_string_length(value):
            return False

        return True

    def _validate_numeric_range(self, value: Any) -> bool:
        """验证数值范围"""
        if self.validation_rules and "min_value" in self.validation_rules:
            if value < self.validation_rules["min_value"]:
                return False
        if self.validation_rules and "max_value" in self.validation_rules:
            if value > self.validation_rules["max_value"]:
                return False
        return True

    def _validate_string_length(self, value: Any) -> bool:
        """验证字符串长度"""
        if self.validation_rules and "min_length" in self.validation_rules:
            if len(str(value)) < self.validation_rules["min_length"]:
                return False
        if self.validation_rules and "max_length" in self.validation_rules:
            if len(str(value)) > self.validation_rules["max_length"]:
                return False
        return True


@dataclass
class NodeOutput:
    """节点输出定义"""

    name: str  # 输出名称
    data_type: Type  # 数据类型
    description: str = ""  # 输出描述


@dataclass
class NodeConnection:
    """节点连接定义"""

    from_node_id: str  # 源节点ID
    from_output: str  # 源节点输出名称
    to_node_id: str  # 目标节点ID
    to_input: str  # 目标节点输入名称

    def __str__(self) -> str:
        return f"{self.from_node_id}.{self.from_output} -> {self.to_node_id}.{self.to_input}"


@dataclass
class NodeExecutionResult:
    """节点执行结果"""

    node_id: str  # 节点ID
    success: bool  # 是否成功
    outputs: Dict[str, Any] = field(default_factory=dict)  # 输出数据
    error_message: Optional[str] = None  # 错误信息
    execution_time: float = 0.0  # 执行时间(秒)
    start_time: Optional[datetime] = None  # 开始时间
    end_time: Optional[datetime] = None  # 结束时间

    def __post_init__(self) -> None:
        """计算执行时间"""
        if self.start_time and self.end_time:
            self.execution_time = (self.end_time - self.start_time).total_seconds()


@dataclass
class NodeMetadata:
    """节点元数据"""

    node_type: str  # 节点类型
    category: str  # 节点分类
    display_name: str  # 显示名称
    description: str  # 节点描述
    version: str = "1.0.0"  # 版本号
    author: str = "BlueV Team"  # 作者
    tags: List[str] = field(default_factory=list)  # 标签
    icon: Optional[str] = None  # 图标路径

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "node_type": self.node_type,
            "category": self.category,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "tags": self.tags,
            "icon": self.icon,
        }


# 常用数据类型别名
NodeInputValue = Union[str, int, float, bool, list, dict, Any]
NodeOutputValue = Union[str, int, float, bool, list, dict, Any]

# 节点类型注册表类型
NodeClassType = Type["BaseNode"]  # 前向引用，避免循环导入
