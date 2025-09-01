# -*- coding: utf-8 -*-
import asyncio

from bluev.core.execution_context import ExecutionContext
from bluev.nodes.control.delay_node import DelayNode


def test_delay_node_basic():
    async def _run():
        node = DelayNode(label="delay-test")
        # 设置较小的延迟，注意 min_delay 默认 0.1 秒
        node.set_input("duration", 0.05)

        ctx = ExecutionContext(workflow_id="wf-test")
        out = await node.execute(ctx)

        assert out["completed"] is True
        assert out["actual_delay"] >= 0.1  # 至少达到 min_delay

    asyncio.run(_run())
