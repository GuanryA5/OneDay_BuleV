# -*- coding: utf-8 -*-
"""
LogNode - 日志输出节点

提供结构化日志输出功能，集成项目日志系统，
支持多种日志级别和自定义字段。
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

# 使用模块引用，便于测试中通过 patch('bluev.utils.logging.logger') 生效
import bluev.utils.logging as logging_utils

if TYPE_CHECKING:
    from bluev.core.execution_context import ExecutionContext
from bluev.core import BaseNode, NodeInput, NodeMetadata, NodeOutput
from bluev.core.decorators import utility_node


@utility_node(
    node_type="log",
    display_name="日志输出",
    description="输出结构化日志信息，支持多种日志级别",
)
class LogNode(BaseNode):
    """
    日志输出节点

    功能：
    - 多级别日志输出 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - 结构化日志支持
    - 自定义字段添加
    - 与项目日志系统集成

    适用场景：
    - 工作流执行状态记录
    - 调试信息输出
    - 错误和异常记录
    - 业务数据记录
    """

    # 支持的日志级别
    VALID_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    @classmethod
    def get_input_spec(cls) -> List[NodeInput]:
        """获取输入规范"""
        return [
            NodeInput(
                name="message",
                data_type=str,
                default_value="",
                required=True,
                description="日志消息内容",
            ),
            NodeInput(
                name="level",
                data_type=str,
                default_value="INFO",
                required=False,
                description=f"日志级别，支持: {', '.join(cls.VALID_LEVELS)}",
            ),
            NodeInput(
                name="extra_data",
                data_type=Optional[Dict[str, Any]],  # type: ignore
                default_value=None,
                required=False,
                description="额外的结构化数据字典",
            ),
            NodeInput(
                name="category",
                data_type=str,
                default_value="workflow",
                required=False,
                description="日志分类标签",
            ),
        ]

    @classmethod
    def get_output_spec(cls) -> List[NodeOutput]:
        """获取输出规范"""
        return [
            NodeOutput(name="logged", data_type=bool, description="是否成功记录日志"),
            NodeOutput(
                name="log_level", data_type=str, description="实际使用的日志级别"
            ),
            NodeOutput(name="timestamp", data_type=str, description="日志记录时间戳"),
            NodeOutput(
                name="log_entry",
                data_type=Dict[str, Any],
                description="完整的日志条目数据",
            ),
        ]

    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """获取节点元数据"""
        return NodeMetadata(
            node_type="log_node",
            display_name="日志输出",
            description="输出结构化日志信息，支持多种日志级别",
            category="utility",
            tags=["log", "debug", "monitoring", "output"],
            version="1.0.0",
        )

    async def execute(self, context: "ExecutionContext") -> Dict[str, Any]:
        """
        执行日志输出

        Args:
            context: 执行上下文

        Returns:
            包含日志记录结果的字典
        """
        try:
            # 获取输入参数
            message = self.inputs.get("message", "")
            level = self.inputs.get("level", "INFO").upper()
            extra_data = self.inputs.get("extra_data") or {}
            category = self.inputs.get("category", "workflow")

            # 验证日志级别
            if level not in self.VALID_LEVELS:
                self.logger.warning(f"无效的日志级别 '{level}'，使用默认级别 'INFO'")
                level = "INFO"

            # 生成时间戳
            timestamp = datetime.now().isoformat()

            # 构建日志条目
            log_entry = {
                "timestamp": timestamp,
                "level": level,
                "category": category,
                "message": message,
                "node_id": self.node_id,
                "node_type": "log",
                **extra_data,  # 合并额外数据
            }

            # 根据级别输出日志（通过模块属性 logger 绑定，便于单测 patch 生效）
            bound = logging_utils.logger.bind()
            log_method = getattr(bound, level.lower())

            if extra_data:
                log_method(message, **extra_data, category=category)
            else:
                log_method(message, category=category)

            # 返回结果
            result = {
                "logged": True,
                "log_level": level,
                "timestamp": timestamp,
                "log_entry": log_entry,
            }

            return result

        except Exception as e:
            # 记录错误但不抛出异常，确保工作流继续执行
            self.logger.error(f"日志输出失败: {e}")

            return {
                "logged": False,
                "log_level": "ERROR",
                "timestamp": datetime.now().isoformat(),
                "log_entry": {"error": str(e), "message": "日志输出失败"},
            }
