# -*- coding: utf-8 -*-
import pytest

from bluev.core.base_node import BaseNode
from bluev.core.node_registry import NodeRegistry


def test_register_and_create_node():
    reg = NodeRegistry()

    class Dummy(BaseNode):
        @classmethod
        def get_input_spec(cls):
            return []

        @classmethod
        def get_output_spec(cls):
            return []

        @classmethod
        def get_metadata(cls):
            from bluev.core import NodeMetadata

            return NodeMetadata(
                node_type="dummy",
                category="x",
                display_name="d",
                description="",
                tags=[],
                version="1.0.0",
            )

        async def execute(self, context) -> None:
            return {}

    reg.register_node("dummy", Dummy)
    assert reg.get_node_class("dummy") is Dummy

    n = reg.create_node("dummy", node_id="n1")
    assert isinstance(n, Dummy)
    assert n.node_id == "n1"


def test_register_invalid_class():
    reg = NodeRegistry()
    with pytest.raises(TypeError):
        reg.register_node("bad", object)  # type: ignore[arg-type]


def test_register_duplicate():
    reg = NodeRegistry()

    class Dummy(BaseNode):
        @classmethod
        def get_input_spec(cls):
            return []

        @classmethod
        def get_output_spec(cls):
            return []

        @classmethod
        def get_metadata(cls):
            from bluev.core import NodeMetadata

            return NodeMetadata(
                node_type="dummy",
                category="x",
                display_name="d",
                description="",
                tags=[],
                version="1.0.0",
            )

        async def execute(self, context) -> None:
            return {}

    reg.register_node("dummy", Dummy)
    # 重复注册相同类将被忽略并返回 False（不抛异常）
    ok = reg.register_node("dummy", Dummy)
    assert ok is False
