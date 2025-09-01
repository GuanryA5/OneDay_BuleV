# -*- coding: utf-8 -*-
"""
BlueV 工作流执行引擎

简化的工作流执行引擎，支持节点的添加、连接和执行。
"""

import asyncio
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List

from bluev.core.base_node import BaseNode
from bluev.core.execution_context import ExecutionContext
from bluev.core.node_types import NodeConnection, NodeState
from bluev.utils.logging import get_logger


class WorkflowExecutionError(Exception):
    """工作流执行异常"""

    pass


class CircularDependencyError(WorkflowExecutionError):
    """循环依赖异常"""

    pass


class WorkflowEngine:
    """
    简化的工作流执行引擎

    支持节点的添加、连接、拓扑排序和执行。
    使用线程池来处理可能的阻塞操作。
    """

    def __init__(self, max_concurrent_nodes: int = 4) -> None:
        """
        初始化工作流引擎

        Args:
            max_concurrent_nodes: 最大并发节点数
        """
        # 节点存储
        self.nodes: Dict[str, BaseNode] = {}

        # 连接存储
        self.connections: List[NodeConnection] = []

        # 并发控制
        self.max_concurrent_nodes = max_concurrent_nodes
        self.thread_pool = ThreadPoolExecutor(max_workers=max_concurrent_nodes)

        # 日志记录器
        self.logger = get_logger("WorkflowEngine")

        self.logger.debug(f"工作流引擎初始化完成，最大并发数: {max_concurrent_nodes}")

    def add_node(self, node: BaseNode) -> None:
        """
        添加节点到工作流

        Args:
            node: 要添加的节点

        Raises:
            ValueError: 节点ID已存在
        """
        if node.node_id in self.nodes:
            raise ValueError

        self.nodes[node.node_id] = node
        self.logger.info(f"添加节点: {node.node_id} ({node.__class__.__name__})")

    def remove_node(self, node_id: str) -> bool:
        """
        从工作流中移除节点

        Args:
            node_id: 节点ID

        Returns:
            是否成功移除
        """
        if node_id not in self.nodes:
            self.logger.warning(f"尝试移除不存在的节点: {node_id}")
            return False

        # 移除节点
        del self.nodes[node_id]

        # 移除相关连接
        self.connections = [
            conn
            for conn in self.connections
            if conn.from_node_id != node_id and conn.to_node_id != node_id
        ]

        self.logger.info(f"移除节点: {node_id}")
        return True

    def connect_nodes(
        self, from_node_id: str, from_output: str, to_node_id: str, to_input: str
    ) -> None:
        """
        连接两个节点

        Args:
            from_node_id: 源节点ID
            from_output: 源节点输出名称
            to_node_id: 目标节点ID
            to_input: 目标节点输入名称

        Raises:
            ValueError: 节点不存在或连接无效
        """
        # 验证节点存在
        if from_node_id not in self.nodes:
            raise ValueError
        if to_node_id not in self.nodes:
            raise ValueError

        # 验证输入输出规范
        from_node = self.nodes[from_node_id]
        to_node = self.nodes[to_node_id]

        # 检查输出是否存在
        from_outputs = [spec.name for spec in from_node.get_output_spec()]
        if from_output not in from_outputs:
            raise ValueError

        # 检查输入是否存在
        to_inputs = [spec.name for spec in to_node.get_input_spec()]
        if to_input not in to_inputs:
            raise ValueError

        # 创建连接
        connection = NodeConnection(from_node_id, from_output, to_node_id, to_input)

        # 检查是否已存在相同连接
        for existing_conn in self.connections:
            if (
                existing_conn.from_node_id == from_node_id
                and existing_conn.from_output == from_output
                and existing_conn.to_node_id == to_node_id
                and existing_conn.to_input == to_input
            ):
                self.logger.warning(f"连接已存在: {connection}")
                return

        self.connections.append(connection)
        self.logger.info(f"创建连接: {connection}")

    def disconnect_nodes(
        self, from_node_id: str, from_output: str, to_node_id: str, to_input: str
    ) -> bool:
        """
        断开节点连接

        Args:
            from_node_id: 源节点ID
            from_output: 源节点输出名称
            to_node_id: 目标节点ID
            to_input: 目标节点输入名称

        Returns:
            是否成功断开
        """
        original_count = len(self.connections)

        self.connections = [
            conn
            for conn in self.connections
            if not (
                conn.from_node_id == from_node_id
                and conn.from_output == from_output
                and conn.to_node_id == to_node_id
                and conn.to_input == to_input
            )
        ]

        removed = len(self.connections) < original_count
        if removed:
            self.logger.info(
                f"断开连接: {from_node_id}.{from_output} -> {to_node_id}.{to_input}"
            )

        return removed

    def topological_sort(self) -> List[str]:
        """
        对节点进行拓扑排序

        Returns:
            排序后的节点ID列表

        Raises:
            CircularDependencyError: 存在循环依赖
        """
        # 构建邻接表和入度表
        graph = defaultdict(list)
        in_degree = defaultdict(int)

        # 初始化所有节点的入度为0
        for node_id in self.nodes:
            in_degree[node_id] = 0

        # 构建图
        for conn in self.connections:
            graph[conn.from_node_id].append(conn.to_node_id)
            in_degree[conn.to_node_id] += 1

        # Kahn算法进行拓扑排序
        queue = deque([node_id for node_id in self.nodes if in_degree[node_id] == 0])
        result = []

        while queue:
            current = queue.popleft()
            result.append(current)

            # 处理当前节点的所有邻居
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # 检查是否存在循环依赖
        if len(result) != len(self.nodes):
            set(self.nodes.keys()) - set(result)
            raise CircularDependencyError

        self.logger.debug(f"拓扑排序结果: {result}")
        return result

    async def execute_workflow(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        执行工作流

        Args:
            context: 执行上下文

        Returns:
            执行结果字典

        Raises:
            WorkflowExecutionError: 工作流执行失败
        """
        self.logger.info(f"开始执行工作流: {context.workflow_id}")

        # 重置所有节点状态
        for node in self.nodes.values():
            node.reset()

        # 开始执行
        context.start_execution()

        try:
            # 获取执行顺序
            execution_order = self.topological_sort()
            self.logger.info(f"执行顺序: {execution_order}")

            # 触发工作流开始回调
            await context.trigger_callback(
                "workflow_start", execution_order=execution_order
            )

            results = {}

            # 按顺序执行节点
            for node_id in execution_order:
                # 检查是否被取消
                if context.is_cancelled:
                    self.logger.info("工作流执行被取消")
                    break

                # 检查是否暂停
                await context.wait_if_paused()

                # 检查超时
                if context.check_timeout():
                    raise WorkflowExecutionError

                # 执行节点
                node = self.nodes[node_id]
                try:
                    result = await self._execute_node(node, context)
                    results[node_id] = result
                    context.record_node_execution(node_id, True)
                except Exception as e:
                    context.record_node_execution(node_id, False)
                    self.logger.error(f"节点执行失败: {node_id}, 错误: {e}")

                    # 触发节点错误回调
                    await context.trigger_callback(
                        "node_error", node_id=node_id, error=str(e)
                    )
                    # 兼容统一事件命名：node_end（失败）
                    await context.trigger_callback(
                        "node_end", node_id=node_id, success=False, error=str(e)
                    )

                    # 根据配置决定是否继续执行
                    raise WorkflowExecutionError(f"节点 {node_id} 执行失败") from e

            # 触发工作流完成回调
            await context.trigger_callback("workflow_complete", results=results)
            # 兼容统一事件命名：workflow_end（成功）
            await context.trigger_callback(
                "workflow_end", results=results, success=True
            )

            context.finish_execution(success=True)
            self.logger.info(f"工作流执行完成，共执行 {len(results)} 个节点")

            return results

        except Exception as e:
            context.finish_execution(success=False)
            await context.trigger_callback("workflow_error", error=str(e))
            # 兼容统一事件命名：workflow_end（失败）
            await context.trigger_callback("workflow_end", success=False, error=str(e))
            raise

    async def _execute_node(
        self, node: BaseNode, context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        执行单个节点

        Args:
            node: 要执行的节点
            context: 执行上下文

        Returns:
            节点输出数据
        """
        self.logger.debug(f"开始执行节点: {node.node_id}")

        # 触发节点开始回调
        await context.trigger_callback("node_start", node_id=node.node_id)

        # 准备节点输入
        await self._prepare_node_inputs(node, context)

        # 验证输入（抛异常则上抛为 WorkflowExecutionError）
        try:
            node.validate_inputs()
        except ValueError as e:
            raise WorkflowExecutionError(
                f"节点 {node.node_id} 输入验证失败: {e}"
            ) from e

        # 记录开始时间
        node.start_time = datetime.now()
        node.state = NodeState.RUNNING

        try:
            # 执行节点（在线程池中执行以避免阻塞）
            loop = asyncio.get_event_loop()
            outputs = await loop.run_in_executor(
                self.thread_pool, lambda: asyncio.run(node.execute(context))
            )

            # 记录结束时间
            node.end_time = datetime.now()
            node.execution_time = (node.end_time - node.start_time).total_seconds()

            # 设置节点状态和输出
            node.state = NodeState.COMPLETED
            node.outputs.update(outputs)

            # 保存输出到上下文
            context.set_node_output(node.node_id, outputs)

            # 触发节点完成回调
            await context.trigger_callback(
                "node_complete", node_id=node.node_id, outputs=outputs
            )
            # 兼容统一事件命名：node_end
            await context.trigger_callback(
                "node_end", node_id=node.node_id, outputs=outputs, success=True
            )

            self.logger.info(
                f"节点执行成功: {node.node_id}, 耗时: {node.execution_time:.3f}秒"
            )
            return outputs

        except Exception as e:
            # 记录错误
            node.end_time = datetime.now()
            node.execution_time = (node.end_time - node.start_time).total_seconds()
            node.state = NodeState.FAILED
            node.error_message = str(e)

            self.logger.error(f"节点执行失败: {node.node_id}, 错误: {e}")
            raise

    async def _prepare_node_inputs(
        self, node: BaseNode, context: ExecutionContext
    ) -> None:
        """
        准备节点输入数据

        Args:
            node: 目标节点
            context: 执行上下文
        """
        # 查找连接到此节点的所有连接
        for conn in self.connections:
            if conn.to_node_id == node.node_id:
                # 获取源节点的输出
                source_output = context.get_node_output(
                    conn.from_node_id, conn.from_output
                )
                if source_output is not None:
                    node.set_input(conn.to_input, source_output)
                    self.logger.debug(
                        f"传递数据: {conn.from_node_id}.{conn.from_output} -> {conn.to_node_id}.{conn.to_input}"
                    )

    def get_workflow_info(self) -> Dict[str, Any]:
        """
        获取工作流信息

        Returns:
            工作流信息字典
        """
        return {
            "node_count": len(self.nodes),
            "connection_count": len(self.connections),
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "connections": [
                {
                    "from": f"{conn.from_node_id}.{conn.from_output}",
                    "to": f"{conn.to_node_id}.{conn.to_input}",
                }
                for conn in self.connections
            ],
        }

    def clear(self) -> None:
        """清空工作流"""
        self.nodes.clear()
        self.connections.clear()
        self.logger.info("清空工作流")

    def __del__(self) -> None:
        """析构函数，清理线程池"""
        if hasattr(self, "thread_pool"):
            self.thread_pool.shutdown(wait=False)
