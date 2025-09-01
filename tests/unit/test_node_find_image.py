# -*- coding: utf-8 -*-
import asyncio

import numpy as np

from bluev.core.execution_context import ExecutionContext
from bluev.nodes.image.find_image_node import FindImageNode


def test_find_image_basic():
    async def _run():
        # 使用简单数组：在 10x10 源图像中匹配 2x2 模板
        source = np.zeros((10, 10), dtype=np.uint8)
        template = np.zeros((2, 2), dtype=np.uint8)
        node = FindImageNode(label="find-test")
        node.set_input("source_image", source)
        node.set_input("template_image", template)
        node.set_input("threshold", 0.1)

        ctx = ExecutionContext(workflow_id="wf-test")
        out = await node.execute(ctx)

        assert "found" in out
        assert isinstance(out["found"], bool)

    asyncio.run(_run())
