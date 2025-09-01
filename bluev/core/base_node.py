# -*- coding: utf-8 -*-
"""
BlueV 节点基类

定义所有节点的基础抽象类，提供统一的节点接口和行为规范。
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from bluev.core.node_types import (
    NodeExecutionResult,
    NodeInput,
    NodeMetadata,
    NodeOutput,
    NodeState,
)
from bluev.utils.logging import get_logger

if TYPE_CHECKING:
    # 仅用于类型检查，避免运行时循环依赖
    from bluev.core.execution_context import ExecutionContext


class BaseNode(ABC):
    """BlueV 节点基类

    约定：
    - 子类必须实现 get_input_spec, get_output_spec, get_metadata, execute
    - execute 为异步方法，返回节点输出字典（键为输出名称）
    - 使用 validate_inputs 对入参进行统一校验
    - 通过 set_input/get_input, set_output/get_output 读写数据
    - 使用 reset 重置运行状态
    """

    def __init__(
        self, node_id: Optional[str] = None, label: Optional[str] = None
    ) -> None:
        """
        初始化节点

        Args:
            node_id: 节点唯一标识，如果为None则自动生成
            label: 节点显示标签，如果为None则使用node_id
        """
        self.node_id = node_id or str(uuid.uuid4())
        self.label = label or self.node_id
        self.state = NodeState.READY

        # 输入输出数据
        self.inputs: Dict[str, Any] = {}
        self.outputs: Dict[str, Any] = {}

        # 执行状态
        self.error_message: Optional[str] = None
        self.execution_time: float = 0.0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        # 日志记录器
        self.logger = get_logger(f"{self.__class__.__name__}[{self.node_id[:8]}]")

        # 初始化输入输出规范
        self._input_specs = self.get_input_spec()
        self._output_specs = self.get_output_spec()

        # 初始化默认输入值
        self._initialize_default_inputs()

        self.logger.debug(f"节点初始化完成: {self.node_id}")

    def _initialize_default_inputs(self) -> None:
        """初始化默认输入值：根据输入规范填充 default_value"""
        for input_spec in self._input_specs:
            if input_spec.default_value is not None:
                self.inputs[input_spec.name] = input_spec.default_value

    @classmethod
    @abstractmethod
    def get_input_spec(cls) -> List[NodeInput]:
        """
        获取节点输入规范

        Returns:
            输入参数规范列表
        """
        pass

    @classmethod
    @abstractmethod
    def get_output_spec(cls) -> List[NodeOutput]:
        """
        获取节点输出规范

        Returns:
            输出参数规范列表
        """
        pass

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> NodeMetadata:
        """
        获取节点元数据

        Returns:
            节点元数据信息
        """
        pass

    @abstractmethod
    async def execute(self, context: "ExecutionContext") -> Dict[str, Any]:
        """
        执行节点逻辑

        Args:
            context: 执行上下文

        Returns:
            节点输出数据字典

        Raises:
            Exception: 执行过程中的任何异常
        """
        pass

    def set_input(self, name: str, value: Any) -> None:
        """设置输入参数值

        Args:
            name: 参数名称
            value: 参数值

        Raises:
            ValueError: 参数名称不存在或值无效
        """
        # 检查参数是否存在
        input_spec = self._get_input_spec_by_name(name)
        if input_spec is None:
            raise ValueError(f"输入参数 '{name}' 不存在")

        # 验证参数值
        if not input_spec.validate(value):
            raise ValueError(f"输入参数 '{name}' 的值 '{value}' 无效")

        self.inputs[name] = value
        # 统一使用格式化后的字符串，避免额外位置参数导致的记录器签名不一致
        self.logger.debug(f"设置输入参数: {name} = {value!r}")

    def get_input(self, name: str, default: Any = None) -> Any:
        """
        获取输入参数值

        Args:
            name: 参数名称
            default: 默认值

        Returns:
            参数值
        """
        return self.inputs.get(name, default)

    def set_output(self, name: str, value: Any) -> None:
        """
        设置输出值

        Args:
            name: 输出名称
            value: 输出值
        """
        self.outputs[name] = value
        self.logger.debug(f"设置输出: {name} = {value}")

    def get_output(self, name: str, default: Any = None) -> Any:
        """
        获取输出值

        Args:
            name: 输出名称
            default: 默认值

        Returns:
            输出值
        """
        return self.outputs.get(name, default)

    def validate_inputs(self) -> None:
        """
        验证所有输入参数

        Raises:
            ValueError: 任一输入不符合规范
        """
        for input_spec in self._input_specs:
            value = self.inputs.get(input_spec.name)
            if not input_spec.validate(value):
                self.logger.error(f"输入参数验证失败: {input_spec.name} = {value}")
                raise ValueError(f"输入参数 '{input_spec.name}' 无效: {value!r}")

        self.logger.debug("输入参数验证通过")
        return None

    def reset(self) -> None:
        """重置节点状态"""
        self.state = NodeState.READY
        self.outputs.clear()
        self.error_message = None
        self.execution_time = 0.0
        self.start_time = None
        self.end_time = None
        self.logger.debug("节点状态已重置")

    def cancel(self) -> None:
        """取消节点执行"""
        if self.state == NodeState.RUNNING:
            self.state = NodeState.CANCELLED
            self.logger.info("节点执行已取消")

    def get_execution_result(self) -> NodeExecutionResult:
        """
        获取执行结果

        Returns:
            节点执行结果
        """
        return NodeExecutionResult(
            node_id=self.node_id,
            success=(self.state == NodeState.COMPLETED),
            outputs=self.outputs.copy(),
            error_message=self.error_message,
            execution_time=self.execution_time,
            start_time=self.start_time,
            end_time=self.end_time,
        )

    def _get_input_spec_by_name(self, name: str) -> Optional[NodeInput]:
        """根据名称获取输入规范"""
        for spec in self._input_specs:
            if spec.name == name:
                return spec
        return None

    def _get_output_spec_by_name(self, name: str) -> Optional[NodeOutput]:
        """根据名称获取输出规范"""
        for spec in self._output_specs:
            if spec.name == name:
                return spec
        return None

    def to_dict(self) -> Dict[str, Any]:
        """
        将节点转换为字典格式

        Returns:
            节点数据字典
        """
        return {
            "node_id": self.node_id,
            "label": self.label,
            "node_type": self.__class__.__name__,
            "state": self.state.value,
            "inputs": self.inputs.copy(),
            "outputs": self.outputs.copy(),
            "error_message": self.error_message,
            "execution_time": self.execution_time,
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.node_id[:8]}]({self.state.value})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(node_id='{self.node_id}', label='{self.label}', state={self.state})"
