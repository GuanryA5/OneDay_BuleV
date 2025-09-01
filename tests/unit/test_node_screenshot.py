# -*- coding: utf-8 -*-
import asyncio
from unittest.mock import patch

import numpy as np

from bluev.core.execution_context import ExecutionContext
from bluev.nodes.image.screenshot_node import ScreenshotNode


@patch("bluev.nodes.image.screenshot_node.get_system_adapter")
def test_screenshot_node_basic(mock_get_adapter):
    async def _run():
        class M:
            def screenshot(self, region=None) -> None:
                from PIL import Image

                # 生成 3x2 RGB 图像
                return Image.new("RGB", (3, 2), color=(255, 0, 0))

        mock_get_adapter.return_value = M()

        node = ScreenshotNode(label="shot-test")
        node.set_input("region", None)

        ctx = ExecutionContext(workflow_id="wf-test")
        out = await node.execute(ctx)

        assert isinstance(out["image"], np.ndarray)
        assert out["image_size"] == (3, 2)

    asyncio.run(_run())
