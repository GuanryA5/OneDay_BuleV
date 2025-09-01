# -*- coding: utf-8 -*-
"""
BlueV 执行上下文

管理工作流执行过程中的状态、数据和回调函数。
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

from bluev.utils.logging import get_logger


@dataclass
class ExecutionMetrics:
    """执行指标统计"""

    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    nodes_executed: int = 0
    nodes_failed: int = 0
    nodes_cancelled: int = 0
    memory_usage: float = 0.0

    def finish(self) -> None:
        """完成执行，计算总时长"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "nodes_executed": self.nodes_executed,
            "nodes_failed": self.nodes_failed,
            "nodes_cancelled": self.nodes_cancelled,
            "memory_usage": self.memory_usage,
        }


class ExecutionContext:
    """
    工作流执行上下文

    管理工作流执行过程中的所有状态信息、节点输出数据、
    执行历史和回调函数。
    """

    def __init__(
        self, workflow_id: str, max_execution_time: Optional[float] = None
    ) -> None:
        """
        初始化执行上下文

        Args:
            workflow_id: 工作流唯一标识
            max_execution_time: 最大执行时间(秒)，None表示无限制
        """
        self.workflow_id = workflow_id
        self.max_execution_time = max_execution_time

        # 执行状态
        self.is_running = False
        self.is_cancelled = False
        self.is_paused = False

        # 数据存储
        self.global_variables: Dict[str, Any] = {}
        self.node_outputs: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[str] = []
        self.failed_nodes: Set[str] = set()

        # 执行指标
        self.metrics = ExecutionMetrics()

        # 回调函数
        self.callbacks: Dict[str, List[Callable]] = {
            "workflow_start": [],
            "workflow_complete": [],
            "workflow_error": [],
            "node_start": [],
            "node_complete": [],
            "node_error": [],
            "progress_update": [],
        }

        # 日志记录器
        self.logger = get_logger(f"ExecutionContext[{workflow_id[:8]}]")

        # 异步控制
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # 初始状态为非暂停

        self.logger.debug(f"执行上下文初始化完成: {workflow_id}")

    def set_global_variable(self, name: str, value: Any) -> None:
        """
        设置全局变量

        Args:
            name: 变量名
            value: 变量值
        """
        self.global_variables[name] = value
        self.logger.debug(f"设置全局变量: {name} = {value}")

    def get_global_variable(self, name: str, default: Any = None) -> Any:
        """
        获取全局变量

        Args:
            name: 变量名
            default: 默认值

        Returns:
            变量值
        """
        return self.global_variables.get(name, default)

    def set_node_output(self, node_id: str, outputs: Dict[str, Any]) -> None:
        """
        设置节点输出数据

        Args:
            node_id: 节点ID
            outputs: 输出数据字典
        """
        self.node_outputs[node_id] = outputs.copy()
        self.logger.debug(f"保存节点输出: {node_id} -> {list(outputs.keys())}")

    def get_node_output(self, node_id: str, output_name: Optional[str] = None) -> Any:
        """
        获取节点输出数据

        Args:
            node_id: 节点ID
            output_name: 输出名称，如果为None则返回所有输出

        Returns:
            输出数据
        """
        if node_id not in self.node_outputs:
            return None

        if output_name is None:
            return self.node_outputs[node_id]

        return self.node_outputs[node_id].get(output_name)

    def add_callback(self, event_type: str, callback: Callable) -> None:
        """
        添加回调函数

        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
            self.logger.debug(f"添加回调函数: {event_type}")
        else:
            self.logger.warning(f"未知的事件类型: {event_type}")

    async def trigger_callback(self, event_type: str, **kwargs: Any) -> None:
        """
        触发回调函数

        Args:
            event_type: 事件类型
            **kwargs: 回调参数
        """
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(self, **kwargs)
                    else:
                        callback(self, **kwargs)
                except Exception as e:
                    self.logger.error(f"回调函数执行失败 ({event_type}): {e}")

    def start_execution(self) -> None:
        """开始执行"""
        self.is_running = True
        self.is_cancelled = False
        self.is_paused = False
        self.metrics = ExecutionMetrics()
        self.execution_history.clear()
        self.failed_nodes.clear()
        self._pause_event.set()
        self.logger.info("开始工作流执行")

    def finish_execution(self, success: bool = True) -> None:
        """完成执行"""
        self.is_running = False
        self.metrics.finish()

        if success:
            self.logger.info(f"工作流执行完成，耗时: {self.metrics.duration:.2f}秒")
        else:
            self.logger.error(f"工作流执行失败，耗时: {self.metrics.duration:.2f}秒")

    def cancel_execution(self) -> None:
        """取消执行"""
        self.is_cancelled = True
        self.is_running = False
        self._pause_event.set()  # 确保暂停的执行可以继续并检查取消状态
        self.logger.info("工作流执行已取消")

    def pause_execution(self) -> None:
        """暂停执行"""
        if self.is_running:
            self.is_paused = True
            self._pause_event.clear()
            self.logger.info("工作流执行已暂停")

    def resume_execution(self) -> None:
        """恢复执行"""
        if self.is_paused:
            self.is_paused = False
            self._pause_event.set()
            self.logger.info("工作流执行已恢复")

    async def wait_if_paused(self) -> None:
        """如果暂停则等待"""
        if self.is_paused:
            self.logger.debug("等待执行恢复...")
            await self._pause_event.wait()

    def check_timeout(self) -> bool:
        """
        检查是否超时

        Returns:
            是否超时
        """
        if self.max_execution_time is None:
            return False

        if self.metrics.start_time is None:
            return False

        elapsed = (datetime.now() - self.metrics.start_time).total_seconds()
        return elapsed > self.max_execution_time

    def record_node_execution(self, node_id: str, success: bool) -> None:
        """
        记录节点执行结果

        Args:
            node_id: 节点ID
            success: 是否成功
        """
        self.execution_history.append(node_id)
        self.metrics.nodes_executed += 1

        if success:
            self.logger.debug(f"节点执行成功: {node_id}")
        else:
            self.failed_nodes.add(node_id)
            self.metrics.nodes_failed += 1
            self.logger.warning(f"节点执行失败: {node_id}")

    def get_execution_summary(self) -> Dict[str, Any]:
        """
        获取执行摘要

        Returns:
            执行摘要字典
        """
        return {
            "workflow_id": self.workflow_id,
            "is_running": self.is_running,
            "is_cancelled": self.is_cancelled,
            "is_paused": self.is_paused,
            "execution_history": self.execution_history.copy(),
            "failed_nodes": list(self.failed_nodes),
            "metrics": self.metrics.to_dict(),
            "global_variables": self.global_variables.copy(),
            "node_count": len(self.node_outputs),
        }

    def __str__(self) -> str:
        status = "running" if self.is_running else "stopped"
        if self.is_cancelled:
            status = "cancelled"
        elif self.is_paused:
            status = "paused"

        return f"ExecutionContext[{self.workflow_id[:8]}]({status})"
