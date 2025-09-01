# -*- coding: utf-8 -*-
import asyncio
from unittest.mock import patch

from bluev.core.execution_context import ExecutionContext
from bluev.nodes.interaction.click_node import ClickNode


@patch("bluev.utils.system_adapter.get_system_adapter")
def test_click_node_basic(mock_get_adapter):
    async def _run():
        # mock adapter to avoid real clicks
        class M:
            def get_screen_size(self) -> None:
                return (1920, 1080)

            def click(self, x, y, button="left") -> None:
                return None

        mock_get_adapter.return_value = M()

        node = ClickNode(label="click-test")
        node.set_input("location", (100, 100))
        node.set_input("clicks", 1)
        node.set_input("button", "left")

        ctx = ExecutionContext(workflow_id="wf-test")
        out = await node.execute(ctx)

        assert out["success"] is True
        assert out["actual_clicks"] == 1
        assert out["click_location"] == (100, 100)

    asyncio.run(_run())
