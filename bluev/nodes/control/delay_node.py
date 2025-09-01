# -*- coding: utf-8 -*-
"""
DelayNode - 延迟等待节点

提供延迟等待功能，支持固定延迟和随机延迟，
用于控制工作流执行节奏。
"""

import asyncio
import secrets
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from bluev.core.execution_context import ExecutionContext
from bluev.core import BaseNode, NodeInput, NodeMetadata, NodeOutput
from bluev.core.decorators import control_flow_node


@control_flow_node(
    node_type="delay",
    display_name="延迟等待",
    description="延迟指定时间，支持固定和随机延迟",
)
class DelayNode(BaseNode):
    """
    延迟等待节点

    功能：
    - 固定时间延迟
    - 随机范围延迟
    - 异步执行，不阻塞其他任务
    - 精确的时间测量

    适用场景：
    - 控制操作间隔，避免过快执行
    - 等待界面加载或动画完成
    - 模拟人工操作的自然节奏
    """

    @classmethod
    def get_input_spec(cls) -> List[NodeInput]:
        """获取输入规范"""
        return [
            NodeInput(
                name="duration",
                data_type=float,
                default_value=1.0,
                required=True,
                description="延迟时间（秒），必须大于0",
            ),
            NodeInput(
                name="random_range",
                data_type=Optional[float],  # type: ignore
                default_value=None,
                required=False,
                description="随机范围（秒），None表示固定延迟",
            ),
            NodeInput(
                name="min_delay",
                data_type=float,
                default_value=0.1,
                required=False,
                description="最小延迟时间（秒），防止延迟过短",
            ),
        ]

    @classmethod
    def get_output_spec(cls) -> List[NodeOutput]:
        """获取输出规范"""
        return [
            NodeOutput(
                name="actual_delay", data_type=float, description="实际延迟时间（秒）"
            ),
            NodeOutput(name="start_time", data_type=str, description="延迟开始时间戳"),
            NodeOutput(name="end_time", data_type=str, description="延迟结束时间戳"),
            NodeOutput(
                name="completed", data_type=bool, description="延迟是否正常完成"
            ),
        ]

    @classmethod
    def get_metadata(cls) -> NodeMetadata:
        """获取节点元数据"""
        return NodeMetadata(
            node_type="delay_node",
            display_name="延迟等待",
            description="延迟指定时间，支持固定和随机延迟",
            category="control_flow",
            tags=["delay", "wait", "timing", "control"],
            version="1.0.0",
        )

    async def execute(self, context: "ExecutionContext") -> Dict[str, Any]:
        """
        执行延迟等待

        Args:
            context: 执行上下文

        Returns:
            包含延迟信息的字典

        Raises:
            ValueError: 延迟参数无效时抛出异常
        """
        self.logger.info("开始执行延迟等待")

        try:
            # 获取输入参数
            duration = self.inputs.get("duration", 1.0)
            random_range = self.inputs.get("random_range")
            min_delay = self.inputs.get("min_delay", 0.1)

            # 参数验证
            if duration <= 0:
                raise ValueError

            if min_delay < 0:
                raise ValueError

            # 计算实际延迟时间
            if random_range is not None and random_range > 0:
                # 随机延迟：duration ± random_range
                min_time = max(duration - random_range, min_delay)
                max_time = duration + random_range
                actual_delay = secrets.SystemRandom().uniform(min_time, max_time)
                self.logger.debug(
                    f"随机延迟: {min_time:.3f}s - {max_time:.3f}s, 实际: {actual_delay:.3f}s"
                )
            else:
                # 固定延迟
                actual_delay = max(duration, min_delay)
                self.logger.debug(f"固定延迟: {actual_delay:.3f}s")

            # 记录开始时间
            start_time = time.time()
            start_time_str = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(start_time)
            )

            self.logger.info(f"开始延迟 {actual_delay:.3f} 秒")

            # 执行异步延迟
            await asyncio.sleep(actual_delay)

            # 记录结束时间
            end_time = time.time()
            end_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))

            # 计算实际延迟时间（可能有微小误差）
            measured_delay = end_time - start_time

            # 返回结果
            result = {
                "actual_delay": measured_delay,
                "start_time": start_time_str,
                "end_time": end_time_str,
                "completed": True,
            }

            self.logger.info(
                f"延迟完成: 预期 {actual_delay:.3f}s, 实际 {measured_delay:.3f}s"
            )
            return result

        except Exception as e:
            self.logger.error(f"延迟执行失败: {e}")
            # 返回失败状态
            return {
                "actual_delay": 0.0,
                "start_time": "",
                "end_time": "",
                "completed": False,
            }
