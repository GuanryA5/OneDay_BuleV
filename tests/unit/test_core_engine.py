# -*- coding: utf-8 -*-
import pytest

from bluev.core.workflow_engine import WorkflowEngine
from bluev.nodes.control.delay_node import DelayNode
from bluev.nodes.utility.log_node import LogNode


def test_engine_connect_and_topological():
    eng = WorkflowEngine()

    n1 = DelayNode(node_id="n1", label="delay")
    n2 = LogNode(node_id="n2", label="log")

    # 设置必要输入
    n1.set_input("duration", 0.05)
    n2.set_input("message", "ok")

    eng.add_node(n1)
    eng.add_node(n2)

    # 使用存在的端口名进行连线：DelayNode.actual_delay -> LogNode.message
    eng.connect_nodes("n1", "actual_delay", "n2", "message")

    info = eng.get_workflow_info()
    assert info["node_count"] == 2
    assert info["connection_count"] == 1

    order = eng.topological_sort()
    # n1 应先于 n2
    assert order.index("n1") < order.index("n2")


def test_engine_connect_invalid_port_name():
    eng = WorkflowEngine()

    n1 = DelayNode(node_id="n1", label="delay")
    n2 = LogNode(node_id="n2", label="log")

    eng.add_node(n1)
    eng.add_node(n2)

    with pytest.raises(ValueError):
        eng.connect_nodes("n1", "not_exist", "n2", "message")

    with pytest.raises(ValueError):
        eng.connect_nodes("n1", "actual_delay", "n2", "not_exist")
