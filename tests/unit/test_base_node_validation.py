# -*- coding: utf-8 -*-
import pytest

from bluev.core import NodeInput, NodeMetadata, NodeOutput
from bluev.core.base_node import BaseNode


def make_dummy(required=True, default=None):
    class D(BaseNode):
        @classmethod
        def get_input_spec(cls):
            return [
                NodeInput(
                    name="a",
                    data_type=int,
                    required=required,
                    default_value=default,
                    description="",
                )
            ]

        @classmethod
        def get_output_spec(cls):
            return [NodeOutput(name="b", data_type=int, description="")]

        @classmethod
        def get_metadata(cls):
            return NodeMetadata(
                node_type="d",
                category="x",
                display_name="d",
                description="",
                tags=[],
                version="1.0.0",
            )

        async def execute(self, context) -> None:
            return {"b": 1}

    return D


def test_default_filled_when_provided():
    dummy_class = make_dummy(required=False, default=3)
    n = dummy_class()
    assert n.get_input("a") == 3


def test_validate_required_missing():
    dummy_class = make_dummy(required=True, default=None)
    n = dummy_class()
    with pytest.raises(ValueError):
        n.validate_inputs()


def test_set_input_and_get_output():
    dummy_class = make_dummy()
    n = dummy_class()
    n.set_input("a", 10)
    assert n.get_input("a") == 10

    n.set_output("b", 2)
    assert n.get_output("b") == 2
