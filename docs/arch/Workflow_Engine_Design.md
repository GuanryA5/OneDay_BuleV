# BlueV工作流执行引擎设计

**文档版本**: v1.0
**创建日期**: 2025-01-27
**关联文档**: BlueV_Architecture_Design.md, Node_System_Implementation.md

---

## 🎯 **执行引擎设计目标**

### **核心特性**
- ⚡ **高性能**: 异步执行和并行处理
- 🔄 **状态管理**: 完整的执行状态追踪
- 🛡️ **错误处理**: 健壮的异常处理和恢复机制
- 📊 **可观测性**: 详细的执行日志和监控
- 🔀 **灵活调度**: 支持多种执行策略

---

## 🏗️ **执行引擎核心组件**

### **执行上下文管理**
```python
import asyncio
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ExecutionMetrics:
    """执行指标"""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    nodes_executed: int = 0
    nodes_failed: int = 0
    memory_usage: float = 0.0

class ExecutionContext:
    """增强的执行上下文"""

    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.variables: Dict[str, Any] = {}
        self.node_outputs: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[str] = []
        self.metrics = ExecutionMetrics()
        self.callbacks: Dict[str, List[Callable]] = {
            "node_start": [],
            "node_complete": [],
            "node_error": [],
            "workflow_complete": [],
            "workflow_error": []
        }

    def add_callback(self, event: str, callback: Callable):
        """添加事件回调"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    async def trigger_callback(self, event: str, **kwargs):
        """触发事件回调"""
        for callback in self.callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self, **kwargs)
                else:
                    callback(self, **kwargs)
            except Exception as e:
                print(f"Callback error for {event}: {e}")

    def get_variable(self, name: str, default: Any = None) -> Any:
        return self.variables.get(name, default)

    def set_variable(self, name: str, value: Any):
        self.variables[name] = value

    def get_node_output(self, node_id: str, output_name: str, default: Any = None) -> Any:
        return self.node_outputs.get(node_id, {}).get(output_name, default)

    def set_node_output(self, node_id: str, outputs: Dict[str, Any]):
        self.node_outputs[node_id] = outputs

    def get_execution_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        return {
            "workflow_id": self.workflow_id,
            "metrics": {
                "start_time": self.metrics.start_time.isoformat(),
                "end_time": self.metrics.end_time.isoformat() if self.metrics.end_time else None,
                "duration": self.metrics.duration,
                "nodes_executed": self.metrics.nodes_executed,
                "nodes_failed": self.metrics.nodes_failed,
                "memory_usage": self.metrics.memory_usage
            },
            "execution_history": self.execution_history,
            "variables": self.variables
        }
```

### **工作流执行引擎**
```python
import asyncio
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import logging

class WorkflowExecutionError(Exception):
    """工作流执行异常"""
    def __init__(self, message: str, node_id: str = None, original_error: Exception = None):
        super().__init__(message)
        self.node_id = node_id
        self.original_error = original_error

class WorkflowEngine:
    """BlueV工作流执行引擎"""

    def __init__(self, max_concurrent_nodes: int = 5):
        self.nodes: Dict[str, BaseNode] = {}
        self.connections: List[Tuple[str, str, str, str]] = []
        self.max_concurrent_nodes = max_concurrent_nodes
        self.logger = logging.getLogger(__name__)
        self._execution_semaphore = asyncio.Semaphore(max_concurrent_nodes)

    def add_node(self, node: BaseNode):
        """添加节点"""
        self.nodes[node.node_id] = node
        self.logger.info(f"Added node: {node.node_id} ({node.__class__.__name__})")

    def remove_node(self, node_id: str):
        """移除节点"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            # 移除相关连接
            self.connections = [
                conn for conn in self.connections
                if conn[0] != node_id and conn[2] != node_id
            ]
            self.logger.info(f"Removed node: {node_id}")

    def add_connection(self, from_node: str, from_output: str, to_node: str, to_input: str):
        """添加连接"""
        if from_node not in self.nodes:
            raise ValueError(f"Source node '{from_node}' not found")
        if to_node not in self.nodes:
            raise ValueError(f"Target node '{to_node}' not found")

        self.connections.append((from_node, from_output, to_node, to_input))
        self.logger.info(f"Added connection: {from_node}.{from_output} -> {to_node}.{to_input}")

    def build_execution_graph(self) -> Tuple[Dict[str, Set[str]], Dict[str, int]]:
        """构建执行图"""
        graph = defaultdict(set)
        in_degree = defaultdict(int)

        # 初始化所有节点
        for node_id in self.nodes:
            in_degree[node_id] = 0

        # 构建依赖关系
        for from_node, _, to_node, _ in self.connections:
            if to_node not in graph[from_node]:
                graph[from_node].add(to_node)
                in_degree[to_node] += 1

        return graph, in_degree

    def topological_sort(self) -> List[str]:
        """拓扑排序确定执行顺序"""
        graph, in_degree = self.build_execution_graph()
        queue = deque([node for node, degree in in_degree.items() if degree == 0])
        result = []

        while queue:
            current = queue.popleft()
            result.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self.nodes):
            cycle_nodes = [node for node, degree in in_degree.items() if degree > 0]
            raise WorkflowExecutionError(f"Workflow contains cycles involving nodes: {cycle_nodes}")

        return result

    async def execute_workflow(self, context: ExecutionContext) -> Dict[str, Any]:
        """执行工作流"""
        self.logger.info(f"Starting workflow execution: {context.workflow_id}")
        context.metrics.start_time = datetime.now()

        try:
            # 获取执行顺序
            execution_order = self.topological_sort()
            self.logger.info(f"Execution order: {execution_order}")

            # 触发工作流开始回调
            await context.trigger_callback("workflow_start", execution_order=execution_order)

            results = {}

            # 顺序执行节点
            for node_id in execution_order:
                node = self.nodes[node_id]

                try:
                    # 执行节点
                    node_result = await self._execute_node(node, context)
                    results[node_id] = node_result
                    context.metrics.nodes_executed += 1

                except Exception as e:
                    context.metrics.nodes_failed += 1
                    self.logger.error(f"Node {node_id} execution failed: {e}")

                    # 触发节点错误回调
                    await context.trigger_callback("node_error", node_id=node_id, error=e)

                    # 根据错误处理策略决定是否继续
                    if self._should_stop_on_error(node, e):
                        raise WorkflowExecutionError(
                            f"Workflow stopped due to node {node_id} failure: {e}",
                            node_id=node_id,
                            original_error=e
                        )

            # 计算执行指标
            context.metrics.end_time = datetime.now()
            context.metrics.duration = (
                context.metrics.end_time - context.metrics.start_time
            ).total_seconds()

            # 触发工作流完成回调
            await context.trigger_callback("workflow_complete", results=results)

            self.logger.info(f"Workflow execution completed: {context.workflow_id}")
            return results

        except Exception as e:
            context.metrics.end_time = datetime.now()
            context.metrics.duration = (
                context.metrics.end_time - context.metrics.start_time
            ).total_seconds()

            # 触发工作流错误回调
            await context.trigger_callback("workflow_error", error=e)

            self.logger.error(f"Workflow execution failed: {context.workflow_id}, error: {e}")
            raise

    async def _execute_node(self, node: BaseNode, context: ExecutionContext) -> Dict[str, Any]:
        """执行单个节点"""
        async with self._execution_semaphore:
            self.logger.info(f"Executing node: {node.node_id}")

            # 触发节点开始回调
            await context.trigger_callback("node_start", node_id=node.node_id)

            try:
                # 准备节点输入
                await self._prepare_node_inputs(node, context)

                # 验证输入
                node.validate_inputs()

                # 执行节点
                node.state = NodeState.RUNNING
                outputs = await node.execute(context)

                # 保存输出
                context.set_node_output(node.node_id, outputs)
                context.execution_history.append(node.node_id)

                # 触发节点完成回调
                await context.trigger_callback("node_complete", node_id=node.node_id, outputs=outputs)

                self.logger.info(f"Node {node.node_id} completed successfully")
                return outputs

            except Exception as e:
                node.state = NodeState.FAILED
                node.error_message = str(e)
                self.logger.error(f"Node {node.node_id} failed: {e}")
                raise

    async def _prepare_node_inputs(self, node: BaseNode, context: ExecutionContext):
        """准备节点输入数据"""
        for from_node, from_output, to_node, to_input in self.connections:
            if to_node == node.node_id:
                output_value = context.get_node_output(from_node, from_output)
                if output_value is not None:
                    node.inputs[to_input] = output_value
                    self.logger.debug(f"Set input {to_input} for node {node.node_id}")

    def _should_stop_on_error(self, node: BaseNode, error: Exception) -> bool:
        """判断是否应该因错误停止执行"""
        # 可以根据节点类型或错误类型制定不同的策略
        # 这里简单地对所有错误都停止执行
        return True

    def get_workflow_status(self) -> Dict[str, Any]:
        """获取工作流状态"""
        node_states = {}
        for node_id, node in self.nodes.items():
            node_states[node_id] = {
                "state": node.state.value,
                "error_message": node.error_message
            }

        return {
            "nodes": node_states,
            "connections": self.connections,
            "total_nodes": len(self.nodes),
            "total_connections": len(self.connections)
        }

    def validate_workflow(self) -> List[str]:
        """验证工作流完整性"""
        errors = []

        # 检查循环依赖
        try:
            self.topological_sort()
        except WorkflowExecutionError as e:
            errors.append(str(e))

        # 检查连接有效性
        for from_node, from_output, to_node, to_input in self.connections:
            if from_node not in self.nodes:
                errors.append(f"Connection references non-existent source node: {from_node}")
            if to_node not in self.nodes:
                errors.append(f"Connection references non-existent target node: {to_node}")

        # 检查节点输入完整性
        for node_id, node in self.nodes.items():
            input_spec = node.get_input_spec()
            required_inputs = {spec.name for spec in input_spec if spec.required}

            # 检查哪些输入有连接
            connected_inputs = set()
            for _, _, to_node, to_input in self.connections:
                if to_node == node_id:
                    connected_inputs.add(to_input)

            # 检查缺失的必需输入
            missing_inputs = required_inputs - connected_inputs
            for missing_input in missing_inputs:
                # 检查是否有默认值
                spec = next((s for s in input_spec if s.name == missing_input), None)
                if spec and spec.default_value is None:
                    errors.append(f"Node {node_id} missing required input: {missing_input}")

        return errors
```

---

## 🔄 **并行执行支持**

### **并行执行引擎**
```python
class ParallelWorkflowEngine(WorkflowEngine):
    """支持并行执行的工作流引擎"""

    def __init__(self, max_concurrent_nodes: int = 5, executor_type: str = "thread"):
        super().__init__(max_concurrent_nodes)
        self.executor_type = executor_type
        self.executor = None

    async def execute_workflow_parallel(self, context: ExecutionContext) -> Dict[str, Any]:
        """并行执行工作流"""
        self.logger.info(f"Starting parallel workflow execution: {context.workflow_id}")

        # 构建执行图
        graph, in_degree = self.build_execution_graph()

        # 初始化执行状态
        completed_nodes = set()
        running_tasks = {}
        results = {}

        # 创建执行器
        if self.executor_type == "thread":
            self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_nodes)
        elif self.executor_type == "process":
            self.executor = ProcessPoolExecutor(max_workers=self.max_concurrent_nodes)

        try:
            context.metrics.start_time = datetime.now()

            while len(completed_nodes) < len(self.nodes):
                # 找到可以执行的节点
                ready_nodes = [
                    node_id for node_id in self.nodes
                    if node_id not in completed_nodes
                    and node_id not in running_tasks
                    and in_degree[node_id] == 0
                ]

                # 启动就绪节点的执行
                for node_id in ready_nodes:
                    if len(running_tasks) < self.max_concurrent_nodes:
                        node = self.nodes[node_id]
                        task = asyncio.create_task(self._execute_node(node, context))
                        running_tasks[node_id] = task

                # 等待至少一个任务完成
                if running_tasks:
                    done, pending = await asyncio.wait(
                        running_tasks.values(),
                        return_when=asyncio.FIRST_COMPLETED
                    )

                    # 处理完成的任务
                    for task in done:
                        # 找到对应的节点ID
                        node_id = next(
                            nid for nid, t in running_tasks.items() if t == task
                        )

                        try:
                            result = await task
                            results[node_id] = result
                            completed_nodes.add(node_id)
                            context.metrics.nodes_executed += 1

                            # 更新依赖节点的入度
                            for dependent in graph[node_id]:
                                in_degree[dependent] -= 1

                        except Exception as e:
                            context.metrics.nodes_failed += 1
                            self.logger.error(f"Parallel node {node_id} failed: {e}")

                            # 根据错误处理策略决定是否继续
                            if self._should_stop_on_error(self.nodes[node_id], e):
                                # 取消所有运行中的任务
                                for pending_task in pending:
                                    pending_task.cancel()
                                raise WorkflowExecutionError(
                                    f"Parallel workflow stopped due to node {node_id} failure: {e}",
                                    node_id=node_id,
                                    original_error=e
                                )

                        # 移除已完成的任务
                        del running_tasks[node_id]

            # 计算执行指标
            context.metrics.end_time = datetime.now()
            context.metrics.duration = (
                context.metrics.end_time - context.metrics.start_time
            ).total_seconds()

            self.logger.info(f"Parallel workflow execution completed: {context.workflow_id}")
            return results

        finally:
            if self.executor:
                self.executor.shutdown(wait=True)
```

---

**文档状态**: ✅ 工作流执行引擎设计已完成
**核心特性**: 高性能、状态管理、错误处理、可观测性、灵活调度
**执行模式**: 顺序执行 + 并行执行支持
**监控能力**: 完整的执行指标和回调机制
**下一步**: 实现实时通信系统和PySide6集成
