# -*- coding: utf-8 -*-
"""Integration test: Screenshot -> FindImage -> Click -> Delay -> Log
使用 monkeypatch 隔离系统交互，验证工作流加载与执行闭环。
"""

import asyncio
from unittest.mock import patch

import numpy as np

from bluev.core.execution_context import ExecutionContext
from bluev.core.workflow_loader import build_engine_from_workflow


def test_min_workflow_pipeline(monkeypatch):
    # Patch ScreenshotNode 的系统适配器，返回小尺寸 PIL 图像
    with patch(
        "bluev.nodes.image.screenshot_node.get_system_adapter"
    ) as mock_get_adapter:

        class SA:
            def screenshot(self, region=None) -> None:
                from PIL import Image

                return Image.new("RGB", (4, 3), color=(200, 200, 200))

        mock_get_adapter.return_value = SA()

        # Patch ClickNode 的系统适配器，避免真实点击
        with patch(
            "bluev.nodes.interaction.click_node.get_system_adapter"
        ) as mock_click_adapter:

            class CA:
                def get_screen_size(self) -> None:
                    return (1920, 1080)

                def click(self, x, y, button="left") -> None:
                    return None

            mock_click_adapter.return_value = CA()

            # Patch FindImageNode.execute，避免依赖真实 cv2/template 文件
            from bluev.nodes.image.find_image_node import FindImageNode

            async def fake_execute(self, context) -> None:
                # 模拟一次成功匹配，提供 bbox 与 location（中心点）
                bbox = [1, 1, 2, 2]
                x, y, w, h = bbox
                location = (x + w // 2, y + h // 2)
                return {
                    "found": True,
                    "bbox": bbox,
                    "location": location,
                    "score": 0.99,
                }

            monkeypatch.setattr(FindImageNode, "execute", fake_execute, raising=True)

            # 定义最小完整 5 节点工作流
            wf = {
                "workflow_id": "wf-int",
                "nodes": [
                    {"id": "n1", "type": "screenshot", "params": {}},
                    {
                        "id": "n2",
                        "type": "find_image",
                        "params": {
                            "template_image": np.zeros((2, 2), dtype=np.uint8),
                            "threshold": 0.85,
                        },
                    },
                    {"id": "n3", "type": "click", "params": {"offset": [0, 0]}},
                    {"id": "n4", "type": "delay", "params": {"ms": 50}},
                    {"id": "n5", "type": "log", "params": {"message": "done"}},
                ],
                "edges": [["n1", "n2"], ["n2", "n3"], ["n3", "n4"], ["n4", "n5"]],
            }

            eng = build_engine_from_workflow(wf)

            async def _run():
                ctx = ExecutionContext(workflow_id="wf-int", max_execution_time=5)
                results = await eng.execute_workflow(ctx)
                # 至少包含末节点输出
                assert "n5" in results

            asyncio.run(_run())
