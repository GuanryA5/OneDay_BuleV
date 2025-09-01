# -*- coding: utf-8 -*-
import asyncio
from unittest.mock import Mock, patch

from bluev.core.execution_context import ExecutionContext
from bluev.nodes.utility.log_node import LogNode


@patch("bluev.utils.logging.logger")
def test_log_node_basic(mock_logger):
    async def _run():
        mock_bound = Mock()
        mock_logger.bind.return_value = mock_bound

        node = LogNode(label="log-test")
        node.set_input("message", "hello")
        node.set_input("level", "INFO")

        ctx = ExecutionContext(workflow_id="wf-test")
        out = await node.execute(ctx)

        assert out["logged"] is True
        mock_logger.bind.assert_called()
        mock_bound.info.assert_called_with("hello", category="workflow")

    asyncio.run(_run())
